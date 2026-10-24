#!/usr/bin/env python3
"""Build Kampo 100Q pages from locked S0 HTML sources plus QA feedback UI.

Usage:
  python scripts/build_kampo_qa.py
  python scripts/build_kampo_qa.py --check

The six source HTML snapshots are the canonical content inputs. Edit these
sources first and regenerate; do not edit generated pages independently.
"""
from pathlib import Path
import argparse
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/kampo_qa_sources"
TOPICS = {"concepts":14, "quality":9, "indications":36, "safety":23, "evidence":18}

JS = r'''<script>
(function () {
  "use strict";
  var root = document.querySelector("main");
  if (!root || !window.JMAIAnalytics) return;
  var tracker = window.JMAIAnalytics.create({table:"jmai_site_events"});
  root.addEventListener("click", function (event) {
    var btn = event.target.closest("button[data-qa-helpful]");
    if (!btn || !root.contains(btn)) return;
    var panel = btn.closest(".qa-feedback");
    var qid = panel && panel.getAttribute("data-qid");
    var theme = panel && panel.getAttribute("data-theme");
    if (!/^s-\d{3}$/.test(qid || "") || !/^(concepts|quality|indications|safety|evidence)$/.test(theme || "")) return;
    var key = "jmai_qa_feedback_v1_" + qid;
    try {
      if (sessionStorage.getItem(key) === "1") {
        panel.querySelector(".qa-feedback-status").textContent = "感谢反馈";
        return;
      }
    } catch (_) {}
    var helpful = btn.getAttribute("data-qa-helpful") === "true";
    panel.querySelectorAll("button").forEach(function (b) { b.disabled = true; });
    tracker.trackOnce("qa_feedback", {qid:qid,theme:theme,helpful:helpful}, key).then(function (result) {
      if (result && result.ok) {
        try { sessionStorage.setItem(key, "1"); } catch (_) {}
        panel.querySelector(".qa-feedback-status").textContent = "感谢反馈";
      } else {
        panel.querySelectorAll("button").forEach(function (b) { b.disabled = false; });
        panel.querySelector(".qa-feedback-status").textContent = "反馈暂未送达，请稍后再试";
      }
    });
  });
})();
</script>'''

CSS = '''<style>
.qa-feedback{display:flex;align-items:center;flex-wrap:wrap;gap:9px;margin:18px 0;padding:12px 0;border-top:1px solid #e0e6eb}
.qa-feedback button{padding:8px 12px;border:1px solid #a9bfd4;background:#fff;color:#234c76;border-radius:8px;cursor:pointer}
.qa-feedback button:focus-visible{outline:3px solid #2876bf;outline-offset:2px}
.qa-feedback button:disabled{opacity:.55;cursor:default}
.qa-feedback-status{font-size:13px;color:#345}
</style>'''


def render(theme, source):
    if theme == "index":
        return source
    matches = re.findall(r'<article class="qa"><h2 id="(s-\d{3})">', source)
    assert len(matches) == TOPICS[theme], (theme, "source q count", len(matches))
    assert len(set(matches)) == len(matches), (theme, "duplicate qid")
    def add_feedback(m):
        qid = m.group(1)
        fragment = m.group(0)
        panel = (
            '<div class="qa-feedback" data-qid="' + qid + '" data-theme="' + theme + '">'
            '<span>这条回答对您有帮助吗？</span>'
            '<button type="button" data-qa-helpful="true" aria-label="' + qid + ' 有帮助">有帮助</button>'
            '<button type="button" data-qa-helpful="false" aria-label="' + qid + ' 没帮助">没帮助</button>'
            '<span class="qa-feedback-status" aria-live="polite"></span></div>'
        )
        return fragment[:-len("</article>")] + panel + "</article>"
    output, count = re.subn(r'<article class="qa"><h2 id="(s-\d{3})">.*?</article>',
                            add_feedback, source, flags=re.S)
    assert count == TOPICS[theme], (theme, count)
    assert "</body>" in output
    return output.replace("</head>", CSS + "</head>").replace("</body>", JS + "</body>")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    problems = []
    for theme in ("index", *TOPICS):
        source_path = SOURCE / (theme + ".html")
        assert source_path.is_file(), source_path
        target = ROOT / "kampo/qa" / ("" if theme == "index" else theme) / "index.html"
        content = render(theme, source_path.read_text(encoding="utf-8"))
        if args.check:
            if not target.is_file() or target.read_text(encoding="utf-8") != content:
                problems.append(str(target.relative_to(ROOT)))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
    if problems:
        sys.exit("Generated HTML out of date: " + ", ".join(problems))
    print("PASS: 6 regenerated HTML pages, 100 QA feedback panels; deterministic output")


if __name__ == "__main__":
    main()
