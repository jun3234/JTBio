#! usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import re
import os
from collections import defaultdict


## define function
def condition(L1=list(), L2=list()):
    """ figure out two region A (s1,e1) and B(s2,e2) overlap condition
    """
    s1, e1, r1 = list(L1)
    s2, e2, r2 = list(L2)

    if s1 < s2:
        if e1 < s2:
            return "no_over", (s1, e1, r1), (s2, e2, r2)
        elif (e1 >= s2) & (e1 <= e2):
            return "overlap", (s1, e1, r1), (s2, e2, r2)
        elif e1 > e2:
            return "contain", (s1, e1, r1), (s2, e2, r2)
    elif s1 >= s2:
        if e1 < e2:
            return "contain",(s2, e2, r2),(s1, e1, r1)
        elif (e1 >= e2) & (s1 <= e2):
            return "overlap",(s2, e2, r2),(s1, e1, r1)
        elif s1 > e2:
            return "no_over",(s2, e2, r2),(s1, e1, r1)


def read_bed(bedfile,rank=None):
    """ load bed file and store according Chr-start
    """
    dedict = defaultdict(list)

    for line in open(bedfile):
        chr, start,end,*rest_list = line.strip().split()
        if rank:
            dedict[chr].append((int(start),int(end),rank))
        else:
            dedict[chr].append((int(start), int(end)))
    return dedict


def bed_cat(onbedfile, anbedfile, type="union"):
    """ cat two bed to one dict
    """
    mergedict = defaultdict(list)
    if type == "union":
        chrs = set(onbedfile.keys()) | set(anbedfile.keys())
    elif type == "intersect":
        chrs = set(onbedfile.keys()) & set(anbedfile.keys())
    elif type == "difference":
        chrs = set(onbedfile.keys())

    for chr in chrs:
        mergedict[chr].extend(onbedfile[chr])
        mergedict[chr].extend(anbedfile[chr])
    return mergedict


def bed_sort(bedfile_dict):
    """ sort bed file according chromosome-start, return tuple (chrs_sorted, bedfile_dict)
    """
    # sort chr
    chrs = [key for key in bedfile_dict.keys()]
    pattern = re.compile(r'(.*?)(\d+$)')

    chr_tuple = []
    for chr in chrs:
        flist = pattern.findall(chr)
        if flist:
            chr_tuple.append(flist[0])
        else:
            chr_tuple.append((chr,'999999'))

    chr_tuple.sort(key=lambda x:(x[0],int(x[1])))
    chrs_sorted = [ i+j if j!="999999" else i for i,j in chr_tuple ]

    # sort start coord
    for key in chrs:
        bedfile_dict[key].sort(key=lambda x:x[0])

    # return
    return chrs_sorted, bedfile_dict


## class

class bedFile:
    """ record bedfile relate info
    """
    filenum = 0
    def __init__(self, infile):
        bedFile.filenum += 1
        self.path = os.path.abspath(infile)
        self.load = read_bed(infile,self.filenum)
