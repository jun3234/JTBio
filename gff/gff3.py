#! usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import re
import argparse
import collections
from collections import Iterable
from collections import UserDict

Linedata = collections.namedtuple("Linedata","seqid source type start end score strand phase attributes")
Mcgff = collections.namedtuple("Mcgff", "seqid gene start end strand")

class Attrbutie(UserDict):
    """ to store nine columns the description Part in gff3 file
    """

    def __init__(self, mapping):
        self.__dict__.update(mapping)

    def __getitem__(self, name):
        return self.__dict__[name]

    def __repr__(self):
        msg = 'AttrDict({0.__dict__})'.format(self)
        return msg

    def __str__(self):
        msg = 'AttrDict({0.__dict__})'.format(self)
        return msg

    def __iter__(self):
        return iter(self.__dict__)


class GFF3:
    """ The GFF3 class record gff3 related info, including some methodes
    """

    def __init__(self, path):
        self.path = path
        self.gff_vesion = None
        self.anno_version = None
        self.gff3 = collections.defaultdict(list)
        self.mcgff = collections.defaultdict(list)

    def load(self):
        """ read gff3 file in
        """
        flag = True
        for line in open(self.path):
            if line.startswith("##gff"):
                self.gff_vesion = line.strip()
            elif line.startswith("#") or not line:
                continue
            else:
                # gff file must have gene or mRNA feature, it contain ID in attributes
                line = Linedata(*self.attr_to_dict(line))
                if line.type == "gene":
                    flag = False
                    key = line.attributes["ID"]
                    if key in self.gff3:    # multiple same name gene feature
                        cnt = len([k for k in self.gff3.keys() if k.startswith(key)])
                        key = line.attributes["ID"] + "@copy_%s" % cnt
                    self.mcgff[line.seqid].append(Mcgff(line.seqid, key, line.start, line.end, line.strand))

                elif flag and line.type == "mRNA":
                    key = line.attributes["ID"]
                    if key in self.gff3:
                        cnt = len([k for k in self.gff3.keys() if k.startswith(key)])
                        key = line.attributes["ID"] + "@copy_%s" % cnt
                    self.mcgff[line.seqid].append(Mcgff(line.seqid, key, line.start, line.end, line.strand))

                self.gff3[key].append(line)

        print("mcgff store key %s" % len(self.mcgff.values()), file=sys.stderr)
        print("gff3 store feature %s" % len(self.gff3),file=sys.stderr)


    def attr_to_dict(self, line):
        line_list = line.strip().split("\t")
        tmp = Attrbutie(dict((s.split("=")[0], s.split("=")[-1]) for s in line_list[-1].split(";")))
        line_list[-1] = tmp
        return line_list


## function region
def linedata2print(input, fileout="None"):
    """ print Linedata object
    """
    assert isinstance(input, Linedata)
    Descrpt = ["%s=%s" % (key, values) if key != "" else "" for key,values in input.attributes.items() ]
    print(input.seqid, input.source, input.type, input.start, input.end, input.score, input.strand, input.phase, ";".join(Descrpt), sep="\t", file=fileout)


def sort_seqname(input):
    """ the end numeric characters are sort ascending, and the other part is alphabet sorting
    """
    un_chr_spl = []
    can_chr_spl = []
    chrs = [key for key in input]
    for chr in chrs:
        chr_split = [ele for ele in re.split(r'(\d+)', chr) if ele]
        if len(chr_split) == 1:
            un_chr_spl.append(chr_split)
        else:
            can_chr_spl.append(chr_split)

    can_chr_spl.sort(key=lambda x:int(x[1]))
    un_chr_spl.sort()

    # union split chr
    return [ i+j for i,j in can_chr_spl] + [ e for e in chain(un_chr_spl)]


##
def chain(*iterables):
    """ get elements from iterable
    """
    for it in iterables:
        for ele in it:
            if isinstance(ele,str):
                yield ele
            elif isinstance(ele,Iterable):
                yield from chain(ele)
            else:
                yield ele



if __name__== "__main__":
    ##parameter
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", dest="gff3_file", type=str, required=True,
                        help="the input gff3 file")
    parser.add_argument("--outfile", dest="out_bed", type=argparse.FileType('w'),
                        default=sys.stdout, help="the output bed file, [default:stdout]")
    args = parser.parse_args()


    #Lch = GFF3(args.gff3_file)
    #Lch.load()
    #print(Lch.gff3["gw00001"])
    #print(sorted(Lch.mcgff, key=lambda x: x[-1]))