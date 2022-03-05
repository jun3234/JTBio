#! usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import argparse
import functools
from JTBio.bed.base import condition,bedFile,bed_cat,bed_sort
from JTBio.bed.bed_merge import bed_merge


## define fun
def bed_diff(L1=list(), L2=list()):
    """ get union among two region, like:
    A = (1,3), B = (2,4);   bed_merge(A,B) --> ("nowrite",(),(1,4))
    A = (1,4), B = (2,3);   bed_merge(A,B) --> ("nowrite",(),(1,4))
    A = (1,2), B = (3,4);   bed_merge(A,B) --> ("write",(1,2),(3,4))

    bed file is 0-based, and Half closed half open interval eg: [0, 851)
    """
    s1, e1, r1 = L1 = list(L1)
    s2, e2, r2 = L2 = list(L2)

    if s1 < s2:
        cond, (s1, e1, r1), (s2, e2, r2) = condition(L1, L2)
        if cond == "no_over":
            return "write", (s1, e1, r1), (None, None, None)
        elif cond == "overlap":
            return "write", (s1, s2, r1), (None, None, None)
        elif cond == "contain":
            return "write", (s1, s2, r1), (e2, e1, r1)

    elif s1 >= s2:
        cond, (s2, e2, r2), (s1, e1, r1) = condition(L1, L2)
        if cond == "no_over":
            return "nowrite", (None, None, None), (s1, e1, r1)
        elif cond == "overlap":
            return "nowrite", (None, None, None), (e2, e1, r1)
        elif cond == "contain":
            return "nowrite", (None, None, None), (None, None, None)


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
    bed_cat = functools.partial(bed_cat, type="difference")
    all_bedfile_dict = functools.reduce(bed_cat, [bedfile.load for bedfile in bedfiles])

    # sort chr and start
    chrs_sorted, bedfile_dict_sorted = bed_sort(all_bedfile_dict)


    # output
    for chr in chrs_sorted:
        pre_ele = []
        for ele in bedfile_dict_sorted[chr]:
            *_, rank1 = ele
            if not pre_ele:
                if rank1 == 1:  # just start from 1st file
                    pre_ele = ele
                    flag = True
            elif flag:
                if rank1 != 1:  # is not from the 1st file
                    wsign, (ws1, we1, r1), (ws2, we2, r2) = bed_diff(pre_ele,ele)
                    if wsign == "write":
                        print(chr, ws1, we1, sep="\t", file=args.out_bed)
                        if ws2 is None:
                            pre_ele = []  # reset list
                        else:
                            pre_ele = (ws2, we2, r2)
                    elif wsign == "nowrite":
                        if ws2 is None:
                            pre_ele = []
                        else:
                            pre_ele = (ws2, we2, r2)
                elif rank1 == 1:    # from the same file
                    wsign, (ws1, we1, r1), (ws2, we2, r2) = bed_merge(pre_ele, ele)
                    pre_ele = (ws2, we2, r2)
                    if wsign == "write":
                        print(pre_ele, ele)
                        print(chr, ws1, we1, sep="\t", file=args.out_bed)
        if pre_ele:
            ws2, we2, r2 = pre_ele
            print(chr, ws2, we2, sep="\t", file=args.out_bed)