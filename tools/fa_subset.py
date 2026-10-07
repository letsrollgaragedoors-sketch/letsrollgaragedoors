import re, glob, os, json, urllib.request
from fontTools import subset

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
FAV = '6.5.0'
BASE = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/%s/' % FAV
BRANDS = {'facebook-f', 'google', 'instagram', 'yelp'}


def rd(p):
    with open(p, encoding='utf8', newline='') as f:
        return f.read()


def wr(p, s):
    with open(p, 'w', encoding='utf8', newline='') as f:
        f.write(s)


def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read()


html_files = sorted(glob.glob('*.html'))

# 1. icons used
icons = set()
for f in html_files:
    for m in re.finditer(r'class="([^"]*)"', rd(f)):
        for t in m.group(1).split():
            if t.startswith('fa-') and t not in ('fa-solid', 'fa-regular', 'fa-brands'):
                icons.add(t[3:])

# 2. name -> codepoint from official css
fa_css = get(BASE + 'css/all.min.css').decode('utf8')
cmap = {}
for m in re.finditer(r'((?:\.fa-[\w-]+:{1,2}before,?)+)\{[^}]*?content:"\\([0-9a-fA-F]+)"', fa_css):
    for sel in m.group(1).split(','):
        n = re.match(r'\.fa-([\w-]+):', sel)
        if n:
            cmap[n.group(1)] = m.group(2).lower()
unmapped = sorted(i for i in icons if i not in cmap)

# 3. subset fonts
os.makedirs('fonts', exist_ok=True)
solid = {i: cmap[i] for i in icons if i in cmap and i not in BRANDS}
brand = {i: cmap[i] for i in icons if i in cmap and i in BRANDS}
sizes = {}
for key, name, group in (('solid', 'fa-solid-900', solid), ('brands', 'fa-brands-400', brand)):
    src = os.path.join(os.environ.get('TEMP', '.'), name + '.woff2')
    open(src, 'wb').write(get(BASE + 'webfonts/' + name + '.woff2'))
    opts = subset.Options()
    opts.flavor = 'woff2'
    opts.layout_features = []
    opts.notdef_outline = False
    opts.name_IDs = []
    font = subset.load_font(src, opts)
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=[int(c, 16) for c in set(group.values())])
    sub.subset(font)
    out = 'fonts/fa-%s-sub.woff2' % key
    subset.save_font(font, out, opts)
    sizes[key] = os.path.getsize(out)

# 4. css
rules = ''.join('.fa-%s:before{content:"\\%s"}' % (n, c) for n, c in sorted({**solid, **brand}.items()))
block = ('\n/* icons subset */\n'
         '.fas,.fab{-moz-osx-font-smoothing:grayscale;-webkit-font-smoothing:antialiased;display:inline-block;font-style:normal;font-variant:normal;line-height:1;text-rendering:auto}\n'
         '.fas{font-family:"Font Awesome 6 Free";font-weight:900}\n'
         '.fab{font-family:"Font Awesome 6 Brands";font-weight:400}\n'
         '@font-face{font-family:"Font Awesome 6 Free";font-style:normal;font-weight:900;font-display:swap;src:url(../fonts/fa-solid-sub.woff2) format("woff2")}\n'
         '@font-face{font-family:"Font Awesome 6 Brands";font-style:normal;font-weight:400;font-display:swap;src:url(../fonts/fa-brands-sub.woff2) format("woff2")}\n'
         + rules + '\n')
css = rd('css/homepage.css')
css = re.sub(r'\n/\* icons subset \*/.*?(?=\n/\*|\Z)', '', css, flags=re.S)
wr('css/homepage.css', css.rstrip() + '\n' + block)

# 5. html
PRELOAD = '<link rel="preload" as="font" type="font/woff2" crossorigin href="fonts/fa-solid-sub.woff2">\n'
CSSLINK = '<link rel="stylesheet" href="css/homepage.css">'
removed_overlay = 0
for f in html_files:
    s = orig = rd(f)
    s = re.sub(r'<link[^>]*font-awesome[^>]*>\s*', '', s)
    s = re.sub(r'<link[^>]*rel="preconnect"[^>]*cdnjs\.cloudflare\.com[^>]*>\s*', '', s)
    s = re.sub(r'<style>@font-face\{font-family:"Font Awesome[^<]*</style>\s*', '', s)
    s = re.sub(r'<noscript>\s*</noscript>\s*', '', s)
    if PRELOAD not in s and CSSLINK in s:
        s = s.replace(CSSLINK, PRELOAD + CSSLINK, 1)
    if s != orig:
        wr(f, s)

# 6. vercel
vj = json.load(open('vercel.json', encoding='utf8'))
if not any(h.get('source') == '/fonts/(.*)' for h in vj['headers']):
    vj['headers'].append({'source': '/fonts/(.*)', 'headers': [{'key': 'Cache-Control', 'value': 'public, max-age=604800'}]})
    with open('vercel.json', 'w', encoding='utf8') as fh:
        json.dump(vj, fh, indent=2)
        fh.write('\n')

left = sum(1 for f in html_files if 'font-awesome' in rd(f))
print('icons used=%d unmapped=%s | solid=%dB brands=%dB | pages still referencing FA cdn=%d | index overlay removed=%d bytes' % (len(icons), unmapped, sizes['solid'], sizes['brands'], left, removed_overlay))
