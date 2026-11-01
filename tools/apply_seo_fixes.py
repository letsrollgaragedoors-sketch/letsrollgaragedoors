#!/usr/bin/env python3
"""SEO / GEO fixes applied on top of the converted pages (run after the apply_redesign*.py tools).

Idempotent: every change is skipped if it is already present.
  1. shorter meta descriptions (search results cut off after ~160 characters)
  2. FAQPage structured data for pages that show an FAQ but had no schema
  3. BreadcrumbList structured data where the page shows a breadcrumb
  4. gallery / legal pages: robots, Open Graph, Twitter card, basic structured data
  5. fresh dateModified (schema + the visible "Updated" date) on pages whose prices changed
  6. sitemap.xml lastmod for pages whose content changed
Run from the repo root:  python tools/apply_seo_fixes.py   (or python tools/rebuild_site.py to do everything)
"""
import re, json, html, glob

BASE = 'https://www.letsrollgaragedoors.com'
TODAY = '2026-10-31'
TODAY_LONG = 'October 31, 2026'
PHONE = '+15129474451'

DESCRIPTIONS = {
    'index.html': "Same-day & 24/7 garage door repair in Austin, TX. Springs, openers and new doors. Background-checked & insured. Free estimate: (512) 947-4451.",
    'garage-door-wont-open-austin.html': "Garage door won't open in Austin? We repair broken springs, cables, rollers, openers and tracks. Same-day service. Call (512) 947-4451.",
    'same-day-garage-door-service-austin.html': "Need your garage door fixed today? Same-day service across Austin, TX for springs, cables, openers, off-track doors and more. Call (512) 947-4451.",
    'garage-door-maintenance-tips-austin.html': "Five garage door maintenance tasks Austin homeowners can do in under 30 minutes: lubrication, balance, seals, hardware and safety sensors.",
    'garage-door-spring-warning-signs-austin.html': "A broken torsion spring is one of the most dangerous garage door failures. Learn the 7 warning signs every Austin homeowner should know.",
    'garage-door-repair-georgetown.html': "Same-day garage door repair in Georgetown, TX. Springs, cables, openers & more. Serving Sun City, Wolf Ranch & Georgetown zip codes. Call (512) 947-4451.",
    'garage-door-repair-leander.html': "Same-day garage door repair in Leander, TX. Springs, cables, openers & more. Serving Crystal Falls, Travisso, Grand Mesa & Bryson. Call (512) 947-4451.",
    'garage-door-repair-lakeway.html': "Same-day garage door repair in Lakeway, TX. Springs, cables, openers & more. Serving Rough Hollow, Flintrock Falls, The Hills & Bee Cave. Call (512) 947-4451.",
    'garage-door-austin-heat-humidity.html': "Central Texas heat, UV and humidity are hard on garage doors. Here is how Austin homeowners can protect their door through every season.",
    'garage-door-wont-open-close-austin.html': "Garage door won't open or close in Austin, TX? The 10 most common causes with real job photos, what to do, and when to call. (512) 947-4451.",
    'blog.html': "Expert garage door tips, maintenance guides and pricing info from Let's Roll Garage Doors in Austin, TX. Spring safety, opener upgrades and seasonal care.",
    'garage-door-repair-buda.html': "Same-day garage door repair in Buda, TX. Springs, cables, openers & more. Serving Garlic Creek, Sunfield, Shadow Creek & Buda zip codes. Call (512) 947-4451.",
    'garage-door-repair-kyle.html': "Same-day garage door repair in Kyle, TX. Springs, cables, openers & more. Serving 6 Creeks, Anthem, Plum Creek & Crosswinds. Call (512) 947-4451.",
    'what-breaks-garage-doors-austin-by-season.html': "Springs, openers, sensors and seals fail at different times of year in Austin. What we see on service calls, why, and what to check each season.",
}
# pages whose visible prices changed today ($469 -> $499): refresh their dates
PRICE_ARTICLES = ['garage-door-spring-warning-signs-austin.html', 'garage-door-repair-cost-austin.html',
                  'garage-door-wont-open-close-austin.html']
# pages whose content changed materially: new lastmod in the sitemap
LASTMOD_PAGES = ['index.html', 'garage-door-spring-repair-austin.html', 'same-day-garage-door-service-austin.html',
                 'emergency-garage-door-repair-austin.html', 'garage-door-repair-cost-austin.html',
                 'garage-door-spring-warning-signs-austin.html', 'garage-door-wont-open-close-austin.html',
                 'liftmaster-garage-door-openers-austin.html', 'blog.html']


def read(p):
    return open(p, encoding='utf-8').read()


def write(p, t):
    open(p, 'w', encoding='utf-8', newline='\n').write(t)


def ld(obj):
    return '<script type="application/ld+json">\n' + json.dumps(obj, indent=2, ensure_ascii=False) + '\n</script>\n'


