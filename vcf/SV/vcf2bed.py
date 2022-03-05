#! usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import pysam
import argparse


if __name__ == "__main__":
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", dest="vcffile", type=str, required=True, help="the input vcf file, calling from Nextpolish")
    parser.add_argument("--outfile", dest="out_bed", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output bed file, [ default:stdout]")
    args = parser.parse_args()

    ## infile
    vcffile = pysam.VariantFile(args.vcffile,'r')

    ##
    for vcfrecord in vcffile:

        ## get other info
        infodict = dict(vcfrecord.info.items())

        ## sv type and length
        SVLen = infodict["SVLEN"]
        SVTyp = infodict["SVTYPE"]
        Star = vcfrecord.start
        End = vcfrecord.stop

        ## genotype every sample
        gt_info = [value["GT"] for value in vcfrecord.samples.values()]
        gt = ["%s|%s" % (i,j) for i,j in gt_info]

        ##print
        print(vcfrecord.chrom, Star, End, SVTyp, SVLen, "\t".join(gt), sep="\t", file=args.out_bed)