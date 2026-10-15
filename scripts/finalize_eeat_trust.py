from pathlib import Path

ROOT=Path('.')
DATE='2026-10-15'
trust_paths=['trust','about','editorial-policy','medical-review','sources','corrections','authors','privacy']

# sitemap
p=ROOT/'sitemap.xml'
t=p.read_text(encoding='utf-8')
entries=''.join([f'  <url><loc>https://www.japanmedai.com/{x}/</loc><lastmod>{DATE}</lastmod></url>\n' for x in trust_paths if f'https://www.japanmedai.com/{x}/' not in t])
if entries:
    t=t.replace('</urlset>', entries+'</urlset>')
    p.write_text(t,encoding='utf-8')

# visible trust links on key public entry pages
files=['index.html','blog/index.html','bnct/index.html','ips/index.html','checkup/index.html','medicines/index.html','hospitals/index.html','kampo/index.html','second-opinion/index.html','pet/index.html']
block='<div class="trustLinks" style="margin-top:12px;font-size:13px;line-height:1.8"><a href="/trust/">信任中心</a> · <a href="/about/">关于我们</a> · <a href="/editorial-policy/">编辑政策</a> · <a href="/medical-review/">医学复核</a> · <a href="/sources/">来源标准</a> · <a href="/corrections/">纠错</a> · <a href="/privacy/">隐私</a></div>'
for fp in files:
    p=ROOT/fp
    if not p.exists():
        continue
    t=p.read_text(encoding='utf-8')
    if 'href="/trust/"' not in t:
        if '</footer>' in t:
            t=t.replace('</footer>',block+'</footer>',1)
        elif '</body>' in t:
            t=t.replace('</body>',block+'</body>',1)
    if fp=='index.html' and '<nav class="navMenu">' in t and '信任中心</a>' not in t.split('</nav>',1)[0]:
        t=t.replace('</nav>','<a href="/trust/">信任中心</a></nav>',1)
    p.write_text(t,encoding='utf-8')

# internal registry for governance
rows=['path\trole\tpublic_status']
roles={
'trust':'信任中心总入口','about':'平台与主体说明','editorial-policy':'编辑政策','medical-review':'医学复核政策','sources':'来源与证据标准','corrections':'纠错政策','authors':'作者与审核状态','privacy':'隐私政策'}
for x in trust_paths:
    rows.append(f'/{x}/\t{roles[x]}\tprepared_not_production')
(ROOT/'docs').mkdir(exist_ok=True)
(ROOT/'docs/eeat-trust-registry.tsv').write_text('\n'.join(rows)+'\n',encoding='utf-8')

# QA
for x in trust_paths:
    f=ROOT/x/'index.html'
    assert f.exists(), x
    s=f.read_text(encoding='utf-8')
    assert f'https://www.japanmedai.com/{x}/' in s
    assert 'index,follow' in s
    for bad in ['医生审核通过','医学审核通过','专家审核通过']:
        assert bad not in s, (x,bad)
site=(ROOT/'sitemap.xml').read_text(encoding='utf-8')
for x in trust_paths:
    assert f'https://www.japanmedai.com/{x}/' in site
for fp in files:
    p=ROOT/fp
    if p.exists():
        s=p.read_text(encoding='utf-8')
        assert 'href="/trust/"' in s, fp
print('E-E-A-T trust QA PASS:', len(trust_paths), 'trust pages +', len(files), 'entry pages checked')
