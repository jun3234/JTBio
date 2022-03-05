#! usr/bin/env python

"""
merge multiple gene count csv file to one
"""

import argparse
import sys
import collections

if __name__ == '__main__':
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--files", required=True, nargs = "*",
                        help="the gene count file, can be specified multiple files")
    parser.add_argument("-t", "--tab", required=True, nargs="?",type=str,
                        help="the 1st and 2nd are allelic gene pairs info, tab file")
    parser.add_argument("--out", dest="outfile", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output bed file, [ default:stdout]")
    args = parser.parse_args()

    ##
    allel_pairs = [line.strip().split() for line in open(args.tab)]

    ##
    Lhead = ["gene_id"]
    D = collections.defaultdict(list)
    LA = []
    LB = []
    for file in args.files:

        for line in open(file, "r"):
            llist = line.strip().split(",")
            if line.startswith("gene_id"):
                for ele in llist[1:]:
                    LA.append("HA_" + ele)
                    LB.append("HB_" + ele)

            else:
                key = llist[0]
                D[key].extend(llist[1:])

    ## file header
    Lhead.extend(LA+LB)

    ## write to file
    print(",".join(Lhead))
    for a1,a2 in allel_pairs:

        try:
            HA = D[a1]
        except KeyError:
            D[a1] = ["0"] * len(LA)

        try:
            HB = D[a2]
        except KeyError:
            D[a2] = ["0"] * len(LB)

        line_val = D[a1] + D[a2]
        pa = "%s@%s" % (a1, a2)
        print(pa, ",".join(line_val), sep=",", file=args.outfile)