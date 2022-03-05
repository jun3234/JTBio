#! usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import pysam
import argparse
import collections
import os



if __name__ == "__main__":
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", dest="vcffile", type=str, required=True, help="the input vcf file, calling from Nextpolish")
    parser.add_argument("--outfile", dest="out_vcf", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output bed file, [ default:stdout]")
    parser.add_argument("--het", dest="het", type=str, default=None,
                        help="get vcf line of GW and HML is homo., and FZX is hete.")
    args = parser.parse_args()

    ## infile
    vcffile = pysam.VariantFile(args.vcffile,'r')

    ## outvcf
    outvcf = pysam.VariantFile(args.out_vcf, "w", header=vcffile.header)

    ##
    for vcfrecord in vcffile:
        cnt = 0
        gt_info = [value["GT"] for value in vcfrecord.samples.values()]
        FZX_m, FZX_n, GW_m, GW_n, HML_m, HML_n = gt_info
        cnt += 1 if FZX_m == FZX_n and None not in FZX_m else 0
        cnt += 1 if GW_m == GW_n and None not in GW_m else 0
        cnt += 1 if HML_m == HML_n and None not in HML_m else 0
        if cnt >= 2:
            Maxcnt = max(dict(collections.Counter(gt_info)).values())
            if Maxcnt < 5:
                if not args.het:
                    outvcf.write(vcfrecord)
                else:
                    if (FZX_m == FZX_n) & (GW_m == GW_n) & (HML_m == HML_n) & (FZX_n != GW_m) & (GW_n != HML_m) & (FZX_n != HML_m):
                        outvcf.write(vcfrecord)

    outvcf.close()