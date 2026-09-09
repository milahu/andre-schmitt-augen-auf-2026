#!/usr/bin/env python3

import glob
import os
import re
import shutil
import subprocess
import sys
import zipfile
import shlex
from datetime import datetime
from pathlib import Path

from _shared import (
    load_config,
    get_page_num,
)


src = Path("090-ocr")

# write EPUB file
# dst = Path(Path(__file__).stem + ".epub")

# write unpacked EPUB files to workdir
dst = Path(".")


config = load_config()


if dst != Path(".") and dst.exists():
    print(f"error: output exists: {dst}")
    sys.exit(1)


# downscale to 300 dpi
# 600 dpi -> 300 dpi: 90 MB -> 60 MB
scale = 300 / config.scan_resolution


hocr_to_epub_fxl = "hocr-to-epub-fxl"

# TODO dont commit
if 1:
    hocr_to_epub_fxl = "/home/user/src/archive-hocr-tools/bin/hocr-to-epub-fxl"

args = [
    hocr_to_epub_fxl,
    "--output", str(dst),
]

if dst == Path("."):
    args.append("--output-unpacked")


def git_modified():
    return subprocess.check_output(
        ["git", "show", "-s", "--format=%cI", "HEAD"],
        text=True,
    ).strip()


def stat_modified(path):
    ts = Path(path).stat().st_mtime
    dt = datetime.fromtimestamp(ts).astimezone()
    return dt.isoformat(timespec="seconds")


doc_modified = max(
    git_modified(),
    stat_modified(src),
)


args += [
    "--scale", str(scale),
    "--image-format", "avif",
    "--text-format", "html",
    # TODO? move these config items to 000-config.py
    "--doc-modified", doc_modified,
    "--doc-title", "Augen Auf!",
    "--doc-subtitle", "Wie du Gefahr erkennst, bevor sie dich erkennt",
    # "--doc-subject", "",
    "--doc-date", "2026",
    "--doc-edition", "1",
    "--doc-extent", "399 pages",
    "--color-image-pages", "401-",
    "--doc-author", "Andre Schmitt",
    "--doc-author", "Dr. Charlie Chromehead",
    # "--doc-introducer", "",
    # "--doc-contributor", "",
    # "--doc-translator", "",
    # "--doc-publisher", "",
    "--doc-language", "de", # german
    # "--doc-language", "en", # english
    "--doc-isbn", "9798278822394",
    "--doc-cover-image", "072-deskew-fix-page-size/401.tiff",
    "--canonical-url-base", "https://TODO_REPO_OWNER_USERNAME.github.io/TODO_REPO_NAME/",
    "--doc-description", """
Der Fehler den du nicht machen darfst:
Ein ungutes Gefühl ignorieren.
Den flüchtigen Blick abtun.
Sich selbst beruhigen:
„Wird schon nichts sein.“
Das ist die Denkweise, die Opfer hervorbringt.
Denn wenn du siehst, bist du schon im Kampf.
Aber wenn du erkennst, bist du noch frei.

Dieses Buch ist dein ungeschminkter Blick hinter die Fassade der Sicherheit -
geschrieben von den Schattenprofilern André Schmitt
(Veteran des Kommando Spezialkräfte (KSK); Überlebender aus Krisen- und Kriegsgebieten)
und Dr. Charlie Chromehead
(Fachpsychologe, Profiler und ehemaliger Soldat militärischer Spezialkräfte; Experte für manipulative Muster).

Sie haben an Orten operiert, wo ein Fehler den Tod bedeutete.
Jetzt brechen sie das Schweigen und geben dir das Wissen,
das bisher nur Geheimdiensten und Spezialeinheiten vorbehalten war.

Wir geben dir keine Ratschläge.
Wir geben dir ein Werkzeug, das Leben rettet:

Der Code der Gefahr:
Lerne, Mimik, Gestik und Körpersprache so schnell zu lesen, dass du die Bedrohung erkennst,
bevor sie weiß, dass sie gesehen wurde.

Entlarve die Täuschung:
Durchschaue manipulative Muster und löse Täuschungen auf, bevor sie ausgesprochen werden.

Die 3-Sekunden-Regel:
Trainiere dein Frühwarnsystem und erkenne den kritischen Moment,
in dem du verschwindest, bevor die Eskalation beginnt.

Hör auf, blind zu sein:
In einer Zeit, in der Verbrechen am helllichten Tag passieren und Gewalt ohne Vorwarnung explodiert,
ist Wegsehen Verrat an deiner eigenen Sicherheit.

Du kannst dich nicht mehr auf andere verlassen.
Dein Verstand ist deine beste Waffe.

Dies ist das härteste und ehrlichste Training für deinen mentalen Muskel.
Geschrieben für alle, die bereit sind, den unbequemen Preis der Klarheit zu zahlen,
um ihre Autonomie zu sichern.

Öffne die Augen. Sei kompetent. Überlebe!
""",
]


print(">", shlex.join(args + sys.argv[1:]) + f" {src}/*.hocr")


hocr_files = list(src.glob("*.hocr"))

hocr_files.sort()

subprocess.run(
    args + sys.argv[1:] + hocr_files,
    check=True,
)


if dst == Path("."):
    print("done ./index.xhtml")
    sys.exit(0)


print(f"done {dst}")


# extract the EPUB content files

# rm -rf $dst.unzip
unzip_dir = Path(str(dst) + ".unzip")
shutil.rmtree(unzip_dir, ignore_errors=True)
unzip_dir.mkdir()


# unzip -q ../$dst
with zipfile.ZipFile(dst) as z:
    z.extractall(unzip_dir)


print(f"done {unzip_dir}/index.html")
