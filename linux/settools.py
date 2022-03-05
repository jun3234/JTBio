#! usr/bin/env python

import argparse
import sys

"""
When the file are too big and too many ids, linux grep command are too slow
"""

## parameter
parser = argparse.ArgumentParser()
parser.add_argument("-ids1", type=argparse.FileType('r'),
                    default=sys.stdin, help="the ids in one set")
parser.add_argument("-ids2", type=argparse.FileType('r'),
                    default=sys.stdin, help="the ids in another set")
parser.add_argument("-o", type=argparse.FileType('w'),
                    default=sys.stdout, help="the out ids")
parser.add_argument("-m", type=str, choices=["u","i","d"],
                    default="u", help="the manipulate between two sets")
args = parser.parse_args()


## analytic parameter
ids1 = set([line.strip() for line in args.ids1])
ids2 = set([line.strip() for line in args.ids2])


if args.m == "u":
    idset = ids1.union(ids2)
    for id in idset:
        print(id, file=args.o)

elif args.m == "d":
    idset = ids1.difference(ids2)
    for id in idset:
        print(id, file=args.o)

elif args.m == "i":
    idset = ids1.intersection(ids2)
    for id in idset:
        print(id, file=args.o)