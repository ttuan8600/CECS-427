import re
print(sum(list(map(int,re.findall(r'[0-9]+',open('s1.txt').read())))))
