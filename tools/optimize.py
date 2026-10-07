import re, glob, os, json, io, urllib.request
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
ORIGIN = 'https://www.letsrollgaragedoors.com/'
LOGO_T = 'img-63f59f98af3e-transparent.webp'
LOGO_O = 'img-63f59f98af3e.webp'
summary = {}


def rd(p):
    with open(p, encoding='utf8', newline='') as f:
        return f.read()


def wr(p, s):
    with open(p, 'w', encoding='utf8', newline='') as f:
        f.write(s)


# ---------------------------------------------------------------- contrast helpers
def rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(c):
    def f(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = c
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def ratio(a, b):
    la, lb = lum(rgb(a)), lum(rgb(b))
    if la < lb:
        la, lb = lb, la
    return (la + 0.05) / (lb + 0.05)


def hx(c):
    return '#%02x%02x%02x' % c


def darken_to(fg, bg, target=4.5):
    r, g, b = rgb(fg)
    for i in range(0, 300):
        f = 1 - i / 300
        c = (int(r * f), int(g * f), int(b * f))
        if ratio(hx(c), bg) >= target:
            return hx(c)
    return '#000000'


def blend(fg, a, bg):
    f, b = rgb(fg), rgb(bg)
    return hx(tuple(round(f[i] * a + b[i] * (1 - a)) for i in range(3)))


NEW_ORANGE = '#c24c07'
NEW_ORANGE_DARK = '#9c3e05'
OFFW = '#fafafa'
GOLD_TEXT = darken_to('#c9962c', OFFW)
ORANGE_TEXT_ON_OFFW = ratio(NEW_ORANGE, OFFW)
BADGE_SOON = darken_to('#e67e22', OFFW)
GREEN = darken_to('#27ae60', OFFW)

# ---------------------------------------------------------------- 1. images
img_before = sum(os.path.getsize(p) for p in glob.glob('images/*') if os.path.isfile(p))
changed_imgs = 0


def encode(im, path, ext, q):
    if ext == '.webp':
        im.save(path, 'WEBP', quality=q, method=6)
    elif ext in ('.jpg', '.jpeg'):
        im.convert('RGB').save(path, 'JPEG', quality=q, optimize=True, progressive=True)
    elif ext == '.png':
        im.save(path, 'PNG', optimize=True)


def reencode(path, maxw, force=False):
    global changed_imgs
    ext = os.path.splitext(path)[1].lower()
    if ext not in ('.webp', '.jpg', '.jpeg', '.png'):
        return
    orig = open(path, 'rb').read()
    im = Image.open(path)
    if getattr(im, 'n_frames', 1) > 1:
        return
    w, h = im.size
    if w > maxw:
        im = im.resize((maxw, round(h * maxw / w)), Image.LANCZOS)
    elif not force and len(orig) <= 200 * 1024:
        return
    q = 78 if ext == '.webp' else 80
    encode(im, path, ext, q)
    if len(open(path, 'rb').read()) >= len(orig) and w <= maxw:
        open(path, 'wb').write(orig)
        return
    changed_imgs += 1


for p in glob.glob('images/*'):
    name = os.path.basename(p)
    if not os.path.isfile(p):
        continue
    if name in (LOGO_T, LOGO_O):
        reencode(p, 520, force=True)
    elif os.path.getsize(p) > 200 * 1024:
        reencode(p, 1600 if re.match(r'job.*\.webp$', name) else 1200)

# cable drum must end under 150 KB
cd = 'images/img-cable-drum-real.webp'
if os.path.exists(cd) and os.path.getsize(cd) > 150 * 1024:
    im0 = Image.open(cd)
    done = False
    for w in (1000, 900, 800, 700):
        for q in (72, 66, 60, 54, 48, 42):
            im = im0.resize((w, round(im0.size[1] * w / im0.size[0])), Image.LANCZOS) if im0.size[0] > w else im0
            im.save(cd, 'WEBP', quality=q, method=6)
            if os.path.getsize(cd) < 150 * 1024:
                done = True
                break
        if done:
            break

# external unsplash images -> local webp (800px)
unsplash_map = {}
html_files = sorted(glob.glob('*.html'))
for f in html_files:
    for u in re.findall(r'https://images\.unsplash\.com/[^"\'\s)]+', rd(f)):
        unsplash_map.setdefault(u, None)
for u in list(unsplash_map):
    pid = re.search(r'photo-([\w-]+)', u).group(1)[:20]
    local = 'images/unsplash-%s.webp' % pid
    try:
        data = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read()
        im = Image.open(io.BytesIO(data)).convert('RGB')
        if im.size[0] > 800:
            im = im.resize((800, round(im.size[1] * 800 / im.size[0])), Image.LANCZOS)
        im.save(local, 'WEBP', quality=78, method=6)
        unsplash_map[u] = local
    except Exception as e:
        summary.setdefault('skipped', []).append('unsplash download failed: %s' % pid)

img_after = sum(os.path.getsize(p) for p in glob.glob('images/*') if os.path.isfile(p))

dim_cache = {}


def dims(src):
    s = src.split('?')[0].split('#')[0]
    if s.startswith(ORIGIN):
        s = s[len(ORIGIN):]
    s = s.lstrip('/')
    if not s or s.startswith('http') or not os.path.exists(s):
        return None
    if s not in dim_cache:
        try:
            dim_cache[s] = Image.open(s).size
        except Exception:
            dim_cache[s] = None
    return dim_cache[s]


# ---------------------------------------------------------------- 2. CSS
css = rd('css/homepage.css')
css_miss = []


def setp(sel, prop, val):
    global css
    m = re.search(r'(?m)^(%s)\{([^}]*)\}' % re.escape(sel), css)
    if not m:
        css_miss.append(sel)
        return
    body = m.group(2)
    if re.search(r'(^|;)\s*%s\s*:' % re.escape(prop), body):
        body = re.sub(r'((?:^|;)\s*%s\s*:)[^;]*' % re.escape(prop), lambda mm: mm.group(1) + val, body, count=1)
    else:
        body = body.rstrip().rstrip(';') + ';' + prop + ':' + val
    css = css[:m.start()] + m.group(1) + '{' + body + '}' + css[m.end():]


css = css.replace('--orange:#d9540a', '--orange:' + NEW_ORANGE)
css = css.replace('--orange-dark:#b5450a', '--orange-dark:' + NEW_ORANGE_DARK)
if '--gold-text' not in css:
    css = css.replace('--gold:#c9962c;', '--gold:#c9962c;\n  --gold-text:' + GOLD_TEXT + ';', 1)
css = css.replace('217,84,10', '194,76,7')
setp('img', 'height', 'auto')
setp('.sticky-cta', 'background', 'rgba(194,76,7,.97)')
setp('.sticky-call', 'background', 'rgba(194,76,7,.97)')
setp('.about-badge', 'color', 'var(--black)')
setp('.stat-lbl', 'color', '#fff')
setp('.cta-inner p', 'color', '#fff')
setp('.emergency-cta small', 'color', 'rgba(255,255,255,.75)')
setp('.author-loc', 'color', 'var(--gray)')
setp('.blog-meta', 'color', 'var(--gray)')
setp('.article-img-caption', 'color', 'var(--gray)')
setp('.stars', 'color', 'var(--gold-text)')
setp('.badge-soon', 'color', BADGE_SOON)
setp('.badge-wait', 'color', GREEN)
setp('.good', 'color', GREEN)
setp('.rvalue-table .best', 'color', GREEN)
setp('.article-footer .footer-bottom', 'color', 'rgba(255,255,255,.65)')
setp('.article-footer .footer-col img', 'width', 'auto')
css = re.sub(r'(?m)^(\.photo-placeholder span\{[^}]*?)color:#aaa', r'\1color:var(--gray)', css)
css = css.replace('.footer-col h4{', '.footer-col h4,.footer-col h3{', 1)
css = css.replace('.article-footer .footer-col h4{', '.article-footer .footer-col h4,.article-footer .footer-col h3{', 1)
css = css.replace('.about-item h4{', '.about-item h4,.about-item h3{', 1)
if '/* perf+a11y overrides */' not in css:
    css = css.rstrip() + '''

/* perf+a11y overrides */
.hero-photo-poster{background-image:url('../images/hero-poster.webp')}
@media(max-width:768px){.hero-video{display:none}}
.faq .section-tag,.process .section-tag,.sectors .section-tag,.page-header .section-tag,.page-hero .section-tag,.svc-hero .section-tag,.hero .section-tag,.cta-strip .section-tag{color:var(--orange-light)}
.faq .section-title span,.process .section-title span,.sectors .section-title span,.cta-strip h2 span,.page-hero h1 span,.emergency h2 span{color:var(--orange-light)}
.author-avatar,.job-card-header span{color:var(--orange-light)}
.footer-col h3{font-family:'Oswald',sans-serif}
.inline-cta h2{margin:0 0 8px;padding:0;border:0;font-size:clamp(17px,2.5vw,21px);font-weight:600}
'''
wr('css/homepage.css', css)

# ---------------------------------------------------------------- 3. HTML
FA_FONT = {
    'solid': ('Font Awesome 6 Free', 900, 'fa-solid-900'),
    'regular': ('Font Awesome 6 Free', 400, 'fa-regular-400'),
    'brands': ('Font Awesome 6 Brands', 400, 'fa-brands-400'),
}
CSSLINK = '<link rel="stylesheet" href="css/homepage.css">'
touched = 0
head_ok = 0
heads_seq = []
lazy_added = 0
dims_added = 0
no_dims_left = 0

for f in html_files:
    s = orig = rd(f)

    # ---- head: fonts / FA / preconnect / noscript
    gf = re.search(r'https://fonts\.googleapis\.com/css2\?[^"\'\s>]+', s)
    fa = re.search(r'https://cdnjs\.cloudflare\.com/ajax/libs/font-awesome/([\d.]+)/css/all\.min\.css', s)
    if gf and fa and CSSLINK in s:
        gurl, fver = gf.group(0), fa.group(1)
        furl = fa.group(0)
        hd, rest = s.split('</head>', 1)
        hd = re.sub(r'<link\b[^>]*(?:fonts\.googleapis\.com|fonts\.gstatic\.com|cdnjs\.cloudflare\.com)[^>]*>\s*', '', hd)
        hd = re.sub(r'<noscript>\s*</noscript>\s*', '', hd)
        hd = re.sub(r'<style>@font-face\{font-family:"Font Awesome[^<]*</style>\s*', '', hd)
        used = set()
        for m in re.finditer(r'class="([^"]*)"', rest):
            for tkn in m.group(1).split():
                if tkn in ('fas', 'fa-solid'):
                    used.add('solid')
                elif tkn in ('far', 'fa-regular'):
                    used.add('regular')
                elif tkn in ('fab', 'fa-brands'):
                    used.add('brands')
        ff = ''.join('@font-face{font-family:"%s";font-style:normal;font-weight:%d;font-display:swap;src:url(https://cdnjs.cloudflare.com/ajax/libs/font-awesome/%s/webfonts/%s.woff2) format("woff2")}' % (FA_FONT[k][0], FA_FONT[k][1], fver, FA_FONT[k][2]) for k in ('solid', 'regular', 'brands') if k in used)
        block = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
                 '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
                 '<link rel="preconnect" href="https://cdnjs.cloudflare.com" crossorigin>\n'
                 '<link rel="preload" as="style" href="%s" onload="this.onload=null;this.rel=\'stylesheet\'">\n'
                 '<link rel="preload" as="style" href="%s" onload="this.onload=null;this.rel=\'stylesheet\'">\n'
                 '<style>%s</style>\n'
                 '<noscript><link rel="stylesheet" href="%s"><link rel="stylesheet" href="%s"></noscript>\n') % (gurl, furl, ff, gurl, furl)
        hd = hd.replace(CSSLINK, block + CSSLINK, 1)
        s = hd + '</head>' + rest
        head_ok += 1
    else:
        summary.setdefault('skipped', []).append('head not rebuilt: ' + f)

    # ---- hero (index)
    if f == 'index.html':
        s = re.sub(r'<link rel="preload" as="image" href="images/img-d8d103469b7c\.webp"[^>]*>', '<link rel="preload" as="image" href="images/hero-poster.webp" fetchpriority="high">', s)
        s = s.replace('<div class="hero-photo"></div>', '<div class="hero-photo hero-photo-poster"></div>', 1)
        s = s.replace('<video class="hero-video" autoplay muted loop playsinline preload="auto" aria-hidden="true">', '<video class="hero-video" autoplay muted loop playsinline preload="none" poster="images/hero-poster.webp" aria-hidden="true">', 1)
        s = s.replace('<source src="videos/hero-bg.mp4" type="video/mp4">', '<source data-src="videos/hero-bg.mp4" type="video/mp4">', 1)
        if 'data-src="videos/hero-bg.mp4"' in s and 'hero-video-loader' not in s:
            loader = ('<script id="hero-video-loader">window.addEventListener("load",function(){var v=document.querySelector(".hero-video");if(!v)return;var c=navigator.connection;'
                      'if(!matchMedia("(min-width:769px)").matches||matchMedia("(prefers-reduced-motion:reduce)").matches||(c&&c.saveData))return;'
                      'var s=v.querySelector("source[data-src]");if(!s)return;s.src=s.getAttribute("data-src");v.load();var p=v.play();if(p&&p.catch)p.catch(function(){})});</script>')
            s = s.replace('</video>', '</video>\n  ' + loader, 1)
        s = s.replace('style="border-color:rgba(0,0,0,0.25);color:var(--navy)"', 'style="border-color:rgba(255,255,255,.7);color:#fff"')

    # ---- unsplash
    for u, local in unsplash_map.items():
        if local:
            s = s.replace(u, local)

    # ---- images
    first_img = [True]
    lcp_idx = None
    for key in ('class="article-wrap"', 'class="blog-card featured"'):
        k = s.find(key)
        if k != -1:
            m2 = re.compile(r'<img\b').search(s, k)
            if m2:
                lcp_idx = m2.start()
                break

    def fix_img(m):
        global lazy_added, dims_added, no_dims_left
        t = m.group(0)
        t = re.sub(r'(?<=["\'\w])\s+/\s+(?=[a-zA-Z-]+=)', ' ', t)
        sm = re.search(r'\ssrc="([^"]*)"', t)
        src = sm.group(1) if sm else ''
        is_first = first_img[0]
        exempt = is_first or 'fetchpriority="high"' in t or m.start() == lcp_idx
        first_img[0] = False
        add = []
        d = dims(src) if src else None
        if LOGO_T in src:
            t = re.sub(r'\s(width|height)="[^"]*"', '', t)
            add += ['width="194"', 'height="60"']
            dims_added += 1
        elif d:
            wm = re.search(r'\swidth="(\d+)"', t)
            hm = re.search(r'\sheight="(\d+)"', t)
            if not wm and not hm:
                add += ['width="%d"' % d[0], 'height="%d"' % d[1]]
                dims_added += 1
            elif wm and not hm:
                add.append('height="%d"' % round(int(wm.group(1)) * d[1] / d[0]))
                dims_added += 1
            elif hm and not wm:
                add.append('width="%d"' % round(int(hm.group(1)) * d[0] / d[1]))
                dims_added += 1
        elif src and not re.search(r'\swidth=', t):
            no_dims_left += 1
        if exempt:
            t = re.sub(r'\sloading="lazy"', '', t)
            if not is_first and m.start() == lcp_idx and 'fetchpriority' not in t:
                add.append('fetchpriority="high"')
        elif src:
            if 'loading=' not in t:
                add.append('loading="lazy"')
                lazy_added += 1
            if 'decoding=' not in t:
                add.append('decoding="async"')
        if add:
            em = re.search(r'\s*(/?)>$', t)
            t = t[:em.start()] + ' ' + ' '.join(add) + (' />' if em.group(1) else '>')
        return t

    s = re.sub(r'<img\b[^>]*>', fix_img, s)

    # ---- <main>
    if '<main' not in s:
        mc = s.find('class="m-cta"')
        ft = s.find('<footer')
        if mc != -1 and ft != -1:
            e = s.find('</div>', mc)
            if e != -1 and e < ft:
                e += len('</div>')
                s = s[:e] + '\n<main id="main">' + s[e:ft] + '</main>\n' + s[ft:]
            else:
                summary.setdefault('skipped', []).append('main not wrapped: ' + f)
        else:
            summary.setdefault('skipped', []).append('main not wrapped: ' + f)

    # ---- headings
    s = re.sub(r'<h4>(Quick Links|Services|Service Areas|Contact)</h4>', r'<h3>\1</h3>', s)
    s = re.sub(r'(<div class="about-item">(?:(?!</div>).)*?)<h4>(.*?)</h4>', r'\1<h3>\2</h3>', s)
    if f == 'smart-garage-door-openers-austin.html':
        s = s.replace('<h3>Need help right now?</h3>', '<h2>Need help right now?</h2>', 1)

    # ---- aria
    s = re.sub(r'<i\b(?![^>]*\brole=)([^>]*?)\saria-label="([^"]*)"', r'<i\1 role="img" aria-label="\2"', s)

    # ---- inline contrast
    s = s.replace('class="fas fa-star" style="color:var(--gold-light);opacity:1"', 'class="fas fa-star" style="color:#fff0b3;opacity:1"')
    s = s.replace('class="stat-num" style="color:var(--gold-light)"', 'class="stat-num" style="color:#fff0b3"')
    s = s.replace('.badge-stars { color: #c9962c;', '.badge-stars { color: var(--gold-text);')
    s = s.replace('217,84,10', '194,76,7')

    # ---- reflow
    s = s.replace('document.getElementById(id).scrollTop=0;', 'requestAnimationFrame(function(){document.getElementById(id).scrollTop=0});')

    if s != orig:
        wr(f, s)
        touched += 1

