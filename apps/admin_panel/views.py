import datetime
import json
from pathlib import Path

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Count, Max, Q, Subquery, OuterRef
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from apps.accounts.models import CustomUser
from apps.chat.models import ChatRoom, Message
from apps.documents.models import Document, DocumentType
from apps.meetings.models import AvailableSlot, Meeting
from apps.notifications.models import Notification
from apps.notifications.services import dispatch_bulk, dispatch_notification
from apps.onboarding.models import OnboardingResponse
from apps.plans.models import Plan, Subscription

from .decorators import staff_required
from .models import PlatformSetting


def _broadcast_staff_inbox(message):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    preview = (message.content or '').strip()
    if not preview and message.file:
        preview = 'Piece jointe'
    async_to_sync(channel_layer.group_send)(
        'staff_inbox',
        {
            'type': 'inbox_message',
            'room_id': message.room_id,
            'sender_name': message.sender.first_name or message.sender.email.split('@')[0],
            'is_staff': bool(message.sender.is_staff or message.sender.is_advisor),
            'content': preview,
            'timestamp': message.created_at.strftime('%H:%M'),
        },
    )


# ── Auth ─────────────────────────────────────────────────────────────

def staff_login(request):
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_advisor):
        return redirect('admin_panel:overview')

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user and (user.is_staff or user.is_advisor):
            login(request, user)
            return redirect('admin_panel:overview')
        messages.error(request, 'Identifiants invalides ou acces non autorise.')

    return render(request, 'admin_panel/login.html')


def staff_logout(request):
    logout(request)
    return redirect('admin_panel:login')


# ── Context helper ───────────────────────────────────────────────────

def _get_admin_context(user=None):
    today = timezone.now().date()

    pending_docs = Document.objects.filter(status='pending').count()
    unread_messages = Message.objects.filter(status='sent').exclude(
        Q(sender__is_staff=True) | Q(sender__is_advisor=True),
    ).count()
    urgent_chats = ChatRoom.objects.filter(is_urgent=True).count()
    unread_notifs_qs = Notification.objects.filter(is_read=False, audience='staff')
    if user and user.is_authenticated:
        unread_notifs_qs = unread_notifs_qs.filter(user=user)
    else:
        unread_notifs_qs = unread_notifs_qs.filter(
            user__in=CustomUser.objects.filter(Q(is_staff=True) | Q(is_advisor=True)),
        )
    unread_notifs = unread_notifs_qs.count()

    return {
        'pending_docs_count': pending_docs,
        'unread_messages_count': unread_messages,
        'urgent_chats_count': urgent_chats,
        'unread_notifications_count': unread_notifs,
        'today': today,
    }


def _students_queryset():
    return CustomUser.objects.filter(
        is_student=True,
        is_staff=False,
        is_superuser=False,
        is_advisor=False,
    )


