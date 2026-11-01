#!/usr/bin/env python3
"""Convert index.html (homepage) to Design B.

Keeps <head>/JSON-LD, the quote form (ids, names, hidden fields, submit script), the referral-code script and
all section copy; rebuilds the layout with the work-order components. The H1 is the one deliberate copy change.
Run from the repo root:  python tools/apply_redesign_home.py
"""
import re, html
from apply_redesign import edit_copy, git_head, load_chrome, FONTS, text

H1_LINES = [('l1', 'Garage Door Trouble'), ('l2', 'in Austin?'), ('l3', "Let's Roll.")]
HERO_IMG = 'install-easton-park.webp'
ICON = re.compile(r'<i [^>]*></i>\s*')


def g(pat, s, f=re.S):
    m = re.search(pat, s, f)
    assert m, pat
    return m


def sec(src, cls):
    return g(r'<section class="%s"[^>]*>.*?</section>' % cls, src).group(0)


def tag_h2(s, h2cls=''):
    tag = text(g(r'<div class="section-tag[^>]*>(.*?)</div>', s).group(1))
    h2 = g(r'<h2[^>]*>(.*?)</h2>', s).group(1).strip()
    return tag, re.sub(r'\s*<br>\s*', ' ', h2)


def clean_links(s):
    s = re.sub(r'(<a [^>]*?)\s*style="[^"]*"', lambda m: m.group(1) + (' class="lnk"' if 'class=' not in m.group(1) else ''), s)
    return ICON.sub('', s)


LOOP_JS = '''<script>
(function(){var t=document.getElementById('quotes-track'),b=document.getElementById('q-toggle');if(!t)return;
if(matchMedia('(prefers-reduced-motion:reduce)').matches){if(b)b.hidden=true;return}
[].slice.call(t.children).forEach(function(c){var k=c.cloneNode(true);k.setAttribute('aria-hidden','true');t.appendChild(k)});
var half=t.scrollWidth/2;t.style.setProperty('--qdur',Math.max(40,Math.round(half/55))+'s');
t.parentNode.classList.add('running');t.classList.add('run');
if(b)b.addEventListener('click',function(){var p=t.classList.toggle('paused');b.setAttribute('aria-pressed',p);b.textContent=p?'Play reviews':'Pause reviews'});
})();
</script>
'''


