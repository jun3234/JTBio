#! usr/bin/env python

"""
change format to a new statistics table
"""

import sys
import argparse

def read_rd_phased(in_rd_phased):
    read_db = {}
    for line in open(in_rd_phased):
        chrn, pos, GT, hp1_lst, hp2_lst = line.strip().split(",")
        hap1, hap2 = GT.split("|")

        for readn in hp1_lst.split("|"):
            if not readn:
                continue
            if readn not in read_db:
                read_db[readn] = {}
            if chrn not in read_db[readn]:
                read_db[readn][chrn] = {'ref': {}, 'alt':{}}
            read_db[readn][chrn]["ref"][pos] = hap1

        for readn in hp2_lst.split("|"):
            if not readn:
                continue
            if readn not in read_db:
                read_db[readn] = {}
            if chrn not in read_db[readn]:
                read_db[readn][chrn] = {'ref': {}, 'alt':{}}
            read_db[readn][chrn]["alt"][pos] = hap2

    return read_db


if __name__=='__main__':
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-r","--rd_phased", required=True, help="the rd_phased.txt file generated from 'retrieveReads.py'")
    parser.add_argument("--out", dest="outfile", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output bed file, [ default:stdout]")
    args = parser.parse_args()

    ##read txt
    rd_db = read_rd_phased(args.rd_phased)

    ##
    print("\t".join(["ReadName", "Hap1", "Hap2", "Total"]), file=args.outfile)
    for rd in rd_db:
        for chrn in rd_db[rd]:
            ref_len = len(rd_db[rd][chrn]['ref'])
            alt_len = len(rd_db[rd][chrn]['alt'])
            print(rd, chrn, ref_len, alt_len, ref_len+alt_len, sep="\t", file=args.outfile)

