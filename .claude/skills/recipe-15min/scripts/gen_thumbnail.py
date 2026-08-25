#!/usr/bin/env python
"""Generate a Ghibli-style recipe thumbnail with Gemini (Nano Banana Pro).

Usage:
    python gen_thumbnail.py --out <path.jpg> --subject "<food description>"
    python gen_thumbnail.py --out <path.jpg> --subject-file <file.txt>
    python gen_thumbnail.py --out a.jpg --subject "..." --out b.jpg --subject "..."   # parallel

The locked STYLE block is appended to every subject so all thumbnails in the
recipe book stay visually consistent. Do not edit STYLE casually — changing it
makes new images clash with the existing ones.

Requires the GEMINI_API_KEY environment variable.
"""
import argparse, base64, json, os, sys, threading, urllib.error, urllib.request

MODEL = "gemini-3-pro-image-preview"  # Nano Banana Pro
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"

# --- LOCKED STYLE BLOCK — keep identical across the whole recipe book ---
STYLE = """
Art style: Studio Ghibli anime film background art, hand-painted watercolor and gouache texture, soft cel shading, clean delicate line art, gentle painterly brush strokes, warm earthy palette, no harsh contrast, cozy nostalgic and appetizing atmosphere. Soft natural daylight from a window on the left casting warm highlights and a gentle shadow.
No text, no letters, no watermark. Horizontal 16:9 composition suitable for a recipe article thumbnail.
"""

LEAD = "A warm, hand-painted Studio Ghibli style illustration of "


def build_prompt(subject):
    subject = subject.strip()
    if not subject.lower().startswith(("a ", "an ", "the ")):
        subject = LEAD + subject
    return subject + "\n" + STYLE


def generate(out, subject, key, results):
    body = {"contents": [{"parts": [{"text": build_prompt(subject)}]}]}
    req = urllib.request.Request(
        ENDPOINT.format(m=MODEL),
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "x-goog-api-key": key},
    )
    try:
        with urllib.request.urlopen(req, timeout=420) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        results.append((out, "HTTP %s: %s" % (e.code, e.read().decode()[:400])))
        return
    except Exception as e:
        results.append((out, repr(e)))
        return

    for c in data.get("candidates", []):
        for p in c.get("content", {}).get("parts", []):
            if "inlineData" in p:
                with open(out, "wb") as f:
                    f.write(base64.b64decode(p["inlineData"]["data"]))
                results.append((out, None))
                print("SAVED", out)
                return
    # No image part: usually a safety block or a text-only reply.
    results.append((out, "no image in response: " + json.dumps(data)[:400]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", action="append", required=True,
                    help="output .jpg path (the API returns JPEG)")
    ap.add_argument("--subject", action="append", default=[],
                    help="food/scene description, one per --out")
    ap.add_argument("--subject-file", action="append", default=[],
                    help="read the description from a file instead")
    args = ap.parse_args()

    subjects = list(args.subject) + [open(f, encoding="utf-8").read() for f in args.subject_file]
    if len(subjects) != len(args.out):
        sys.exit("error: number of --subject/--subject-file must match --out")

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        sys.exit("error: GEMINI_API_KEY is not set. Add it to .claude/settings.local.json "
                 'under "env", or export it in the shell.')

    results = []
    threads = [threading.Thread(target=generate, args=(o, s, key, results))
               for o, s in zip(args.out, subjects)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    failed = [(o, e) for o, e in results if e]
    for o, e in failed:
        print("FAILED", o, "-", e, file=sys.stderr)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
