from __future__ import annotations

import html
import json
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

from pypinyin import lazy_pinyin
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.japanmedai.com"
TODAY = "2026-10-15"
DB = "379b079dc6068060b529e37ef490d25a"

HUBS = {
    "bnct": {
        "label": "BNCT 硼中子治疗",
        "kicker": "BORON NEUTRON CAPTURE THERAPY",
        "view": "379b079dc6068008b4f7000c4dafd95b",
        "description": "JapanMedAI BNCT 硼中子治疗知识库：整理治疗原理、适用边界、复发肿瘤评估、既往放疗、机构选择与资料准备等高频问题。",
        "checklist": ["当前内容属于已批准治疗、临床研究还是基础研究？", "具体癌种、复发位置、病理与影像是否符合接诊机构评估范围？", "既往放疗计划、DICOM-RT、累计剂量和重要器官受量是否齐全？", "BNCT 是否只是局部治疗选择之一，是否仍需系统治疗或多学科评估？", "日本或台湾不同机构的接诊标准、硼药与设备条件是否已逐家确认？"],
    },
    "ips": {
        "label": "iPS / 再生医疗",
        "kicker": "iPS & REGENERATIVE MEDICINE",
        "view": "379b079dc60680d48ce5000cca0a58d1",
        "description": "JapanMedAI iPS 与再生医疗知识库：区分获批产品、临床试验、转化研究与基础研究，整理帕金森、眼科、心肌、免疫细胞等方向的公开信息。",
        "checklist": ["所述技术属于获批产品、临床试验、研究性治疗还是基础研究？", "具体细胞来源、制备方式、适应证与实施机构是什么？", "研究结果来自多少患者、什么设计，能否外推到当前个体？", "潜在肿瘤形成、免疫反应、移植失败等风险是否有长期随访？", "海外患者是否真实具备进入该项目或机构的条件？"],
    },
    "checkup": {
        "label": "日本精密体检",
        "kicker": "PRECISION HEALTH CHECKUP",
        "view": "379b079dc60680cba746000cfbb9c24e",
        "description": "JapanMedAI 日本精密体检与第二意见知识库：围绕癌症筛查、影像、心血管、体检结果解读与异常后转诊路径整理实用信息。",
        "checklist": ["检查是否与年龄、性别、家族史、症状和既往风险真正匹配？", "筛查项目是否存在假阳性、假阴性或过度检查的可能？", "异常结果由谁解释，后续复查、专科转诊和病理确认路径是否明确？", "海外体检前既往影像、病史、用药和家族史是否准备完整？", "体检不能替代针对症状的临床诊疗，出现警示症状是否应直接就医？"],
    },
    "medicines": {
        "label": "日本新药与疗法",
        "kicker": "JAPANESE MEDICINES & THERAPIES",
        "view": "379b079dc60680ae8612000c5012060d",
        "description": "JapanMedAI 日本新药与疗法知识库：整理日本及全球重要药物批准、适应证、研究进展与跨境用药信息，强调处方与监管边界。",
        "checklist": ["药物在日本及目标国家/地区的最新批准状态和适应证是什么？", "研究结果属于随机试验、单臂研究、真实世界数据还是早期探索？", "药物是否为处方药，具体用药应由有资质医生评估和开具？", "禁忌、不良反应、相互作用与监测要求是否核对最新说明书？", "跨境携带、邮寄、储存与冷链是否符合目的地法规和产品要求？"],
    },
    "hospitals": {
        "label": "日本医院与专家",
        "kicker": "JAPAN HOSPITALS & SPECIALISTS",
        "view": "379b079dc6068089aad5000c7ece42a7",
        "description": "JapanMedAI 日本医院与专家知识库：整理大学附属医院、癌症中心、专科优势、第二意见与海外患者资料准备等公开信息。",
        "checklist": ["医院和科室的优势是否与具体疾病、分期和治疗问题匹配？", "专家职务、门诊、研究方向和接诊条件是否以机构官网最新信息为准？", "海外患者是否需要转诊信、医疗协调机构或预先资料审核？", "病理、原始影像、治疗时间线和既往方案是否达到目标医院要求？", "排名与知名度不能代替疾病匹配度，是否优先选择真正对症的团队？"],
    },
    "kampo": {
        "label": "日本汉方",
        "kicker": "JAPANESE KAMPO MEDICINE",
        "view": "379b079dc60680158c1f000cccef59e4",
        "description": "JapanMedAI 日本汉方知识库：整理处方级汉方、常见使用场景、质量控制、医疗体系应用及安全边界，不以传统概念替代临床诊断。",
        "checklist": ["具体汉方制剂是处方药、OTC 还是一般健康产品？", "适应证、组成、剂量与禁忌是否以日本正式说明书为准？", "天然并不等于无风险，是否核对甘草等成分相关不良反应与相互作用？", "症状相似不代表可以自行套方，是否先排除需要现代医学检查的疾病？", "长期使用、合并西药、孕期、儿童或高龄患者是否需要专业医师/药师评估？"],
    },
}

