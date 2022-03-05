#! usr/bin/env python

"""
If gmap transfer anno to new assembly, sometimes multiple gene would map to one loci
Then, the script is to get the best match and remove the rest
"""

import sys
import argparse
import JTBio.gff.gff3 as gff


##
def init_para(obj,key,lst):
    assert isinstance(obj, gff.GFF3)
    init_llist = obj.gff3[key]
    init_key = key
    _, key, start, end, _ = lst
    init_len = int(end) - int(start)
    init_str = int(end)

    return init_llist,init_key,init_len,init_str


##
def get_feature(g_lines, feature="mRNA"):
    for line in g_lines:
        if line[2] == feature:
            return line


## source identity
def get_cv(obj, key, lst, init_key, source="base"):

    if source == "gmap":
        init_i = get_feature(lst, feature="mRNA")[-1]["identity"]
        curr_i = get_feature(obj.gff3[key], feature="mRNA")[-1]["identity"]

    elif source == "liftoff":
        init_i = get_feature(lst, feature="gene")[-1]["sequence_ID"]
        curr_i = get_feature(obj.gff3[key],feature="gene")[-1]["sequence_ID"]

    elif source == "base":
        init_i = 1
        curr_i = 1

    return init_i, curr_i


##
def rm_dup(gff3_file,op,source="base"):
    D = {}
    GFF = gff.GFF3(gff3_file)                   ## read in gff3
    GFF.load()                                  ## store in GFF.gff3 attribute
    sorted_chrs = gff.sort_seqname(GFF.mcgff)   ## get sorted chrs name

    for chrn in sorted_chrs:
        D[chrn] = {}
        chr_list = GFF.mcgff[chrn]
        chr_list.sort(key=lambda x: int(x[2]))  # sort gene start coord in one chromosome

        init_str = 0
        init_llist = []

        for lst in chr_list:
            _, key, start, end, _ = lst
            cur_len = int(end) - int(start)

            if init_str >= int(start):
                ins_len = init_str - int(start)
                ino = ins_len/init_len
                cuo = ins_len/cur_len
                init_i, curr_i = get_cv(GFF, key, init_llist, init_key, source=source)

                if (cuo >= op) and (ino < op):     # keep no change
                    pass

                elif (cuo >= op) and (ino >= op):
                    if source in ("gmap", "liftoff"):
                        if float(init_i) <= float(curr_i):
                            init_llist, init_key, init_len, init_str = init_para(GFF, key, lst)
                        elif float(init_i) > float(curr_i):     # keep no change
                            pass

                    elif source == "base":
                        if cuo <= ino:
                            init_llist, init_key, init_len, init_str = init_para(GFF, key, lst)
                        elif cuo > ino:
                            pass

                elif (cuo < op) and (ino >= op):
                    init_llist, init_key, init_len, init_str = init_para(GFF, key, lst)

                elif (cuo < op) and (ino < op):
                    D[chrn][init_key] = init_llist
                    init_llist, init_key, init_len, init_str = init_para(GFF, key, lst)


            elif init_str < int(start):
                if init_llist:
                    D[chrn][init_key] = init_llist
                init_llist, init_key, init_len, init_str = init_para(GFF, key, lst)

        ##the last one anno
        D[chrn][init_key] = init_llist

    return D




if __name__ == "__main__":

    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", dest="gff3_file", type=str, required=True,
                        help="the input gff3 file")
    parser.add_argument("-g2", dest="gff_alt", type=str,
                        help="another gff3 file, the nonredundant anno will be added to [-g]")
    parser.add_argument("-i", dest="overlap", type=float, default=0.6,
                        help="the overlap threshold between, overlap ratio > 'i' will be remove")
    parser.add_argument("-t", dest="type", type=str, default="base", choices=["base", "gmap", "liftoff"],
                        help="choose how to remove duplication genes")
    parser.add_argument("--outfile", dest="out", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output gff3 file, [default:stdout]")
    args = parser.parse_args()


    # remove redundant
    gff_rmdup = rm_dup(args.gff3_file, args.overlap, args.type)
    ##
    for chrn in gff_rmdup:
        for key in gff_rmdup[chrn]:
            for line in gff_rmdup[chrn][key]:
                gff.linedata2print(line, fileout=args.out)
