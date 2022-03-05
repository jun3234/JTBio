#! /usr/bin/env python

import sys
import collections
import argparse

import JTBio.gff.gff3 as gff

def cutcount(S1,E1,L = list()):
    Lcp = L.copy()
    Lcp.append(S1)
    Lcp.append(E1)
    Lcp.sort()
    if S1 > E1:
        return 0
    else:
        S1_index = Lcp.index(S1)
        E1_index = Lcp.index(E1)
        Le1cnt = Lcp.count(E1)      # SNP was
        if Le1cnt == 1:
            return E1_index - S1_index - 1
        else:
            return E1_index - S1_index - 1 + Le1cnt - 1

## read in vcf
def read_vcf(vcf):
    D = collections.defaultdict(list)
    for line in open(vcf):

        if line.startswith("#") or not line.strip():
            continue

        Chr,Pos,*rest = line.strip().split()
        D[Chr].append(int(Pos))

if __name__=='__main__':
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("--vcf",type=str,help="the input vcf file")
    parser.add_argument("--gff3", type=str, help="the gff3 formats file")
    parser.add_argument("--type", type=str, help="the feature formats file")
    parser.add_argument("--key", type=str, help="the geneName are show")
    args = parser.parse_args()

    ## read in data
    SNPinfo = read_vcf(args.vcf)
    GFF = gff.GFF3(args.gff3)
    GFF.load()
    gff3 = GFF.gff3
    mcgff = GFF.mcgff

    ## start deal with every gene
    for chr in mcgff.keys():
        for _,key,start,end,strand in mcgff[chr]:

            mRNA_crd = [[int(ele[3]),int(ele[4])] for ele in gff3[key] if ele[2] == "mRNA"]
            CDS_crd = [[int(ele[3]),int(ele[4])] for ele in gff3[key] if ele[2] == "CDS"]

            min_cds = min(i[0] for i in CDS_crd)
            max_cds = max(i[1] for i in CDS_crd)
            min_mRNA = min(mRNA_crd[0])
            max_mRNA = max(mRNA_crd[0])
            if strand == "+":
                UTR5_crd = [[min_mRNA,(min_cds -1)]]
                UTR3_crd = [[(max_cds + 1), max_mRNA]]
                pro_5 = [[min_mRNA -2000 if min_mRNA - 2000 >= 0 else 0, min_mRNA - 1]]
                pro_3 = [[max_mRNA + 1, max_mRNA + 2000]]

            elif strand == "-":
                UTR3_crd = [[min_mRNA, (min_cds - 1)]]
                UTR5_crd = [[(max_cds + 1), max_mRNA]]
                pro_3 = [[min_mRNA -2000 if min_mRNA - 2000 >= 0 else 0, min_mRNA - 1]]
                pro_5 = [[max_mRNA + 1, max_mRNA + 2000]]

            Chr_vcf = SNPinfo[chr]
            if strand == "+":
                for p51,p52 in pro_5:
                    interval_cnt = cutcount(p51,p52,Chr_vcf)
                    mRNA_len = p52 - p51 + 1
                    print(chr,key,"pro_5",p51,p52,interval_cnt,mRNA_len,strand,sep="\t")

                for P1,P2 in mRNA_crd:
                    interval_cnt = cutcount(P1,P2,Chr_vcf)
                    mRNA_len = P2 - P1 + 1
                    print(chr,key,"mRNA",P1,P2,interval_cnt,mRNA_len,strand,sep="\t")

                for U51, U52 in UTR5_crd:
                    interval_cnt = cutcount(U51,U52,Chr_vcf)
                    UTR5_len = U52 - U51 + 1
                    print(chr,key,"UTR5",U51,U52,interval_cnt,UTR5_len,strand,sep="\t")

                for C1, C2 in CDS_crd:
                    interval_cnt = cutcount(C1,C2,Chr_vcf)
                    CDS_len = C2 - C1 + 1
                    print(chr,key,"CDS",C1,C2,interval_cnt,CDS_len,strand,sep="\t")

                for U31, U32 in UTR3_crd:
                    interval_cnt = cutcount(U31,U32,Chr_vcf)
                    UTR3_len = U32 - U31 + 1
                    print(chr,key,"UTR3",U31,U32,interval_cnt,UTR3_len,strand,sep="\t")

                for p31,p32 in pro_3:
                    interval_cnt = cutcount(p31,p32,Chr_vcf)
                    mRNA_len = p32 - p31 + 1
                    print(chr,key,"pro_3",p31,p32,interval_cnt,mRNA_len,strand,sep="\t")


            if strand == "-":
                for p31,p32 in pro_3:
                    interval_cnt = cutcount(p31,p32,Chr_vcf)
                    mRNA_len = p32 - p31 + 1
                    print(chr,key,"pro_3",p31,p32,interval_cnt,mRNA_len,strand,sep="\t")

                for P1,P2 in mRNA_crd:
                    interval_cnt = cutcount(P1,P2,Chr_vcf)
                    mRNA_len = P2 - P1 + 1
                    print(chr,key,"mRNA",P1,P2,interval_cnt,mRNA_len,strand,sep="\t")

                for U31, U32 in UTR3_crd:
                    interval_cnt = cutcount(U31,U32,Chr_vcf)
                    UTR3_len = U32 - U31 + 1
                    print(chr,key,"UTR3",U31,U32,interval_cnt,UTR3_len,strand,sep="\t")

                for C1, C2 in CDS_crd:
                    interval_cnt = cutcount(C1,C2,Chr_vcf)
                    CDS_len = C2 - C1 + 1
                    print(chr,key,"CDS",C1,C2,interval_cnt,CDS_len,strand,sep="\t")

                for U51, U52 in UTR5_crd:
                    interval_cnt = cutcount(U51,U52,Chr_vcf)
                    UTR5_len = U52 - U51 + 1
                    print(chr,key,"UTR5",U51,U52,interval_cnt,UTR5_len,strand,sep="\t")

                for p51,p52 in pro_5:
                    interval_cnt = cutcount(p51,p52,Chr_vcf)
                    mRNA_len = p52 - p51 + 1
                    print(chr,key,"pro_5",p51,p52,interval_cnt,mRNA_len,strand,sep="\t")