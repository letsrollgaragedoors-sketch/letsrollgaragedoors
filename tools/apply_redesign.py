#!/usr/bin/env python3
"""Convert the svc-* service pages to the Design B ("work order") layout.

Reads each page from the original-site commit (safe to re-run), keeps the <head> and all JSON-LD untouched,
swaps the stylesheet, nav, hero, FAQ markup and footer, and leaves the page body copy as it is.
Chrome (nav / footer / scripts) is taken from redesign/garage-door-installation-austin-workorder.html.
Run from the repo root:  python tools/apply_redesign.py
"""
import re, subprocess, glob, os, html

# copy edits applied on top of the original text (keep in one place so re-running the tools keeps them)
CONTENT_EDITS = [('$469', '$499')]  # two-spring replacement now starts at $499


def edit_copy(s):
    for a, b in CONTENT_EDITS:
        s = s.replace(a, b)
    return s


ORIGINAL = 'a491293'  # last commit of the pre-redesign site; converters always start from it
DRAFT = 'tools/design-b-source.html'
PHONE = '+15129474451'
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Archivo:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap">\n'
         '<link rel="stylesheet" href="/css/workorder.css?v=20261103">')

HERO_BY_KEY = [  # filename keyword -> hero photo
    ('spring', 'garage-door-both-springs-broken-austin-tx.jpg'),
    ('cable', 'garage-door-cable-off-drum-austin-tx.jpg'),
    ('roller', 'worn-garage-door-roller-austin-tx.jpg'),
    ('off-track', 'garage-door-off-track-austin-tx.jpg'),
    ('opener', 'img-liftmaster-opener-real.webp'),
    ('liftmaster', 'img-liftmaster-opener-real.webp'),
    ('tune-up', 'img-tuneup-lubricant.webp'),
    ('installation', 'install-mueller.webp'),
    ('wont-open', 'garage-door-damaged-panels-austin-tx.jpg'),
]
ROTATE = ['install-paige.webp', 'install-easton-park.webp', 'install-cedar-creek.webp', 'job1-after-1.webp',
          'job2-after-1.webp', 'job3-after-1.webp', 'job4-after-1.webp', 'job5-after-1.webp', 'job7-after-1.webp',
          'spring-replacement-easton-park-after.webp', 'install-mueller.webp']


def git_head(path):
    return subprocess.run(['git', 'show', ORIGINAL + ':' + path], capture_output=True, text=True,
                          encoding='utf-8', check=True).stdout


def root(s):
    """draft uses ../ paths; production pages live at the site root"""
    s = s.replace('../index.html#', '/#').replace('../index.html', '/')
    return s.replace('../', '/')


def load_chrome():
    d = open(DRAFT, encoding='utf-8').read()
    top = d[d.index('<body>') + 6:d.index('<main id="main">')]
    footer = d[d.index('<footer>'):d.index('</footer>') + 9]
    script = re.search(r"<script>\ndocument\.documentElement\.classList\.add\('js'\);.*?</script>", d, re.S).group(0)
    main = d[d.index('<main id="main">'):d.index('</main>') + 7]
    return root(top), root(footer), script, root(main)


def text(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s)).strip()


def split_h1(h):
    words = h.split()
    tail = []
    for i in range(len(words) - 1, 0, -1):
        if words[i] == 'in':
            words, tail = words[:i], words[i:]
            break
    n = len(words)
    if n >= 4:
        l1, rest = words[:2], words[2:]
        k = (len(rest) + 1) // 2 if len(rest) >= 3 else len(rest)
        lines = [l1, rest[:k], rest[k:]]
    elif n == 3:
        lines = [words[:2], words[2:]]
    elif n == 2:
        lines = [words[:1], words[1:]]
    else:
        lines = [words]
    lines = [' '.join(x) for x in lines if x]
    if tail:
        lines.append(' '.join(tail))
    cls = ['l1', 'l2', 'l3', 'l4']
    if len(lines) == 2:
        cls = ['l2', 'l4']
    elif len(lines) == 3:
        cls = ['l1', 'l2', 'l4'] if tail else ['l1', 'l2', 'l3']
    return '\n        '.join(f'<span class="{c}">{t}</span>' for c, t in zip(cls, lines))


