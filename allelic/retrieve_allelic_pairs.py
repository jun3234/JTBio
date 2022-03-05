#! usr/bin/env python

"""
Gene annotation was mapped to HY and HH. Due to one vs multiple relations.
The allelic gene pairs need retrieve again.
"""

import sys
import re
import argparse
import collections

##
def read_blast(blastout):
    blastd = collections.defaultdict(list)

    for line in open(blastout):
        qry, sub, *_ = line.strip().split()
        blastd[qry].append(sub)

    return blastd


## get chrn's number
def get_ele(g_cmp, s=0):
    chrn = re.findall(r'(\d+)$', g_cmp.split("_")[s])[0]
    return chrn

if __name__== "__main__":
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-b","--blast", dest="blastout", type=str, required=True,
                        help="the 'g1_vs_g2' blast output")
    parser.add_argument("--outfile", dest="out", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output bed file, [default:stdout]")
    args = parser.parse_args()


    ## parse input para
    blast = read_blast(args.blastout)
    sorted_key = sorted(blast,key=lambda x:int(x.split("_")[-1]))

    ## iter dict, every chr
    inum = 0
    for q_cmp in sorted_key:
        qgn, qchr, qstart, qend, qnum = q_cmp.split("_")
        qchrn = re.findall(r'(\d+)$', qchr)[0]

        flag = []
        s_cmps = sorted(blast[q_cmp], key=lambda x: int(x.split("_")[-1]))
        for s_cmp in s_cmps:

            sgn, schr, sstart, send, snum = s_cmp.split("_")
            schrn = re.findall(r'(\d+)$', schr)[0]

            if qchrn == schrn:
                flag.append("schr_snam") if qgn.split(".")[0] == sgn.split(".")[0] else flag.append("schr")
            else:
                flag.append("NaN")

        if "schr_snam" in flag:
            inx = flag.index("schr_snam")
        elif "schr" in flag:
            inx = flag.index("schr")
        elif "NaN" in flag:
            inx = flag.index("NaN")

        s_cmp = s_cmps[inx]
        sgn, schr, sstart, send, snum = s_cmp.split("_")
        schrn = re.findall(r'(\d+)$', schr)[0]
        if qchrn == schrn:
            print(q_cmp, s_cmp, sep="\t", file=args.out)

