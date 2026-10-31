#!/usr/bin/env python3
"""Compare converted pages with git HEAD: head/JSON-LD identical, headings, internal links and visible words kept.
Usage: python tools/check_parity.py page1.html page2.html ...   (chrome text is ignored: nav, footer, scripts)"""
import re, sys, html, subprocess
from collections import Counter

def git_head(p): return subprocess.run(['git','show','HEAD:'+p],capture_output=True,text=True,encoding='utf-8').stdout
def norm_head(t): return re.sub(r'<link rel="preconnect" href="https://fonts\.googleapis\.com">.*?(homepage\.css|workorder\.css)[^>]*>','',t[:t.index('</head>')],flags=re.S)
def main(t):
    a=t.index('<main'); b=t.index('</main>'); return t[a:b]
def words(t):
    t=re.sub(r'<script.*?</script>|<style.*?</style>|<!--.*?-->','',t,flags=re.S)
    t=html.unescape(re.sub(r'<[^>]+>',' ',t)).lower()
    return Counter(re.findall(r"[a-z0-9$%'&@.\-/]+",t))
def links(t):
    s=set()
    for h in re.findall(r'href="([^"]+)"',t):
        if h.startswith(('tel','mailto')) : s.add(h); continue
        h=re.sub(r'^https?://(www\.)?letsrollgaragedoors\.com','',h).split('#')[0].lstrip('/')
        if h and not h.startswith('http'): s.add(h)
    return s
def heads(t):
    return {re.sub(r'\s+',' ',html.unescape(re.sub('<.*?>','',m))).strip().lower() for m in re.findall(r'<h[123][^>]*>(.*?)</h[123]>',re.sub(r'<script.*?</script>','',t,flags=re.S),flags=re.S)}
bad=0
for p in sys.argv[1:]:
    o,n=git_head(p),open(p,encoding='utf-8').read(); pr=[]
    if norm_head(o)!=norm_head(n): pr.append('HEAD differs')
    if n.count('<h1')!=1: pr.append('h1 count %d'%n.count('<h1'))
    mo,mn=main(o),main(n)
    if heads(mo)-heads(mn): pr.append('missing headings %s'%sorted(heads(mo)-heads(mn))[:3])
    if links(mo)-links(mn): pr.append('missing links %s'%sorted(links(mo)-links(mn))[:4])
    miss=words(mo)-words(mn)
    if sum(miss.values())>0: pr.append('missing words %s'%dict(list(miss.most_common(8))))
    if pr: bad+=1; print(p,pr)
print('checked',len(sys.argv)-1,'pages; with problems:',bad)
