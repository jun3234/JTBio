#! usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Merge two simplified vcf to one according tuple (Chr, Start), like that:

#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	10x_fzx
Chr1	16	.	G	T	524.77	PASS	.	GT:PS	0|1:1
Chr1	39	.	T	C	821.77	PASS	.	GT:PS	1|0:1
Chr1	56	.	C	A	767.77	PASS	.	GT:PS	1|0:1
Chr1	112	.	A	G	670.77	PASS	.	GT:PS	0|1:1
Chr1	122	.	G	A	717.77	PASS	.	GT:PS	0|1:1
Chr1	161	.	T	A	448.77	PASS	.	GT:PS	0|1:1
Chr1	201	.	A	G	594.77	PASS	.	GT:PS	0|1:1
Chr1	312	.	C	T	517.77	PASS	.	GT:PS	0|1:1
"""


import sys
from collections import defaultdict
from collections import namedtuple
import argparse


nDict = namedtuple("vcfline", "CHROM POS ID REF ALT QUAL FILTER INFO FORMAT FValue")
## read in vcf file, defaultdict(lambda : abaa)
def readvcf(vcf):
    vcf_dict = defaultdict(list)

    for line in open(vcf):
        if line.startswith("#CHROM"):
            header = line.strip().split()
        elif not line.startswith("#"):
            vcfline = nDict(*line.strip().split())
            key = (vcfline.CHROM, vcfline.POS)
            vcf_dict[key] = vcfline

    return (vcf_dict, header)



if __name__ == "__main__":
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-v1", dest="vcffile1", type=str, required=True, help="the input one vcf file, following abovementioned format")
    parser.add_argument("-v2", dest="vcffile2", type=str, required=True, help="the input another vcf file, following abovementioned format")
    parser.add_argument("--outfile", dest="out_vcf", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output vcf file, [ default:stdout]")
    args = parser.parse_args()

    ##infile
    v1_dt,h1 = readvcf(args.vcffile1)
    v2_dt,h2 = readvcf(args.vcffile2)

    ##merge and sort all key, including key1 and key2, key maybe string like: (Chr1,16),(Chr1,52),...,(Chr15,16)
    key1 = [key for key in v1_dt]
    key2 = [key for key in v2_dt]
    keylist = list(set(key1 + key2))
    keylist.sort(key=lambda x: (int(x[0][3:]), int(x[-1])))

    ##get line data
    print("\t".join(h1[:3] + h1[3:] + h2[3:]), file=args.out_vcf)
    for CHROM, POS in keylist:
        key = (CHROM, POS)

        v1_line = v1_dt[key]
        if not v1_line:
            ## 4 pos: REF ALT QUAL FILTER INFO FORMAT sample1
            v1_out = (".",) * 7
        else:
            v1_out = v1_line[3:]

        v2_line = v2_dt[key]
        if not v2_line:
            ## 4 pos: REF ALT QUAL Fvalue
            v2_out = (".",) * 7
        else:
            v2_out = v2_line[3:]

        line_pref = v1_line[:3] if len(v1_line) >= len(v2_line) else v2_line[:3]

        print("\t".join(line_pref + v1_out + v2_out), file=args.out_vcf)