def _document_preview_kind(doc):
    file_name = (doc.file.name or '').lower()
    ext = Path(file_name).suffix
    if ext == '.pdf':
        return 'pdf'
    if ext in {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'}:
        return 'image'
    return 'none'


def _apply_document_review(doc, action, comment, reviewed_by=None):
    status_map = {
        'approve': 'approved',
        'reject': 'rejected',
        'reupload': 'reupload',
    }
    if action not in status_map:
        return False

    doc.status = status_map[action]
    doc.admin_comment = comment
    doc.reviewed_at = timezone.now()
    doc.save(update_fields=['status', 'admin_comment', 'reviewed_at'])

    notif_map = {
        'approve': ('document_approved', 'Document approuve', f'Votre document "{doc}" a ete approuve.'),
        'reject': ('document_rejected', 'Document refuse', f'Votre document "{doc}" a ete refuse. {comment}'),
        'reupload': ('document_rejected', 'Re-telechargement requis', f'Veuillez re-televerser votre document "{doc}". {comment}'),
    }
    n_type, n_title, n_msg = notif_map[action]
    dispatch_notification(
        user=doc.user,
        created_by=reviewed_by,
        notification_type=n_type,
        category='document',
        priority='normal' if action == 'approve' else 'high',
        title=n_title,
        message=n_msg,
        link='/dashboard/documents/',
    )
    return True


# ── 1. Overview ──────────────────────────────────────────────────────

@staff_required
def overview(request):
    ctx = _get_admin_context(request.user)
    today = ctx['today']

    students_qs = _students_queryset()
    total_students = students_qs.count()
    active_subs = Subscription.objects.filter(status='active').count()
    pending_docs = ctx['pending_docs_count']
    upcoming_meetings = Meeting.objects.filter(
        slot__date__gte=today, status='scheduled',
    ).count()

    recent_students = students_qs.order_by('-created_at')[:5]

    recent_docs = Document.objects.filter(
        status='pending',
    ).select_related('user', 'document_type').order_by('-uploaded_at')[:5]

    upcoming_meeting_list = Meeting.objects.filter(
        slot__date__gte=today, status='scheduled',
    ).select_related('student', 'slot').order_by('slot__date', 'slot__start_time')[:5]

    recent_payments = Subscription.objects.filter(
        status='active',
    ).select_related('user', 'plan').order_by('-paid_at')[:5]

    ctx.update({
        'total_students': total_students,
        'active_subs': active_subs,
        'pending_docs': pending_docs,
        'upcoming_meetings': upcoming_meetings,
        'recent_students': recent_students,
        'recent_docs': recent_docs,
        'upcoming_meeting_list': upcoming_meeting_list,
        'recent_payments': recent_payments,
    })
    return render(request, 'admin_panel/overview.html', ctx)


# ── 2. Students List ────────────────────────────────────────────────

@staff_required
def students_list(request):
    ctx = _get_admin_context(request.user)

    qs = _students_queryset().order_by('-created_at')

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(
            Q(email__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
        )

    plan_filter = request.GET.get('plan', '')
    if plan_filter:
        if plan_filter.isdigit():
            qs = qs.filter(subscription__plan_id=int(plan_filter))
        else:
            qs = qs.filter(subscription__plan__slug=plan_filter)

    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        qs = qs.filter(subscription__status='active')
    elif status_filter == 'pending':
        qs = qs.filter(subscription__status='pending')
    elif status_filter in {'no_plan', 'none'}:
        qs = qs.filter(subscription__isnull=True)

    students = qs.select_related('subscription__plan')

    ctx.update({
        'students': students,
        'q': q,
        'plan_filter': plan_filter,
        'status_filter': status_filter,
        'plans': Plan.objects.filter(is_active=True),
    })
    return render(request, 'admin_panel/students_list.html', ctx)


# ── 3. Student Detail ───────────────────────────────────────────────

@staff_required
def student_detail(request, pk):
    ctx = _get_admin_context(request.user)

    student = get_object_or_404(
        CustomUser,
        pk=pk,
        is_student=True,
        is_staff=False,
        is_superuser=False,
        is_advisor=False,
    )

    subscription = None
    try:
        subscription = student.subscription
    except Subscription.DoesNotExist:
        pass

    onboarding = None
    try:
        onboarding = student.onboarding
    except OnboardingResponse.DoesNotExist:
        pass

    documents = Document.objects.filter(user=student).select_related('document_type').order_by('-uploaded_at')
    meetings = Meeting.objects.filter(student=student).select_related('slot').order_by('-slot__date')
    notifications = Notification.objects.filter(user=student).order_by('-created_at')[:10]

    chat_room = None
    try:
        chat_room = student.chat_room
    except ChatRoom.DoesNotExist:
        pass

    ctx.update({
        'student': student,
        'subscription': subscription,
        'onboarding': onboarding,
        'documents': documents,
        'meetings': meetings,
        'notifications': notifications,
        'chat_room': chat_room,
    })
    return render(request, 'admin_panel/student_detail.html', ctx)


# ── 4. Document Review ──────────────────────────────────────────────

@staff_required
def documents_list(request):
    ctx = _get_admin_context(request.user)

    search = request.GET.get('q', '').strip()

    students = CustomUser.objects.filter(is_student=True).annotate(
        doc_count=Count('documents'),
        pending_count=Count('documents', filter=Q(documents__status='pending')),
    )

    if search:
        students = students.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search),
        )

    # Students with pending docs first, then by total doc count
    students = students.order_by('-pending_count', '-doc_count')

    paginator = Paginator(students, 24)
    page_number = request.GET.get('page')
    students_page = paginator.get_page(page_number)

    ctx.update({
        'students': students_page.object_list,
        'students_page': students_page,
        'search': search,
    })
    return render(request, 'admin_panel/documents_list.html', ctx)


