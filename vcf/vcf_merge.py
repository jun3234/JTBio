#! usr/bin/env python

"""
Merge two vcf file, the same site from different sample (未完成的脚本)
"""

import sys
import argparse
import pysam


##parameter
def get_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v1","--vcf1", type=str, help="the merged first vcf file")
    parser.add_argument("-v2", "--vcf2", type=str, help="the merged second vcf file")
    parser.add_argument("--outfile", dest="out", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output tidy file, [default:stdout]")
    return parser.parse_args()


##merge vcf header
def mhead(vcf1, vcf2):
    v1 = pysam.VariantFile(vcf1, 'rb', threads=24)
    v2 = pysam.VariantFile(vcf2, 'rb', threads=24)
    t1,t2 = v1.header, v2.header

    t2_sp = [i for i in t2.samples]
    for s in t2_sp:
        t1.samples.add(s)

    return t1.samples.header


##merge two vcf
def vcf_merge(vcf1, vcf2, hd, file=sys.stdout):
    v1 = pysam.VariantFile(vcf1, 'rb', threads=24)
    v2 = pysam.VariantFile(vcf2, 'rb', threads=24)


    ## outvcf
    outvcf = pysam.VariantFile(file, "w",header=hd)

    for rcd1 in v1:
        v2_ft = v2.fetch(rcd1.chrom,start=rcd1.pos -1, end=rcd1.pos)
        for rcd2 in v2_ft:
            print([rcd1.chrom, rcd1.pos, "rcd1"])
            print([rcd2.chrom, rcd2.pos, "rcd2"])
            if rcd1.alts == rcd2.alts:
                print(dir(rcd1.samples))
                for it in rcd1.samples.values():

                    print(dir(it))
                    rcd2.samples.update(rcd1.samples)


                    print(rcd1.samples.update(rcd2.samples))
                    outvcf.write(rcd2)
                    sys.exit("55")


if __name__ == '__main__':
    args = get_opts()
    hd = mhead(args.vcf1, args.vcf2)
    vcf_merge(args.vcf1, args.vcf2, hd, args.out)
