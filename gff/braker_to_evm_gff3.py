#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Transforms Braker2 output gff3 to ensure compatibilty with e.g. EvidenceModeler
"""

import argparse
import sys

example = ''' 
#Before
contig07        AUGUSTUS        gene    15008360        15009148        .       -       .       ID=jg33527;Name=jg33527
contig07        AUGUSTUS        mRNA    15008360        15009148        .       -       .       ID=jg33527.t1;Parent=jg33527;Name=jg33527.t1
contig07        AUGUSTUS        CDS     15008360        15008412        0.91    -       2       ID=jg33527.t1.CDS1;Parent=jg33527.t1
contig07        AUGUSTUS        exon    15008360        15008412        .       -       .       ID=jg33527.t1.exon1;Parent=jg33527.t1
contig07        AUGUSTUS        CDS     15008504        15008555        0.86    -       0       ID=jg33527.t1.CDS2;Parent=jg33527.t1
contig07        AUGUSTUS        exon    15008504        15008555        .       -       .       ID=jg33527.t1.exon2;Parent=jg33527.t1
contig07        AUGUSTUS        CDS     15008651        15009148        0.96    -       0       ID=jg33527.t1.CDS3;Parent=jg33527.t1
contig07        AUGUSTUS        exon    15008651        15009148        .       -       .       ID=jg33527.t1.exon3;Parent=jg33527.t1

#After
contig07        AUGUSTUS        gene    15008360        15009148        .       -       .       ID=jg33527;Name=jg33527
contig07        AUGUSTUS        mRNA    15008360        15009148        .       -       .       ID=jg33527.t1;Parent=jg33527;Name=jg33527.t1
contig07        AUGUSTUS        exon    15008360        15008412        .       -       .       ID=jg33527.t1.exon1;Parent=jg33527.t1
contig07        AUGUSTUS        CDS     15008360        15008412        0.91    -       2       ID=cds_of_jg33527.t1;Parent=jg33527.t1
contig07        AUGUSTUS        exon    15008504        15008555        .       -       .       ID=jg33527.t1.exon2;Parent=jg33527.t1
contig07        AUGUSTUS        CDS     15008504        15008555        0.86    -       0       ID=cds_of_jg33527.t1;Parent=jg33527.t1
contig07        AUGUSTUS        exon    15008651        15009148        .       -       .       ID=jg33527.t1.exon3;Parent=jg33527.t1
contig07        AUGUSTUS        CDS     15008651        15009148        0.96    -       0       ID=cds_of_jg33527.t1;Parent=jg33527.t1
'''


def get_opts():
    """ parser parameters
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_gff3", type=str, required=True,
                        help="the Braker2 output gff3 file")
    parser.add_argument("-f", "--filter", default=True, type=bool,
                        help="print only the features gene, mRNA, CDS and exon")
    parser.add_argument("-o", "--output", dest="out", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output GFF3 file, [default:stdout]")
    return parser.parse_args()


def rename_gff3(gff3, fo):
    kp = ["gene", "mRNA", "CDS", "exon"]
    for line in open(gff3):
        ll = line.strip().split()
        feature = ll[2]
        if line.startswith("#"):
            continue
        elif feature == "gene":
            print("\t".join(ll), file=fo)
        elif feature == "mRNA":
            flag = True
            print("\t".join(ll), file=fo)
        elif feature == "CDS":

            ll[8] = "ID=cds_of_" + ".".join(ll[8].split("=")[1].split(".")[:-1]) + ";" + ";".join(ll[8].split(";")[1:])
            cds_store = ll
        elif feature == "exon":
            print("\t".join(ll), file=fo)
            print("\t".join(cds_store), file=fo)

if __name__ == "__main__":
    print("Parser the parameters ...", file=sys.stderr)
    args = get_opts()

    print("Summarizing clusterblast results ...", file=sys.stderr)
    rename_gff3(args.input_gff3, args.out)