#! usr/bin/env python

import sys
import argparse

"""
split file into two part according ID match
    python test.py  idfile rawdata  std.out
"""

if __name__=='__main__':
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("--snpdensity", type=str, help="the feature formats file")
    parser.add_argument("--dea",type=str,help="the input vcf file")
    parser.add_argument("--allel_pairs", type=str, help="the gff3 formats file")
    args = parser.parse_args()

dea = set(line.strip() for line in open(args.dea))
alp = set(line.strip() for line in open(args.allel_pairs))

for line in open(args.snpdensity):
    line = line.strip()

    if line.startswith("geneName"):
        print("sign", line, sep="\t", file=sys.stdout)

    else:
        gname, *_ = line.split()
        if gname in dea:
            print("DEA", line, sep="\t", file=sys.stdout)
        elif gname in alp:
            print("EEA", line, sep="\t", file=sys.stdout)
        else:
            print("noSign", line, sep="\t", file=sys.stdout)