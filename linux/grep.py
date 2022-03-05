#!/usr/bin/env python
import argparse
import sys

"""
When the file are too big and too many columns, you can specified column to filter
"""

##parameter
def grep():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=str, help="the file you want grep")
    parser.add_argument("-c", "--col", type=int, nargs='+', help="the id column "
                                                                     "in the file where lines will be exacted")
    parser.add_argument("-i", "--id", type=str, help="the id file",nargs='?', default=sys.stdin)
    args = parser.parse_args()

    # read in id
    if isinstance(args.id, str):
        ID = set([i.strip() for i in open(args.id)])
    else:
        ID = set([i.strip() for i in args.id])

    ## grep
    for line in open(args.file):
        line_list = line.strip().split()
        mark="\t".join([line_list[i-1] for i in args.col])
        if mark in ID:
            print("\t".join(line_list))

if __name__=='__main__':
    grep()
