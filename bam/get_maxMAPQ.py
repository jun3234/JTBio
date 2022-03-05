#!/usr/bin/env python
import argparse
import pysam
import sys

if __name__=='__main__':
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("--inBam", type = str, help="the sam file, default [stdin]")
    parser.add_argument("--threads", type = int, help="the cpu numbers to use")
    parser.add_argument("--out", type=str, help="the name of output bam, default [stdout]")
    args = parser.parse_args()

    #init para
    cpu = args.threads if args.threads else 2
    # preparation data
    inBam = sys.stdin if not args.inBam else args.inBam
    samfile = pysam.AlignmentFile(inBam, "rb", threads=cpu, require_index=False)

    ##ouput para
    outBam = sys.stdout if not args.out else args.out
    fw = pysam.AlignmentFile(outBam, "wb", template=samfile, threads=cpu)

    ## sam file must sort according to qname
    tmp = {}
    for read in samfile.fetch(until_eof=True):
        if read.qname in tmp:
            if read.mapping_quality > tmp[read.qname]:
                tmp[read.qname] = read.mapping_quality
                bestRead = read
        else:
            if tmp:
                fw.write(bestRead)
                tmp = {}
            tmp[read.qname] = read.mapping_quality
            bestRead = read