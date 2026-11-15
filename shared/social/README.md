# Shared social icon row (all Cigala sites)

The footer of every site shows the social accounts as a row of monochrome icons, not names (Matteo, 15 Nov 2026).

- The icons come from Simple Icons v16.37.0 (CC0 licence) and are stored in `icons.json` as inline SVG paths, so there are no external requests.
- Each icon is a 40px tap area with a 20px icon in `--text-2` grey. On hover it turns `--green-text` with a faint background, like the other footer links.
- Each link has an `aria-label` and a `title` (the tooltip), so screen readers and hover still show the name.
- The row sits in the footer's Contact column, under phone / email / "★ Google reviews".

## Use

```python
import sys; sys.path.insert(0, ROOT + 'shared/social'); from social import social_row, SOCIAL_CSS
html = social_row()          # all 7 Cigala accounts (CIGALA list in social.py)
html = social_row([('instagram', 'https://...'), ...])  # or a site-specific subset
```

Add `SOCIAL_CSS` to the site's CSS once. On WordPress, Elementor's kit link colour (`.elementor-kit-N a`) overrides it, so also add:

```css
.elementor-kit-N .cc-social a { color: var(--text-2); }
.elementor-kit-N .cc-social a:hover { color: var(--green-text); }
```

See `tools/build_wp.py` for how cigalacycling.com does it.
