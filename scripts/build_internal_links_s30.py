#!/usr/bin/env python3
from pathlib import Path
import csv
import html
import json
import re
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.japanmedai.com"
TODAY = "2026-10-15"

CATEGORIES = {
    "bnct": {
        "name": "BNCT硼中子治疗",
        "s30": ["001","004","010","011","016","017","021","022","024","029"],
        "business_goal": "BNCT资料预审与二次会诊",
        "decision_steps": [
            "先区分日本现行临床适应证、机构接诊范围与研究探索，不用“技术存在”代替“个人可用”。",
            "整理病理、原始DICOM、既往治疗时间线；做过放疗者优先补齐原放疗计划与剂量资料。",
            "由目标机构或专科团队完成资料预审，再决定是否进入赴日评估、进一步检查或其他治疗路径。"
        ],
        "cta_url": "/bnct/024/",
        "cta_label": "查看BNCT资料准备清单",
    },
    "checkup": {
        "name": "日本精密体检与二次会诊",
        "s30": ["004","005","006","009","015","017","022","023"],
        "business_goal": "日本癌症专家二次会诊",
        "decision_steps": [
            "先明确目标是健康筛查、异常复核，还是已有诊断和治疗方案的第二意见；三者需要的资料和专家不同。",
            "把病理、影像、治疗时间线与最想解决的3个决策问题整理成一套资料，而不是只发零散截图。",
            "根据预审结果决定远程第二意见、补充检查、精密体检或赴日面诊，避免先排行程再找医院。"
        ],
        "cta_url": "/second-opinion/",
        "cta_label": "进入二次会诊资料自查",
    },
    "hospitals": {
        "name": "日本医院与专家",
        "s30": ["001","004","013","020","025"],
        "business_goal": "医院匹配与国际患者预审",
        "decision_steps": [
            "先按疾病亚型、治疗阶段和所需技术筛选专家类型，而不是先看医院排名或医生名气。",
            "核对目标医院的国际患者、介绍状、转诊、翻译和资料预审规则，确认是否真正接受该类海外病例。",
            "拿到明确的科室或医院反馈后，再安排翻译、预约和赴日行程。"
        ],
        "cta_url": "/checkup/006/",
        "cta_label": "查看日本会诊资料清单",
    },
    "medicines": {
        "name": "日本新药与疗法",
        "s30": ["004","017","029"],
        "business_goal": "新药信息核对与治疗路径判断",
        "decision_steps": [
            "先核对批准国家/地区、批准日期、准确适应证、治疗线次和证据阶段，避免把研究进展当成已获批治疗。",
            "再核对患者的病理、分期、生物标志物、既往治疗和合并疾病，看是否进入官方适用范围。",
            "最后由接诊医生或正规医疗机构判断处方、接诊和跨境可及性；“日本有药”不等于个人可以直接使用。"
        ],
        "cta_url": "/hospitals/004/",
        "cta_label": "查看日本就医选院与接诊路径",
    },
    "ips": {
        "name": "iPS再生医疗",
        "s30": ["003","007"],
        "business_goal": "正规机构辨别与临床可及性预审",
        "decision_steps": [
            "先把正式批准、临床试验、研究探索、自由诊疗或商业项目分开，避免只凭“已经有人做”判断成熟度。",
            "核对目标疾病、年龄、既往治疗、入组或接诊条件，以及海外患者是否可以申请。",
            "只向可核验的医院、大学、试验注册或正规机构提交资料做预审，再决定是否值得进一步推进。"
        ],
        "cta_url": "/hospitals/025/",
        "cta_label": "查看海外患者资料预审逻辑",
    },
    "kampo": {
        "name": "日本汉方",
        "s30": ["010","011"],
        "business_goal": "日本汉方正规用药信息核对",
        "decision_steps": [
            "先确认准确方名、厂家、剂型，以及属于处方汉方还是OTC产品，避免只按中文俗称判断。",
            "核对官方适应证、成分比例、每日剂量、基础疾病和合并用药，尤其关注重复成分和相互作用风险。",
            "持续症状、异常化验或明确疾病应优先进入正规诊疗；汉方信息不能替代诊断或自行处方。"
        ],
        "cta_url": "/kampo/010/",
        "cta_label": "查看日本处方汉方适应证怎么查",
    },
}