def plain(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()


def add_to_head(t, snippet):
    return t.replace('</head>', snippet + '</head>', 1)


def page_url(f):
    return BASE + '/' if f == 'index.html' else f'{BASE}/{f}'


def head_of(t):
    return t[:t.index('</head>')]


def fix_page(f):
    t = read(f)
    orig = t
    head = head_of(t)
    # 1. description
    if f in DESCRIPTIONS:
        assert len(DESCRIPTIONS[f]) <= 160, (f, len(DESCRIPTIONS[f]))
        t = re.sub(r'(<meta name="description" content=")[^"]*(")', lambda m: m.group(1) + DESCRIPTIONS[f] + m.group(2), t, count=1)
    # 2. FAQPage schema from the visible accordion
    if '"FAQPage"' not in head and 'class="svc-faq"' in t:
        qa = re.findall(r'<details><summary><h3>(.*?)</h3></summary>(.*?)</details>', t, re.S)
        if qa:
            faq = {"@context": "https://schema.org", "@type": "FAQPage",
                   "mainEntity": [{"@type": "Question", "name": plain(q),
                                   "acceptedAnswer": {"@type": "Answer", "text": plain(a)}} for q, a in qa]}
            t = add_to_head(t, ld(faq))
    # 3. BreadcrumbList from the visible breadcrumb
    if '"BreadcrumbList"' not in head and 'class="breadcrumb"' in t:
        bc = re.search(r'<div class="breadcrumb">(.*?)</div>', t, re.S).group(1)
        links = re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', bc, re.S)
        last = plain(re.sub(r'<a .*?</a>|<span>.*?</span>', '', bc, flags=re.S))
        items = []
        for href, name in links:
            u = href if href.startswith('http') else BASE + '/' + href.lstrip('/')
            if u.endswith('/index.html'):
                u = BASE + '/'
            items.append((plain(name), u))
        items.append((last, page_url(f)))
        crumbs = {"@context": "https://schema.org", "@type": "BreadcrumbList",
                  "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}
        t = add_to_head(t, ld(crumbs))
    # 4. social tags, robots and basic structured data where missing
    head = head_of(t)
    title = plain((re.search(r'<title>(.*?)</title>', t, re.S) or [0, ''])[1])
    desc = (re.search(r'<meta name="description" content="(.*?)"', head) or [0, ''])[1]
    add = ''
    if 'name="robots"' not in head:
        add += '<meta name="robots" content="index, follow">\n'
    og = lambda k: re.search(r'<meta property="og:%s" content="(.*?)"' % k, head)
    ogt = og('title').group(1) if og('title') else html.escape(title)
    ogd = og('description').group(1) if og('description') else desc
    if not og('title'):
        add += f'<meta property="og:title" content="{ogt}">\n<meta property="og:description" content="{ogd}">\n'
        add += f'<meta property="og:type" content="website">\n<meta property="og:url" content="{page_url(f)}">\n<meta property="og:site_name" content="Let\'s Roll Garage Doors">\n'
    if not og('image'):
        add += f'<meta property="og:image" content="{BASE}/logo.png">\n<meta property="og:image:alt" content="Let\'s Roll Garage Doors logo">\n'
    if 'name="twitter:card"' not in head:
        add += (f'<meta name="twitter:card" content="summary_large_image">\n<meta name="twitter:title" content="{ogt}">\n'
                f'<meta name="twitter:description" content="{ogd}">\n<meta name="twitter:image" content="{BASE}/logo.png">\n')
    if 'application/ld+json' not in head and f in ('gallery.html', 'warranty-terms.html'):
        kind = 'CollectionPage' if f == 'gallery.html' else 'WebPage'
        page = {"@context": "https://schema.org", "@type": kind, "name": title, "url": page_url(f), "description": html.unescape(desc),
                "isPartOf": {"@type": "WebSite", "name": "Let's Roll Garage Doors", "url": BASE + '/'},
                "publisher": {"@type": "HomeAndConstructionBusiness", "name": "Let's Roll Garage Doors", "url": BASE + '/',
                              "telephone": PHONE,
                              "address": {"@type": "PostalAddress", "streetAddress": "720 Airport Blvd #1280",
                                          "addressLocality": "Austin", "addressRegion": "TX", "postalCode": "78702", "addressCountry": "US"}}}
        add += ld(page)
    if add:
        t = add_to_head(t, add)
    # 5. fresh dates on pages whose prices changed
    if f in PRICE_ARTICLES:
        t = re.sub(r'("dateModified"\s*:\s*")[^"]+(")', lambda m: m.group(1) + TODAY + m.group(2), t)
        t = re.sub(r'(<meta property="article:modified_time" content=")[^"]+(")', lambda m: m.group(1) + TODAY + m.group(2), t)
        t = re.sub(r'Updated [A-Z][a-z]+ \d{1,2}, 20\d\d', 'Updated ' + TODAY_LONG, t)
    if t != orig:
        write(f, t)
        return True
    return False


def fix_sitemap():
    t = read('sitemap.xml')
    n = 0
    for f in LASTMOD_PAGES:
        u = page_url(f)
        pat = re.compile(r'(<loc>' + re.escape(u) + r'</loc>\s*<lastmod>)[^<]*(</lastmod>)')
        t, k = pat.subn(lambda m: m.group(1) + TODAY + m.group(2), t)
        n += k
    write('sitemap.xml', t)
    return n


if __name__ == '__main__':
    changed = [f for f in sorted(glob.glob('*.html')) if fix_page(f)]
    print(len(changed), 'pages updated;', fix_sitemap(), 'sitemap lastmod entries set to', TODAY)
