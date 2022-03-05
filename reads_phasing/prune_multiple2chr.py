#! usr/bin/env python

import sys
import argparse
import re


def read_phased_stat(rdps):
    rd_db = {}
    for line in open(rdps):
        rg, *rst = line.strip().split()
        sn = int(rst[-1])
        readn, mapq, align_len = re.findall(r'(m.*)\((\d+);(\d+)\)', rg)[0]

        if readn not in rd_db:
            rd_db[readn] = [mapq, align_len] + rst
        elif readn in rd_db:
            map_quality = int(rd_db[readn][0])
            alignment_length = int(rd_db[readn][1])
            sn_tt = int(rd_db[readn][-1])
            if int(mapq) > map_quality:
                rd_db[readn] = [mapq, align_len] + rst
            elif int(mapq) == map_quality:
                if (sn/int(align_len)) > (sn_tt/alignment_length):
                    rd_db[readn] = [mapq, align_len] + rst
    return rd_db


if __name__=='__main__':
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-rs","--rd_phased_stat", required=True, help="the rd_phased.txt file generated from 'retrieveReads.py'")
    parser.add_argument("--out", dest="outfile", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output bed file, [ default:stdout]")
    args = parser.parse_args()

    ##
    rd_db = read_phased_stat(args.rd_phased_stat)

    for rdn in rd_db:
        rst = rd_db[rdn][2:]
        print(rdn, "\t".join(rst), sep="\t", file=args.outfile)



