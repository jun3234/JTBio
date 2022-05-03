#! usr/bin/env python

"""
split sequence witn N or other base
"""

import sys
import pysam
import argparse
import re

# parameter
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--infasta", dest="fasta", required=True, help="the fasta formats file")
parser.add_argument("-o", "--output", dest="out_seq", nargs='?', type=argparse.FileType('w'),
                    default=sys.stdout, help="the output fasta file")
parser.add_argument("-s", "--seq", dest="seq_base", type=str, default=None,
                    help="split sequence with N or other base")
args = parser.parse_args()


# parameter
infasta = pysam.FastaFile(args.fasta)

# output
bre_point = open("break_point.txt", "w")

##
for name in infasta.references:
    seq = infasta.fetch(name)
    iter = re.finditer(r'[^N]+', seq)

    cnt = 0
    gap = 0
    for it in iter:
        gap = it.start() - gap
        print(">%s_chunk%s" % (name, cnt), file=args.out_seq)
        print(it.group(), file=args.out_seq)
        print(name, it.start(), it.end(), cnt, gap, sep="\t", file=bre_point)
        gap = it.end()
        cnt += 1
