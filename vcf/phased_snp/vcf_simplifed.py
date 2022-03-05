#! usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Simplified phased file that must contain field PS
"""

import sys
import argparse
import gzip


if __name__ == "__main__":
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", dest="vcffile", type=str, required=True, help="the input vcf file, can be .gz file")
    parser.add_argument("--outfile", dest="out_vcf", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output bed file, [ default:stdout]")
    args = parser.parse_args()

    ##infile
    is_gz = True if args.vcffile.endswith("gz") else False
    fh = gzip.open(args.vcffile) if is_gz else open(args.vcffile)
    for line in fh:
        line = line.decode() if is_gz else line

        if line.startswith("#"):
            print(line.strip(), file=args.out_vcf)

        else:
            *rest, INFO, FORMAT, Fvalue = line.strip().split()

            # modified and simplified
            INFO = "."
            F_Fvalue_dict = dict(zip(FORMAT.split(":"),Fvalue.split(":")))

            if "PS" in F_Fvalue_dict:
                FORMAT = "GT" + ":" + "PS"
                Fvalue = F_Fvalue_dict["GT"] + ":" + F_Fvalue_dict["PS"]
            else:
                FORMAT = "GT"
                Fvalue = F_Fvalue_dict["GT"]

            llist = rest + [INFO, FORMAT, Fvalue]
            print("\t".join(llist), file=args.out_vcf)