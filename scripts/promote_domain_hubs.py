from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_required(text, old, new, label):
    if old not in text:
        raise SystemExit(f"Missing expected fragment: {label}")
    return text.replace(old, new)

# Homepage: all core business cards point first to JapanMedAI first-party hubs.
p = ROOT / "index.html"
t = p.read_text(encoding="utf-8")
t = replace_required(t,
    '<div class="card officialService"><span class="kicker">BNCT</span><h3>BNCT 硼中子俘获治疗</h3><p>介绍 BNCT 的适应范围、证据与就医评估流程。是否适用须由具备相应资质的医疗机构结合具体诊断与既往治疗判断，不能据此推定个人适合。</p></div>',
    '<a class="card officialService" href="/bnct/"><span class="kicker">BNCT</span><h3>BNCT 硼中子俘获治疗</h3><p>介绍 BNCT 的适应范围、证据与就医评估流程。是否适用须由具备相应资质的医疗机构结合具体诊断与既往治疗判断，不能据此推定个人适合。</p><b>进入 BNCT 专题 →</b></a>',
    'homepage BNCT card')
t = replace_required(t,
    '<div class="card officialService"><span class="kicker">REGENERATIVE MEDICINE</span><h3>iPS / 再生医疗</h3><p>持续整理日本 iPS 与再生医疗进展，并区分已获批治疗、临床试验、基础研究和个案治疗；研究进展不代表已成为常规治疗。</p></div>',
    '<a class="card officialService" href="/ips/"><span class="kicker">REGENERATIVE MEDICINE</span><h3>iPS / 再生医疗</h3><p>持续整理日本 iPS 与再生医疗进展，并区分已获批治疗、临床试验、基础研究和个案治疗；研究进展不代表已成为常规治疗。</p><b>进入 iPS / 再生医疗专题 →</b></a>',
    'homepage iPS card')
t = replace_required(t,
    '<div class="card officialService"><span class="kicker">HEALTH CHECKUP</span><h3>日本精密体检</h3><p>根据年龄、风险与筛查目标，匹配日本体检机构与检查方案，并提供赴日流程支持。</p></div>',
    '<a class="card officialService" href="/checkup/"><span class="kicker">HEALTH CHECKUP</span><h3>日本精密体检</h3><p>根据年龄、风险与筛查目标，理解日本体检机构、检查方案与赴日流程。</p><b>进入精密体检专题 →</b></a>',
    'homepage checkup card')
t = replace_required(t,
    '<a class="card officialService" href="/blog/"><span class="kicker">MEDICAL INFORMATION</span><h3>日本新药与医疗情报</h3><p>围绕日本新药、癌症治疗、精准放疗、再生医疗、专家第二意见及日本先进医疗英文内容持续建设知识专题。</p><b>进入医疗知识库 →</b></a>',
    '<a class="card officialService" href="/medicines/"><span class="kicker">MEDICAL INFORMATION</span><h3>日本新药与医疗情报</h3><p>围绕日本新药、获批适应证、研究进展、精准医疗与用药边界持续建设知识专题。</p><b>进入日本新药专题 →</b></a>',
    'homepage medicines card')
t = replace_required(t,
    '<a class="topicPill" href="/medicines/tirzepatide-japan.html">日本新药</a>',
    '<a class="topicPill" href="/bnct/">BNCT</a>\n<a class="topicPill" href="/ips/">iPS / 再生医疗</a>\n<a class="topicPill" href="/checkup/">日本精密体检</a>\n<a class="topicPill" href="/medicines/">日本新药</a>\n<a class="topicPill" href="/hospitals/">日本医院与专家</a>\n<a class="topicPill" href="/kampo/">日本汉方</a>',
    'homepage knowledge hubs')
p.write_text(t, encoding="utf-8")