PROPERTY_LABELS = {
    "BNCT章节", "iPS章节", "会诊章节", "内容层级", "分类", "医院专家章节", "推荐顺序", "最终分类",
    "服务总览章节", "案例章节", "汉方章节", "药品章节", "Text", "Empty"
}
GLOBAL_NOISE = {
    "Skip to content", "Get Notion free", "Buntou Co., Ltd. — Services (EN/ZH)", "JapanMed AI｜日本医疗知识库", "/"
}
OLD_PROMO = re.compile(r"让全球华人|公众号[:：].*德川|微信[:：]\s*JAPANYAO111|新特药/干细胞|海外医疗/BNCT", re.I)
HIGH_RISK = re.compile(
    r"(?:\d+(?:\.\d+)?\s*%|客观缓解率|总生存率|治愈率|最高可|2000\s*余?例|10万|神药|无敌|终极答案|震惊世界|改变命运|无路可走|成功案例|保证治愈|彻底治愈|无需手术|无需全麻)", re.I
)

REPLACEMENTS = [
    ("神药", "治疗"), ("终极答案", "如何选择"), ("无敌王者", "优势学科"), ("天花板", "前沿"),
    ("震惊世界", "值得关注"), ("彻底改变", "可能改变"), ("成功案例", "案例解读"),
    ("改变命运", "影响治疗选择"), ("无路可走", "治疗选择受限"), ("治愈率", "长期治疗结果"),
    ("最全", "实用"), ("最强", "重点"), ("独一无二", "具有代表性"),
]


def clean_title(title: str) -> str:
    title = re.sub(r"\*+", "", title).strip()
    for old, new in REPLACEMENTS:
        title = title.replace(old, new)
    title = re.sub(r"[！!]{2,}", "！", title)
    title = re.sub(r"\s+", " ", title).strip(" -—｜")
    return title[:105]


def norm_title(title: str) -> str:
    t = clean_title(title).lower()
    t = re.sub(r"[\s\-—_｜|：:，,。！？!?（）()【】\[\]“”\"'·/]+", "", t)
    return t


def slugify(title: str, pid: str) -> str:
    py = "-".join(lazy_pinyin(clean_title(title)))
    py = re.sub(r"[^a-zA-Z0-9-]+", "-", py).lower()
    py = re.sub(r"-+", "-", py).strip("-")
    if not py:
        py = "guide"
    return f"{py[:72]}-{pid[-6:]}"


def page_id_from_href(href: str) -> str | None:
    href = href.split("#", 1)[0]
    m = re.search(r"([0-9a-f]{32})(?=\?|$)", href, re.I)
    return m.group(1).lower() if m else None


def public_notion_url(pid: str) -> str:
    return f"https://japanmedai.notion.site/{pid}"


