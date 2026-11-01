#!/usr/bin/env python3
"""Rebuild every redesigned page from the original-site commit, then apply the SEO fixes.
Run from the repo root:  python tools/rebuild_site.py
"""
import subprocess, sys, os
here = os.path.dirname(os.path.abspath(__file__))
for step in ('apply_redesign.py', 'apply_redesign_more.py', 'apply_redesign_home.py', 'apply_seo_fixes.py'):
    r = subprocess.run([sys.executable, os.path.join(here, step)], capture_output=True, text=True, encoding='utf-8')
    print(step, '->', (r.stdout.strip().splitlines() or ['(no output)'])[-1])
    if r.returncode:
        print(r.stderr[-800:]); sys.exit(1)
