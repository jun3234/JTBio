#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Get infos from `angsd` sfs file, and generating `stairwayPlot` blueprint config.
"""

import sys
import argparse


# parameters
def get_opts():
    """ parse parameters
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--sfs", type=str, required=True,
                        help="the SFS file from angsd")
    parser.add_argument("-p", "--ploidy", type=int, default=2,
                        help="the ploidy of individuals sample. [2]")
    parser.add_argument("-f", "--fold", type=str, default="false",
                        help="whether the SFS is folded 'true' or unfolded 'false'. [false]")
    parser.add_argument("-m", "--mu", type=float, default=1e-8,
                        help="assumed mutation rate per site per generation. [1e-8]")
    parser.add_argument("-t", "--gt", type=float, default=10,
                        help="assumed generation time (in years). [10]")
    parser.add_argument("-o", "--output", dest="out", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output count matrix, [default:stdout]")
    return parser.parse_args()


# get nseq, sfs = 2N + 1
def parser_sfs(sfs_file):
    """ from SFS file get (L, nseq, sfs_list)
    """
    lst = [line.strip().split() for line in open(sfs_file)][0]

    n = len(lst) - 1
    l, *sfs = lst
    l = int(float(l))

    return n, l, sfs


# print blue_print file
def blue_print(nseq, l, sfs, args, fo):
    """ Print blue_print file
    """
    fn = ".".join(args.sfs.split("/")[-1].split(".")[:-1])

    print("popid: %s # id of the population" % fn, file=fo)
    print("nseq: %s  # number of sequences" % nseq, file=fo)
    print("L: %s # total number of observed nucleic sites" % l, file=fo)
    print("whether_folded: %s # SFS is folded (true or false)" % args.fold, file=fo)
    print("SFS: ", "\t".join(sfs[:-1]), sep="", file=fo)
    print("#smallest_size_of_SFS_bin_used_for_estimation: 1 # default is 1; to ignore singletons", file=fo)
    print("#largest_size_of_SFS_bin_used_for_estimation: 29 # default is n-1; to ignore singletons", file=fo)
    print("pct_training: %s # percentage of sites for training" % 0.67, file=fo)

    nrand = int((nseq - 2) / 4), int((nseq - 2) / 2), int((nseq - 2) * 3 / 4), int(nseq - 2)
    print("nrand: %s %s %s %s # random break points for each try" % nrand, file=fo)

    print("project_dir: two-epoch.pop.%s # project directory" % fn, file=fo)

    print("stairway_plot_dir: stairway_plot_es # directory to the stairway plot files", file=fo)
    print("ninput: %s # number of input files to be created for each estimation" % 200, file=fo)
    print("#random_seed: %s" % 6, file=fo)
    print("##output setting", file=fo)
    print("mu: {} # assumed mutation rate per site per generation".format(args.mu), file=fo)
    print("year_per_generation: {} # assumed generation time (in years)".format(args.gt), file=fo)

    print("##plot setting", file=fo)
    print("plot_title: pop.%s # title of the plot" % fn, file=fo)
    print("xrange: %s,%s # Time (1k year) range; format: xmin,xmax; '0,0' for default" % (0.1, 10000), file=fo)
    print("yrange: %s,%s # Ne (1k individual) range; format: xmin,xmax; '0,0' for default" % (0, 0), file=fo)
    print("xspacing: %s # X axis spacing" % 2, file=fo)
    print("yspacing: %s # Y axis spacing" % 2, file=fo)
    print("fontsize: %s # Font size" % 12, file=fo)


if __name__ == "__main__":
    args = get_opts()
    n, l, sfs = parser_sfs(args.sfs)
    blue_print(n, l, sfs, args, args.out)
