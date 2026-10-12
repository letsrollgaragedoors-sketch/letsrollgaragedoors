"""One-off: deepen garage-door-spring-repair-austin.html (SEO content, images, schema, internal links).
Run from repo root: python tools/improve_spring.py"""
import os, re, json, glob
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
PAGE = 'garage-door-spring-repair-austin.html'
URL = 'https://www.letsrollgaragedoors.com/' + PAGE
TODAY = '2026-10-12'
UP = r'C:\Users\dudue\.claude\uploads\454d960f-b36a-4f41-a680-0e885457db54'


def rd(p):
    return open(p, encoding='utf8', newline='').read()


def wr(p, s):
    open(p, 'w', encoding='utf8', newline='').write(s)


def words(html):
    t = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', html, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    return len(re.findall(r"[A-Za-z0-9$'’&-]+", t))


# ---------- images
def webp(src, dst, maxw=1200, q=78):
    im = Image.open(src).convert('RGB')
    if im.size[0] > maxw:
        im = im.resize((maxw, round(im.size[1] * maxw / im.size[0])), Image.LANCZOS)
    im.save(dst, 'WEBP', quality=q, method=6)
    return Image.open(dst).size


sz = {}
sz['both'] = webp('images/garage-door-both-springs-broken-austin-tx.jpg', 'images/garage-door-both-springs-broken-austin-tx.webp')
sz['one'] = webp('images/garage-door-one-broken-spring-austin-tx.jpg', 'images/garage-door-one-broken-spring-austin-tx.webp')
sz['before'] = webp(UP + r'\6cfdfd80-image.jpg', 'images/spring-replacement-easton-park-before.webp')
sz['after'] = webp(UP + r'\228dfecf-image.jpg', 'images/spring-replacement-easton-park-after.webp')

s = rd(PAGE)
nl = '\r\n' if '\r\n' in s else '\n'
before_words, before_size = words(s), len(s.encode('utf8'))
assert 'torsion-vs-extension' not in s, 'already applied'

# ---------- 1. title / meta
TITLE = 'Garage Door Spring Repair Austin TX | Same-Day Service'
DESC = 'Garage door spring repair in Austin, TX from $249. Same-day torsion & extension spring replacement, 24/7 emergency. Call (512) 947-4451.'
OGD = 'Garage door spring repair in Austin, TX from $249. Same-day torsion and extension spring replacement. Call (512) 947-4451.'
assert len(TITLE) <= 60 and len(DESC) <= 155, (len(TITLE), len(DESC))
s = re.sub(r'<title>.*?</title>', '<title>%s</title>' % TITLE, s, count=1)
s = re.sub(r'(name="description" content=")[^"]*"', lambda m: m.group(1) + DESC.replace('&', '&amp;') + '"', s, count=1)
s = re.sub(r'(property="og:title" content=")[^"]*"', lambda m: m.group(1) + TITLE + '"', s, count=1)
s = re.sub(r'(property="og:description" content=")[^"]*"', lambda m: m.group(1) + OGD + '"', s, count=1)
s = re.sub(r'(name="twitter:title" content=")[^"]*"', lambda m: m.group(1) + TITLE + '"', s, count=1)
s = re.sub(r'(name="twitter:description" content=")[^"]*"', lambda m: m.group(1) + OGD + '"', s, count=1)

# ---------- 2. new sections
LNK = 'style="color:var(--orange);font-weight:600"'
CITIES = [
    ('south-austin', 'South Austin'), ('north-austin', 'North Austin'), ('east-austin', 'East Austin'),
    ('west-austin', 'West Austin'), ('round-rock', 'Round Rock'), ('cedar-park', 'Cedar Park'),
    ('pflugerville', 'Pflugerville'), ('georgetown', 'Georgetown'), ('leander', 'Leander'),
    ('lakeway', 'Lakeway'), ('kyle', 'Kyle'), ('buda', 'Buda'), ('hutto', 'Hutto'), ('manor', 'Manor'),
    ('bastrop', 'Bastrop'),
]
city_links = []
for slug, name in CITIES:
    if os.path.exists('garage-door-repair-%s.html' % slug):
        city_links.append('<a href="garage-door-repair-%s.html" %s>garage door spring repair in %s</a>' % (slug, LNK, name))
