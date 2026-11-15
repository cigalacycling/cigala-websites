"""Build the Blog page: coachingpages/blog.html -> /blog/ (page 4354)

The live post list is WordPress's own loop grid (template 4718), so new posts keep appearing by themselves: the
WordPress build puts that live widget where this preview has the data-live-widget placeholder. Live H1 and the
subtitle H2 stay; the "By ..." author H2s come from the loop template and stay there.
"""
import os, sys, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coaching_common import *
import build_coaching_generic as G

live = LIVE[C + '/blog/']
author_h2 = sorted({h for h in live['h2'] if h.startswith('By ')})
MAIN = f'''<div class="hero hero-sm blog-hero">
  <img src="{img('imgi_25_F42ZwHhq', 'blog-hero-matteo-win')}" alt="Matteo Cigala winning a gran fondo in Siena, arms raised at the finish" style="object-position:50% 45%">
  <div class="in">
    <div class="eyebrow eb-pill"><span class="dot"></span>Blog</div>
    <h1>STAY UP TO DATE WITH OUR LATEST BLOG POSTS</h1>
    <h2 class="lede blog-sub">Get inspired, Read our cycling &amp; triathlon coaching articles. Any questions get in touch.</h2>
  </div>
</div>

<section class="blog-list">
  <div class="in">
    <div data-live-widget="4354:loop-grid" class="blog-placeholder">Latest posts (WordPress loop grid)</div>
  </div>
</section>

{tools_band()}'''
CSS = G.GCSS + FT_CSS + '''<style>
.blog-sub { font: 500 18px/1.5 var(--body) !important; text-transform: none !important; letter-spacing: 0 !important; color: var(--text-2) !important; max-width: 60ch; margin-top: 16px; }
.blog-placeholder { padding: 40px; border: 1px dashed var(--border-strong); border-radius: 12px; color: var(--text-3); text-align: center; }
</style>'''
build('blog', '/blog/', MAIN, 'New Blog page: live post list kept (automatic), H1 and subtitle kept.', h1='STAY UP TO DATE WITH OUR LATEST BLOG POSTS',
      h2_changes={'drop': author_h2}, extra_css=CSS)
