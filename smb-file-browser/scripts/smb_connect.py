#!/usr/bin/env python3
"""
SMB Server connector with automatic proxy/DNS bypass.
Handles Clash Verge fake-ip, cross-platform mounting, and authentication.

Usage:
  python3 smb_connect.py --server HT-FILE2 --share DMFile --user panxiaoying --password 'Password@2025'
  python3 smb_connect.py --server HT-FILE2 --share 双师智学2026 --user panxiaoying --password 'Password@2025'
  python3 smb_connect.py --check   # check if already mounted
"""

import argparse
import json
import os
import platform
import re
import socket
import subprocess
import sys
import time


CORPORATE_DOMAIN = "vipkid.work"
MOUNT_BASE_MAC = "/tmp/smb_mounts"
MOUNT_BASE_WIN = "Z:"


def run(cmd, timeout=15, shell=True):
    try:
        r = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"
    except Exception as e:
        return -1, "", str(e)


def detect_dhcp_dns():
    """Extract corporate DNS servers from DHCP lease (macOS only)."""
    code, out, _ = run("ipconfig getpacket en0")
    if code != 0:
        return []
    dns_servers = []
    for line in out.splitlines():
        if "domain_name_server" in line:
            ips = re.findall(r'(\d+\.\d+\.\d+\.\d+)', line)
            dns_servers.extend(ips)
    return dns_servers


def detect_clash_tun():
    """Detect if Clash Verge TUN mode is active (fake-ip DNS hijacking)."""
    code, out, _ = run("ifconfig")
    if code != 0:
        return False
    for line in out.splitlines():
        if "198.18.0." in line and "utun" in out:
            return True
    return False


def clash_api_query_dns(hostname):
    """Query real IP via Clash mihomo unix socket API."""
    sock_path = "/tmp/verge/verge-mihomo.sock"
    if not os.path.exists(sock_path):
        return None
    fqdn = f"{hostname}.{CORPORATE_DOMAIN}" if "." not in hostname else hostname
    code, out, _ = run(
        f"curl -s --unix-socket {sock_path} "
        f"'http://localhost/dns/query?name={fqdn}&type=A'"
    )
    if code != 0:
        return None
    try:
        data = json.loads(out)
        for ans in data.get("Answer", []):
            if ans.get("type") == 1:
                return ans["data"]
    except (json.JSONDecodeError, KeyError):
        pass
    return None


def patch_clash_dns_for_domain(domain, dns_servers):
    """
    Patch Clash Verge runtime config to bypass fake-ip for a domain
    and use corporate DNS for resolution.
    """
    sock_path = "/tmp/verge/verge-mihomo.sock"
    if not os.path.exists(sock_path):
        return False

    config_path = os.path.expanduser(
        "~/Library/Application Support/"
        "io.github.clash-verge-rev.clash-verge-rev/clash-verge.yaml"
    )
    if not os.path.exists(config_path):
        return False

    with open(config_path, "r") as f:
        content = f.read()

    domain_pattern = f"+.{domain}"
    needs_update = False

    if "fake-ip-filter:" not in content:
        content = content.replace(
            "fake-ip-range: 198.18.0.1/16",
            f"fake-ip-range: 198.18.0.1/16\n"
            f"  fake-ip-filter:\n"
            f"  - '*.lan'\n  - '*.local'\n  - '*.arpa'\n"
            f"  - {domain_pattern}",
        )
        needs_update = True
    elif domain_pattern not in content:
        content = content.replace(
            "fake-ip-filter:\n",
            f"fake-ip-filter:\n  - {domain_pattern}\n",
        )
        needs_update = True

    if "nameserver-policy:" not in content or domain_pattern not in content:
        dns_list = "\n".join(f"    - {s}" for s in dns_servers)
        if "nameserver-policy:" not in content:
            idx = content.find("fake-ip-range:")
            line_end = content.find("\n", idx)
            content = (
                content[:line_end + 1]
                + f"  nameserver-policy:\n    '{domain_pattern}':\n{dns_list}\n"
                + content[line_end + 1:]
            )
        elif domain_pattern not in content.split("nameserver-policy")[1][:200]:
            content = content.replace(
                "nameserver-policy:\n",
                f"nameserver-policy:\n    '{domain_pattern}':\n{dns_list}\n",
            )
        needs_update = True

    if needs_update:
        with open(config_path, "w") as f:
            f.write(content)
        code, _, _ = run(
            f"curl -s --unix-socket {sock_path} -X PUT "
            f"'http://localhost/configs?force=true' "
            f"-H 'Content-Type: application/json' "
            f'-d \'{{"path":"{config_path}"}}\''
        )
        time.sleep(2)
        return code == 0

    return True