def extract_view_items(page, view_url: str) -> list[dict]:
    page.goto(view_url, wait_until="domcontentloaded", timeout=120000)
    page.wait_for_timeout(10000)
    last_count = 0
    stable = 0
    for _ in range(30):
        page.mouse.wheel(0, 2200)
        page.wait_for_timeout(500)
        count = page.locator("a").count()
        if count == last_count:
            stable += 1
        else:
            stable = 0
        last_count = count
        if stable >= 5:
            break
    items, seen_ids, seen_titles = [], set(), set()
    loc = page.locator("a")
    for i in range(loc.count()):
        a = loc.nth(i)
        try:
            href = a.get_attribute("href") or ""
            txt = " ".join((a.inner_text(timeout=2000) or "").split())
        except Exception:
            continue
        pid = page_id_from_href(href)
        if not pid or pid == DB or pid == "9296157b9a1e468eb561d570ce4146ba" or not txt:
            continue
        title = clean_title(txt)
        nt = norm_title(title)
        if pid in seen_ids or nt in seen_titles or len(title) < 5:
            continue
        if title in {"JapanMed AI｜日本医疗知识库", "Buntou Co., Ltd. — Services (EN/ZH)"}:
            continue
        seen_ids.add(pid); seen_titles.add(nt)
        items.append({"id": pid, "title": title, "source_url": public_notion_url(pid)})
        if len(items) >= 30:
            break
    return items


def render_page_text(page, url: str, title: str) -> str:
    last_error = None
    for attempt in range(4):
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=120000)
            try:
                page.wait_for_function(
                    "([needle]) => document.body && document.body.innerText.includes(needle) && document.body.innerText.length > 900",
                    arg=[title[:24]], timeout=30000
                )
            except PlaywrightTimeoutError:
                page.wait_for_timeout(6000 + attempt * 3000)
            text = page.locator("body").inner_text(timeout=30000)
            if len(text) > 700:
                return text
        except Exception as exc:
            last_error = exc
        time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"Failed to render {url}: {last_error}")


def clean_body(raw: str, title: str) -> list[str]:
    lines = [re.sub(r"\s+", " ", x).strip() for x in raw.splitlines()]
    lines = [x for x in lines if x]
    # Start after the second visible title when possible.
    nt = norm_title(title)
    matches = [i for i, line in enumerate(lines) if norm_title(line) == nt]
    start = matches[1] + 1 if len(matches) >= 2 else (matches[0] + 1 if matches else 0)
    lines = lines[start:]

    cleaned = []
    skip_next = False
    for line in lines:
        if skip_next:
            skip_next = False
            continue
        if line in GLOBAL_NOISE:
            continue
        if line in PROPERTY_LABELS and line != "Empty":
            skip_next = True
            continue
        if line == "Empty" or OLD_PROMO.search(line):
            continue
        # Drop most duplicated English translation prose; retain URLs/source labels when present.
        cjk = len(re.findall(r"[\u4e00-\u9fff]", line))
        latin = len(re.findall(r"[A-Za-z]", line))
        if cjk == 0 and latin > 45 and not line.startswith("http"):
            continue
        if HIGH_RISK.search(line):
            # Replace unverified outcome/absolute claims with a durable safety sentence once.
            marker = "涉及疗效比例、生存数据、病例数量或绝对化结论时，应回到原始论文、监管文件或医疗机构最新公开资料核对，不能据旧版科普数字推断个人结果。"
            if marker not in cleaned:
                cleaned.append(marker)
            continue
        if len(line) > 4:
            cleaned.append(line)
    # Remove repeated consecutive lines and cap legacy body so pages stay focused.
    result = []
    for line in cleaned:
        if not result or line != result[-1]:
            result.append(line)
    return result[:55]


def direct_answer(lines: list[str], hub: str, title: str) -> str:
    candidates = [x for x in lines if len(x) >= 18 and not re.match(r"^\d+[\.、)）]", x)]
    if candidates:
        text = " ".join(candidates[:2])
        return text[:330]
    defaults = {
        "bnct": "BNCT 是否适合某位患者，不能仅凭病名判断，需要结合病理、复发部位、既往放疗、原始影像以及接诊机构的具体标准综合评估。",
        "ips": "iPS 与再生医疗需要先区分获批治疗、临床试验和研究阶段，再判断具体疾病、细胞产品、实施机构与患者条件。",
        "checkup": "精密体检的价值在于针对风险选择合适检查并建立异常后的复查路径，而不是检查项目越多越好。",
        "medicines": "新药信息首先要核对最新批准状态、适应证、研究证据与处方要求，不能把研究结果直接当作个人用药建议。",
        "hospitals": "选择日本医院和专家时，应优先看疾病与科室匹配度、接诊条件和资料要求，而不是只看医院名气或排名。",
        "kampo": "日本汉方属于规范化药物体系的一部分，但具体制剂是否适合使用仍需结合症状、诊断、合并用药与安全风险由专业人员评估。",
    }
    return defaults[hub]


