#!/usr/bin/env python3
from __future__ import annotations
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TODAY = "2026-10-15"
DATA_DIR = ROOT / "scripts" / "evidence"
CATEGORIES = ["bnct", "checkup", "hospitals", "medicines", "ips", "kampo"]
STYLE = ".evidencePanel{margin:30px 0;padding:22px;border:1px solid #d7e6f2;border-radius:16px;background:#fbfdff}.evidencePanel ul{padding-left:22px}.evidencePanel li{margin:8px 0;line-height:1.8}.evidenceSources{margin-top:14px}.evidenceSources a{word-break:break-word}.evidenceBoundary{margin-top:14px;padding:12px 14px;border-left:4px solid #7c91a7;background:#f6f8fa;line-height:1.7}"

def load_packs():
    packs = {}
    for cat in CATEGORIES:
        p = DATA_DIR / f"{cat}.json"
        packs.update(json.loads(p.read_text(encoding="utf-8")))
    return packs

def update_schema(text, urls):
    pat = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
    def repl(m):
        try:
            data = json.loads(m.group(1))
        except Exception:
            return m.group(0)
        if isinstance(data, dict) and data.get("@type") == "MedicalWebPage":
            data["dateModified"] = TODAY
            data["citation"] = urls
            return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + '</script>'
        return m.group(0)
    return pat.sub(repl, text)

def render(pack):
    facts = ''.join('<li>' + html.escape(x) + '</li>' for x in pack['facts'])
    srcs = ''.join('<li><a href="' + html.escape(url, quote=True) + '" target="_blank" rel="noopener noreferrer">' + html.escape(label) + '</a></li>' for label, url in pack['sources'])
    return '<!-- JMAI_EVIDENCE_START --><section class="evidencePanel" data-jmai-evidence="s30"><h2>权威证据与官方核对</h2><p class="meta"><strong>证据核对日期：</strong>' + TODAY + '｜优先使用日本监管机构、接诊医院官方资料和原始研究。</p><ul>' + facts + '</ul><h3>优先核对来源</h3><ol class="evidenceSources">' + srcs + '</ol><div class="evidenceBoundary"><strong>不能直接推出：</strong>' + html.escape(pack['boundary']) + '</div></section><!-- JMAI_EVIDENCE_END -->'

def inject(path, pack):
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'<!-- JMAI_EVIDENCE_START -->.*?<!-- JMAI_EVIDENCE_END -->', '', text, flags=re.S)
    if '.evidencePanel{' not in text:
        text = text.replace('</style>', STYLE + '</style>', 1)
    block = render(pack)
    marker = '<!-- JMAI_DECISION_START -->'
    if marker in text:
        text = text.replace(marker, block + marker, 1)
    elif '<h2>常见问题</h2>' in text:
        text = text.replace('<h2>常见问题</h2>', block + '<h2>常见问题</h2>', 1)
    else:
        raise RuntimeError(f'No evidence injection point: {path}')
    urls = [u for _, u in pack['sources']]
    text = update_schema(text, urls)
    path.write_text(text, encoding='utf-8', newline='\n')

def write_registry(packs):
    rows = ['path\tfacts\tsources\tdomains']
    for key, pack in packs.items():
        domains = []
        for _, url in pack['sources']:
            m = re.match(r'https://([^/]+)', url)
            if m and m.group(1) not in domains:
                domains.append(m.group(1))
        rows.append(f"{key}\t{len(pack['facts'])}\t{len(pack['sources'])}\t{','.join(domains)}")
    (ROOT / 'docs' / 's30-evidence-registry.tsv').write_text('\n'.join(rows) + '\n', encoding='utf-8')

def qa(packs):
    errors = []
    priorities = set(packs)
    for key, pack in packs.items():
        path = ROOT / key / 'index.html'
        if not path.exists():
            errors.append('missing ' + key)
            continue
        text = path.read_text(encoding='utf-8')
        if text.count('JMAI_EVIDENCE_START') != 1:
            errors.append('bad evidence block count ' + key)
        if 'data-jmai-evidence="s30"' not in text:
            errors.append('missing evidence marker ' + key)
        urls = [u for _, u in pack['sources']]
        for u in urls:
            if u not in text:
                errors.append('missing source ' + key + ' ' + u)
        medical = None
        for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', text, re.S):
            try:
                data = json.loads(raw)
            except Exception:
                continue
            if isinstance(data, dict) and data.get('@type') == 'MedicalWebPage':
                medical = data
                break
        if not medical:
            errors.append('MedicalWebPage missing ' + key)
        else:
            if medical.get('citation') != urls:
                errors.append('citation mismatch ' + key)
            if medical.get('dateModified') != TODAY:
                errors.append('dateModified mismatch ' + key)
        if 'FAQPage' not in text or 'rel="canonical"' not in text:
            errors.append('canonical/schema lost ' + key)
    for cat in CATEGORIES:
        for p in (ROOT / cat).glob('[0-9][0-9][0-9]/index.html'):
            key = cat + '/' + p.parent.name
            has = 'data-jmai-evidence="s30"' in p.read_text(encoding='utf-8')
            if has and key not in priorities:
                errors.append('non-S30 evidence marker ' + key)
    if len(packs) != 30:
        errors.append('expected 30 packs, got ' + str(len(packs)))
    if errors:
        raise SystemExit('\n'.join(errors))
    print('S30 evidence QA PASS:', len(packs), 'pages')

def main():
    packs = load_packs()
    for key, pack in packs.items():
        inject(ROOT / key / 'index.html', pack)
    write_registry(packs)
    qa(packs)

if __name__ == '__main__':
    main()
