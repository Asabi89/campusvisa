import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.chat.models import ChatRoom, Message
from apps.documents.models import Document, DocumentType
from apps.meetings.models import AvailableSlot, Meeting
from apps.notifications.models import Notification
from apps.notifications.services import notify_staff
from apps.onboarding.models import OnboardingResponse
from apps.plans.models import Subscription


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


def _build_calendar_url(user, slot, topic, meet_link=''):
    """Build a Google Calendar 'Add to Calendar' URL for the meeting."""
    from urllib.parse import quote
    date_str = slot.date.strftime('%Y%m%d')
    start_str = slot.start_time.strftime('%H%M%S')
    end_str = slot.end_time.strftime('%H%M%S')
    title = quote(f'Visanextstep — {topic}')
    details = f'Rendez-vous avec {user.email}'
    if meet_link:
        details += f'\n\nLien Meet : {meet_link}'
    return (
        f'https://calendar.google.com/calendar/render?action=TEMPLATE'
        f'&text={title}'
        f'&dates={date_str}T{start_str}/{date_str}T{end_str}'
        f'&details={quote(details)}'
        f'&add={quote(user.email)}'
    )


def _generate_meet_link(user, slot, topic):
    """Generate a Google Meet link and a calendar URL for the meeting.

    Returns a tuple (meet_link, calendar_link).
    meet_link is the actual Google Meet URL (or empty string on failure).
    calendar_link is always a Google Calendar 'Add to Calendar' URL.
    """
    meet_link = ''
    try:
        token_path = settings.BASE_DIR / 'env' / 'google-token.json'
        calendar_id = getattr(settings, 'GOOGLE_CALENDAR_ID', 'primary')

        if token_path.exists():
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build

            creds = Credentials.from_authorized_user_file(
                str(token_path), ['https://www.googleapis.com/auth/calendar']
            )
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                token_path.write_text(creds.to_json())

            service = build('calendar', 'v3', credentials=creds)

            start_dt = timezone.datetime.combine(slot.date, slot.start_time).isoformat()
            end_dt = timezone.datetime.combine(slot.date, slot.end_time).isoformat()

            event_body = {
                'summary': f'Visanextstep — {topic}',
                'description': f'Rendez-vous Visanextstep avec {user.email}',
                'start': {'dateTime': start_dt, 'timeZone': 'Africa/Porto-Novo'},
                'end': {'dateTime': end_dt, 'timeZone': 'Africa/Porto-Novo'},
                'conferenceData': {
                    'createRequest': {
                        'requestId': uuid.uuid4().hex,
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'},
                    }
                },
                'attendees': [{'email': user.email}],
            }

            created = service.events().insert(
                calendarId=calendar_id,
                body=event_body,
                conferenceDataVersion=1,
            ).execute()

            meet_link = created.get('hangoutLink', '')
    except Exception:
        pass

    calendar_link = _build_calendar_url(user, slot, topic, meet_link)
    return meet_link, calendar_link


def _get_plan_context(user):
    subscription = None
    plan_slug = 'none'
    plan_name = 'Aucun plan'
    plan_status = None

    try:
        subscription = user.subscription
        plan_slug = subscription.plan.slug
        plan_name = subscription.plan.name
        plan_status = subscription.status
    except Subscription.DoesNotExist:
        pass

    can_upload = plan_slug in ('standard', 'premium')
    can_chat = plan_slug in ('standard', 'premium')
    can_meet = plan_slug in ('standard', 'premium')
    meetings_limit = {'standard': 3, 'premium': -1}.get(plan_slug, 0)
    has_dedicated_advisor = plan_slug == 'premium'

    needs_assistance = False
    try:
        needs_assistance = user.onboarding.needs_assistance
    except OnboardingResponse.DoesNotExist:
        pass

    unread_count = Notification.objects.filter(user=user, is_read=False).count()

    return {
        'subscription': subscription,
        'plan_slug': plan_slug,
        'plan_name': plan_name,
        'plan_status': plan_status,
        'can_upload': can_upload,
        'can_chat': can_chat,
        'can_meet': can_meet,
        'meetings_limit': meetings_limit,
        'has_dedicated_advisor': has_dedicated_advisor,
        'needs_assistance': needs_assistance,
        'unread_count': unread_count,
    }


