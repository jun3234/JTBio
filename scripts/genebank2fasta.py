#! usr/bin/env python

"""
Exact fasta from genebank file
"""

import sys
import re
import argparse

# parameter
parser = argparse.ArgumentParser()
parser.add_argument("gb", type=argparse.FileType('r'), help="the genebank file",nargs='?', default=sys.stdin)
args = parser.parse_args()

## new and old name mapping
flag = False
for line in args.gb:
    line = line.strip()

    if line.startswith("//"):
        flag = False

    elif flag:
        strlist = re.findall(r'[a-zA-Z]+', line)
        print("".join(strlist).upper(), file=sys.stdout)

    elif line.startswith("DEFINITION"):
        line = line.lstrip("DEFINITION").strip(" ")
        print(">", line, sep="", file=sys.stdout)

    elif line.startswith("ORIGIN"):
        flag = True


