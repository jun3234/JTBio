#! usr/bin/env python
# -*- coding: UTF-8 -*-

"""
SNPs from 10x pashed and hapcut2 phased were used to mutual confirmation, merged file like:

Chr1    16      .       G       T       30      PASS    .       GT:PS   1|0:1   G       T       524.77  PASS    .       GT:PS   0|1:1
Chr1    39      .       T       C       30      PASS    .       GT:PS   0|1:1   T       C       821.77  PASS    .       GT:PS   1|0:1
Chr1    56      .       C       A       30      PASS    .       GT:PS   0|1:1   C       A       767.77  PASS    .       GT:PS   1|0:1
Chr1    112     .       A       G       30      PASS    .       GT:PS   1|0:1   A       G       670.77  PASS    .       GT:PS   0|1:1
Chr1    122     .       G       A       30      PASS    .       GT:PS   1|0:1   G       A       717.77  PASS    .       GT:PS   0|1:1
Chr1    161     .       T       A       30      PASS    .       GT:PS   1|0:1   T       A       448.77  PASS    .       GT:PS   0|1:1
Chr1    201     .       A       G       30      PASS    .       GT:PS   1|0:1   A       G       594.77  PASS    .       GT:PS   0|1:1
Chr1    312     .       C       T       30      PASS    .       GT:PS   1|0:1   C       T       517.77  PASS    .       GT:PS   0|1:1

And, output report with columns like this:

CHROM   hapcut2_PS	length	10x_PS	length	1_vs_3	1_vs_4	2_vs_3	2_vs_4

"""

import sys
import argparse
import re

from collections import defaultdict


##read in merge vcf
def read_mergervcf(vcf):
    D = defaultdict(list)

    #
    for line in open(args.vcffile):
        llist = line.strip().split()
        Chr, *_, X10 = llist
        key = (Chr, X10.split(":")[-1])
        D[key].append(llist)

    return D


## get haplotype from vcf, have those columns,
## REF, ALT, QUAL, FILTER, INFO, FORMAT, sample

def get_hp(vcf_list):

    REF, ALT, *_, sample = vcf_list
    gt = re.findall(r'(\d)\|(\d)', sample)[0]
    hp1_base = REF if gt[0] == "0" else ALT
    hp2_base = REF if gt[1] == "0" else ALT

    return (hp1_base, hp2_base)

if __name__ == "__main__":
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", dest="vcffile", type=str, required=True, help="the input vcf file, calling from Nextpolish")
    parser.add_argument("--outfile", dest="out_stat", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output bed file, [ default:stdout]")
    args = parser.parse_args()


    ##read in merge vcf file
    vcf_d = read_mergervcf(args.vcffile)

    ##stat and output
    print("#CHROM","hapcut2_PS","length","10x_PS", "length",
          "1_vs_3","1_vs_4","2_vs_3","2_vs_4", "hap1_acu", "hap2_acu" ,sep="\t", file=args.out_stat)
    for key,value in vcf_d.items():
        Chr, X10_id = key

        ##collection haplotype
        hp_hap1 = []; hp_hap2 = []
        x10_hap1 = []; x10_hap2 = []
        for lst in value:
            #hapcut2
            hp_id = lst[9].split(":")[-1]
            hp_list = lst[3:10]
            h1_base,h2_base = get_hp(hp_list)
            hp_hap1.append(h1_base); hp_hap2.append(h2_base)

            #10x genomic
            x10_list = lst[10:]
            h1_base, h2_base = get_hp(x10_list)
            x10_hap1.append(h1_base); x10_hap2.append(h2_base)

        length = len(x10_hap1)

        ##compare pair
        ZP13 = zip(hp_hap1,x10_hap1)
        ZP14 = zip(hp_hap1, x10_hap2)
        ZP23 = zip(hp_hap2, x10_hap1)
        ZP24 = zip(hp_hap2, x10_hap2)

        equal_base = []
        for Pair in (ZP13,ZP14,ZP23,ZP24):
            cnt = 0
            for base1,base2 in Pair:
                cnt = cnt + 1 if base1 == base2 else cnt
            equal_base.append(str(cnt))

        #copy list
        acy = sorted(equal_base,key=lambda x:int(x), reverse=True)
        hap1_acu = round(int(acy[0]) / length * 100, 2)
        hap2_acu = round(int(acy[1]) / length * 100, 2)

        print(Chr, hp_id, str(length), X10_id, str(length), "\t".join(equal_base),
              str(hap1_acu), str(hap2_acu), sep="\t", file=args.out_stat)





