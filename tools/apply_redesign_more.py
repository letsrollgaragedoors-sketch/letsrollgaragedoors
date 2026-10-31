#!/usr/bin/env python3
"""Convert the guide articles and the text pages (about, privacy, warranty) to Design B.

Same approach as apply_redesign.py: read from git HEAD, keep <head> and JSON-LD untouched, swap the
stylesheet, nav, footer and scripts, build a plain (photo-less) hero from the page's own title block,
and turn the FAQ accordions into <details>. Run from the repo root:  python tools/apply_redesign_more.py
"""
import re, html
from apply_redesign import git_head, load_chrome, FONTS, text, build_hero

ARTICLES = ['garage-door-austin-heat-humidity', 'garage-door-insulated-doors-austin',
            'garage-door-maintenance-tips-austin', 'garage-door-repair-cost-austin',
            'garage-door-spring-warning-signs-austin', 'garage-door-tune-up-maintenance-austin',
            'garage-door-wont-open-close-austin', 'smart-garage-door-openers-austin',
            'what-breaks-garage-doors-austin-by-season', 'when-to-replace-garage-door-austin']
LEGAL = ['about', 'privacy-policy', 'warranty-terms']
GALLERY, BLOG = 'gallery', 'blog'


def shell(path, build_main, chrome):
    top, footer, script, _ = chrome
    src = git_head(path)
    m = re.search(r'<link rel="preconnect" href="https://fonts\.googleapis\.com">.*?homepage\.css[^>]*>', src, re.S)
    assert m and 'ld+json' not in m.group(0), path
    head_end = src.index('</head>')
    head = src[:m.start()] + FONTS + src[m.end():head_end]
    body = src[head_end:]
    a, b = body.index('<main id="main">'), body.index('</main>')
    main = build_main(body[a:b + 7])
    main = re.sub(r'(href|src)="(?!https?:|tel:|mailto:|#|/|data:)([^"]+)"', r'\1="/\2"', main)
    tail = body[b + 7:]
    tail = re.sub(r'<footer>.*?</footer>', lambda _: footer, tail, count=1, flags=re.S)
    tail = re.sub(r'<script>\s*// Mobile menu.*?</script>', lambda _: script, tail, count=1, flags=re.S)
    tail = tail.replace('src="js/widgets.js"', 'src="/js/widgets.js"')
    open(path, 'w', encoding='utf-8', newline='\n').write(head + '</head>\n<body>\n' + top + main + tail)


def strips(h, budget=20):
    lines, cur = [], ''
    for w in h.split():
        if cur and len(cur) + 1 + len(w) > budget:
            lines.append(cur); cur = w
        else:
            cur = (cur + ' ' + w).strip()
    lines.append(cur)
    cls = ['l1'] + ['l2' if i % 2 else 'l3' for i in range(1, len(lines))]
    return '\n        '.join(f'<span class="{c}">{t}</span>' for c, t in zip(cls, lines))


def plain_hero(tag, h1, back='', ticket='', foot=''):
    return f'''<section class="hero plain">
  <div class="wrap hero-grid">
    <div>
      {back}
      <p class="mono tag" style="background:var(--accent);color:var(--navy)">{tag}</p>
      <h1>
        {strips(h1)}
      </h1>
    </div>
    {foot}
  </div>
  {ticket}
</section>
'''


def article_main(main):
    crumb = re.search(r'<div class="breadcrumb">.*?</div>', main, re.S)
    crumb = crumb.group(0) if crumb else ''
    back = re.search(r'<a [^>]*class="back-link"[^>]*>.*?</a>', main, re.S)
    tag = re.search(r'<span class="article-tag">(.*?)</span>', main, re.S)
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', main, re.S)
    meta = re.search(r'<div class="article-meta">(.*?)</div>', main, re.S)
    assert back and tag and h1 and meta, 'article header parts missing'
    items = ''.join(f'<li>{re.sub(r"<i [^>]*></i>", "", s).strip()}</li>'
                    for s in re.findall(r'<span>(.*?)</span>', meta.group(1), re.S))
    ticket = ('<aside class="ticket" aria-label="Article details">\n    <div class="hd mono"><span>Field notes</span><span>Austin, TX</span></div>\n'
              f'    <ul class="tmeta">{items}</ul>\n    <div class="perf"><span>Let\'s Roll Garage Doors</span></div>\n  </aside>')
    back_html = re.sub(r'<i [^>]*></i>\s*', '', back.group(0))
    hero = plain_hero(tag.group(1), h1.group(1).strip(), back_html, ticket)
    for piece in (crumb, back.group(0), tag.group(0), h1.group(0), meta.group(0)):
        if piece:
            main = main.replace(piece, '', 1)
    main = re.sub(r'<div class="article-header">\s*</div>', '', main)
    main = main.replace('<main id="main">', '<main id="main">\n' + crumb + '\n' + hero, 1)
    main = re.sub(r'<div class="faq-item"><div class="faq-q"[^>]*>(.*?)\s*<i class="fas fa-chevron-down"></i></div>'
                  r'<div class="faq-a">(.*?)</div></div>',
                  r'<details class="faq-d"><summary>\1</summary><div class="faq-a">\2</div></details>', main, flags=re.S)
    return main