CROSS_LINKS = {
    "bnct": [
        ("/hospitals/001/", "复发头颈癌二次会诊应该找什么类型的专家"),
        ("/checkup/006/", "申请日本二次会诊要准备哪些资料"),
        ("/hospitals/025/", "为什么日本医院常要求海外患者先做资料预审"),
        ("/second-opinion/", "日本二次会诊资料准备入口"),
    ],
    "ips": [
        ("/hospitals/025/", "为什么日本医院常要求海外患者先做资料预审"),
        ("/checkup/023/", "日本二次专家会诊怎么申请"),
        ("/hospitals/004/", "海外就医怎么选日本医院"),
        ("/second-opinion/", "日本二次会诊资料准备入口"),
    ],
    "checkup": [
        ("/hospitals/004/", "海外就医怎么选日本医院"),
        ("/hospitals/025/", "为什么日本医院常要求海外患者先做资料预审"),
        ("/hospitals/020/", "东京大学附属医院国际患者怎么申请"),
        ("/second-opinion/", "日本二次会诊资料准备入口"),
    ],
    "medicines": [
        ("/hospitals/004/", "海外就医怎么选日本医院"),
        ("/hospitals/025/", "为什么日本医院常要求海外患者先做资料预审"),
        ("/checkup/006/", "申请日本二次会诊要准备哪些资料"),
        ("/second-opinion/", "日本二次会诊资料准备入口"),
    ],
    "hospitals": [
        ("/checkup/006/", "申请日本二次会诊要准备哪些资料"),
        ("/checkup/005/", "哪些癌症患者更值得做日本二次专家会诊"),
        ("/checkup/023/", "日本二次专家会诊怎么申请"),
        ("/second-opinion/", "日本二次会诊资料准备入口"),
    ],
    "kampo": [
        ("/medicines/029/", "日本获批药物的处方、接诊与跨境规则"),
        ("/hospitals/004/", "海外就医怎么选日本医院"),
        ("/checkup/023/", "日本二次专家会诊怎么申请"),
        ("/second-opinion/", "日本二次会诊资料准备入口"),
    ],
}

ARTICLE_STYLE = '''
.relatedReading{margin:34px 0 8px;padding-top:24px;border-top:1px solid #dfe8ef}
.relatedReading h2{margin-bottom:14px}
.relatedGrid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}
.relatedGrid a{display:block;padding:14px 16px;border:1px solid #dbe7f2;border-radius:12px;background:#fff;text-decoration:none;color:inherit;line-height:1.55}
.relatedGrid a:hover{text-decoration:underline}
.decisionPath{margin:30px 0;padding:22px;border:1px solid #cfe0ec;border-radius:16px;background:#f7fbff}
.decisionPath ol{padding-left:22px;margin:12px 0 18px}
.decisionPath li{margin:8px 0}
.decisionPath .btn{display:inline-block}
@media(max-width:700px){.relatedGrid{grid-template-columns:1fr}}
'''.strip()

