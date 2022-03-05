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
def exact_match_FS(format, samples, kp=[], k=1):
    """
    :param format:
    :param samples:
    :param kp:
    :param n: the alt numbers, to cut AD and PL
    :return:
    """

    fmt = ["GT","AD","DP","GQ","PL"]
    kp = kp if kp else fmt
    tmp = list()
    for sp in samples:
        fl = format.strip().split(":")
        sl = sp.strip().split(":")
        D = dict(zip(fl,sl))

        if "AD" not in kp:  # some times v2 no "AD"
            D["AD"] = "%s,0" % D["DP"]

        if "DP" not in D:   # some samples no DP value
            D["DP"] = '.'

        if "GQ" not in D:   # some samples no GQ value
            D["GQ"] = '.'

        if "PL" not in D:   # some samples no PL value
            D["PL"] = '0,0,0'

        stl = [1]    #  skip inregular GT, eg: 0/2,0/3
        if D["GT"] not in ['0/1','1/0','1/1','0/0','0|1','1|0','1|1','0|0']:
            stl.append(0)

        if k > 1:   # cut AD and PL string
            D["AD"] = ",".join(D["AD"].split(",")[:2])
            D["PL"] = ",".join(D["PL"].split(",")[:3])

        s = ":".join([D[i] for i in fmt])
        tmp.append(s)

    return tmp,all(stl)


##merge two vcf
def vcf_merge(vcf1, vcf2, outfile=sys.stdout, ty="bp"):

    # read vcf
    v1_d, h1 = rdin_vcf(vcf1)
    v2_d, h2 = rdin_vcf(vcf2)

    # out put setting
    #fw = write_vcf(outfile)

    # header merge
    ap =  h1[-1].strip().split() + h2[-1].strip().split()[9:]
    h1[-1] = "\t".join(ap) + "\n"
    for line in h1:
        print(line.strip(), file=outfile)

    # site merge
    for v1_key in v1_d:
        v1_line = v1_d[v1_key]
        v2_line = v2_d[v1_key]

        if "PL" in v2_line.FORMAT:  #skip record nt contain PL
            fmt = ["GT", "AD", "DP", "GQ", "PL"]
            if v2_line.ALT == '<NON_REF>':
                #print(v2_line.CHROM, v2_line.POS)
                samples_v1,s1 = exact_match_FS(v1_line.FORMAT, v1_line.Samples)
                kp = fmt if ty == "bp" else ["GT","DP","GQ","PL"]
                samples_v2,s2 = exact_match_FS(v2_line.FORMAT, v2_line.Samples, kp=kp) # no AD in sample
                if s1 and s2:
                    txt = list(v1_line[:8]) + [":".join(fmt)] + samples_v1 + samples_v2
                    print("\t".join(txt), file=outfile)
            else:
                if '<NON_REF>' in v2_line.ALT and v2_line.ALT.startswith(("A","G","C","T")):
                    n = len(v2_line.ALT.split(","))
                    #print(v2_line.ALT, file=sys.stderr)
                    ALT = [i for i in v2_line.ALT.split(",") if i.startswith(("A","G","C","T"))][0]

                    if v1_line.ALT == ALT:
                        samples_v1,s1 = exact_match_FS(v1_line.FORMAT, v1_line.Samples)
                        samples_v2,s2 = exact_match_FS(v2_line.FORMAT, v2_line.Samples, k=n)
                        if s1 and s2:   # skip inregular GT, eg: 0/2,0/3
                            txt = list(v1_line[:8]) + [":".join(fmt)] + samples_v1 + samples_v2
                            print("\t".join(txt), file=outfile)




if __name__ == '__main__':
    args = get_opts()
    vcf_merge(args.vcf1, args.vcf2, outfile=args.out)