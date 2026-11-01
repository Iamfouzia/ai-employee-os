from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/calendar.events",
]


PROJECT_ROOT = Path(__file__).resolve().parents[3]

CREDENTIALS_FILE = (
    PROJECT_ROOT
    / ".secrets"
    / "google"
    / "credentials.json"
)

TOKEN_FILE = (
    PROJECT_ROOT
    / ".secrets"
    / "google"
    / "token.json"
)


def _get_google_credentials() -> Credentials:
    """
    Load, refresh, or create Google OAuth credentials.

    The same credentials can be reused by Gmail and
    Google Calendar integrations.
    """

    credentials = None

    if TOKEN_FILE.exists():
        credentials = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES,
        )

    if not credentials or not credentials.valid:

        if (
            credentials
            and credentials.expired
            and credentials.refresh_token
        ):
            credentials.refresh(Request())

        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    f"Google credentials not found at: "
                    f"{CREDENTIALS_FILE}"
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES,
            )

            credentials = flow.run_local_server(
                port=0,
            )

        TOKEN_FILE.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        TOKEN_FILE.write_text(
            credentials.to_json(),
            encoding="utf-8",
        )

    return credentials


def get_google_credentials() -> Credentials:
    """
    Return authenticated Google credentials for
    services such as Google Calendar.
    """

    return _get_google_credentials()


def get_gmail_service():
    """
    Return an authenticated Gmail API service.
    """

    credentials = _get_google_credentials()

    return build(
        "gmail",
        "v1",
        credentials=credentials,
    )