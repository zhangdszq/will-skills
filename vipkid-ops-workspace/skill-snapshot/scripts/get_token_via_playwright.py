#!/usr/bin/env python3
"""
Launch a dedicated Chrome profile with Playwright, wait for login, then read a cookie.
"""

import argparse
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

try:
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import sync_playwright
except ImportError as exc:
    print(
        "Playwright is not installed for Python. Install it first, for example:\n"
        "python3 -m pip install playwright && python3 -m playwright install chrome",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc


DEFAULT_URL = "https://sa-manager.lionabc.com"
DEFAULT_COOKIE_NAME = "intlAuthToken"
DEFAULT_TIMEOUT_SECONDS = 300


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Open a dedicated Chrome window, wait for login, and extract a cookie.",
    )
    parser.add_argument("--url", default=DEFAULT_URL, help="Target site URL.")
    parser.add_argument("--cookie", default=DEFAULT_COOKIE_NAME, help="Cookie name to read.")
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="Maximum seconds to wait for login.",
    )
    parser.add_argument(
        "--profile-dir",
        required=True,
        help="Persistent profile directory for the dedicated Playwright browser.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run headless. Mostly useful for automated verification.",
    )
    return parser.parse_args()


def cookie_matches(cookie: dict, cookie_name: str, hostname: str) -> bool:
    if cookie.get("name") != cookie_name:
        return False

    domain = str(cookie.get("domain", "")).lstrip(".")
    return domain == hostname or hostname.endswith(f".{domain}")


def read_cookie_value(context, target_url: str, cookie_name: str) -> str | None:
    hostname = urlparse(target_url).hostname or ""
    cookies = context.cookies([target_url])
    for cookie in cookies:
        if cookie_matches(cookie, cookie_name, hostname):
            return cookie.get("value") or None
    return None


def ensure_page(context, target_url: str):
    page = context.pages[0] if context.pages else context.new_page()
    page.bring_to_front()
    try:
        page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_load_state("networkidle", timeout=5000)
    except PlaywrightError:
        # Login pages or redirects may keep network requests alive; polling cookies is enough.
        pass
    return page


def main() -> int:
    args = parse_args()
    profile_dir = Path(args.profile_dir).expanduser()
    profile_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        try:
            context = playwright.chromium.launch_persistent_context(
                user_data_dir=str(profile_dir),
                channel="chrome",
                headless=args.headless,
                args=["--start-maximized"],
                viewport={"width": 1440, "height": 960},
            )
        except PlaywrightError as exc:
            print(f"Failed to launch Chrome with Playwright: {exc}", file=sys.stderr)
            return 1

        try:
            ensure_page(context, args.url)

            token = read_cookie_value(context, args.url, args.cookie)
            if token:
                print(
                    f"Detected existing {args.cookie} in the dedicated Playwright profile.",
                    file=sys.stderr,
                )
                sys.stdout.write(token)
                return 0

            print(
                "\nPlease complete login in the opened browser window.\n"
                f"Waiting up to {args.timeout} seconds for cookie `{args.cookie}` from {args.url}...\n",
                file=sys.stderr,
            )

            deadline = time.time() + args.timeout
            while time.time() < deadline:
                token = read_cookie_value(context, args.url, args.cookie)
                if token:
                    sys.stdout.write(token)
                    return 0
                time.sleep(1)

            print(
                f"Timed out after {args.timeout} seconds without finding cookie `{args.cookie}`.",
                file=sys.stderr,
            )
            return 1
        finally:
            context.close()


if __name__ == "__main__":
    raise SystemExit(main())
