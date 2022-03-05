#! usr/bin/env python

"""
change the output of 'show-snps' to simplified vcf
"""

import sys
import argparse
import collections
import pysam

#
def get_opts():
    args = argparse.ArgumentParser()
    args.add_argument('-s', '--snps', type=str, required=True, help='the output of show-snps command')
    args.add_argument('-f', '--fasta', type=str, required=True, help='the reference fasta')
    args.add_argument('-g', '--gt', type=str, required=False, default="0|1",
                      help='the genotype to specified')
    args.add_argument("--out", dest="outfile", type=argparse.FileType('w'),
                      default=sys.stdout, help="the output vcf file, [default:stdout]")

    return args.parse_args()


#
Snd = collections.namedtuple("Snd","rps ref alt aps buff dist rlen alen rfrm afrm rchr achr")
def read_snps(snps):
    snp_db = {}
    ps_db = {}
    key = 0
    p_rps = p_aps = "0"

    for line in open(snps):
        lst = Snd(*line.strip().split())

        if (lst.rps != p_rps) and (lst.aps != p_aps):
            key += 1

        if key not in ps_db:
            ps_db[key] = []

        if key not in snp_db:
            snp_db[key] = {"rps":[],"aps":[]}

        ps_db[key].append((lst.rchr, lst.rps))
        snp_db[key]["rps"].append(lst.ref)
        snp_db[key]["aps"].append(lst.alt)
        p_rps = lst.rps
        p_aps = lst.aps

    return ps_db, snp_db


##
def snpTovcf(snps, inGenome, gt,fw=sys.stdout):

    ps_db, snp_db = read_snps(snps)

    ## constant
    ID = "."
    QUAL = "30"
    FILTER = "PASS"
    INFO = "."
    FORMAT = "GT"
    Value = gt

    #
    print("\t".join(["#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO", "FORMAT", "sample1"]), file=fw)
    for key in ps_db:
        rchr, rps = ps_db[key][0]
        rb = "".join([ b for b in snp_db[key]["rps"] if b != "."])
        ab = "".join([ b for b in snp_db[key]["aps"] if b != "."])

        if rb and ab:
            ref = rb
            alt = ab

        elif not rb:
            ib = inGenome.fetch(rchr, int(rps)-1, int(rps))     #start and end are 0-based, nucmer is 1-based, get current base
            #print("rb is %s, ==> add base %s" % (rb, ib))
            ref = ib
            alt = ib + ab

        elif not ab:
            ib = inGenome.fetch(rchr, int(rps)-2, int(rps)-1)   #start and end are 0-based, nucmer is 1-based, get before base
            #print("ab is %s, ==> add base %s" % (ab, ib))
            ref = ib + rb
            alt = ib
            rps = str(int(rps)-1)   # out put 1-based vcf

        print(rchr, rps, ID, ref, alt, QUAL, FILTER, INFO, FORMAT, Value, sep="\t", file=fw)


if __name__ == "__main__":
    args = get_opts()
    inGenome = pysam.FastaFile(args.fasta)
    snpTovcf(args.snps, inGenome, args.gt, fw=args.outfile)