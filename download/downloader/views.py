import json

from django.http import FileResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .services import (
    build_preview_items,
    create_job,
    extract_all_urls,
    get_job_snapshot,
    resolve_download_path,
)


@require_GET
def index(request):
    return render(request, "downloader/index.html")


@require_POST
def preview_urls(request):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    urls = payload.get("urls")
    if isinstance(urls, list) and urls:
        clean_urls = [str(url).strip() for url in urls if str(url).strip()]
    else:
        raw_text = (payload.get("text") or "").strip()
        clean_urls = extract_all_urls(raw_text)

    if not clean_urls:
        return JsonResponse({"error": "No supported social URL was found in your input."}, status=400)

    clean_urls = clean_urls[:50]
    items = build_preview_items(clean_urls)
    return JsonResponse({"items": items, "total": len(items)})


@require_POST
def start_download(request):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    urls = payload.get("urls")
    if isinstance(urls, list) and urls:
        clean_urls = [str(url).strip() for url in urls if str(url).strip()]
    else:
        raw_text = (payload.get("text") or "").strip()
        clean_urls = extract_all_urls(raw_text)

    if not clean_urls:
        return JsonResponse({"error": "No supported social URL was found in your input."}, status=400)

    clean_urls = clean_urls[:50]
    job_id, items = create_job(clean_urls)
    return JsonResponse({"job_id": job_id, "items": items, "total": len(items)})


@require_GET
def job_status(request, job_id):
    job = get_job_snapshot(job_id)
    if not job:
        return JsonResponse({"error": "Job not found."}, status=404)

    return JsonResponse(
        {
            "status": job["status"],
            "total": job["total"],
            "done": job["done"],
            "items": job["items"],
        }
    )


@require_GET
def download_file(request, filename):
    file_path = resolve_download_path(filename)
    if not file_path:
        return HttpResponseNotFound("File not found.")
    return FileResponse(open(file_path, "rb"), as_attachment=True, filename=file_path.name)
