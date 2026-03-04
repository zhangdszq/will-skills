#!/usr/bin/env python3
"""
Search files on mounted SMB share with filters and local index caching.
First scan builds a JSON index (~74s for 4000+ files); subsequent searches are instant.

Usage:
  python3 smb_search.py /tmp/smb_mounts/DMFile/双师智学2026 --name "*.pptx"
  python3 smb_search.py /tmp/smb_mounts/DMFile --ext pptx,xlsx --max-depth 3
  python3 smb_search.py /tmp/smb_mounts/DMFile --size-gt 100M --top 20
  python3 smb_search.py /tmp/smb_mounts/DMFile --tree --max-depth 2
  python3 smb_search.py /tmp/smb_mounts/DMFile --rebuild   # force rebuild index
"""

import argparse
import fnmatch
import hashlib
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path


CACHE_DIR = Path.home() / ".cache" / "smb-file-index"


def parse_size(s):
    s = s.strip().upper()
    units = {"B": 1, "K": 1024, "M": 1024**2, "G": 1024**3}
    for u, m in units.items():
        if s.endswith(u):
            return float(s[:-1]) * m
    return float(s)


def fmt_size(n):
    for u in ["B", "KB", "MB", "GB"]:
        if n < 1024:
            return f"{n:.1f}{u}"
        n /= 1024
    return f"{n:.1f}TB"


def fmt_time(ts):
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


def cache_path_for(root):
    key = hashlib.md5(root.encode()).hexdigest()[:12]
    name = os.path.basename(root.rstrip("/")) or "root"
    return CACHE_DIR / f"{name}_{key}.json"


def build_index(root, max_depth=4, max_files=10000):
    """Walk SMB share and build file index with progress reporting."""
    files = []
    count = 0
    dirs_scanned = 0
    root_depth = root.rstrip(os.sep).count(os.sep)
    t0 = time.time()

    for dirpath, dirnames, filenames in os.walk(root):
        depth = dirpath.rstrip(os.sep).count(os.sep) - root_depth
        if max_depth is not None and depth >= max_depth:
            dirnames.clear()
        dirs_scanned += 1
        if dirs_scanned % 10 == 0:
            rel = os.path.relpath(dirpath, root)
            elapsed = time.time() - t0
            print(
                f"\r[index] {count} files, {dirs_scanned} dirs, {elapsed:.0f}s ... {rel[:50]}",
                end="", flush=True, file=sys.stderr,
            )
        for f in filenames:
            if f.startswith("."):
                continue
            count += 1
            if count > max_files:
                print(f"\n[warn] Index capped at {max_files} files.", file=sys.stderr)
                return files
            filepath = os.path.join(dirpath, f)
            try:
                st = os.stat(filepath)
                files.append({
                    "path": os.path.relpath(filepath, root),
                    "size": st.st_size,
                    "mtime": st.st_mtime,
                })
            except OSError:
                pass

    elapsed = time.time() - t0
    print(
        f"\r[index] Done: {count} files, {dirs_scanned} dirs in {elapsed:.1f}s{' ' * 30}",
        file=sys.stderr,
    )
    return files


def load_or_build_index(root, max_depth, max_files, force_rebuild=False):
    """Load cached index or build a new one."""
    cp = cache_path_for(root)
    if not force_rebuild and cp.exists():
        age_hours = (time.time() - cp.stat().st_mtime) / 3600
        try:
            data = json.loads(cp.read_text())
            meta = data.get("meta", {})
            print(
                f"[cache] Loaded {len(data['files'])} files from index "
                f"(built {age_hours:.1f}h ago, depth={meta.get('max_depth', '?')})",
                file=sys.stderr,
            )
            if age_hours > 24:
                print("[cache] Index older than 24h. Use --rebuild to refresh.", file=sys.stderr)
            return data["files"]
        except (json.JSONDecodeError, KeyError):
            pass

    print(f"[index] Building index for {root} (depth={max_depth})...", file=sys.stderr)
    files = build_index(root, max_depth, max_files)

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "meta": {
            "root": root,
            "max_depth": max_depth,
            "file_count": len(files),
            "built_at": datetime.now().isoformat(),
        },
        "files": files,
    }
    cp.write_text(json.dumps(data, ensure_ascii=False, indent=None))
    print(f"[index] Saved to {cp}", file=sys.stderr)
    return files


