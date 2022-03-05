#! usr/bin/env python

"""
convert 3dDNA assembly file to agp so that annotation could transfer to FINAL fasta
"""

import sys
import argparse
import re


if __name__ == "__main__":
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", dest="assembly_file", type=str, required = True, help="the input bed file")
    parser.add_argument("-g", dest="gap", default=500, type = int, help="the N number between two contig")
    parser.add_argument("-o", dest="out_agp", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output agp file, [ default:stdout]")
    args = parser.parse_args()

    Dtmp = {}
    seqname = ''
    sum = 0
    Chrnum = 0
    for line in open(args.assembly_file):

        ## read in contig info
        if line.startswith(">"):
            findout = re.findall(r'>([^:]*).*\s(\d+)\s(\d+)', line.strip())
            ctg_name, id, Len = findout[0]
            sum = 0 if ctg_name != seqname else sum
            Dtmp[id] = (ctg_name, sum + 1, sum + int(Len), int(Len))
            sum = int(Len) + sum
            seqname = ctg_name

        ## write to agp
        else:
            Chrnum += 1
            Str = 0
            cnt = 0
            llist = line.strip().split()
            for frag_id in llist:
                cnt += 1
                Strain = "-" if frag_id.startswith("-") else "+"
                frag_id = str(abs(int(frag_id)))
                ctg_name, ctg_str, ctg_end, Len = Dtmp[frag_id]
                Cum_Chr_Str = Str + 1
                Cum_Chr_End = Str + Len
                print("HiC_scaffold_%s" % Chrnum, Cum_Chr_Str, Cum_Chr_End, cnt, "W", ctg_name, ctg_str, ctg_end, Strain, sep="\t", file=args.out_agp)
                flag = False if frag_id == str(abs(int(llist[-1]))) else True
                if flag:
                    cnt += 1
                    print("HiC_scaffold_%s" % Chrnum, Cum_Chr_End + 1, Cum_Chr_End + args.gap, cnt, "U", args.gap, "contig", "yes", "map", sep="\t", file=args.out_agp)
                    Str = Cum_Chr_End + args.gap
                else:
                    Str = Cum_Chr_End

