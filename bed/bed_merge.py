#! usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import argparse
import functools
from JTBio.bed.base import condition,bedFile,bed_cat,bed_sort


## define fun
def bed_merge(L1=list(), L2=list()):
    """ get union among two region, like:
    A = (1,3), B = (2,4);   bed_merge(A,B) --> ("nowrite",(),(1,4))
    A = (1,4), B = (2,3);   bed_merge(A,B) --> ("nowrite",(),(1,4))
    A = (1,2), B = (3,4);   bed_merge(A,B) --> ("write",(1,2),(3,4))
    """
    L1 = list(L1)
    L2 = list(L2)

    cond, (s1, e1, r1), (s2, e2, r2) = condition(L1, L2)
    if cond == "no_over":
        return "write",(s1,e1,r1),(s2,e2,r2)
    elif cond == "overlap":
        return "nowrite",(None,None,None),(s1,e2,r2)
    elif cond == "contain":
        return "nowrite",(None,None,None),(s1,e1,r1)


if __name__ == "__main__":
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", dest="a_bedfile", type=str, help="the input bed file")
    parser.add_argument("-b", dest="b_bedfile", type=str, help="the input bed file,")
    parser.add_argument("--outfile", dest="out_bed", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output bed file, [ default:stdout]")
    args = parser.parse_args()


    # bedFile instance object
    bedfiles = map(bedFile, [args.a_bedfile, args.b_bedfile])

    # multiple dict cat together
    all_bedfile_dict = functools.reduce(bed_cat, [bedfile.load for bedfile in bedfiles])

    # sort chr and start
    chrs_sorted, bedfile_dict_sorted = bed_sort(all_bedfile_dict)

    # output
    for chr in chrs_sorted:
        pre_ele = []

        for ele in bedfile_dict_sorted[chr]:
            if pre_ele:
                wsign,(s1,e1,r1),(s2,e2,r2) = bed_merge(pre_ele,ele)
                pre_ele = (s2, e2, r2)
                if wsign == "write":
                    print(chr, s1, e1, sep="\t", file=args.out_bed)
            else:
                pre_ele = ele
        print(chr, pre_ele[0], pre_ele[1], sep="\t", file=args.out_bed)