def build(src):
    top, footer, script, _ = load_chrome()
    m0 = re.search(r'<link rel="preconnect" href="https://fonts\.googleapis\.com">.*?homepage\.css[^>]*>', src, re.S)
    assert m0 and 'ld+json' not in m0.group(0)
    he = src.index('</head>')
    head = src[:m0.start()] + FONTS + src[m0.end():he]
    head = re.sub(r'<link rel="preload"[^>]*hero-poster[^>]*>\s*', '', head)
    body = src[he:]
    a, b = body.index('<main id="main">'), body.index('</main>')
    old = body[a:b + 7]
    tail = body[b + 7:]

    # ---- hero
    hero = sec(old, 'hero')
    eyebrow = text(g(r'<div class="hero-eyebrow">(.*?)</div>', hero).group(1))
    sub = g(r'<p class="hero-sub">(.*?)</p>', hero).group(1)
    phone = g(r'<a href="(tel:[^"]+)">([^<]+)</a>', g(r'<div class="hero-phone-row">.*?</div>', hero).group(0))
    phone_lbl = text(g(r'<div class="hero-phone-row">.*?<span>(.*?)</span>', hero).group(1))
    est = g(r'<a href="#quote" class="btn btn-orange">(.*?)</a>', hero).group(1)
    svc = g(r'<a href="#services" class="btn btn-outline-white">(.*?)</a>', hero).group(1)
    card = g(r'<div class="hero-card" id="quote">.*?</form>\s*</div>', hero).group(0)
    card = ICON.sub('', card)
    spans = '\n        '.join(f'<span class="{c}">{t}</span>' for c, t in H1_LINES)
    trust = re.findall(r'<span class="trust-item-text">(.*?)</span>', old, re.S)
    out = [f'''<section class="hero home" id="home">
  <figure class="hero-photo"><picture><source media="(max-width:768px)" srcset="/images/hero-poster-m.webp"><img src="/images/hero-poster.webp" alt="A newly installed garage door and open garage at a home in Austin, TX" width="1280" height="720" fetchpriority="high"></picture>
    <video class="hero-video" muted loop playsinline preload="none" aria-hidden="true" tabindex="-1"><source data-src="/videos/hero-bg.mp4" type="video/mp4"></video></figure>
  <script id="hero-video-loader">window.addEventListener("load",function(){{var v=document.querySelector(".hero-video");if(!v)return;var c=navigator.connection;if(matchMedia("(prefers-reduced-motion:reduce)").matches||(c&&(c.saveData||/(^|-)2g$/.test(c.effectiveType||""))))return;var s=v.querySelector("source[data-src]");if(!s)return;s.src=s.getAttribute("data-src");v.load();var p=v.play();if(p&&p.then)p.then(function(){{v.classList.add("on")}}).catch(function(){{}})}});</script>
  <div class="wrap hero-grid">
    <div>
      <p class="mono tag" style="background:var(--accent);color:var(--navy)">{eyebrow}</p>
      <h1>
        {spans}
      </h1>
    </div>
    <div class="hero-foot">
      <p>{sub}</p>
      <div class="call">
        <a href="#quote" class="btn">{ICON.sub('', est)}</a>
        <a href="#services" class="lnk">{ICON.sub('', svc)}</a>
      </div>
      <p class="callrow"><span>{phone_lbl}</span> <a href="{phone.group(1)}" class="lnk">{phone.group(2)}</a></p>
    </div>
  </div>
  {card}
</section>
<div class="wrap">
  <ul class="proof">
''' + ''.join(f'    <li>{text(t)}</li>\n' for t in trust) + '''  </ul>
</div>''']

    # ---- services
    s = sec(old, 'services')
    tag, h2 = tag_h2(s)
    sub = g(r'<p class="section-sub[^>]*>(.*?)</p>', s).group(1)
    rows = []
    for card in re.findall(r'<article class="service-card">.*?</article>', s, re.S):
        img = g(r'<div class="sc-img">(.*?)</div>', card).group(1)
        h3 = g(r'<h3>(.*?)</h3>', card).group(1)
        p = g(r'<p>(.*?)</p>\s*<a href="#quote"', card).group(1)
        ln = g(r'<a href="#quote" class="service-link">(.*?)</a>', card).group(1)
        rows.append(f'    <article class="srv rv"><div class="srv-img">{img}</div><div class="srv-body"><h3>{clean_links(h3)}</h3><p>{clean_links(p)}</p><a href="#quote" class="service-link">{ICON.sub("", ln)} &rarr;</a></div></article>')
    out.append(f'''<section class="sec" id="services">
  <div class="wrap">
    <span class="tag mono rv">{tag}</span>
    <h2 class="rv">{h2}</h2>
    <p class="lede rv" style="margin-top:1rem">{sub}</p>
    <div class="srv-list">
''' + '\n'.join(rows) + '''
    </div>
  </div>
</section>''')

    # ---- about
    s = sec(old, 'about')
    tag, h2 = tag_h2(s)
    img = g(r'<img [^>]*>', s).group(0)
    num, lbl = (text(x) for x in g(r'<span class="num">(.*?)</span><span class="lbl">(.*?)</span>', s).groups())
    sub = g(r'<p class="section-sub">(.*?)</p>', s).group(1)
    items = ''.join(f'<li><h3>{h}</h3><p>{clean_links(p)}</p></li>' for h, p in re.findall(r'<h3>(.*?)</h3><p>(.*?)</p>', s, re.S))
    cta = g(r'<a href="#quote" class="btn btn-orange"[^>]*>(.*?)</a>', s).group(1)
    out.append(f'''<section class="sec kraft" id="about">
  <div class="wrap about-grid">
    <figure class="about-photo rv">{img}<figcaption class="about-badge"><b>{num}</b><span>{lbl}</span></figcaption></figure>
    <div class="rv">
      <span class="tag mono">{tag}</span>
      <h2>{h2}</h2>
      <p class="lede" style="margin-top:1rem">{sub}</p>
      <ul class="about-list">{items}</ul>
      <a href="#quote" class="btn" style="margin-top:28px">{ICON.sub('', cta)}</a>
    </div>
  </div>
</section>''')

    # ---- emergency
    s = sec(old, 'emergency')
    h2 = re.sub(r'\s*<br>\s*', ' ', g(r'<h2>(.*?)</h2>', s).group(1))
    p = g(r'<div>\s*<h2>.*?</h2>\s*<p>(.*?)</p>', s).group(1)
    call = g(r'<a href="(tel:[^"]+)"[^>]*>(.*?)</a>', s)
    smalls = re.findall(r'<small>(.*?)</small>', s, re.S)
    out.append(f'''<section class="sec navy emerg">
  <div class="wrap emerg-in">
    <div class="rv"><h2>{h2}</h2><p class="lede" style="margin-top:1rem">{p}</p></div>
    <div class="emerg-cta rv">
      <a href="{call.group(1)}" class="btn">{ICON.sub('', call.group(2))}</a>
''' + ''.join(f'      <small>{clean_links(x)}</small>\n' for x in smalls) + '''    </div>
  </div>
</section>''')

    # ---- stats
    s = sec(old, 'stats')
    st = re.findall(r'<div class="stat-num"[^>]*>(.*?)</div><div class="stat-lbl">(.*?)</div>', s, re.S)
    out.append('<section class="stats-band">\n  <div class="wrap stats-row">\n' + ''.join(
        f'    <div class="stat rv"><b>{n}</b><span class="mono">{l}</span></div>\n' for n, l in st) + '  </div>\n</section>')

    # ---- testimonials
    s = sec(old, 'testimonials')
    tag, h2 = tag_h2(s)
    badge = g(r'<a href="https://share\.google[^"]*"[^>]*class="google-review-badge".*?</a>', s).group(0)
    badge = ICON.sub('', badge)
    cards = re.findall(r'<article class="testimonial-card">.*?</article>', s, re.S)
    qs = []
    for qi, c in enumerate(cards):
        q = g(r'<blockquote>(.*?)</blockquote>', c).group(1)
        av = g(r'<div class="author-avatar">(.*?)</div>', c).group(1)
        nm = g(r'<div class="author-name">(.*?)</div>', c).group(1)
        lc = g(r'<div class="author-loc">(.*?)</div>', c).group(1)
        qs.append(f'<article class="q-card q-v{qi % 3}"><div class="stars" aria-label="5 stars">★★★★★</div><blockquote>{q}</blockquote><div class="q-by"><span class="q-av">{av}</span><span><b>{nm}</b><br>{lc}</span></div></article>')
    out.append(f'''<section class="sec kraft" id="reviews">
  <div class="wrap">
    <span class="tag mono rv">{tag}</span>
    <h2 class="rv">{h2}</h2>
    <p class="rv" style="margin-top:1.2rem">{badge}</p>
  </div>
  <div class="quotes" tabindex="0" role="region" aria-label="Customer reviews">
    <div class="quotes-track" id="quotes-track">
''' + '\n'.join(qs) + '''
    </div>
  </div>
  <div class="wrap"><button type="button" class="q-toggle mono" id="q-toggle" aria-pressed="false">Pause reviews</button></div>
</section>''')

    # ---- deals
    s = sec(old, 'deals-home')
    tag, h2 = tag_h2(s)
    sub = g(r'<p class="deals-home-sub">(.*?)</p>', s).group(1)
    dg = g(r'<div class="deals-grid">.*?</div>\s*(?=<div class="deals-home-actions">)', s).group(0)
    act = s
    allbtn = g(r'<a href="coupons\.html" class="btn btn-orange">(.*?)</a>', act).group(1)
    callbar = g(r'<div class="deals-callbar">(.*?)</div>', act).group(1)
    fine = g(r'<p class="deal-fine">(.*?)</p>', act).group(1)
    out.append(f'''<section class="sec" id="deals">
  <div class="wrap">
    <span class="tag mono rv">{tag}</span>
    <h2 class="rv">{h2}</h2>
    <p class="lede rv" style="margin-top:1rem">{sub}</p>
    <div class="rv">{ICON.sub('', dg)}</div>
    <div class="deals-actions rv">
      <a href="coupons.html" class="btn">{allbtn}</a>
      <p class="deals-callbar">{clean_links(callbar)}</p>
      <p class="deal-fine">{fine}</p>
    </div>
  </div>
</section>''')

    # ---- faq
    s = sec(old, 'faq')
    tag, h2 = tag_h2(s)
    sub = g(r'<p class="section-sub white"[^>]*>(.*?)</p>', s).group(1)
    call = g(r'<a href="(tel:[^"]+)" class="btn btn-orange"[^>]*>(.*?)</a>', s)
    det = []
    for i, (cls, q, a) in enumerate(re.findall(r'<div class="faq-item( open)?"><div class="faq-question"[^>]*>(.*?)\s*<i class="fas fa-chevron-down"></i></div><div class="faq-answer">(.*?)</div></div>', s, re.S)):
        det.append(f'<details class="faq-d"{" open" if cls else ""}><summary>{q}</summary><div class="faq-a">{clean_links(a)}</div></details>')
    out.append(f'''<section class="sec kraft" id="faq">
  <div class="wrap faq">
    <div class="hd rv"><span class="tag mono">{tag}</span><h2 style="font-size:clamp(1.8rem,3.2vw,3.2rem)">{h2}</h2><p style="margin-top:1rem">{sub}</p><a href="{call.group(1)}" class="btn" style="margin-top:22px">{ICON.sub('', call.group(2))}</a></div>
    <div class="rv">
      ''' + '\n      '.join(det) + '''
    </div>
  </div>
</section>''')

    # ---- areas
    s = sec(old, 'areas')
    tag, h2 = tag_h2(s)
    sub = g(r'<p class="areas-sub">(.*?)</p>', s).group(1)
    links = ''.join(f'<a href="{h}">{text(n)}</a>' for h, n in re.findall(r'<a href="([^"]+)" class="area-pill">(.*?)</a>', s, re.S))
    out.append(f'''<section class="sec" id="areas">
  <div class="wrap">
    <span class="tag mono rv">{tag}</span>
    <h2 class="rv">{h2}</h2>
    <p class="lede rv" style="margin-top:1rem">{sub}</p>
    <nav class="cities rv" aria-label="Service areas">{links}</nav>
  </div>
</section>''')

    # ---- map
    s = sec(old, 'map-section')
    h2 = g(r'<h2>(.*?)</h2>', s).group(1)
    p = g(r'<p>(.*?)</p>', s).group(1)
    iframe = g(r'<div class="map-embed">.*?</div>', s).group(0)
    out.append(f'''<section class="sec kraft" id="find-us">
  <div class="wrap">
    <span class="tag mono rv">Find us</span>
    <h2 class="rv">{h2}</h2>
    <p class="lede rv" style="margin-top:1rem">{clean_links(p)}</p>
    <div class="rv">{iframe}</div>
  </div>
</section>''')

    # ---- final cta
    s = sec(old, 'cta')
    h2 = g(r'<h2>(.*?)</h2>', s).group(1)
    p = g(r'<p>(.*?)</p>', s).group(1)
    call = g(r'<a href="(tel:[^"]+)"[^>]*>(.*?)</a>', s)
    est = g(r'<a href="#quote"[^>]*>(.*?)</a>', s).group(1)
    out.append(f'''<section class="cta">
  <div class="wrap cta-in" style="padding-top:18px">
    <div><h2>{h2}</h2><p>{p}</p></div>
    <div>
      <a href="{call.group(1)}" class="tel"><svg class="ico" style="width:.6em;height:.6em"><use href="#i-phone"/></svg>{ICON.sub('', call.group(2))}</a>
      <a href="#quote" class="oq lnk">{ICON.sub('', est)}</a>
    </div>
  </div>
</section>''')

    main = '<main id="main">\n' + '\n\n'.join(out) + '\n</main>'
    main = re.sub(r'(href|src)="(?!https?:|tel:|mailto:|#|/|data:)([^"]+)"', r'\1="/\2"', main)

    # ---- tail: footer, scripts (keep form submit + referral + analytics, replace the menu / faq-accordion code)
    tail = re.sub(r'<footer>.*?</footer>', lambda _: footer, tail, count=1, flags=re.S)
    def fix_script(m):
        js = m.group(1)
        i, j = js.index('// Mobile menu'), js.index('// Form')
        return '<script>\n' + js[:i] + js[j:] + '</script>\n' + script
    tail = re.sub(r'<script>(\s*// Mobile menu.*?)</script>', fix_script, tail, count=1, flags=re.S)
    tail = tail.replace('src="js/widgets.js"', 'src="/js/widgets.js?v=20261101"')
    tail = tail.replace('</body>', LOOP_JS + '</body>', 1)
    return head + '</head>\n<body>\n' + top + main + tail


if __name__ == '__main__':
    open('index.html', 'w', encoding='utf-8', newline='\n').write(edit_copy(build(git_head('index.html'))))
    print('index.html converted')
