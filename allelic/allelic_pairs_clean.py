#! usr/bin/env python

"""
clear away obvious not allelic gene pairs <<Unfinished>>
"""

import sys
import re
import argparse
import collections


# read pairs
def read_pairs(allelic_pairs):
    d = collections.defaultdict(list)
    s = []

    for line in open(allelic_pairs):
        qry, sbj = line.strip().split()
        qnum = int(get_ele(qry, -1))
        snum = int(get_ele(sbj, -1))
        d[qnum].extend([qry,sbj])
        s.append((qnum,snum))

    return d,s


## get chrn's number
def get_ele(g_cmp, s=0):
    chrn = re.findall(r'(\d+)$', g_cmp.split("_")[s])[0]
    return chrn


if __name__== "__main__":
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-a","--allele", dest="allelic_pairs", type=str, required=True,
                        help="the allelic pairs, can be retrieve from blast")
    parser.add_argument("-u","--upper", dest="gene_upper", type=int, default=20,
                        help="the gene pos great than '-u' was regarded not witgin synteny")
    parser.add_argument("--outfile", dest="out", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output bed file, [default:stdout]")
    args = parser.parse_args()

    # parse para
    pa,se = read_pairs(args.allelic_pairs)

    # filter
    fn_lst = []
    qn_lst = []
    tmp = []
    stag = 0
    step = 1
    cnt = 0
    for qn, sn in se:

        if abs(sn - stag) > 20:
            tmp.append(sn);qn_lst.append(qn)
            stag = stag
            cnt += 1
            step = 2

        elif abs(sn - stag) <= 20:
            if step == 2:
                if cnt >= 3:
                    fn_lst.extend(qn_lst)
                elif cnt < 3:
                    fn_lst.extend(qn_lst[:-cnt])
                tmp = [];qn_lst = []
                step = 1

            if step == 1:
                tmp.append(sn);qn_lst.append(qn)
                stag = sn

    ##output
    print(len(fn_lst))
    for qn in fn_lst:
        print("\t".join(pa[qn]), file=args.out)
