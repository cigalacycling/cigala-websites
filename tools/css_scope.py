"""Scope a design stylesheet to one wrapper class, so several designs can share the Elementor kit CSS.
scope_css(css, 'html .cl') turns ':root' into the wrapper and prefixes every other selector."""
import re

PREVIEW_ONLY = ('body::before', '.topo', '.page')

def _sel(sel, P):
    sel = sel.strip()
    if sel in (':root', 'html', 'body', 'html, body'): return P
    if sel == '*': return P + ' *'
    return P + ' ' + sel

def _scope(block, P):
    out, i = [], 0
    while i < len(block):
        j = block.find('{', i)
        if j < 0: out.append(block[i:]); break
        head = block[i:j].strip()
        if head.startswith(('@media', '@supports')):
            depth, k = 1, j + 1
            while depth:
                depth += {'{': 1, '}': -1}.get(block[k], 0); k += 1
            out.append(head + ' {' + _scope(block[j + 1:k - 1], P) + '}\n'); i = k; continue
        k = block.index('}', j)
        body = block[j + 1:k]
        if head.startswith('@'): out.append(head + ' {' + body + '}\n')
        elif head in PREVIEW_ONLY or head.startswith('.ribbon'): pass
        else: out.append(', '.join(_sel(x, P) for x in head.split(',')) + ' {' + body + '}\n')
        i = k + 1
    return ''.join(out)

def scope_css(css, P):
    return _scope(re.sub(r'/\*.*?\*/', '', css, flags=re.S), P)
