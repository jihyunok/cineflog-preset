import sys
L=open("ko_words.txt",encoding="utf-8").read().split("\n")
for a in sys.argv[1:]:
    if "-" in a: x,y=map(int,a.split("-"))
    else: x=y=int(a)
    for n in range(x,y+1): print(L[2*(n-1)]); print(L[2*(n-1)+1])
