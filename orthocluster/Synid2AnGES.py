#! /usr/bin/env python

import argparse
import os
import os.path as op
from JTBio.orthocluster.cluster2syn_block import timeuse
import sys


# read in block
@timeuse
def readBlockid(fr):
    DICT = dict()

    Star = 0
    for line in fr:
        key,Spe,GeneName = line.strip().split()

        if key not in DICT:
            DICT[key] = []
            DICT[key].append([])
            DICT[key][-1].append(GeneName)
        else:
            if int(Spe) == Star:
                DICT[key][-1].append(GeneName)
            else:
                DICT[key].append([])
                DICT[key][-1].append(GeneName)

        Star = int(Spe)

    return DICT


def gff2region(gfflist=list()):
    tmp = [[],[],[]]
    for bedlist in gfflist:
        gene,Chr,Str,End,Strand = bedlist
        tmp[0].append(Chr.split("_")[-1])
        tmp[1].extend([int(Str),int(End)])
        tmp[2].append(int(Strand))

    ## out
    Chr,Str,End = tmp[0][0],min(tmp[1]),max(tmp[1])
    Strand = '+' if sum(tmp[2]) >= 0 else '-'

    return [Chr,Str,End,Strand]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--block", type=str, help="the block ")
    parser.add_argument("-gn", "--genomefile", type=str, nargs='+', help="the input files the same as orthocluster gn,"
                                                              "the same order with orthocluster mapping file")
    parser.add_argument("-d", "--dir", type=str, help="the directory of gn files, default current dir")
    args = parser.parse_args()

    # parameter
    ## abspath of gn files
    gndir = os.getcwd() if not args.dir else op.abspath(args.dir)
    gnfiles = [op.join(gndir,gn) for gn in args.genomefile]
    outPrefix = [i.split(".")[0] for i in args.genomefile]

    #
    print("read in {}".format(op.abspath(args.block)), file=sys.stderr)
    DICT = readBlockid(open(args.block))

    D_Nblock = {}
    for key in DICT: # 物种有多个区块
        N = len(DICT[key])
        out_tmp = {}
        out_tmp[key] = []

        for i in range(N): # 每个区块有N个物种
            out_tmp[key].append([])
            tmp = []

            for line in open(gnfiles[i]):  # 每个区块每个物种遍历一次gn文件，统计信息
                llist = line.strip().split()
                gene,*other = llist
                if gene in DICT[key][i]:
                    tmp.append(llist)

            # 合并N个物种某个区块的计算结果
            bed_list = gff2region(tmp)
            out_tmp[key][-1].append(args.genomefile[i].split(".")[0])
            out_tmp[key][-1].extend(bed_list)

        # 收集所有区块
        Skey = ">" + key.split("-")[-1]
        D_Nblock[Skey] = []
        D_Nblock[Skey].extend(out_tmp[key])

    # 对ref,也就是第一个物种按染色体和坐标排序
    ZIP_list = [[key,value] for key,value in D_Nblock.items()]
    ZIP_list.sort(key=lambda x:(x[1][0][1],int(x[1][0][2])))
    # 格式化输出
    for i in range(len(ZIP_list)):
        print(">", i+1, sep="")
        block = ZIP_list[i]
        for pre,Chr,Str,End,Strand in block[-1]:
            print(pre, ".", Chr, ":", Str, "-", End, " ", Strand, sep="")
        print("")
