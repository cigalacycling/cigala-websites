"""Renders the shared Cigala cookie banner for one site.
Usage from a build script:
    import sys; sys.path.insert(0, ROOT + 'shared/consent'); from render import banner, head_snippet
    html = banner(ga_id='G-XXXX', pixel_id='1986332861692106', openwidget_org='...')
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))

def banner(ga_id, pixel_id='1986332861692106', openwidget_org='43e5f685-37fc-4f78-9420-122fd2a3c5e3'):
    s = open(os.path.join(HERE, 'banner.html')).read()
    s = s.replace('{{GA_ID}}', ga_id).replace('{{PIXEL_ID}}', pixel_id).replace('{{OPENWIDGET_ORG}}', openwidget_org)
    assert '{{' not in s
    return s

def head_snippet():
    """Elementor custom code (location: head). Re-grants consent for returning visitors who accepted."""
    return open(os.path.join(HERE, 'head-snippet.html')).read()
