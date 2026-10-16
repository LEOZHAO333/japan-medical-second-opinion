"""Upload repository HTML to Blogger drafts; never call the publish endpoint."""
import argparse
import html
import json
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = "https://www.googleapis.com/blogger/v3"
TOKEN_URL = "https://oauth2.googleapis.com/token"


def request_json(url, *, token=None, data=None, form=False, method=None, etag=None):
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    if etag:
        headers["If-Match"] = etag
    if data is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded" if form else "application/json"
        data = (urlencode(data) if form else json.dumps(data)).encode("utf-8")
    try:
        with urlopen(Request(url, data=data, headers=headers, method=method), timeout=45) as response:
            return json.load(response)
    except HTTPError as error:
        # Never print response bodies, request headers or credentials.
        raise RuntimeError(
            f"Blogger API request failed: HTTP {error.code}. Check Blogger account access and blog ID."
        ) from None
    except URLError:
        raise RuntimeError("Blogger connection failed. Check connectivity and retry.") from None


def _oauth_error_code(error):
    """Return only Google's OAuth error code; never expose descriptions or secrets."""
    try:
        payload = json.loads(error.read(4096).decode("utf-8", "replace"))
    except (ValueError, OSError, UnicodeDecodeError):
        return ""
    if not isinstance(payload, dict):
        return ""
    code = str(payload.get("error") or "")
    allowed = {"invalid_grant", "invalid_client", "unauthorized_client", "invalid_request"}
    return code if code in allowed else ""


def access_token():
    required = ("BLOGGER_CLIENT_ID", "BLOGGER_CLIENT_SECRET", "BLOGGER_REFRESH_TOKEN")
    missing = [name for name in required if not os.getenv(name, "").strip()]
    if missing:
        raise ValueError("Missing Actions secrets: " + ", ".join(missing))

    form = {
        "client_id": os.environ["BLOGGER_CLIENT_ID"].strip(),
        "client_secret": os.environ["BLOGGER_CLIENT_SECRET"].strip(),
        "refresh_token": os.environ["BLOGGER_REFRESH_TOKEN"].strip(),
        "grant_type": "refresh_token",
    }
    request = Request(
        TOKEN_URL,
        data=urlencode(form).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=45) as response:
            result = json.load(response)
    except HTTPError as error:
        code = _oauth_error_code(error)
        if code == "invalid_grant":
            raise RuntimeError(
                "Google OAuth refresh failed: invalid_grant. The refresh token is expired, revoked, "
                "or no longer valid. If the OAuth consent app is in Testing, move it to In production, "
                "generate a new refresh token with Blogger scope, and replace BLOGGER_REFRESH_TOKEN."
            ) from None
        if code == "invalid_client":
            raise RuntimeError(
                "Google OAuth refresh failed: invalid_client. Check that BLOGGER_CLIENT_ID and "
                "BLOGGER_CLIENT_SECRET belong to the same OAuth client used to create the refresh token."
            ) from None
        if code == "unauthorized_client":
            raise RuntimeError(
                "Google OAuth refresh failed: unauthorized_client. Re-authorize Blogger access with the "
                "configured OAuth client and replace BLOGGER_REFRESH_TOKEN."
            ) from None
        if code == "invalid_request":
            raise RuntimeError(
                "Google OAuth refresh failed: invalid_request. Check the OAuth client credentials and "
                "refresh-token configuration."
            ) from None
        raise RuntimeError(
            f"Google OAuth token refresh failed: HTTP {error.code}. Re-authorize Blogger access and "
            "replace BLOGGER_REFRESH_TOKEN if needed."
        ) from None
    except URLError:
        raise RuntimeError("Google OAuth connection failed. Check connectivity and retry.") from None

    if not result.get("access_token"):
        raise RuntimeError("Google did not return an access token")
    return result["access_token"]


def blog_id_from_env():
    blog_id = os.getenv("BLOGGER_BLOG_ID", "").strip()
    if not re.fullmatch(r"[0-9]+", blog_id):
        raise ValueError("Set Actions secret BLOGGER_BLOG_ID to the numeric blog ID")
    return blog_id


def verify_auth():
    blog_id = blog_id_from_env()
    token = access_token()
    result = request_json(f"{API}/blogs/{blog_id}?view=ADMIN", token=token)
    if str(result.get("id") or "") != blog_id:
        raise RuntimeError("Blogger authentication succeeded but the configured blog could not be verified")
    print("Blogger OAuth and blog access verified.")


