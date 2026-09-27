#!/usr/bin/env python3
"""Publish HTML files to WordPress.

WordPress.com-hosted sites use XML-RPC with an application password.
Self-hosted sites use the standard WordPress REST API.
"""

import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xmlrpc.client
from html import unescape
from pathlib import Path
from urllib.parse import urlparse


WECHAT_FOOTER = """
<hr>
<section class="wechat-official-account" aria-label="WeChat official account">
<h2>关注微信公众号：德川在东京</h2>
<p><strong>日本医疗资源整合者｜跨境医疗创业者｜AI医疗内容实践者</strong></p>
<p>服务10000+华人健康用户，累计发布2000+原创医疗内容，对接16+日本知名医院。</p>
<p>持续分享日本特效药、癌症筛查、专家第二意见、iPS再生医学、BNCT与医疗咨询信息。</p>
<p><em>内容仅供健康教育与就医决策参考，不替代医生诊断或个体化治疗建议。</em></p>
</section>
""".strip()


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"Missing required secret: {name}")
    return value


def extract(pattern: str, html: str, fallback: str = "") -> str:
    match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
    return unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip() if match else fallback


def parse_file(path: Path):
    raw = path.read_text(encoding="utf-8")
    title = extract(r"<h1[^>]*>(.*?)</h1>", raw, path.stem)
    description = extract(
        r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',
        raw,
        "",
    )
    body_match = re.search(r"<body[^>]*>(.*?)</body>", raw, re.IGNORECASE | re.DOTALL)
    body = body_match.group(1).strip() if body_match else raw
    if "wechat-official-account" not in body:
        article_end = re.search(r"</article>\s*$", body, re.IGNORECASE)
        if article_end:
            body = body[: article_end.start()] + WECHAT_FOOTER + "\n" + body[article_end.start() :]
        else:
            body = body + "\n" + WECHAT_FOOTER
    slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem).strip("-").lower()
    return title, description, body, slug


def request_json(url: str, username: str, password: str, method: str = "GET", payload=None):
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        "Authorization": f"Basic {token}",
        "Accept": "application/json",
        "User-Agent": "Buntou-WordPress-Publisher/1.1",
    }
    data = None
    if payload is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"WordPress API returned HTTP {exc.code}: {detail[:800]}") from exc


def is_wordpress_com(site: str) -> bool:
    hostname = (urlparse(site).hostname or "").lower()
    return hostname == "wordpress.com" or hostname.endswith(".wordpress.com")


def publish_wordpress_com(path: Path, site: str, username: str, password: str, status: str):
    title, description, body, slug = parse_file(path)
    server = xmlrpc.client.ServerProxy(site.rstrip("/") + "/xmlrpc.php", allow_none=True)

    existing_id = None
    posts = server.wp.getPosts(
        0,
        username,
        password,
        {"post_type": "post", "number": 100, "post_status": "any"},
        ["post_id", "post_name", "post_status"],
    )
    for post in posts:
        if post.get("post_name") == slug:
            if post.get("post_status") != "draft":
                raise RuntimeError("Matching WordPress post is not a draft; refusing to alter it")
            existing_id = post.get("post_id")
            break

    post_data = {
        "post_type": "post",
        "post_title": title,
        "post_content": body,
        "post_status": status,
        "post_excerpt": description,
        "post_name": slug,
    }
    if existing_id:
        server.wp.editPost(0, username, password, existing_id, post_data)
        post_id = existing_id
        action = "updated"
    else:
        post_id = server.wp.newPost(0, username, password, post_data)
        action = "created"
    verified = server.wp.getPost(0, username, password, post_id, ["post_status"])
    if verified.get("post_status") != "draft":
        raise RuntimeError("WordPress did not confirm draft status")
    print(f"{action}: {path} -> WordPress.com post {post_id} (verified draft)")


def publish_rest(path: Path, site: str, username: str, password: str, status: str):
    title, description, body, slug = parse_file(path)
    api = site.rstrip("/") + "/wp-json/wp/v2/posts"
    query = api + "?" + urllib.parse.urlencode({"slug": slug, "context": "edit", "per_page": 1, "status": "any"})
    existing = request_json(query, username, password)
    payload = {
        "title": title,
        "content": body,
        "slug": slug,
        "status": status,
        "excerpt": description,
    }
    if existing:
        if existing[0].get("status") != "draft":
            raise RuntimeError("Matching WordPress post is not a draft; refusing to alter it")
        result = request_json(f"{api}/{existing[0]['id']}", username, password, "POST", payload)
        action = "updated"
    else:
        result = request_json(api, username, password, "POST", payload)
        action = "created"
    if result.get("status") != "draft":
        raise RuntimeError("WordPress did not confirm draft status")
    print(f"{action}: {path} -> post {result.get('id')} ({result.get('status')})")


def publish_file(path: Path, site: str, username: str, password: str, status: str):
    if is_wordpress_com(site):
        publish_wordpress_com(path, site, username, password, status)
    else:
        publish_rest(path, site, username, password, status)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file-list", required=True)
    args = parser.parse_args()

    site = required_env("WP_SITE_URL")
    username = required_env("WP_USERNAME")
    password = required_env("WP_APP_PASSWORD").replace(" ", "")
    status = os.getenv("WP_POST_STATUS", "draft").strip().lower()
    if status != "draft":
        raise SystemExit("This uploader only permits draft status")

    paths = [Path(line.strip()) for line in Path(args.file_list).read_text().splitlines() if line.strip()]
    if not paths:
        print("No WordPress files selected.")
        return

    failed = False
    for path in paths:
        if not path.is_file() or path.suffix.lower() != ".html" or path.parent.as_posix() != "wordpress":
            print(f"Rejected unsafe or missing path: {path}", file=sys.stderr)
            failed = True
            continue
        try:
            publish_file(path, site, username, password, status)
        except Exception as exc:
            print(f"Failed: {path}: {exc}", file=sys.stderr)
            failed = True
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
