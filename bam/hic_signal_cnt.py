#! usr/bin/env python

import sys
import argparse
import collections

##parameter
parser = argparse.ArgumentParser()
parser.add_argument("-b", dest="bam_file", type=argparse.FileType('r'), default=sys.stdin,
                    help="the input hic bam file")
parser.add_argument("--outfile", dest="out", type=argparse.FileType('w'),
                    default=sys.stdout, help="the output gff3 file, [default:stdout]")
args = parser.parse_args()


##dict to store count
Dcnt = collections.defaultdict(int)
for line in args.bam_file:
    llist = line.strip().split()

    RENAME = llist[2]
    MRNM = RENAME if llist[6] == "=" else llist[6]

    key1 = "%s=%s" % (RENAME, MRNM)
    key2 = "%s=%s" % (MRNM, RENAME)

    if key1 in Dcnt:
        Dcnt[key1] += 1
    elif key2 in Dcnt:
        Dcnt[key2] += 1
    else:
        Dcnt[key1] += 1


##out
k1list = sorted(list(set([k.split("=")[0] for k in Dcnt])), key=lambda x:x[-1])
k2list = sorted(list(set([k.split("=")[1] for k in Dcnt])), key=lambda x:x[-1])
print("Chr", "\t".join(k2list), sep="\t", file=args.out)
for k1 in k1list:
    tmp = []
    for k2 in k2list:
        key = "%s=%s" % (k1, k2)
        tmp.append(str(Dcnt[key]))

    print(k1, "\t".join(tmp), sep="\t", file=args.out)