#! usr/bin/env python

"""
Tidy kmersGWAS output, reduced to one signal in a define region, like 50kb, 100kb, and find genes
"""


import sys
import argparse
import JTBio.gff.gff3 as gff

##parameter
def get_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b","--bowtie", type=str, help="the kmers bowtie to reference file")
    parser.add_argument("-r", "--region", type=int, default=100000,
                        help="the extension scope centered with a sign")
    parser.add_argument("-n", "--gene_num", type=int, default=10,
                        help="the gene numbers were kept upstream or downstream")
    parser.add_argument("-gff3", type=str, help="reference gene structure file file")
    parser.add_argument("--outfile", dest="out", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output tidy file, [default:stdout]")
    return parser.parse_args()


##read in bowtie alignment file
def read_bw(file):
    D = dict()
    for line in open(file):
        if line.startswith("#"):
            continue
        else:
            _, _, chr, pos, *_ = line.strip().split("\t")
            key = (chr,int(pos))
            D[key] = line.strip().split("\t")

    return D


##multiple singal site trim to one in a region
def signal_trim(file, region):

    bw = read_bw(file)
    key_list = sorted(bw, key=lambda x:(int(x[0][3:]),int(x[-1])))

    D_flt = dict()
    flag = True
    for chr, pos in key_list:
        if flag:
            i_c = chr; i_ps = i_pe = pos
            flag = False
        elif (chr != i_c) or ((chr == i_c) and (pos > i_pe + region)):
            key = (i_c, i_pe)
            D_flt[key] = bw[key] + [i_ps,i_pe]
            i_c = chr; i_ps = i_pe = pos
        elif (chr == i_c) and (pos <= i_pe + region):
            i_c = i_c; i_pe = pos; i_ps = i_ps

    key = (i_c, i_pe)
    D_flt[key] = bw[key] + [i_ps,i_pe]

    return D_flt


#get pos index
def get_pos_index(crd_list, region = ()):

    rl, rr = region
    rg_tuple = (int(rl), int(rr))
    lcp = crd_list[:]
    lcp.append(rg_tuple)

    #get start index
    lcp.sort(key=lambda x:int(x[0]))
    si = lcp.index(rg_tuple)

    #get end index
    lcp.sort(key=lambda x:int(x[1]))
    ei = lcp.index(rg_tuple)

    return si,ei


##look genes
def look_genes(file, gff3, region, n, out=sys.stdout):

    #kmersGWAS site
    flt_sign = signal_trim(file, region)
    ##gff
    GFF = gff.GFF3(gff3); GFF.load()

    #iter the site
    print("\t".join(["#kmers_num", "kmers_seq", "kmers_Region", "Chr", "pos", "distance", "geneID"]), file=out)
    for key in flt_sign:
        *ssite, rl, rr = flt_sign[key]
        chr = ssite[2]
        chr_list = GFF.mcgff[chr]
        chr_list.sort(key=lambda x: int(x[2]))

        #insert pos to gene coord list, and sort
        crd_list = [(int(s),int(e),g) for _, g,s,e,_ in chr_list]
        si,ei = get_pos_index(crd_list, (rl, rr))

        #get n genes before or after
        candidate = crd_list[(si-n):(ei+n)]

        print("#", file=out)
        pflag = False
        for start, end, gene in candidate:
            if (end <= rl) and (end >= rl -region):
                loc = "upstream, distance (-{:>6}) to region left".format(rl - end)
                pflag = True
            elif (start >= rr) and (start <= rr + region):
                loc = "dnstream, distance (+{:>6}) to region right".format(start - rr)
                pflag = True
            elif (rl < end < rr) or (rl < start < rr):
                rm = int((rl + rr)/2); gm = int((start + end)/2)
                loc = "locate, distane ({:>6}) to region middle".format(gm - rm)
                pflag = True
            if pflag:
                print(ssite[0], ssite[4], "\t".join([str(rl), str(rr)]), "\t".join(ssite[2:4]), loc, gene, sep="\t", file=out)
                pflag = False


if __name__ == '__main__':
    args = get_opts()
    D_flt = signal_trim(args.bowtie,args.region)
    look_genes(args.bowtie, args.gff3, args.region, args.gene_num)

