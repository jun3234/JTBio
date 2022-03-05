#! usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Convert plink freq output file into SweepFinder2
"""


import sys
import argparse
import re


##parameter
parser = argparse.ArgumentParser()
parser.add_argument("-f", dest="afreq", required=True, help="the freq file generated with 'plink2 --fre'")
parser.add_argument("-o", dest="out", type=argparse.FileType('w'),
                    default=sys.stdout, help="the output allele frequency file used to SF2 input")
args = parser.parse_args()

## format the outfile header
outheader = ["Chr", "position", "x", "n", "folded"]
print("\t".join(outheader), file=args.out)

for line in open(args.afreq):
    line = line.strip()
    if line.startswith("#"):
        print("skip irregular line: {%s} " % line, file=sys.stderr)
    else:
        Chr, ID, *_, ALTfreq, Ttcnt = line.split()
        Pos = int(re.findall(r':(\d+)[ACGT]:', ID)[0])
        Ttcnt = int(Ttcnt)
        Alcnt = int(round(float(ALTfreq) * Ttcnt))
        print(Chr, Pos, Alcnt, Ttcnt, 0, sep="\t", file=args.out)