def paragraphs_html(lines: list[str]) -> str:
    if not lines:
        return "<p>该条目来源于 JapanMed AI 既有 Notion 知识库。同步到主域后仅保留可用于健康教育的核心信息；涉及具体批准状态、疗效数字与个体治疗判断的内容需要进一步核对原始来源。</p>"
    out = []
    for line in lines:
        esc = html.escape(line)
        if len(line) <= 70 and (line.endswith("？") or re.match(r"^\d+[\.、)）]", line) or line.endswith("：")):
            out.append(f"<h2>{esc}</h2>")
        else:
            out.append(f"<p>{esc}</p>")
    return "\n".join(out)


def article_html(hub: str, cfg: dict, item: dict, body_lines: list[str], related: list[dict]) -> str:
    title = clean_title(item["title"])
    slug = item["slug"]
    url = f"{SITE}/{hub}/{slug}.html"
    answer = direct_answer(body_lines, hub, title)
    desc = answer[:155]
    checks = "".join(f"<li>{html.escape(x)}</li>" for x in cfg["checklist"])
    related_html = "".join(f'<li><a href="/{hub}/{r["slug"]}.html">{html.escape(clean_title(r["title"]))}</a></li>' for r in related)
    schema = {
        "@context":"https://schema.org", "@type":"Article", "headline":title, "description":desc,
        "dateModified":TODAY, "inLanguage":"zh-CN", "mainEntityOfPage":{"@type":"WebPage","@id":url},
        "author":{"@type":"Organization","name":"JapanMedAI Editorial Team","url":SITE+"/"},
        "publisher":{"@type":"Organization","name":"Buntou Co., Ltd.","alternateName":"文腾株式会社","url":SITE+"/"},
        "isPartOf":{"@type":"CollectionPage","name":cfg["label"],"url":f"{SITE}/{hub}/"},
        "isAccessibleForFree": True
    }
    return f'''<!doctype html><html lang="zh-CN"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}｜JapanMedAI {html.escape(cfg['label'])}</title>
<meta name="description" content="{html.escape(desc, quote=True)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:site_name" content="JapanMedAI"><meta property="og:title" content="{html.escape(title, quote=True)}"><meta property="og:description" content="{html.escape(desc, quote=True)}"><meta property="og:url" content="{url}"><meta property="og:locale" content="zh_CN">
<meta name="twitter:card" content="summary"><meta name="twitter:title" content="{html.escape(title, quote=True)}"><meta name="twitter:description" content="{html.escape(desc, quote=True)}">
<link rel="stylesheet" href="/assets/jmai.css"><style>.articleWrap{{max-width:900px;margin:auto;padding:42px 20px 72px}}.articleWrap p,.articleWrap li{{line-height:1.86}}.answer{{padding:18px 20px;border:1px solid #dbe7f2;background:#f7fbff;border-radius:14px}}.meta{{font-size:13px;opacity:.72}}.verify{{border-left:4px solid #5d7e9c;padding:14px 18px;background:#f7fafc;margin:22px 0}}.sourceBox{{margin-top:32px;padding:18px;border:1px solid #dfe8ef;border-radius:14px;background:#f8fbfd}}</style>
<script type="application/ld+json">{json.dumps(schema,ensure_ascii=False,separators=(',',':'))}</script>
</head><body>
<div class="top"><div class="wrap nav navHome"><a class="brand" href="/">JapanMed AI<small>日本医疗资源整合与跨境医疗信息平台</small></a><nav class="navMenu"><a href="/">首页</a><a href="/{hub}/">{html.escape(cfg['label'])}</a><a href="/second-opinion/">二次会诊</a><a href="/blog/">医疗知识库</a></nav></div></div>
<main class="articleWrap"><div class="crumb"><a href="/{hub}/">{html.escape(cfg['label'])}</a> › 知识专题</div><article>
<header><span class="kicker">{html.escape(cfg['kicker'])}</span><h1>{html.escape(title)}</h1><p class="meta">来源同步：JapanMed AI Notion知识库｜重新整理：{TODAY}｜医学审核：待专业复核</p></header>
<section><h2>直接回答</h2><div class="answer"><p>{html.escape(answer)}</p></div></section>
<div class="verify"><strong>核对说明：</strong>本页由 JapanMed AI 既有知识库同步并重新整理。批准状态、适应证、临床数据、费用与机构接诊条件属于时间敏感信息；涉及具体疗效数字时，应以原始监管文件、论文或医疗机构最新公开资料为准。本页不用于判断个体是否适合某项治疗。</div>
<section><h2>知识库内容整理</h2>{paragraphs_html(body_lines)}</section>
<section><h2>S级核对清单</h2><ul>{checks}</ul></section>
<section><h2>相关内容</h2><ul>{related_html}</ul></section>
<section class="sourceBox"><h2>资料来源与边界</h2><p>原知识库记录：<a href="{html.escape(item['source_url'], quote=True)}" target="_blank" rel="nofollow noopener noreferrer">Notion 原记录</a></p><p>本页用于医学信息整理与健康教育，不替代医生诊断、处方、机构接诊审核或个体治疗决定。若涉及急症或快速恶化，应优先在所在地及时就医。</p></section>
</article></main><footer class="footer"><div class="wrap footerInner"><img class="footerLogo" src="/assets/bunto-official-logo.png" alt="BUNTO.CO 文腾株式会社"><div><span class="footerBrand">JapanMed AI · Buntou Medical Japan｜日本文腾医疗</span><br>日本医疗信息整理与跨境医疗导航。</div></div></footer><script src="/assets/jmai-analytics.js"></script></body></html>'''


