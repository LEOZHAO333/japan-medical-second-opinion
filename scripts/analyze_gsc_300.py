#!/usr/bin/env python3
import csv, sys, math
from collections import defaultdict
from urllib.parse import urlparse

PROTECTED_TERMS = [
    '批准','适应证','风险','禁忌','接诊','资料','DICOM','病理','监管','临床试验','研究','BNCT','iPS','进口','说明书','药品'
]

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

def norm_path(url):
    try:
        return urlparse(url).path
    except Exception:
        return url

def tier(path):
    if path in P0:
        return 'P0'
    parts = [p for p in path.split('/') if p]
    if len(parts) >= 2 and parts[0] in P1_IDS and parts[1] in P1_IDS[parts[0]]:
        return 'P1'
    return 'P2'

def is_protected(title_or_query):
    s = title_or_query or ''
    return any(k in s for k in PROTECTED_TERMS)

def decide(row, page_totals):
    path = norm_path(row['page'])
    t = tier(path)
    imp = float(row.get('impressions') or 0)
    clk = float(row.get('clicks') or 0)
    ctr_raw = str(row.get('ctr') or '0').replace('%','')
    ctr = float(ctr_raw or 0)
    if ctr > 1:
        ctr = ctr / 100.0
    pos = float(row.get('position') or 0)
    query = row.get('query','')

    if t in ('P0','P1'):
        if imp >= 50 and ctr < 0.02:
            return 'STRENGTHEN','high-value page with impressions but low CTR'
        if 8 <= pos <= 30 and imp > 0:
            return 'STRENGTHEN','high-value page ranking 8-30'
        return 'KEEP','protected priority tier'

    if imp >= 50 and ctr < 0.02:
        return 'STRENGTHEN','impressions >= 50 and CTR < 2%'
    if 8 <= pos <= 30 and imp > 0:
        return 'STRENGTHEN','ranking opportunity 8-30'
    if clk > 0 or imp >= 20:
        return 'KEEP','has real search demand'
    if is_protected(query):
        return 'KEEP','medical/regulatory boundary protected'
    return 'OBSERVE','insufficient data; do not merge/noindex yet'

def main():
    if len(sys.argv) < 2:
        print('Usage: analyze_gsc_300.py <gsc.csv> [output.tsv]')
        sys.exit(2)
    inp = sys.argv[1]
    outp = sys.argv[2] if len(sys.argv) > 2 else 'docs/gsc-action-output.tsv'

    rows = []
    with open(inp, newline='', encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        required = {'page','query','clicks','impressions','ctr','position'}
        missing = required - set(r.fieldnames or [])
        if missing:
            raise SystemExit('Missing columns: ' + ','.join(sorted(missing)))
        rows = list(r)

    page_totals = defaultdict(lambda: {'clicks':0.0,'impressions':0.0})
    for row in rows:
        p = norm_path(row['page'])
        page_totals[p]['clicks'] += float(row.get('clicks') or 0)
        page_totals[p]['impressions'] += float(row.get('impressions') or 0)

    with open(outp,'w',newline='',encoding='utf-8') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(['page','query','tier','clicks','impressions','ctr','position','action','reason'])
        for row in rows:
            action, reason = decide(row, page_totals)
            w.writerow([
                row['page'], row.get('query',''), tier(norm_path(row['page'])),
                row.get('clicks','0'), row.get('impressions','0'), row.get('ctr','0'), row.get('position','0'),
                action, reason
            ])

    print(f'Wrote {outp} from {len(rows)} query rows')
    print('Note: MERGE/NOINDEX are intentionally not automated; they require 60-90+ day evidence and manual intent-overlap review.')

if __name__ == '__main__':
    main()
