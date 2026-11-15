import sys,re,html
from html.parser import HTMLParser
t=open(sys.argv[1]).read()
i=t.find('data-elementor-type="wp-page"')
if i<0: i=t.find('data-elementor-type="wp-post"')
if i<0: i=t.find('data-elementor-type="single-post"')
j=t.find('data-elementor-type="footer"')
t=t[t.rfind('<',0,i):j]
class P(HTMLParser):
    def __init__(s): super().__init__(); s.out=[]; s.cur=None; s.buf=''; s.skip=0
    def handle_starttag(s,tag,a):
        a=dict(a)
        if tag in('script','style'): s.skip+=1
        if tag in('h1','h2','h3','h4','h5','h6','p','li','button','label','strong','b','em'):
            if tag in('strong','b'): s.buf+='**'; return
            if tag=='em': return
            s.flush(); s.cur=tag
        if tag=='br': s.buf+='\n'
        if tag=='a': s.buf+='['; s.href=a.get('href')
        if tag in('input','textarea','select'): s.flush(); s.out.append(f"<{tag} name={a.get('name')} type={a.get('type')} placeholder={a.get('placeholder')} required={'required' in a}>")
        if tag=='img': s.flush(); s.out.append(f"<img {a.get('src')} alt={a.get('alt')!r}>")
    def handle_endtag(s,tag):
        if tag in('script','style'): s.skip-=1
        if tag in('strong','b'): s.buf+='**'
        if tag=='a': s.buf+=f']({s.href})'
        if tag in('h1','h2','h3','h4','h5','h6','p','li','button','label'): s.flush()
    def handle_data(s,d):
        if not s.skip: s.buf+=d
    def flush(s):
        x=re.sub(r'[ \t]+',' ',s.buf).strip()
        if x and x not in('[]',): s.out.append(f"{(s.cur or 'txt').upper()}: {x}")
        s.buf=''; s.cur=None
p=P(); p.feed(t); p.flush(); print('\n'.join(p.out))
