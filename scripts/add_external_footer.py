#!/usr/bin/env python3
"""Inject the canonical JapanMed AI public footer into outbound HTML drafts.

This script runs only in CI before WordPress/Blogger draft upload. It does not
publish anything by itself and it does not edit live posts.
"""

import argparse
import re
import sys
from pathlib import Path

PUBLIC_FOOTER = """
<section class="wechat-official-account japanmed-external-footer" aria-label="JapanMed AI official links">
<hr>
<p><strong>JapanMed AI｜日本医疗情报</strong></p>
<p>官网：<a href="https://JapanMedAI.com" rel="noopener noreferrer">JapanMedAI.com</a>｜微信公众号：德川在东京</p>
<p><em>医疗信息仅供科普与就医决策参考，不替代医生诊断或个体化治疗建议。</em></p>
</section>
""".strip()

NEW_FOOTER_RE = re.compile(
    r'<section\b[^>]*class=["\'][^"\']*japanmed-external-footer[^"\']*["\'][^>]*>.*?</section>',
    re.IGNORECASE | re.DOTALL,
)
LEGACY_WECHAT_RE = re.compile(
    r'<section\b[^>]*class=["\'][^"\']*wechat-official-account[^"\']*["\'][^>]*>.*?</section>',
    re.IGNORECASE | re.DOTALL,
)
ARTICLE_END_RE = re.compile(r'</article\s*>', re.IGNORECASE)


def inject_footer(path: Path) -> None:
    if path.is_symlink() or not path.is_file() or path.suffix.lower() != ".html":
        raise ValueError(f"Unsafe or missing HTML file: {path}")
    if path.parent.as_posix() not in {"wordpress", "blogger"}:
        raise ValueError(f"Outbound footer only supports wordpress/ or blogger/: {path}")

    raw = path.read_text(encoding="utf-8")

    if NEW_FOOTER_RE.search(raw):
        updated = NEW_FOOTER_RE.sub(PUBLIC_FOOTER, raw, count=1)
    elif LEGACY_WECHAT_RE.search(raw):
        updated = LEGACY_WECHAT_RE.sub(PUBLIC_FOOTER, raw, count=1)
    else:
        matches = list(ARTICLE_END_RE.finditer(raw))
        if not matches:
            raise ValueError(f"Missing </article> in {path}")
        match = matches[-1]
        updated = raw[: match.start()] + "\n" + PUBLIC_FOOTER + "\n" + raw[match.start() :]

    path.write_text(updated, encoding="utf-8")
    print(f"Footer normalized: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file-list", required=True)
    args = parser.parse_args()

    file_list = Path(args.file_list)
    if not file_list.is_file():
        raise ValueError(f"Missing file list: {file_list}")

    files = [Path(line.strip()) for line in file_list.read_text(encoding="utf-8").splitlines() if line.strip()]
    for path in files:
        inject_footer(path)

    print(f"Normalized {len(files)} outbound HTML file(s)")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f"Footer normalization stopped: {exc}", file=sys.stderr)
        sys.exit(1)