def resolve_server(hostname):
    """Resolve SMB server hostname to real IP, bypassing proxy if needed."""
    fqdn = f"{hostname}.{CORPORATE_DOMAIN}" if "." not in hostname else hostname
    is_tun = detect_clash_tun()

    if is_tun:
        print(f"[info] Clash TUN detected, checking DNS bypass for {CORPORATE_DOMAIN}...")
        real_ip = clash_api_query_dns(fqdn)
        if real_ip and not real_ip.startswith("198.18."):
            print(f"[info] Resolved {fqdn} -> {real_ip}")
            return real_ip

        dhcp_dns = detect_dhcp_dns()
        if dhcp_dns:
            print(f"[info] Corporate DNS: {dhcp_dns}, patching Clash config...")
            patch_clash_dns_for_domain(CORPORATE_DOMAIN, dhcp_dns)
            real_ip = clash_api_query_dns(fqdn)
            if real_ip and not real_ip.startswith("198.18."):
                print(f"[info] Resolved {fqdn} -> {real_ip} (after patch)")
                return real_ip

        for dns in dhcp_dns:
            code, out, _ = run(f"dig @{dns} {fqdn} +short +timeout=3 +tcp")
            if code == 0 and out and not out.startswith("198.18."):
                print(f"[info] Resolved via TCP DNS: {fqdn} -> {out}")
                return out.splitlines()[0]

    try:
        ip = socket.gethostbyname(fqdn)
        if not ip.startswith("198.18."):
            return ip
    except socket.gaierror:
        pass

    print(f"[error] Cannot resolve {fqdn}. Check VPN/network connection.")
    sys.exit(1)


def check_port(ip, port=445, timeout=5):
    try:
        s = socket.create_connection((ip, port), timeout=timeout)
        s.close()
        return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def mount_smb_mac(ip, share, user, password):
    mount_point = os.path.join(MOUNT_BASE_MAC, share.replace(" ", "_"))
    code, out, _ = run(f"mount | grep '{mount_point}'")
    if code == 0 and out:
        print(f"[info] Already mounted at {mount_point}")
        return mount_point

    os.makedirs(mount_point, exist_ok=True)
    pwd_escaped = password.replace("@", "%40").replace("#", "%23").replace("&", "%26")
    cmd = f"mount_smbfs -o nobrowse '//{user}:{pwd_escaped}@{ip}/{share}' '{mount_point}'"
    code, out, err = run(cmd)
    if code != 0:
        print(f"[error] Mount failed: {err or out}")
        if "Authentication" in (err + out):
            print("[hint] Try different username format (e.g. without email domain)")
        sys.exit(1)
    print(f"[ok] Mounted //{ip}/{share} -> {mount_point}")
    return mount_point


def mount_smb_win(ip, share, user, password, drive=MOUNT_BASE_WIN):
    code, out, _ = run(f'net use {drive}', shell=True)
    if code == 0 and ip in out:
        print(f"[info] Already mapped to {drive}")
        return drive

    fqdn_user = user
    cmd = f'net use {drive} \\\\{ip}\\{share} /user:{fqdn_user} "{password}" /persistent:no'
    code, out, err = run(cmd)
    if code != 0:
        print(f"[error] Map failed: {err or out}")
        sys.exit(1)
    print(f"[ok] Mapped \\\\{ip}\\{share} -> {drive}")
    return drive


def list_shares(ip, user, password):
    """List available shares on the server (macOS only)."""
    pwd_escaped = password.replace("@", "%40").replace("#", "%23")
    code, out, err = run(f"smbutil view '//{user}:{pwd_escaped}@{ip}'")
    if code != 0:
        print(f"[error] Cannot list shares: {err}")
        return
    print(out)


def main():
    parser = argparse.ArgumentParser(description="SMB Server Connector")
    parser.add_argument("--server", default="HT-FILE2", help="Server hostname")
    parser.add_argument("--share", default="DMFile", help="Share name")
    parser.add_argument("--user", default="panxiaoying", help="Username (no email domain)")
    parser.add_argument("--password", default="Password@2025", help="Password")
    parser.add_argument("--check", action="store_true", help="Check existing mounts")
    parser.add_argument("--list-shares", action="store_true", help="List server shares")
    parser.add_argument("--drive", default=MOUNT_BASE_WIN, help="Windows drive letter")
    args = parser.parse_args()

    if args.check:
        if platform.system() == "Darwin":
            code, out, _ = run(f"mount | grep smb")
            print(out if out else "No SMB mounts found.")
        else:
            code, out, _ = run("net use")
            print(out if out else "No mapped drives found.")
        return

    ip = resolve_server(args.server)
    print(f"[info] Server IP: {ip}")

    if not check_port(ip):
        print(f"[error] SMB port 445 not reachable on {ip}")
        sys.exit(1)

    if args.list_shares:
        list_shares(ip, args.user, args.password)
        return

    if platform.system() == "Darwin":
        path = mount_smb_mac(ip, args.share, args.user, args.password)
    elif platform.system() == "Windows":
        path = mount_smb_win(ip, args.share, args.user, args.password, args.drive)
    else:
        print(f"[error] Unsupported OS: {platform.system()}")
        sys.exit(1)

    print(f"\n[ready] Mount path: {path}")
    print(f"  Browse: ls '{path}'")


if __name__ == "__main__":
    main()