assert len(city_links) >= 10
cities_html = ', '.join(city_links[:-1]) + ', and ' + city_links[-1]

NEW = '''<section class="svc-section" id="torsion-vs-extension">
  <h2>Torsion vs Extension Springs: Which Does Your Door Have?</h2>
  <p>Look at the top of your garage door. If a long, coiled spring sits on a metal bar above the door, it is a <strong>torsion spring</strong>. If you see springs running along the side tracks, with a cable and pulley at the end, those are <strong>extension springs</strong>.</p>
  <p>Torsion springs are on most newer Austin homes. They twist to lift the door, wear evenly and are rated for 10,000 cycles as standard. Extension springs stretch and contract, are common on older and lighter doors, and need safety cables so a snapped spring can't whip across the garage.</p>
  <p>Torsion systems usually cost a little more to replace, but they are smoother and last longer. We replace both types, and we'll tell you which one you have before any work starts.</p>
</section>

<section class="svc-section" style="background:#fafafa;border-radius:14px" id="broken-spring-signs">
  <h2>Signs Your Garage Door Spring Is Broken</h2>
  <ul>
    <li>A loud bang from the garage, like a gunshot, when the spring snapped</li>
    <li>The opener hums but the door won't lift, or only rises a few inches</li>
    <li>The door feels extremely heavy when you try to lift it by hand</li>
    <li>A visible gap in the coil above the door</li>
    <li>The door slams down, or drops unevenly on one side</li>
  </ul>
  <p>Not sure yet? Read our guide to the <a href="garage-door-spring-warning-signs-austin.html" %(LNK)s>broken spring warning signs</a>. If your door shows any of the signs above, stop using it and call us.</p>
</section>

<section class="svc-section" id="spring-cost-factors">
  <h2>What Affects Spring Replacement Cost in Austin</h2>
  <p>Our pricing starts at $249 for a single torsion spring and $399 for a two-spring replacement, and your final price is confirmed before we start. Four things move it up or down:</p>
  <ul>
    <li><strong>Door size and weight.</strong> A heavy insulated double door needs stronger, longer springs than a light single-car door.</li>
    <li><strong>Torsion or extension.</strong> The two types use different parts and take different amounts of labor.</li>
    <li><strong>Cycle rating.</strong> Standard springs are rated for about 10,000 cycles. Upgrading to high-cycle springs rated for 25,000 to 50,000 cycles costs more up front and lasts years longer on a door that is used a lot.</li>
    <li><strong>One spring or both.</strong> If one spring breaks, the second is usually close behind. Replacing both together is cheaper than two visits.</li>
    <li><strong>Emergency or after-hours calls.</strong> Service outside normal hours can cost more.</li>
  </ul>
  <p>For the full picture, see our <a href="garage-door-repair-cost-austin.html" %(LNK)s>garage door repair cost guide</a>.</p>
</section>

<section class="svc-section" style="background:#fafafa;border-radius:14px" id="spring-job-proof">
  <h2>Recent Spring Replacement in Easton Park, Austin</h2>
  <p>Here is a spring replacement we completed in the Easton Park neighborhood of Austin. The old springs are on the left and the new springs are on the right.</p>
  <!-- TODO: Dudu to confirm job month/year and what was replaced (both springs or one) -->
  <div class="svc-grid">
    <figure style="margin:0"><img src="images/spring-replacement-easton-park-before.webp" alt="Old worn torsion springs above a garage door before replacement in Easton Park, Austin TX" width="%(bw)d" height="%(bh)d" loading="lazy" decoding="async" style="width:100%%;height:auto;border-radius:12px"><figcaption style="font-size:14px;margin-top:8px">Before: old springs, Easton Park, Austin</figcaption></figure>
    <figure style="margin:0"><img src="images/spring-replacement-easton-park-after.webp" alt="New torsion springs installed above a garage door in Easton Park, Austin TX" width="%(aw)d" height="%(ah)d" loading="lazy" decoding="async" style="width:100%%;height:auto;border-radius:12px"><figcaption style="font-size:14px;margin-top:8px">After: new springs installed, Easton Park, Austin</figcaption></figure>
  </div>
  <!-- TODO: Dudu to confirm what these two shots show before keeping captions below -->
  <div class="svc-grid" style="margin-top:20px">
    <figure style="margin:0"><img src="images/garage-door-both-springs-broken-austin-tx.webp" alt="Garage door interior with torsion spring system above the door, Austin TX" width="%(gw)d" height="%(gh)d" loading="lazy" decoding="async" style="width:100%%;height:auto;border-radius:12px"><figcaption style="font-size:14px;margin-top:8px">Garage door spring system, Austin TX</figcaption></figure>
    <figure style="margin:0"><img src="images/garage-door-one-broken-spring-austin-tx.webp" alt="Garage door with torsion springs on the bar above the door, Austin TX" width="%(ow)d" height="%(oh)d" loading="lazy" decoding="async" style="width:100%%;height:auto;border-radius:12px"><figcaption style="font-size:14px;margin-top:8px">Torsion springs above the door, Austin TX</figcaption></figure>
  </div>
</section>

<section class="svc-section" id="spring-warranty">
  <h2>Our Spring Replacement Warranty</h2>
  <p>Every spring replacement is covered by our workmanship guarantee, which runs 45 to 60 days from the date of service unless your invoice says otherwise. If something we did isn't right, call us and we will come back and fix it.</p>
  <p>The springs themselves also carry the manufacturer's own parts warranty. Terms vary by brand and part. The full terms, including what is and isn't covered, are on our <a href="warranty-terms.html" %(LNK)s>warranty terms</a> page.</p>
</section>

<section class="svc-section" style="background:#fafafa;border-radius:14px" id="spring-repair-areas">
  <h2>Spring Repair Across Austin</h2>
  <p>We repair and replace garage door springs across Austin and the surrounding area. Our technicians are dispatched from our Austin location at 720 Airport Blvd #1280, and our emergency line is open 24/7. Nearby we offer %(cities)s. Call (512) 947-4451 to check same-day availability for your address.</p>
</section>

'''
NEW = NEW.replace('%(LNK)s', LNK)
NEW = NEW % dict(bw=sz['before'][0], bh=sz['before'][1], aw=sz['after'][0], ah=sz['after'][1],
                 gw=sz['both'][0], gh=sz['both'][1], ow=sz['one'][0], oh=sz['one'][1], cities=cities_html)
