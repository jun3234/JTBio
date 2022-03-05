#! /usr/bin/env python

import sys
import argparse

def perm(item=list()):
    n = len(item)
    if n == 1:
        for v in item[0]:
            yield str(v)
    else:
        for v in item[0]:
            res = item[1:]
            for p in perm(res):
                yield str(v) + "\t" + str(p)


if __name__=='__main__':
    # parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-Kmin","--keepmin", type=str, help="the same digit with Species in Orthogroups.tsv, "
                                                      "three species, like 2-2-2, default=0")
    parser.add_argument("-Kmax","--keepmax", type=str, help="the same digit with Species in Orthogroups.tsv, "
                                                      "three species, like 5-5-5, default=9999")
    parser.add_argument("-f", type=str, help="the line of Orthogroups.tsv ", nargs='?', default=sys.stdin)
    args = parser.parse_args()


    ## read in line
    if isinstance(args.f, str):
        ID = [i.replace("\r\n","") for i in open(args.f)]
    else:
        ID = [i.replace("\r\n","") for i in args.f]


    ## keep ref
    for line in ID:
        llist = line.split("\t")
        famNum = llist[0]

        ## keep genes if the count > specified num
        n = len(famNum[1:])
        kminlist = [int(i) for i in args.keepmin.split("-")] if args.keepmin else [0] * n
        kmaxlist = [int(i) for i in args.keepmax.split("-")] if args.keepmax else [9999] * n


        ## store gene that meet the conditions
        tmp = []
        Spes = llist[1:]
        meetCon = []
        for i in range(len(Spes)):
            if  Spes[i] == '':
                Spegene = [gene.strip() for gene in Spes[i].split(",") if gene.strip() != '']
                meetCon.append(1) if kminlist[i] <= len(Spegene) <= kmaxlist[i] else meetCon.append(0)
                Spegene = ['noGene']
            else:
                Spegene = [gene.strip() for gene in Spes[i].split(",") if gene.strip() != '']
                meetCon.append(1) if kminlist[i] <= len(Spegene) <= kmaxlist[i] else meetCon.append(0)

            tmp.append(Spegene)

        if sum(meetCon) == len(Spes):
            # formats list to data
            p = perm(tmp)
            for i in p:
                print("\t".join(i.split()))
