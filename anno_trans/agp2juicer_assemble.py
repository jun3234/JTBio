#! usr/bin/env python

"""
convert agp to 3dDNA assembly file so that Juicer Box Analysis Tools can use to manual curate
"""

import sys
import argparse
from collections import defaultdict


if __name__ == "__main__":
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", dest="agp_file", type=str, required = True, help="the input agp file")
    parser.add_argument("-o", dest="out_assembly", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output agp file, [ default:stdout]")
    args = parser.parse_args()

    ##
    asm = defaultdict(list)
    id = 0
    Start_group = ''
    for line in open(args.agp_file):
        group, *_, sign, ctg_name, ctg_Str, ctg_End,  Strand = line.strip().split()
        if sign == "W":
            id += 1
            ctg_Len = int(ctg_End) - int(ctg_Str) + 1

            print(">" + ctg_name, id, ctg_Len, sep=" ", file=args.out_assembly)
            Strand = '' if Strand == "+" else '-'
            asm[group].append(Strand + str(id))

    ##write assemble info
    for key in asm.keys():
        print(" ".join(asm[key]), file=args.out_assembly)