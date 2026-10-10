# kitchen/reader.py -- talk to the free local model (OpenAI-compatible)
import json, re, time, base64, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from db import env
import requests

def _strip_think(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()

def _extract_json(text):
    start = min([i for i in (text.find("{"), text.find("[")) if i >= 0], default=-1)
    if start < 0:
        raise ValueError("no JSON found")
    end = max(text.rfind("}"), text.rfind("]"))
    return text[start:end + 1]

def ask(system, user, images=None, max_tokens=6000, temperature=0.0,
        expect_json=True, retries=3, timeout=3600):
    url = env("READER_BASE_URL").rstrip("/") + "/chat/completions"
    no_think = env("READER_NO_THINK_TAG", "")
    if no_think:
        system = system + "\n" + no_think
    content = [{"type": "text", "text": user}]
    for path in (images or []):
        b64 = base64.b64encode(Path(path).read_bytes()).decode()
        content.append({"type": "image_url",
                        "image_url": {"url": "data:image/png;base64," + b64}})
    body = {
        "model": env("READER_VISION_MODEL") if images else env("READER_MODEL"),
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": content if images else user}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    # DEVIATION from the BIBLE's verbatim reader.py, recorded in PROGRESS.md:
    # Ollama silently truncates to its default 4096-token window unless the
    # window is set in the request. A Table of Contents is up to ~100,000
    # characters, so without this the reader would answer from a truncated
    # page and quietly lose chapters. The model supports 262,144.
    num_ctx = env("READER_NUM_CTX")
    if num_ctx:
        body["options"] = {"num_ctx": int(num_ctx)}
    last_error = None
    for attempt in range(retries):
        try:
            r = requests.post(url, json=body, timeout=timeout)
            r.raise_for_status()
            text = _strip_think(r.json()["choices"][0]["message"]["content"])
            if not expect_json:
                return text
            return json.loads(_extract_json(text))
        except Exception as e:
            last_error = e
            time.sleep(3)
    raise RuntimeError(f"reader failed after {retries} attempts: {last_error}")

if __name__ == "__main__":
    print(ask("Answer in JSON.", 'Return {"ok": true}'))

