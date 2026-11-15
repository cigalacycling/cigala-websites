"""Build the Group & Club Packages preview: coachingpages/group-club-packages.html

The live page is thin (H1 + ~50 words). All live copy, the H1 and the title stay; added from material already on the site:
the clubs our riders come from (club names in the athletes' own testimonials), Club Talks, athlete reviews, and an
on-page contact form (the live "CONTACT US" link pointed to /contact/), prefilled for a group enquiry.
/group-club-packages2/ (exact duplicate) is redirected here (coaching/SEO-DECISIONS.md section 3).
"""
import os, sys, io, contextlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coaching_common import *
with contextlib.redirect_stdout(io.StringIO()):
    import build_coaching_packages as P

PATH = '/group-club-packages/'
HERO = img('imgi_21_ZtFBdo0p', 'hero')
TEAM = img('T140342.560', 'group-swords-cc')
# club names exactly as the athletes wrote them in their testimonials (coaching/text/testimonials.txt)
CLUBS = ['Swords Cycling Club', 'Navan Road Club', 'Clontarf Cycling Club', 'Orwell Wheelers', 'Newcastle West', 'St Tiernans Cycling Club',
         'Team BikeWorkx', 'Osborne Cycling Team', 'Wexford Wheelers', 'De Ronde Van Cork', 'Tralee Manor West ibike', 'Al Jassra Race Team, Qatar']
clubs = ''.join(f'<li>{E(c)}</li>' for c in CLUBS)

MAIN = f'''<div class="hero hero-sm">
  <img src="{HERO}" alt="Four Cigala Cycling riders climbing together in team kit" width="1600" height="1082">
  <div class="in">
    <div class="eyebrow eb-pill"><span></span>Teams &amp; clubs</div>
    <h1>Group &amp; club packages</h1>
    <p class="lede">This option is perfect for a group of friends or a team who have similar goals and fitness level.</p>
    <div class="ctas">
      <a class="btn btn-go" href="#contact" data-waitlist="group">Ask for group prices</a>
      <a class="btn btn-ghost" href="{C}/club-talk/" {EXT}>Club talks &amp; coaching nights</a>
    </div>
  </div>
</div>

<section>
  <div class="in split">
    <div class="photo grp-photo"><img src="{TEAM}" alt="{E(live_alt('T140342.560'))}" loading="lazy" width="720" height="480"></div>
    <div>
      <div class="eyebrow">How it works</div>
      <h3 class="h-sec">COACHING FOR YOUR TEAM</h3>
      <div class="bar"></div>
      <p class="first">We currently coach numbers of different teams composed by 4 to 10 members.<br>Prices depend for how many people want to be trained.</p>
      <p>To discover more about the prices please <a href="#contact" data-waitlist="group"><b>CONTACT US</b></a></p>
      <ul class="ticks">
        <li>Teams of 4 to 10 riders with similar goals and fitness level</li>
        <li>Plans built by Head Coach Matteo Cigala</li>
        <li>Price based on the number of riders</li>
      </ul>
    </div>
  </div>
</section>

<section>
  <div class="in">
    <div class="head"><div><div class="eyebrow">Our riders</div><h3 class="h-sec">RIDERS FROM THESE CLUBS TRAIN WITH US</h3><div class="bar"></div></div></div>
    <ul class="clubs">{clubs}</ul>
  </div>
</section>

<section>
  <div class="in">
    <a class="band club-band" href="{C}/club-talk/" {EXT}>
      <img src="{img('imgi_21_Lu1whOJ', 'cta')}" alt="Cyclists riding below the Tre Cime di Lavaredo peaks" loading="lazy" width="1367" height="1492">
      <div class="tx">
        <div class="eyebrow eb-pill"><span></span>Club talks</div>
        <h3 class="h-sec">CLUB INFORMATION DAYS, COACHING NIGHTS, Q&amp;A AND GROUP SESSIONS</h3>
        <div class="bar"></div>
        <span class="arrow-link">See club talks →</span>
      </div>
    </a>
  </div>
</section>

<section>
  <div class="in">
    <div class="head">
      <div><div class="eyebrow">Our athletes</div><h3 class="h-sec">WHAT OUR ATHLETES SAY</h3><div class="bar"></div></div>
      <div class="rv-links"><a class="arrow-link" href="{GOOGLE_REVIEWS}" {EXT}>★ Read our reviews on Google →</a><a class="arrow-link" href="{C}/testimonials/" {EXT}>All testimonials →</a></div>
    </div>
    {reviews_strip()}
  </div>
</section>

<section id="contact">
  <div class="in split">
    <div class="photo rider"><img src="{HERO}" alt="Four Cigala Cycling riders climbing together in team kit" loading="lazy" width="1600" height="1082"></div>
    <div>
      <div class="eyebrow">Group prices</div>
      <h3 class="h-sec">GET IN TOUCH TODAY</h3>
      <div class="bar"></div>
      <p class="lede">Tell us about your group or club, how many riders and your goals, and we'll come back to you with the prices.</p>
      <form class="form panel" method="post" action="#" onsubmit="return false">
        <label>Name<input name="form_fields[name]" type="text" placeholder="Name *" required autocomplete="name"></label>
        <label>Email<input name="form_fields[email]" type="email" placeholder="Email *" required autocomplete="email"></label>
        <label>Phone<input name="form_fields[phone]" type="tel" placeholder="Phone (with country code) *" required autocomplete="tel"></label>
        <label>Message<textarea name="form_fields[message]" placeholder="Your Message *" rows="5" required></textarea></label>
        <button class="btn btn-go" type="submit">Send &gt;</button>
      </form>
    </div>
  </div>
</section>'''

GCSS = P.PCSS + '''<style>
.grp-photo { aspect-ratio: 3 / 2; }
.split .first { margin-top: 16px; }
.split p a { color: var(--green-text); }
.split .ticks { margin-top: 16px; }
.clubs { list-style: none; margin: 0; padding: 0; display: flex; flex-wrap: wrap; gap: 10px; }
.clubs li { font-size: 14px; font-weight: 600; color: var(--text); background: var(--wash); border: 1px solid var(--border-strong); border-radius: 999px; padding: 8px 16px; }
.club-band { display: block; text-decoration: none; }
.club-band .h-sec { max-width: 22ch; }
.club-band:hover { border-color: rgba(0,154,68,.6); }
</style>'''
GJS = '''<script>
document.querySelectorAll('[data-waitlist="group"]').forEach(function (b) {
  b.addEventListener('click', function () {
    var m = document.querySelector('#contact textarea');
    if (m && !m.value) m.value = 'Hi Matteo, I would like the prices for a group / club package. Club or group: ... Number of riders: ... Our goals: ...';
  });
});
</script>''' + REVIEWS_JS

build('group-club-packages', PATH, MAIN, 'New Group & Club Packages page: live copy, H1 and title, with clubs, club talks, reviews and a contact form.',
      extra_css=GCSS, extra_js=GJS)
