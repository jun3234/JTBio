#! usr/bin/env python

import argparse
import collections
import sys

"""
When the file are too big and too many columns, you can specified column to filter
"""

##parameter
def get_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument("-bed", type=str, help="the bed file")
    parser.add_argument("-map", type=str, help="crd map file file")
    parser.add_argument("--outfile", dest="out", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output bed file, [default:stdout]")
    return parser.parse_args()

##
def read_bed(bed):
    D = collections.defaultdict(list)

    for line in open(bed):
        chrn, start, end = line.strip().split()

        D[chrn].append(line.strip().split())

    return D

##
def read_map(map):
    D = collections.defaultdict(list)

    for line in open(map):
        *_, chrn, start, end = line.strip().split()

        D[chrn].append(line.strip().split())

    return D



def get_cnt(bed, map, file=sys.stdout):

    bed = read_bed(bed)
    map = read_map(map)

    for key in bed:
        for bc, bs, be in bed[key]:

            for e in map[key]:
                *_, mc, ms, me = e

                if int(bs) >= int(ms) and int(bs) <= int(me):
                    print("\t".join(e + [bc, bs, be]), file=file)

                elif int(be) >= int(ms) and int(be) <= int(me):
                    print("\t".join(e + [bc, bs, be]), file=file)


if __name__ == '__main__':
    args = get_opts()
    get_cnt(args.bed, args.map, args.out)