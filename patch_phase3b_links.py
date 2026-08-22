#!/usr/bin/env python3
"""Phase 3b link patcher — run this ONCE from your repo folder (the folder
with index.html), after copying the four new pages into it.

What it does:
  1. Finds every page with an "Explore Our Other Services" section and
     rewrites the links so every service/guide page links to all the others.
  2. Adds the four new pages to sitemap.xml (skips any already there) and
     bumps <lastmod> on pages whose links changed.
  3. Appends the four new pages to llms.txt (skips any already there).

It edits files in place — review the diff in GitHub Desktop before committing.
Run:  python3 patch_phase3b_links.py
"""
import glob, os, re, sys, datetime

BASE = "https://www.letsrollgaragedoors.com/"
TODAY = datetime.date.today().isoformat()

NEW_PAGES = [
    "garage-door-repair-south-austin.html",
    "garage-door-tune-up-austin.html",
    "garage-door-sensor-alignment-austin.html",
    "garage-door-manual-release-austin.html",
]

# Preferred short labels + display order. Any page found on disk that isn't
# listed here still gets included — its label is derived from its <h1>.
KNOWN = [
    ("garage-door-repair-austin.html",          "Garage Door Repair"),
    ("garage-door-spring-repair-austin.html",   "Spring Repair"),
    ("garage-door-cable-repair-austin.html",    "Cable Repair"),
    ("garage-door-opener-repair-austin.html",   "Opener Repair"),
    ("garage-door-installation-austin.html",    "New Installation"),
    ("garage-door-repair-south-austin.html",    "South Austin Service"),
    ("garage-door-tune-up-austin.html",         "Tune-Up &amp; Maintenance"),
    ("garage-door-sensor-alignment-austin.html","Sensor Alignment Guide"),
    ("garage-door-manual-release-austin.html",  "Manual Release Guide"),
]
KNOWN_FILES = [f for f, _ in KNOWN]
KNOWN_LABELS = dict(KNOWN)

LLMS_ENTRIES = {
    "garage-door-repair-south-austin.html":
        "- [Garage Door Repair South Austin](https://www.letsrollgaragedoors.com/garage-door-repair-south-austin.html): Same-day garage door repair across South Austin neighborhoods and zip codes 78704, 78745, 78748, 78749.",
    "garage-door-tune-up-austin.html":
        "- [Garage Door Tune-Up & Maintenance](https://www.letsrollgaragedoors.com/garage-door-tune-up-austin.html): Preventive maintenance in Austin, TX — lubrication, spring balance testing, hardware tightening, and safety inspection.",
    "garage-door-sensor-alignment-austin.html":
        "- [How to Align Garage Door Sensors](https://www.letsrollgaragedoors.com/garage-door-sensor-alignment-austin.html): DIY guide to cleaning, aligning, and testing garage door safety sensors when the door won't close.",
    "garage-door-manual-release-austin.html":
        "- [How to Open a Garage Door Manually](https://www.letsrollgaragedoors.com/garage-door-manual-release-austin.html): Safety guide to using the red emergency release cord during a power outage or opener failure.",
}

RELATED_RE = re.compile(r'(<div class="svc-related-grid">)(.*?)(</div>)', re.S)

def derive_label(html, fname):
    m = re.search(r"<h1>(.*?)</h1>", html, re.S)
    if not m:
        return fname
    label = re.sub(r"<[^>]+>", "", m.group(1)).strip()
    label = re.sub(r"\s+in\s+(South\s+)?Austin(,?\s*TX)?\s*$", "", label, flags=re.I)
    return label

def main():
    if not os.path.exists("index.html"):
        sys.exit("Run this from your website repo folder (index.html not found here).")

    missing = [f for f in NEW_PAGES if not os.path.exists(f)]
    if missing:
        sys.exit("Copy the new page(s) into this folder first, missing: " + ", ".join(missing))

    # ── discover every page with a related-services section ──────────
    roster, pages = {}, {}
    for f in sorted(glob.glob("*.html")):
        with open(f, encoding="utf-8") as fh:
            html = fh.read()
        if '<section class="svc-related">' not in html:
            continue
        pages[f] = html
        roster[f] = KNOWN_LABELS.get(f) or derive_label(html, f)

    # display order: KNOWN order first, then any extras alphabetically
    ordered = [f for f in KNOWN_FILES if f in roster] + \
              sorted(f for f in roster if f not in KNOWN_FILES)

    print(f"Found {len(ordered)} pages with an 'Explore Our Other Services' section:")
    for f in ordered:
        print(f"  {f}  →  {roster[f]}")

    # ── 1. rewrite related links (everything except self) ────────────
    changed = []
    for f in ordered:
        links = "\n".join(
            f'<a href="{o}" class="svc-related-link">{roster[o]} →</a>'
            for o in ordered if o != f)
        new_html, n = RELATED_RE.subn(
            lambda m: m.group(1) + "\n    " + links + "\n  " + m.group(3),
            pages[f], count=1)
        if n == 0:
            print(f"  WARNING: no svc-related-grid found in {f}, skipped")
            continue
        if new_html != pages[f]:
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(new_html)
            changed.append(f)
    print(f"\nUpdated related links on {len(changed)} page(s).")

    # ── 2. sitemap.xml ───────────────────────────────────────────────
    if os.path.exists("sitemap.xml"):
        with open("sitemap.xml", encoding="utf-8") as fh:
            sm = fh.read()
        # copy the shape of an existing entry so formatting matches
        tmpl_m = re.search(r"(<url>.*?</url>)", sm, re.S)
        added = 0
        for f in NEW_PAGES:
            loc = BASE + f
            if loc in sm:
                continue
            if tmpl_m:
                entry = tmpl_m.group(1)
                entry = re.sub(r"<loc>.*?</loc>", f"<loc>{loc}</loc>", entry, flags=re.S)
                entry = re.sub(r"<lastmod>.*?</lastmod>", f"<lastmod>{TODAY}</lastmod>", entry, flags=re.S)
            else:
                entry = f"<url>\n    <loc>{loc}</loc>\n    <lastmod>{TODAY}</lastmod>\n  </url>"
            sm = sm.replace("</urlset>", "  " + entry + "\n</urlset>")
            added += 1
        # bump lastmod on the existing pages we just edited
        bumped = 0
        for f in changed:
            loc = BASE + f
            pat = re.compile(
                r"(<loc>" + re.escape(loc) + r"</loc>.*?<lastmod>).*?(</lastmod>)", re.S)
            sm, n = pat.subn(r"\g<1>" + TODAY + r"\g<2>", sm)
            bumped += n
        with open("sitemap.xml", "w", encoding="utf-8") as fh:
            fh.write(sm)
        print(f"sitemap.xml: added {added} new URL(s), refreshed lastmod on {bumped} existing page(s).")
    else:
        print("WARNING: sitemap.xml not found here — new pages NOT added to the sitemap.")

    # ── 3. llms.txt ──────────────────────────────────────────────────
    if os.path.exists("llms.txt"):
        with open("llms.txt", encoding="utf-8") as fh:
            llms = fh.read()
        added = [e for f, e in LLMS_ENTRIES.items() if f not in llms]
        if added:
            llms = llms.rstrip("\n") + "\n" + "\n".join(added) + "\n"
            with open("llms.txt", "w", encoding="utf-8") as fh:
                fh.write(llms)
        print(f"llms.txt: added {len(added)} new entr{'y' if len(added)==1 else 'ies'}.")
    else:
        print("WARNING: llms.txt not found here — skipped.")

    print("\nDone. Open GitHub Desktop, review the diff, commit, and push.")

if __name__ == "__main__":
    main()