def clean_text(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()

def parse_index(cat):
    p = ROOT / cat / "index.html"
    text = p.read_text(encoding="utf-8")
    found = re.findall(
        rf'<a class="card" href="/{re.escape(cat)}/(\d{{3}})/"[^>]*><h3>(.*?)</h3></a>',
        text, re.S
    )
    if len(found) != 30:
        found = re.findall(
            rf'<a[^>]+href="/{re.escape(cat)}/(\d{{3}})/"[^>]*>\s*<h3>(.*?)</h3>\s*</a>',
            text, re.S
        )
    titles = {pid: clean_text(title) for pid, title in found}
    if len(titles) != 30:
        raise RuntimeError(f"{cat}: expected 30 index titles, got {len(titles)}")
    return text, titles

def classify_intent(title):
    rules = [
        ("费用与价值", r"费用|多少钱|价格|性价比|贵"),
        ("流程与可及性", r"申请|预约|流程|资料|预审|接诊|海外患者|能直接|怎么选医院|怎么申请"),
        ("风险与安全", r"副作用|风险|安全|致癌|不良|长期风险|禁忌"),
        ("批准与证据阶段", r"批准|获批|适应证|监管|临床应用|进入临床|研究阶段"),
        ("疗效与证据", r"效果|疗效|ORR|OS|PFS|数据|靠谱吗|证据|改变率"),
        ("方案比较", r"区别|不同|比较|怎么选|和.+有什么|还是|差在哪"),
        ("适用人群", r"哪些患者|哪些人|适合|能治疗|可以做|值得|是否适合"),
        ("机制与基础理解", r"是什么|原理|为什么|意味着什么"),
    ]
    for label, pat in rules:
        if re.search(pat, title, re.I):
            return label
    return "临床决策判断"

def grams(s):
    s = re.sub(r"[\s，。！？、：；（）()“”\"'·｜/+\-]", "", s)
    for word in ["JapanMedAI","日本","治疗","医疗","患者","怎么","什么","为什么","哪些","应该","可以","是否"]:
        s = s.replace(word, "")
    if len(s) < 2:
        return {s} if s else set()
    return {s[i:i+2] for i in range(len(s)-1)}

def similarity(a, b):
    ga, gb = grams(a), grams(b)
    jac = len(ga & gb) / max(1, len(ga | gb))
    seq = SequenceMatcher(None, a, b).ratio()
    return jac * .7 + seq * .3

def related_same(cat, pid, titles):
    title = titles[pid]
    intent = classify_intent(title)
    scores = []
    for other, ot in titles.items():
        if other == pid:
            continue
        score = similarity(title, ot)
        if classify_intent(ot) == intent:
            score += .16
        scores.append((score, other, ot))
    scores.sort(reverse=True)
    return [(f"/{cat}/{other}/", ot, other) for _, other, ot in scores[:2]]

def cross_for(cat, title):
    links = CROSS_LINKS[cat]
    if cat == "bnct":
        if re.search(r"头颈|放疗", title):
            order = [0,1,2,3]
        elif re.search(r"资料|申请|流程|费用", title):
            order = [1,2,3,0]
        else:
            order = [2,1,3,0]
    elif cat == "checkup":
        if "二次" in title or "会诊" in title:
            order = [1,0,2,3]
        else:
            order = [0,2,1,3]
    elif cat == "hospitals":
        if re.search(r"资料|预审|预约|申请|直接", title):
            order = [0,2,3,1]
        else:
            order = [1,0,3,2]
    elif cat == "medicines":
        if re.search(r"获批|海外|处方|可及", title):
            order = [1,0,2,3]
        else:
            order = [2,0,3,1]
    elif cat == "ips":
        if re.search(r"临床|申请|海外|骗局|商业", title):
            order = [0,1,2,3]
        else:
            order = [2,1,0,3]
    else:
        if re.search(r"处方|OTC|买|海外", title):
            order = [0,1,2,3]
        else:
            order = [1,0,2,3]
    return [links[i] for i in order[:2]]

def strip_block(text, start, end):
    return re.sub(re.escape(start) + r".*?" + re.escape(end), "", text, flags=re.S)

def ensure_style(text):
    if ".relatedReading{" in text:
        return text
    return text.replace("</style>", ARTICLE_STYLE + "</style>", 1)

def s30_decision_html(cat, pid):
    cfg = CATEGORIES[cat]
    cta_url = cfg["cta_url"]
    if cta_url == f"/{cat}/{pid}/":
        cta_url = "/second-opinion/" if cat != "kampo" else "/kampo/011/"
    items = "".join(f"<li>{html.escape(x)}</li>" for x in cfg["decision_steps"])
    return (
        '<!-- JMAI_DECISION_START -->'
        '<section class="decisionPath" data-jmai-s30="1">'
        '<h2>把这个问题转成下一步决策</h2>'
        f"<ol>{items}</ol>"
        f'<a class="btn" href="{cta_url}" data-jmai-track="decision" '
        f'data-jmai-id="s30_{cat}_{pid}" data-jmai-position="decision">{html.escape(cfg["cta_label"])} →</a>'
        '</section>'
        '<!-- JMAI_DECISION_END -->'
    )

def related_html(cat, pid, title, titles):
    same = related_same(cat, pid, titles)
    cross = cross_for(cat, title)
    cards = []
    for url, label, oid in same:
        cards.append(
            f'<a href="{url}" data-jmai-track="related" '
            f'data-jmai-id="rel_{cat}_{pid}_{oid}" data-jmai-position="related">{html.escape(label)}</a>'
        )
    for idx, (url, label) in enumerate(cross, 1):
        safe_target = re.sub(r"[^a-z0-9]+", "_", url.lower()).strip("_")[:40] or f"x{idx}"
        cards.append(
            f'<a href="{url}" data-jmai-track="pathway" '
            f'data-jmai-id="path_{cat}_{pid}_{safe_target}" data-jmai-position="related">{html.escape(label)}</a>'
        )
    return (
        '<!-- JMAI_RELATED_START -->'
        '<section class="relatedReading">'
        '<h2>继续看：与这个决策最相关的内容</h2>'
        '<div class="relatedGrid">' + "".join(cards) + '</div>'
        '</section>'
        '<!-- JMAI_RELATED_END -->'
    ), same, cross

def update_article(cat, pid, title, titles):
    path = ROOT / cat / pid / "index.html"
    text = path.read_text(encoding="utf-8")
    text = strip_block(text, "<!-- JMAI_DECISION_START -->", "<!-- JMAI_DECISION_END -->")
    text = strip_block(text, "<!-- JMAI_RELATED_START -->", "<!-- JMAI_RELATED_END -->")
    text = ensure_style(text)
    related, same, cross = related_html(cat, pid, title, titles)
    block = ""
    if pid in CATEGORIES[cat]["s30"]:
        block += s30_decision_html(cat, pid)
    block += related
    if '<div class="next">' in text:
        text = text.replace('<div class="next">', block + '<div class="next">', 1)
    elif "</article>" in text:
        text = text.replace("</article>", block + "</article>", 1)
    else:
        raise RuntimeError(f"{cat}/{pid}: no insertion point")
    path.write_text(text, encoding="utf-8")
    return same, cross

def update_index(cat, index_text, titles):
    cfg = CATEGORIES[cat]
    order = cfg["s30"] + [pid for pid in sorted(titles) if pid not in cfg["s30"]]
    cards = "\n".join(
        f'<a class="card" href="/{cat}/{pid}/" data-jmai-track="hub" '
        f'data-jmai-id="hub_{cat}_{pid}" data-jmai-position="hub"><h3>{html.escape(titles[pid])}</h3></a>'
        for pid in order
    )
    new_text, n = re.subn(
        r'(<section class="section"><div class="wrap"><div class="grid">).*?(</div></div></section>)',
        lambda m: m.group(1) + cards + m.group(2),
        index_text,
        count=1,
        flags=re.S
    )
    if n != 1:
        raise RuntimeError(f"{cat}: could not rebuild grid")
    new_text = re.sub(
        r'<script id="jmai-itemlist" type="application/ld\+json">.*?</script>',
        "",
        new_text,
        flags=re.S,
    )
    itemlist = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": cfg["name"] + "核心问题",
        "numberOfItems": 30,
        "itemListElement": [
            {"@type": "ListItem", "position": i, "url": f"{SITE}/{cat}/{pid}/", "name": titles[pid]}
            for i, pid in enumerate(order, 1)
        ],
    }
    schema = '<script id="jmai-itemlist" type="application/ld+json">' + json.dumps(itemlist, ensure_ascii=False, separators=(",", ":")) + "</script>"
    new_text = new_text.replace("</head>", schema + "</head>", 1)
    (ROOT / cat / "index.html").write_text(new_text, encoding="utf-8")

