#!/usr/bin/env python
import argparse
import sys
import random


##parameter
parser = argparse.ArgumentParser()
parser.add_argument("--infile", dest="fasta_dict", nargs='?', type=argparse.FileType('r'),
                    default=sys.stdin, help="the samtools faidx output file")
parser.add_argument("--outfile", dest="out_bed", nargs='?', type=argparse.FileType('w'),
                    default=sys.stdout, help="the output bed file")
parser.add_argument("--n", dest="num_region", type=int, default=10,
                    help="the numbers of output bed, [default:10]")
parser.add_argument("--l", dest="region_length", type=int, default=1000,
                    help="the range of region of output bed, [default:1000]")
args = parser.parse_args()


##generate bed
fasta_dict = {Chr:int(Length) for Chr,Length,*_ in (line.strip().split() for line in args.fasta_dict)}

for _ in range(args.num_region):
    seq_name = random.choice([key for key in fasta_dict.keys()])
    seq_len = fasta_dict[seq_name]
    rnd_str = random.randint(1,seq_len)
    rnd_str = rnd_str if rnd_str <= seq_len - args.region_length else seq_len - args.region_length
    print(seq_name, rnd_str, rnd_str + args.region_length, sep="\t")
