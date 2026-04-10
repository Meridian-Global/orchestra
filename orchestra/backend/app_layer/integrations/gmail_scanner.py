import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def scan_inbox(max_results: int = 20) -> list[dict]:
    credentials_path = Path(os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json"))
    token_path = Path(os.getenv("GOOGLE_TOKEN_PATH", "token.json"))

    # Explicitly resolve relative paths from repo root (current working directory).
    if not credentials_path.is_absolute():
        credentials_path = Path.cwd() / credentials_path
    if not token_path.is_absolute():
        token_path = Path.cwd() / token_path

    if not token_path.exists():
        raise RuntimeError("Gmail not authenticated. Run: python orchestra/examples/gmail_auth.py")

    creds = Credentials.from_authorized_user_file(
        str(token_path),
        ["https://www.googleapis.com/auth/gmail.readonly"],
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json(), encoding="utf-8")

    try:
        service = build("gmail", "v1", credentials=creds)
        result = service.users().messages().list(
            userId="me",
            maxResults=max_results,
            labelIds=["INBOX"],
        ).execute()

        messages = result.get("messages")
        if not messages:
            return []

        items: list[dict] = []
        for msg in messages:
            msg_id = msg["id"]
            detail = service.users().messages().get(
                userId="me",
                id=msg_id,
                format="metadata",
                metadataHeaders=["Subject"],
            ).execute()

            headers = detail.get("payload", {}).get("headers", [])
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), "(no subject)")
            snippet = detail.get("snippet", "")

            items.append({"id": msg_id, "subject": subject, "snippet": snippet})

        return items
    except HttpError as e:
        raise RuntimeError(str(e)) from e
