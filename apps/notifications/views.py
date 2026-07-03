import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Notification, NotificationPreference, PushDevice, default_category_channels


@login_required
def list_notifications(request):
    if request.user.is_staff or request.user.is_advisor:
        return redirect('admin_panel:notifications')

    notifications_qs = Notification.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(notifications_qs, 20)
    page = paginator.get_page(request.GET.get('page'))

    prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)
    categories = prefs.category_channels or {}
    default_channels = default_category_channels()
    preference_categories = []
    for category in ('document', 'chat', 'meeting', 'billing', 'system'):
        cfg = categories.get(category, default_channels.get(category, {'in_app': True, 'email': False, 'push': False}))
        preference_categories.append({
            'key': category,
            'label': category.title(),
            'cfg': cfg,
        })
    return render(request, 'notifications/list.html', {
        'notifications': page.object_list,
        'notifications_page': page,
        'notification_prefs': prefs,
        'preference_categories': preference_categories,
        'notifications_unread_count': notifications_qs.filter(is_read=False).count(),
    })


@login_required
@require_POST
def mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    if not notif.is_read:
        notif.is_read = True
        notif.read_at = timezone.now()
        notif.save(update_fields=['is_read', 'read_at'])
    return redirect(request.POST.get('next') or 'notifications:list')


@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True, read_at=timezone.now())
    return redirect(request.POST.get('next') or 'notifications:list')


@login_required
@require_POST
def update_preferences(request):
    prefs, _ = NotificationPreference.objects.get_or_create(user=request.user)
    prefs.in_app_enabled = 'in_app_enabled' in request.POST
    prefs.email_enabled = 'email_enabled' in request.POST
    prefs.push_enabled = 'push_enabled' in request.POST
    prefs.digest_enabled = 'digest_enabled' in request.POST

    categories = prefs.category_channels or {}
    default_channels = default_category_channels()
    for category in ('document', 'chat', 'meeting', 'billing', 'system'):
        category_cfg = categories.get(category, default_channels.get(category, {'in_app': True, 'email': False, 'push': False}))
        category_cfg['in_app'] = f'{category}_in_app' in request.POST
        category_cfg['email'] = f'{category}_email' in request.POST
        category_cfg['push'] = f'{category}_push' in request.POST
        categories[category] = category_cfg
    prefs.category_channels = categories
    prefs.save()
    return redirect(request.POST.get('next') or 'notifications:list')


@login_required
@require_POST
def push_register(request):
    data = {}
    if request.content_type and 'application/json' in request.content_type:
        try:
            data = json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'ok': False, 'error': 'invalid_json'}, status=400)
    else:
        data = request.POST

    token = (data.get('token') or '').strip()
    platform = (data.get('platform') or 'web').strip().lower()
    if platform not in {'ios', 'android', 'web'}:
        platform = 'web'

    if not token:
        return JsonResponse({'ok': False, 'error': 'missing_token'}, status=400)

    device, _ = PushDevice.objects.update_or_create(
        token=token,
        defaults={
            'user': request.user,
            'platform': platform,
            'is_active': True,
        },
    )
    return JsonResponse({'ok': True, 'device_id': device.id})


@login_required
@require_POST
def push_unregister(request):
    data = {}
    if request.content_type and 'application/json' in request.content_type:
        try:
            data = json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'ok': False, 'error': 'invalid_json'}, status=400)
    else:
        data = request.POST

    token = (data.get('token') or '').strip()
    if not token:
        return JsonResponse({'ok': False, 'error': 'missing_token'}, status=400)

    updated = PushDevice.objects.filter(user=request.user, token=token, is_active=True).update(is_active=False)
    return JsonResponse({'ok': True, 'updated': updated})