@login_required
def overview(request):
    ctx = _get_plan_context(request.user)

    steps = [
        {'label': 'Inscription', 'done': True},
        {'label': 'Evaluation', 'done': request.user.has_completed_onboarding},
        {'label': 'Plan choisi', 'done': ctx['subscription'] is not None},
        {'label': 'Paiement confirme', 'done': ctx['plan_status'] == 'active'},
    ]
    if ctx['can_upload']:
        doc_count = Document.objects.filter(user=request.user).count()
        steps.append({'label': 'Documents soumis', 'done': doc_count > 0})
    if ctx['can_meet']:
        has_meeting = Meeting.objects.filter(student=request.user).exists()
        steps.append({'label': 'Rendez-vous planifie', 'done': has_meeting})

    completed_steps = sum(1 for s in steps if s['done'])
    progress_pct = round(completed_steps / len(steps) * 100) if steps else 0

    recent_notifs = Notification.objects.filter(user=request.user)[:5]

    ctx.update({
        'steps': steps,
        'progress_pct': progress_pct,
        'completed_steps': completed_steps,
        'total_steps': len(steps),
        'recent_notifs': recent_notifs,
    })
    return render(request, 'dashboard/overview.html', ctx)


@login_required
def documents(request):
    ctx = _get_plan_context(request.user)

    doc_types = DocumentType.objects.all()
    user_docs = Document.objects.filter(user=request.user).select_related('document_type')
    user_doc_type_ids = set(user_docs.filter(document_type__isnull=False).values_list('document_type_id', flat=True))
    custom_docs = user_docs.filter(is_custom=True)

    doc_items = []
    for dt in doc_types:
        uploaded = user_docs.filter(document_type=dt).first()
        doc_items.append({
            'doc_type': dt,
            'uploaded': uploaded,
            'status': uploaded.status if uploaded else None,
        })

    default_doc_names = [
        'Passeport valide', 'Releves de notes', 'Diplomes',
        'Attestation de pre-inscription', 'Justificatif financier',
        "Photo d'identite", 'Formulaire Campus France',
    ]
    ctx.update({
        'doc_items': doc_items,
        'custom_docs': custom_docs,
        'default_doc_names': default_doc_names,
    })
    return render(request, 'dashboard/documents.html', ctx)


@login_required
def document_upload(request, slug):
    ctx = _get_plan_context(request.user)
    if not ctx['can_upload']:
        return redirect('dashboard:documents')

    is_custom = slug == 'autre'
    doc_type = None
    existing_doc = None

    if not is_custom:
        doc_type = get_object_or_404(DocumentType, slug=slug)
        existing_doc = Document.objects.filter(user=request.user, document_type=doc_type).first()

    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            if existing_doc:
                existing_doc.file = uploaded_file
                existing_doc.status = 'pending'
                existing_doc.admin_comment = ''
                existing_doc.save()
                uploaded_doc = existing_doc
            else:
                uploaded_doc = Document(user=request.user, file=uploaded_file)
                if is_custom:
                    uploaded_doc.is_custom = True
                    uploaded_doc.custom_name = request.POST.get('custom_name', 'Document').strip() or 'Document'
                else:
                    uploaded_doc.document_type = doc_type
                uploaded_doc.save()
            doc_label = (
                uploaded_doc.custom_name if uploaded_doc.is_custom
                else (uploaded_doc.document_type.name if uploaded_doc.document_type_id else 'Document')
            )
            notify_staff(
                created_by=request.user,
                notification_type='staff_new_document',
                category='document',
                priority='high',
                title='Nouveau document soumis',
                message=f'{request.user.email} a televerse "{doc_label}".',
                link=f'/documents/student/{request.user.id}/',
                payload={'student_id': request.user.id, 'document_id': uploaded_doc.id},
            )
            messages.success(request, 'Document televerse avec succes.')
            return redirect('dashboard:documents')

    ctx.update({
        'is_custom': is_custom,
        'doc_type': doc_type,
        'existing_doc': existing_doc,
    })
    return render(request, 'dashboard/document_upload.html', ctx)


@login_required
def chat_view(request):
    ctx = _get_plan_context(request.user)

    if ctx['can_chat']:
        room, _ = ChatRoom.objects.get_or_create(
            student=request.user,
            defaults={'is_urgent': ctx['needs_assistance']},
        )

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
                    is_priority=ctx['needs_assistance'],
                )
                notify_staff(
                    created_by=request.user,
                    notification_type='staff_new_message',
                    category='chat',
                    priority='normal',
                    title='Nouveau message etudiant',
                    message=f'{request.user.email} a envoye un message.',
                    link=f'/messages/{room.id}/',
                    payload={'student_id': request.user.id, 'room_id': room.id, 'message_id': msg.id},
                )
                _broadcast_staff_inbox(msg)
                return redirect('dashboard:messages')

        chat_messages = room.messages.select_related('sender', 'reply_to', 'reply_to__sender').all()
        ctx.update({
            'room': room,
            'chat_messages': chat_messages,
        })

    return render(request, 'dashboard/messages.html', ctx)


