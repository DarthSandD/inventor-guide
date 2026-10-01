#!/usr/bin/env python
"""Verify every video id in video_db.json is live (YouTube oEmbed returns 200)."""
import json
import os
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "video_db.json")


def check(item):
    key, vid = item
    url = ("https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v="
           + vid + "&format=json")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return key, vid, r.status
    except urllib.error.HTTPError as e:
        return key, vid, e.code
    except Exception as e:                       # noqa: BLE001
        return key, vid, f"ERR:{e}"


def main():
    db = json.load(open(DB, encoding="utf-8"))
    items = [(k, v["videoId"]) for k, v in db.items() if v and v.get("videoId")]
    print(f"checking {len(items)} ids ...", flush=True)
    bad = []
    with ThreadPoolExecutor(max_workers=16) as ex:
        for fut in as_completed([ex.submit(check, it) for it in items]):
            k, vid, code = fut.result()
            if code != 200:
                bad.append((k, vid, code))
    print(f"OK: {len(items) - len(bad)}   BAD: {len(bad)}")
    for b in bad:
        print("  ", b)
    json.dump(bad, open(os.path.join(HERE, "dead_videos.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
