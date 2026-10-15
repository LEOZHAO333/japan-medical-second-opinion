#!/usr/bin/env python3
from __future__ import annotations
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TODAY = "2026-10-15"
EVIDENCE_DIR = ROOT / "scripts" / "evidence"


def load_entries():
    out = {}
    for p in sorted(EVIDENCE_DIR.glob("*.json")):
        data = json.loads(p.read_text(encoding="utf-8"))
        out.update(data)
    return out


def answer_parts(item):
    facts = item["facts"]
    # Keep the top answer concise and evidence-led: two verified facts + one explicit boundary.
    return [facts[0], facts[1], f"判断边界：{item['boundary']}"]


def replace_jsonld(text, answer_text):
    pat = re.compile(r'(<script\s+type="application/ld\+json">)(.*?)(</script>)', re.S)
    changed = 0
    def repl(m):
        nonlocal changed
        try:
            data = json.loads(m.group(2))
        except Exception:
            return m.group(0)
        if isinstance(data, dict) and data.get("@type") == "FAQPage":
            ents = data.get("mainEntity") or []
            if ents and isinstance(ents[0], dict):
                ents[0].setdefault("acceptedAnswer", {})["text"] = answer_text
                changed += 1
                return m.group(1) + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + m.group(3)
        if isinstance(data, dict) and data.get("@type") == "MedicalWebPage":
            data["dateModified"] = TODAY
            return m.group(1) + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + m.group(3)
        return m.group(0)
    out = pat.sub(repl, text)
    if changed != 1:
        raise RuntimeError(f"FAQPage update count={changed}")
    return out


def update_page(key, item):
    path = ROOT / key / "index.html"
    text = path.read_text(encoding="utf-8")
    parts = answer_parts(item)
    answer_html = '<div class="answer">' + ''.join(f'<p>{html.escape(x)}</p>' for x in parts) + '</div>'
    plain = ' '.join(parts)

    # Direct answer block.
    text, n1 = re.subn(r'<div class="answer">.*?</div>', answer_html, text, count=1, flags=re.S)
    if n1 != 1:
        raise RuntimeError(f"{key}: direct answer block not found")

    # Visible FAQ first answer: target only the first Q&A immediately after 常见问题.
    faq_pat = re.compile(r'(<h2>常见问题</h2><h3>.*?</h3>)<p>.*?</p>', re.S)
    text, n2 = faq_pat.subn(lambda m: m.group(1) + f'<p>{html.escape(plain)}</p>', text, count=1)
    if n2 != 1:
        raise RuntimeError(f"{key}: visible FAQ first answer not found")

    text = replace_jsonld(text, plain)
    path.write_text(text, encoding="utf-8", newline="\n")


def qa(entries):
    touched = 0
    for key, item in entries.items():
        path = ROOT / key / "index.html"
        text = path.read_text(encoding="utf-8")
        parts = answer_parts(item)
        plain = ' '.join(parts)
        if text.count('data-jmai-evidence="s30"') != 1:
            raise AssertionError(f"{key}: missing S30 evidence marker")
        if parts[0] not in text or parts[1] not in text or item['boundary'] not in text:
            raise AssertionError(f"{key}: evidence-aligned answer missing")
        m = re.search(r'<div class="answer">(.*?)</div>', text, re.S)
        if not m:
            raise AssertionError(f"{key}: no direct answer")
        answer_plain = re.sub(r'<[^>]+>', ' ', m.group(1))
        answer_plain = html.unescape(re.sub(r'\s+', ' ', answer_plain)).strip()
        if answer_plain != plain:
            raise AssertionError(f"{key}: direct answer/plain mismatch")
        faq_visible = re.search(r'<h2>常见问题</h2><h3>.*?</h3><p>(.*?)</p>', text, re.S)
        if not faq_visible or html.unescape(re.sub(r'<[^>]+>', '', faq_visible.group(1))).strip() != plain:
            raise AssertionError(f"{key}: visible FAQ mismatch")
        faq_schema = None
        for raw in re.findall(r'<script\s+type="application/ld\+json">(.*?)</script>', text, re.S):
            try:
                data = json.loads(raw)
            except Exception:
                continue
            if isinstance(data, dict) and data.get('@type') == 'FAQPage':
                faq_schema = data
        if not faq_schema:
            raise AssertionError(f"{key}: FAQ schema missing")
        schema_answer = faq_schema['mainEntity'][0]['acceptedAnswer']['text']
        if schema_answer != plain:
            raise AssertionError(f"{key}: FAQ schema mismatch")
        touched += 1
    if touched != 30:
        raise AssertionError(f"Expected 30 S30 pages, got {touched}")
    print(f"QA PASS: {touched} S30 direct answers aligned to authoritative evidence")


def main():
    entries = load_entries()
    if len(entries) != 30:
        raise SystemExit(f"Expected exactly 30 evidence entries, got {len(entries)}")
    for key, item in sorted(entries.items()):
        update_page(key, item)
    qa(entries)

if __name__ == '__main__':
    main()
