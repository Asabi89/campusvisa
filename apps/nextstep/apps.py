from django.apps import AppConfig

class NextstepConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.nextstep'
    verbose_name = 'Visa NextStep Consulting'

    def ready(self):
        from django.contrib import admin
        admin.site.site_header = "Nextstep Consulting"
        admin.site.site_title = "Nextstep Consulting Admin"
        admin.site.index_title = "Administration Nextstep Consulting"
