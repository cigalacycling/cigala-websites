# Usage: python3 -I recolor.py <in> <out>   (binary-safe; prints counts)
import sys,re
b=open(sys.argv[1],'rb').read()
reps=[(rb'--cc-green-text: #018a44',rb'--cc-green-text: #34c46a'),(rb'--cc-green-text:#018a44',rb'--cc-green-text:#34c46a')]
total={}
for a,c in reps:
    total[a.decode()]=b.count(a); b=b.replace(a,c)
for pat,c in [(rb'(?i)#018a44',rb'#009a44'),(rb'rgba\(1,( ?)138,( ?)68,',rb'rgba(0,\g<1>154,\g<2>68,'),(rb'(?i)#ca212a',rb'#E10600'),(rb'rgba\(202,( ?)33,( ?)42,',rb'rgba(225,\g<1>6,\g<2>0,'),(rb'(?i)#ff4a3d',rb'#ff3d33')]:
    b,n=re.subn(pat,c,b); total[pat.decode()]=n
open(sys.argv[2],'wb').write(b); print(total)
