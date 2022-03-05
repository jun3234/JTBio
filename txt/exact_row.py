#! usr/bin/env python

"""
table1:
chr1    12  A   B   c
chr2    25  A   C   C

table2:
chr2    25  A   G   F
chr3    36  D   G   F

According the region (union field 1 and 2) in table2 to match table1 field 1 and 2,
and exacting those sublines

    python script.py -f table1, -kf 1,2 -i table2, -ki 1,2
"""

import sys
import argparse
import gzip
import collections


##parameter
def get_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--ffile", type=str, help="the file where lines will be exacted")
    parser.add_argument("-i", "--ifile", type=str, help="the file second vcf file")
    parser.add_argument("--outfile", dest="out", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output tidy file, [default:stdout]")
    return parser.parse_args()