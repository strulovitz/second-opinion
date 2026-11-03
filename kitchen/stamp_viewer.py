#!/usr/bin/env python3
"""Cache-busting for the viewer: rewrite every relative import and the app.js
script tag with ?v=<stamp>, so Cloudflare and browsers fetch new code after a
deploy. Idempotent. Run after any change under site/viewer/."""
import re, subprocess, sys
from pathlib import Path

VIEWER = Path(__file__).resolve().parents[1] / "site" / "viewer"
stamp = sys.argv[1] if len(sys.argv) > 1 else subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=VIEWER).stdout.strip() or "dev"
stamp = stamp + "-" + subprocess.run(["date", "+%Y%m%d%H%M"], capture_output=True, text=True).stdout.strip()
n = 0
for f in list(VIEWER.glob("*.js")) + [VIEWER / "index.html"]:
    s = f.read_text()
    t = re.sub(r"""((?:from|import)\s*['"]\./[\w-]+\.js)(?:\?v=[\w.-]+)?(['"])""", rf"\1?v={stamp}\2", s)
    t = re.sub(r"""(src=['"]app\.js)(?:\?v=[\w.-]+)?(['"])""", rf"\1?v={stamp}\2", t)
    t = re.sub(r"""(import\(\s*['"]\./[\w-]+\.js)(?:\?v=[\w.-]+)?(['"])""", rf"\1?v={stamp}\2", t)
    if t != s:
        f.write_text(t); n += 1
print(f"stamped {n} files with v={stamp}")
