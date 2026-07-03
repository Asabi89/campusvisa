"""
One-time command to authorize Visanextstep with your Google account.

Usage:
    python manage.py google_auth

This opens a browser window where you sign in with your Gmail and grant
calendar access. The resulting token is saved to env/google-token.json
and reused automatically for all future Meet link generation.
"""

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Authorize Visanextstep with your Google account (one-time setup)'

    def handle(self, *args, **options):
        from google_auth_oauthlib.flow import InstalledAppFlow

        SCOPES = ['https://www.googleapis.com/auth/calendar']
        client_secret = Path(settings.BASE_DIR) / 'env' / 'google-client-secret.json'
        token_path = Path(settings.BASE_DIR) / 'env' / 'google-token.json'

        if not client_secret.exists():
            self.stderr.write(self.style.ERROR(
                f'\nMissing {client_secret}\n\n'
                'Go to https://console.cloud.google.com/apis/credentials\n'
                '  1. Click "Create Credentials" → "OAuth client ID"\n'
                '  2. Application type: "Desktop app"\n'
                '  3. Download the JSON → save as env/google-client-secret.json\n'
            ))
            return

        flow = InstalledAppFlow.from_client_secrets_file(str(client_secret), SCOPES)
        creds = flow.run_local_server(port=8090)

        token_path.write_text(creds.to_json())
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Token saved to {token_path}\n'
            'Google Meet links will now be generated automatically.\n'
        ))

