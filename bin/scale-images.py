#!/usr/bin/env python3
"""
scale-images.py — Skalziert alle Bilder in docs/images/ auf max. 800px Breite.

Vorschaubilder sind quadratisch; sie werden proportional auf 800×800 skaliert.
Die längere Seite wird auf 800px gesetzt, das Bild bleibt proportional.
Baseline-JPEG, Qualität 90 (kein Transparenz-Problem, keine Metadaten-Schwellen).

Aufruf:
    python3 bin/scale-images.py [--max 800] [--check]
    --check : nur prüfen, nichts schreiben
    Ohne Flag: schreibt alle > 800px neu (Dry-Run ohne --write)
"""

import argparse
import glob
import os
import sys

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(ROOT, "docs", "images")
DEFAULT_MAX = 800


def scale_file(path, max_dim, quality=90):
    """Skalziert eine Datei proportional auf max_dim, schreibt sie neu."""
    with Image.open(path) as im:
        w, h = im.size
        dim = max(w, h)
        if dim <= max_dim:
            return False, "%d px (unter %d, unverändert)" % (dim, max_dim)
        nw, nh = int(max_dim * w / dim), int(max_dim * h / dim)
        im = im.resize((nw, nh), Image.LANCZOS)
        # baseline JPEG, quality 90
        im.save(path, "JPEG", quality=quality)
        return True, "%d -> %d px" % (dim, max(nw, nh))


def main():
    parser = argparse.ArgumentParser(description="Skalziert Vorschaubilder auf max. 800px Breite.")
    parser.add_argument("--max", type=int, default=DEFAULT_MAX,
                        help="Max. Abmessung in px (Default: %d)" % DEFAULT_MAX)
    parser.add_argument("--check", action="store_true", help="Nur prüfen, nichts schreiben")
    parser.add_argument("--quality", type=int, default=90, help="JPEG-Qualität")
    args = parser.parse_args()

    files = sorted(glob.glob(os.path.join(IMAGES_DIR, "*.jpg")))
    files += sorted(glob.glob(os.path.join(IMAGES_DIR, "*.jpeg")))

    if not files:
        print("Keine JPG/JPEG-Dateien in docs/images/")
        return

    if args.check:
        print("=== Prüfen: Bilder > %d px ===" % args.max)
        big = []
        for f in files:
            try:
                with Image.open(f) as im:
                    dim = max(im.size)
                    if dim > args.max:
                        big.append((dim, os.path.basename(f)))
            except Exception as e:
                print("Fehler (Lesen): %s: %s" % (os.path.basename(f), e))
        if big:
            print("  %d Bilder > %d px:" % (len(big), args.max))
            for dim, name in sorted(big, reverse=True):
                print("    %6d px  %s" % (dim, name))
        else:
            print("Alle %d Bilder <= %d px." % (len(files), args.max))
        return

    print("=== Skalieren auf max. %d px ===" % args.max)
    count = 0
    errors = 0
    for f in files:
        try:
            ok, msg = scale_file(f, args.max, args.quality)
            if ok:
                count += 1
                print("  %s (%s)" % (os.path.basename(f), msg))
            else:
                print("  %s (%s)" % (os.path.basename(f), msg))
        except Exception as e:
            errors += 1
            print("Fehler: %s: %s" % (os.path.basename(f), e))

    print()
    print("Skaliert: %d, unverändert: %d, Fehler: %d" % (count, len(files) - count, errors))
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
