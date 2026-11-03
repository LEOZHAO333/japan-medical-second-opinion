#!/usr/bin/env python3
"""A2「需要专家书面意见？」转化模块：供生成脚本调用，也可直接给静态文章页补模块。

Run: python3 scripts/expert_opinion_module.py [--check]
覆盖：guide/NNN、bnct/NNN 及专题页、ips/NNN、checkup/NNN、patient-questions/* 文章页（不含减重、医院、药品、汉方）。
已有 class="a2Module" 的页面跳过（幂等）。生成脚本（build_guides / build_page_rewrites / build_so_topics）自行调用 module_html()。
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MARK = 'class="evidencePanel a2Module"'
TEXT = {
    "bnct": "BNCT 对患者的筛选非常严格：病理、复发范围、既往放疗剂量和全身状况都会影响能否进入正式评估。建议先由日本相关专科医生根据完整资料出具书面意见，判断是否值得申请评估，以及还有哪些可选路径。",
    "ips": "iPS 和再生医疗的批准范围、临床试验与个人适用性差别很大。如果您正在考虑相关治疗，可以先由日本相关专科医生根据完整资料出具书面意见，弄清现阶段真正可行的选择。",
    "default": "如果您正面临诊断、治疗方案或下一步选择的不确定，可以先用3分钟完成资料自查，再决定是否申请日本相关专科医生的书面第二意见。",
}
TAIL = "第二意见是决策参考，不是转院，也不保证改变原方案。"


def module_html(section="default"):
    t = TEXT.get(section, TEXT["default"])
    return (f'<section {MARK}><h2>需要专家书面意见？</h2><p>{t}{TAIL}</p>'
            '<p><a class="btn" href="/tools/second-opinion-records/">开始资料自查 →</a> '
            '<a href="/second-opinion/">了解日本专家第二意见 →</a></p></section>')


def targets():
    for sec in ("bnct", "ips", "checkup", "guide"):
        for p in sorted((ROOT / sec).glob("*/index.html")):
            if p.parent.name in ("qa",):
                continue
            yield sec, p
    for p in sorted((ROOT / "patient-questions").glob("*/index.html")):
        yield "default", p


def insert(html_, section):
    if MARK in html_:
        return html_
    mod = module_html(section if section in TEXT else "default")
    for anchor in ('<section class="decisionPath">', '</article>', '</main>'):
        if anchor in html_:
            return html_.replace(anchor, mod + anchor, 1)
    return html_


def main():
    check = "--check" in sys.argv
    missing, n = [], 0
    for sec, p in targets():
        old = p.read_text(encoding="utf-8")
        new = insert(old, sec)
        if MARK not in new:
            print("WARN no anchor:", p.relative_to(ROOT)); continue
        if old != new:
            if check:
                missing.append(str(p.relative_to(ROOT)))
            else:
                p.write_text(new, encoding="utf-8"); n += 1
    if check:
        if missing:
            sys.exit("A2 module missing: " + ", ".join(missing[:10]))
        print("PASS: A2 module present on all target pages"); return
    print("A2 module inserted into", n, "pages")


if __name__ == "__main__":
    main()
