#! /usr/bin/env python

import re
from JTBio.orthocluster.cluster2syn_block import timeuse
import os.path as op
import argparse
import sys


## ----------------------------------------------
# function
@timeuse
def readSynblock(fr):
    D = dict()
    global N
    for line in open(args.block):
        if not line.strip():
            continue
        elif line.startswith(">"):
            key = line.strip()
            D[key] = []
            N = 0
        else:
            N += 1
            D[key].append([])
            llist = re.split('\.|:|\s',line.strip()) # 负链的-号和坐标S-E之间符号不好区别
            llist = llist[0:2] + llist[2].split("-") + llist[3:]
            D[key][-1].extend(llist)

    return D

def Crdtrim(Str1,End1,Str2,End2):
    """
    :param Str1:
    :param End1:
    :param Str2:
    :param End2:
    :return:
    """
    S1,E1,S2,E2 = int(Str1),int(End1),int(Str2),int(End2)
    Lout = []
    if E1 < S2:
        flag = True
        Lout.extend([flag, str(S2), str(E2), str(S2), str(E2)])
    elif S2 <= E1 <= E2:
        flag = True
        Lout.extend([flag, str(S2), str(E2), str(E1 + 10), str(E2)])
    elif E1 >= E2:
        flag = False
        Lout.extend([flag, str(S2), str(E1), '', ''])
    return Lout


## ------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--block", type=str, help="the block ")
    parser.add_argument("-gn", "--genomefile", type=str, nargs='+',
                        help="the input files the same as orthocluster gn,"
                             "the same order with orthocluster mapping file")
    parser.add_argument("-d", "--dir", type=str, help="the directory of gn files, default current dir")
    args = parser.parse_args()


    ## read in Synblock
    print("read in {}".format(op.abspath(args.block)), file=sys.stderr)
    D = readSynblock(open(args.block))


    # 将每个物种的坐标收集，排序，然后以窗口为2来判断
    DICT = dict()
    for i in range(N):
        Spe = [(key,D[key][i]) for key in D]
        Spe.sort(key=lambda x: (x[-1][1],int(x[-1][2])))

        # 以窗口来比较，只和前面那个坐标比较
        window = []
        for key,(pre,Chr,Str,End,Strand) in Spe:
            if key not in DICT:
                DICT[key] = []
            if not window:  # 如果是当前物种第一个坐标
                DICT[key].append([pre, Chr, Str, End, Strand])
                window.extend([pre,Chr,Str,End,Strand])
            else:
                if Chr == window[1]: # 染色体相等才考虑坐标重叠
                    Lout = Crdtrim(window[2], window[3], Str, End)
                    key_flag,*(other) =  Lout
                    window = [pre, Chr] + other[:2] + [Strand]
                    if key_flag:
                        DICT[key].append([pre,Chr] + other[2:] + [Strand])

                else:
                    DICT[key].append([pre, Chr, Str, End, Strand])
                    window = [pre, Chr, Str, End, Strand]


    # output
    logfw = open("trim_block.log", "w")
    print("OldBlockid","trimBlockid",file=logfw)
    key_sort = sorted(DICT,key=lambda x:int(x[1:]))
    Cnt = 0
    for key in key_sort:
        logfw.write(key + "\t")
        if len(DICT[key]) == N:
            Cnt += 1
            logfw.write(str(Cnt) + "\n")
            print(">", Cnt, sep="")
            for pre,Chr,Str,End,Strand in DICT[key]:
                print(pre, ".", Chr, ":", Str, "-", End, " ", Strand, sep="")
            print("")
        else:
            logfw.write("\n")



