from functools import wraps

from django.shortcuts import redirect


def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin_panel:login')
        if not (request.user.is_staff or request.user.is_advisor):
            return redirect('admin_panel:login')
        return view_func(request, *args, **kwargs)
    return wrapper