def hub_html(hub: str, cfg: dict, items: list[dict]) -> str:
    url = f"{SITE}/{hub}/"
    cards = "\n".join(f'<a class="card hubCard" href="/{hub}/{x["slug"]}.html"><h3>{html.escape(clean_title(x["title"]))}</h3></a>' for x in items)
    item_list = [{"@type":"ListItem","position":i+1,"url":f'{url}{x["slug"]}.html',"name":clean_title(x["title"])} for i,x in enumerate(items)]
    schema = {"@context":"https://schema.org","@graph":[
        {"@type":"CollectionPage","name":f'JapanMedAI {cfg["label"]}知识库',"url":url,"description":cfg["description"],"dateModified":TODAY,"isPartOf":{"@type":"WebSite","name":"JapanMedAI","url":SITE+"/"}},
        {"@type":"ItemList","name":f'{cfg["label"]}精选30问',"numberOfItems":len(items),"itemListElement":item_list}
    ]}
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>JapanMedAI {html.escape(cfg['label'])}知识库｜30个核心问题</title><meta name="description" content="{html.escape(cfg['description'], quote=True)}"><link rel="canonical" href="{url}"><meta property="og:type" content="website"><meta property="og:site_name" content="JapanMedAI"><meta property="og:title" content="JapanMedAI {html.escape(cfg['label'])}知识库"><meta property="og:description" content="{html.escape(cfg['description'], quote=True)}"><meta property="og:url" content="{url}"><link rel="stylesheet" href="/assets/jmai.css"><style>.hubHero{{padding:58px 0 30px;background:linear-gradient(180deg,#f7fbff,#fff)}}.hubHero p{{max-width:880px;line-height:1.8}}.hubGrid{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px 20px}}.hubCard{{display:block;text-decoration:none;color:inherit;padding:20px 22px}}.hubCard h3{{margin:0;line-height:1.5;font-size:17px}}@media(max-width:760px){{.hubGrid{{grid-template-columns:1fr}}}}</style><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False,separators=(',',':'))}</script></head><body><div class="top"><div class="wrap nav navHome"><a class="brand" href="/">JapanMed AI<small>日本医疗资源整合与跨境医疗信息平台</small></a><nav class="navMenu"><a href="/">首页</a><a href="/second-opinion/">二次会诊</a><a href="/blog/">医疗知识库</a><a href="/#contact">联系我们</a></nav></div></div><section class="hubHero"><div class="wrap"><span class="kicker">{html.escape(cfg['kicker'])}</span><h1>{html.escape(cfg['label'])}知识库</h1><p>{html.escape(cfg['description'])}</p><p class="small">精选30个核心问题，优先在 JapanMedAI 主域提供可索引的一方版本。内容用于医学信息整理，不替代诊断或个体治疗判断。</p></div></section><section class="section"><div class="wrap"><span class="kicker">TOP 30</span><h2>{html.escape(cfg['label'])}｜30个核心问题</h2><div class="hubGrid">{cards}</div></div></section><footer class="footer"><div class="wrap footerInner"><img class="footerLogo" src="/assets/bunto-official-logo.png" alt="BUNTO.CO 文腾株式会社"><div><span class="footerBrand">JapanMed AI · Buntou Medical Japan｜日本文腾医疗</span><br>内容用于医疗信息整理与健康教育，不替代医生诊疗。</div></div></footer><script src="/assets/jmai-analytics.js"></script></body></html>'''


def update_robots_and_sitemap(all_items: dict[str,list[dict]]) -> None:
    sitemap_path = ROOT / "sitemap-hubs.xml"
    urls = []
    for hub, items in all_items.items():
        urls.append(f"  <url><loc>{SITE}/{hub}/</loc><lastmod>{TODAY}</lastmod></url>")
        urls.extend(f'  <url><loc>{SITE}/{hub}/{x["slug"]}.html</loc><lastmod>{TODAY}</lastmod></url>' for x in items)
    sitemap_path.write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(urls) + '\n</urlset>\n', encoding="utf-8")
    robots = ROOT / "robots.txt"
    txt = robots.read_text(encoding="utf-8")
    line = f"Sitemap: {SITE}/sitemap-hubs.xml"
    if line not in txt:
        txt = txt.rstrip() + "\n" + line + "\n"
        robots.write_text(txt, encoding="utf-8")


def main() -> None:
    all_items: dict[str,list[dict]] = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width":1440,"height":1500}, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/155 Safari/537.36")
        page = context.new_page()
        for hub, cfg in HUBS.items():
            view_url = f"https://japanmedai.notion.site/{DB}?v={cfg['view']}"
            print(f"Collecting {hub}: {view_url}")
            items = extract_view_items(page, view_url)
            if len(items) < 30:
                raise RuntimeError(f"{hub}: only {len(items)} unique items found")
            for item in items:
                item["slug"] = slugify(item["title"], item["id"])
            all_items[hub] = items
            print(f"{hub}: selected {len(items)} unique items")

        total = sum(len(x) for x in all_items.values())
        done = 0
        for hub, cfg in HUBS.items():
            items = all_items[hub]
            out_dir = ROOT / hub
            out_dir.mkdir(parents=True, exist_ok=True)
            for idx, item in enumerate(items):
                done += 1
                print(f"[{done}/{total}] {hub}: {item['title']}")
                raw = render_page_text(page, item["source_url"], item["title"])
                lines = clean_body(raw, item["title"])
                related = [items[(idx+j) % len(items)] for j in (1,2,3)]
                (out_dir / f"{item['slug']}.html").write_text(article_html(hub,cfg,item,lines,related), encoding="utf-8")
                time.sleep(0.8)
            (out_dir / "index.html").write_text(hub_html(hub,cfg,items), encoding="utf-8")
        browser.close()

    update_robots_and_sitemap(all_items)
    (ROOT / "notion-hub-sync-manifest.json").write_text(json.dumps(all_items,ensure_ascii=False,indent=2),encoding="utf-8")
    print("Completed first-party Notion sync:", {k:len(v) for k,v in all_items.items()})

if __name__ == "__main__":
    main()
