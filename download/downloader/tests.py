from django.test import TestCase
from django.urls import reverse

from .services import detect_platform, extract_all_urls


class DownloaderPagesTests(TestCase):
    def test_home_page(self):
        response = self.client.get(reverse("downloader:index"))
        self.assertEqual(response.status_code, 200)

    def test_preview_api_rejects_empty_input(self):
        response = self.client.post(
            reverse("downloader:preview"),
            data='{"urls":[]}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)


class DownloaderLogicTests(TestCase):
    def test_platform_detection(self):
        self.assertEqual(detect_platform("https://www.pinterest.com/pin/123/"), "pinterest")
        self.assertEqual(detect_platform("https://www.tiktok.com/@user/video/111"), "tiktok")
        self.assertEqual(detect_platform("https://www.facebook.com/reel/abc"), "facebook")
        self.assertEqual(detect_platform("https://youtu.be/xyz"), "youtube")

    def test_extract_urls(self):
        urls = extract_all_urls(
            "a https://youtu.be/xyz and https://pin.it/aa and https://pin.it/aa"
        )
        self.assertEqual(len(urls), 2)
