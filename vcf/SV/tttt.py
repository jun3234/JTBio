#! usr/bin/env python

D = {1:31,2:30,3:31,4:28,5:31,6:30,
    7:31,8:31,9:30,10:31,11:30,12:31}


def cumd(s2):
    s2_m, s2_d = s2.split(".")
    sm = sum([D[i+1] for i in range(int(s2_m)-1)])
    return sm + int(s2_d)

for line in open("flower_data.txt","r"):
    num,s2,s3,m = line.strip().split()

    s2 = cumd(s2) if s2 != "NA" else s2
    s3 = cumd(s3) if s3 != "NA" else s3
    m = cumd(m) if m != "NA" else m
    if m != "NA":
        os2 = m - s2 + 1 if s2 != "NA" else "NA"
        os3 = m - s3 + 1 if s3 != "NA" else "NA"
    else:
        os2 = os3 = "NA"

    print(line.strip(),os2, os3, sep="\t")