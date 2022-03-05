#! usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import pysam
import argparse
import numpy as np


from JTBio.vcf.SV.base import chain
from JTBio.vcf.SV.base import get_spe_len


if __name__ == "__main__":
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", dest="vcffile", type=str, required=True,
                        help="the input vcf file, calling from nextsv and merged with SURVIVOR")
    parser.add_argument("--outfile", dest="out_vcf", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output vcf file, [ default:stdout ]")
    parser.add_argument("-H", dest="is_high_quality", default=None, action="store_true",
                        help="exclude record with low-quality SVs, like flag:UNRESOLVED.")
    parser.add_argument("-P", dest="is_PRECISE", default=None, action="store_true",
                        help="exclude record with ambiguous breakpoints, flag:IMPRECISE.")
    parser.add_argument("-t", dest="SVtype", type=str, default=None,
                        help="get vcf line containing this type variants, can be any of 'DEL-DUP-INS-INV-TRA'.")
    parser.add_argument("-l", dest="minSVlen", type=int, default=None,
                        help="this record are keep, if the length of SV is great than SVlen, default output all")
    parser.add_argument("-L", dest="maxSVlen", type=int, default=None,
                        help="this record are keep, if the length of SV is less than SVlen, default output all")
    parser.add_argument("-n", dest="SVread", type=int, default=None,
                        help="this record are keep, if the number of read supporting SV is great than SVread")
    parser.add_argument("-d", dest="dected", type=int, default=None,
                        help="get vcf line containing the genotype; 0 rep (0,0), 1 rep (1,0) or (0,1) and 2 rep (1,1).")
    parser.add_argument("-c", dest="comman", default=None, action="store_true",
                        help="get vcf line that dected both in minimap2 and ngmlr")
    args = parser.parse_args()

    ## infile
    vcffile = pysam.VariantFile(args.vcffile, 'r')

    ## outvcf
    outvcf = pysam.VariantFile(args.out_vcf, "w", header=vcffile.header)

    ##fliter
    for vcfrecord in vcffile:
        is_write = [True]

        ## is high quality SV
        if args.is_high_quality:
            is_write.append(True) if vcfrecord.filter.keys()[0] != "UNRESOLVED" else is_write.append(False)

        ## info filter
        infodict = dict(vcfrecord.info.items())
        # is PRECISE SV
        if args.is_PRECISE:
            is_write.append(True) if list(infodict.keys())[0] != "IMPRECISE" else is_write.append(False)
        # SVlen filter
        if args.minSVlen:
            is_write.append(True) if abs(infodict["SVLEN"]) >= args.minSVlen else is_write.append(False)
        if args.maxSVlen:
            is_write.append(True) if abs(infodict["SVLEN"]) <= args.maxSVlen else is_write.append(False)
        # SVtype filter
        if args.SVtype:
            is_write.append(True) if infodict["SVTYPE"] in args.SVtype.split("-") else is_write.append(False)
        # Read Supporting SV, store in a tuple
        if args.SVread:
            is_write.append(True) if int(infodict["ZMW"][0]) >= args.SVread else is_write.append(False)
        # genotype filter
        if args.dected:
            gt_info = [value["GT"] for value in vcfrecord.samples.values()]
            gt = np.array([i if i != None else 0 for i in chain(gt_info)])
            mgt = (gt >= args.dected).sum()
            is_write.append(True) if mgt else is_write.append(False)
        # the intersect between minimap2 and ngmlr
        if args.comman:
            gt_info = [value["GT"] for value in vcfrecord.samples.values()]
            for g1,g2 in get_spe_len(gt_info,2):
                is_write.append(True) if g1==g2 else is_write.append(False)

        # output
        if all(is_write):
            outvcf.write(vcfrecord)

    outvcf.close()