#! usr/bin/env python

"""
Merge the traits data into plink fam file
"""

import sys
import argparse
import collections


##parameter
parser = argparse.ArgumentParser()
parser.add_argument("-f", dest="fam", required=True, help="the plink fam format file")
parser.add_argument("-t", dest="traits", required=True, type=argparse.FileType('r'),
                    default=sys.stdin, help="the trait file")
parser.add_argument("-o", dest="out", type=argparse.FileType('w'),
                    default=sys.stdout, help="the output allele frequency file used to SF2 input")
args = parser.parse_args()


##missing data marked as -9 in fam file
traits = collections.defaultdict(lambda :-9)
for line in args.traits:
    llist = line.strip().split()
    ncol = len(llist) - 1      # 1st column was sample id
    k,*v = llist
    traits[k] = tuple(v)


##handle fam file, the column of 6th and after it were traits data
for line in open(args.fam):
    llist = line.strip().split()[:-1]
    _, Snum, *_ = llist
    tr = traits[Snum]
    if tr == -9:
        tr = ("-9",) * ncol
    print("\t".join(llist), "\t".join(tr), sep="\t", file=args.out)

