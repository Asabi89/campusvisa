from .models import NextStepSettings

def nextstep_settings(request):
    """Inject NextStepSettings into all templates."""
    try:
        settings = NextStepSettings.get_solo()
    except Exception:
        settings = None
    return {
        'ns_settings': settings
    }
