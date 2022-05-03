#! usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
sort, filter and rename gff file
"""

import sys
import argparse
import JTBio.gff.gff3 as gff


# parameter
parser = argparse.ArgumentParser()
parser.add_argument("-g", dest="gff3_file", type=str, required=True,
                    help="the input gff3 file")
parser.add_argument("-i", dest="include", type=str,
                    help="the gene or mRNA id you want to keep")
parser.add_argument("-e", dest="exclude", type=str,
                    help="the gene or mRNA id you want not to keep")
parser.add_argument("-r", dest="rename", type=str, default=None,
                    help="the new prefix of gene or mRNA id")
parser.add_argument("-o", "--outfile", dest="out", type=argparse.FileType('w'),
                    default=sys.stdout, help="the output gff3 file, [default:stdout]")
args = parser.parse_args()


# parameter
iid = [line.strip() for line in open(args.include)] if args.include else []
eid = [line.strip() for line in open(args.exclude)] if args.include else []

# read in gff3
GFF = gff.GFF3(args.gff3_file)
GFF.load()  # store in GFF.gff3 attribute

# get sorted chrs name
sorted_chrs = gff.sort_seqname(GFF.mcgff)
gn = 0
for chr in sorted_chrs:
    chr_list = GFF.mcgff[chr]
    chr_list.sort(key=lambda x: int(x[2]))  # sort gene start coord in one chromosome

    for ele in chr_list:
        gene = ele.gene

        flag = [True]  # condition to keep that gene
        if iid or eid:  # filter mode
            if iid:
                flag.append(True) if gene in iid else flag.append(False)
            if eid:
                flag.append(True) if gene not in eid else flag.append(False)

        if any(flag):   # output gene
            gn += 1
            mn = en = cn = 0
            for line in GFF.gff3[gene]:
                mn = mn + 1 if line.type == "mRNA" else mn
                en = en + 1 if line.type == "exon" else en
                cn = cn + 1 if line.type == "CDS" else cn
                ntuple = (gn, mn, en, cn)
                line = gff.gene_rename(line, args.rename, ntuple)
                gff.linedata2print(line, fileout=args.out)
