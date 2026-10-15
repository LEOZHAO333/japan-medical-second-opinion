#!/usr/bin/env python3
from pathlib import Path
from html import unescape
import re, csv
from difflib import SequenceMatcher

ROOT = Path('.')
CATS = ['bnct','ips','checkup','medicines','hospitals','kampo']
P0 = {
    '/bnct/001/','/bnct/004/','/bnct/010/','/bnct/024/',
    '/checkup/005/','/checkup/006/','/checkup/023/',
    '/hospitals/013/','/medicines/004/','/ips/003/'
}
P1_IDS = {
    'bnct': {'001','004','010','011','016','017','021','022','024','029'},
    'checkup': {'004','005','006','009','015','017','022','023'},
    'hospitals': {'001','004','013','020','025'},
    'medicines': {'004','017','029'},
    'ips': {'003','007'},
    'kampo': {'010','011'},
}

def strip_brand(s):
    return re.sub(r'\s*[｜|]\s*JapanMedAI.*$','',s).strip()

def extract_title(txt):
    m = re.search(r'<title>(.*?)</title>', txt, re.I|re.S)
    return strip_brand(unescape(re.sub(r'<[^>]+>','',m.group(1))).strip()) if m else ''

def extract_desc(txt):
    m = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']',txt,re.I|re.S)
    return unescape(m.group(1).strip()) if m else ''

def tier(cat, pid):
    path=f'/{cat}/{pid}/'
    if path in P0: return 'P0'
    if pid in P1_IDS.get(cat,set()): return 'P1'
    return 'P2'

def main():
    rows=[]
    for cat in CATS:
        for i in range(1,51):
            pid=f'{i:03d}'
            p=ROOT/cat/pid/'index.html'
            if not p.exists():
                raise SystemExit(f'Missing: {p}')
            txt=p.read_text(encoding='utf-8')
            rows.append({
                'category':cat,'id':pid,'tier':tier(cat,pid),
                'url':f'https://www.japanmedai.com/{cat}/{pid}/',
                'title':extract_title(txt),'description':extract_desc(txt),
                'robots':'index,follow' if 'index,follow' in txt else 'CHECK',
                'canonical_ok':'yes' if f'https://www.japanmedai.com/{cat}/{pid}/' in txt else 'no'
            })
    out=ROOT/'docs/seo-300-baseline.tsv'
    with out.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys(),delimiter='\t')
        w.writeheader(); w.writerows(rows)

    pairs=[]
    for idx,a in enumerate(rows):
        for b in rows[idx+1:]:
            if a['category']!=b['category']: continue
            score=SequenceMatcher(None,a['title'],b['title']).ratio()
            if score>=0.66:
                pairs.append((a['category'],a['id'],b['id'],f'{score:.3f}',a['title'],b['title']))
    pairs.sort(key=lambda x: float(x[3]), reverse=True)
    with (ROOT/'docs/seo-cannibalization-precheck.tsv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f,delimiter='\t'); w.writerow(['category','id_a','id_b','title_similarity','title_a','title_b']); w.writerows(pairs)

    assert len(rows)==300
    assert sum(r['tier']=='P0' for r in rows)==10
    assert all(r['canonical_ok']=='yes' for r in rows)
    print(f'baseline=300, P0={sum(r["tier"]=="P0" for r in rows)}, P1={sum(r["tier"]=="P1" for r in rows)}, P2={sum(r["tier"]=="P2" for r in rows)}, title_pairs={len(pairs)}')

if __name__=='__main__': main()
