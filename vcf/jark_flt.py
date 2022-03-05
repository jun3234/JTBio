#! usr/bin/env python3
# -*- coding: UTF-8 -*-

import gzip
import argparse
import re

if __name__ == "__main__":
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", dest="vcffile", type=str, required=True,
                        help="the input vcf file, calling from nextsv and merged with SURVIVOR")
    parser.add_argument("-o", dest="out_vcf", type=argparse.FileType('wb'), required=True,
                        help="the output vcf file, [ no default ]")
    parser.add_argument("-m", dest="chr_map", type=str, default=None,
                        help="the chromosome name of old mapping to new")
    args = parser.parse_args()

    ## read chr map
    chr_map = dict((line.strip().split()[0], line.strip().split()[1]) for line in open(args.chr_map))

    ##out
    outvcf = gzip.open(args.out_vcf, 'wb')

    ##loop over the file
    for line in gzip.open(args.vcffile, 'rb'):
        line = line.decode().strip()
        if line.startswith("#"):
            if line.startswith("##contig"):
                old_name = re.findall(r'.*=(.*),', line)[0]
                line = line.replace(old_name, chr_map[old_name])
            line = line + "\n"
            outvcf.write(line.encode())

        else:
            llist = line.split()
            llist[0] = chr_map[llist[0]]
            llist[7] = ";".join([ele for ele in llist[7].split(";") if not ele.startswith("EFF=")])
            line = "\t".join(llist) + "\n"
            outvcf.write(line.encode())







