#! usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import pysam
import argparse
import functools

##function
def form(e, n):
    if not isinstance(n, int):
        raise  Exception("digit must be int")

    e = float(e)
    s = "{:.%sf}" % n
    rs = s.format(e)
    return rs

#partional, n is equal to significant digit in STD_quant_star
form = functools.partial(form, n=6)

if __name__ == "__main__":
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", dest="vcffile", type=str, required=True,
                        help="the input vcf file")
    parser.add_argument("--outfile", dest="out_vcf", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output vcf file, [ default:stdout ]")
    parser.add_argument("-s", dest="supporting_info", type=str, required=True,
                        help="The file recored supporting SV read nums")
    args = parser.parse_args()


    ## invcf
    invcf = pysam.VariantFile(args.vcffile,'r')
    ## supporting info dict
    tmp = dict()
    dup_kep = dict()
    for line in open(args.supporting_info):
        chr, pos, ZMW, *STD = line.strip().split()
        key = (chr, pos)
        info = [ZMW] + list(map(form, STD))

        if key in tmp:
            if int(tmp[key][0]) > int(info[0]):
                dup_kep[key] = tmp[key]
            elif int(tmp[key][0]) < int(info[0]):
                dup_kep[key] = info
            elif int(tmp[key][0]) == int(info[0]):
                if sum(map(float,tmp[key][1:])) > sum(map(float, info[1:])):
                    dup_kep[key] = info
                else:
                    dup_kep[key] = tmp[key]

        else:
            tmp[key] = info

    ## outvcf
    outvcf = pysam.VariantFile(args.out_vcf, "w", header=invcf.header)

    ## removed duplicate SV calls from Sniffles
    # Sniffles frequently called multiple SVs at the same position.
    # In these cases, we kept the SV with the most supporting reads.
    for rcd in invcf:
        key = (rcd.chrom, str(rcd.pos))

        if key in dup_kep:
            ## info filter
            infodict = dict(rcd.info.items())
            sr = "_".join([str(int(infodict["ZMW"][0]))] +
                          list(map(form, [infodict["STD_quant_start"][0],infodict["STD_quant_stop"][0]]))
                          )
            kep_sr = "_".join(dup_kep[key])

            if sr == kep_sr:
                outvcf.write(rcd)
            else:
                print([infodict["STD_quant_start"][0],infodict["STD_quant_stop"][0]], file=sys.stderr)
                print("skip site %s_%s %s !=> %s" % (rcd.chrom, str(rcd.pos), sr, kep_sr), file=sys.stderr)
        else:
            outvcf.write(rcd)

