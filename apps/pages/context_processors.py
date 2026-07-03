from .models import SiteSettings

def site_settings(request):
    """Inject SiteSettings into all templates for Visanextstep."""
    try:
        settings = SiteSettings.get_solo()
    except Exception:
        settings = None
    return {
        'site_settings': settings
    }
