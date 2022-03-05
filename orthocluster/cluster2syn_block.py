#!/usr/bin/env python

import argparse
import time
import sys
import os.path as op

## decorator
def timeuse(func):
    def wrapper(*agrs, **kwargs):
        strtime = time.time()
        res = func(*agrs, **kwargs)
        endtime = time.time()
        print("Info: time elapsed: {0:=>.3f} seconds".format(endtime-strtime), file=sys.stderr)
        return res
    return wrapper


## function
# read in ".cluster"
@timeuse
def readCL(fw):
    """
    Read in .cluster file generate by orthocluster
    :param fw: the infile must be opened
    :return: a dict with one key per cluster
    """
    global N
    D,N,SpeName = {},0,[]
    flag,Collection = False,False
    for line in fw:
        N = N + 1 if line.startswith("Sequence") else N   # N species
        if line.startswith("Sequence"):
            SpeName.append(line.strip().split("\t")[-1].split(".")[0])

        elif line.startswith("CL-"):
            Collection = True
            if flag:
                for i in range(len(SpeName)):
                    exec('''D["{}"].append({})'''.format(key,SpeName[i]))
                flag = False
                ## every CLUSTER one key
                key, *clinfo = line.strip().split()
                D[key] = []
                D[key].append(clinfo)
                ## one key have four list elements
                for Spe in SpeName:
                    exec('{}=[]'.format(Spe))
            else:
                ## every CLUSTER one key
                key,*clinfo = line.strip().split()
                D[key] = []
                D[key].append(clinfo)
                ## one key have four list elements
                for Spe in SpeName:
                    exec('{}=[]'.format(Spe))

        elif not line.strip():
            continue
        elif Collection:
            flag = True
            llist = line.split("\t")
            for i in range(len(SpeName)):
                S,E = i * 6, (i+1)*6
                exec('{}.append({})'.format(SpeName[i],llist[S:E]))

    for i in range(len(SpeName)):
        exec('''D["{}"].append({})'''.format(key,SpeName[i]))

    return D



if __name__=='__main__':
    # parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-CL","--cluster", type=str, help="the orthocluster output file postfix '.cluster'")
    args = parser.parse_args()

    #
    print("read in {}".format(op.abspath(args.cluster)), file=sys.stderr)
    D = readCL(open(args.cluster))

    for i in range(N):
        exec("g{}_genes = []".format(i + 1))

    key_keep = []
    for key in D:
        clinfo,*blockinfo = D[key]
        key_keep.append([])

        for i in range(N):
            exec("g{} = blockinfo[{}]".format(i + 1, i))
            exec("tmp_g{}=[]".format(i + 1))
            exec("tmp_g{}.extend([i[4].strip().strip('*') for i in g{} if i[4].strip().strip('*') != ''])".format(i + 1, i + 1))
            exec(
'''
# 判断每个物种是否和之前的有重叠，有重叠记录0，无重叠记录1
if g{0}_genes:
    if set(tmp_g{1}) & set(g{2}_genes): # intersection set
        key_keep[-1].append(0)
    else:
        g{3}_genes.extend(tmp_g{4})
        key_keep[-1].append(1)
else:
    g{5}_genes.extend(tmp_g{6})
    key_keep[-1].append(1)
            '''.format(i+1,i+1,i+1,i+1,i+1,i+1,i+1))

    ## format output
    for k,key in zip(key_keep,D):
        if sum(k) == N:
            clinfo,*SpesInfo = D[key]
            for i in range(len(SpesInfo)):
                for ele in SpesInfo[i]:
                    geneName = ele[4].strip().strip('*').strip()
                    if geneName:
                        print(key,i,geneName,sep="\t")