NEW = NEW.replace('\n', nl)

m = re.search(r'<section class="svc-section">\s*<h2>Frequently Asked Questions</h2>', s)
assert m
s = s[:m.start()] + NEW + s[m.start():]

# ---------- 2f. FAQ items (html + schema)
FAQS = [
    ('Why did my garage door spring break?',
     "Springs wear out. Each open and close is one cycle, and a standard spring is rated for about 10,000 cycles, which is roughly 7 to 10 years of normal use. Heavy daily use, rust, and a door that is out of balance all shorten that. Austin heat also dries out lubricant, so a yearly tune-up helps."),
    ('Torsion or extension spring: how do I tell?',
     "Look above the door. A coiled spring on a bar mounted over the door opening is a torsion spring. Springs that run along the horizontal side tracks, with cables and pulleys at the ends, are extension springs. If you aren't sure, send us a photo or call (512) 947-4451 and we'll tell you."),
    ('Do you replace springs after hours in Austin?',
     "Yes. Our emergency line is answered 24/7, and we replace broken springs after hours, on weekends and on holidays when we can get to you safely. Call (512) 947-4451. After-hours service can cost more than a regular daytime visit."),
]
faq_html = ''.join('<div class="svc-faq-item"><h3>%s</h3><p>%s</p></div>%s' % (q, a, nl) for q, a in FAQS)
fm = re.search(r'(<div class="svc-faq-item">.*?</div>)(\s*</div>\s*</section>\s*<section class="svc-cta-band">)', s, re.S)
assert fm
last = fm.end(1)
s = s[:last] + nl + faq_html.rstrip() + s[last:]

# JSON-LD FAQPage
def fix_ld(m):
    try:
        d = json.loads(m.group(2))
    except Exception:
        return m.group(0)
    changed = False
    for node in d.get('@graph', [d]):
        if node.get('@type') == 'FAQPage':
            names = {q['name'] for q in node['mainEntity']}
            for q, a in FAQS:
                if q not in names:
                    node['mainEntity'].append({'@type': 'Question', 'name': q,
                                               'acceptedAnswer': {'@type': 'Answer', 'text': a}})
                    changed = True
    if not changed:
        return m.group(0)
    return m.group(1) + nl + json.dumps(d, indent=2, ensure_ascii=False).replace('\n', nl) + nl + m.group(3)

