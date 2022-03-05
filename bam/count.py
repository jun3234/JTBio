#!/usr/bin/env python
import argparse
import pysam

def count(*bed):
    Chr,Star,End = bed
    Star = int(Star)
    End = int(End)
    Count_out = samfile.count(Chr, Star, End)       # get count
    mod_bed = [Chr, Star, End, Count_out] + bed[3:]     # insert 'count_out' into raw list
    return mod_bed

if __name__=='__main__':
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("inBam", required=True, help="the bam file")
    parser.add_argument("--inBed", type=str, help="the bed file, first three colunm are 'contig, Start, End'")
    parser.add_argument("--threads", type = int, help="the cpu numbers to use")
    args = parser.parse_args()

    # preparation data
    samfile = pysam.AlignmentFile(args.inBam, "rb", threads=args.threads)

    # call count function
    for line in args.inBed:
        bed = line.strip().split()
        cnt_bed = count(*bed)
        print(*cnt_bed, sep = "\t")