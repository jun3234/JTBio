#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Expanded taxonomy strings to 7 columns, 'unknown' and null strings were replaced by 'NA'
"""

import sys
import argparse


##parameters
def get_opts():
    """ parse parameters
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--table", type=str, help="the input biom table with taxonomy")
    parser.add_argument("-o", "--output", dest="out", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output count matrix, [default:stdout]")
    return parser.parse_args()

# tax split to 7 levels
def expanded_tax(table, fo):
    """ Spliting taxonomy to seven levels
    """

    sign = ["d__", "p__", "c__", "o__", "f__", "g__", "s__"]
    for line in open(table):
        char = []
        if line.startswith("#"):
            head = ['Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species']
            print("\t".join(head), line.strip(), sep="\t", file=fo)
        else:
            tax = line.strip().split("\t")[-1]
            lst = tax.split("; ")
            for i in sign:
                l = [w for w in lst if w.startswith(i)]
                cs = l[0] if l else i + "NA"
                char.append(cs)

            print("\t".join(char), line.strip(), sep="\t", file=fo)


if __name__ == '__main__':
    print("Parser the parameters ...", file=sys.stderr)
    args = get_opts()

    print("Spliting the taxonomy columns ...", file=sys.stderr)
    expanded_tax(args.table, args.out)
