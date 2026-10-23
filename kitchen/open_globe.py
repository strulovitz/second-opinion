#!/usr/bin/env python3
"""Serve only site/ on loopback and open the actual globe in the desktop browser."""

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-open", action="store_true")
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("port must be 1024..65535")
    url = f"http://127.0.0.1:{args.port}/viewer/"
    marker = b'data-app="second-opinion-viewer"'

    def ready():
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                if marker not in response.read(10000):
                    raise SystemExit(f"Port {args.port} serves a different application; choose --port")
            return True
        except urllib.error.HTTPError:
            raise SystemExit(f"Port {args.port} serves a different application; choose --port")
        except (urllib.error.URLError, TimeoutError):
            return False

    if not ready():
        logs = ROOT / "kitchen/logs"
        logs.mkdir(exist_ok=True)
        with (logs / "globe-server.log").open("ab") as output:
            process = subprocess.Popen([sys.executable, "-m", "http.server", str(args.port), "--bind", "127.0.0.1", "--directory", str(ROOT / "site")],
                                       stdout=output, stderr=output, stdin=subprocess.DEVNULL, start_new_session=True)
        for _ in range(50):
            if process.poll() is not None:
                raise SystemExit("Server failed; see kitchen/logs/globe-server.log")
            if ready():
                break
            time.sleep(0.1)
        else:
            process.terminate()
            raise SystemExit("Server did not become ready in time")
        (logs / "globe-server.json").write_text(json.dumps({"pid": process.pid, "url": url, "root": str(ROOT / "site")}) + "\n")
    print(url + "#/globe")
    if not args.no_open:
        if not webbrowser.open(url + "#/globe"):
            raise SystemExit("Could not request the desktop browser; open the printed URL")


if __name__ == "__main__":
    main()
