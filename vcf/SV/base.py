#! usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
from collections import Iterable
from collections import defaultdict

## get element from Iterable object
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

## combination
def comb(item=list()):
    n = len(item)
    if n == 1:
        for v in item[0]:
            yield str(v)
    else:
        for v in item[0]:
            res = item[1:]
            for p in comb(res):
                yield str(v) + str(p)

## get n elements every time
def get_spe_len(a=list, n=int):

    l = len(a)
    for i in range(0, l, n):
        yield a[i:i+n]


if __name__ == "__main__":
    L = [["Chr1"],["Chr2"],["Chr3"]]
    #print([ e for e in chain(L)])

    L = [(0, 1), (0, 0),(1,1),(1,0)]
    A = chain(L)
    print([i for i in A])

    for i,j in get_spe_len(L,2):
        print(i,"===>",j)
