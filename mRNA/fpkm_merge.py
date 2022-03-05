#! usr/bin/env python

"""
merge multiple fpkm csv file to one
"""

import os.path as op
import argparse
import collections

def mergefpkm():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_abspath_file", type=str, help="the file containing count file path")
    args = parser.parse_args()

    file_path_list = [line.strip() for line in open(args.input_abspath_file)]

    D = collections.defaultdict(list)
    for abspath in file_path_list:
        for line in open(abspath):
            line_list = line.strip().split()
            key = line_list[0]
            D[key].append(line_list[1])

    # write file to file
    Basename = [op.basename(absfile) for absfile in file_path_list]
    file = open("merged.fpkm", "w")
    print("gene_id",",".join(Basename),sep=",", file=file)

    # write fpkm to file
    for key,value in D.items():
        print(key,",".join(value),sep=",", file=file)

if __name__=='__main__':
    mergefpkm()



