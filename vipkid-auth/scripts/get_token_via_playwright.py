#!/usr/bin/env python3
"""
使用 Playwright 打开独立 Chrome 配置目录，等待登录完成后读取指定 Cookie。
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
        "当前 Python 环境未安装 Playwright，请先执行：\n"
        "python3 -m pip install playwright && python3 -m playwright install chrome",
        file=sys.stderr,
    )
    raise SystemExit(1) from exc


DEFAULT_URL = "https://power.lionabc.com"
DEFAULT_COOKIE_NAME = "intlAuthToken"
DEFAULT_TIMEOUT_SECONDS = 300


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="打开独立 Chrome 窗口，等待登录完成后提取指定 Cookie。",
    )
    parser.add_argument("--url", default=DEFAULT_URL, help="目标站点地址。")
    parser.add_argument("--cookie", default=DEFAULT_COOKIE_NAME, help="要读取的 Cookie 名称。")
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_SECONDS,
        help="最长等待登录的秒数。",
    )
    parser.add_argument(
        "--profile-dir",
        required=True,
        help="独立 Playwright 浏览器配置目录。",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="以无头模式运行，主要用于自动化验证。",
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
        # 登录页或跳转页可能持续有网络请求，这里只依赖轮询 Cookie 即可。
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
            print(f"通过 Playwright 启动 Chrome 失败：{exc}", file=sys.stderr)
            return 1

        try:
            ensure_page(context, args.url)

            token = read_cookie_value(context, args.url, args.cookie)
            if token:
                print(
                    f"在独立 Playwright 配置目录中检测到已有 {args.cookie}。",
                    file=sys.stderr,
                )
                sys.stdout.write(token)
                return 0

            print(
                "\n请在弹出的浏览器窗口中完成登录。\n"
                f"正在等待 {args.url} 写入 Cookie `{args.cookie}`，最长 {args.timeout} 秒。\n",
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
                f"超时：在 {args.timeout} 秒内未检测到 Cookie `{args.cookie}`。",
                file=sys.stderr,
            )
            return 1
        finally:
            context.close()


if __name__ == "__main__":
    raise SystemExit(main())