def legal_main(main):
    ph = re.search(r'<div class="page-header">(.*?)</div>\s*(?=<div class="legal-wrap">)', main, re.S)
    tag = text(re.search(r'<div class="section-tag[^>]*>(.*?)</div>', ph.group(1), re.S).group(1))
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', ph.group(1), re.S).group(1).strip()
    paras = ''.join(re.findall(r'<p[^>]*>.*?</p>', ph.group(1), re.S))
    foot = f'<div class="hero-foot">{paras}</div>' if paras else ''
    return main.replace(ph.group(0), plain_hero(tag, h1, foot=foot), 1)


def blog_main(main):
    hd = re.search(r'<div class="blog-header">.*?(?=<div class="blog-grid">)', main, re.S)
    tag = text(re.search(r'<div class="section-tag[^>]*>(.*?)</div>', hd.group(0), re.S).group(1))
    h1 = text(re.search(r'<h1[^>]*>(.*?)</h1>', hd.group(0), re.S).group(1))
    sub = re.search(r'<p class="section-sub"[^>]*>(.*?)</p>', hd.group(0), re.S).group(1)
    back = re.search(r'<a [^>]*class="view-all"[^>]*>.*?</a>', hd.group(0), re.S).group(0)
    back = re.sub(r'<i [^>]*></i>\s*', '', back).replace('class="view-all"', 'class="back-link"')
    foot = f'<div class="hero-foot"><p>{sub}</p></div>'
    main = main.replace(hd.group(0), '', 1)
    main = re.sub(r'<section class="blog" id="blog"[^>]*>', '<section class="blog-sec" id="blog">', main, 1)
    return main.replace('<!-- BLOG PAGE CONTENT -->', plain_hero(tag, h1, back, '', foot), 1)


def gallery_main(main):
    ph = re.search(r'<section class="page-hero">.*?</section>', main, re.S)
    tag = text(re.search(r'<div class="section-tag[^>]*>(.*?)</div>', ph.group(0), re.S).group(1))
    h1 = text(re.search(r'<h1[^>]*>(.*?)</h1>', ph.group(0), re.S).group(1))
    p = re.search(r'<p>(.*?)</p>', ph.group(0), re.S).group(1)
    return main.replace(ph.group(0), plain_hero(tag, h1, foot=f'<div class="hero-foot"><p>{p}</p></div>'), 1)


