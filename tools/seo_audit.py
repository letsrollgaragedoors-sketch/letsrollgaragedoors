#!/usr/bin/env python3
"""SEO + GEO audit of the live site (what Google and AI crawlers actually fetch).

Fetches every URL in sitemap.xml plus the site files, then checks titles, descriptions, canonicals, robots,
headings, JSON-LD, Open Graph, images, internal links, NAP consistency and AI-search signals.
Run from the repo root:  python tools/seo_audit.py            (prints a report, writes tools/seo_audit.json)
"""
import re, json, sys, os, html, urllib.request, urllib.error, concurrent.futures as cf
from collections import Counter, defaultdict

BASE = 'https://www.letsrollgaragedoors.com'
UA = {'User-Agent': 'Mozilla/5.0 (compatible; LetsRollSEOAudit/1.0)'}
PHONE_DIGITS = '5129474451'


def fetch(url, method='GET', timeout=30):
    req = urllib.request.Request(url, headers=UA, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read() if method == 'GET' else b''
            return r.status, dict(r.headers), body, r.geturl()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), b'', url
    except Exception as e:
        return 0, {}, str(e).encode(), url


def txt(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()


def jsonld(h):
    out, errs = [], []
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', h, re.S):
        try:
            out.append(json.loads(m.group(1)))
        except Exception as e:
            errs.append(str(e)[:80])
    return out, errs


def walk(node):
    if isinstance(node, dict):
        yield node
        for v in node.values():
            yield from walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from walk(v)


def types_of(blocks):
    ts = Counter()
    for b in blocks:
        for n in walk(b):
            t = n.get('@type')
            for x in (t if isinstance(t, list) else [t]):
                if x:
                    ts[x] += 1
    return ts


def audit_page(url):
    st, hd, body, final = fetch(url)
    h = body.decode('utf-8', 'replace')
    P = {'url': url, 'status': st, 'final': final, 'bytes': len(body)}
    if st != 200:
        return P
    g = lambda pat, flags=re.S: (re.search(pat, h, flags) or [None, None])[1]
    P['title'] = txt(g(r'<title>(.*?)</title>') or '')
    P['desc'] = html.unescape(g(r'<meta name="description" content="(.*?)"') or '')
    P['canonical'] = g(r'<link rel="canonical" href="(.*?)"')
    P['robots'] = g(r'<meta name="robots" content="(.*?)"')
    P['lang'] = g(r'<html[^>]*lang="(.*?)"')
    P['viewport'] = bool(g(r'<meta name="viewport" content="(.*?)"'))
    P['og'] = {k: bool(g(r'<meta property="og:%s" content="(.*?)"' % k)) for k in ('title', 'description', 'image', 'url', 'type')}
    P['twitter'] = bool(g(r'<meta name="twitter:card" content="(.*?)"'))
    hs = [(int(m.group(1)), txt(m.group(2))) for m in re.finditer(r'<h([1-6])[^>]*>(.*?)</h\1>', re.sub(r'<script.*?</script>|<style.*?</style>', '', h, flags=re.S), re.S)]
    P['h1'] = [t for l, t in hs if l == 1]
    P['h2n'], P['h3n'] = sum(1 for l, _ in hs if l == 2), sum(1 for l, _ in hs if l == 3)
    skips = 0
    last = 0
    for l, _ in hs:
        if last and l > last + 1:
            skips += 1
        last = l
    P['heading_skips'] = skips
    body_html = re.sub(r'<script.*?</script>|<style.*?</style>|<nav.*?</nav>|<footer.*?</footer>', '', h, flags=re.S)
    P['words'] = len(txt(body_html).split())
    blocks, errs = jsonld(h)
    P['jsonld_types'] = dict(types_of(blocks))
    P['jsonld_errors'] = errs
    faq_q = sum(1 for b in blocks for n in walk(b) if n.get('@type') == 'Question')
    P['faq_schema'] = faq_q
    P['faq_visible'] = len(re.findall(r'<details', h))
    P['nap_phone'] = PHONE_DIGITS in re.sub(r'\D', '', ' '.join(json.dumps(b) for b in blocks)) if blocks else False
    # schema price strings
    P['schema_prices'] = sorted(set(re.findall(r'\$\s?[\d,]{3,6}', ' '.join(json.dumps(b) for b in blocks))))
    imgs = re.findall(r'<img\b[^>]*>', h)
    P['imgs'] = len(imgs)
    P['img_no_alt'] = sum(1 for i in imgs if not re.search(r'\balt="[^"]+"', i))
    P['img_no_dims'] = sum(1 for i in imgs if not (re.search(r'\bwidth="', i) and re.search(r'\bheight="', i)))
    P['hero_lazy'] = bool(imgs) and 'loading="lazy"' in imgs[0] if imgs else False
    P['render_blocking_css'] = len(re.findall(r'<link rel="stylesheet"', h))
    P['links'] = re.findall(r'<a\b[^>]*href="([^"#][^"]*|#[^"]*)"', h)
    P['ext_no_noopener'] = sum(1 for a in re.findall(r'<a\b[^>]*target="_blank"[^>]*>', h) if 'noopener' not in a)
    P['mixed'] = len(re.findall(r'(?:src|href)="http://', h))
    P['cache'] = hd.get('Cache-Control') or hd.get('cache-control')
    P['modified'] = g(r'"dateModified"\s*:\s*"(.*?)"')
    P['author_schema'] = '"Person"' in ' '.join(json.dumps(b) for b in blocks)
    P['has_breadcrumb_html'] = 'class="breadcrumb"' in h
    return P


def main():
    rep = {}
    st, hd, sm, _ = fetch(BASE + '/sitemap.xml')
    sm = sm.decode('utf-8', 'replace')
    urls = re.findall(r'<loc>(.*?)</loc>', sm)
    lastmods = dict(re.findall(r'<loc>(.*?)</loc>\s*(?:<lastmod>(.*?)</lastmod>)?', sm))
    rep['sitemap'] = {'status': st, 'urls': len(urls), 'lastmod_missing': sum(1 for u in urls if not lastmods.get(u)),
                      'lastmods': dict(Counter(v for v in lastmods.values() if v)),
                      'has_priority': '<priority>' in sm, 'has_changefreq': '<changefreq>' in sm}
    local = [f for f in os.listdir('.') if f.endswith('.html')]
    rep['pages_on_disk_not_in_sitemap'] = sorted(f for f in local if f not in ('index.html',) and f'{BASE}/{f}' not in urls)
    rep['sitemap_urls_without_page'] = sorted(u for u in urls if u != BASE + '/' and not os.path.exists(u.split('/')[-1]))
    with cf.ThreadPoolExecutor(8) as ex:
        pages = list(ex.map(audit_page, urls))
    rep['pages'] = pages
    # site files
    files = {}
    for f in ('robots.txt', 'llms.txt', 'sitemap.xml', 'favicon.ico', 'logo.png', 'css/workorder.css', 'js/widgets.js'):
        s, h2, b, _ = fetch(BASE + '/' + f)
        files[f] = {'status': s, 'bytes': len(b), 'type': h2.get('Content-Type'), 'cache': h2.get('Cache-Control')}
    rep['files'] = files
    rep['robots_txt'] = fetch(BASE + '/robots.txt')[2].decode('utf-8', 'replace')
    rep['llms_txt'] = fetch(BASE + '/llms.txt')[2].decode('utf-8', 'replace')
    # protocol / host redirects
    red = {}
    for u in ('http://letsrollgaragedoors.com/', 'http://www.letsrollgaragedoors.com/', 'https://letsrollgaragedoors.com/'):
        s, h2, _, fin = fetch(u, 'GET')
        red[u] = {'status': s, 'final': fin}
    rep['redirects'] = red
    # internal link + anchor check against local files
    ids = {}
    for f in local:
        ids[f] = set(re.findall(r'\bid="([^"]+)"', open(f, encoding='utf-8').read()))
    broken = defaultdict(list)
    for p in pages:
        for href in p.get('links', []):
            if re.match(r'(tel:|mailto:|sms:|javascript:)', href):
                continue
            u = href
            if u.startswith(BASE):
                u = u[len(BASE):] or '/'
            if re.match(r'https?://', u):
                continue
            path, _, frag = u.partition('#')
            if not path or path == '/':
                path = 'index.html' if (u.startswith('/') or u.startswith('#')) and not u.startswith('#') else p['url'].split('/')[-1] or 'index.html'
            if u.startswith('#'):
                path = p['url'].split('/')[-1] or 'index.html'
            path = path.lstrip('/').split('?')[0]
            if path == '':
                path = 'index.html'
            if not os.path.exists(path):
                broken[p['url']].append(href)
            elif frag and frag not in ids.get(path, set()) and path.endswith('.html'):
                broken[p['url']].append(href + '  (anchor missing)')
    rep['broken_links'] = {k: sorted(set(v)) for k, v in broken.items()}
    # public files that should not be public
    rep['exposed_files'] = [f for f in ('blog-fixes-patch.md', 'patch_phase3b_links.py', 'tools/apply_redesign.py', 'tools/design-b-source.html',
                                        'skills-lock.json', 'tools/seo_audit.py') if fetch(BASE + '/' + f, 'GET')[0] == 200]
    json.dump(rep, open('tools/seo_audit.json', 'w', encoding='utf-8'), indent=1, default=str)
    print('audit complete:', len(pages), 'pages')


if __name__ == '__main__':
    main()
