# Moving topographic background (all Cigala sites)

Matteo wants the topo background to visibly move when scrolling (15 Nov 2026), and the same on every site. This is a light parallax: the background moves at 40% of the scroll speed.

- It assumes the body background has two layers, the dark overlay gradient first and the topo tile second, as in the kit CSS of each site. So the script sets `background-position: 0 0, center <scrollY*0.4>px !important`.
- It's throttled with requestAnimationFrame and a passive scroll listener, and it works on iPhone (unlike `background-attachment: fixed`).
- It's skipped for visitors who have "reduce motion" switched on.
- Tours uses the same code in `tools/build_tours_wp.py` (PARALLAX), limited to its redesigned pages. cigalacycling.com adds `parallax.html` to the footer template (`tools/build_wp.py`).
