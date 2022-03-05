#! usr/bin/env python

import sys
import argparse

import JTBio.gff.gff3 as gff

##parameter
parser = argparse.ArgumentParser()
parser.add_argument("-g", dest="gff3_file", type=str, required=True,
                    help="the input gff3 file")
parser.add_argument("-t", dest="include_tab", type=str, required=True,
                    help="the representative tab generate by TBtools")
parser.add_argument("--outfile", dest="out", type=argparse.FileType('w'),
                    default=sys.stdout, help="the output gff3 file, [default:stdout]")
args = parser.parse_args()

## read gff3 file in
GFF = gff.GFF3(args.gff3_file)
GFF.load()

## read representative table generated from TBtools
rep_trans = {}
for line in open(args.include_tab):
    llist = line.strip().split()
    rep_trans[llist[1]] = llist[0]

## write gff3
for gene in rep_trans:
    trans = rep_trans[gene]

    # if gff3 no gene feature and use the mRNA feature
    gene_gff = GFF.gff3[gene] if gene in GFF.gff3.keys() else GFF.gff3[trans]
    for line in gene_gff:
        if line.type == "gene":
            gff.linedata2print(line, fileout=args.out)
        elif line.type == "mRNA":
            if line.attributes["ID"] == trans:
                gff.linedata2print(line, fileout=args.out)
        elif line.type == "CDS" or line.type == "exon":
            if line.attributes["Parent"] == trans:
                gff.linedata2print(line, fileout=args.out)