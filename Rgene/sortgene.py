#! usr/bin/env python

import sys
import pysam
import argparse

##
def read_mcgff(mcgff):
    D = {}
    cnt = 0
    for line in open(mcgff):
        cnt += 1
        chrn,gene,start,end,strand = line.strip().split()
        D[gene] = [chrn,start,end,strand,str(cnt)]
    return D

def outfmt(SeqName,Sequence):
    """ output sequence
    """
    Out = []
    Out.append(">" + SeqName)
    # python 2.7 version: 3.6/2 return 1.8, 3/2 return 1
    # python 2.7 version: 3.6/2 return 1.8, 3/2 return 1.5
    # int(1.8) = 1, so we add extra 1 to RowNum
    RowNum = int(len(Sequence) / 60) + 1
    for i in range(RowNum):
        Rowleft = i * 60
        RowRight = (i + 1) * 60
        Out.append(Sequence[Rowleft:RowRight])
    return Out


if __name__== "__main__":
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-g","--gff", dest="gff3_file", type=str, required=True,
                        help="the input gff3 file1")
    parser.add_argument("-f","--fasta", dest="fasta_file", type=str, required=True,
                        help="seqid need be added chr etc infos")
    parser.add_argument("--outfile", dest="out", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output bed file, [default:stdout]")
    args = parser.parse_args()

    ## parse para
    inGenome = pysam.FastaFile(args.fasta_file)
    mcgff = read_mcgff(args.gff3_file)

    ##start sort
    for seqid in inGenome.references:
        chrn, start, end, _, cnt = mcgff[seqid]
        newName = "_".join([seqid,chrn,start,end,cnt])
        Seq = inGenome.fetch(seqid)
        Out_list = outfmt(newName, Seq)
        print("\n".join(Out_list), file=args.out)