def build_hero(sec, fname, idx):
    tag = text(re.search(r'<div class="section-tag[^>]*>(.*?)</div>', sec, re.S).group(1))
    h1 = re.search(r'<h1>(.*?)</h1>', sec, re.S).group(1).strip()
    paras = ''.join(f'<p>{p}</p>' for p in re.findall(r'<p>(.*?)</p>', sec, re.S))
    badges = [text(b) for b in re.findall(r'<span class="svc-badge">(.*?)</span>', sec, re.S)]
    deal = ''
    bx = re.search(r'<div style="display:inline-block;background:rgba\(255,255,255,\.1\)[^"]*">(.*?)</div>\s*(?=<div class="svc-hero-ctas">|<div class="svc-badges">|</section>)', sec, re.S)
    if bx:
        parts = re.findall(r'<div[^>]*>(.*?)</div>', bx.group(1), re.S)
        parts = [re.sub(r'\s*style="[^"]*"', '', re.sub(r'<i [^>]*></i>\s*', '', x)).strip() for x in parts]
        label, value, note = (parts + ['', '', ''])[:3]
        deal = f'<div class="hero-deal"><span class="mono">{label}</span><b>{value}</b><small>{note}</small></div>'
    ctas = re.findall(r'<a href="([^"]+)" class="nav-cta"[^>]*>(.*?)</a>', sec, re.S)
    alt_href, alt_text = (ctas[1][0], text(ctas[1][1])) if len(ctas) > 1 else ('/#quote', 'Get a Free Quote')
    img = next((v for k, v in HERO_BY_KEY if k in fname), None) or ROTATE[idx % len(ROTATE)]
    alt = html.escape(f"Garage door work by Let's Roll Garage Doors: {text(h1)}", quote=True)
    perf = ' · '.join(badges[:2]) if badges else 'Background-checked &amp; insured'
    # city / area pages get a "back" button in the top-left, like the old "Back to Services" link
    is_loc = re.fullmatch(r'garage-door-repair-(?!austin\.html|cost-austin\.html).+\.html', fname) is not None
    back = '<a href="/#areas" class="back-link back-btn">Back to Service Areas</a>\n      ' if is_loc else ''
    proof = ''
    if badges:
        proof = '<div class="wrap">\n  <ul class="proof">\n' + ''.join(f'    <li>{b}</li>\n' for b in badges) + '  </ul>\n</div>\n'
    return f'''<section class="hero">
  <figure class="hero-photo">
    <img src="/images/{img}" alt="{alt}" width="800" height="600" fetchpriority="high">
  </figure>
  <aside class="ticket" aria-label="Job summary">
    <div class="hd mono"><span>Work order</span><span>Austin, TX</span></div>
    <dl>
      <dt>Hours</dt><dd>24/7 emergency</dd>
      <dt>Call</dt><dd>(512) 947-4451</dd>
    </dl>
    <div class="perf"><span>{perf}</span></div>
  </aside>
  <div class="wrap hero-grid">
    <div>
      {back}<p class="mono tag" style="background:var(--accent);color:var(--navy)">{tag}</p>
      <h1>
        {split_h1(h1)}
      </h1>
    </div>
    <div class="hero-foot">
      {paras}
      {deal}
      <div class="call">
        <a href="tel:{PHONE}" class="btn"><svg class="ico"><use href="#i-phone"/></svg>Call (512) 947-4451</a>
        <a href="{alt_href}" class="lnk">{alt_text}</a>
      </div>
    </div>
  </div>
</section>
{proof}'''


def convert(path, idx, chrome):
    top, footer, script, draft_main = chrome
    src = git_head(path)
    # head: swap fonts/css only; JSON-LD and meta stay byte-identical
    m = re.search(r'<link rel="preconnect" href="https://fonts\.googleapis\.com">.*?homepage\.css[^>]*>', src, re.S)
    assert m and 'ld+json' not in m.group(0), path
    head_end = src.index('</head>')
    head = src[:m.start()] + FONTS + src[m.end():head_end]
    # body
    body = src[head_end:]
    if path == 'garage-door-installation-austin.html':
        main = draft_main
    else:
        a, b = body.index('<main id="main">'), body.index('</main>')
        main = body[a:b + 7]
        main = re.sub(r'<div class="back-btn-wrap">.*?</div>\s*', '', main, flags=re.S)
        hs = re.search(r'<section class="svc-hero">.*?</section>', main, re.S)
        main = main[:hs.start()] + build_hero(hs.group(0), path, idx) + main[hs.end():]
        main = re.sub(r'<div class="svc-faq-item">\s*<h3>(.*?)</h3>\s*(.*?)\s*</div>',
                      r'<details><summary><h3>\1</h3></summary>\2</details>', main, flags=re.S)
        main = re.sub(r'(<a [^>]*?)\s*style="color:var\(--orange\);font-weight:600"',
                      lambda m: (m.group(1) if 'class=' in m.group(1) else m.group(1) + ' class="lnk"'), main)
        main = main.replace(' style="background:#fafafa;border-radius:14px"', '')
        main = re.sub(r'(class="svc-area-pill") style="[^"]*"', r'\1', main)
        main = re.sub(r'(class="svc-areas-grid") style="[^"]*"', r'\1', main)
        main = re.sub(r'(href|src)="(?!https?:|tel:|mailto:|#|/|data:)([^"]+)"', r'\1="/\2"', main)
    tail = body[body.index('</main>') + 7:]
    tail = re.sub(r'<footer>.*?</footer>', lambda _: footer, tail, count=1, flags=re.S)
    tail = re.sub(r'<script>\s*// Mobile menu.*?</script>', lambda _: script, tail, count=1, flags=re.S)
    tail = tail.replace('src="js/widgets.js"', 'src="/js/widgets.js?v=20261101"')
    new = head + '</head>\n<body>\n' + top + main + tail
    open(path, 'w', encoding='utf-8', newline='\n').write(edit_copy(new))


if __name__ == '__main__':
    chrome = load_chrome()
    pages = sorted(p for p in glob.glob('*.html') if 'class="svc-hero"' in git_head(p))
    for i, p in enumerate(pages):
        convert(p, i, chrome)
    print(len(pages), 'pages converted')
