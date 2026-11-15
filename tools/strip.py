import sys
b=open(sys.argv[1],'rb').read()
i=b.index(b'<body>')+len(b'<body>')
j=b.rindex(b'</body></html>')
body=b[i:j]
assert body.startswith(b'\n') and body.endswith(b'\n'), (body[:20],body[-20:])
body=body[1:-1]
open(sys.argv[2],'wb').write(body)
print(len(body), body.count(b'\r\n'))
