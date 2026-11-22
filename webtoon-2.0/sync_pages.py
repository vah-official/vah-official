#!/usr/bin/env python3
"""Rebuild a chapter's pages.json from the panel files that are actually on disk.

The point: nobody edits pages.json by hand. Drop the JPG in, run this, run
build_reader.py. Names decide everything.

Accepted names for a page file (the "p" and the extension are forgiving):
  p09.jpg   p9.jpg   09.jpg   9.jpg    -> page p09
  p09.JPG   p09.jpeg  p09.png   p09.webp -> page p09

Reading order is the number. A file that already sits in pages.json keeps its
own fields (title, label, dialog, status); a new file gets status "reviewed"
unless --new-status says otherwise.

Usage:
  python3 sync_pages.py --chapter 1 --assets /workspace/vah-hf
  python3 sync_pages.py --chapter 1 --assets /workspace/vah-hf --dry-run
  python3 sync_pages.py --chapter 1 --assets /workspace/vah-hf \
      --new-status queued --air-date 2026-11-25

A page stocked for release (status "queued") needs a date, because the release
gate in build_reader --check rejects an undated queue.
"""
import argparse
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE_RE = re.compile(r"^p?(\d{1,2})[a-z]?\.(jpe?g|png|webp)$", re.IGNORECASE)
EXT_PREF = (".jpg", ".jpeg", ".png", ".webp")


def scan(asset_dir):
    """-> {page_id: relative file path}, highest-preference extension wins."""
    try:
        names = os.listdir(asset_dir)
    except FileNotFoundError:
        sys.exit("asset dir not found: %s" % asset_dir)
    found = {}
    for name in sorted(names):
        m = PAGE_RE.match(name)
        if not m:
            continue
        num = int(m.group(1))
        ext = os.path.splitext(name)[1].lower()
        best = found.get(num)
        if best is None or EXT_PREF.index(ext) < EXT_PREF.index(os.path.splitext(best[1])[1].lower()):
            found[num] = ("p%02d" % num, name)
    return found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter", type=int, default=1)
    ap.add_argument("--assets", required=True, help="tree that holds assets/panels/chNN")
    ap.add_argument("--dir", default=None, help="override the panel folder (default: <assets>/<asset_dir>)")
    ap.add_argument("--new-status", default="reviewed",
                    choices=["draft", "queued", "reviewed", "published", "canon"],
                    help="status given to a page that is not in pages.json yet")
    ap.add_argument("--air-date", default=None,
                    help="YYYY-MM-DD for pages added as queued (required for --new-status queued)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.new_status == "queued" and not args.air_date:
        sys.exit("--new-status queued needs --air-date YYYY-MM-DD")
    if args.air_date:
        try:
            datetime.date.fromisoformat(args.air_date)
        except ValueError:
            sys.exit("bad --air-date %r (want YYYY-MM-DD)" % args.air_date)

    path = os.path.join(HERE, "ch%02d" % args.chapter, "pages.json")
    with open(path, encoding="utf-8") as f:
        meta = json.load(f)

    asset_dir = args.dir or os.path.join(args.assets, meta["asset_dir"])
    asset_prefix = meta["asset_dir"].rstrip("/")
    on_disk = scan(asset_dir)
    if not on_disk:
        sys.exit("no page files in %s (want p01.jpg, p02.jpg, ...)" % asset_dir)

    old = {p["page"]: p for p in meta.get("pages", [])}
    pages, added, relinked, missing = [], [], [], []

    for num in sorted(on_disk):
        pid, name = on_disk[num]
        rel = "%s/%s" % (asset_prefix, name)
        if pid in old:
            entry = dict(old[pid])
            if entry.get("file") != rel:
                relinked.append((pid, entry.get("file"), rel))
                entry["file"] = rel
        else:
            entry = {"page": pid, "file": rel, "dialog": "en-final", "status": args.new_status}
            if args.new_status == "queued":
                entry["air_date"] = args.air_date
            added.append(pid)
        pages.append(entry)

    for pid, entry in old.items():
        if pid not in [p["page"] for p in pages] and pid not in [i.get("panel") for i in meta.get("inserts", [])]:
            missing.append((pid, entry.get("file")))

    meta["pages"] = pages

    print("panel dir : %s" % asset_dir)
    print("pages     : %d (%s .. %s)" % (len(pages), pages[0]["page"], pages[-1]["page"]))
    print("added     : %s" % (", ".join(added) or "-"))
    print("relinked  : %s" % (", ".join("%s %s -> %s" % r for r in relinked) or "-"))
    print("in json, no file on disk: %s" % (", ".join("%s (%s)" % m for m in missing) or "-"))
    print("existing fields kept for: %s" % (", ".join(p for p in old if p in [q["page"] for q in pages]) or "-"))

    if args.dry_run:
        print("\n[dry-run] pages.json not written")
        return
    with open(path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("\nwrote %s" % path)


if __name__ == "__main__":
    main()