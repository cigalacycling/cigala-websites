# Status dot (all sites)

`dot.css` is the one dot used on every Cigala site: cigalacycling.com, Coaching, Tours and Retail.

- **Still dot** (`<span class="dot"></span>`): category labels, e.g. Gran Fondo (red), Gravel (`.sand`), Road (red).
- **Pulsing dot** (`<span class="dot live"></span>`): only for something time-sensitive or changing:
  - Tours: early-bird price ends soon (red); "few places left" (red).
  - Retail: "In stock" (`.green`); "Low stock" (`.amber`); "Out of stock" uses a still grey dot, with no pulse.
- Matteo's decision (15 Nov 2026): the pulse is the standard for status everywhere. Category labels stay still, so the pulse keeps its meaning.
- Size 7px, 7px gap to the text. The pulse is the Tours early-bird one (1.8s glow), and it stops when the visitor has reduced motion on.
