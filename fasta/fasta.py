#! usr/bin/env python

import sys
import pysam
import argparse


##parameter
parser = argparse.ArgumentParser()
parser.add_argument("-I", "--infasta", dest="fasta", required=True, help="the fasta formats file")
parser.add_argument("-o", "--output", dest="out_seq", nargs='?', type=argparse.FileType('w'),
                    default=sys.stdout, help="the output fasta file")
parser.add_argument("-s", "--seq", dest="seq_base", type=str, default=None,
                    help="split sequence with N or other base")
parser.add_argument("--l", dest="region_length", type=int, default=1000,
                    help="the range of region of output bed, [default:1000]")
args = parser.parse_args()


## parameter
infasta = pysam.FastaFile(args.fasta)