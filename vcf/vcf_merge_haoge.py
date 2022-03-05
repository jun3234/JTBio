#! usr/bin/env python

"""
Merge two vcf file, the same site from different sample
"""

import sys
import argparse
import gzip
import collections


##parameter
def get_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v1","--vcf1", type=str, help="the merged first vcf file")
    parser.add_argument("-v2", "--vcf2", type=str, help="the merged second vcf file")
    parser.add_argument("--outfile", dest="out", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output tidy file, [default:stdout]")
    return parser.parse_args()


##readin vcf
def rdin_vcf(vcf):

    nDict = collections.namedtuple("vcfline", "CHROM POS ID REF ALT QUAL FILTER INFO FORMAT Samples")
    ## read in vcf file, defaultdict(lambda : abaa)
    vcf_dict = collections.defaultdict(list)
    header = list()

    for line in open_vcf(vcf):
        if line.startswith("#"):
            header.append(line)
        elif not line.startswith("#"):
            vcfline = nDict(*line.strip().split()[:9],line.strip().split()[9:])
            key = (vcfline.CHROM, vcfline.POS)
            vcf_dict[key] = vcfline

    return (vcf_dict, header)


##infile type, end with gz or not
def open_vcf(vcf):
    is_gz = True if vcf.endswith("gz") else False
    fh = gzip.open(vcf,"rb") if is_gz else open(vcf, "r")
    for line in fh:
        yield line.decode() if is_gz else line


## file is 'file handle' not string object
def write_vcf(file):
    is_gz = True if file.name.endswith("gz") else False
    fh = gzip.open(file, "wb") if is_gz else open(file, "w")
    return fh


## associated FORMAT and Sample value
def exact_match_FS(format, samples, kp=[]):

    F =  ["GT","AD","DP","GQ","PL"] if not kp else kp
    tmp = list()
    for sp in samples:
        fl = format.strip().split(":")
        sl = sp.strip().split(":")
        D = dict(zip(fl,sl))
        tmp.append(":".join([D[i] for i in F]))

    return tmp


##merge two vcf
def vcf_merge(vcf1, vcf2, outfile=sys.stdout):

    # read vcf
    v1_d, h1 = rdin_vcf(vcf1)
    v2_d, h2 = rdin_vcf(vcf2)

    # out put setting
    #fw = write_vcf(outfile)

    # header merge
    ap =  h1[-1].strip().split() + h2[-1].strip().split()[9:]
    h1[-1] = "\t".join(ap) + "\n"
    # for line in h1:
    #     print(line.strip(), file=outfile)

    # site merge
    for v1_key in v1_d:
        v1_line = v1_d[v1_key]
        v2_line = v2_d[v1_key]

        if v2_line:
            samples_v1 = [i for i in v1_line][0:8]
            samples_v2 = [j for j in v2_line][0:8]
            txt = samples_v1 + samples_v2

            print("\t".join(txt), file=outfile)


if __name__ == '__main__':
    args = get_opts()
    vcf_merge(args.vcf1, args.vcf2, args.out)