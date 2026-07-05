class SubdomainRoutingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().lower()

        if host.startswith('visa.'):
            request.urlconf = 'config.urls_visa'
        elif host.startswith('staff.'):
            request.urlconf = 'config.urls_staff'
        elif host.startswith('admin.'):
            request.urlconf = 'config.urls_admin'
        else:
            request.urlconf = 'config.urls'

        response = self.get_response(request)
        return response
