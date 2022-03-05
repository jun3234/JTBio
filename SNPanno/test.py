#! usr/bin/env python

import sys

"""
generated bed in a specified region
    python test.py  chr  str  end  width
"""

chr = sys.argv[1]
str = int(sys.argv[2])
end = int(sys.argv[3])
wth = int(sys.argv[4])

##write bed
snt = str
while True:
    s = snt
    e = s + wth - 1
    if e >= end:
        print(chr, s, end, sep="\t", file=sys.stdout)
        break
    print(chr, s, e, sep="\t", file=sys.stdout)
    snt = e + 1