# Blog category chips: first-party topic hubs become the public entry layer.
p = ROOT / "blog/index.html"
t = p.read_text(encoding="utf-8")
old = '<div class="blogCats"><a href="#archive">日本先进医疗英文版</a><a href="/second-opinion/">二次专家会诊</a><a href="https://japanmedai.notion.site/379b079dc6068060b529e37ef490d25a?v=379b079dc6068008b4f7000c4dafd95b" target="_blank" rel="noopener noreferrer">BNCT</a><a href="https://japanmedai.notion.site/379b079dc6068060b529e37ef490d25a?v=379b079dc60680d48ce5000cca0a58d1" target="_blank" rel="noopener noreferrer">iPS / 再生医疗</a><a href="https://japanmedai.notion.site/379b079dc6068060b529e37ef490d25a?v=379b079dc60680ae8612000c5012060d" target="_blank" rel="noopener noreferrer">日本新药</a><a href="https://japanmedai.notion.site/379b079dc6068060b529e37ef490d25a" target="_blank" rel="noopener noreferrer">全部文章</a></div>'
new = '<div class="blogCats"><a href="#archive">日本先进医疗英文版</a><a href="/second-opinion/">二次专家会诊</a><a href="/bnct/">BNCT</a><a href="/ips/">iPS / 再生医疗</a><a href="/checkup/">精密体检</a><a href="/medicines/">日本新药</a><a href="/hospitals/">医院与专家</a><a href="/kampo/">日本汉方</a><a href="#archive">全部文章</a></div>'
t = replace_required(t, old, new, 'blog category links')
p.write_text(t, encoding="utf-8")

# llms.txt: make first-party hub architecture explicit and demote Notion to supplementary database.
p = ROOT / "llms.txt"
t = p.read_text(encoding="utf-8")
t = t.replace('# Knowledge hub: https://japanmedai.notion.site', '# Supplementary public database: https://japanmedai.notion.site')
anchor = '- Japanese specialist second-opinion information and preparation: https://www.japanmedai.com/second-opinion/\n'
insert = anchor + '- BNCT hub: https://www.japanmedai.com/bnct/\n- iPS / regenerative medicine hub: https://www.japanmedai.com/ips/\n- Precision checkup hub: https://www.japanmedai.com/checkup/\n- Japanese medicines hub: https://www.japanmedai.com/medicines/\n- Hospitals and specialists hub: https://www.japanmedai.com/hospitals/\n- Japanese Kampo hub: https://www.japanmedai.com/kampo/\n'
t = replace_required(t, anchor, insert, 'llms core resources')
t = t.replace('- Knowledge hub: https://japanmedai.notion.site', '- Supplementary public database: https://japanmedai.notion.site')
p.write_text(t, encoding="utf-8")

# llms-full.txt: first-party hubs are preferred answer-engine destinations.
p = ROOT / "llms-full.txt"
t = p.read_text(encoding="utf-8")
t = t.replace('**Knowledge hub:** https://japanmedai.notion.site', '**Supplementary public database:** https://japanmedai.notion.site')
t = t.replace('Public deep-reading database:\nhttps://japanmedai.notion.site', 'First-party BNCT hub:\nhttps://www.japanmedai.com/bnct/\n\nSupplementary public database:\nhttps://japanmedai.notion.site')
anchor = '- Second opinion: https://www.japanmedai.com/second-opinion/\n'
insert = anchor + '- BNCT: https://www.japanmedai.com/bnct/\n- iPS / regenerative medicine: https://www.japanmedai.com/ips/\n- Precision checkup: https://www.japanmedai.com/checkup/\n- Japanese medicines: https://www.japanmedai.com/medicines/\n- Hospitals and specialists: https://www.japanmedai.com/hospitals/\n- Japanese Kampo: https://www.japanmedai.com/kampo/\n'
t = replace_required(t, anchor, insert, 'llms-full preferred locations')
p.write_text(t, encoding="utf-8")

# Main sitemap: make every business hub independently indexable under JapanMedAI.com.
p = ROOT / "sitemap.xml"
t = p.read_text(encoding="utf-8")
anchor = '  <url><loc>https://www.japanmedai.com/zh-hant/</loc><lastmod>2026-10-15</lastmod></url>\n'
insert = anchor + ''.join([
'  <url><loc>https://www.japanmedai.com/bnct/</loc><lastmod>2026-10-15</lastmod></url>\n',
'  <url><loc>https://www.japanmedai.com/ips/</loc><lastmod>2026-10-15</lastmod></url>\n',
'  <url><loc>https://www.japanmedai.com/checkup/</loc><lastmod>2026-10-15</lastmod></url>\n',
'  <url><loc>https://www.japanmedai.com/medicines/</loc><lastmod>2026-10-15</lastmod></url>\n',
'  <url><loc>https://www.japanmedai.com/hospitals/</loc><lastmod>2026-10-15</lastmod></url>\n',
'  <url><loc>https://www.japanmedai.com/kampo/</loc><lastmod>2026-10-15</lastmod></url>\n',
])
t = replace_required(t, anchor, insert, 'sitemap hub entries')
p.write_text(t, encoding="utf-8")

print('Promoted first-party domain hubs successfully')
