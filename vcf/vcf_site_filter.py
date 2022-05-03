#! usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Filter vcf file according the chromosome and coord
"""

import sys
import pysam
import argparse
import gzip


##parameters
def get_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--vcf", type=str, help="the Variants file")
    parser.add_argument("-s", "--site", type=str, help="the file containing the site will be keep")
    parser.add_argument("--outfile", dest="out", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output vcf file, [default:stdout]")
    return parser.parse_args()


##read in 4fold site
def read_4fold_info(file):
    """ read in 4fold file info and store {chr:[crd1,crd2,...]}
    """
    S = set()   #to remove repeat
    for line in open(file):
        chr, crd, *_ = line.strip().split()
        S.add((chr,crd))
    return list(S)


def filter_vcf(vcf, site, outfile):
    """ Filter vcf site according to 4fold info
    """
    ##read in
    vcffile = pysam.VariantFile(vcf,"rb")
    ##out site
    outvcf = pysam.VariantFile(outfile, "w", header=vcffile.header)

    ##
    L = read_4fold_info(site)
    print("read 4fold site %s." % len(L), file=sys.stderr)
    L.sort(key=lambda x: (x[0], int(x[-1])))
    print("sorted site according (chr, pos)...", file=sys.stderr)

    ##
    print("start filter vcf file...", file=sys.stderr)
    for chr,crd in L:
        fet = vcffile.fetch(chr, start = int(crd) - 1, end = int(crd)) # 0-based in pysam
        for rcd in fet:
            outvcf.write(rcd)

    print("VCF file filter has been finished...", file=sys.stderr)

if __name__ == "__main__":
    args = get_opts()
    filter_vcf(args.vcf, args.site, args.out)