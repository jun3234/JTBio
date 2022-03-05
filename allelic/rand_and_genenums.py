#! usr/bin/env python

import os
import os.path as op
import sys
import argparse
import random

parser = argparse.ArgumentParser()
parser.add_argument("dirname", type=str, help="the dirname containing different expression genes ID")
args = parser.parse_args()


diffExpfiles = [op.join(op.abspath(args.dirname),name) for name in os.listdir(args.dirname) if name.endswith(".diff.id") if
                op.isfile(op.join(args.dirname,name))]

Rnd = 199  ##随机生成Rnd次结果，允许重复取样
n = len(diffExpfiles)   ##文件的个数
Nsample=2 ## 至少满足在几个组织中出现
L = [i for i in range(n) if i+1 > (Nsample-1)]

def Returnkey(d=dict(),threshold=2):
    L = []
    for key,value in d.items():
        if value >= threshold:
            L.append(key)
    return L

for i in L:
    file_num = i + 1
    cnt = 0
    L = []
    while cnt <= Rnd:
        D = {}
        sublst = random.sample(diffExpfiles,file_num)
        for idfile in sublst:
            for line in open(idfile):
                key = line.strip()
                if key not in D.keys():
                    D[key] = 0
                    D[key] = D[key] + 1
                else:
                    D[key] = D[key] + 1
        Outlist = Returnkey(D,2)
        cnt += 1
        L.append(str(len(Outlist)))
    print(file_num, "\t".join(L), sep="\t", file=sys.stdout)