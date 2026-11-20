"""Early-bird offers end by themselves (Matteo 20 Nov): the day after 'Early bird price until dd/mm' the note disappears
and every price on the tour card and the tour page goes up by EARLY_UP (in each currency shown), on the visitor's
screen (EARLY_JS) and in the TouristTrip schema. The year of dd/mm: the last such date before the tour starts.
"""
import re, datetime
EARLY_UP = 100
def early_iso(text, start):
    m = re.search(r'(\d{1,2})/(\d{1,2})', text or '')
    if not m: return ''
    d, mo = int(m.group(1)), int(m.group(2)); s = datetime.date.fromisoformat(start)
    y = s.year if (mo, d) <= (s.month, s.day) else s.year - 1
    return datetime.date(y, mo, d).isoformat()
def expired(iso, today=None):
    return bool(iso) and (today or datetime.date.today()) > datetime.date.fromisoformat(iso)
EARLY_JS = """<script>(function(){var t=new Date();t.setHours(0,0,0,0);
document.querySelectorAll('[data-until]').forEach(function(e){var u=new Date(e.dataset.until+'T23:59:59');if(t<=u&&Date.now()<=u.getTime())return;
var box=e.closest('.tcard,.bk2');e.classList.add('none');e.setAttribute('aria-hidden','true');if(e.closest('.bk2'))e.style.display='none';
if(!box)return;box.querySelectorAll('.price').forEach(function(p){var w=document.createTreeWalker(p,4),n;while(n=w.nextNode())n.nodeValue=n.nodeValue.replace(/([\\u20ac\\u00a3$])(\\d[\\d,]*)/g,function(m,c,v){return c+(parseInt(v.replace(/,/g,''),10)+%d);});});
if(e.closest('.bk2'))document.querySelectorAll('script[type="application/ld+json"]').forEach(function(s){try{var d=JSON.parse(s.text);if(d['@type']==='TouristTrip'&&d.offers&&!s.dataset.up){d.offers.price=String(+d.offers.price+%d);s.text=JSON.stringify(d);s.dataset.up=1;}}catch(x){}});});})();</script>""" % (EARLY_UP, EARLY_UP)
