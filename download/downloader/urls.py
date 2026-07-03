from django.urls import path

from . import views

app_name = "downloader"

urlpatterns = [
    path("", views.index, name="index"),
    path("api/preview/", views.preview_urls, name="preview"),
    path("api/start/", views.start_download, name="start"),
    path("api/status/<str:job_id>/", views.job_status, name="status"),
    path("files/<str:filename>/", views.download_file, name="file"),
]

