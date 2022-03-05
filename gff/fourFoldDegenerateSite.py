#! usr/bin/env python

"""
Output four-fold degenerate site according proteome and gff3 file
"""

import sys
import argparse
import pysam
import JTBio.gff.gff3 as gff

##condon table
condon = {'CTT':'L', 'CTC':'L', 'CTA':'L', 'CTG':'L',
          'GTT':'V', 'GTC':'V', 'GTA':'V', 'GTG':'V',
          'TCT':'S', 'TCC':'S', 'TCA':'S', 'TCG':'S',
          'CCU':'P', 'CCC':'P', 'CCA':'P', 'CCG':'P',
          'ACU':'T', 'ACC':'T', 'ACA':'T', 'ACG':'T',
          'GCT':'A', 'GCC':'A', 'GCA':'A', 'GCG':'A',
          'CGT':'R', 'CGC':'R', 'CGA':'R', 'CGG':'R',
          'GGU':'G', 'GGC':'G', 'GGA':'G', 'GGG':'G'}

## complement table
com = {"A":"T", "G":"C", "C":"G", "T":"A",
       "a":"t", "g":"c", "c":"g", "t":"a",
       "N":"N", "n":"n"}

def get_opts():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fasta", type=str, help="the genome fasta file")
    parser.add_argument("-g", "--gff", type=str, help="the genome annotation file")
    parser.add_argument("--outfile", dest="out", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output four-fold degenerate site, [default:stdout]")
    return parser.parse_args()


def rev_com(seq, reverse=True, complement=True):
    """ return reverse and complement sequences
    """
    seq = seq[::-1] if reverse else seq
    seq = "".join([com[base] for base in seq])  if complement else seq

    return seq


def align_seq_and_crd(chr, cds_crd, genome, strand):
    """ alignment sequence base and its coord
    """
    #pysam fasta object
    fx = pysam.FastaFile(genome)

    #get seqs
    #get crd, 1-based
    bases = []; crds = []
    for crd in cds_crd:
        bases.append(fx.fetch(chr, start = int(crd[0]) - 1, end = int(crd[-1])))
        crds.append([i for i in range(int(crd[0]), int(crd[-1]) + 1)])
    seq = "".join(bases)
    crds = [ i for i in gff.chain(crds)]

    # plus or mins
    if strand == "-":
        seq = rev_com(seq)
        crds = crds[::-1]

    return seq, crds


def judge_4foldsite(seq, crds):
    """ judge 4-fold degenerate site according condon table
    """
    if len(seq) != len(crds):
        raise ValueError("seq is not the same length to crds")

    for i in range(0, len(seq), 3):
        con = seq[i:i+3]
        crd = crds[i:i+3]

        if con in condon:
            yield (con, crd, True)
        else:
            yield (None, None, False)

#
def cacu_4fold_dSite(gff3, genome, outfile):
    ''' Output 4fold degenerate site according genome fasta and annotation file
    '''

    ## read in gff3
    GFF = gff.GFF3(gff3)
    GFF.load()  # store GFF.gff3 and GFF.mcgff attribute

    ## get sorted chrs name
    sorted_chrs = gff.sort_seqname(GFF.mcgff)

    for chr in sorted_chrs:
        chr_list = GFF.mcgff[chr]
        chr_list.sort(key=lambda x: int(x[2]))  # sort gene start coord in one chromosome

        for ele in chr_list:
            gene, strand = ele.gene, ele.strand
            crds = [(line.start, line.end) for line in GFF.gff3[gene] if line.type == "CDS"]
            seq,crds = align_seq_and_crd(chr, crds, genome, strand)
            for con,crd,flag in judge_4foldsite(seq, crds):
                if flag:
                    print(chr, crd[-1], con, condon[con], crd, sep="\t", file=outfile)


if __name__ == "__main__":
    args = get_opts()
    cacu_4fold_dSite(args.gff,args.fasta, args.out)
