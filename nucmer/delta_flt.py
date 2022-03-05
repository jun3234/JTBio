#! usr/bin/env python

"""
get the target region
"""

import sys
import argparse
import collections

##
def get_opts():
    args = argparse.ArgumentParser()
    args.add_argument('-d', '--delta', type=str, required=True, help='get the target region info')
    args.add_argument('-t', '--table', type=str, required=True, help='the right chrs map, in delta ">" line')
    args.add_argument("--out", dest="outfile", type=argparse.FileType('w'),
                      default=sys.stdout, help="the output bed file, [ default:stdout]")

    return args.parse_args()


##
def read_tab(intab):
    cmap = collections.defaultdict(list)
    with open(intab,"r") as fn:
        for line in fn:
            key, val = line.strip().split()
            cmap[key].append(val)
    return cmap


##
def delta_flt(indelta, intab, file=sys.stdout):
    flag = False
    for line in open(indelta,"r"):
        if line.startswith(">"):
            ref, qry, rlen, qlen = line[1:].strip().split()
            cmap = read_tab(intab)
            flag = True if qry in cmap[ref] else False

        if flag:
            print(line.strip(), file=file)

        elif line.startswith(("/","NUCMER")):
            print(line.strip(), file=file)

    return "Finished !"



if __name__ == '__main__':
    args = get_opts()
    delta_flt(args.delta, args.table, file=args.outfile)
