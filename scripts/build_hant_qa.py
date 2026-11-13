#!/usr/bin/env python3
"""Traditional-Chinese twins of the two 100-question pages (BNCT, cancer second opinion).

Run after the simplified generators: python3 scripts/build_hant_qa.py [--check]
Source = the generated simplified page; output = OpenCC s2twp conversion with zh-Hant lang, own canonical,
og:locale zh_TW and reciprocal hreflang (the simplified page gets a matching hreflang block that the
simplified generators keep via pillar_links.carry). Also syncs sitemap.xml, llms.txt and /zh-hant/ links.
"""
import pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pillar_links  # noqa: E402
from build_pillars import hant, sync_sitemap, marker_sync, SITE  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAGES = [  # simplified path, traditional path, short title for link lists
    ("/bnct/qa/", "/zh-hant/bnct-qa/", "日本BNCT 100問"),
    ("/checkup/qa/", "/zh-hant/checkup-qa/", "癌症第二意見100問"),
]
# links inside the converted page that have a Traditional twin
TWIN = {"/bnct/guide/": "/zh-hant/bnct-guide/", "/second-opinion/guide/": "/zh-hant/second-opinion-guide/",
        "/kampo/guide/": "/zh-hant/kampo-guide/", "/ips/guide/": "/zh-hant/ips-guide/", "/": "/zh-hant/"}
TWIN.update({s: t for s, t, _ in PAGES})
FIX = [("程式", "程序"), ("隨訪", "隨訪")]  # s2twp turns 程序 (procedure) into 程式 (program)


def hreflang(s, t):
    return (pillar_links.HSTART + f'<link rel="alternate" hreflang="zh-CN" href="{SITE}{s}">'
            f'<link rel="alternate" hreflang="zh-TW" href="{SITE}{t}">'
            f'<link rel="alternate" hreflang="x-default" href="{SITE}{s}">' + pillar_links.HEND)


def convert(src, s, t):
    h = hant(src)
    for a, b in FIX:
        h = h.replace(a, b)
    h = re.sub(r'<html lang="[^"]*"', '<html lang="zh-Hant"', h, count=1)
    h = h.replace(f'<link rel="canonical" href="{SITE}{s}">', f'<link rel="canonical" href="{SITE}{t}">')
    h = h.replace(f'content="{SITE}{s}"', f'content="{SITE}{t}"')  # og:url
    h = re.sub(r'<meta property="og:locale" content="[^"]*">', "", h)
    h = h.replace("</title>", '</title><meta property="og:locale" content="zh_TW">', 1)
    h = re.sub(r'"inLanguage": ?"zh-CN"', '"inLanguage":"zh-Hant"', h)
    h = re.sub(r'("@id"|"url"|"item"): ?"' + re.escape(SITE + s) + r'(#[^"]*)?"', lambda m: m.group(1) + ':"' + SITE + t + (m.group(2) or "") + '"', h)
    for a, b in TWIN.items():
        h = h.replace(f'href="{a}"', f'href="{b}"')
    h = h.replace(pillar_links.START, "").replace(pillar_links.END, "")  # twin page is not managed by build_pillars
    h = pillar_links.insert_head(h, hreflang(s, t))
    note = '<p class="small" style="max-width:860px;margin:8px auto;padding:0 16px">本頁為簡體版自動轉換的繁體中文版；頁內連結的文章多為簡體中文。<a href="' + s + '">简体中文版</a></p>'
    h = re.sub(r"(<main[^>]*>)", lambda m: m.group(1) + note, h, count=1) if "<main" in h else h.replace("<body>", "<body>" + note, 1)
    return h


def main():
    check = "--check" in sys.argv
    stale, edits = [], {}

    def edit(rel, fn):
        edits[rel] = fn(edits.get(rel, (ROOT / rel).read_text(encoding="utf-8")))

    for s, t, _ in PAGES:
        src_rel = s.strip("/") + "/index.html"
        edit(src_rel, lambda x, s=s, t=t: pillar_links.insert_head(x, hreflang(s, t)))
        out = convert(edits[src_rel], s, t)
        bad = [w for w in ("程式", "釋出") if w in re.sub(r"<script.*?</script>", "", out, flags=re.S)]
        assert not bad, (t, bad)
        edits[t.strip("/") + "/index.html"] = out
        edit("sitemap.xml", lambda x, t=t: sync_sitemap(x, t, "2026-11-13"))
    llms = "\n## 繁體中文問答\n\n" + "".join(f"- {n}：{SITE}{t}（简体：{SITE}{s}）\n" for s, t, n in PAGES)
    edit("llms.txt", lambda x: marker_sync(x, "hant-qa", llms, lambda tt, full: tt.rstrip("\n") + "\n\n" + full + "\n"))
    links = ('<section class="guide pillarLinks"><div class="wrap"><h2>繁體中文100問</h2><ul>'
             + "".join(f'<li><a href="{t}">{n}</a></li>' for _, t, n in PAGES) + "</ul></div></section>")

    def zh_anchor(x, full):
        i = x.find("<footer")
        return x[:i] + full + x[i:]
    edit("zh-hant/index.html", lambda x: marker_sync(x, "hant-qa", links, zh_anchor))
    for rel, new in edits.items():
        p = ROOT / rel
        if not p.is_file() or p.read_text(encoding="utf-8") != new:
            if check:
                stale.append(rel)
            else:
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(new, encoding="utf-8")
    if check:
        if stale:
            sys.exit("Out of date: " + ", ".join(stale))
        print("PASS: Traditional QA twins up to date", [t for _, t, _ in PAGES])
    else:
        print("Built", [t for _, t, _ in PAGES])


if __name__ == "__main__":
    main()
