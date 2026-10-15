#!/usr/bin/env python3
from __future__ import annotations

import csv
import html as html_lib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TODAY = "2026-10-15"
BRAND = "JapanMedAI"

SECTION_SIGNAL = {
    "bnct": "日本PMDA、BNCT机构与原始研究",
    "checkup": "日本癌症官方信息与国际患者流程",
    "hospitals": "日本医院国际患者官方规则",
    "medicines": "PMDA/MHLW批准与适应证资料",
    "ips": "PMDA/MHLW再生医疗监管资料",
    "kampo": "PMDA药品资料与处方/OTC边界",
}

HUBS = {
    "bnct": {
        "title": "日本BNCT硼中子治疗：适应证、疗效、风险与申请｜JapanMedAI",
        "description": "日本BNCT硼中子治疗专题：核对批准适应证、复发头颈癌、既往放疗后再评估、疗效数据、副作用、费用和申请资料。关键结论优先依据PMDA、接诊机构与原始研究。",
        "hero": "聚焦日本BNCT硼中子治疗的批准适应证、复发头颈癌、既往放疗后再评估、疗效数据、风险与申请资料。关键结论优先回到PMDA、接诊机构与原始研究核对。",
        "hint": "页面已按决策价值排序：先判断能否评估、证据怎么看、需要准备什么，再进入费用、流程与研究边界。",
    },
    "ips": {
        "title": "日本iPS再生医疗：临床进展、批准状态与申请｜JapanMedAI",
        "description": "日本iPS与再生医疗专题：区分已批准产品、临床试验、研究探索和商业项目，核对帕金森、心肌等进展、海外患者可及性与申请条件。",
        "hero": "聚焦日本iPS与再生医疗的批准产品、临床试验、研究阶段和海外患者可及性。所有页面明确区分“已批准”“临床研究”和“研究探索”。",
        "hint": "页面按实际决策价值排序：先确认监管状态与项目阶段，再判断是否招募、是否接受海外患者及需要哪些资料。",
    },
    "checkup": {
        "title": "日本二次会诊与精密体检：申请、费用、资料与医院｜JapanMedAI",
        "description": "日本癌症二次专家会诊与精密体检专题：涵盖适合人群、申请流程、病理影像资料、费用、远程第二意见、医院选择和异常结果衔接。",
        "hero": "聚焦日本癌症二次专家会诊与精密体检：什么时候值得做、要准备哪些病理和影像、如何申请、费用与医院怎么判断，以及体检异常后如何衔接专科。",
        "hint": "页面按决策价值排序：先明确要解决的医学问题，再准备资料、选择专家或医院，而不是先按套餐和名气做决定。",
    },
    "medicines": {
        "title": "日本新药与新疗法：批准状态、适应证与用药信息｜JapanMedAI",
        "description": "日本新药与新疗法专题：核对PMDA/MHLW批准状态、适应证、临床证据、处方要求和研究阶段，避免把试验结果或海外批准误写成日本已可常规使用。",
        "hero": "聚焦日本新药与新疗法的批准状态、适应证、处方要求、临床证据和研究阶段。优先使用PMDA、厚生劳动省、医院与原始研究资料核对。",
        "hint": "页面按决策价值排序：先确认日本是否批准、批准给谁用，再看证据、可及性和下一步咨询。",
    },
    "hospitals": {
        "title": "日本医院与专家：海外患者预约、转诊与资料预审｜JapanMedAI",
        "description": "日本医院与专家专题：面向海外华人解释国际患者预约、介绍状、医疗协调机构、资料预审、专科匹配、二次意见和赴日接诊流程。",
        "hero": "聚焦日本医院与专家的实际接诊：海外患者如何预约、是否需要介绍状或协调机构、怎样做资料预审，以及如何围绕疾病和治疗目标匹配专科。",
        "hint": "页面按决策价值排序：先确认医院是否接受当前病例与海外患者，再谈名气、行程和正式赴日。",
    },
    "kampo": {
        "title": "日本汉方：处方药、OTC、适应证与安全使用｜JapanMedAI",
        "description": "日本汉方专题：区分医疗用处方汉方与OTC，核对官方适应证、成分、剂量重复、用药风险和就医边界，避免把“天然”误解为可以随意叠加。",
        "hero": "聚焦日本汉方的处方药与OTC区别、官方适应证、成分重复、长期使用风险和就医边界。具体产品信息优先回到PMDA和正式药品资料核对。",
        "hint": "页面按决策价值排序：先确认产品类别与适应证，再核对成分和重复用药风险，最后讨论是否适合个体使用。",
    },
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def plain(fragment: str) -> str:
    fragment = re.sub(r"<script.*?</script>|<style.*?</style>", " ", fragment, flags=re.I | re.S)
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html_lib.unescape(fragment)).strip()


