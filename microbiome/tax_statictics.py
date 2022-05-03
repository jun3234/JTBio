#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Statistics of otu/asv table count
"""

import sys
import pandas as pd
import argparse
from collections import defaultdict


# parameters
def get_opts():
    """ parse parameters
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--table", type=str, help="the input biom table with taxonomy")
    parser.add_argument("-l", "--level", type=str, default="p__",
                        choices=["d__", "p__", "c__", "o__", "f__", "g__", "s__"],
                        help="the prefix of taxonomy represent")
    parser.add_argument("-m", "--min", type=int, default=2,
                        help="the min count to calculated taxonomy")
    parser.add_argument("-o", "--output", dest="out", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output count matrix, [default:stdout]")
    return parser.parse_args()


# universal set
def get_universal_set(table, level):
    """ Known how many certain levels in total
    """
    s = set()
    for line in open(table):
        if line.startswith("#"):
            pass
        else:
            tax = line.strip().split("\t")[-1]
            t = [v[3:] for v in tax.split("; ") if v.startswith(level)]
            s.add("Unknown") if len(t) == 0 else s.add(t[0])
    return s


# every sample posses levels
def get_sample_level(table, level, m):
    """ collecting all levels in every sample
    """

    # read in table
    data = pd.read_table(table, header=1, index_col=0, delimiter="\t")
    d = {}
    for sample in data.columns[:-1]:
        d[sample] = defaultdict(list)
        criteria = data[sample] >= m
        sdata = data[criteria]

        # iter nrows
        for i in range(0, sdata.shape[0]):
            otu = sdata[sample][i]
            tax = sdata["taxonomy"][i]
            t = [v[3:] for v in tax.split("; ") if v.startswith(level)]
            s = "Unknown" if len(t) == 0 else t[0]
            d[sample][s].append(otu)
    return d


# statistics
def statis_count(sample_level, total_set, file=sys.stdout):
    """ The statistics count at levels in every sample
    """

    # write, set store value are random, but Once storage is complete
    # the read order is constant, "order list(set) == for i in set"
    head = [""] + list(total_set)
    print("\t".join(head), file=file)
    for sample in sample_level:
        ltp = []
        for tax in total_set:
            cnt = sum(sample_level[sample][tax])
            ltp.append(str(cnt))
        llist = [sample] + ltp
        print("\t".join(llist), file=file)


if __name__ == '__main__':
    print("Parser the parameters ...", file=sys.stderr)
    args = get_opts()

    print("Calculated the universal set ...", file=sys.stderr)
    ts = get_universal_set(args.table, args.level)

    print("Mapping taxonomy and count in every sample ...", file=sys.stderr)
    sl = get_sample_level(args.table, args.level, args.min)

    print("Summary counts and output ...", file=sys.stderr)
    statis_count(sl, ts, file=args.out)
