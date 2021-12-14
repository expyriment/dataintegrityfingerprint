
import sys
import os
from tempfile import NamedTemporaryFile
from subprocess import call

OUT_PDF = "dataintegrityfingerprint.pdf"

PANDOC="pandoc"
PANDOC_OPTIONS = []

HEADER = """
---
  title: "Data Integrity Fingerprint (DIF)"
  subtitle: "A proposal for a human-readable fingerprint of scientific datasets that allows verifying their integrity"
  author: O. Lindemann & F. Krause
  documentclass: scrartcl
  fontsize: 12pt
  linestretch: 1
  #indent: true
  #toc: true
  linkcolor: red
  urlcolor: blue
---
"""

REMOVE_LINES = 4


if __name__ == "__main__":

    try:
        fl = open(sys.argv[1], "r")
    except:
        raise RuntimeError("Please specify README.md file")

    a = fl.readlines()
    fl.close()

    # make temporary md file to render in pandoc
    with  NamedTemporaryFile(mode ='w+', delete=False) as tmpfl:
        tmpfl.write(HEADER)
        tmpfl.writelines(a[REMOVE_LINES:])

    # make pdf
    cmd = [PANDOC, tmpfl.name, "-o", OUT_PDF] + PANDOC_OPTIONS
    print(" ".join(cmd))
    call(cmd)