def same_day_main(main):
    """same-day page is built from the old homepage template: map its blocks onto the svc-* building blocks"""
    g = lambda pat, s, f=re.S: re.search(pat, s, f)
    hero = g(r'<section class="hero">.*?</section>', main).group(0)
    h1 = re.sub(r'<[^>]+>', '', g(r'<h1>(.*?)</h1>', hero).group(1))
    syn = ('<section class="svc-hero"><div class="section-tag">' + text(g(r'<div class="hero-eyebrow">(.*?)</div>', hero).group(1)) + '</div>'
           f'<h1>{h1}</h1><p>{g(r"""<p class="hero-sub">(.*?)</p>""", hero).group(1)}</p>'
           '<p>Trusted by homeowners across <a href="/#areas">Austin &amp; surrounding areas</a></p>'
           + ''.join(f'<span class="svc-badge">{text(b)}</span>' for b in re.findall(r'<span class="trust-item-text">(.*?)</span>', main, re.S))
           + '</section>')
    out = [build_hero(syn, 'same-day-garage-door-service-austin.html', 0)]

    def block(cls):
        return g(r'<section class="%s"[^>]*>.*?</section>' % cls, main).group(0)

    def head(s):
        tag = text(g(r'<div class="section-tag[^>]*>(.*?)</div>', s).group(1))
        h2 = g(r'<h2[^>]*>(.*?)</h2>', s).group(1).strip()
        sub = g(r'<p class="section-sub[^>]*>(.*?)</p>', s)
        return f'<p class="mono kick">{tag}</p>\n  <h2>{h2}</h2>' + (f'\n  <p>{sub.group(1)}</p>' if sub else '')

    pairs = lambda s: re.findall(r'<h3>(.*?)</h3>\s*<p>(.*?)</p>', s, re.S)
    items = lambda s: ''.join(f'<div class="svc-item"><h3>{a}</h3><p>{b}</p></div>' for a, b in pairs(s))
    s = block('services'); out.append(f'<section class="svc-section">\n  {head(s)}\n  <div class="svc-grid">{items(s)}</div>\n</section>')
    s = block('fixlist')
    lnk = g(r'<a href="([^"]+)" class="btn btn-orange">(.*?)</a>', s)
    lis = ''.join(f'<li>{x}</li>' for x in re.findall(r'<div class="fix-item">.*?<p>(.*?)</p>', s, re.S))
    out.append(f'<section class="svc-section">\n  {head(s)}\n  <p><a href="{lnk.group(1)}" class="lnk">{lnk.group(2)}</a></p>\n  <ul>{lis}</ul>\n</section>')
    s = block('process')
    steps = ''.join(f'<div class="svc-step"><div class="svc-step-num"></div><div class="svc-step-body"><h3>{a}</h3><p>{b}</p></div></div>' for a, b in pairs(s))
    out.append(f'<section class="svc-section">\n  {head(s)}\n  <div class="svc-steps">{steps}</div>\n</section>')
    s = block('compare'); out.append(f'<section class="svc-section">\n  {head(s)}\n  <div class="svc-grid">{items(s)}</div>\n</section>')
    s = block('faq')
    qa = re.findall(r'<div class="faq-question"[^>]*><span>(.*?)</span>.*?<div class="faq-answer">(.*?)</div>\s*</div>', s, re.S)
    det = ''.join(f'<details class="faq-d"><summary>{q}</summary><div class="faq-a">{a}</div></details>' for q, a in qa)
    out.append(f'<section class="svc-section" id="faq">\n  {head(s)}\n  <div class="svc-faq">{det}</div>\n</section>')
    s = block('related')
    links = ''.join(f'<a href="{h}" class="svc-related-link">{text(x)}</a>' for h, x in re.findall(r'<a href="([^"]+)">(.*?)</a>', s, re.S))
    out.append(f'<section class="svc-related">\n  <p class="mono kick">{text(g(r"""<div class="section-tag[^>]*>(.*?)</div>""", s).group(1))}</p>\n  <h2>{g(r"<h2[^>]*>(.*?)</h2>", s).group(1)}</h2>\n  <div class="svc-related-grid">{links}</div>\n</section>')
    s = block('cta')
    qlink = g(r'<a href="([^"]+)" class="btn btn-outline-white">(.*?)</a>', s)
    out.append(f'<section class="svc-cta-band">\n  <h2>{g(r"<h2>(.*?)</h2>", s).group(1)}</h2>\n  <p>{g(r"<p>(.*?)</p>", s).group(1)}</p>\n'
               f'  <a href="tel:+15129474451" class="nav-cta">Call (512) 947-4451</a>\n  <p><a href="{qlink.group(1)}">{qlink.group(2)}</a></p>\n</section>')
    return '<main id="main">\n' + '\n'.join(out) + '\n</main>'


if __name__ == '__main__':
    chrome = load_chrome()
    for a in ARTICLES:
        shell(a + '.html', article_main, chrome)
    for l in LEGAL:
        shell(l + '.html', legal_main, chrome)
    shell(BLOG + '.html', blog_main, chrome)
    shell(GALLERY + '.html', gallery_main, chrome)
    shell('same-day-garage-door-service-austin.html', same_day_main, chrome)
    print(len(ARTICLES) + len(LEGAL) + 3, 'pages converted')
