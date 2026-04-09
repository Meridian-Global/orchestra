import os
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main() -> int:
    credentials_path = Path(os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json"))
    token_path = Path(os.getenv("GOOGLE_TOKEN_PATH", "token.json"))

    if not credentials_path.is_absolute():
        credentials_path = Path.cwd() / credentials_path
    if not token_path.is_absolute():
        token_path = Path.cwd() / token_path

    if not credentials_path.exists():
        print(
            "credentials.json not found. Download it from Google Cloud Console (APIs & Services \u2192 Credentials \u2192 OAuth 2.0 Client \u2192 Desktop app)."
        )
        return 1

    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
    creds = flow.run_local_server(port=0)

    token_path.write_text(creds.to_json(), encoding="utf-8")
    print("token.json written. Gmail scanner is ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
