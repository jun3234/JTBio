#! usr/bin/env python
# -*- coding: UTF-8 -*-

"""
split contig into slices, and transfer gff to those slices
"""

import sys
import argparse
import collections
import JTBio.gff.gff3 as gff


# function
def read_break_point(input):
    """ read break_point.txt file
    """
    D = collections.defaultdict(list)
    bpinfo = collections.namedtuple("bp_info", "seqname, start, end, gap")

    for line in open(input):
        bp_info = bpinfo(*line.strip().split())
        D[bp_info.seqname].append((bp_info.start, bp_info.end, bp_info.gap))

    return D


# parameter
parser = argparse.ArgumentParser()
parser.add_argument("-g", dest="gff3_file", type=str, required=True,
                    help="the input gff3 file")
parser.add_argument("-t", dest="break_point", type=str, required=True,
                    help="the 'break_point.txt' that record contig coord")
parser.add_argument("--outfile", dest="out", type=argparse.FileType('w'),
                    default=sys.stdout, help="the output gff3 file, [default:stdout]")
args = parser.parse_args()


# read in gff3
GFF = gff.GFF3(args.gff3_file)
GFF.load()  # store in GFF.gff3 attribute

# read in break point
bp_dict = read_break_point(args.break_point)


# handle
for Chr in GFF.mcgff:
    seqn = GFF.mcgff.seqid
    gene = GFF.mcgff.gene
    for line in GFF.gff3[gene]:

        # start coord
        bplist = bp_dict[seqn][:]
        bplist.append((line.start, ))
        bplist.sort(key=lambda x:int(x[0]))
        str_ind = bplist.index((line.start, ))
        str_crd_red = bp_dict[seqn][str_ind - 1][0]
        str_gap_num = bp_dict[seqn][str_ind - 1][-1]

        # end coord
        bplist = bp_dict[seqn][:]   # copy list
        bplist.append((line.start, ))
        bplist.sort(key=lambda x:int(x[0]))
        end_ind = bplist.index((line.start, ))
        end_crd_red = bp_dict[seqn][end_ind - 1][0]
        end_gap_num = bp_dict[seqn][end_ind - 1][-1]

        # output
        #print(bplist[ind], bp_dict[seqn][ind - 1])
        #line = line._replace(seqid="%s_chunk%s" % (seqn, gap_num),
         #                    start=int(line.start) - int(crd_should_reduce),
          #                   end=int(line.end) - int(crd_should_reduce))

        gff.linedata2print(line, fileout=args.out)
