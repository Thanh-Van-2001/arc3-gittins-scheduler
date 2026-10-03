"""Fetch ARC-AGI-3 Kaggle discussion topics (public) through the web app's internal API."""
import json
import os
import re
import sys
import time

import requests

OUT = r"D:\arc3_paper\meta\discussions"
os.makedirs(OUT, exist_ok=True)
S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0"
S.get("https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3/discussion")
XSRF = S.cookies.get("XSRF-TOKEN") or next((c.value for c in S.cookies if "XSRF" in c.name.upper()), "")


def call(service, method, body):
    r = S.post(f"https://www.kaggle.com/api/i/{service}/{method}", json=body,
               headers={"x-xsrf-token": XSRF, "Content-Type": "application/json"}, timeout=60)
    if r.status_code != 200:
        return {"_error": r.status_code, "_text": r.text[:300]}
    return r.json()


def forum_id():
    c = call("competitions.CompetitionService", "GetCompetition", {"competitionName": "arc-prize-2026-arc-agi-3"})
    return c.get("forumId") or c.get("competition", {}).get("forumId"), c


def topics(fid, sort, pages=3):
    out = []
    for page in range(1, pages + 1):
        r = call("discussions.DiscussionsService", "GetTopicListByForumId",
                 {"forumId": fid, "page": page, "sortBy": sort, "category": "TOPIC_LIST_CATEGORY_ALL"})
        ts = r.get("topics") or []
        if not ts:
            if page == 1:
                print("topic list response:", json.dumps(r)[:400])
            break
        out += ts
    return out


def topic(tid):
    return call("discussions.DiscussionsService", "GetForumTopicById", {"forumTopicId": tid, "includeComments": True})


if __name__ == "__main__":
    fid, raw = forum_id()
    print("forum id", fid)
    if not fid:
        print(json.dumps(raw)[:600]); sys.exit(1)
    seen = {}
    for sort in ["TOPIC_LIST_SORT_BY_VOTES", "TOPIC_LIST_SORT_BY_RECENT_COMMENTS"]:
        for t in topics(fid, sort):
            seen[t["id"]] = t
    rows = sorted(seen.values(), key=lambda t: -(t.get("votes") or 0))
    json.dump(rows, open(os.path.join(OUT, "_index.json"), "w"), indent=1)
    for t in rows:
        print(t["id"], t.get("votes"), t.get("commentCount"), (t.get("lastCommentPostDate") or t.get("postDate") or "")[:10], t.get("title", "")[:100])
