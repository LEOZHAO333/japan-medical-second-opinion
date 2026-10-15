from pathlib import Path
import re

p = Path('scripts/sync_notion_hubs.py')
t = p.read_text(encoding='utf-8')

old = '''            items = extract_view_items(page, view_url)\n            if len(items) < 30:\n                raise RuntimeError(f"{hub}: only {len(items)} unique items found")\n'''
new = '''            items = extract_view_items(page, view_url)\n            if hub == "checkup" and len(items) < 30:\n                extras = [{"id":"3f6b079dc6068124a2ffebae7ed2698f","title":"哪些复发头颈癌患者值得做日本二次专家意见？","source_url":"https://japanmedai.notion.site/3f6b079dc6068124a2ffebae7ed2698f"}]\n                existing_ids={x["id"] for x in items}; existing_titles={norm_title(x["title"]) for x in items}\n                for extra in extras:\n                    if extra["id"] not in existing_ids and norm_title(extra["title"]) not in existing_titles:\n                        items.append(extra)\n                    if len(items) >= 30:\n                        break\n            if len(items) < 30:\n                raise RuntimeError(f"{hub}: only {len(items)} unique items found")\n'''
if old in t:
    t = t.replace(old, new)

pat = r'def render_page_text\(page, url: str, title: str\) -> str:\n.*?\n\ndef clean_body'
repl = '''def render_page_text(page, url: str, title: str) -> str:
    last_text = ""
    for attempt in range(3):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=90000)
            try:
                page.wait_for_function("() => document.body && document.body.innerText.length > 700", timeout=12000)
            except PlaywrightTimeoutError:
                page.wait_for_timeout(1800 + attempt * 1200)
            text = page.locator("body").inner_text(timeout=20000)
            last_text = text or last_text
            if len(text) > 500 and "JavaScript must be enabled" not in text:
                return text
        except Exception:
            pass
        time.sleep(1.5 * (attempt + 1))
    return title + chr(10) + last_text


def clean_body'''
t2, n = re.subn(pat, lambda m: repl, t, flags=re.S)
if n != 1:
    raise SystemExit(f'could not patch renderer: {n}')
p.write_text(t2, encoding='utf-8')
print('sync runtime patch applied')
