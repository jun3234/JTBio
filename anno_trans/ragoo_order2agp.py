#! usr/bin/env python

"""
convert the output directory 'orderings.txt' assembly files to agp so that annotation could transfer to FINAL fasta
"""

import os
import sys
import argparse
import os.path as op


if __name__ == "__main__":
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", dest="ragoo_out_dir", type=str, required = True,
                        help="the RaGOO assembler output directory containg orderings")
    parser.add_argument("-f", "--fai", dest="ctg_fai", required=True, type=str,
                        help="the faidx of contigs, can be generated bu samtools faidx")
    parser.add_argument("-g", dest="gap", default=500, type = int,
                        help="the N number between two contig. [500]")
    parser.add_argument("-o", dest="out_agp", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output agp file, [ default:stdout]")
    args = parser.parse_args()


    # read in faidx
    fai = dict([(line.strip().split()[0], int(line.strip().split()[1])) for line in open(args.ctg_fai)])

    # lookup ordering.txt file
    ord_dir = op.join(op.abspath(args.ragoo_out_dir),"orderings")
    files = [op.join(ord_dir, name) for name in os.listdir(ord_dir)
             if name.endswith("_orderings.txt")
             if op.isfile(op.join(ord_dir, name))]

    # generate agp file
    for file in files:
        Chr_name = op.split(file)[-1].strip("_orderings.txt") + "_RaGOO"
        Chr_contain_ctg_num = sum([1 for line in open(file)])   # stat a file containing how many contigs
        cum_str = 0
        cnt = 0

        for line in open(file, "r"):
            ctg_name, strand, *_ = line.strip().split()
            if "misasm_break" not in ctg_name:
                ctg_len = fai[ctg_name]
                ctg_str = 1
                ctg_end = ctg_len
            else:
                ctg_name, crd_region = ctg_name.split("_misasm_break:")
                ctg_str = int(crd_region.split("-")[0]) + 1
                ctg_end = int(crd_region.split("-")[1])
                ctg_len = ctg_end - ctg_str + 1

            # print contig part
            cnt += 1
            print(Chr_name, cum_str + 1, cum_str + ctg_len, cnt, "W",
                  ctg_name, ctg_str, ctg_end, strand, sep="\t", file=args.out_agp)
            cum_str = cum_str + ctg_len

            # print gap part
            if (2 * Chr_contain_ctg_num - 1)  == cnt:
                continue
            else:
                cnt += 1
                print(Chr_name, cum_str + 1, cum_str + args.gap, cnt, "U",
                      args.gap, "contig", "yes", "map", sep="\t", file=args.out_agp)

            cum_str = cum_str + args.gap
