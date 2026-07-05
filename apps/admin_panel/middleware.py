from django.conf import settings
from django.core.cache import cache
from django.db.utils import OperationalError, ProgrammingError
from django.shortcuts import redirect, render


class SubdomainMiddleware:
    """Route requests on the `staff.` subdomain to the staff URL config."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0].lower().strip('.')
        subdomain_prefix = getattr(settings, 'STAFF_SUBDOMAIN_PREFIX', 'staff').lower().strip('.')
        if host.startswith(f'{subdomain_prefix}.'):
            request.urlconf = settings.STAFF_URLCONF
            request.is_staff_portal = True
        else:
            request.is_staff_portal = False
        return self.get_response(request)


class MaintenanceModeMiddleware:
    """Return a maintenance page for non-staff users when maintenance mode is enabled."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path or '/'
        host = request.get_host().split(':')[0].lower().strip('.')

        staff_subdomain_prefix = getattr(settings, 'STAFF_SUBDOMAIN_PREFIX', 'staff').lower().strip('.')
        is_staff_host = host.startswith(f'{staff_subdomain_prefix}.')
        student_space_prefixes = getattr(
            settings,
            'STUDENT_SPACE_PATH_PREFIXES',
            (
                '/dashboard/',
                '/onboarding/',
                '/plans/',
                '/documents/',
                '/chat/',
                '/meetings/',
            ),
        )

        if request.user.is_authenticated and (
            request.user.is_staff or request.user.is_superuser or request.user.is_advisor
        ):
            is_admin_host = host.startswith('admin.')
            if not is_staff_host and not is_admin_host:
                if any(path.startswith(prefix) for prefix in student_space_prefixes):
                    # Force staff/advisors to use the staff portal only.
                    return redirect('https://staff.nextstepc.com/')

        # Keep static/media/admin/staff tooling reachable while maintenance is active.
        if (
            path.startswith('/static/')
            or path.startswith('/media/')
            or path.startswith('/admin/')
            or path.startswith('/management/')
            or getattr(request, 'is_staff_portal', False)
        ):
            return self.get_response(request)

        if request.user.is_authenticated and (
            request.user.is_staff or request.user.is_superuser or request.user.is_advisor
        ):
            return self.get_response(request)

        maintenance_mode = cache.get('platform_maintenance_mode')
        if maintenance_mode is None:
            try:
                from .models import PlatformSetting
                maintenance_mode = PlatformSetting.get_solo().maintenance_mode
                cache.set('platform_maintenance_mode', maintenance_mode, 30)
            except (OperationalError, ProgrammingError):
                maintenance_mode = False

        if maintenance_mode:
            return render(request, 'maintenance.html', status=503)

        return self.get_response(request)
