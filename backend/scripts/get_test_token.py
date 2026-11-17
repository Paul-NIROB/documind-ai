"""Dev helper: sign in a test user and print an access token to stdout."""

import getpass
import json
import sys
import urllib.error
import urllib.request

from app.core.config import get_settings


def main() -> None:
    """Ask for credentials on stderr, so only the token reaches stdout and can be captured."""
    settings = get_settings()
    print("Test user email:", file=sys.stderr)
    email = input().strip()
    password = getpass.getpass("Test user password: ")
    request = urllib.request.Request(
        f"{settings.supabase_url}/auth/v1/token?grant_type=password",
        data=json.dumps({"email": email, "password": password}).encode(),
        headers={"apikey": settings.supabase_anon_key, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request) as response:
            print(json.load(response)["access_token"])
    except urllib.error.HTTPError as error:
        print(f"Login failed: HTTP {error.code}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()