def extract_h1(text: str) -> str:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.I | re.S)
    if not m:
        raise ValueError("missing h1")
    return plain(m.group(1))


def answer_paragraphs(text: str) -> list[str]:
    m = re.search(r'<h2>直接回答</h2>\s*<div class="answer">(.*?)</div>', text, re.I | re.S)
    if not m:
        raise ValueError("missing direct answer")
    ps = [plain(x) for x in re.findall(r"<p[^>]*>(.*?)</p>", m.group(1), re.I | re.S)]
    return [x for x in ps if x]


def clip_sentence(text: str, max_len: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= max_len:
        return text
    pieces = re.split(r"(?<=[。！？；])", text)
    out = ""
    for piece in pieces:
        if not piece:
            continue
        if len(out) + len(piece) <= max_len:
            out += piece
        else:
            break
    if len(out) >= max(40, max_len // 2):
        return out.rstrip()
    return text[: max_len - 1].rstrip("，、；： ") + "…"


def set_title(text: str, value: str) -> str:
    escaped = html_lib.escape(value)
    if re.search(r"<title>.*?</title>", text, re.I | re.S):
        return re.sub(r"<title>.*?</title>", f"<title>{escaped}</title>", text, count=1, flags=re.I | re.S)
    return text.replace("</head>", f"<title>{escaped}</title></head>", 1)


def set_meta(text: str, attr: str, key: str, value: str) -> str:
    value = html_lib.escape(value, quote=True)
    pat1 = re.compile(rf'<meta\s+{attr}=["\']{re.escape(key)}["\'][^>]*>', re.I)
    pat2 = re.compile(rf'<meta\s+[^>]*{attr}=["\']{re.escape(key)}["\'][^>]*>', re.I)
    tag = f'<meta {attr}="{key}" content="{value}">'
    if pat1.search(text):
        return pat1.sub(tag, text, count=1)
    if pat2.search(text):
        return pat2.sub(tag, text, count=1)
    return text.replace("</head>", tag + "</head>", 1)


def update_jsonld(text: str, type_name: str, updater) -> str:
    pattern = re.compile(r'<script([^>]*)type=["\']application/ld\+json["\']([^>]*)>(.*?)</script>', re.I | re.S)

    def repl(match: re.Match) -> str:
        raw = match.group(3).strip()
        try:
            data = json.loads(raw)
        except Exception:
            return match.group(0)
        if isinstance(data, dict) and data.get("@type") == type_name:
            updater(data)
            payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
            return f'<script{match.group(1)}type="application/ld+json"{match.group(2)}>{payload}</script>'
        return match.group(0)

    return pattern.sub(repl, text)


def load_s30() -> list[str]:
    registry = ROOT / "docs/s30-evidence-registry.tsv"
    with registry.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    paths = [r["path"] for r in rows]
    if len(paths) != 30 or len(set(paths)) != 30:
        raise AssertionError(f"expected 30 unique S30 paths, got {len(paths)}")
    return paths


def optimize_s30(paths: list[str]) -> list[tuple[str, str, str]]:
    report = []
    for rel in paths:
        page = ROOT / rel / "index.html"
        text = read_text(page)
        h1 = extract_h1(text)
        paras = answer_paragraphs(text)
        if len(paras) < 2:
            raise AssertionError(f"{rel}: need at least 2 direct-answer paragraphs")

        section = rel.split("/", 1)[0]
        search_title = f"{h1}｜{BRAND}"
        evidence_lead = clip_sentence(" ".join(paras[:2]), 112)
        meta_desc = clip_sentence(
            f"{evidence_lead} 核对{SECTION_SIGNAL[section]}，并说明适用边界与下一步准备。",
            155,
        )
        abstract = " ".join(paras)

        text = set_title(text, search_title)
        text = set_meta(text, "name", "description", meta_desc)
        text = set_meta(text, "property", "og:title", search_title)
        text = set_meta(text, "property", "og:description", meta_desc)
        text = set_meta(text, "name", "twitter:card", "summary")
        text = set_meta(text, "name", "twitter:title", search_title)
        text = set_meta(text, "name", "twitter:description", meta_desc)

        def update_medical(data: dict) -> None:
            data["abstract"] = abstract
            data["dateModified"] = TODAY

        text = update_jsonld(text, "MedicalWebPage", update_medical)
        write_text(page, text)
        report.append((rel, search_title, meta_desc))
    return report


def optimize_hubs() -> None:
    for section, cfg in HUBS.items():
        page = ROOT / section / "index.html"
        text = read_text(page)
        text = set_title(text, cfg["title"])
        text = set_meta(text, "name", "description", cfg["description"])
        text = set_meta(text, "property", "og:title", cfg["title"])
        text = set_meta(text, "property", "og:description", cfg["description"])
        text = set_meta(text, "name", "twitter:card", "summary")
        text = set_meta(text, "name", "twitter:title", cfg["title"])
        text = set_meta(text, "name", "twitter:description", cfg["description"])

        hero_pat = re.compile(
            r'(<section class="hero"><div class="wrap"><span class="kicker">.*?</span><h1>.*?</h1>)'
            r'<p>.*?</p><p class="small">.*?</p>',
            re.I | re.S,
        )
        hero_repl = (
            r'\1'
            + f'<p>{html_lib.escape(cfg["hero"])}</p>'
            + f'<p class="small">{html_lib.escape(cfg["hint"])}</p>'
        )
        text, n = hero_pat.subn(hero_repl, text, count=1)
        if n != 1:
            raise AssertionError(f"{section}: hero block not found")

        def update_collection(data: dict) -> None:
            data["description"] = cfg["description"]
            data["dateModified"] = TODAY

        text = update_jsonld(text, "CollectionPage", update_collection)
        write_text(page, text)


def write_registry(report: list[tuple[str, str, str]]) -> None:
    out = ROOT / "docs/s30-search-entry-registry.tsv"
    with out.open("w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(["path", "title_chars", "description_chars", "title"])
        for rel, title, desc in report:
            w.writerow([rel, len(title), len(desc), title])


def qa(paths: list[str]) -> None:
    titles = set()
    descs = set()
    for rel in paths:
        text = read_text(ROOT / rel / "index.html")
        h1 = extract_h1(text)
        tm = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
        dm = re.search(r'<meta name="description" content="([^"]*)">', text, re.I)
        if not tm or not dm:
            raise AssertionError(f"{rel}: missing title/description")
        title = html_lib.unescape(tm.group(1)).strip()
        desc = html_lib.unescape(dm.group(1)).strip()
        if title != f"{h1}｜{BRAND}":
            raise AssertionError(f"{rel}: search title not aligned to h1")
        if title in titles or desc in descs:
            raise AssertionError(f"{rel}: duplicate title or description")
        titles.add(title)
        descs.add(desc)
        if not (55 <= len(desc) <= 160):
            raise AssertionError(f"{rel}: description length {len(desc)}")
        for needle in [
            f'<meta property="og:title" content="{html_lib.escape(title, quote=True)}">',
            f'<meta property="og:description" content="{html_lib.escape(desc, quote=True)}">',
            f'<meta name="twitter:title" content="{html_lib.escape(title, quote=True)}">',
            f'<meta name="twitter:description" content="{html_lib.escape(desc, quote=True)}">',
            '"@type":"MedicalWebPage"',
            '"abstract":',
            'JMAI_EVIDENCE_START',
            'JMAI_DECISION_START',
        ]:
            if needle not in text:
                raise AssertionError(f"{rel}: missing {needle[:40]}")

    for section, cfg in HUBS.items():
        text = read_text(ROOT / section / "index.html")
        if f"<title>{html_lib.escape(cfg['title'])}</title>" not in text:
            raise AssertionError(f"{section}: hub title mismatch")
        if html_lib.escape(cfg["description"], quote=True) not in text:
            raise AssertionError(f"{section}: hub description mismatch")
        if cfg["hero"] not in html_lib.unescape(text):
            raise AssertionError(f"{section}: hub hero mismatch")

    print(f"QA OK: {len(paths)} S30 search-entry pages + {len(HUBS)} hubs")


def main() -> None:
    paths = load_s30()
    report = optimize_s30(paths)
    optimize_hubs()
    write_registry(report)
    qa(paths)
    print("Search-entry optimization complete")


if __name__ == "__main__":
    main()