@staff_required
def student_documents(request, pk):
    ctx = _get_admin_context(request.user)
    student = get_object_or_404(CustomUser, pk=pk, is_student=True)

    qs = Document.objects.filter(user=student).select_related('document_type').order_by(
        '-uploaded_at',
    )

    status_filter = request.GET.get('status', '')
    if status_filter:
        qs = qs.filter(status=status_filter)

    # Reorder so pending is always first
    qs = qs.extra(
        select={'is_pending': "status = 'pending'"},
    ).order_by('-is_pending', '-uploaded_at')

    documents = list(qs)
    for doc in documents:
        doc.preview_kind = _document_preview_kind(doc)

    ctx.update({
        'student': student,
        'documents': documents,
        'status_filter': status_filter,
        'status_choices': Document.STATUS_CHOICES,
    })
    return render(request, 'admin_panel/student_documents.html', ctx)


@staff_required
@require_POST
def document_review(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    action = request.POST.get('action')
    comment = request.POST.get('comment', '').strip()

    if _apply_document_review(doc, action, comment, reviewed_by=request.user):
        messages.success(request, f'Document mis a jour: {doc.get_status_display()}')

    return redirect('admin_panel:student_documents', pk=doc.user_id)


@staff_required
@require_POST
def documents_bulk_review(request):
    action = request.POST.get('action')
    comment = request.POST.get('comment', '').strip()
    doc_ids = request.POST.getlist('doc_ids')
    student_pk = request.POST.get('student_pk')

    if not doc_ids:
        messages.error(request, 'Selectionnez au moins un document.')
        if student_pk:
            return redirect('admin_panel:student_documents', pk=student_pk)
        return redirect('admin_panel:documents')

    docs = Document.objects.filter(pk__in=doc_ids).select_related('user', 'document_type')
    updated = 0
    for doc in docs:
        if _apply_document_review(doc, action, comment, reviewed_by=request.user):
            updated += 1

    if updated:
        messages.success(request, f'{updated} document(s) mis a jour.')
    else:
        messages.error(request, 'Action invalide.')
    if student_pk:
        return redirect('admin_panel:student_documents', pk=student_pk)
    return redirect('admin_panel:documents')


# ── 5. Document Types ────────────────────────────────────────────────

@staff_required
def document_types_list(request):
    ctx = _get_admin_context(request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            name = request.POST.get('name', '').strip()
            if name:
                DocumentType.objects.create(
                    name=name,
                    slug=slugify(name),
                    description=request.POST.get('description', '').strip(),
                    tip=request.POST.get('tip', '').strip(),
                    is_required='is_required' in request.POST,
                    order=DocumentType.objects.count(),
                )
                messages.success(request, 'Type de document cree.')
            return redirect('admin_panel:document_types')

        elif action == 'edit':
            dt = get_object_or_404(DocumentType, pk=request.POST.get('pk'))
            dt.name = request.POST.get('name', '').strip() or dt.name
            dt.description = request.POST.get('description', '').strip()
            dt.tip = request.POST.get('tip', '').strip()
            dt.is_required = 'is_required' in request.POST
            dt.save()
            messages.success(request, 'Type de document modifie.')
            return redirect('admin_panel:document_types')

        elif action == 'delete':
            dt = get_object_or_404(DocumentType, pk=request.POST.get('pk'))
            dt.delete()
            messages.success(request, 'Type de document supprime.')
            return redirect('admin_panel:document_types')

    ctx['doc_types'] = DocumentType.objects.all()
    return render(request, 'admin_panel/document_types.html', ctx)


@staff_required
@require_POST
def document_types_reorder(request):
    try:
        order = json.loads(request.body).get('order', [])
        for i, pk in enumerate(order):
            DocumentType.objects.filter(pk=pk).update(order=i)
        return JsonResponse({'ok': True})
    except (json.JSONDecodeError, Exception):
        return JsonResponse({'ok': False}, status=400)


# ── 6. Meetings & Slots ─────────────────────────────────────────────

@staff_required
def meetings_list(request):
    ctx = _get_admin_context(request.user)
    today = ctx['today']

    tab = request.GET.get('tab', 'meetings')

    # Meetings tab
    meetings_qs = Meeting.objects.select_related('student', 'slot').order_by('-slot__date')
    m_status = request.GET.get('m_status', '')
    if m_status:
        meetings_qs = meetings_qs.filter(status=m_status)
    m_search = request.GET.get('m_search', '').strip()
    if m_search:
        meetings_qs = meetings_qs.filter(
            Q(student__email__icontains=m_search) | Q(topic__icontains=m_search)
        )
    m_date = request.GET.get('m_date', '').strip()
    if m_date:
        meetings_qs = meetings_qs.filter(slot__date=m_date)

    # Slots tab
    slots = AvailableSlot.objects.filter(date__gte=today).order_by('date', 'start_time')

    ctx.update({
        'tab': tab,
        'meetings': meetings_qs,
        'm_status': m_status,
        'm_search': m_search,
        'm_date': m_date,
        'slots': slots,
        'meeting_status_choices': Meeting.STATUS_CHOICES,
    })
    return render(request, 'admin_panel/meetings.html', ctx)


@staff_required
@require_POST
def slot_create(request):
    date = request.POST.get('date')
    start_time = request.POST.get('start_time')
    end_time = request.POST.get('end_time')
    if date and start_time and end_time:
        AvailableSlot.objects.create(date=date, start_time=start_time, end_time=end_time)
        messages.success(request, 'Creneau cree.')
    return redirect('admin_panel:meetings')


@staff_required
@require_POST
def slots_bulk_create(request):
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    start_time = request.POST.get('start_time')
    end_time = request.POST.get('end_time')

    if start_date and end_date and start_time and end_time:
        s_date = datetime.date.fromisoformat(start_date)
        e_date = datetime.date.fromisoformat(end_date)
        s_time = datetime.time.fromisoformat(start_time)
        e_time = datetime.time.fromisoformat(end_time)

        created = 0
        current = s_date
        while current <= e_date:
            if current.weekday() < 5:  # Mon-Fri only
                AvailableSlot.objects.create(date=current, start_time=s_time, end_time=e_time)
                created += 1
            current += datetime.timedelta(days=1)
        messages.success(request, f'{created} creneaux crees.')

    return redirect('admin_panel:meetings')


@staff_required
@require_POST
def slot_delete(request, pk):
    slot = get_object_or_404(AvailableSlot, pk=pk)
    if not slot.is_booked:
        slot.delete()
        messages.success(request, 'Creneau supprime.')
    else:
        messages.error(request, 'Ce creneau est deja reserve.')
    return redirect('admin_panel:meetings')


@staff_required
@require_POST
def meeting_update(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    new_status = request.POST.get('status')
    if new_status in dict(Meeting.STATUS_CHOICES):
        meeting.status = new_status
        meeting.save(update_fields=['status'])
        if new_status == 'cancelled':
            meeting.slot.is_booked = False
            meeting.slot.save(update_fields=['is_booked'])
            dispatch_notification(
                user=meeting.student,
                created_by=request.user,
                notification_type='general',
                category='meeting',
                priority='high',
                title='Rendez-vous annule',
                message=f'Votre rendez-vous du {meeting.slot.date} a ete annule.',
                link='/dashboard/meetings/',
            )
        elif new_status == 'scheduled':
            dispatch_notification(
                user=meeting.student,
                created_by=request.user,
                notification_type='meeting_confirmed',
                category='meeting',
                priority='normal',
                title='Rendez-vous confirme',
                message=f'Votre rendez-vous du {meeting.slot.date} est confirme.',
                link='/dashboard/meetings/',
            )
        messages.success(request, 'Rendez-vous mis a jour.')
    return redirect('admin_panel:meetings')


# ── 7. Chat / Messages ──────────────────────────────────────────────

@staff_required
def messages_list(request):
    ctx = _get_admin_context(request.user)

    rooms = ChatRoom.objects.select_related('student').annotate(
        last_message_time=Max('messages__created_at'),
        unread_count=Count('messages', filter=Q(messages__status='sent') & ~Q(messages__sender__is_staff=True) & ~Q(messages__sender__is_advisor=True)),
    ).order_by('-is_urgent', '-last_message_time')

    # Attach last message text and sender info
    last_msg_qs = Message.objects.filter(
        room=OuterRef('pk'),
    ).order_by('-created_at')
    rooms = rooms.annotate(
        last_message_preview=Subquery(last_msg_qs.values('content')[:1]),
        last_message_sender_is_staff=Subquery(last_msg_qs.values('sender__is_staff')[:1]),
    )

    paginator = Paginator(rooms, 20)
    page_number = request.GET.get('page')
    rooms_page = paginator.get_page(page_number)

    ctx['rooms'] = rooms_page.object_list
    ctx['rooms_page'] = rooms_page
    return render(request, 'admin_panel/messages_list.html', ctx)


@staff_required
def chat_detail(request, pk):
    ctx = _get_admin_context(request.user)
    room = get_object_or_404(ChatRoom.objects.select_related('student'), pk=pk)

    if request.method == 'POST':
        content = request.POST.get('message', '').strip()
        attached = request.FILES.get('file')
        if content or attached:
            reply_to = None
            reply_to_id = request.POST.get('reply_to')
            if reply_to_id and reply_to_id.isdigit():
                reply_to = Message.objects.filter(pk=int(reply_to_id), room=room).first()
            msg = Message.objects.create(
                room=room,
                sender=request.user,
                content=content,
                file=attached,
                reply_to=reply_to,
                is_priority='is_priority' in request.POST,
            )
            preview = (msg.content or '').strip() or 'Piece jointe'
            dispatch_notification(
                user=room.student,
                created_by=request.user,
                audience='student',
                notification_type='new_message',
                category='chat',
                priority='normal',
                title='Nouveau message du conseiller',
                message=preview,
                link='/dashboard/messages/',
                payload={'room_id': room.id, 'message_id': msg.id},
            )
            _broadcast_staff_inbox(msg)
            # Mark all student messages in this room as seen
            room.messages.filter(status='sent').exclude(sender=request.user).update(status='seen', seen_at=timezone.now())
            return redirect('admin_panel:chat_detail', pk=pk)

    # Mark as seen on open
    room.messages.filter(status='sent').exclude(sender=request.user).update(status='seen', seen_at=timezone.now())
    chat_messages = room.messages.select_related('sender', 'reply_to', 'reply_to__sender').all()

    ctx.update({
        'room': room,
        'chat_messages': chat_messages,
    })
    return render(request, 'admin_panel/chat_detail.html', ctx)


@staff_required
@require_POST
def room_toggle_urgent(request, pk):
    room = get_object_or_404(ChatRoom, pk=pk)
    room.is_urgent = not room.is_urgent
    room.save(update_fields=['is_urgent'])
    messages.success(request, 'Priorite de conversation mise a jour.')
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('admin_panel:messages')


@staff_required
@require_POST
def rooms_bulk_urgent(request):
    action = request.POST.get('action', '').strip()
    room_ids = request.POST.getlist('room_ids')
    if not room_ids:
        messages.error(request, 'Selectionnez au moins une conversation.')
        return redirect('admin_panel:messages')

    rooms = ChatRoom.objects.filter(pk__in=room_ids)
    if action == 'mark_urgent':
        updated = rooms.update(is_urgent=True)
    elif action == 'clear_urgent':
        updated = rooms.update(is_urgent=False)
    elif action == 'toggle':
        updated = 0
        for room in rooms:
            room.is_urgent = not room.is_urgent
            room.save(update_fields=['is_urgent'])
            updated += 1
    else:
        messages.error(request, 'Action invalide.')
        return redirect('admin_panel:messages')

    messages.success(request, f'Priorite mise a jour pour {updated} conversation(s).')
    return redirect('admin_panel:messages')


@staff_required
@require_POST
def message_toggle_priority(request, pk):
    msg = get_object_or_404(Message.objects.select_related('room'), pk=pk)
    msg.is_priority = not msg.is_priority
    msg.save(update_fields=['is_priority'])
    messages.success(request, 'Priorite du message mise a jour.')
    return redirect('admin_panel:chat_detail', pk=msg.room_id)


# ── 8. Subscriptions & Payments ─────────────────────────────────────

@staff_required
def subscriptions_list(request):
    ctx = _get_admin_context(request.user)

    qs = Subscription.objects.select_related('user', 'plan').order_by('-created_at')

    plan_filter = request.GET.get('plan', '')
    if plan_filter:
        if plan_filter.isdigit():
            qs = qs.filter(plan_id=int(plan_filter))
        else:
            qs = qs.filter(plan__slug=plan_filter)

    status_filter = request.GET.get('status', '')
    if status_filter:
        qs = qs.filter(status=status_filter)

    ctx.update({
        'subscriptions': qs,
        'plan_filter': plan_filter,
        'status_filter': status_filter,
        'plans': Plan.objects.filter(is_active=True),
        'sub_status_choices': Subscription.STATUS_CHOICES,
    })
    return render(request, 'admin_panel/subscriptions.html', ctx)


@staff_required
@require_POST
def subscription_update(request, pk):
    sub = get_object_or_404(Subscription, pk=pk)
    new_status = request.POST.get('status')
    if new_status in dict(Subscription.STATUS_CHOICES):
        sub.status = new_status
        if new_status == 'active' and not sub.paid_at:
            sub.paid_at = timezone.now()
        sub.save(update_fields=['status', 'paid_at'])

        sub.user.has_active_plan = (new_status == 'active')
        sub.user.save(update_fields=['has_active_plan'])

        dispatch_notification(
            user=sub.user,
            created_by=request.user,
            notification_type='payment_success' if new_status == 'active' else 'general',
            category='billing',
            priority='normal',
            title='Abonnement mis a jour',
            message=f'Votre abonnement {sub.plan.name} est maintenant: {sub.get_status_display()}.',
            link='/dashboard/plan/',
        )
        messages.success(request, f'Abonnement mis a jour: {sub.get_status_display()}')
    return redirect('admin_panel:subscriptions')


# ── 9. Plans Management ─────────────────────────────────────────────

@staff_required
def plans_list(request):
    ctx = _get_admin_context(request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            name = request.POST.get('name', '').strip()
            if name:
                features_raw = request.POST.get('features', '[]').strip()
                try:
                    features = json.loads(features_raw)
                except json.JSONDecodeError:
                    features = [f.strip() for f in features_raw.split('\n') if f.strip()]
                Plan.objects.create(
                    name=name,
                    slug=slugify(name),
                    description=request.POST.get('description', '').strip(),
                    price=request.POST.get('price', 0),
                    features=features,
                    is_active='is_active' in request.POST,
                    order=Plan.objects.count(),
                )
                messages.success(request, 'Plan cree.')
            return redirect('admin_panel:plans')

        elif action == 'edit':
            plan = get_object_or_404(Plan, pk=request.POST.get('pk'))
            plan.name = request.POST.get('name', '').strip() or plan.name
            plan.description = request.POST.get('description', '').strip()
            plan.price = request.POST.get('price', plan.price)
            plan.is_active = 'is_active' in request.POST
            features_raw = request.POST.get('features', '').strip()
            try:
                plan.features = json.loads(features_raw)
            except json.JSONDecodeError:
                plan.features = [f.strip() for f in features_raw.split('\n') if f.strip()]
            plan.save()
            messages.success(request, 'Plan modifie.')
            return redirect('admin_panel:plans')

        elif action == 'delete':
            plan = get_object_or_404(Plan, pk=request.POST.get('pk'))
            if not plan.subscription_set.exists():
                plan.delete()
                messages.success(request, 'Plan supprime.')
            else:
                messages.error(request, 'Ce plan a des abonnes, il ne peut pas etre supprime.')
            return redirect('admin_panel:plans')

    ctx['plans_list'] = Plan.objects.annotate(sub_count=Count('subscription')).order_by('order')
    return render(request, 'admin_panel/plans.html', ctx)


# ── 10. Notifications ───────────────────────────────────────────────

@staff_required
def notifications_list(request):
    ctx = _get_admin_context(request.user)
    platform_settings = PlatformSetting.get_solo()

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        message_text = request.POST.get('message', '').strip()
        target = request.POST.get('target', '')

        if title and message_text:
            if target in {'all', 'active'} and not platform_settings.broadcast_enabled:
                messages.error(request, 'La diffusion globale est desactivee dans les parametres.')
                return redirect('admin_panel:notifications')
            students_base = _students_queryset()
            if target == 'all':
                students = students_base
            elif target == 'active':
                students = students_base.filter(subscription__status='active')
            elif target.isdigit():
                students = students_base.filter(pk=target)
            else:
                students = CustomUser.objects.none()

            selected_students = list(students)
            dispatch_bulk(
                selected_students,
                created_by=request.user,
                notification_type='general',
                category='system',
                priority='low',
                title=title,
                message=message_text,
                link='/dashboard/',
            )
            count = len(selected_students)
            messages.success(request, f'Notification envoyee a {count} etudiant(s).')
            return redirect('admin_panel:notifications')

    sent = Notification.objects.order_by('-created_at')[:50]
    my_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:20]
    students = _students_queryset().order_by('email')

    ctx.update({
        'sent_notifications': sent,
        'my_notifications': my_notifications,
        'my_unread_notifications': Notification.objects.filter(user=request.user, is_read=False).count(),
        'students': students,
        'platform_settings': platform_settings,
    })
    return render(request, 'admin_panel/notifications.html', ctx)


@staff_required
@require_POST
def notification_mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    if not notif.is_read:
        notif.is_read = True
        notif.read_at = timezone.now()
        notif.save(update_fields=['is_read', 'read_at'])
    return redirect(request.POST.get('next') or 'admin_panel:notifications')


@staff_required
@require_POST
def notification_mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True, read_at=timezone.now())
    return redirect(request.POST.get('next') or 'admin_panel:notifications')


# ── 11. Settings ─────────────────────────────────────────────────────

@staff_required
def settings_view(request):
    ctx = _get_admin_context(request.user)
    platform_settings = PlatformSetting.get_solo()

    if request.method == 'POST':
        form_type = request.POST.get('form_type', 'profile')
        if form_type == 'profile':
            user = request.user
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name = request.POST.get('last_name', '').strip()
            user.save(update_fields=['first_name', 'last_name'])
            messages.success(request, 'Profil mis a jour.')
        elif form_type == 'platform':
            platform_settings.platform_name = request.POST.get('platform_name', '').strip() or 'Visanextstep'
            platform_settings.support_email = request.POST.get('support_email', '').strip()
            platform_settings.support_phone = request.POST.get('support_phone', '').strip()
            platform_settings.default_student_language = request.POST.get('default_student_language', 'fr')
            platform_settings.maintenance_mode = 'maintenance_mode' in request.POST
            platform_settings.broadcast_enabled = 'broadcast_enabled' in request.POST
            platform_settings.save()
            cache.delete('platform_maintenance_mode')
            messages.success(request, 'Parametres de la plateforme mis a jour.')
        return redirect('admin_panel:settings')

    # Google Calendar status
    from django.conf import settings as django_settings
    creds_path = getattr(django_settings, 'GOOGLE_CALENDAR_CREDENTIALS_FILE', None)
    token_path = django_settings.BASE_DIR / 'env' / 'google-token.json'
    google_configured = creds_path and creds_path.exists() if creds_path else False
    google_token_exists = token_path.exists()

    ctx.update({
        'google_configured': google_configured,
        'google_token_exists': google_token_exists,
        'total_students': _students_queryset().count(),
        'total_documents': Document.objects.count(),
        'total_meetings': Meeting.objects.count(),
        'platform_settings': platform_settings,
    })
    return render(request, 'admin_panel/settings.html', ctx)

