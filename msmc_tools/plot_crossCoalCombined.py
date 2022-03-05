#! usr/bin/env python

import sys
import argparse

from JTBio.msmc_tools import plot_utils


##
##parameter
def get_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p1", "--pop1", type=str, help="the msmc out within population1")
    parser.add_argument("-p2", "--pop2", type=str, help="the msmc out within population2")
    parser.add_argument("-p12", "--pop12", type=str, help="the msmc out cross population1 and population2")
    parser.add_argument("-m", "--mu", type=float, default=1.25e-8,
                        help="the mutations per base per generations")
    parser.add_argument("-g", "--gn", type=int, default=10,
                        help="the years of generations time")
    parser.add_argument("--out_table", dest="out", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output tidy file, [default:stdout]")
    return parser.parse_args()


if __name__ == '__main__':
    args = get_opts()
    x, y = plot_utils.crossCoalPlotCombined(args.pop1,args.pop2,args.pop12,mu=args.mu,gen=args.gn)

    ##format out
    print("\t".join(["years", "populations"]), file=args.out)
    for x,y in zip(x, y):
        print(x, y, sep="\t", file=args.out)