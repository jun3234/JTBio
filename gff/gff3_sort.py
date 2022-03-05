#! usr/bin/env python

import sys
import argparse

import JTBio.gff.gff3 as gff


##parameter
parser = argparse.ArgumentParser()
parser.add_argument("-g", dest="gff3_file", type=str, required=True,
                    help="the input gff3 file")
parser.add_argument("-in", dest="include", type=str,
                    help="the gene or mRNA id you want to keep")
parser.add_argument("-ex", dest="exclude", type=str,
                    help="the gene or mRNA id you want not to keep")
parser.add_argument("--outfile", dest="out", type=argparse.FileType('w'),
                    default=sys.stdout, help="the output gff3 file, [default:stdout]")
args = parser.parse_args()


# parameter
iid = [line.strip() for line in open(args.include)] if args.include else []
eid = [line.strip() for line in open(args.exclude)] if args.include else []

## read in gff3
GFF = gff.GFF3(args.gff3_file)
GFF.load()  # store in GFF.gff3 attribute

## get sorted chrs name
sorted_chrs = gff.sort_seqname(GFF.mcgff)


for chr in sorted_chrs:
    chr_list = GFF.mcgff[chr]
    chr_list.sort(key=lambda x: int(x[2]))  # sort gene start coord in one chromosome

    for ele in chr_list:
        gene = ele.gene

        flag = [True]   # condition to keep that gene
        if iid:
            flag.append(True) if gene in iid else flag.append(False)
        if eid:
            flag.append(True) if gene not in eid else flag.append(False)

        #output gene
        if any(flag):
            for ele in GFF.gff3[gene]:
                gff.linedata2print(ele, fileout=args.out)