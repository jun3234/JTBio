#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Gather all summary outputs to one table
"""

import collections
import sys
import argparse


def get_opts():
    """ parser parameters
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--inputs", type=str, nargs='+', required=True,
                        help="the summary output file")
    parser.add_argument("-o", "--output", dest="out", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output total summary, [default:stdout]")
    return parser.parse_args()


def read_table(fi):
    """ read in antismash summary file
    """
    d = collections.defaultdict(dict)

    for line in open(fi):
        if not line.startswith("q-cluster"):
            lst = line.strip().split("\t")
            q = lst[0]
            s = lst[3]
            if s not in d[q]:
                d[q][s] = []
            d[q][s].append(lst)

    return d


def scluster_index(fi):
    """ calculating index for 's-cluster' in every 'q-cluster'
    """
    d = read_table(fi)
    ind_dict = collections.defaultdict(list)
    for q in d:
        for s in d[q]:
            tmp = []
            cov_init = -1
            for lst in d[q][s]:
                idt, sco, cov = [i for i in map(float, lst[9:12])]
                if not cov == cov_init:
                    tmp.append([idt, sco, cov])
                cov_init = cov

            # 130 means identity > 70% should be considerate in particular
            ind = sum([idt * sco for idt, sco, *_ in tmp]) / sum([130-idt for idt, *_ in tmp])
            ind_dict[q].append((s, ind))

    return ind_dict


def gather_summary(inputs, fo):
    """ exact lines with max index in every 'q-cluster'
    """
    header = ["species", "q-cluster", "start", "end", "s-cluster", "source", "type", "CumBlastScore",
              "query", "subject", "identity", "score", "coverage", "e-value"]
    print("\t".join(header), file=fo)

    # collecting all table records that pass filter
    tmp_unknown = collections.defaultdict()     # other annotations without to 'BGC0001854'
    tmp_known = collections.defaultdict()       # annotate to known database, eg: 'BGC0001854'
    for f in inputs:
        sp = "_".join(f.split("_")[:-1])

        d = read_table(f)
        idict = scluster_index(f)

        for q in d:
            cs = sorted(idict[q], key=lambda x: x[-1])[-1][0]
            for lst in d[q][cs]:
                lst = [sp] + lst
                print("\t".join(lst), file=fo)

                idt = lst[1] + lst[4]
                if lst[4].startswith("BGC00"):
                    if idt not in tmp_known:
                        tmp_known[idt] = lst
                else:
                    if idt not in tmp_unknown:
                        tmp_unknown[idt] = lst

    print("Starting in writing known annotation heatmap table ...", file=sys.stderr)
    fo1 = fo.name + ".known.heatmap.table"
    heatmap_table([v for v in tmp_known.values()], fo1, md="known")

    print("Starting in writing unknown annotation heatmap table ...", file=sys.stderr)
    fo2 = fo.name + ".unknown.heatmap.table"
    heatmap_table([v for v in tmp_unknown.values()], fo2, md="unknown")


def heatmap_table(lists, fo, md="known"):
    """ Generating heatmap table data, count 'type' according 'species'
    """

    # gathering all type
    ts = set()
    for lst in lists:
        if md == "unknown":
            for t in lst[6].strip().split(","):
                ts.add(t)
        if md == "known":
            t = lst[5].strip().split(" / ")[0]
            ts.add(t)

    # counts
    d = collections.defaultdict(dict)
    for lst in lists:
        sp = lst[0]
        if sp not in d:
            for t in ts:
                d[sp][t] = []
        if md == "unknown":
            for ty in lst[6].strip().split(","):
                d[sp][ty].append(1)
        if md == "known":
            ty = lst[5].strip().split(" / ")[0]
            d[sp][ty].append(1)

    # write to stdout
    f = open(fo, "w")
    print(ts, file=sys.stderr)
    f.write("\t" + "\t".join(list(ts)) + "\n")
    for sp in d:
        total = []
        for t in d[sp]:
            total.append(str(sum(d[sp][t])))

        f.write(sp + "\t")
        f.write("\t".join(total) + "\n")


if __name__ == "__main__":
    print("Parser the parameters ...", file=sys.stderr)
    args = get_opts()

    print("Gathering summarizes results ...", file=sys.stderr)
    gather_summary(args.inputs, args.out)
