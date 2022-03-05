#!/usr/bin/env python

import argparse

def gff_read(gff3, type="mRNA", key="Name"):
    D = dict()
    for line in open(gff3):
        line = line.strip()
        if line.startswith("#") or not line :
            continue
        else:
            line_list = line.split("\t")
            if line_list[2] == type:
                Des_list = line_list[8].split(";")
                geneName = [Ele.split("=")[1].split(".")[0] for Ele in Des_list if key in Ele]
                D_key = geneName[0]
                if D_key in D.keys():
                    D[D_key].append(line_list)
                else:
                    D[D_key] = []
                    D[D_key].append(line_list)
            else:
                D[D_key].append(line_list)
    return D


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("gff3", type=str, help="the gff3 file")
    parser.add_argument("-t", "--type", type=str, default="mRNA",
                        help="the most upper feature in gff3 file, must be 'gene' or 'mRNA'")
    parser.add_argument("-k", "--key", type=str, default="geneID",
                        help="if gff3 no gene feature, which character are used as gene name,"
                             "like geneID=abc;geneName=xyz, if choose 'geneID', and abc was gene name")
    args = parser.parse_args()


    # process
    gff_dict = gff_read(args.gff3, type=args.type, key=args.key)

    for key in gff_dict.keys():
        genefeature_Chr = gff_dict[key][0][0]
        genefeature_sou = gff_dict[key][0][1]
        genefeature_CrdStr = min([int(line_list[3]) for line_list in gff_dict[key] if line_list[2] == args.type])
        genefeature_CrdEnd = max([int(line_list[4]) for line_list in gff_dict[key] if line_list[2] == args.type])
        genefeature_strain = [line_list[6] for line_list in gff_dict[key] if line_list[2] == args.type][0]
        genefeature_line_list = [genefeature_Chr, genefeature_sou, "gene", str(genefeature_CrdStr), str(genefeature_CrdEnd), ".",
                                 genefeature_strain, ".", "ID=%s;Name=%s" % (key, key)]
        print("\t".join(genefeature_line_list))
        # other line with feature is not gene
        for line_list in gff_dict[key]:
            if line_list[2] != "gene":
                print("\t".join(line_list))