def update_analytics():
    path = ROOT / "assets" / "jmai-analytics.js"
    text = path.read_text(encoding="utf-8")
    marker = "JMAI_INTERNAL_LINK_TRACKING_V1"
    if marker in text:
        return
    extra = r'''
/* JMAI_INTERNAL_LINK_TRACKING_V1
   Tracks only anonymous navigation metadata (no free text, medical answers or contact fields). */
(function () {
  "use strict";
  document.addEventListener("click", function (event) {
    var link = event.target && event.target.closest ? event.target.closest("[data-jmai-track]") : null;
    if (!link) return;
    try {
      var tracker = window.JMAIAnalytics && window.JMAIAnalytics.create({
        table: "jmai_site_events",
        scope: "site",
        pageVersion: "topic-cluster-v2"
      });
      if (!tracker) return;
      tracker.track("internal_link_click", {
        kind: link.getAttribute("data-jmai-track") || "internal",
        cta_id: link.getAttribute("data-jmai-id") || "internal_link",
        cta_position: link.getAttribute("data-jmai-position") || "body"
      });
    } catch (_) {}
  }, { passive: true });
})();
'''
    path.write_text(text.rstrip() + "\n" + extra.strip() + "\n", encoding="utf-8")

def write_docs(rows, s30_rows):
    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)
    with (docs / "internal-link-map.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["url","category","page_id","title","search_intent","s30","related_1","related_2","cross_1","cross_2","business_goal"])
        for r in rows:
            w.writerow(r)

    lines = [
        "# JapanMedAI S30 Priority Pages",
        "",
        f"Updated: {TODAY}",
        "",
        "Internal planning file. These 30 pages are the first deep-upgrade cohort because they sit closest to patient decisions, service qualification, document preparation, institution matching or regulated-treatment access.",
        "",
        "| # | Category | URL | Primary search intent | Funnel role | Title |",
        "|---:|---|---|---|---|---|",
    ]
    for i, r in enumerate(s30_rows, 1):
        cat, url, intent, goal, title = r
        lines.append(f"| {i} | {CATEGORIES[cat]['name']} | `{url}` | {intent} | {goal} | {title.replace('|','｜')} |")
    lines += [
        "",
        "## Distribution",
        "",
        "- BNCT: 10",
        "- 精密体检 / 二次会诊: 8",
        "- 医院与专家: 5",
        "- 日本新药与疗法: 3",
        "- iPS再生医疗: 2",
        "- 日本汉方: 2",
        "",
        "## Rule",
        "",
        "The public website does not display an “S级” label. Priority is expressed through stronger internal-link equity, decision-path sections and contextual next-step CTAs.",
    ]
    (docs / "seo-s30-priority.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

def qa():
    total = 0
    s_count = 0
    problems = []
    for cat, cfg in CATEGORIES.items():
        index_text, titles = parse_index(cat)
        hrefs = re.findall(rf'href="/{cat}/(\d{{3}})/"', index_text)
        if hrefs[:len(cfg["s30"])] != cfg["s30"]:
            problems.append(f"{cat}: S30 not first on hub")
        if 'id="jmai-itemlist"' not in index_text:
            problems.append(f"{cat}: missing ItemList")
        for pid in sorted(titles):
            total += 1
            p = ROOT / cat / pid / "index.html"
            t = p.read_text(encoding="utf-8")
            if t.count("JMAI_RELATED_START") != 1:
                problems.append(f"{cat}/{pid}: related block count")
            if t.count('data-jmai-track="related"') < 2 or t.count('data-jmai-track="pathway"') < 2:
                problems.append(f"{cat}/{pid}: missing related/pathway links")
            m = re.search(r'JMAI_RELATED_START.*?JMAI_RELATED_END', t, re.S)
            if not m:
                problems.append(f"{cat}/{pid}: related block missing")
            elif f'href="/{cat}/{pid}/"' in m.group(0):
                problems.append(f"{cat}/{pid}: self related link")
            is_s = pid in cfg["s30"]
            if is_s:
                s_count += 1
                if t.count("JMAI_DECISION_START") != 1 or 'data-jmai-s30="1"' not in t:
                    problems.append(f"{cat}/{pid}: missing S30 decision path")
            elif "JMAI_DECISION_START" in t:
                problems.append(f"{cat}/{pid}: unexpected S30 decision path")
            if f'<link rel="canonical" href="{SITE}/{cat}/{pid}/">' not in t:
                problems.append(f"{cat}/{pid}: canonical")
            if '"@type":"FAQPage"' not in t:
                problems.append(f"{cat}/{pid}: FAQ schema")
    if total != 180:
        problems.append(f"expected 180 pages got {total}")
    if s_count != 30:
        problems.append(f"expected 30 S pages got {s_count}")
    map_path = ROOT / "docs" / "internal-link-map.csv"
    if not map_path.exists() or sum(1 for _ in map_path.open(encoding="utf-8")) != 181:
        problems.append("internal-link-map.csv row count")
    if "JMAI_INTERNAL_LINK_TRACKING_V1" not in (ROOT/"assets/jmai-analytics.js").read_text(encoding="utf-8"):
        problems.append("analytics tracking marker")
    if problems:
        raise RuntimeError("QA failed:\n- " + "\n- ".join(problems))
    print("QA PASS: 180 topic pages, 30 priority pages, static related links, hub ordering, analytics tracking.")

def main():
    rows = []
    s30_rows = []
    for cat, cfg in CATEGORIES.items():
        index_text, titles = parse_index(cat)
        update_index(cat, index_text, titles)
        for pid in sorted(titles):
            title = titles[pid]
            same, cross = update_article(cat, pid, title, titles)
            url = f"{SITE}/{cat}/{pid}/"
            intent = classify_intent(title)
            rows.append([
                url, cfg["name"], pid, title, intent,
                "yes" if pid in cfg["s30"] else "no",
                SITE + same[0][0], SITE + same[1][0],
                SITE + cross[0][0], SITE + cross[1][0],
                cfg["business_goal"],
            ])
            if pid in cfg["s30"]:
                s30_rows.append((cat, url, intent, cfg["business_goal"], title))
    update_analytics()
    write_docs(rows, s30_rows)
    qa()

if __name__ == "__main__":
    main()