@login_required
def meetings(request):
    ctx = _get_plan_context(request.user)

    # Delete past meetings
    Meeting.objects.filter(
        student=request.user, slot__date__lt=timezone.now().date(),
    ).delete()

    user_meetings = Meeting.objects.filter(student=request.user).select_related('slot')
    for m in user_meetings:
        updated_fields = []
        if not m.calendar_link and m.slot:
            m.calendar_link = _build_calendar_url(request.user, m.slot, m.topic, m.meeting_link)
            updated_fields.append('calendar_link')
        if m.meeting_link and 'calendar.google.com' in m.meeting_link:
            m.meeting_link = ''
            updated_fields.append('meeting_link')
        if updated_fields:
            m.save(update_fields=updated_fields)
    meetings_count = user_meetings.count()

    can_book = False
    if ctx['can_meet']:
        if ctx['meetings_limit'] == -1 or meetings_count < ctx['meetings_limit']:
            can_book = True

    available_slots = []
    if can_book:
        available_slots = list(
            AvailableSlot.objects.filter(is_booked=False, date__gte=timezone.now().date())
        )

    if request.method == 'POST' and can_book:
        slot_id = request.POST.get('slot_id')
        topic = request.POST.get('topic', '').strip()
        if slot_id and topic:
            try:
                slot = AvailableSlot.objects.get(id=slot_id, is_booked=False)
                meet_link, calendar_link = _generate_meet_link(request.user, slot, topic)
                Meeting.objects.create(
                    student=request.user, slot=slot, topic=topic,
                    meeting_link=meet_link,
                    calendar_link=calendar_link,
                )
                slot.is_booked = True
                slot.save()
                notify_staff(
                    created_by=request.user,
                    notification_type='staff_meeting_booked',
                    category='meeting',
                    priority='high',
                    title='Nouveau rendez-vous reserve',
                    message=f'{request.user.email} a reserve le {slot.date} ({slot.start_time.strftime("%H:%M")}).',
                    link='/meetings/',
                    payload={'student_id': request.user.id, 'slot_id': slot.id},
                )
                messages.success(request, 'Rendez-vous planifie avec succes.')
                return redirect('dashboard:meetings')
            except AvailableSlot.DoesNotExist:
                messages.error(request, "Ce creneau n'est plus disponible.")
            except IntegrityError:
                slot.is_booked = True
                slot.save()
                messages.error(request, "Ce creneau n'est plus disponible.")

    ctx.update({
        'user_meetings': user_meetings,
        'meetings_count': meetings_count,
        'can_book': can_book,
        'available_slots': available_slots,
    })
    return render(request, 'dashboard/meetings.html', ctx)


@login_required
def profile(request):
    ctx = _get_plan_context(request.user)

    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.phone = request.POST.get('phone', '').strip()
        user.save(update_fields=['first_name', 'last_name', 'phone'])
        messages.success(request, 'Profil mis a jour.')
        return redirect('dashboard:profile')

    return render(request, 'dashboard/profile.html', ctx)


@login_required
def avatar_upload(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        request.user.avatar = request.FILES['avatar']
        request.user.save(update_fields=['avatar'])
        messages.success(request, 'Photo de profil mise a jour.')
    return redirect('dashboard:profile')


@login_required
def plan_detail(request):
    ctx = _get_plan_context(request.user)

    from apps.onboarding.views import PLAN_PRICES
    from apps.plans.views import PLAN_FEATURES

    all_plans = [
        {'name': 'Basique', 'slug': 'basic', 'price': PLAN_PRICES['basic'], 'features': PLAN_FEATURES['basic']},
        {'name': 'Standard', 'slug': 'standard', 'price': PLAN_PRICES['standard'], 'features': PLAN_FEATURES['standard']},
        {'name': 'Premium', 'slug': 'premium', 'price': PLAN_PRICES['premium'], 'features': PLAN_FEATURES['premium']},
    ]

    ctx.update({'all_plans': all_plans})
    return render(request, 'dashboard/plan.html', ctx)

