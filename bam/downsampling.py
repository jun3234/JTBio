#! usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Downsampling fq file to target depth
"""

import sys
import pysam
import argparse
from random import random


##parameters
def get_opts():
    """ parse parameters
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--bam", type=str, help="the input bam file")
    parser.add_argument("-g", "--genome", type=int, default=500,
                        help="the reference genome size (M)")
    parser.add_argument("-d", "--depth", type=int, default=30,
                        help="the target coverage depth")
    parser.add_argument("-r", "--ratio", type=float, default=0.6,
                        help="the sample ratio")
    parser.add_argument("-o", "--output", dest="out", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output fq.gz file, [default:stdout]")
    return parser.parse_args()


def bam_summary(bam):
    """ Quickly get count and Total Base data
    """
    inbam = pysam.AlignmentFile(bam, "rb", threads=16, require_index=True)

    statis = tuple()
    for name in inbam.references:
        count = inbam.count(contig=name)
        qlens = []
        for rd in inbam.fetch(contig=name):
            qlens.append(rd.qlen)

        print([name, count, sum(qlens)])
        statis = statis + tuple([name, count, sum(qlens)])

    return statis


def det_sampling_per(genome, depth, statis):
    """ Defined down-sampling ratio
    """
    total_base = sum(i[-1] for i in statis)
    ratio = (genome*1000000*depth)/total_base
    return ratio


def downsampling(bam, ratio, outfile):
    """ Random down-sampling
    """
    inbam = pysam.AlignmentFile(bam, "rb", require_index=True)
    outbam = pysam.AlignmentFile(outfile, "wb", header=inbam.header, threads=4)

    for name in inbam.references:
        for rd in inbam.fetch(contig=name):
            r = random()    # a float between 0 and 1
            if r <= ratio:
                outbam.write(rd)

    outbam.close()

if __name__=='__main__':
    args = get_opts()
    downsampling(args.bam, args.ratio, args.out)
    # create index
    pysam.index(args.out.name)