# heading report (visible page only)
skips = []
for f in html_files:
    body = rd(f).split('</head>', 1)[1]
    body = re.split(r'<div class="article-page"', body)[0]
    body = re.sub(r'<script.*?</script>', '', body, flags=re.S)
    prev = 0
    for m in re.finditer(r'<h([1-6])\b', body):
        l = int(m.group(1))
        if prev and l > prev + 1:
            skips.append('%s h%d>h%d' % (f, prev, l))
        prev = l

# ---------------------------------------------------------------- 4. vercel.json
vj = json.load(open('vercel.json', encoding='utf8')) if os.path.exists('vercel.json') else {}
hdrs = vj.setdefault('headers', [])


def setcache(src, val):
    for h in hdrs:
        if h.get('source') == src:
            h['headers'] = [{'key': 'Cache-Control', 'value': val}]
            return
    hdrs.append({'source': src, 'headers': [{'key': 'Cache-Control', 'value': val}]})


setcache('/images/(.*)', 'public, max-age=604800')
setcache('/videos/(.*)', 'public, max-age=604800')
setcache('/css/(.*)', 'public, max-age=86400')
with open('vercel.json', 'w', encoding='utf8') as fh:
    json.dump(vj, fh, indent=2)
    fh.write('\n')

# ---------------------------------------------------------------- 5. contrast verification
pairs = [
    ('#ffffff', NEW_ORANGE, 4.5, 'white on orange'),
    (NEW_ORANGE, '#ffffff', 4.5, 'orange on white'),
    (NEW_ORANGE, OFFW, 4.5, 'orange on offwhite'),
    ('#ffd7b8', '#132a52', 4.5, 'x'),
    ('#ff8a3d', '#132a52', 4.5, 'orange-light on navy'),
    ('#ff8a3d', '#1d1d1f', 4.5, 'orange-light on black'),
    ('#ffffff', NEW_ORANGE_DARK, 4.5, 'white on orange-dark'),
    ('#6e6e73', OFFW, 4.5, 'gray on offwhite'),
    (GOLD_TEXT, OFFW, 4.5, 'gold text'),
    (BADGE_SOON, OFFW, 4.5, 'badge soon'),
    (GREEN, OFFW, 4.5, 'green'),
    ('#1d1d1f', '#c9962c', 4.5, 'dark on gold badge'),
    (blend('#ffffff', .75, '#132a52'), '#132a52', 4.5, 'emergency small'),
    (blend('#ffffff', .65, '#132a52'), '#132a52', 4.5, 'article footer bottom'),
    ('#fff0b3', NEW_ORANGE, 3.0, 'stat 5 star (large)'),
    ('#ffffff', blend(NEW_ORANGE, .97, '#ffffff'), 4.5, 'sticky bar on white'),
    ('#ffffff', '#132a52', 4.5, 'white on navy'),
]
cfail = ['%s %.2f' % (p[3], ratio(p[0], p[1])) for p in pairs if p[3] != 'x' and ratio(p[0], p[1]) < p[2]]

vsz = os.path.getsize('videos/hero-bg.mp4')
print('FILES touched html=%d css=1 vercel=1 | head rebuilt=%d' % (touched, head_ok))
print('IMAGES reencoded=%d total %.1fMB -> %.1fMB | dims added=%d | lazy added=%d | no-dims left=%d' % (changed_imgs, img_before / 1048576, img_after / 1048576, dims_added, lazy_added, no_dims_left))
print('video now %.2fMB | cable-drum %dKB' % (vsz / 1048576, os.path.getsize(cd) // 1024 if os.path.exists(cd) else -1))
print('CSS selectors not found:', css_miss)
print('heading skips left:', skips)
print('contrast fails:', cfail)
print('computed: gold-text=%s badge-soon=%s green=%s' % (GOLD_TEXT, BADGE_SOON, GREEN))
print('skipped:', summary.get('skipped', []))