s = re.sub(r'(<script type="application/ld\+json">)(.*?)(</script>)', fix_ld, s, flags=re.S)
wr(PAGE, s)

# ---------- 4. internal links in
ANCHOR = 'garage door spring repair in Austin'
LINK = '<a href="%s" %s>%s</a>' % (PAGE, LNK, ANCHOR)
targets = {
    'index.html': ("<p>Broken torsion or extension springs are a safety risk. Our techs replace them safely using quality parts backed by <a href=\"warranty-terms.html\"", None),
    'garage-door-repair-austin.html': (None, 'Need a spring fixed? See our %s page.' % LINK),
    'garage-door-cable-repair-austin.html': (None, 'If a spring broke at the same time, we handle %s too.' % LINK),
    'garage-door-repair-cost-austin.html': (None, 'For a closer look at one common repair, see our %s page.' % LINK),
    'emergency-garage-door-repair-austin.html': (None, 'A snapped spring is one of the most common emergencies, and we cover %s around the clock.' % LINK),
    'garage-door-spring-warning-signs-austin.html': (None, 'When you are ready to fix it, see our %s page.' % LINK),
}
changed_pages = []
for f, (marker, sentence) in targets.items():
    t = rd(f)
    if re.search(r'<a [^>]*href="(?:https://www\.letsrollgaragedoors\.com/)?%s"[^>]*>(?:garage door spring repair in Austin|broken spring repair)</a>' % re.escape(PAGE), t):
        continue
    if f == 'index.html':
        i = t.find('<p>Broken torsion or extension springs are a safety risk.')
        assert i > 0
        j = t.index('</p>', i)
        t = t[:j] + ' Learn more about our %s.' % LINK + t[j:]
    else:
        # first plain body paragraph after the hero that mentions springs-related context: first <p> of first svc-section/article paragraph
        hero_end = t.find('</section>', t.find('svc-hero')) if 'svc-hero' in t else t.find('<div class="article-wrap">')
        k = t.find('<p>', hero_end)
        assert k > 0, f
        j = t.index('</p>', k)
        t = t[:j] + ' ' + sentence + t[j:]
    wr(f, t)
    changed_pages.append(f)

# ---------- 6. sitemap
sm = rd('sitemap.xml')
sm2 = re.sub(r'(<loc>%s</loc>\s*<lastmod>)[^<]*(</lastmod>)' % re.escape(URL), r'\g<1>%s\g<2>' % TODAY, sm)
wr('sitemap.xml', sm2)

# ---------- 5/7. validate
t = rd(PAGE)
bad = 0
for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
    try:
        json.loads(m.group(1))
    except Exception:
        bad += 1
h1 = len(re.findall(r'<h1[ >]', t))
heads = [int(x) for x in re.findall(r'<h([1-6])[ >]', t)]
body = t[t.index('<main'):t.index('</main>')]
bh = [int(x) for x in re.findall(r'<h([1-6])[ >]', body)]
skips = [(a, b) for a, b in zip(bh, bh[1:]) if b - a > 1]
print('title len', len(TITLE), '| desc len', len(DESC))
print('section open/close:', len(re.findall(r'<section[ >]', body)), len(re.findall(r'</section>', body)))
print('h1 count:', h1, '| heading skips:', skips, '| jsonld errors:', bad)
print('words %d -> %d (+%d)' % (before_words, words(t), words(t) - before_words))
print('bytes %d -> %d' % (before_size, len(t.encode('utf8'))))
print('links added to:', changed_pages)
print('img sizes KB:', {k: os.path.getsize(p) // 1024 for k, p in [
    ('both', 'images/garage-door-both-springs-broken-austin-tx.webp'),
    ('one', 'images/garage-door-one-broken-spring-austin-tx.webp'),
    ('before', 'images/spring-replacement-easton-park-before.webp'),
    ('after', 'images/spring-replacement-easton-park-after.webp')]})
