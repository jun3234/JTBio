#! /usr/bin/env python

import sys

## readin Info
D = dict()
for line in sys.stdin:
    Chr,gene,feature,Str,End,vcfN,Len,Strand = line.strip().split()
    if gene not in D:
        D[gene] = []
        D[gene].append([feature, vcfN, Len])
    else:
        D[gene].append([feature, vcfN, Len])

## get feature
print("geneName", "pro5vcfN", "pro5Len", "pro3vcfN", "pro3Len", "mRNAvcfN", "mRNALen", "CDSvcfN","CDSLen","UTR5vcfN","UTR5Len","UTR3vcfN","UTR3Len","intronvcfN","intronLen",sep="\t")
for key in D:
    pro5 = [(feature, vcfN, Len) for feature, vcfN, Len, in D[key] if feature == "pro_5"]
    pro3 = [(feature, vcfN, Len) for feature, vcfN, Len, in D[key] if feature == "pro_3"]
    mRNA = [(feature, vcfN, Len) for feature, vcfN, Len, in D[key] if feature == "mRNA"]
    UTR3 = [(feature, vcfN, Len) for feature, vcfN, Len, in D[key] if feature == "UTR3"]
    UTR5 = [(feature, vcfN, Len) for feature, vcfN, Len, in D[key] if feature == "UTR5"]

    ## Summary CDS feature
    sum_cds_vcfN = sum([int(vcfN) for feature, vcfN, Len, in D[key] if feature == "CDS"])
    sum_cds_len = sum([int(Len) for feature, vcfN, Len, in D[key] if feature == "CDS"])
    CDS = [("CDS",sum_cds_vcfN,sum_cds_len)]

    ## get intron info
    intron_vcfN = int(mRNA[0][1]) - int(UTR5[0][1]) - int(UTR3[0][1]) - int(CDS[0][1])
    intron_len = int(mRNA[0][2]) - int(UTR5[0][2]) - int(UTR3[0][2]) - int(CDS[0][2])
    intron = [("intron",intron_vcfN,intron_len)]

    ## write
    print(key,pro5[0][1],pro5[0][2],pro3[0][1],pro3[0][2],mRNA[0][1],mRNA[0][2],CDS[0][1],CDS[0][2],UTR5[0][1],UTR5[0][2],UTR3[0][1],UTR3[0][2],intron[0][1],intron[0][2],sep="\t")
