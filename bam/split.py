#!/usr/bin/env python
import argparse
import pysam

if __name__=='__main__':
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("inBam", required=True, help="the bam file")
    parser.add_argument("--inBed", type=str, help="the bed file")
    parser.add_argument("--chr", type=str, help="the name of chr")
    parser.add_argument("--threads", type = int, help="the cpu numbers to use")
    args = parser.parse_args()

    # preparation data
    samfile = pysam.AlignmentFile(args.inBam, "rb", threads=args.threads)

    #
    # if bed file are given
    if args.inBed:
        for line in open(args.inBed):
            Chr, Start, End = line.strip().split()
            Start = int(Start) - 1
            End = int(End)

            # write out to file, must use pysam write function
            fileWrite = pysam.AlignmentFile("%s.%s-%s.bam" % (Chr, Start, End), "wb", template=samfile, threads=args.threads)
            for read in samfile.fetch(Chr, Start, End):
                fileWrite.write(read)
            fileWrite.close()
    elif args.chr:
        fileWrite = pysam.AlignmentFile("%s.bam" % args.chr, "wb", template=samfile, threads=args.threads)
        for read in samfile.fetch(args.chr):
            fileWrite.write(read)
        fileWrite.close()
