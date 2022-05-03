#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Summary antismash output to a table
"""

import sys
import os
import re
import argparse


def get_opts():
    """ parser parameters
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_dir", type=str, required=True,
                        help="the antismash output dir")
    parser.add_argument("-o", "--output", dest="out", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output count matrix, [default:stdout]")
    return parser.parse_args()


def clustertxt_parser(file):
    """ parser cluster table, exact infos from this
    """
    rflag = False
    pflag = False
    cnt = 0
    tmp = []
    for line in open(file):
        line = line.strip()
        if line.startswith(">>"):
            rflag = True
            cnt += 1
        if rflag:
            if line.startswith(f'{cnt}.'):
                scluster = line.split()[1]
            elif line.startswith("Source"):
                source = line.replace("Source: ", "")
            elif line.startswith("Type:"):
                typ = line.replace("Type: ", "")
            elif line.startswith("Cumulative"):
                cumblastscore = line.split()[-1]

            elif line.startswith("Table of Blast hits"):
                pflag = True

            elif pflag:
                if line:
                    llist = line.split()
                    tmp.append([scluster, source, typ, cumblastscore] + llist)
                elif not line:
                    pflag = False
                    rflag = False

    return tmp


def clusterblast_summary(inpath, fo):
    """ gather cluster blast out tables, then read tables and summarize it
    """

    gbks = [os.path.join(inpath, file) for file in os.listdir(inpath) if file.endswith(".gbk") if "region" in file]
    header = ["q-cluster", "start", "end", "s-cluster", "source", "type", "CumBlastScore",
              "query", "subject", "identity", "score", "coverage", "e-value"]
    print("\t".join(header), file=fo)
    for file in gbks:
        print(file, file=sys.stderr)
        # corresponding blast file name
        prefix = ".".join(os.path.basename(file).split(".")[:-2])     #eg: file="'M1_test/M1_chr1.region003.gbk"
        num = int(re.findall(r'\d+', file.split(".")[-2])[0])
        txt = f'{prefix}_c{num}.txt'

        # get cluster coord from gbk file
        for line in open(file):
            line = line.strip()
            if line.startswith("Orig. start"):      # eg: s="Orig. start  :: 3933677"
                start = int(re.findall(r'\d+$', line)[0]) + 1
            if line.startswith("Orig. end"):        # eg: s="Orig. end    :: >3981358"
                end = int(re.findall(r'\d+$', line)[0])
                break

        # get significant hits 'clusterblast'
        c_abspath = os.path.join(inpath, "clusterblast", txt)
        print(c_abspath, file=sys.stderr)
        lists = clustertxt_parser(c_abspath)
        for lst in lists:
            l = [txt.rstrip(".txt"), str(start), str(end)] + lst
            print("\t".join(l), file=fo)

        # get significant hits from 'knownclusterblast'
        k_abspath = os.path.join(inpath, "knownclusterblast", txt)
        print(k_abspath, file=sys.stderr)
        lists = clustertxt_parser(k_abspath)
        for lst in lists:
            l = [txt.rstrip(".txt"), str(start), str(end)] + lst
            if l:
                print("\t".join(l), file=fo)


if __name__ == "__main__":
    print("Parser the parameters ...", file=sys.stderr)
    args = get_opts()

    print("Summarizing clusterblast results ...", file=sys.stderr)
    clusterblast_summary(args.input_dir, args.out)