def search(all_files, args, root):
    results = []
    for entry in all_files:
        filename = os.path.basename(entry["path"])

        if args.name and not fnmatch.fnmatch(filename.lower(), args.name.lower()):
            continue

        if args.ext:
            exts = [e.strip().lower().lstrip(".") for e in args.ext.split(",")]
            file_ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            if file_ext not in exts:
                continue

        if args.size_gt and entry["size"] < parse_size(args.size_gt):
            continue
        if args.size_lt and entry["size"] > parse_size(args.size_lt):
            continue

        if args.path_contains:
            if args.path_contains.lower() not in entry["path"].lower():
                continue

        results.append(entry)

    if args.sort == "size":
        results.sort(key=lambda x: x["size"], reverse=True)
    elif args.sort == "date":
        results.sort(key=lambda x: x["mtime"], reverse=True)
    elif args.sort == "name":
        results.sort(key=lambda x: x["path"].lower())

    if args.top:
        results = results[:args.top]

    return results


def print_tree(root, max_depth=2, prefix=""):
    try:
        entries = sorted(os.listdir(root))
    except OSError:
        return
    dirs = [e for e in entries if os.path.isdir(os.path.join(root, e)) and not e.startswith(".")]
    files = [e for e in entries if os.path.isfile(os.path.join(root, e)) and not e.startswith(".")]

    for i, f in enumerate(files):
        connector = "└── " if (i == len(files) - 1 and not dirs) else "├── "
        try:
            sz = fmt_size(os.path.getsize(os.path.join(root, f)))
        except OSError:
            sz = "?"
        print(f"{prefix}{connector}{f}  ({sz})")

    for i, d in enumerate(dirs):
        connector = "└── " if i == len(dirs) - 1 else "├── "
        print(f"{prefix}{connector}{d}/")
        if max_depth > 1:
            ext = "    " if i == len(dirs) - 1 else "│   "
            print_tree(os.path.join(root, d), max_depth - 1, prefix + ext)


def main():
    parser = argparse.ArgumentParser(description="SMB File Search (with index cache)")
    parser.add_argument("root", help="Mount path to search")
    parser.add_argument("--name", help="Filename glob pattern (e.g. '*.pptx')")
    parser.add_argument("--ext", help="Comma-separated extensions (e.g. 'pptx,xlsx')")
    parser.add_argument("--path-contains", help="Filter by path substring (e.g. 'level 1')")
    parser.add_argument("--size-gt", help="Min file size (e.g. '10M', '1G')")
    parser.add_argument("--size-lt", help="Max file size (e.g. '100M')")
    parser.add_argument("--max-depth", type=int, default=3, help="Max scan depth (default: 3)")
    parser.add_argument("--max-files", type=int, default=10000, help="Max files to index (default: 10000)")
    parser.add_argument("--sort", choices=["size", "date", "name"], default="name")
    parser.add_argument("--top", type=int, help="Show top N results")
    parser.add_argument("--tree", action="store_true", help="Show directory tree (no cache, direct SMB)")
    parser.add_argument("--rebuild", action="store_true", help="Force rebuild index")
    parser.add_argument("--stats", action="store_true", help="Show index statistics")
    args = parser.parse_args()

    if not os.path.isdir(args.root):
        print(f"[error] Path not found: {args.root}")
        sys.exit(1)

    if args.tree:
        print(f"{os.path.basename(args.root)}/")
        print_tree(args.root, args.max_depth)
        return

    root = os.path.abspath(args.root)
    all_files = load_or_build_index(root, args.max_depth, args.max_files, args.rebuild)

    if args.stats:
        total_size = sum(f["size"] for f in all_files)
        exts = {}
        for f in all_files:
            ext = os.path.basename(f["path"]).rsplit(".", 1)[-1].lower() if "." in f["path"] else "(none)"
            exts[ext] = exts.get(ext, 0) + 1
        print(f"Total files: {len(all_files)}")
        print(f"Total size:  {fmt_size(total_size)}")
        print(f"\nTop extensions:")
        for ext, cnt in sorted(exts.items(), key=lambda x: -x[1])[:15]:
            print(f"  .{ext:10s} {cnt:>5} files")
        return

    results = search(all_files, args, root)
    if not results:
        print("[info] No files found matching criteria.")
        return

    print(f"{'Size':>10}  {'Modified':>16}  Path")
    print("-" * 80)
    for r in results:
        print(f"{fmt_size(r['size']):>10}  {fmt_time(r['mtime']):>16}  {r['path']}")
    print(f"\n[info] {len(results)} file(s) found.")


if __name__ == "__main__":
    main()
