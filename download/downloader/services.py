import copy
import json
import os
import re
import subprocess
import threading
import time
import uuid
from pathlib import Path

import requests
from django.conf import settings

DOWNLOAD_DIR = Path(settings.BASE_DIR) / "downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

JOBS = {}
JOBS_LOCK = threading.Lock()

_UC = r'[^\s"\'<>\[\](){}]+'

PLATFORM_PATTERNS = {
    "pinterest": [
        r"https?://(?:www\.|[a-z]{2}\.)?pinterest\.[a-z]{2,3}/" + _UC,
        r"https?://pin\.it/" + _UC,
    ],
    "tiktok": [
        r"https?://(?:www\.|vm\.|vt\.)?tiktok\.com/" + _UC,
    ],
    "facebook": [
        r"https?://(?:[a-zA-Z0-9-]+\.)?facebook\.com/" + _UC,
        r"https?://fb\.watch/" + _UC,
    ],
    "youtube": [
        r"https?://(?:www\.|m\.)?youtube\.com/watch\?" + _UC,
        r"https?://youtu\.be/" + _UC,
        r"https?://(?:www\.)?youtube\.com/shorts/" + _UC,
    ],
}


def detect_platform(url):
    for platform, patterns in PLATFORM_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, url):
                return platform
    return "unknown"


def extract_all_urls(raw_text):
    found = []
    seen = set()
    for patterns in PLATFORM_PATTERNS.values():
        for pattern in patterns:
            for url in re.findall(pattern, raw_text):
                cleaned = url.rstrip('.,;:!?)\'"')
                if cleaned not in seen:
                    seen.add(cleaned)
                    found.append(cleaned)
    return found


def resolve_short_url(url):
    try:
        response = requests.head(
            url,
            allow_redirects=True,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        return response.url
    except Exception:
        return url


def get_pinterest_video_info(pin_url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.pinterest.com/",
    }
    try:
        source_url = resolve_short_url(pin_url) if "pin.it" in pin_url else pin_url
        response = requests.get(source_url, headers=headers, timeout=15)
        html = response.text

        video_patterns = [
            r'"url":\s*"(https://v\d+\.pinimg\.com/videos/[^"]+\.mp4[^"]*)"',
            r'"(https://v\d+\.pinimg\.com/videos/[^"]+\.mp4[^"]*)"',
            r"(https://v\d+\.pinimg\.com/[^\s\"']+\.mp4[^\s\"']*)",
        ]
        video_url = None
        for pattern in video_patterns:
            matches = re.findall(pattern, html)
            if matches:
                video_url = matches[0].replace("\\u0026", "&").replace("\\/", "/")
                break

        thumb_match = re.search(r'<meta\s+property="og:image"\s+content="([^"]+)"', html)
        thumbnail = thumb_match.group(1) if thumb_match else None

        title_match = re.search(r"<title>(.*?)</title>", html, flags=re.IGNORECASE | re.DOTALL)
        title = re.sub(r"\s+", " ", title_match.group(1)).strip() if title_match else "Pinterest Video"

        if not video_url:
            pws = re.search(r"__PWS_DATA__\s*=\s*(\{.+?\});", html, re.DOTALL)
            if pws:
                mp4s = re.findall(r"https://v\d+\.pinimg\.com/[^\s\"'\\]+\.mp4", pws.group(1))
                if mp4s:
                    video_url = mp4s[0]

        if not video_url:
            return None, None, title, "No video stream found on this Pinterest link."
        return video_url, thumbnail, title, None
    except requests.exceptions.Timeout:
        return None, None, "Pinterest Video", "Pinterest timeout."
    except Exception as exc:
        return None, None, "Pinterest Video", str(exc)


def _preview_with_ytdlp(url):
    command = [
        "yt-dlp",
        "--skip-download",
        "--no-warnings",
        "--dump-single-json",
        url,
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=80)
        if result.returncode != 0:
            err = result.stderr.strip().splitlines()
            msg = err[-1] if err else "Unable to build preview."
            return None, msg

        info = json.loads(result.stdout or "{}")
        title = info.get("title") or "Untitled video"
        thumbnail = info.get("thumbnail")
        preview_video_url = info.get("url")
        return {
            "title": title,
            "thumbnail": thumbnail,
            "preview_video_url": preview_video_url,
        }, None
    except FileNotFoundError:
        return None, "yt-dlp was not found. Install it with: pip install yt-dlp"
    except subprocess.TimeoutExpired:
        return None, "Preview timeout exceeded."
    except Exception as exc:
        return None, str(exc)


def build_preview_item(url):
    platform = detect_platform(url)
    item = {
        "url": url,
        "platform": platform,
        "title": "Untitled video",
        "thumbnail": None,
        "preview_video_url": None,
        "can_download": platform in {"pinterest", "tiktok", "facebook", "youtube"},
        "warning": None,
    }
    if platform == "pinterest":
        video_url, thumbnail, title, error = get_pinterest_video_info(url)
        item["title"] = title
        item["thumbnail"] = thumbnail
        item["preview_video_url"] = video_url
        if error:
            item["warning"] = error
        return item

    if platform in {"tiktok", "facebook", "youtube"}:
        info, error = _preview_with_ytdlp(url)
        if info:
            item["title"] = info["title"]
            item["thumbnail"] = info["thumbnail"]
            item["preview_video_url"] = info["preview_video_url"]
        if error:
            item["warning"] = error
        return item

    item["warning"] = "Unsupported URL."
    return item


def build_preview_items(urls):
    return [build_preview_item(url) for url in urls]


def download_pinterest(pin_url, output_template):
    video_url, _, _, error = get_pinterest_video_info(pin_url)
    if error or not video_url:
        return None, 0, error or "Pinterest video URL not found."

    filepath = re.sub(r"%\([^)]+\)s\.[^.]+$", "video.mp4", output_template)
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.pinterest.com/",
    }
    try:
        response = requests.get(video_url, headers=headers, stream=True, timeout=60)
        response.raise_for_status()
        with open(filepath, "wb") as output:
            for chunk in response.iter_content(65536):
                if chunk:
                    output.write(chunk)
        return filepath, os.path.getsize(filepath), None
    except Exception as exc:
        return None, 0, str(exc)