def parse_post(filename):
    if not re.fullmatch(r"blogger/\d{4}-\d{2}-\d{2}-[a-z0-9-]+\.html", filename):
        raise ValueError("Expected blogger/YYYY-MM-DD-lowercase-slug.html")
    path = Path(filename)
    if path.is_symlink() or Path("blogger").is_symlink():
        raise ValueError("Blogger source must not be a symlink")
    source = path.read_text(encoding="utf-8")
    title = re.search(r"<title\b[^>]*>(.*?)</title>", source, re.I | re.S)
    article = re.search(r"(<article\b[^>]*>.*?</article>)", source, re.I | re.S)
    if not title or not article:
        raise ValueError(f"Missing title or article element: {filename}")
    title = html.unescape(re.sub(r"<[^>]*>", "", title.group(1))).strip()
    if not title:
        raise ValueError("Article title is empty")
    marker = f"<!-- blogger-source: {filename} -->"
    return title, marker + "\n" + article.group(1), marker


def all_posts(blog_id, token, status):
    page = None
    while True:
        query = {"status": status, "view": "ADMIN", "fetchBodies": "true", "maxResults": 100}
        if page:
            query["pageToken"] = page
        result = request_json(f"{API}/blogs/{blog_id}/posts?" + urlencode(query), token=token)
        yield from result.get("items", [])
        page = result.get("nextPageToken")
        if not page:
            break


def upload(filename, blog_id, token):
    title, content, marker = parse_post(filename)
    matches = []
    for status in ("live", "scheduled", "draft"):
        for post in all_posts(blog_id, token, status):
            if marker in post.get("content", "") or post.get("title") == title:
                if status != "draft":
                    raise ValueError(f"Matching {status} article exists; refusing to change or duplicate it: {filename}")
                if "blogger-source:" in post.get("content", "") and marker not in post["content"]:
                    raise ValueError("Same title belongs to a different source file; manual review required")
                matches.append(post)
    if len(matches) > 1:
        raise ValueError("Multiple matching drafts exist; manual review required")

    base = f"{API}/blogs/{blog_id}/posts"
    body = {"kind": "blogger#post", "blog": {"id": blog_id}, "title": title, "content": content}
    if matches:
        current = request_json(f"{base}/{matches[0]['id']}?view=ADMIN", token=token)
        if current.get("status") != "DRAFT":
            raise ValueError("Matched post is no longer DRAFT; stopping")
        if not current.get("etag"):
            raise ValueError("Missing draft ETag; refusing unguarded update")
        result = request_json(
            f"{base}/{current['id']}", token=token, data=body, method="PUT", etag=current["etag"]
        )
        action = "Updated"
    else:
        result = request_json(base + "?isDraft=true", token=token, data=body, method="POST")
        action = "Created"

    if result.get("status") != "DRAFT" or not result.get("id"):
        raise RuntimeError("Blogger response did not confirm DRAFT; inspect Blogger before retrying")
    confirmed = request_json(f"{base}/{result['id']}?view=ADMIN", token=token)
    if confirmed.get("status") != "DRAFT":
        raise RuntimeError("Read-back did not confirm DRAFT; manual inspection required")
    print(f"{action}: {filename}; post_id={result['id']}; confirmed_status=DRAFT")
    if os.getenv("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as summary:
            summary.write(f"- {action} `{filename}` — verified **DRAFT**; post ID `{result['id']}`.\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file-list")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--auth-check", action="store_true")
    args = parser.parse_args()

    if args.auth_check:
        if args.validate_only:
            raise ValueError("--auth-check cannot be combined with --validate-only")
        verify_auth()
        return

    if not args.file_list:
        raise ValueError("--file-list is required unless --auth-check is used")

    files = list(
        dict.fromkeys(
            line.strip() for line in Path(args.file_list).read_text().splitlines() if line.strip()
        )
    )
    for filename in files:
        parse_post(filename)
    if args.validate_only:
        print(f"Validated {len(files)} Blogger HTML file(s); no network requests")
        return
    if not files:
        print("No changed Blogger HTML files")
        return

    blog_id = blog_id_from_env()
    token = access_token()
    for filename in files:
        upload(filename, blog_id, token)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError, KeyError) as error:
        print(f"Upload stopped: {error}", file=sys.stderr)
        sys.exit(1)
