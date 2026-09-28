"""Create or update Blogger drafts from reviewed repository HTML files.

This program intentionally does not contain a publish operation.
"""

import argparse
import json
import os
from pathlib import Path
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API = "https://www.googleapis.com/blogger/v3"
TOKEN_URL = "https://oauth2.googleapis.com/token"


def request_json(url, *, token=None, data=None, method=None):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if data is not None:
        headers["Content-Type"] = "application/json" if isinstance(data, dict) else "application/x-www-form-urlencoded"
        data = json.dumps(data).encode() if isinstance(data, dict) else urlencode(data).encode()
    with urlopen(Request(url, data=data, headers=headers, method=method), timeout=30) as response:
        return json.load(response)


def access_token():
    required = ("BLOGGER_CLIENT_ID", "BLOGGER_CLIENT_SECRET", "BLOGGER_REFRESH_TOKEN")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise ValueError("Missing Blogger OAuth secrets: " + ", ".join(missing))
    response = request_json(TOKEN_URL, data={
        "client_id": os.environ["BLOGGER_CLIENT_ID"],
        "client_secret": os.environ["BLOGGER_CLIENT_SECRET"],
        "refresh_token": os.environ["BLOGGER_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }, method="POST")
    return response["access_token"]


def parse_post(filename):
    path = Path(filename)
    if not re.fullmatch(r"blogger/\d{4}-\d{2}-\d{2}-[a-z0-9-]+\.html", path.as_posix()):
        raise ValueError(f"Unexpected Blogger article path: {filename}")
    source = path.read_text(encoding="utf-8")
    title_match = re.search(r"<title>(.*?)</title>", source, re.I | re.S)
    article_match = re.search(r"(<article\b[^>]*>.*?</article>)", source, re.I | re.S)
    if not title_match or not article_match:
        raise ValueError(f"Missing <title> or <article> in {filename}")
    import html
    title = html.unescape(re.sub(r"<[^>]*>", "", title_match.group(1))).strip()
    marker = f"<!-- blogger-source: {path.as_posix()} -->"
    return title, marker + "\n" + article_match.group(1), marker


def all_posts(blog_id, token, status):
    url = f"{API}/blogs/{blog_id}/posts"
    next_page = None
    while True:
        query = {"status": status, "fetchBodies": "true", "maxResults": 500}
        if next_page:
            query["pageToken"] = next_page
        result = request_json(url + "?" + urlencode(query), token=token)
        yield from result.get("items", [])
        next_page = result.get("nextPageToken")
        if not next_page:
            break


def upload(filename, blog_id, token):
    title, content, marker = parse_post(filename)
    drafts = list(all_posts(blog_id, token, "draft"))
    found = next((p for p in drafts if marker in p.get("content", "")), None)
    if not found:
        found = next((p for p in drafts if p.get("title") == title), None)
    if not found:
        for post in all_posts(blog_id, token, "live"):
            if marker in post.get("content", "") or post.get("title") == title:
                raise ValueError(f"A published post already matches {filename}; refusing to alter it")
    base = f"{API}/blogs/{blog_id}/posts"
    if found:
        result = request_json(f"{base}/{found['id']}", token=token,
                              data={"kind": "blogger#post", "id": found["id"],
                                    "blog": {"id": blog_id}, "title": title, "content": content}, method="PUT")
        action = "Updated"
    else:
        result = request_json(base + "?isDraft=true", token=token,
                              data={"kind": "blogger#post", "blog": {"id": blog_id},
                                    "title": title, "content": content}, method="POST")
        action = "Created"
    if result.get("status", "").upper() != "DRAFT":
        raise RuntimeError("Blogger did not confirm DRAFT status")
    print(f"{action} Blogger draft {result['id']}: {title}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file-list", required=True)
    args = parser.parse_args()
    blog_id = os.environ.get("BLOGGER_BLOG_ID", "")
    if not re.fullmatch(r"\d+", blog_id):
        raise ValueError("BLOGGER_BLOG_ID must be numeric")
    files = [name.strip() for name in Path(args.file_list).read_text().splitlines() if name.strip()]
    if not files:
        return
    token = access_token()
    for name in files:
        upload(name, blog_id, token)


if __name__ == "__main__":
    main()