def download_with_ytdlp(url, output_template):
    command = [
        "yt-dlp",
        "--no-playlist",
        "--no-warnings",
        "-f",
        "bestvideo[ext=mp4]+bestaudio/best[ext=mp4]/bestvideo+bestaudio/best",
        "--merge-output-format",
        "mp4",
        "-o",
        output_template,
        "--print",
        "after_move:filepath",
        url,
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=240)
        if result.returncode == 0:
            lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
            if lines:
                filepath = lines[-1]
                if os.path.exists(filepath):
                    return filepath, os.path.getsize(filepath), None

            videos = sorted(
                [
                    os.path.join(DOWNLOAD_DIR, name)
                    for name in os.listdir(DOWNLOAD_DIR)
                    if name.endswith((".mp4", ".mkv", ".webm"))
                ],
                key=os.path.getmtime,
                reverse=True,
            )
            if videos:
                return videos[0], os.path.getsize(videos[0]), None
            return None, 0, "Download finished but output file was not found."

        err_lines = result.stderr.strip().splitlines()
        message = next(
            (line for line in reversed(err_lines) if line and not line.startswith("[")),
            "yt-dlp error.",
        )
        return None, 0, message
    except subprocess.TimeoutExpired:
        return None, 0, "Timeout exceeded (>4 minutes)."
    except FileNotFoundError:
        return None, 0, "yt-dlp was not found. Install it with: pip install yt-dlp"
    except Exception as exc:
        return None, 0, str(exc)


def _run_job(job_id):
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if not job:
            return
        urls = list(job["urls"])
        job["status"] = "running"
        job["done"] = 0

    for index, url in enumerate(urls):
        with JOBS_LOCK:
            job = JOBS.get(job_id)
            if not job:
                return
            item = job["items"][index]
            platform = item["platform"]
            item["status"] = "downloading"
            item["message"] = "Downloading..."

        output_template = str(DOWNLOAD_DIR / f"{platform}_{int(time.time())}_{index}_%(id)s.%(ext)s")
        if platform == "pinterest":
            filepath, size, error = download_pinterest(url, output_template)
        elif platform in {"tiktok", "facebook", "youtube"}:
            filepath, size, error = download_with_ytdlp(url, output_template)
        else:
            filepath, size, error = None, 0, "Unsupported URL."

        with JOBS_LOCK:
            job = JOBS.get(job_id)
            if not job:
                return
            item = job["items"][index]
            if error:
                item["status"] = "error"
                item["message"] = error
            else:
                item["status"] = "done"
                item["message"] = f"Done ({(size / (1024 * 1024)):.1f} MB)"
                item["filename"] = os.path.basename(filepath)
            job["done"] += 1

        time.sleep(0.2)

    with JOBS_LOCK:
        job = JOBS.get(job_id)
        if job:
            job["status"] = "finished"


def create_job(urls):
    job_id = uuid.uuid4().hex
    items = [
        {
            "url": url,
            "platform": detect_platform(url),
            "status": "pending",
            "message": "Queued...",
            "filename": None,
        }
        for url in urls
    ]
    payload = {
        "status": "pending",
        "total": len(urls),
        "done": 0,
        "urls": list(urls),
        "items": items,
        "created_at": int(time.time()),
    }
    with JOBS_LOCK:
        JOBS[job_id] = payload

    threading.Thread(target=_run_job, args=(job_id,), daemon=True).start()
    return job_id, copy.deepcopy(items)


def get_job_snapshot(job_id):
    with JOBS_LOCK:
        payload = JOBS.get(job_id)
        return copy.deepcopy(payload) if payload else None


def resolve_download_path(filename):
    candidate = (DOWNLOAD_DIR / filename).resolve()
    base = DOWNLOAD_DIR.resolve()
    if base not in candidate.parents:
        return None
    if not candidate.exists() or not candidate.is_file():
        return None
    return candidate

