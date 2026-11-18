<?php
/* Cigala athlete area (Matteo, 16 Nov 2026): every coached athlete has their own login, removed when they finish.
 * Runs as a Code Snippets snippet on the Coaching site (pushed by tools/coaching_athlete_area.py; the snippet holds this file
 * without the opening PHP tag).
 *
 * How Matteo uses it:
 *   New athlete:  Users > Add New, role Subscriber, set a password. Their own page is created under "Athletes" automatically.
 *   Reports:      Athletes > open the athlete > upload PDFs inside that page. Those files open only for that athlete (and Matteo).
 *   Shared hub:   Athletes > "Shared hub (all athletes)": links and PDFs every athlete sees.
 *   Athlete ends: Users > delete the user. The login stops working at once; their page stays (renamed "Former athlete: …")
 *                 so the reports are not lost, and can be deleted by hand.
 * Athletes log in at /athletes/ (noindex, not in the sitemap, never cached) and stay logged in for a year on their phone.
 */
if (!defined('ABSPATH')) return;

const CC_ATH_SLUG = 'athletes';

add_action('init', function () {
    register_post_type('cc_athlete', [
        'labels' => ['name' => 'Athletes', 'singular_name' => 'Athlete page', 'menu_name' => 'Athletes', 'all_items' => 'All athlete pages',
                     'edit_item' => 'Edit athlete page', 'add_new_item' => 'Add athlete page', 'search_items' => 'Search athletes'],
        'public' => false, 'publicly_queryable' => false, 'exclude_from_search' => true, 'show_ui' => true, 'show_in_menu' => true,
        'show_in_rest' => true, 'menu_icon' => 'dashicons-groups', 'menu_position' => 25, 'supports' => ['title', 'editor', 'custom-fields'],
        'capability_type' => 'page', 'map_meta_cap' => true, 'rewrite' => false, 'query_var' => false,
    ]);
    $auth = function () { return current_user_can('edit_pages'); };
    register_post_meta('cc_athlete', 'cc_user', ['type' => 'integer', 'single' => true, 'show_in_rest' => true, 'auth_callback' => $auth]);
    register_post_meta('cc_athlete', 'cc_shared', ['type' => 'boolean', 'single' => true, 'show_in_rest' => true, 'auth_callback' => $auth]);
    register_post_meta('cc_athlete', 'cc_ended', ['type' => 'integer', 'single' => true, 'show_in_rest' => true, 'auth_callback' => $auth]);   // when coaching ended (onboarding.php)
    // the private upload folder, closed to direct downloads (files are served by cc_ath_serve_file after a login check)
    $u = wp_get_upload_dir(); $dir = $u['basedir'] . '/cc-private';
    if (!file_exists($dir . '/.htaccess')) {
        wp_mkdir_p($dir);
        @file_put_contents($dir . '/.htaccess', "Require all denied\n<IfModule !mod_authz_core.c>\nOrder allow,deny\nDeny from all\n</IfModule>\nOptions -Indexes\n");
        @file_put_contents($dir . '/index.php', "<?php // Silence is golden.\n");
    }
});

// athlete pages are always private (never public, whatever button is pressed)
add_filter('wp_insert_post_data', function ($d) {
    if ($d['post_type'] === 'cc_athlete' && in_array($d['post_status'], ['publish', 'future', 'pending'], true)) $d['post_status'] = 'private';
    return $d;
});

/* ---------- language (Matteo 16 Nov): Italian athletes get the hub in Italian ----------
   Set per athlete on their WordPress user page ("Hub language"). The login page follows the phone's language. */
add_action('init', function () {
    register_meta('user', 'cc_lang', ['type' => 'string', 'single' => true, 'show_in_rest' => true, 'auth_callback' => function () { return current_user_can('edit_users'); }]);
    // the language of the athlete's personal things: reports from Matteo's PC tools, availability box, race plans (any language)
    register_meta('user', 'cc_report_lang', ['type' => 'string', 'single' => true, 'show_in_rest' => true, 'auth_callback' => function () { return current_user_can('edit_users'); }]);
    register_post_meta('cc_athlete', 'cc_lang', ['type' => 'string', 'single' => true, 'show_in_rest' => true, 'auth_callback' => function () { return current_user_can('edit_pages'); }]);
});
const CC_REPORT_LANGS = ['en' => 'English', 'it' => 'Italiano', 'sl' => 'Slovenščina', 'de' => 'Deutsch', 'fr' => 'Français', 'es' => 'Español',
    'nl' => 'Nederlands', 'pt' => 'Português', 'pl' => 'Polski', 'hr' => 'Hrvatski', 'cs' => 'Čeština', 'da' => 'Dansk', 'sv' => 'Svenska', 'no' => 'Norsk', 'fi' => 'Suomi', 'ga' => 'Gaeilge'];
// Matteo 16 Nov: ONE "Athlete language" per athlete. The hub, their reports and the availability box use it.
// The hub interface needs that language in cc_t() (English and Italian today); otherwise it shows in English.
// PDFs, articles and free tools are English, or Italian for Italian athletes where an Italian version exists.
const CC_UI_LANGS = ['en', 'it'];
function cc_ath_lang_code($uid) {
    $l = get_user_meta((int) $uid, 'cc_lang', true);
    if (!isset(CC_REPORT_LANGS[$l]) || $l === 'en') { $r = get_user_meta((int) $uid, 'cc_report_lang', true); if (isset(CC_REPORT_LANGS[$r])) $l = $r; }   // older setting
    return isset(CC_REPORT_LANGS[$l]) ? $l : 'en';
}
function cc_ath_flag_cc($cc, $name) {   // a round flag like the Tours site (embedded images); other countries: the emoji flag in the same round frame
    static $IMG = ['be' => 'UklGRowAAABXRUJQVlA4IIAAAACwBwCdASp4AFoAPjEWiUMiISEUX1wAIAMEsoBrrIAfgBpgPwA/YAA4opcUbfcnT1aw7HffvwsZ9lixkE66tkwWXKNi8ETAAP7+pWydvGl/xmH//8obF6o5hgXWtWIArfUo7n0rJ4lol9xygFRr0/7dkACnFhD+cqK4dpmL1nAAAA==', 'ch' => 'UklGRnQCAABXRUJQVlA4IGgCAACQEwCdASp4AFoAPjEYiUMiIaEVrwwAIAMEoA1fG3/qv5Aa41zP8Zfy06SHbnthxyFAf138t/7v7s/6B0gH6Hf47dAfqr+t3ux/wD/Yf13sAP1a6wD0Cf1c9Hr/W/7L4P/2+9F/Vq+ksygTwp/o/UAF5oqYyxGuzEoavrzMlS/C9mF3ILGAqmQvx9SJEgZnU4+dcJzpRIITfmD1R4SnbqWS6E397mAA/vIiS3zgStlpn5ep0+p09ShCngI1L1PJn29vl0XBoNGVafmPLG7HFoHUN02B/Ai2UaNqZr5nffz+zFT+NJp721rjK9flf1nW6IEWzcuLvcBbQySxwzvNZo/FqfQgnYYh9RH8N6bOrwkUJWR/Ojuhf+E2EAXGcfxAAjLlZl8Y+7RBK/vAf3cZv/GQKixGfYxtpQf06iNZJkXO6vn5RLYgVpNwkj33YJrvn84cS9KPLweu5cCzB6TWHdlJNnkVI3X7MMG3PBdPRS9rsT8lrQ46+vPA9lo3pK/mvb/53//7SdAEp9pO03pzIvK1+MH+E62afekR8tq+08g6rEGr+PV9H+mf/nsVxzslf11v5/eDPGR93zhaekuifdAL51nzXEdICpuOmnZtXljrpIdebYXEF0lJZODOR8fq96NnsKkCC6JynuVBxr9h1L6Z/+exXHOyym0L0DHfjjP5NVeb1n2qRBylGpbhbatqGVKzglwLixbE3M+pqbFrzTJ9fCp8MWEndZS/0YP6uMjs6y2fRdyAMqZXidWze0VTCPXTJvhOtDGOKpPJGFz4PXRDoWZoKvGM3soQHKMC3JfMBIoNAAAAAAAA', 'cy' => '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', 'es' => 'UklGRtQAAABXRUJQVlA4IMgAAADQCgCdASp4AFoAPjEWiUMiISEVpAAgAwSxgEoAfiBtJHFvwY/ZnmDNAu0FoA/gH5AYoB6/92Af4AC0GMA3Og37cku9uD5hjdyQj4CCxgG/jaMdhuoE5hjdT9+3zavK8AD++ajvvsUNPG/Dy9kCJyTgcz5//nVcP/dgVNIO9xPnxLh7ifV7mE/6+4FtBWsldoM7gtW1UZasutWXWszEAAPn/CKpvgnKwj5DrYP3SPDeziL22MGEoYWZ2KGhpvAUs2/roQhwAAAAAA==', 'fr' => 'UklGRogAAABXRUJQVlA4IHwAAADwBwCdASp4AFoAPjEWiUMiISEUVAAgAwSygEqB/APxV1QrgH4m/qTXfgG56NQSXaFbY19yg/lPH3J5TnfYz7/KePuTynO+uAAA/v37iyu1UHj/lAGles/itnj//619A6kWzXlpfsviADJFLc7qj2xFxj/dYAAAAAAAAAAA', 'gr' => 'UklGRtYCAABXRUJQVlA4IMoCAACQFwCdASp4AFoAPjESiEKiISEXWR+IIAMEtBZgAcd5gH4gbQjwD8O/xz6w/Vzvzk//L190+2v3ifxP7WesA3AH6Af2z+6e+V/Zv4B1gH9y/s3ozeyB6AH6q+ib+qvwa/uZ6MP//zgD+Mfg1GgH0APAA1QL8A/E3+AeYAPIC490U8QTxZlawbu1jjsIDO8NZY5RtUVjdY8/YEXw/fu+kwUVu5uM0PYgWHPVPFPJFqa+h3Fs5lczBhYEROhZjEYcV3NuaewBQAD++ajvU6fj4fxgPxgPxDPrhrL2uv9NW8//83UXiEkajmLCxpCEczylgG1+43aNSKoGDWJStxy1heDW27YA2oaGfv17/ymf9S4V2jvOdVNrSXpc8n0NFLzyltt7mNgdhQ0QtlKsifkdXvx8hLbmb4qHH+lChBvg3E37kvcvaibPq704qMNMgx81HueJA1HHlnuGLoYu3No8oIlc8elP/tDWrd78cjH5mM4mVzdZZKQuY+378x+FAbFnbVQ25bMPjiFiTi502mXEJiQoci4wMFJFODl9C6hmwiyL5Ljhvw4F/ZmaLSD+MXfh0o8Oj5BRLalZv//AINyi2XUbhc6WMEaEOt5X2CcwIGvjAC3hFvz53lA7d+NOcS78Ml42nk63Rra9Dzo0as746Kl1n+NzQ+RAKG4B3gNqjuwBzvgILvvVOIG+p6zadqk8GRbgNVpHew6LAPMpBflWkOuP41xID+zKfzk3tMHzEDhQk0k7+g+ecbemDQeAzLK1/z3+G6g9UIsBFUIsCPjVf4ZHya1kIq4Y3T/907mGMq1bPwCsqK/S7tNdX9f0Krwyo8snovHxW7stm8oRIieWIoyN1E8mOod61J+4eSnfaU0hJ+1xqYj9nnccdc7VRemI/6Mc5YPK7EaEUEl5LkM5OQyMADY+p+XjAfj4fxgPxgPuTnB027KXU5YAAAA=', 'hr' => 'UklGRmQEAABXRUJQVlA4IFgEAABQHgCdASp4AFoAPjEYikOiIaESCV2EIAMEsQBqntv/VfxV2sztP4x/hBylfgfJ2+R37L+Q/ss/xf5GdRF/gPyd+AHOA/Rz/M/5n3a/65+pPYAfzD/KdYB6AH7Gejh/nf7n8Fv64f9r/i/Aj+qWaAfwD8AO/H+efh3+s3S4ngXyX8IPwx9wP4B+AG2c3PH+AfgB+//OAawB/AP5T9onvi/j/5Kf0T//+ph6FH9D/LX+08gB+jZXOixO9FR2oQARKZxC9GAfaVt5+fqmPaxg/igk/B37A3C3BWFv4Aq9E+MycISJteOYtiY5rM4fNP8y70A2mj1Xm3qxPslJgAD++U82mmvOp/y08eT/0BP/QE/8/8AAn0UZQ6EbJXIDrPoFqNpZJRLwu4l02PnSwr3ukvisdFgzQN/27QZ4UQZOy2RTW5j795QI3DE96KbY/k5mzQl/oX/gVEvLPuVJzIMQPZkKXDtnetdMwSLLxrqoMBbGgyoUi9vjBQCHCsxC3nbdQzFy5NAo7lSdEh4iFQkavCuttlKkxTqoUPDjO5Os9a1yS56FGY4lNT5w3OOYVf7BU36yr7Qzpo009mUMfLiTu2DCjOoELmKRpsMC2NBlQpF7fGChd5OU44snZkKbSF1cskhsxOtz57D9qi09xA87YT4unClZEM2/If/WbuRHbzUhTAqb+3vctYqTmHYlH3Qx5bGo+bKvo4jZjJQ+wXKO/5yJydCMbQ/KA1BQES41NEOVKM4d2HAHnVFP6KfV/Qbn9WBf7Wj+JiUiThzKGiLVWv7m1+IlApdGOBuldqGuiP1xNVMqQAO/+NYVwN8Zk6xx4FwfWLccFFCaFF3+qCl9oJPdQDDTcfl8KqPBR2MB4zrInCV/nIlK+NHMXeRMgZukKVLneno8RFF1+eBnQE1nPilG2VNADY3PsAHdIAkUDuwLhRJkP0csvl/No+Tq6tUhGd38F/5abuMKwWo75EINra5VE/P66SpK/vb9hkY9Agmfdb2h2FP/S4x7PBkEzuLu5XUeZR96dnesH+jft7S/8+Mmh0yLmjp1VpO+FZXRunh/xf//C8IOi58ULdtalKqRv2Cy+WaFOc1M8N7aO7CCuTl0fTRT7QObg/10kOEiZKPZGkMn3N15ZbSgPpNAO39RtIVnN3kCOr/+N/IgSvExBIwCfq0yWX3LTWSDlnrRuDfpInaYFaUgR+IBlHiK9IJzLP1PKvtAGYPiPYUF5fBTHpkhJ3QXCZiWq3y0ioii03aG/FwA9JaVbVaX2KZ3xyA9U7JVZW0wdcV8I0Lyyr7vEdAIE2OWcQDKPEV6QTuzuVPKvhzu2f35aueLA3B/3FgPG4gOEnDvyyl57k8beez8L+Cf+o6p+p1PSzi8Id6etqk8tgVxG2s7x0e7vBIRa9qet47kNP3mCnz0UMT5D3DV6Ej4VCQxKqI//SDxIDi5ZbQd8K6zsfepO5XYQAAyauhiCG0+w3AAAAAAAA==', 'ie' => 'UklGRooAAABXRUJQVlA4IH4AAAAQCACdASp4AFoAPjEYikOiIaEUX1wAIAMEsoBKgf1X8ANUK6b+AH4k1/4Cqe7aOZmlwRYyCddWyYLLlGxeCPaeCrq27ngixj8gAP7tztA2S3JgizqML/aNf0aH//yhNXm+S1No+vDNoVsiXfv6eg/TBAcEB/wAAAAAAAAAAAA=', 'it' => 'UklGRpgAAABXRUJQVlA4IIwAAAAQCACdASp4AFoAPjEWiUMiISEUVAAgAwSygGs1Dj8A/FXZ8OAfib+pNd+Aqn6X7+aJFiyiS7QrbGvuUH8p4+5PKc77Gff5Tx7QAP7xlW60w71OO1rg2l/wyFZdet9f/+kUR0zbzUt28gV/ntxawIjukh+PcGPD/oLlJ8HPDVCbXtvZuLL1YW7jk1XAAA==', 'pt' => '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', 'si' => 'UklGRsgDAABXRUJQVlA4ILwDAADQGACdASp4AFoAPjEYikOiIaERVYwgAwSxAGr4gBmgHsRWB+nfhH8TcuV4p/z32k+8T+jfiBqGPMB+pv+k9u30I/kB7gH9J/mfWS+gB+u/pLf7X+0/Bp+yf7Jezj/7rxZ+oV2f9VzLuOt/tmdAcwNG1/sfT9/ufLL8x/7f3Av47/O/9P+aHwgesD0RCQdAX6p4eJlarwOySdToxhtOa4dk+MfSKI4lrBrIW8YDeG+Eh1o6E4gYxHsgPSwKyRkT9Eqi+MpSTo+VrQLZTIemmoAA/v60Ir+dfP7rSZpGjKdPPz/9Mf9HblomL8tZw1PX/NfzxLw/6O420iuv/JhJke5EZ0E1Tt1xXQrzYf+MJQn+Ke/CxbaUPSh20HX+Y3liw64bs5NTkRNW6Dp80O+eLnOrbEfuiNP91ZRIJ6BZazTpBEEMyj//YOA/1eqcOOQcMye0rjigKyoThveRvEHjcP7mxqcv/0N51yO0pLX9KKDIh6ZT2rHpTmb8KCU0QU0HvQPdavxur2Mg9mD5T4dQXN4ryQ7em/KILpl9a/fomQEVTzlR2//Ox+p4CiQ7tt8ZOxS8wGMKFp7DMTmsVf6YZuDRo+KmeqMJxvYqX5+x7F8WAGzTYLPdF0JVqd8TbHlDb/s2eDDIuDe/8aTfx0bX4PvFZ/ZHvokEv/SbwyvEimu87tAPUMvlvETmaa27RtLQ4zYmH/joVn/wKDfhcZhTHMf3g9X2r8rsxggoOSouWj4Ro22vuKcHi3LIA0C1aWLgNSfKSar+fVvIf1K1+nOdwU/xhfVeu2BOUsiQTMH9ijzCdAX2AfON/8b9+F5qAR3/iAHfKaZpH9FN8Hj6ym/hrrsdFCQOuNR42BOqxlHx5OgjJ7lCsV+gOLw36pnwvNbyzhxDFO0P/25Qcer+dW4Qh8ncef/wTYyoDim+IA5vTi+BZnKBxmRQ2EC1AEJwyb11O3/9fdLU5JlhH2yHCWp+waHd+tkRsDCXsWW3R0mU7GeLUjYc2H//Xvq1thZFQl+QBd/+poSMH+iX60nbrte2MWmzTBy9ABxzvh1zk5JeBhpxQxT6mG+oSIBdVV/PwvMLNIrIN81j1EZ79jmS2df/qT+2X/6pY6i3OFP8wvkwzH3lRQXb+1ygJxmfy1ZxzR403xbfgo5urQMsBOvsP7mfmL/0F79/MPle+ESOuX3cijTuQOS5ZeLzgXCh+wCBq44FZ8t+6P/moYhE8T/81DEInbP/4+qR6+v/+PqkevgADcTFOXCPFKRxYnQ3ICekAA=='];
    static $SVG = [   // Matteo 17 Nov: the emoji flags sat off-centre in the round frame; drawn flags for the countries his athletes have
        'us' => '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 30"><rect width="30" height="30" fill="#fff"/><g fill="#B22234"><rect width="30" height="2.31"/><rect y="4.62" width="30" height="2.31"/><rect y="9.23" width="30" height="2.31"/><rect y="13.85" width="30" height="2.31"/><rect y="18.46" width="30" height="2.31"/><rect y="23.08" width="30" height="2.31"/><rect y="27.69" width="30" height="2.31"/></g><rect width="15" height="16.15" fill="#3C3B6E"/><g fill="#fff"><circle cx="4" cy="4" r="1"/><circle cx="9" cy="4" r="1"/><circle cx="6.5" cy="8" r="1"/><circle cx="11.5" cy="8" r="1"/><circle cx="4" cy="12" r="1"/><circle cx="9" cy="12" r="1"/></g></svg>',
        'ca' => '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 30"><rect width="30" height="30" fill="#fff"/><rect width="7.5" height="30" fill="#D52B1E"/><rect x="22.5" width="7.5" height="30" fill="#D52B1E"/><path fill="#D52B1E" d="M15 6.5l1.3 2.6 1.5-.7-.6 3.7 2.2-2.3.5 1.3 2.3-.5-.8 2.4 1.1.6-3.9 3.2.5 1.5-3.6-.6.1 4.3h-1.2l.1-4.3-3.6.6.5-1.5-3.9-3.2 1.1-.6-.8-2.4 2.3.5.5-1.3 2.2 2.3-.6-3.7 1.5.7z"/></svg>',
        'gb-sct' => '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 30"><rect width="30" height="30" fill="#005EB8"/><path d="M0 0L30 30M30 0L0 30" stroke="#fff" stroke-width="5"/></svg>',
    ];
    $cc = strtolower($cc); $n = esc_attr($name);
    if (isset($SVG[$cc])) return ' <img class="ath-flag" src="data:image/svg+xml;base64,' . base64_encode($SVG[$cc]) . '" alt="' . $n . '" title="' . $n . '" width="14" height="14">';
    if (isset($IMG[$cc])) return ' <img class="ath-flag" src="data:image/webp;base64,' . $IMG[$cc] . '" alt="' . $n . '" title="' . $n . '" width="14" height="14">';
    if (in_array($cc, ['gb-eng', 'gb-sct', 'gb-wls'], true)) {   // England, Scotland, Wales: the emoji tag flags
        $f = mb_chr(0x1F3F4, 'UTF-8'); foreach (str_split(str_replace('-', '', $cc)) as $ch) $f .= mb_chr(0xE0000 + ord($ch), 'UTF-8'); $f .= mb_chr(0xE007F, 'UTF-8');
        return ' <span class="ath-flag ath-flag-e" role="img" aria-label="' . $n . '" title="' . $n . '"><span>' . $f . '</span></span>';
    }
    if ($cc === 'gb-nir') $cc = 'gb';
    if (!preg_match('/^[a-z]{2}$/', $cc)) return '';
    $f = ''; foreach (str_split(strtoupper($cc)) as $ch) $f .= mb_chr(0x1F1E6 + ord($ch) - 65, 'UTF-8');
    return ' <span class="ath-flag ath-flag-e" role="img" aria-label="' . $n . '" title="' . $n . '"><span>' . $f . '</span></span>';
}
function cc_ath_flag($lc) {   // by language, when the athlete has not given a nationality yet; nothing for English
    $cc = ['it' => 'it', 'sl' => 'si', 'pt' => 'pt', 'es' => 'es', 'fr' => 'fr', 'hr' => 'hr', 'ga' => 'ie', 'de' => 'de', 'nl' => 'nl', 'pl' => 'pl', 'cs' => 'cz', 'da' => 'dk', 'sv' => 'se', 'no' => 'no', 'fi' => 'fi'][$lc] ?? '';
    return $cc === '' ? '' : cc_ath_flag_cc($cc, CC_REPORT_LANGS[$lc] ?? $lc);
}
function cc_ath_flag_for($pid) {   // Matteo 17 Nov: the nationality from the rider form, else the language
    $prof = json_decode((string) get_post_meta($pid, 'cc_profile', true), true) ?: [];
    $nat = !empty($prof['nat']) ? $prof['nat'] : (string) get_post_meta($pid, 'cc_nat', true);   // the athlete's answer, else what Matteo/the laptop set (pc-api.php)
    if ($nat !== '') return cc_ath_flag_cc($nat, defined('CC_F_COUNTRIES') ? (CC_F_COUNTRIES[$nat] ?? strtoupper($nat)) : strtoupper($nat));
    return cc_ath_flag(cc_ath_lang_code((int) get_post_meta($pid, 'cc_user', true)));
}
function cc_ath_hub_langs() {   // languages the whole hub speaks: English, Italian, plus every language in hub-i18n.php
    $o = ['en', 'it']; foreach (array_keys(CC_REPORT_LANGS) as $l) if (!in_array($l, $o, true) && function_exists('cc_hub_dict') && cc_hub_dict($l)) $o[] = $l;
    return $o;
}
function cc_ath_lang_switch() {   // Matteo 17 Nov: the athlete can change the language Matteo picked; the form, hub and emails follow
    if (!is_user_logged_in() || cc_ath_is_coach()) return '';
    $cur = cc_ath_lang_code(get_current_user_id()); $ls = cc_ath_hub_langs(); if (!in_array($cur, $ls, true)) $ls[] = $cur;
    $opt = ''; foreach ($ls as $l) $opt .= '<option value="' . $l . '"' . selected($cur, $l, false) . '>' . esc_html(CC_REPORT_LANGS[$l]) . '</option>';
    return '<form class="ath-lang" method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="cc_my_lang">' . wp_nonce_field('cc_my_lang', '_wpnonce', false, false)
         . '<label for="ath-lang">' . esc_html(cc_L('Language', 'Lingua')) . '</label><select id="ath-lang" name="lang" onchange="var f=this.form;(window.ccRfSaveNow?window.ccRfSaveNow():Promise.resolve()).catch(function(){}).then(function(){f.submit()})">' . $opt . '</select>'
         . '<noscript><button class="btn btn-ghost">OK</button></noscript></form>';
}
add_action('admin_post_cc_my_lang', function () {
    if (!is_user_logged_in() || !wp_verify_nonce($_POST['_wpnonce'] ?? '', 'cc_my_lang')) wp_die('Not allowed');
    $l = sanitize_key($_POST['lang'] ?? '');
    if (isset(CC_REPORT_LANGS[$l])) { update_user_meta(get_current_user_id(), 'cc_lang', $l); delete_user_meta(get_current_user_id(), 'cc_report_lang'); }
    wp_safe_redirect(home_url('/' . CC_ATH_SLUG . '/')); exit;
});
add_filter('cc_ath_hero_links', function ($html, $coach) { return $coach ? $html : $html . cc_ath_lang_switch(); }, 20, 2);
function cc_ath_user_lang($uid) { $l = cc_ath_lang_code($uid); return in_array($l, CC_UI_LANGS, true) || (function_exists('cc_hub_dict') && cc_hub_dict($l)) ? $l : 'en'; }
function cc_Ln($n, $en1, $it1, $en, $it) {   // plural: Slovenian has its own forms for 2 and 5+ (keys "sl2:" / "sl5:" in hub-i18n.php)
    if (($GLOBALS['cc_ath_lang'] ?? 'en') === 'sl' && function_exists('cc_hub_dict')) { $d = cc_hub_dict('sl'); $m = $n % 100;
        if ($m === 2 && isset($d['sl2:' . $en])) return $d['sl2:' . $en]; if (($m === 0 || $m >= 5) && isset($d['sl5:' . $en])) return $d['sl5:' . $en]; }
    return $n === 1 ? cc_L($en1, $it1) : cc_L($en, $it);
}
// Matteo 17 Nov: every hub text in the athlete's language. cc_L(English, Italian); other languages come from cc_hub_dict() (hub-i18n.php, keyed by the English text).
function cc_L($en, $it) {
    $l = $GLOBALS['cc_ath_lang'] ?? 'en';
    if ($l === 'it') return $it;
    if ($l !== 'en' && function_exists('cc_hub_dict')) { $d = cc_hub_dict($l); if (isset($d[$en])) return $d[$en]; }
    return $en;
}   // the hub interface
function cc_ath_report_lang($uid) { return cc_ath_lang_code($uid); }                                                       // reports, availability, race plans
function cc_ath_lang_field($user = null) {
    $v = ($user instanceof WP_User) ? cc_ath_lang_code($user->ID) : 'en';
    echo '<h2>Athlete hub</h2><table class="form-table" role="presentation"><tr><th><label for="cc_lang">Athlete language</label></th><td><select name="cc_lang" id="cc_lang">';
    foreach (CC_REPORT_LANGS as $k => $n) echo '<option value="' . $k . '"' . selected($v, $k, false) . '>' . esc_html($n) . '</option>';
    echo '</select><p class="description">The athlete\'s hub, reports and availability box use this language. Guides, articles and free tools are in English (Italian for Italian athletes).</p></td></tr></table>';
}
add_action('user_new_form', function ($type) { if ($type === 'add-new-user') cc_ath_lang_field(); });
add_action('show_user_profile', 'cc_ath_lang_field');
add_action('edit_user_profile', 'cc_ath_lang_field');
function cc_ath_lang_save($uid) {
    if (!isset($_POST['cc_lang']) || !current_user_can('edit_users')) return;
    $l = sanitize_key($_POST['cc_lang']);
    update_user_meta($uid, 'cc_lang', isset(CC_REPORT_LANGS[$l]) ? $l : 'en');
    delete_user_meta($uid, 'cc_report_lang');
}
add_action('user_register', 'cc_ath_lang_save', 5);
add_action('edit_user_profile_update', 'cc_ath_lang_save');
add_action('personal_options_update', 'cc_ath_lang_save');
$GLOBALS['cc_ath_lang'] = 'en';
// Matteo 16 Nov: athletes reset their own password (passwords.php); without that module the old "message me" texts stay
function cc_ath_selfpw() { return function_exists('cc_pw_mail'); }
function cc_ath_forgot_url() { return add_query_arg('cc_forgot', 1, home_url('/' . CC_ATH_SLUG . '/')); }
function cc_t($s) {
    static $IT = [
        'Coached athletes' => 'Atleti seguiti', 'Athlete login' => 'Accesso atleti',
        'Your training guides, links and your own reports, all in one place.' => 'Le tue guide di allenamento, i link e i tuoi report personali, tutto in un unico posto.',
        'That username or password is not right. Try again, or message me and I will reset it.' => 'Nome utente o password non corretti. Riprova, oppure scrivimi e te la reimposto.',
        'That email or password is not right. Try again, or tap “Forgot your password?” below to choose a new one.' => 'Email o password non corretti. Riprova, oppure tocca “Password dimenticata?” qui sotto per sceglierne una nuova.',
        'Username or email' => 'Nome utente o email', 'Password' => 'Password', 'Keep me logged in' => 'Resta collegato', 'Log in' => 'Accedi',
        'Athlete area' => 'Area atleta', ' · coach view' => ' · vista coach', 'Welcome' => 'Ciao', 'Log out' => 'Esci',
        'Everything for your coaching in one place. Train smarter. Ride faster.' => 'Tutto il tuo coaching in un unico posto. Train smarter. Ride faster.',
        'report in your folder' => 'report nella tua cartella', 'reports in your folder' => 'report nella tua cartella',
        'Your reports' => 'I tuoi report', 'Sections' => 'Sezioni',
        'Your first assessment, reviews and progress reports will appear here. I will let you know when there is something new.' => 'Qui troverai la tua valutazione iniziale, le revisioni e i report sui tuoi progressi. Ti avviso io quando c’è qualcosa di nuovo.',
        'This area is for athletes I coach. If you are one of them, message me and I will set up your login.' => 'Quest’area è per gli atleti che seguo. Se sei uno di loro, scrivimi e ti creo l’accesso.',
        'Pick a time that suits you' => 'Scegli l’orario che preferisci',
        'Your one-off consult with Marine Lenehan, sports nutritionist' => 'La tua consulenza una tantum con Marine Lenehan, nutrizionista sportiva',
        'I usually reply within a few hours' => 'Di solito rispondo entro poche ore', 'Free for coaching clients' => 'Gratis per gli atleti seguiti',
        'Your plan, workouts and analysis' => 'Il tuo piano, gli allenamenti e le analisi', 'Your plan and workouts' => 'Il tuo piano e gli allenamenti',
        'PDF · opens in a new tab' => 'PDF · si apre in una nuova scheda', 'Open' => 'Apri', 'min read' => 'min di lettura', 'Document' => 'Documento',
        'Matteo Cigala, your coach, in the white Cigala Cycling jersey' => 'Matteo Cigala, il tuo coach, con la maglia bianca Cigala Cycling',
    ];
    $l = $GLOBALS['cc_ath_lang'] ?? 'en';
    if ($l === 'it') return $IT[$s] ?? $s;
    return $l !== 'en' ? cc_L($s, $s) : $s;
}

/* ---------- who is who ---------- */
function cc_ath_page_of($uid, $create = false) {
    $q = get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'meta_key' => 'cc_user', 'meta_value' => (int) $uid, 'numberposts' => 1, 'fields' => 'ids']);
    if ($q) return (int) $q[0];
    if (!$create) return 0;
    $u = get_userdata($uid);
    if (!$u || !in_array('subscriber', (array) $u->roles, true)) return 0;
    $name = trim($u->first_name . ' ' . $u->last_name);
    if ($name === '') $name = $u->display_name ?: $u->user_login;
    $id = wp_insert_post(['post_type' => 'cc_athlete', 'post_status' => 'private', 'post_title' => $name, 'post_content' => '', 'meta_input' => ['cc_user' => (int) $uid]]);
    return is_wp_error($id) ? 0 : (int) $id;
}
function cc_ath_shared_page($lang = 'en') {   // the shared hub in the athlete's language (English when there is no Italian one)
    $q = get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'meta_key' => 'cc_shared', 'meta_value' => '1', 'numberposts' => -1, 'fields' => 'ids', 'orderby' => 'ID', 'order' => 'ASC']);
    $en = 0;
    foreach ($q as $id) {
        $l = get_post_meta($id, 'cc_lang', true) ?: 'en';
        if ($l === $lang) return (int) $id;
        if ($l === 'en' && !$en) $en = (int) $id;
    }
    return $en;
}
function cc_ath_is_coach() { return current_user_can('edit_pages'); }
// Matteo 17 Nov: athletes coached in TrainingPeaks (tick on the Contracts board). Their hub has no Availability, Goals & events or Vekta
// section (they add those in TrainingPeaks); a TrainingPeaks card instead. The rider form stays.
// Matteo 17 Nov: his demo page: a private athlete page with no login, filled from his own Vekta data ("me"); never counted, never emailed
add_action('rest_api_init', function () {
    register_rest_route('cc/v1', '/demo', ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        $nm = sanitize_text_field((string) ($r['name'] ?: 'Matteo Cigala'));
        $ex = get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => 1, 'fields' => 'ids', 'meta_key' => 'cc_demo', 'meta_value' => '1']);
        $pid = $ex ? (int) $ex[0] : (int) wp_insert_post(['post_type' => 'cc_athlete', 'post_status' => 'private', 'post_title' => $nm, 'post_content' => '', 'meta_input' => ['cc_demo' => 1, 'cc_nat' => (string) ($r['nat'] ?: 'it')]]);
        return ['page' => $pid, 'name' => get_the_title($pid)];
    }]);
});
function cc_ath_tp($pid) { return $pid && (bool) get_post_meta((int) $pid, 'cc_tp', true); }
function cc_ath_can_see($pid) {
    if (!$pid || get_post_type($pid) !== 'cc_athlete' || !is_user_logged_in()) return false;
    if (cc_ath_is_coach()) return true;
    $me = get_current_user_id();
    $ok = get_post_meta($pid, 'cc_shared', true) ? (bool) cc_ath_page_of($me) : (int) get_post_meta($pid, 'cc_user', true) === $me;
    return (bool) apply_filters('cc_ath_can_see', $ok, $pid, $me);   // onboarding.php: closed until the rider form is done
}

// a new Subscriber gets their own page; a deleted one loses the link (the page is kept for Matteo)
add_action('user_register', function ($uid) { cc_ath_page_of($uid, true); }, 20);
add_action('set_user_role', function ($uid, $role) { if ($role === 'subscriber') cc_ath_page_of($uid, true); }, 20, 2);
add_action('add_user_role', function ($uid, $role) { if ($role === 'subscriber') cc_ath_page_of($uid, true); }, 20, 2);   // the REST API adds roles this way
add_action('delete_user', function ($uid) {
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'meta_key' => 'cc_user', 'meta_value' => (int) $uid, 'numberposts' => -1]) as $p) {
        delete_post_meta($p->ID, 'cc_user');
        if (!empty($GLOBALS['cc_keep_record'])) continue;   // login removed but still coached (e.g. moved to Basic): not a former athlete
        wp_update_post(['ID' => $p->ID, 'post_author' => get_current_user_id() ?: $p->post_author,
                        'post_title' => 'Former athlete: ' . preg_replace('/^Former athlete: /', '', $p->post_title)]);
    }
});
// show which login each page belongs to, in the Athletes list
add_filter('manage_cc_athlete_posts_columns', function ($c) { $c['cc_user'] = 'Login'; return $c; });
add_action('manage_cc_athlete_posts_custom_column', function ($col, $pid) {
    if ($col !== 'cc_user') return;
    if (get_post_meta($pid, 'cc_shared', true)) { echo 'All athletes'; return; }
    $u = get_userdata((int) get_post_meta($pid, 'cc_user', true));
    echo $u ? esc_html($u->user_login . ' (' . $u->user_email . ')' . (cc_ath_lang_code($u->ID) !== 'en' ? ' · ' . CC_REPORT_LANGS[cc_ath_lang_code($u->ID)] : '')) : '—';
}, 10, 2);

/* ---------- private files: uploads made inside an athlete page go to uploads/cc-private ---------- */
function cc_ath_upload_parent() {
    foreach (['post', 'post_id'] as $k) {
        $p = isset($_REQUEST[$k]) ? (int) $_REQUEST[$k] : 0;
        if ($p && get_post_type($p) === 'cc_athlete') return $p;
    }
    return 0;
}
add_filter('upload_dir', function ($d) {
    if (cc_ath_upload_parent()) { $d['subdir'] = '/cc-private'; $d['path'] = $d['basedir'] . '/cc-private'; $d['url'] = $d['baseurl'] . '/cc-private'; }
    return $d;
});
function cc_ath_is_private_file($id) { $f = get_attached_file($id, true); return $f && strpos(wp_normalize_path($f), '/cc-private/') !== false; }
add_filter('wp_get_attachment_url', function ($url, $id) {
    return cc_ath_is_private_file($id) ? add_query_arg('cc_file', (int) $id, home_url('/' . CC_ATH_SLUG . '/')) : $url;
}, 10, 2);
add_filter('image_downsize', function ($out, $id) {     // private images: always the full file, through the check
    if (!cc_ath_is_private_file($id)) return $out;
    $m = wp_get_attachment_metadata($id);
    return [wp_get_attachment_url($id), $m['width'] ?? 0, $m['height'] ?? 0, false];
}, 10, 2);
add_filter('wp_calculate_image_srcset', function ($s, $size, $src, $meta, $id) { return cc_ath_is_private_file($id) ? false : $s; }, 10, 5);

/* ---------- /athletes/: never cached, never indexed ---------- */
function cc_ath_is_area() { return is_page(CC_ATH_SLUG) || isset($_GET['cc_file']); }
add_action('template_redirect', function () {
    if (!cc_ath_is_area()) return;
    nocache_headers(); header('X-Robots-Tag: noindex, nofollow'); do_action('litespeed_control_set_nocache', 'athlete area');
    if (!isset($_GET['cc_file'])) return;
    $id = (int) $_GET['cc_file']; $file = get_attached_file($id, true);
    if (!$file || !cc_ath_is_private_file($id) || !file_exists($file)) { status_header(404); exit('Not found'); }
    if (!is_user_logged_in()) { wp_safe_redirect(add_query_arg('next', $id, home_url('/' . CC_ATH_SLUG . '/'))); exit; }
    if (!cc_ath_can_see(wp_get_post_parent_id($id))) { status_header(403); exit('This file is not part of your account.'); }
    while (ob_get_level()) ob_end_clean();
    header('Content-Type: ' . (get_post_mime_type($id) ?: 'application/octet-stream'));
    header('Content-Length: ' . filesize($file));
    header('Content-Disposition: inline; filename="' . sanitize_file_name(basename($file)) . '"');
    readfile($file); exit;
}, 0);
add_filter('wpseo_robots', function ($r) { return cc_ath_is_area() ? 'noindex, nofollow' : $r; });
add_filter('wpseo_exclude_from_sitemap_by_post_ids', function ($ids) {
    $p = get_page_by_path(CC_ATH_SLUG); if ($p) $ids[] = $p->ID; return $ids;
});

/* ---------- logged-in athletes use the site as members (Matteo 16 Nov): the free tools open without the newsletter step,
   and the sales pop-ups stay away (newsletter pop-up snoozed, exit pop-up off). Runs first in <head>, before the page scripts.
   Only for athletes: Matteo logged in still sees the site as a visitor does. Logged-in pages are never cached. ---------- */
add_action('wp_head', function () {
    if (!is_user_logged_in() || cc_ath_is_coach() || !cc_ath_page_of(get_current_user_id())) return;
    echo "<script>try{localStorage.setItem('cc_tools_ok','1');var n=JSON.parse(localStorage.getItem('cc_nl')||'{}');if(!n.s){n.c=Date.now();localStorage.setItem('cc_nl',JSON.stringify(n));}sessionStorage.setItem('cc_exit','1');}catch(e){}</script>\n";
    // already coached: no "Want a plan built around these numbers?" box under the free tools (Matteo 16 Nov)
    echo '<style>.cc section:has(.tl-cta){display:none!important}</style>' . "\n";
}, 1);

/* ---------- logins: athletes never see wp-admin and stay logged in for a year ---------- */
add_filter('show_admin_bar', function ($s) { return current_user_can('edit_posts') ? $s : false; });
add_action('admin_init', function () {   // athletes stay out of wp-admin; admin-post.php is let through for their own nonce-checked forms (language)
    if (!current_user_can('edit_posts') && !wp_doing_ajax() && is_user_logged_in() && ($GLOBALS['pagenow'] ?? '') !== 'admin-post.php') { wp_safe_redirect(home_url('/' . CC_ATH_SLUG . '/')); exit; }
});
add_filter('login_redirect', function ($to, $req, $user) {
    if ($user instanceof WP_User && !user_can($user, 'edit_posts')) return $req && strpos($req, '/' . CC_ATH_SLUG) !== false ? $req : home_url('/' . CC_ATH_SLUG . '/');
    return $to;
}, 20, 3);
add_filter('auth_cookie_expiration', function ($len, $uid, $remember) { return ($remember && !user_can($uid, 'edit_posts')) ? YEAR_IN_SECONDS : $len; }, 10, 3);
add_action('wp_login_failed', function () {   // a wrong password goes back to the athlete page, not to the WordPress login screen
    $r = wp_get_referer();
    if ($r && strpos($r, '/' . CC_ATH_SLUG) !== false) { wp_safe_redirect(add_query_arg('login', 'failed', home_url('/' . CC_ATH_SLUG . '/'))); exit; }
});
add_filter('authenticate', function ($u, $log, $pwd) {   // empty fields: same
    $r = wp_get_referer();
    if (($log === '' || $pwd === '') && $r && strpos($r, '/' . CC_ATH_SLUG) !== false && $_SERVER['REQUEST_METHOD'] === 'POST') {
        wp_safe_redirect(add_query_arg('login', 'failed', home_url('/' . CC_ATH_SLUG . '/'))); exit;
    }
    return $u;
}, 99, 3);

/* ---------- the page: [cc_athletes] ---------- */
function cc_ath_content($pid) {
    $p = get_post($pid); if (!$p) return '';
    remove_shortcode('cc_athletes');
    $html = apply_filters('the_content', $p->post_content);
    add_shortcode('cc_athletes', 'cc_ath_shortcode');
    return $html;
}
function cc_ath_inner() {
    $url = home_url('/' . CC_ATH_SLUG . '/');
    $o = '<div class="ath">';
    if (!is_user_logged_in()) {
        $al = strtolower($_SERVER['HTTP_ACCEPT_LANGUAGE'] ?? '');
        $ql = sanitize_key($_GET['lang'] ?? ''); $bl = substr($al, 0, 2);   // the login page: ?lang= or the browser language, when the hub speaks it
        $ok = function ($l) { return $l === 'it' || $l === 'en' || (function_exists('cc_hub_dict') && cc_hub_dict($l)); };
        $GLOBALS['cc_ath_lang'] = $ql !== '' && $ok($ql) ? $ql : ($ql === '' && $ok($bl) ? $bl : 'en');
        $it = $GLOBALS['cc_ath_lang'] === 'it';
        if (isset($_GET['cc_set'])) return $o . cc_ath_setpw_html() . '</div>';   // link from the welcome email
        if (isset($_GET['cc_forgot']) && ($fp = apply_filters('cc_ath_forgot_page', '')) !== '') return $o . $fp . '</div>';   // passwords.php
        $next = isset($_GET['next']) ? add_query_arg('cc_file', (int) $_GET['next'], $url) : $url;
        $o .= '<div class="ath-login"><p class="eyebrow">' . cc_t('Coached athletes') . '</p><h1>' . cc_t('Athlete login') . '</h1>'
            . '<p class="ath-lede">' . cc_t('Your training guides, links and your own reports, all in one place.') . '</p>';
        if (isset($_GET['login'])) $o .= '<p class="ath-err" role="alert">' . cc_t(cc_ath_selfpw() ? 'That email or password is not right. Try again, or tap “Forgot your password?” below to choose a new one.' : 'That username or password is not right. Try again, or message me and I will reset it.') . '</p>';
        $o .= '<form method="post" action="' . esc_url(site_url('wp-login.php', 'login_post')) . '">'
            . '<label for="ath-u">' . cc_t('Username or email') . '</label><input id="ath-u" name="log" type="text" autocomplete="username" autocapitalize="none" required>'
            . '<label for="ath-p">' . cc_t('Password') . '</label><input id="ath-p" name="pwd" type="password" autocomplete="current-password" required>'
            . '<label class="ath-rem"><input name="rememberme" type="checkbox" value="forever" checked> ' . cc_t('Keep me logged in') . '</label>'
            . '<input type="hidden" name="redirect_to" value="' . esc_url($next) . '">'
            . '<button type="submit" class="btn btn-go">' . cc_t('Log in') . '</button></form>'
            . apply_filters('cc_ath_forgot_link', '')   // passwords.php: "Forgot your password?" with a reset link by email
            . (cc_ath_selfpw() ? '' : '<p class="ath-help">' . cc_L('Forgot your password? <a href="https://wa.me/353834777697" target="_blank" rel="noopener">WhatsApp me</a> or <a href="mailto:matteo@cigalacycling.com">email me</a> and I will send you a new one.', 'Password dimenticata? <a href="https://wa.me/353834777697" target="_blank" rel="noopener">Scrivimi su WhatsApp</a> o <a href="mailto:matteo@cigalacycling.com">mandami un’email</a> e te ne invio una nuova.') . '</p>')
            . '<p class="ath-help">' . cc_L('Not coached yet?', 'Non sei ancora seguito?') . ' <a href="' . esc_url(home_url($it ? '/preparatore-di-ciclismo-italia/' : '/individual-packages/')) . '">' . cc_L('See the coaching packages', 'Scopri il coaching') . '</a>.</p>'
            . '</div>';
        return $o . '</div>';
    }
    $me = wp_get_current_user(); $mine = cc_ath_page_of($me->ID); $coach = cc_ath_is_coach();
    $GLOBALS['cc_ath_lang'] = cc_ath_user_lang($me->ID);
    if (!$mine && !$coach) {
        return $o . '<h1>' . cc_t('Athlete area') . '</h1><p>' . cc_t('This area is for athletes I coach. If you are one of them, message me and I will set up your login.') . '</p>'
             . '<p><a class="btn btn-ghost" href="' . esc_url(wp_logout_url($url)) . '">' . cc_t('Log out') . '</a></p></div>';
    }
    // onboarding.php: until the rider form is done, an athlete sees only the form (empty without that module)
    if (!$coach && ($gate = apply_filters('cc_ath_gate', '', $me, $mine)) !== '') return $o . $gate . '</div>';
    $view = $mine;
    if ($coach && isset($_GET['view']) && get_post_type((int) $_GET['view']) === 'cc_athlete') $view = (int) $_GET['view'];
    // the coach sees each athlete's page in that athlete's language; ?lang=it|en previews either hub
    if ($coach) $GLOBALS['cc_ath_lang'] = ($v = (int) get_post_meta($view, 'cc_user', true)) ? cc_ath_user_lang($v) : 'en';
    if ($coach && in_array($_GET['lang'] ?? '', ['it', 'en'], true)) $GLOBALS['cc_ath_lang'] = $_GET['lang'];
    $lang = $GLOBALS['cc_ath_lang'];
    $first = $me->first_name ?: $me->display_name;
    // personal numbers: days since the login was made, and reports in their page
    $vu = $view ? get_userdata((int) get_post_meta($view, 'cc_user', true)) : null;
    $since = $vu ? $vu->user_registered : $me->user_registered;
    $days = max(1, (int) floor((time() - strtotime($since . ' UTC')) / DAY_IN_SECONDS) + 1);
    $mineHtml = $view ? cc_ath_dress(trim(cc_ath_content($view))) : '';
    $nrep = substr_count($mineHtml, 'class="ath-file"');
    $o .= '<header class="ath-hero"><div class="ath-hero-txt"><p class="eyebrow">' . cc_t('Athlete area') . ($coach ? cc_t(' · coach view') : '') . '</p>'
        // Matteo 17 Nov: the athlete's own round photo by the greeting (initials + camera until they add one; tap to add or change)
        . (!$coach && $view && function_exists('cc_ph_widget') ? '<div class="ath-hello">' . cc_ph_widget($view, 72, true, 'ath-me-ph') : '')
        // Matteo 17 Nov: the comma stays glued to the greeting (it slipped out of sight on phones)
        . '<h1><span class="ath-gw"><span class="ath-greet" data-l="' . $lang . '" data-g="' . esc_attr(wp_json_encode([cc_L('Good morning', 'Buongiorno'), cc_L('Good afternoon', 'Buon pomeriggio'), cc_L('Good evening', 'Buonasera')])) . '">' . cc_t('Welcome') . '</span>,</span> ' . '<span class="ath-nm">' . ($coach ? '<span class="ath-coach-tag">Coach</span>&nbsp;' : '') . esc_html($first) . '</span></h1>'
        . (!$coach && $view && function_exists('cc_ph_widget') ? '</div>' . cc_ph_assets() : '')
        // Matteo 17 Nov: his own view drops the athlete line; both get live chips instead (what is new, the next race)
        . ($coach ? '' : '<p class="ath-lede">' . cc_t('Everything for your coaching in one place. Train smarter. Ride faster.') . '</p>')
        . cc_ath_live_chips($coach ? 0 : $view, $coach, $coach ? 0 : $nrep)
        . '<div class="ath-links"><a class="ath-out" href="' . esc_url(wp_logout_url($url)) . '">' . cc_t('Log out') . '</a>' . apply_filters('cc_ath_hero_links', '', $coach) . '</div></div>'   // Matteo 17 Nov: the links in one tidy row
        . '<div class="ath-hero-me">' . cc_ath_sig_photo() . '</div></header>';
    // Matteo 17 Nov: "Change my availability" / "Add or change my goals & events" open their own page (?my=availability|goals); the hub shows a short summary
    $sub = (!$coach && $view && isset($_GET['my'])) ? sanitize_key($_GET['my']) : '';
    if ($sub !== '' && ($sp = apply_filters('cc_ath_subpage', '', $sub, $view)) !== '')
        return $o . '<p class="ath-back"><a href="' . esc_url($url) . '">← ' . esc_html(cc_ath_w('back')) . '</a></p>' . $sp . '</div>' . cc_ath_js();
    if ($coach) {
        $list = get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'orderby' => 'title', 'order' => 'ASC', 'meta_key' => 'cc_user']);
        // Matteo 17 Nov: his own demo page (no login, his own Vekta data), first in the list
        $list = array_merge(get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'meta_key' => 'cc_demo', 'meta_value' => '1']), $list);
        // Matteo 17 Nov: a calmer athlete list: one tidy grid (same-size rows, every face or initials), a search box, and folded away while he looks at one athlete
        $cur = ($view && $view !== $mine) ? get_the_title($view) : '';
        $o .= '<div class="ath-coach"><details class="ath-roster"' . ($cur === '' ? ' open' : '') . '><summary><span class="ath-ro-h">Your athletes <small>' . count($list) . '</small></span>'
            . ($cur !== '' ? '<span class="ath-ro-cur">' . (function_exists('cc_ph_widget') ? cc_ph_widget($view, 26, false, 'ath-lf') : '') . esc_html($cur) . '</span><span class="ath-ro-ch">Change athlete</span>' : '') . '</summary>'
            . '<input type="search" class="ath-ro-q" placeholder="Find an athlete…" aria-label="Find an athlete" autocomplete="off"><div class="ath-list">';
        foreach ($list as $p) $o .= '<a href="' . esc_url(add_query_arg('view', $p->ID, $url)) . '"' . ($view === $p->ID ? ' aria-current="page"' : '') . ' data-q="' . esc_attr(strtolower(remove_accents($p->post_title))) . '">' . (function_exists('cc_ph_widget') ? cc_ph_widget($p->ID, 30, false, 'ath-lf') : '') . '<span class="ath-ln">' . esc_html($p->post_title) . '</span>'
            . cc_ath_flag_for($p->ID) . (get_post_meta($p->ID, 'cc_demo', true) ? ' <small style="opacity:.75">demo</small>' : '') . '</a>';
        $o .= ($list ? '</div>' : '<span>No athletes yet.</span></div>') . '</details>'
            . '<script>(function(){var q=document.querySelector(".ath-ro-q");if(!q)return;q.addEventListener("input",function(){var v=q.value.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"").trim();'
            . 'document.querySelectorAll(".ath-roster .ath-list a").forEach(function(a){a.hidden=v!==""&&a.dataset.q.indexOf(v)<0;});});})();</script>' . (function_exists('cc_ph_assets') ? cc_ph_assets() : '') . (($tl = apply_filters('cc_ath_coach_links', '')) !== '' ? '<div class="ath-coach-tools"><span class="ath-coach-tl">Your coach tools</span>' . $tl . '</div>' : '') . '</div>';
        // coach-only pages (e.g. ?board=availability, from availability.php); empty unless a module adds one
        $board = isset($_GET['board']) ? sanitize_key($_GET['board']) : '';
        if ($board !== '' && ($b = apply_filters('cc_ath_board', '', $board)) !== '') return $o . cc_ath_find() . $b . '</div>' . cc_ath_js();
    }
    $hub = ($shared = cc_ath_shared_page($lang)) ? cc_ath_sections(cc_ath_dress(cc_ath_content($shared))) : ['', []];
    if (cc_ath_tp($view)) {   // TrainingPeaks athlete: the Vekta section of the shared hub becomes a TrainingPeaks card (same place, same title)
        $hub[0] = preg_replace_callback('~<section class="ath-s" id="([^"]+)"><h2>(.*?)</h2><div class="ath-body">(?:(?!</section>).)*?app\.joinvekta\.com(?:(?!</section>).)*</section>~s', function ($m) {
            return '<section class="ath-s" id="' . $m[1] . '"><h2>' . $m[2] . '</h2><div class="ath-body"><p>' . esc_html(cc_ath_w('tp_card')) . '</p>'
                . cc_ath_dress('<div class="wp-block-buttons"><div class="wp-block-button is-style-outline"><a class="wp-block-button__link wp-element-button" href="https://app.trainingpeaks.com/" target="_blank" rel="noreferrer noopener">' . esc_html(cc_ath_w('tp_open')) . '</a></div></div>') . '</div></section>';
        }, $hub[0]);
        // Matteo 17 Nov: any other section that only works with Vekta ("Share your rides": Vekta app steps + video) goes, with its menu link
        $gone = [];
        $hub[0] = preg_replace_callback('~<section class="ath-s" id="([^"]+)">(?:(?!</section>).)*</section>~s', function ($m) use (&$gone) {
            if (stripos(wp_strip_all_tags($m[0]), 'vekta') === false) return $m[0];
            $gone[] = $m[1]; return '';
        }, $hub[0]);
        $hub[1] = array_values(array_filter($hub[1], function ($n) use ($gone) { return !in_array($n[0], $gone, true); }));
    }
    $nav = [['reports', cc_t('Your reports')]];
    foreach ($hub[1] as $s) $nav[] = $s;
    $nav = apply_filters('cc_ath_nav', $nav, $view, $coach);   // modules add their own sections (availability.php)
    $o .= '<nav class="ath-jump" aria-label="' . cc_t('Sections') . '">';
    foreach ($nav as $n) $o .= '<a href="#' . esc_attr($n[0]) . '">' . esc_html($n[1]) . '</a>';
    $o .= '</nav>';
    // Matteo 17 Nov: each menu link gets a small copy of its section's icon (taken from the section, so they always match)
    $o .= '<script>addEventListener("DOMContentLoaded",function(){document.querySelectorAll(".ath-jump a[href^=\'#\']").forEach(function(a){var s=document.getElementById(a.getAttribute("href").slice(1)),i=s&&s.querySelector("h2 .ath-hic");if(!i)return;var c=i.cloneNode(true);c.classList.remove("ath-hic");c.classList.add("ath-jic");c.removeAttribute("id");a.insertBefore(c,a.firstChild);});});</script>'
        . '<style>html .cc .ath-jump a{display:inline-flex;align-items:center;gap:7px}html .cc .ath-jump .ath-jic{flex:none;width:24px;height:24px;border-radius:7px;display:inline-grid;place-items:center;background:rgba(18,161,80,.15);border:1px solid rgba(43,212,122,.35)}'
        . 'html .cc .ath-jump .ath-jic svg{width:13px;height:13px;fill:none;stroke:var(--green-text,#2bd47a);stroke-width:2;stroke-linecap:round;stroke-linejoin:round}html .cc .ath-jump .ath-jic.ath-logo{background-size:62%;background-repeat:no-repeat;background-position:center}</style>';
    $o .= apply_filters('cc_ath_before_reports', '', $view, $coach);   // reports.php: "Your season" card, "N new reports"
    $rx = apply_filters('cc_ath_reports_html', '', $view, $coach);      // reports.php: reports sent from Matteo's PC tools
    $o .= '<section class="ath-s ath-mine" id="reports"><h2>' . cc_ath_icon('reports', 'ath-hic') . cc_t('Your reports') . '</h2>'
        . ($mineHtml !== '' || $rx !== '' ? $rx . ($mineHtml !== '' ? '<div class="ath-body">' . $mineHtml . '</div>' : '')
           : '<div class="ath-empty">' . cc_ath_icon('doc') . '<p>' . (cc_ath_tp($view) ? esc_html(cc_ath_w('tp_empty')) : cc_t('Your first assessment, reviews and progress reports will appear here. I will let you know when there is something new.')) . '</p></div>')
        . '</section>';
    $o .= apply_filters('cc_ath_after_reports', '', $view, $coach);
    $o .= $hub[0];
    $o .= apply_filters('cc_ath_end', '', $view, $coach);   // ideas.php: "Ideas for your hub", the last box
    return $o . '</div>' . cc_ath_js();
}

/* ---------- [cc_latest_posts lang="en|it" n="4"] in the shared hubs (Matteo 16 Nov): the newest posts appear by themselves.
   English hub: newest posts outside the "Italiano" category; Italian hub: newest Italiano posts. The list of /blog/ links
   becomes photo cards (cc_ath_dress), like the hand-picked reading list. ---------- */
add_shortcode('cc_latest_posts', function ($at) {
    $at = shortcode_atts(['lang' => 'en', 'n' => 4], $at);
    $it = get_term_by('name', 'Italiano', 'category');
    // the Simple Custom Post Order plugin imposes its own order on queries, so take them all (about 70) and sort by date here
    $q = ['numberposts' => -1, 'post_status' => 'publish'];
    if ($it) $q[$at['lang'] === 'it' ? 'category__in' : 'category__not_in'] = [$it->term_id];
    $ps = get_posts($q); usort($ps, function ($a, $b) { return strcmp($b->post_date, $a->post_date); });
    $li = '';
    foreach (array_slice($ps, 0, max(1, min(8, (int) $at['n']))) as $p) $li .= '<li><a href="' . esc_url(get_permalink($p)) . '">' . esc_html(get_the_title($p)) . '</a></li>';
    if (!$li) return '';
    return '<ul class="wp-block-list">' . $li . '</ul><p class="ath-allposts"><a href="' . esc_url(home_url('/blog/')) . '">' . esc_html($at['lang'] === 'it' ? 'Tutti gli articoli del blog →' : cc_L('All blog posts →', 'Tutti gli articoli del blog →')) . '</a></p>';
});

/* ---------- the dashboard look ---------- */
function cc_ath_icon($k, $cls = 'ath-ic') {
    static $I = [
        'calendar' => '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/><path d="M8 14h3v3H8z"/>',
        'mic' => '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3M9 21h6"/>',   // notes.php
        'trophy' => '<path d="M8 4h8v5a4 4 0 0 1-8 0z"/><path d="M8 6H5a2.5 2.5 0 0 0 3 4M16 6h3a2.5 2.5 0 0 1-3 4M12 13v4M8.5 21h7M10 17h4v4h-4z"/>',   // results.php
        'food' => '<path d="M12 7.5c-1.6-1.4-4.3-1.9-5.8-.2C4 9.8 5 15.4 7.9 19.2c1.3 1.6 2.7 1.9 4.1.9 1.4 1 2.8.7 4.1-.9 2.9-3.8 3.9-9.4 1.7-11.9-1.5-1.7-4.2-1.2-5.8.2z"/><path d="M12 7.5c0-2.2.9-4 3-4.5"/>',
        'chat' => '<path d="M20.5 11.5a8.5 8.5 0 0 1-12.4 7.6L3.5 20.5l1.4-4.4A8.5 8.5 0 1 1 20.5 11.5z"/><path d="M8.5 11.5h.01M12 11.5h.01M15.5 11.5h.01"/>',
        'people' => '<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6M15.5 14.6c2.8.2 5 2.2 5 5.4"/>',
        'bolt' => '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
        'idea' => '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.7.6 1.1 1.4 1.1 2.2h5c0-.8.4-1.6 1.1-2.2A6 6 0 0 0 12 3z"/>',   // the ideas box
        'peaks' => '<path d="M2 20l6.5-10 4 5.5 3-4L22 20z"/><path d="M8.5 10l1.8 2.6"/>',
        'doc' => '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
        'link' => '<path d="M7 17L17 7M9 7h8v8"/>',
        'phone' => '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
        'gauge' => '<path d="M12 14l4-4"/><path d="M3.5 18a9 9 0 1 1 17 0"/>',
        'book' => '<path d="M4 4h6a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H4z"/><path d="M20 4h-6a3 3 0 0 0-3 3v13a2 2 0 0 1 2-2h7z"/>',
        'reports' => '<path d="M3 3v18h18"/><path d="M7 14l4-4 3 3 5-6"/>',
        'zones' => '<path d="M3 3v18h18"/><path d="M7 15v3M11 11v7M15 8v10M19 5v13"/>',
        'carbs' => '<path d="M12 2v4M5 7l2.5 2.5M19 7l-2.5 2.5"/><rect x="7" y="9" width="10" height="13" rx="3"/><path d="M7 14h10"/>',
        'cp' => '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
        'climb' => '<path d="M2 20h20L14 6l-4 6-2-3-6 11z"/><path d="M14 6l2 3"/>',
        'sweat' => '<path d="M12 2.7l5.7 5.6a8 8 0 1 1-11.4 0z"/>',
        'ftp' => '<circle cx="12" cy="13" r="8"/><path d="M12 13l4-4M12 3V1M9 1h6"/>',
        'gear' => '<circle cx="12" cy="12" r="3"/><path d="M12 1v4M12 19v4M4.2 4.2l2.8 2.8M17 17l2.8 2.8M1 12h4M19 12h4M4.2 19.8L7 17M17 7l2.8-2.8"/>',
        'play' => '<rect x="2" y="5" width="20" height="14" rx="4"/><path d="M10 9l5 3-5 3z"/>',   // Matteo 17 Nov: video routines as small cards
        'insta' => '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".6"/>',
        'swim' => '<path d="M2 18c2 0 2-1.5 4-1.5S8 18 10 18s2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/><path d="M2 13c2 0 2-1.5 4-1.5S8 13 10 13s2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/><circle cx="16" cy="5" r="2"/><path d="M6 9l4-3 3 3"/>',
    ];
    static $LOGO = [   // Matteo 17 Nov: real logos on the brand tiles (Vekta, WhatsApp, Vivify); the catch-up call keeps its calendar icon
        'logo-vekta' => 'data:image/png;base64,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',
        'logo-whatsapp' => 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzMiAzMiI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTE2IDNDOC44IDMgMyA4LjcgMyAxNS44YzAgMi41LjcgNC45IDIgN0wzIDI5bDYuNC0yYzIgMS4xIDQuMyAxLjcgNi42IDEuNyA3LjIgMCAxMy01LjcgMTMtMTIuOFMyMy4yIDMgMTYgM3ptMCAyMy40Yy0yLjEgMC00LjEtLjYtNS45LTEuN2wtLjQtLjMtMy44IDEuMiAxLjItMy43LS4zLS40QzUuNiAxOS44IDUgMTcuOCA1IDE1LjggNSA5LjkgOS45IDUuMiAxNiA1LjJzMTEgNC43IDExIDEwLjYtNC45IDEwLjYtMTEgMTAuNnoiLz48cGF0aCBmaWxsPSIjZmZmIiBkPSJNMjIuMSAxOC42Yy0uMy0uMi0yLTEtMi4zLTEuMS0uMy0uMS0uNS0uMi0uNy4yLS4yLjMtLjggMS0xIDEuMi0uMi4yLS40LjItLjcuMS0uMy0uMi0xLjQtLjUtMi43LTEuNi0xLS45LTEuNy0yLTEuOS0yLjMtLjItLjMgMC0uNS4xLS43bC41LS42Yy4yLS4yLjItLjMuMy0uNi4xLS4yIDAtLjQgMC0uNmwtMS0yLjRjLS4zLS42LS41LS41LS43LS41aC0uNmMtLjIgMC0uNi4xLS45LjQtLjMuMy0xLjIgMS4xLTEuMiAyLjhzMS4yIDMuMiAxLjQgMy41Yy4yLjIgMi40IDMuNiA1LjggNSAuOC4zIDEuNC41IDEuOS43LjguMyAxLjYuMiAyLjIuMS43LS4xIDItLjggMi4zLTEuNi4zLS44LjMtMS41LjItMS42LS4xLS4yLS4zLS4zLS42LS40eiIvPjwvc3ZnPg==',
        'logo-vivify' => 'https://coaching.cigalacycling.com/wp-content/uploads/2026/11/vivify-tile.png',   // Matteo 17 Nov: the green Vivify Sports logo
        'logo-skool' => 'data:image/png;base64,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',
        // TrainingPeaks app icon, from the official logo pack (TrainingPeaks_Logos_Late25, "3 - TrainingPeaks_Icon"), Matteo 17 Nov
        'logo-tp' => 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTc4IiBoZWlnaHQ9IjE3OCIgdmlld0JveD0iMCAwIDE3OCAxNzgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGcgY2xpcC1wYXRoPSJ1cmwoI2NsaXAwXzlfNDYwNSkiPjxwYXRoIGQ9Ik0xODguODEgLTExLjc1NzRILTExLjc1NzRWMTg4LjgxSDE4OC44MVYtMTEuNzU3NFoiIGZpbGw9IiMwMTBGMzEiLz48cGF0aCBkPSJNNjcuNjExNyA1Ni41MzkzSDQ3Ljk4TDM2LjgxNzUgODIuMjgyMUg1Ni40OTgyTDY3LjYxMTcgNTYuNTM5M1oiIGZpbGw9IiMzMTc3RkYiLz48cGF0aCBkPSJNMTIzLjM3OSA1MC4yMzYzTDEwMS45NjcgOTguODMyOEgxMjEuNTk4TDE0My4wNiA1MC4yMzYzSDEyMy4zNzlaIiBmaWxsPSIjMzE3N0ZGIi8+PHBhdGggZD0iTTEwMS42MyAzMy42ODM3SDgxLjk5ODFMNDcuMzA2MiAxMTIuNjQzSDY2Ljk4NjlMMTAxLjYzIDMzLjY4MzdaIiBmaWxsPSIjMzE3N0ZGIi8+PHBhdGggZD0iTTk2LjI4ODUgNTYuNTM5M0w2MS42NDU2IDEzNS40OTdIODEuMjc3M0wxMTUuOTY5IDU2LjUzOTNIOTYuMjg4NVoiIGZpbGw9IiMzMTc3RkYiLz48L2c+PGRlZnM+PGNsaXBQYXRoIGlkPSJjbGlwMF85XzQ2MDUiPjxyZWN0IHdpZHRoPSIxNzcuMDUzIiBoZWlnaHQ9IjE3Ny4wNTMiIGZpbGw9IndoaXRlIi8+PC9jbGlwUGF0aD48L2RlZnM+PC9zdmc+',
        'logo-youtube' => 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzMiAzMiI+PHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiBmaWxsPSIjRkYwMDAwIi8+PHBhdGggZD0iTTEyLjUgMTAuNWw5IDUuNS05IDUuNXoiIGZpbGw9IiNmZmYiLz48L3N2Zz4=',   // red fills the whole tile
        'logo-instagram' => 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzMiAzMiI+PGRlZnM+PHJhZGlhbEdyYWRpZW50IGlkPSJnIiBjeD0iMzAlIiBjeT0iMTA3JSIgcj0iMTUwJSI+PHN0b3Agb2Zmc2V0PSIwIiBzdG9wLWNvbG9yPSIjZmRmNDk3Ii8+PHN0b3Agb2Zmc2V0PSIuMDUiIHN0b3AtY29sb3I9IiNmZGY0OTciLz48c3RvcCBvZmZzZXQ9Ii40NSIgc3RvcC1jb2xvcj0iI2ZkNTk0OSIvPjxzdG9wIG9mZnNldD0iLjYiIHN0b3AtY29sb3I9IiNkNjI0OWYiLz48c3RvcCBvZmZzZXQ9Ii45IiBzdG9wLWNvbG9yPSIjMjg1QUVCIi8+PC9yYWRpYWxHcmFkaWVudD48L2RlZnM+PHJlY3Qgd2lkdGg9IjMyIiBoZWlnaHQ9IjMyIiBmaWxsPSJ1cmwoI2cpIi8+PHJlY3QgeD0iOCIgeT0iOCIgd2lkdGg9IjE2IiBoZWlnaHQ9IjE2IiByeD0iNSIgZmlsbD0ibm9uZSIgc3Ryb2tlPSIjZmZmIiBzdHJva2Utd2lkdGg9IjIiLz48Y2lyY2xlIGN4PSIxNiIgY3k9IjE2IiByPSIzLjgiIGZpbGw9Im5vbmUiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIyIi8+PGNpcmNsZSBjeD0iMjEiIGN5PSIxMSIgcj0iMS4yIiBmaWxsPSIjZmZmIi8+PC9zdmc+',
    ];
    if (isset($LOGO[$k])) return '<span class="' . $cls . ' ath-logo ' . $k . '" aria-hidden="true" style="background-image:url(' . $LOGO[$k] . ')"></span>';
    return '<span class="' . $cls . '" aria-hidden="true"><svg viewBox="0 0 24 24">' . ($I[$k] ?? $I['link']) . '</svg></span>';
}
// what a link is, from where it goes: [icon, line under the title]; Matteo can edit the hub freely and the cards follow
function cc_ath_kind($href) {
    $m = [['cal.com/', 'calendar', 'Pick a time that suits you'], ['calendly.com', 'calendar', 'Pick a time that suits you'], ['vivifysports', 'logo-vivify', 'Your one-off consult with Marine Lenehan, sports nutritionist'],
          ['wa.me', 'logo-whatsapp', 'I usually reply within a few hours'], ['skool.com', 'logo-skool', 'Free for coaching clients'],
          ['vekta', 'logo-vekta', 'Your plan, workouts and analysis'], ['trainingpeaks', 'logo-tp', 'Your plan and workouts'],
          ['training-zones', 'zones', ''], ['carbs-per-hour', 'carbs', ''], ['critical-power', 'cp', ''], ['ftp-test', 'ftp', ''],
          ['sweat-rate', 'sweat', ''], ['climb-time', 'climb', ''], ['gear-speed', 'gear', ''], ['swim-pace', 'swim', ''], ['.pdf', 'doc', ''],
          ['youtube.com/playlist', 'logo-youtube', 'YouTube'], ['instagram.com/reel/', 'play', 'Instagram'], ['instagram.com', 'logo-instagram', '@cigalacycling']];
    foreach ($m as $x) if (stripos($href, $x[0]) !== false) return [$x[1], $x[2] === '' ? '' : cc_t($x[2])];
    return ['link', ''];
}
function cc_ath_attr($attrs, $name) { return preg_match('/\b' . $name . '="([^"]*)"/', $attrs, $m) ? html_entity_decode($m[1]) : ''; }
function cc_ath_dress($html) {
    if ($html === '') return '';
    // buttons -> icon cards
    $html = preg_replace_callback('#<div class="wp-block-button[^"]*">\s*<a ([^>]*)>(.*?)</a>\s*</div>#s', function ($m) {
        $href = cc_ath_attr($m[1], 'href'); $t = cc_ath_attr($m[1], 'target');
        [$ic, $sub] = cc_ath_kind($href);
        return '<a class="ath-tile" href="' . esc_url($href) . '"' . ($t ? ' target="_blank" rel="noopener"' : '') . '>' . cc_ath_icon($ic)
             . '<span class="ath-tt"><b>' . wp_strip_all_tags($m[2]) . '</b>' . ($sub ? '<small>' . esc_html($sub) . '</small>' : '') . '</span><span class="ath-go" aria-hidden="true">→</span></a>';
    }, $html);
    // file blocks (PDFs) -> download cards
    $html = preg_replace_callback('#<div class="wp-block-file"[^>]*>(.*?)</div>#s', function ($m) {
        if (!preg_match('#<a ([^>]*)>(.*?)</a>#s', $m[1], $a)) return $m[0];
        $href = cc_ath_attr($a[1], 'href'); $name = trim(wp_strip_all_tags($a[2])) ?: cc_t('Document');
        return '<a class="ath-file" href="' . esc_url($href) . '" target="_blank" rel="noopener">' . cc_ath_icon('doc')
             . '<span class="ath-tt"><b>' . esc_html($name) . '</b><small>' . cc_t('PDF · opens in a new tab') . '</small></span><span class="ath-dl">' . cc_t('Open') . '</span></a>';
    }, $html);
    // lists of blog links -> photo cards
    $html = preg_replace_callback('#<ul class="wp-block-list">(.*?)</ul>#s', function ($m) {
        if (!preg_match_all('#<li>\s*<a href="([^"]+)"[^>]*>(.*?)</a>\s*</li>#s', $m[1], $li, PREG_SET_ORDER)) return $m[0];
        if (count($li) !== substr_count($m[1], '<li')) return $m[0];
        $out = '';
        foreach ($li as $x) {
            $href = html_entity_decode($x[1]); if (strpos($href, '/blog/') === false) return $m[0];
            $pid = url_to_postid(strpos($href, 'http') === 0 ? $href : home_url($href));
            $img = $pid ? get_the_post_thumbnail_url($pid, 'medium_large') : '';
            $min = $pid ? max(2, (int) round(str_word_count(wp_strip_all_tags(get_post_field('post_content', $pid))) / 220)) : 0;
            $out .= '<a class="ath-read" href="' . esc_url($href) . '"><span class="ath-read-img"' . ($img ? ' style="background-image:url(' . esc_url($img) . ')"' : '') . '></span>'
                  . '<span class="ath-read-t">' . wp_strip_all_tags($x[2]) . '</span>' . ($min ? '<small>' . $min . ' ' . cc_t('min read') . '</small>' : '') . '</a>';
        }
        return '<div class="ath-reads">' . $out . '</div>';
    }, $html);
    return $html;
}
// split the hub at each H2 into its own animated card, with an icon and an anchor for the jump menu
function cc_ath_sections($html) {
    $parts = preg_split('#(<h2[^>]*>.*?</h2>)#s', $html, -1, PREG_SPLIT_DELIM_CAPTURE | PREG_SPLIT_NO_EMPTY);
    $out = ''; $nav = []; $open = false;
    $icons = [['quick', 'bolt'], ['rapid', 'bolt'], ['app', 'phone'], ['guide', 'doc'], ['guida', 'doc'], ['pdf', 'doc'], ['tool', 'gauge'], ['strument', 'gauge'], ['read', 'book'], ['lettur', 'book'], ['legg', 'book'], ['blog', 'book']];
    foreach ($parts as $p) {
        if (preg_match('#^<h2[^>]*>(.*?)</h2>$#s', $p, $h)) {
            if ($open) $out .= '</div></section>';
            $title = trim(wp_strip_all_tags($h[1])); $id = sanitize_title($title) ?: 'section';
            $ic = 'link'; foreach ($icons as $x) if (stripos($title, $x[0]) !== false) { $ic = $x[1]; break; }
            $out .= '<section class="ath-s" id="' . esc_attr($id) . '"><h2>' . cc_ath_icon($ic, 'ath-hic') . esc_html($title) . '</h2><div class="ath-body">';
            $nav[] = [$id, $title]; $open = true;
        } else {
            $out .= $open ? $p : '<section class="ath-s"><div class="ath-body">' . $p . '</div></section>';
        }
    }
    if ($open) $out .= '</div></section>';
    return [$out, $nav];
}
/* Matteo 17 Nov: a livelier header. Athletes: the countdown to their next race, what is new for them, their reports.
 * Matteo: what is waiting for him (new notes, results, forms, ideas, signups), each opening its board. */
function cc_ath_live_w($k, $n = 0) {
    static $W = [
        'today' => ['en' => 'Today', 'it' => 'Oggi', 'pt' => 'Hoje', 'sl' => 'Danes'],
        'tomorrow' => ['en' => 'Tomorrow', 'it' => 'Domani', 'pt' => 'Amanhã', 'sl' => 'Jutri'],
        'day' => ['en' => ['day', 'days'], 'it' => ['giorno', 'giorni'], 'pt' => ['dia', 'dias'], 'sl' => ['dan', 'dni']],
        'new' => ['en' => ['new notification', 'new notifications'], 'it' => ['nuova notifica', 'nuove notifiche'], 'pt' => ['nova notificação', 'novas notificações'], 'sl' => ['novo obvestilo', 'nova obvestila']],
        'rep' => ['en' => ['report in your folder', 'reports in your folder'], 'it' => ['report nella tua cartella', 'report nella tua cartella'], 'pt' => ['relatório na tua pasta', 'relatórios na tua pasta'], 'sl' => ['poročilo v tvoji mapi', 'poročil v tvoji mapi']],
    ];
    $l = $GLOBALS['cc_ath_lang'] ?? 'en'; $v = $W[$k][$l] ?? $W[$k]['en'];
    if (!is_array($v)) return $v;
    if ($k === 'day' && $l === 'sl') return $n === 1 ? 'dan' : ($n === 2 ? 'dneva' : ($n <= 4 ? 'dnevi' : 'dni'));
    if ($k === 'new' && $l === 'sl') return $n === 1 ? 'novo obvestilo' : ($n === 2 ? 'novi obvestili' : ($n <= 4 ? 'nova obvestila' : 'novih obvestil'));
    return $n === 1 ? $v[0] : $v[1];
}
function cc_ath_live_chips($view, $coach, $nrep) {
    $uid = get_current_user_id(); $in = function_exists('cc_inbox_get') ? cc_inbox_get($uid) : [];
    $unread = array_filter($in, function ($x) { return empty($x['read']); });
    $chip = function ($n, $txt, $href = '', $cls = '') { $b = '<b class="ath-n" data-n="' . (int) $n . '">' . (int) $n . '</b> ' . esc_html($txt);
        return $href ? '<a class="ath-chip ' . $cls . '" href="' . esc_url($href) . '">' . $b . '</a>' : '<span class="ath-chip ' . $cls . '">' . $b . '</span>'; };
    $o = '';
    if ($coach) {
        $hub = home_url('/' . CC_ATH_SLUG . '/');
        $kinds = ['cc-note' => ['notes', 'new note', 'new notes'], 'cc-result' => ['results', 'new result', 'new results'], 'cc-form' => ['forms', 'form signed', 'forms signed'],
                  'cc-idea' => ['ideas', 'new idea', 'new ideas'], 'cc-new' => ['contracts', 'new athlete', 'new athletes']];
        foreach ($kinds as $tag => [$board, $one, $many]) {
            $n = count(array_filter($unread, function ($x) use ($tag) { return ($x['tag'] ?? '') === $tag || strpos((string) ($x['tag'] ?? ''), $tag . '-') === 0; }));
            if ($n) $o .= $chip($n, $n === 1 ? $one : $many, add_query_arg('board', $board, $hub), 'ath-chip-go');
        }
        if ($o === '') $o = '<span class="ath-chip ath-chip-ok">✓ All caught up</span>';
        return '<div class="ath-chips ath-live">' . $o . '</div>';
    }
    // the next race or event (within a year; Matteo 17 Nov: a July race in November must show), with its priority colour
    $g = $view && function_exists('cc_g_get') ? cc_g_get($view) : null; $today = current_time('Y-m-d');
    foreach ((array) ($g['events'] ?? []) as $e) {
        if (($e['date'] ?? '') < $today) continue;
        $d = (int) round((strtotime($e['date'] . ' 12:00') - strtotime($today . ' 12:00')) / DAY_IN_SECONDS); if ($d > 366) break;
        $p = strtolower($e['prio'] ?? 'b'); $pri = '<i class="ath-pri ath-pri-' . esc_attr($p) . '">' . esc_html(strtoupper($p)) . '</i>';
        $o .= '<a class="ath-chip ath-chip-race" href="#goals">' . $pri . ($d <= 1 ? '<b>' . esc_html(cc_ath_live_w($d ? 'tomorrow' : 'today')) . '</b> '
            : '<b class="ath-n" data-n="' . $d . '">' . $d . '</b> ' . esc_html(cc_ath_live_w('day', $d))) . ' <span class="ath-chip-nm">' . esc_html($e['name']) . '</span></a>';
        break;
    }
    if ($n = count($unread)) $o .= $chip($n, cc_ath_live_w('new', $n), '#', 'ath-chip-go ath-chip-bell');
    if ($nrep) $o .= $chip($nrep, cc_ath_live_w('rep', $nrep), '#reports');
    return $o !== '' ? '<div class="ath-chips ath-live">' . $o . '</div>' : '';
}
function cc_ath_sig_photo() {
    $u = content_url('/uploads/2026/11/');
    return '<span class="sigph"><img src="' . esc_url($u . 'cigala-coaching-about-hero-matteo-photo.webp') . '" alt="' . esc_attr(cc_t('Matteo Cigala, your coach, in the white Cigala Cycling jersey')) . '" width="720" height="933">'
         . '<img class="signature" src="' . esc_url($u . 'cigala-coaching-matteo-cigala-signature.webp') . '" alt="" aria-hidden="true" width="720" height="933"><span class="sig-anchor" aria-hidden="true"></span></span>';
}
/* Matteo 17 Nov: a microphone on the open text boxes of the rider form and of Goals & events. Tap, speak, the words appear in the box
 * (the browser's own speech-to-text, in the athlete's language; nothing is recorded or sent to the site). Hidden where the browser can't do it. */
add_action('wp_footer', function () {
    if (!is_page(CC_ATH_SLUG) || !is_user_logged_in()) return;
    $l = cc_ath_lang_code(get_current_user_id()); $speech = defined('CC_AV_SPEECH') ? (CC_AV_SPEECH[$l] ?? 'en-GB') : 'en-GB';
    $cfg = wp_json_encode(['lang' => $speech, 'w' => ['mic' => cc_ath_w('mic', $l), 'on' => cc_ath_w('mic_on', $l), 'denied' => cc_ath_w('mic_denied', $l), 'none' => cc_ath_w('mic_none', $l)]]);
    // Matteo 17 Nov (Marine's phone test): answer boxes were small on phones; they start taller and grow with what is written or spoken
    echo '<style id="cc-grow">#rf textarea,#gl-app textarea,#av-note{min-height:120px;line-height:1.5;resize:vertical;overflow:hidden}'
       . '@media(max-width:640px){#rf textarea,#gl-app textarea,#av-note{min-height:150px}}</style>'
       . '<script>(function(){function g(t){if(!t.offsetParent)return;t.style.height="auto";t.style.height=(t.scrollHeight+2)+"px";}'
       . 'function all(){document.querySelectorAll("#rf textarea,#gl-app textarea,#av-note").forEach(function(t){if(t.value)g(t);});}'
       . 'document.addEventListener("input",function(e){var t=e.target;if(t.matches&&t.matches("#rf textarea,#gl-app textarea,#av-note"))g(t);},true);'
       . 'all();document.addEventListener("click",function(e){if(e.target.closest&&e.target.closest(".rf-next,.rf-back"))setTimeout(all,50);});'
       . 'var q=0;new MutationObserver(function(){if(q)return;q=requestAnimationFrame(function(){q=0;all();});}).observe(document.body,{childList:true,subtree:true});})();</script>';
    echo '<style id="cc-mic">.cc-micw{position:relative;display:block}.cc-micw textarea{padding-right:58px!important}.cc-micw input{padding-right:52px!important}'
       . '.cc-mic{position:absolute;right:8px;bottom:8px;width:42px;height:42px;min-height:0!important;padding:0!important;margin:0!important;border-radius:50%!important;border:0!important;background:#018a44!important;display:grid;place-items:center;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,.4)}'
       . '.cc-micw input~.cc-mic{top:50%;bottom:auto;transform:translateY(-50%);width:36px;height:36px}'
       . '.cc-mic svg{width:20px;height:20px;fill:none;stroke:#fff;stroke-width:2;stroke-linecap:round}.cc-mic.on{background:#ca212a!important;animation:ccmic 1.2s ease-in-out infinite}'
       . '@keyframes ccmic{0%,100%{box-shadow:0 0 0 0 rgba(202,33,42,.6)}50%{box-shadow:0 0 0 8px rgba(202,33,42,0)}}'
       . '.cc-mic-msg{display:block;margin-top:6px;font-size:14px;color:#d0d6e0}.cc-mic-msg:empty{display:none}</style>'
       . '<script>(function(){var SR=window.SpeechRecognition||window.webkitSpeechRecognition;if(!SR)return;var C=' . $cfg . ',cur=null;'
       . 'var ico=\'<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/></svg>\';'
       . 'function msg(w,t){var m=w.nextElementSibling;if(!m||!m.classList.contains("cc-mic-msg")){m=document.createElement("small");m.className="cc-mic-msg";w.parentNode.insertBefore(m,w.nextSibling);}m.textContent=t||"";}'
       . 'function stop(){if(cur){try{cur.sr.stop();}catch(x){}}}'
       . 'function start(b,el){stop();var w=b.parentNode,sr=new SR(),base=el.value?el.value.replace(/\s*$/,"")+" ":"",fin="";sr.lang=C.lang;sr.continuous=true;sr.interimResults=true;'
       . 'cur={sr:sr,b:b};b.classList.add("on");b.setAttribute("aria-pressed","true");msg(w,C.w.on);'
       . 'sr.onresult=function(e){var tmp="";for(var i=e.resultIndex;i<e.results.length;i++){if(e.results[i].isFinal)fin+=e.results[i][0].transcript;else tmp+=e.results[i][0].transcript;}'
       . 'el.value=(base+fin+tmp).replace(/\s+/g," ").replace(/^ /,"");el.dispatchEvent(new Event("input",{bubbles:true}));};'
       . 'sr.onerror=function(e){msg(w,(e.error==="not-allowed"||e.error==="service-not-allowed")?C.w.denied:(e.error==="no-speech"||e.error==="aborted"?"":C.w.none));};'
       . 'sr.onend=function(){b.classList.remove("on");b.setAttribute("aria-pressed","false");if(cur&&cur.b===b)cur=null;var m=w.nextElementSibling;if(m&&m.textContent===C.w.on)msg(w,"");el.dispatchEvent(new Event("change",{bubbles:true}));};'
       . 'try{sr.start();}catch(x){msg(w,C.w.none);}}'
       . 'function enhance(){document.querySelectorAll("#rf textarea, #gl-app textarea, #gl-app input.gl-no, #cc-idea textarea").forEach(function(el){if(el.dataset.mic||el.readOnly||el.disabled)return;el.dataset.mic="1";'
       . 'var w=document.createElement("span");w.className="cc-micw";el.parentNode.insertBefore(w,el);w.appendChild(el);var b=document.createElement("button");b.type="button";b.className="cc-mic";'
       . 'b.setAttribute("aria-label",C.w.mic);b.title=C.w.mic;b.setAttribute("aria-pressed","false");b.innerHTML=ico;w.appendChild(b);'
       . 'b.addEventListener("click",function(e){e.preventDefault();e.stopPropagation();if(cur&&cur.b===b){stop();return;}start(b,el);});});}'
       . 'enhance();var q=0;new MutationObserver(function(){if(q)return;q=requestAnimationFrame(function(){q=0;enhance();});}).observe(document.body,{childList:true,subtree:true});})();</script>';
}, 50);
/* Matteo 17 Nov: a search box on his boards (reports, availability, goals, rider forms): type part of a name, only matching rows stay */
function cc_ath_find() {
    return '<div class="ath-find"><label for="ath-find-q">Find an athlete</label><input id="ath-find-q" type="search" placeholder="Type a name…" autocomplete="off"><span class="ath-find-n" aria-live="polite"></span></div>'
        . '<style>html .cc .ath-find{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin:0 0 16px}html .cc .ath-find label{font-weight:700;color:#fff;font-size:15px}'
        . 'html .cc .ath-find input{flex:1 1 260px;max-width:420px;font:16px var(--body);padding:11px 14px;border-radius:999px;border:1px solid rgba(255,255,255,.2);background:#0b0d0f;color:#fff}'
        . 'html .cc .ath-find input:focus{outline:2px solid #018a44;outline-offset:1px}html .cc .ath-find-n{font-size:14px;color:#b8bec8}</style>'
        . '<script>(function(){var q=document.getElementById("ath-find-q");if(!q)return;var S=".rp-row,.av-tr:not(.av-th),.gl-row,.rf-pickrow,.rf-row";'
        . 'function norm(s){return (s||"").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"");}'
        . 'q.addEventListener("input",function(){var v=norm(q.value.trim()),n=0,all=0;document.querySelectorAll(S).forEach(function(r){if(r.parentNode.closest(S))return;all++;var ok=!v||norm(r.textContent).indexOf(v)>-1;r.style.display=ok?"":"none";if(ok)n++;});'
        . 'document.querySelector(".ath-find-n").textContent=v?(n+" of "+all):"";});})();</script>';
}
/* Matteo 17 Nov: hub emails landed in spam (Marine). The domain's SPF only allows Register365's Authenticated SMTP (and Elastic Email
 * behind it), not Hostinger. So every email from this site goes through smtp.reg365.net, signed in as cigalacycling.com, from
 * coaching@cigalacycling.com. The password is typed by Matteo in the Reports board ("Email sending"), kept in the option cc_smtp_pass,
 * never shown again. Until it is set, emails go out as before. */
const CC_SMTP = ['host' => 'smtp.reg365.net', 'port' => 587, 'user' => 'cigalacycling.com', 'from' => 'coaching@cigalacycling.com', 'name' => 'Cigala Cycling Coaching'];
add_action('phpmailer_init', function ($m) {
    $pw = (string) get_option('cc_smtp_pass', ''); if ($pw === '') return;
    if (!get_option('cc_smtp_ok') && empty($GLOBALS['cc_smtp_testing'])) return;   // only after a test succeeded: a wrong login must never stop the hub's emails
    $m->isSMTP(); $m->Host = CC_SMTP['host']; $m->Port = CC_SMTP['port']; $m->SMTPSecure = CC_SMTP['port'] === 465 ? 'ssl' : 'tls';
    $m->SMTPAuth = true;
    $m->Username = (string) get_option('cc_smtp_user', '') ?: CC_SMTP['user'];
    $m->Password = $pw; $m->Timeout = 20;
    // keep only the SERVER's replies (never what we send, so the login never ends up in the log), for the reason shown when a send fails
    $GLOBALS['cc_smtp_srv'] = []; $m->SMTPDebug = 2;
    $m->Debugoutput = function ($s) { if (strpos($s, 'SERVER -> CLIENT') !== false && count($GLOBALS['cc_smtp_srv']) < 40) $GLOBALS['cc_smtp_srv'][] = trim(substr($s, 0, 200)); };
    if (stripos((string) $m->From, '@cigalacycling.com') === false) { $m->From = CC_SMTP['from']; if ($m->FromName === '' || $m->FromName === 'WordPress') $m->FromName = CC_SMTP['name']; }
    $m->Sender = CC_SMTP['from'];
}, 99);
add_filter('wp_mail_from', function ($f) { return stripos($f, 'wordpress@') === 0 ? CC_SMTP['from'] : $f; }, 20);
// why a send failed (PHPMailer's message, never the password), shown in the box and to the hub chat (GET /cc/v1/smtp-status)
add_action('wp_mail_failed', function ($e) { $msg = is_wp_error($e) ? $e->get_error_message() : ''; $pw = (string) get_option('cc_smtp_pass', '');
    if ($pw !== '') $msg = str_replace($pw, '***', $msg);
    $srv = array_slice((array) ($GLOBALS['cc_smtp_srv'] ?? []), -6); if ($pw !== '') $srv = array_map(function ($l) use ($pw) { return str_replace($pw, '***', $l); }, $srv);
    update_option('cc_smtp_err', ['at' => time(), 'msg' => substr($msg, 0, 500), 'server' => $srv], false); });
add_action('rest_api_init', function () { register_rest_route('cc/v1', '/smtp-test', ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function () {
    $me = wp_get_current_user(); $GLOBALS['cc_smtp_testing'] = 1;   // the hub chat's test: always to the coach himself
    $ok = is_email($me->user_email) && wp_mail($me->user_email, 'Test: Cigala Cycling Coaching emails', '<p>Test from your athlete hub, sent through Register365 as coaching@cigalacycling.com.</p>', ['Content-Type: text/html; charset=UTF-8']);
    update_option('cc_smtp_ok', $ok ? time() : 0, false); if ($ok) delete_option('cc_smtp_err'); return ['ok' => (bool) $ok, 'to' => $me->user_email, 'error' => $ok ? null : get_option('cc_smtp_err')];
}]); });
add_action('rest_api_init', function () { register_rest_route('cc/v1', '/smtp-status', ['methods' => 'GET', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function () {
    return ['active' => (int) get_option('cc_smtp_ok', 0) ?: null, 'user' => get_option('cc_smtp_user', '') ?: CC_SMTP['user'], 'password_set' => (bool) get_option('cc_smtp_pass', ''), 'set_at' => (int) get_option('cc_smtp_set', 0) ?: null, 'last_error' => get_option('cc_smtp_err', null),
            'openssl' => extension_loaded('openssl'), 'can_reach_587' => (function () { $s = @fsockopen('smtp.reg365.net', 587, $no, $str, 6); if ($s) { $l = fgets($s, 200); fclose($s); return trim((string) $l); } return "no: $no $str"; })()];
}]); });
function cc_smtp_box() {   // on Matteo's Reports board
    $set = (int) get_option('cc_smtp_set', 0); $r = sanitize_key($_GET['smtp'] ?? ''); $okt = (int) get_option('cc_smtp_ok', 0);
    if ($okt && $r === 'fail') $r = '';   // an old ?smtp=fail address after a later test passed: don't show a stale error
    $msg = ['saved' => 'Saved. Now send yourself a test email.', 'sent' => 'Test email sent to you: check your inbox (and spam, just this once).', 'fail' => 'The test email did not go out: the password may be wrong. Type it again.', 'cleared' => 'Removed: emails go out the old way.'][$r] ?? '';
    return '<section class="ath-s rp-smtp"><h3 class="av-sub" style="margin-top:0">Email sending</h3><p class="av-lede" style="margin:0 0 10px">Emails to athletes go out through your Register365 Authenticated SMTP (smtp.reg365.net, the same login your Gmail “Send mail as” uses) from coaching@cigalacycling.com, so they don’t land in spam. '
        . (get_option('cc_smtp_ok') ? '<b style="color:#34c46a">Working: test passed ' . esc_html(date_i18n('j M Y H:i', (int) get_option('cc_smtp_ok'))) . '. Emails go through Register365.</b>' : '<b style="color:#ff4a3d">Not active yet (no successful test): emails still go the old way.</b>') . '</p>'
        . ($okt && $r !== 'saved' ? '<details class="rp-smtp-d"><summary>Change the login</summary>' : '')   // working: the fields fold away
        . '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" class="rp-smtp-f" autocomplete="off"><input type="hidden" name="action" value="cc_smtp">' . wp_nonce_field('cc_smtp', '_wpnonce', false, false)
        . '<label>SMTP username <input type="text" name="user" autocomplete="off" value="' . esc_attr((string) get_option('cc_smtp_user', '') ?: 'amedeo@cigalacycling.com') . '"></label>'
        . '<label>SMTP password <input type="password" name="pw" autocomplete="new-password" placeholder="' . ($set ? 'Type it again only to change it' : 'The same password Gmail uses for this username') . '"></label>'
        . '<input type="hidden" name="act" value="test"><span class="rp-acts"><button class="btn btn-go" type="submit">Save and send me a test email</button>' . ($set ? '<button class="btn btn-ghost" type="submit" onclick="this.form.act.value=\'clear\'">Remove</button>' : '') . '</span></form>' . ($okt && $r !== 'saved' ? '</details>' : '')
        . ($msg ? '<p class="rp-smtp-m">' . esc_html($msg) . '</p>' : '')
        . ((($er = get_option('cc_smtp_err')) && !empty($er['msg']) && ($r === 'fail' || (int) ($er['at'] ?? 0) > $okt)) ? '<p class="rp-smtp-m" style="color:#ff4a3d">' . ($r === 'fail' ? '' : 'An email failed on ' . esc_html(date_i18n('j M Y H:i', (int) $er['at'])) . '. ') . 'Reason: ' . esc_html($er['msg']) . '</p>' : '') . '</section>'
        . '<style>html .cc .rp-smtp{margin:0 0 18px}html .cc .rp-smtp-f{display:flex;flex-wrap:wrap;gap:10px 12px;align-items:end}html .cc .rp-smtp-f label{display:grid;gap:6px;font-size:14px;color:#d0d6e0;font-weight:600;flex:1 1 260px}'
        . 'html .cc .rp-smtp-f input{font:16px var(--body);padding:10px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.2);background:#0b0d0f;color:#fff}html .cc .rp-smtp-m{margin:10px 0 0;color:#34c46a;font-weight:600}html .cc .rp-smtp-d summary{cursor:pointer;color:#b8bec8;font-size:15px;margin:0 0 10px}</style>';
}
add_action('admin_post_cc_smtp', function () {
    if (!cc_ath_is_coach() || !wp_verify_nonce($_POST['_wpnonce'] ?? '', 'cc_smtp')) wp_die('Not allowed');
    $act = sanitize_key($_POST['act'] ?? ''); $pw = trim(wp_unslash((string) ($_POST['pw'] ?? ''))); $r = '';
    $user = sanitize_text_field(wp_unslash((string) ($_POST['user'] ?? ''))); if ($user !== '' && $act !== 'clear') update_option('cc_smtp_user', $user, false);
    if ($act === 'clear') { delete_option('cc_smtp_pass'); delete_option('cc_smtp_set'); delete_option('cc_smtp_ok'); $r = 'cleared'; }
    else {
        if ($pw !== '') { update_option('cc_smtp_pass', $pw, false); update_option('cc_smtp_set', time(), false); $r = 'saved'; }
        if ($act === 'test') { $me = wp_get_current_user(); $GLOBALS['cc_smtp_testing'] = 1;
            $ok = is_email($me->user_email) && wp_mail($me->user_email, 'Test: Cigala Cycling Coaching emails', '<p>This is a test from your athlete hub, sent through Register365 as coaching@cigalacycling.com. If it is in your inbox (not spam), athletes’ emails will be too.</p>', ['Content-Type: text/html; charset=UTF-8']);
            $r = $ok ? 'sent' : 'fail'; update_option('cc_smtp_ok', $ok ? time() : 0, false); if ($ok) delete_option('cc_smtp_err'); }
    }
    wp_safe_redirect(add_query_arg(['board' => 'reports', 'smtp' => $r], home_url('/' . CC_ATH_SLUG . '/'))); exit;
});
/* Matteo 17 Nov: notification emails showed "WordPress" as the sender: now "Cigala Cycling Coaching" (only replaces WordPress's default name) */
add_filter('wp_mail_from_name', function ($n) { return ($n === '' || $n === 'WordPress') ? 'Cigala Cycling Coaching' : $n; }, 20);
/* Words for the summary cards and their pages (Matteo 17 Nov), in the athlete's hub language; English for any other. */
function cc_ath_w($k, $lang = null) {
    static $W = [
        'back' => ['en' => 'Back to my hub', 'it' => 'Torna al mio hub', 'pt' => 'Voltar ao meu hub', 'sl' => 'Nazaj v moj hub'],
        'av_change' => ['en' => 'Change my availability', 'it' => 'Cambia la mia disponibilità', 'pt' => 'Alterar a minha disponibilidade', 'sl' => 'Spremeni mojo razpoložljivost'],
        'av_set' => ['en' => 'Set my availability', 'it' => 'Imposta la mia disponibilità', 'pt' => 'Definir a minha disponibilidade', 'sl' => 'Nastavi mojo razpoložljivost'],
        'av_once' => ['en' => 'Please set your availability here once, so everything is in one place. After that, change it only when your week changes.',
                      'it' => 'Imposta qui la tua disponibilità una volta, così tutto è in un unico posto. Poi cambiala solo quando cambia la tua settimana.',
                      'pt' => 'Define aqui a tua disponibilidade uma vez, para estar tudo num só sítio. Depois, muda-a só quando a tua semana mudar.',
                      'sl' => 'Tukaj enkrat nastavi svojo razpoložljivost, da bo vse na enem mestu. Potem jo spremeni le, ko se tvoj teden spremeni.'],
        'av_lede' => ['en' => 'Your usual week and anything coming up. Change it whenever things change, and I adjust your plan in Vekta.',
                      'it' => 'La tua settimana tipo e quello che arriva. Cambiala quando le cose cambiano e io adatto il tuo piano in Vekta.',
                      'pt' => 'A tua semana habitual e o que vem aí. Muda-a sempre que algo mudar e eu ajusto o teu plano no Vekta.',
                      'sl' => 'Tvoj običajni teden in kar prihaja. Spremeni ga, ko se kaj spremeni, in jaz prilagodim tvoj načrt v Vekti.'],
        'updated' => ['en' => 'updated %s', 'it' => 'aggiornata il %s', 'pt' => 'atualizada a %s', 'sl' => 'posodobljeno %s'],
        'changes' => ['en' => '%d change coming up|%d changes coming up', 'it' => '%d cambiamento in arrivo|%d cambiamenti in arrivo', 'pt' => '%d alteração a caminho|%d alterações a caminho', 'sl' => '%d sprememba|%d sprememb'],
        'gl_change' => ['en' => 'Add or change my goals & events', 'it' => 'Aggiungi o cambia obiettivi ed eventi', 'pt' => 'Adicionar ou alterar objetivos e eventos', 'sl' => 'Dodaj ali spremeni cilje in dogodke'],
        'gl_next' => ['en' => 'Next', 'it' => 'Prossimo', 'pt' => 'Próximo', 'sl' => 'Naslednji'],
        // Matteo 17 Nov: route question in each race + the race day plan card
        'rt_ask' => ['en' => 'Do you have a GPX file of the route? Add it and you’ll get your race day simulation for this event.',
                     'it' => 'Hai il file GPX del percorso? Aggiungilo e riceverai la simulazione del giorno di gara per questo evento.',
                     'pt' => 'Tens o ficheiro GPX do percurso? Adiciona-o e vais receber a simulação do dia de prova para este evento.',
                     'sl' => 'Imaš GPX datoteko proge? Dodaj jo in prejel boš simulacijo dneva tekme za ta dogodek.'],
        'rt_upload' => ['en' => 'Add the route file (.gpx, .fit or .tcx)', 'it' => 'Aggiungi il file del percorso (.gpx, .fit o .tcx)', 'pt' => 'Adicionar o ficheiro do percurso (.gpx, .fit ou .tcx)', 'sl' => 'Dodaj datoteko proge (.gpx, .fit ali .tcx)'],
        'rt_link' => ['en' => 'Or paste a link to the route (a GPX file works best; a RideWithGPS link is fine too)', 'it' => 'Oppure incolla il link del percorso (meglio il file GPX; va bene anche un link RideWithGPS)',
                      'pt' => 'Ou cola o link do percurso (o ficheiro GPX é o melhor; um link RideWithGPS também serve)', 'sl' => 'Ali prilepi povezavo do proge (najbolje je GPX datoteka; ustreza tudi povezava RideWithGPS)'],
        'rt_start' => ['en' => 'Start time', 'it' => 'Orario di partenza', 'pt' => 'Hora de partida', 'sl' => 'Čas starta'],
        'rt_remove' => ['en' => 'Change the file', 'it' => 'Cambia il file', 'pt' => 'Mudar o ficheiro', 'sl' => 'Zamenjaj datoteko'],
        'rt_up' => ['en' => 'Uploading…', 'it' => 'Caricamento…', 'pt' => 'A carregar…', 'sl' => 'Nalagam…'],
        'rt_bad' => ['en' => 'That file didn’t upload. Please use a .gpx, .fit or .tcx file under 15 MB.', 'it' => 'Il file non è stato caricato. Usa un file .gpx, .fit o .tcx sotto i 15 MB.',
                     'pt' => 'O ficheiro não foi carregado. Usa um ficheiro .gpx, .fit ou .tcx com menos de 15 MB.', 'sl' => 'Datoteka se ni naložila. Uporabi datoteko .gpx, .fit ali .tcx, manjšo od 15 MB.'],
        'rt_ok' => ['en' => 'Route added', 'it' => 'Percorso aggiunto', 'pt' => 'Percurso adicionado', 'sl' => 'Proga dodana'],
        'mic' => ['en' => 'Speak instead of typing', 'it' => 'Parla invece di scrivere', 'pt' => 'Fala em vez de escrever', 'sl' => 'Govori namesto tipkanja'],
        'mic_on' => ['en' => 'Listening… speak now, tap the microphone again to stop.', 'it' => 'Ti ascolto… parla ora, tocca di nuovo il microfono per fermare.',
                     'pt' => 'A ouvir… fala agora, toca outra vez no microfone para parar.', 'sl' => 'Poslušam… govori zdaj, za konec znova tapni mikrofon.'],
        'mic_denied' => ['en' => 'Please allow the microphone for this page, then tap it again.', 'it' => 'Consenti l’uso del microfono per questa pagina, poi toccalo di nuovo.',
                         'pt' => 'Permite o microfone nesta página e depois toca outra vez.', 'sl' => 'Dovoli mikrofon za to stran in ga nato znova tapni.'],
        'mic_none' => ['en' => 'Speaking didn’t work here. You can use the microphone on your phone’s keyboard instead.', 'it' => 'La dettatura qui non ha funzionato. Puoi usare il microfono della tastiera del telefono.',
                       'pt' => 'Ditar não funcionou aqui. Podes usar o microfone do teclado do telemóvel.', 'sl' => 'Narekovanje tu ni delovalo. Uporabiš lahko mikrofon na tipkovnici telefona.'],
        'rc_hint' => ['en' => 'Racing soon? Add your race with its route (GPX) and you’ll get your race day plan: the power for every climb and your finish time. It goes into your Vekta calendar too.',
                      'it' => 'Hai una gara in arrivo? Aggiungila con il percorso (GPX) e riceverai il tuo piano per il giorno di gara: la potenza per ogni salita e il tempo all’arrivo. Finisce anche nel tuo calendario Vekta.',
                      'pt' => 'Tens uma prova em breve? Adiciona-a com o percurso (GPX) e vais receber o teu plano para o dia de prova: a potência para cada subida e o teu tempo final. Também vai para o teu calendário Vekta.',
                      'sl' => 'Kmalu tekmuješ? Dodaj tekmo s progo (GPX) in prejel boš načrt za dan tekme: moč za vsak vzpon in končni čas. Pojavi se tudi v tvojem koledarju Vekta.'],
        'rc_title' => ['en' => 'Race day plan', 'it' => 'Piano per il giorno di gara', 'pt' => 'Plano para o dia de prova', 'sl' => 'Načrt za dan tekme'],
        'rc_text' => ['en' => 'Get a plan for your race: the power for every climb and your finish time. Add your race here with its route, and it goes into your Vekta calendar too. For road, gravel and sportive events.',
                      'it' => 'Ricevi un piano per la tua gara: la potenza per ogni salita e il tuo tempo all’arrivo. Aggiungi qui la tua gara con il percorso: finisce anche nel tuo calendario Vekta. Per gare su strada, gravel e granfondo.',
                      'pt' => 'Recebe um plano para a tua prova: a potência para cada subida e o teu tempo final. Adiciona aqui a tua prova com o percurso, e ela também vai para o teu calendário Vekta. Para provas de estrada, gravel e gran fondo.',
                      'sl' => 'Prejmi načrt za svojo tekmo: moč za vsak vzpon in tvoj končni čas. Tukaj dodaj svojo tekmo s progo in pojavila se bo tudi v tvojem koledarju Vekta. Za cestne, gravel in maratonske dogodke.'],
        'rc_btn' => ['en' => 'Add my race and route', 'it' => 'Aggiungi la mia gara e il percorso', 'pt' => 'Adicionar a minha prova e o percurso', 'sl' => 'Dodaj mojo tekmo in progo'],
        'tp_card' => ['en' => 'Your training is in TrainingPeaks: your plan, your workouts and your calendar. Add your availability, races and goals there, in your TrainingPeaks calendar, so I see them when I plan your training.',
                      'it' => 'Il tuo allenamento è su TrainingPeaks: il piano, gli allenamenti e il calendario. Aggiungi lì la tua disponibilità, le gare e gli obiettivi, nel tuo calendario TrainingPeaks, così li vedo quando pianifico il tuo allenamento.',
                      'pt' => 'O teu treino está no TrainingPeaks: o plano, os treinos e o calendário. Adiciona lá a tua disponibilidade, provas e objetivos, no teu calendário TrainingPeaks, para eu os ver quando planeio o teu treino.',
                      'sl' => 'Tvoj trening je v TrainingPeaks: načrt, treningi in koledar. Tja dodaj svojo razpoložljivost, tekme in cilje, v svoj koledar TrainingPeaks, da jih vidim, ko načrtujem tvoj trening.'],
        'wl_app' => ['en' => 'Your first step: choose your password and fill in the short rider form. In it you choose your training app. If you go with Vekta (recommended), Vekta emails you a code to join me there.',
                     'it' => 'Il primo passo: scegli la password e compila il breve modulo atleta. Lì scegli l’app con cui allenarti. Se scegli Vekta (consigliata), Vekta ti invia via email un codice per raggiungermi.',
                     'pt' => 'O primeiro passo: escolhe a tua palavra-passe e preenche o pequeno formulário de atleta. Nele escolhes a app de treino. Se escolheres o Vekta (recomendada), o Vekta envia-te por email um código para te juntares a mim.',
                     'sl' => 'Prvi korak: izberi geslo in izpolni kratek obrazec za kolesarja. V njem izbereš aplikacijo za trening. Če izbereš Vekta (priporočeno), ti Vekta po e-pošti pošlje kodo, da se mi pridružiš.'],
        'vk_open' => ['en' => 'Open Vekta', 'it' => 'Apri Vekta', 'pt' => 'Abrir o Vekta', 'sl' => 'Odpri Vekta'],
        'vk_title' => ['en' => 'Join me on Vekta', 'it' => 'Raggiungimi su Vekta', 'pt' => 'Junta-te a mim no Vekta', 'sl' => 'Pridruži se mi na Vekta'],
        'vk_text' => ['en' => 'Vekta is sending you an email with a code to join me. Download the Vekta app, sign in with your Google or Apple account and enter the code. Then, in Vekta, connect your devices (Garmin, Wahoo, COROS, Hammerhead, Zwift) and your wearables such as WHOOP or Oura, so I can see your training and recovery. Can’t find the email? Check your spam folder, or message me.',
                      'it' => 'Vekta ti sta inviando un’email con un codice per raggiungermi. Scarica l’app Vekta, accedi con il tuo account Google o Apple e inserisci il codice. Poi, in Vekta, collega i tuoi dispositivi (Garmin, Wahoo, COROS, Hammerhead, Zwift) e i dispositivi indossabili come WHOOP o Oura, così vedo i tuoi allenamenti e il recupero. Non trovi l’email? Controlla lo spam, oppure scrivimi.',
                      'pt' => 'O Vekta está a enviar-te um email com um código para te juntares a mim. Descarrega a app Vekta, entra com a tua conta Google ou Apple e introduz o código. Depois, no Vekta, liga os teus dispositivos (Garmin, Wahoo, COROS, Hammerhead, Zwift) e os teus wearables como WHOOP ou Oura, para eu ver os teus treinos e a tua recuperação. Não encontras o email? Vê a pasta de spam, ou envia-me uma mensagem.',
                      'sl' => 'Vekta ti pošilja e-pošto s kodo, da se mi pridružiš. Prenesi aplikacijo Vekta, prijavi se z Google ali Apple računom in vnesi kodo. Nato v Vekti poveži svoje naprave (Garmin, Wahoo, COROS, Hammerhead, Zwift) in nosljive naprave, kot sta WHOOP ali Oura, da vidim tvoj trening in regeneracijo. Ne najdeš e-pošte? Preveri mapo z neželeno pošto ali mi piši.'],
        'tp_open' => ['en' => 'Open TrainingPeaks', 'it' => 'Apri TrainingPeaks', 'pt' => 'Abrir o TrainingPeaks', 'sl' => 'Odpri TrainingPeaks'],
        'tp_empty' => ['en' => 'Your assessment and reviews will appear here. I will let you know when there is something new.',
                       'it' => 'Qui troverai la tua valutazione e le tue revisioni. Ti avviso io quando c’è qualcosa di nuovo.',
                       'pt' => 'A tua avaliação e as tuas revisões vão aparecer aqui. Eu aviso-te quando houver algo novo.',
                       'sl' => 'Tu se bodo pojavili tvoja ocena in pregledi. Sporočil ti bom, ko bo kaj novega.'],
        'gl_more' => ['en' => '+%d more', 'it' => 'altri %d', 'pt' => 'mais %d', 'sl' => 'še %d'],
        'gl_none' => ['en' => 'No events yet. Add your races, sportives and camps: I plan your training around them.',
                      'it' => 'Ancora nessun evento. Aggiungi gare, granfondo e ritiri: pianifico il tuo allenamento intorno a loro.',
                      'pt' => 'Ainda sem eventos. Adiciona as tuas provas, gran fondos e estágios: planeio o teu treino à volta deles.',
                      'sl' => 'Še ni dogodkov. Dodaj tekme, maratone in priprave: trening načrtujem okoli njih.'],
    ];
    $l = $lang ?: ($GLOBALS['cc_ath_lang'] ?? 'en');
    return $W[$k][$l] ?? $W[$k]['en'];
}
function cc_ath_js() {
    return <<<'JS'
<script>(function(){
var g=document.querySelector('.ath-greet');if(g){var h=new Date().getHours(),it=g.getAttribute('data-l')==='it',w=JSON.parse(g.getAttribute('data-g')||'[]');if(w.length===3)g.textContent=(h>=5&&h<(it?13:12))?w[0]:(h>=5&&h<18)?w[1]:w[2];}
(function(){var L=document.querySelector('.ath-hero-txt .ath-lede'),P=document.querySelector('.ath-hero-me img');if(!L||!P)return;
 function fit(){L.classList.remove('ath-lede-narrow');var l=L.getBoundingClientRect(),p=P.getBoundingClientRect();if(l.bottom>p.top+6&&l.right>p.left+20)L.classList.add('ath-lede-narrow');}
 fit();addEventListener('load',fit);addEventListener('resize',fit);})();
document.querySelectorAll('.ath-chip-bell').forEach(function(c){c.addEventListener('click',function(e){e.preventDefault();var b=document.querySelector('.ath-bell');if(b){e.stopPropagation();b.click();c.remove();}});});
try{localStorage.setItem('cc_tools_ok','1');}catch(e){}   /* coached athletes skip the newsletter step on the free tools */
var rm=matchMedia('(prefers-reduced-motion: reduce)').matches,io='IntersectionObserver' in window;
document.querySelectorAll('.ath-n').forEach(function(el){var n=+el.getAttribute('data-n');if(rm||!n)return;var s=0;el.textContent='0';
 function f(t){if(!s)s=t;var p=Math.min(1,(t-s)/1400);el.textContent=Math.round(n*(1-Math.pow(1-p,3)));if(p<1)requestAnimationFrame(f);}setTimeout(function(){requestAnimationFrame(f);},350);});
if(!rm&&io){   /* Matteo 17 Nov: no fade-in on scroll; every block is there straight away (the ath-anim CSS stays unused) */
 var sig=document.querySelectorAll('img.signature');if(sig.length){document.documentElement.classList.add('sig-ok');var so=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){so.unobserve(e.target);e.target._sig.classList.add('go');}});},{threshold:.5});
 sig.forEach(function(x){var t=x.nextElementSibling||x.parentElement;t._sig=x;so.observe(t);});}}
})();</script>
JS;
}
/* ---------- welcome email + "choose your password" (Matteo 16 Nov 2026, live) ----------
   Matteo creates the athlete (Users > Add New, Subscriber, any password), then Users > hover the athlete > "Send hub welcome email"
   (or Claude via POST /wp-json/cc/v1/athlete-welcome). The athlete gets a branded email in their language with a button that opens
   /athletes/?cc_set=KEY&u=LOGIN, where they choose their own password and land in their hub, logged in. Nobody else sees the password.
   The link is WordPress's own password-reset key: one use, valid 7 days (a new email makes the old link stop working). */
add_filter('password_reset_expiration', function () { return 7 * DAY_IN_SECONDS; });
function cc_ath_setpw_user() {
    $login = isset($_GET['u']) ? sanitize_user(wp_unslash($_GET['u'])) : '';
    $key = isset($_GET['cc_set']) ? preg_replace('/[^a-zA-Z0-9]/', '', wp_unslash($_GET['cc_set'])) : '';
    if ($login === '' || $key === '') return null;
    $u = check_password_reset_key($key, $login);
    return is_wp_error($u) ? null : $u;
}
add_action('template_redirect', function () {   // the form posts back to the same link
    if (!is_page(CC_ATH_SLUG) || !isset($_GET['cc_set']) || ($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST' || !isset($_POST['cc_pw1'])) return;
    $back = remove_query_arg('err');
    $u = cc_ath_setpw_user();
    if (!$u) { wp_safe_redirect(add_query_arg('err', 'expired', $back)); exit; }
    $p1 = (string) wp_unslash($_POST['cc_pw1']); $p2 = (string) wp_unslash($_POST['cc_pw2'] ?? '');
    if (strlen($p1) < 8) { wp_safe_redirect(add_query_arg('err', 'short', $back)); exit; }
    if ($p1 !== $p2) { wp_safe_redirect(add_query_arg('err', 'match', $back)); exit; }
    reset_password($u, $p1);
    update_user_meta($u->ID, 'cc_pw_set', current_time('mysql'));
    wp_set_current_user($u->ID); wp_set_auth_cookie($u->ID, true);
    wp_safe_redirect(home_url('/' . CC_ATH_SLUG . '/')); exit;
}, 2);
function cc_ath_setpw_html() {
    $u = cc_ath_setpw_user();
    $login = isset($_GET['u']) ? sanitize_user(wp_unslash($_GET['u'])) : '';
    $lu = $u ?: get_user_by('login', $login);
    $GLOBALS['cc_ath_lang'] = $lu ? cc_ath_user_lang($lu->ID) : 'en';
    $it = $GLOBALS['cc_ath_lang'] === 'it';
    $help = '<p class="ath-help">' . cc_L('Any trouble? <a href="https://wa.me/353834777697" target="_blank" rel="noopener">WhatsApp me</a> or <a href="mailto:matteo@cigalacycling.com">email me</a>.', 'Problemi? <a href="https://wa.me/353834777697" target="_blank" rel="noopener">Scrivimi su WhatsApp</a> o <a href="mailto:matteo@cigalacycling.com">mandami un’email</a>.') . '</p>';
    $eb = '<p class="eyebrow">' . cc_t('Coached athletes') . '</p>';
    if (!$u) return '<div class="ath-login">' . $eb . '<h1>' . (cc_L('This link has expired', 'Link scaduto')) . '</h1><p class="ath-lede">'
        . (cc_ath_selfpw() ? (cc_L('The link to choose your password works once and lasts 7 days. Ask for a new one here: it comes straight to your email.', 'Il link per scegliere la password vale 7 giorni e si usa una volta sola. Chiedine uno nuovo qui: arriva subito via email.'))
                           : (cc_L('The link to choose your password works once and lasts 7 days. Message me and I will send you a new one.', 'Il link per scegliere la password vale 7 giorni e si usa una volta sola. Scrivimi e te ne mando uno nuovo.')))
        . '</p><p>' . (cc_ath_selfpw() ? '<a class="btn btn-go" href="' . esc_url(cc_ath_forgot_url()) . '">' . (cc_L('Send me a new link', 'Mandami un nuovo link')) . '</a>'
                                      : '<a class="btn btn-go" href="https://wa.me/353834777697" target="_blank" rel="noopener">' . (cc_L('WhatsApp me', 'Scrivimi su WhatsApp')) . '</a>') . '</p>'
        . '<p class="ath-help">' . (cc_L('Already have a password?', 'Hai già una password?')) . ' <a href="' . esc_url(home_url('/' . CC_ATH_SLUG . '/')) . '">' . cc_t('Log in') . '</a></p></div>';
    $first = $u->first_name ?: $u->display_name;
    $err = ['short' => cc_L('Use at least 8 characters.', 'Usa almeno 8 caratteri.'), 'match' => cc_L('The two passwords are not the same.', 'Le due password non coincidono.'),
            'expired' => cc_ath_selfpw() ? (cc_L('The link has expired. Tap “Forgot your password?” on the login page to get a new one.', 'Il link è scaduto. Tocca “Password dimenticata?” nella pagina di accesso per riceverne uno nuovo.'))
                                         : (cc_L('The link has expired. Message me and I will send you a new one.', 'Il link è scaduto. Scrivimi e te ne mando uno nuovo.'))][$_GET['err'] ?? ''] ?? '';
    return '<div class="ath-login">' . $eb . '<h1>' . (cc_L('Choose your password', 'Scegli la tua password')) . '</h1>'
        . '<p class="ath-lede">' . sprintf(cc_L('Hi %s, choose a password for your athlete hub. You will log in with your email, <strong>%s</strong>, and this password.', 'Ciao %s, scegli una password per la tua area atleta. Per entrare userai la tua email, <strong>%s</strong>, e questa password.'), esc_html($first), esc_html($u->user_email)) . '</p>'
        . ($err ? '<p class="ath-err" role="alert">' . esc_html($err) . '</p>' : '')
        . '<form method="post" action="' . esc_url(remove_query_arg('err')) . '">'
        . '<input type="text" name="log" value="' . esc_attr($u->user_email) . '" autocomplete="username" hidden>'
        . '<label for="ath-p1">' . (cc_L('New password (at least 8 characters)', 'Nuova password (almeno 8 caratteri)')) . '</label><input id="ath-p1" name="cc_pw1" type="password" autocomplete="new-password" minlength="8" required>'
        . '<label for="ath-p2">' . (cc_L('Repeat the password', 'Ripeti la password')) . '</label><input id="ath-p2" name="cc_pw2" type="password" autocomplete="new-password" minlength="8" required>'
        . '<button type="submit" class="btn btn-go">' . (cc_L('Save and open my hub', 'Salva e apri la mia area')) . '</button></form>' . $help . '</div>';
}
/* The branded athlete email (Matteo 16-17 Nov): header picture, white card, green button, footer. Used by the welcome, report and password emails.
 * $small: HTML under the button (small grey paragraphs). The language is the athlete's (set $GLOBALS['cc_ath_lang'] before). */
function cc_ath_mail_shell($hi, $p1, $btn, $link, $small = '', $bye = null, $eb = null, $foot = null) {   // $bye false: no sign-off (Matteo's own notices)
    if ($small === '') $small = '<div style="height:24px;line-height:24px;font-size:1px">&nbsp;</div>';   // space between the button and the sign-off
    $it = ($GLOBALS['cc_ath_lang'] ?? 'en') === 'it'; $bye = $bye ?? cc_L('See you on the road,', 'A presto in bici,'); $eb = $eb ?? cc_L('Athlete hub', 'Area atleta');
    $logo = esc_url(get_option('cc_mail_logo', '')); $head = esc_url(get_option('cc_mail_header_' . ($GLOBALS['cc_ath_lang'] ?? 'en'), '') ?: get_option('cc_mail_header_en', ''));   // the header picture in the athlete's language (en, it, pt, sl)
    $logo = str_replace('//staging.coaching.', '//coaching.', $logo); $head = str_replace('//staging.coaching.', '//coaching.', $head);   // pictures always from the live site: staging is password-protected, so mail apps can't load them
    $f = "font-family:Montserrat,Helvetica,Arial,sans-serif";
    $h = '<!doctype html><html><body style="margin:0;padding:0;background:#07080a"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#07080a"><tr><td align="center" style="padding:30px 12px;background-color:#07080a">'
       . '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px">'
       // Matteo 16 Nov: one topographic layer, inside the header picture (logo + "Athlete hub" + lines). Phone mail apps in dark mode
       // recolour text and backgrounds but never pictures, so the header always looks the same. Around the card: plain black.
       . '<tr><td style="background:#ffffff;border-radius:14px;overflow:hidden;box-shadow:0 20px 50px rgba(0,0,0,.45)"><table role="presentation" width="100%" cellpadding="0" cellspacing="0">'
       . ($head ? '<tr><td style="padding:0;background:#07080a"><img src="' . $head . '" width="560" alt="Cigala Cycling Coaching, ' . $eb . '" style="display:block;width:100%;max-width:560px;height:auto;border:0"></td></tr>'
                : '<tr><td style="background:#07080a;padding:22px 30px">' . ($logo ? '<img src="' . $logo . '" width="64" height="64" alt="Cigala Cycling Coaching" style="display:block;border:2px solid #fff">' : '') . '</td></tr>')
       . '<tr><td style="padding:30px 30px 8px;' . $f . ';color:#16181b;font-size:16px;line-height:1.6">'
       . '<p style="margin:0 0 14px;font-size:18px;font-weight:700">' . $hi . '</p><p style="margin:0 0 22px">' . $p1 . '</p>'
       . '<table role="presentation" cellpadding="0" cellspacing="0"><tr><td style="border-radius:10px;background:#12a150"><a href="' . esc_url($link) . '" style="display:inline-block;padding:15px 26px;' . $f . ';font-size:16px;font-weight:700;color:#ffffff;text-decoration:none;border-radius:10px">' . $btn . '</a></td></tr></table>'
       . $small
       . ($bye === false ? '' : '<p style="margin:0 0 18px">' . $bye . '</p>') . '</td></tr>'
       // Matteo 17 Nov: every coaching email signs off with his round photo, his signature across the bottom (see-through, so it takes the email's own colour)
       . ($bye === false ? '' : '<tr><td style="padding:0 30px 18px"><img src="https://coaching.cigalacycling.com/wp-content/uploads/2026/11/cigala-email-matteo-signed-photo-2.png" width="190" alt="Matteo Cigala" style="display:block;width:190px;height:auto;border:0"></td></tr>')
       . '<tr><td style="padding:18px 30px 26px;' . $f . ';font-size:12px;color:#7a808a;border-top:1px solid #eceef1">' . ($foot ?? 'Matteo Cigala · Head Coach, Cigala Cycling Coaching · <a href="https://wa.me/353834777697" style="color:#12a150">WhatsApp</a> · <a href="mailto:matteo@cigalacycling.com" style="color:#12a150">matteo@cigalacycling.com</a>') . '</td></tr>'
       . '</table></td></tr></table></td></tr></table></body></html>';
    return $h;
}
/* Matteo's own notices (availability, goals & events, rider form): the same branded design, in English, no sign-off.
 * Takes the notice HTML as the modules build it (eyebrow, h2 title, content, one green button) and puts it in the shell. */
function cc_ath_coach_wrap($html) {
    $html = preg_replace('~^<div[^>]*>|</div>$~', '', trim($html));
    $title = preg_match('~<h2[^>]*>(.*?)</h2>~s', $html, $m) ? $m[1] : ''; $html = str_replace($m[0] ?? '', '', $html);
    $eb = preg_match('~^<p style="margin:0 0 4px;[^"]*">(.*?)</p>~s', $html, $m2) ? $m2[1] : 'Athlete hub'; if (!empty($m2[0])) $html = substr($html, strlen($m2[0]));
    $btn = ''; $link = home_url('/' . CC_ATH_SLUG . '/');
    if (preg_match('~<p style="margin:20px 0 0"><a href="([^"]+)"[^>]*>(.*?)</a></p>~s', $html, $m3)) { $link = html_entity_decode($m3[1]); $btn = $m3[2]; $html = str_replace($m3[0], '', $html); }
    $keep = $GLOBALS['cc_ath_lang'] ?? 'en'; $GLOBALS['cc_ath_lang'] = 'en';
    $out = cc_ath_mail_shell('<span style="display:block;margin:0 0 6px;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#E10600;font-weight:600">' . $eb . '</span>' . $title,
        '</p><div style="font-size:15px;line-height:1.55;color:#16181b">' . $html . '</div><p style="margin:0">', $btn ?: 'Open the athlete hub', $link, '', false, 'Athlete hub',
        'Notice for Matteo from the Cigala Coaching athlete hub. Reply to answer the athlete directly.');
    $GLOBALS['cc_ath_lang'] = $keep;
    return $out;
}
function cc_ath_mail_small($html) { return '<p style="margin:22px 0 10px;font-size:16px;color:#454a52">' . $html . '</p>'; }
function cc_ath_welcome_mail($uid, $to = null, $dry = false) {
    $u = get_userdata((int) $uid); if (!$u) return new WP_Error('nouser', 'No such user');
    $key = get_password_reset_key($u); if (is_wp_error($key)) return $key;
    $link = add_query_arg(['cc_set' => $key, 'u' => rawurlencode($u->user_login)], home_url('/' . CC_ATH_SLUG . '/'));
    $GLOBALS['cc_ath_lang'] = cc_ath_user_lang($u->ID); $it = $GLOBALS['cc_ath_lang'] === 'it'; $first = esc_html($u->first_name ?: $u->display_name);
    $logo = esc_url(get_option('cc_mail_logo', '')); $head = esc_url(get_option($it ? 'cc_mail_header_it' : 'cc_mail_header_en', ''));
    $T = ['subj' => cc_L('Your Cigala Coaching athlete hub is ready', 'La tua area atleta Cigala Coaching è pronta'), 'hi' => sprintf(cc_L('Hi %s,', 'Ciao %s,'), $first),
          'p1' => cc_L('Your personal athlete hub is ready. It is where you will find your reports from me, the training guides, the free tools without any sign-up and a direct line to me, all in one place.', 'la tua area atleta personale è pronta. Qui trovi i tuoi report, le guide di allenamento, gli strumenti gratuiti senza registrazione e un contatto diretto con me, tutto in un unico posto.'),
          'btn' => cc_L('Choose your password', 'Scegli la tua password'),
          'p2' => sprintf(cc_L('You log in with your email, %s. The button works for 7 days: ', 'Per entrare usi la tua email, %s. Il pulsante vale 7 giorni: '), '<strong>' . esc_html($u->user_email) . '</strong>')
                . (cc_ath_selfpw() ? cc_L('if it has expired, tap “Forgot your password?” on the login page and a new one comes straight away.', 'se è scaduto, tocca “Password dimenticata?” nella pagina di accesso e te ne arriva subito uno nuovo.') : cc_L('if it has expired, just message me and I will send you a new one.', 'se è scaduto, scrivimi e te ne mando uno nuovo.')),
          'p3' => cc_L('Once you are in, bookmark the page on your phone so it is always one tap away.', 'Una volta dentro, salva la pagina tra i preferiti del telefono: così è sempre a un tocco.'),
          'bye' => cc_L('See you on the road,', 'A presto in bici,'), 'eb' => cc_L('Athlete hub', 'Area atleta')];
    $pg = cc_ath_page_of($u->ID); $newApp = $pg && !get_user_meta($u->ID, 'cc_vekta_id', true) && !cc_ath_tp($pg);   // Matteo 17 Nov: new athletes choose their app in the rider form
    $h = cc_ath_mail_shell($T['hi'], $T['p1'], $T['btn'], $link, ($newApp ? '<p style="margin:22px 0 10px;font-size:16px;color:#454a52"><b>' . esc_html(cc_ath_w('wl_app')) . '</b></p>' : '') . '<p style="margin:' . ($newApp ? '0' : '22px') . ' 0 10px;font-size:16px;color:#454a52">' . $T['p2'] . '</p><p style="margin:0 0 22px;font-size:16px;color:#454a52">' . $T['p3'] . '</p>', $T['bye'], $T['eb']);
    if ($dry) return ['to' => $to ?: $u->user_email, 'subject' => $T['subj'], 'link' => $link, 'html' => $h];
    $ok = wp_mail($to ?: $u->user_email, $T['subj'], $h, ['Content-Type: text/html; charset=UTF-8', 'From: Matteo Cigala <coaching@cigalacycling.com>', 'Reply-To: Matteo Cigala <matteo@cigalacycling.com>']);
    if ($ok && !$to) update_user_meta($u->ID, 'cc_welcome_sent', current_time('mysql'));
    return $ok ? ['sent' => true, 'to' => $to ?: $u->user_email] : new WP_Error('mail', 'wp_mail failed');
}
add_action('rest_api_init', function () {   // Matteo 17 Nov: "email me a preview": any email design, sent ONLY to the logged-in coach's own address
    register_rest_route('cc/v1', '/mail-preview', ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function ($r) {
        $me = wp_get_current_user(); if (!is_email($me->user_email)) return new WP_Error('cc_mail', 'No email on your account');
        $GLOBALS['cc_ath_lang'] = 'en';
        $h = (string) $r['html'] ?: cc_ath_mail_shell((string) $r['hi'], (string) $r['p1'], (string) $r['btn'], home_url('/' . CC_ATH_SLUG . '/'), (string) $r['small']);
        $ok = wp_mail($me->user_email, 'PREVIEW · ' . sanitize_text_field((string) $r['subject']), $h, ['Content-Type: text/html; charset=UTF-8', 'From: Matteo Cigala <coaching@cigalacycling.com>']);
        return ['sent' => (bool) $ok, 'to' => $me->user_email];
    }]);
});
add_action('rest_api_init', function () {
    register_rest_route('cc/v1', '/athlete-welcome', ['methods' => 'POST', 'permission_callback' => function () { return current_user_can('edit_users'); },
        'callback' => function ($r) {
            $res = cc_ath_welcome_mail((int) $r['user'], $r['test_to'] ? sanitize_email($r['test_to']) : null, (bool) $r['dry']);
            return is_wp_error($res) ? $res : rest_ensure_response($res);
        }]);
});
add_filter('user_row_actions', function ($a, $u) {   // Users list: "Send hub welcome email" under each athlete
    if (in_array('subscriber', (array) $u->roles, true) && current_user_can('edit_users')) {
        $sent = get_user_meta($u->ID, 'cc_welcome_sent', true);
        $a['cc_welcome'] = '<a href="' . esc_url(wp_nonce_url(admin_url('admin-post.php?action=cc_welcome&user=' . $u->ID), 'cc_welcome_' . $u->ID)) . '">' . ($sent ? 'Resend hub welcome email' : 'Send hub welcome email') . '</a>';
    }
    return $a;
}, 10, 2);
add_action('admin_post_cc_welcome', function () {
    $id = (int) ($_GET['user'] ?? 0);
    if (!current_user_can('edit_users') || !wp_verify_nonce($_GET['_wpnonce'] ?? '', 'cc_welcome_' . $id)) wp_die('Not allowed');
    $r = cc_ath_welcome_mail($id);
    wp_safe_redirect(add_query_arg('cc_welcome', is_wp_error($r) ? 'fail' : 'ok', admin_url('users.php'))); exit;
});
add_action('admin_notices', function () {
    if (!isset($_GET['cc_welcome'])) return;
    echo $_GET['cc_welcome'] === 'ok' ? '<div class="notice notice-success is-dismissible"><p>Hub welcome email sent.</p></div>' : '<div class="notice notice-error"><p>The welcome email could not be sent.</p></div>';
});
add_filter('manage_users_columns', function ($c) { $c['cc_hub'] = 'Athlete hub'; return $c; });
add_filter('manage_users_custom_column', function ($v, $col, $uid) {
    if ($col !== 'cc_hub') return $v;
    if (!user_can($uid, 'subscriber') || user_can($uid, 'edit_posts')) return '';
    $pw = get_user_meta($uid, 'cc_pw_set', true); $ws = get_user_meta($uid, 'cc_welcome_sent', true);
    return $pw ? '✅ password set ' . esc_html(mysql2date('j M', $pw)) : ($ws ? '✉️ email sent ' . esc_html(mysql2date('j M', $ws)) : '— no email yet');
}, 10, 3);

function cc_ath_shortcode() {   // in the site design: the .cc wrapper picks up the Coaching kit styles
    $inner = cc_ath_inner();
    return '<div class="cc cc-page" lang="' . esc_attr($GLOBALS['cc_ath_lang'] ?: 'en') . '"><section class="ath-sec"><div class="in">' . $inner . '</div></section></div>';
}
add_shortcode('cc_athletes', 'cc_ath_shortcode');
add_action('wp_head', function () {
    if (!is_page(CC_ATH_SLUG)) return;
    echo <<<'CSS'
<style id="cc-athletes">
html .cc .ath-sec { padding-block: 48px 80px; min-height: 70vh; }   /* Matteo 16 Nov: closer to the header */
html .cc .ath { max-width: 860px; margin: 0 auto; }
html .cc .ath h1 { font-size: clamp(38px, 7vw, 64px); margin: 6px 0 14px; }
html .cc .ath h2 { font-size: clamp(24px, 4vw, 32px); margin: 0 0 16px; }
html .cc .ath h3 { font-size: 20px; margin: 22px 0 10px; }
html .cc .ath .eyebrow { margin: 0; font-size: 12px; font-weight: 600; letter-spacing: .14em; text-transform: uppercase; }
html .cc .ath-login { max-width: 460px; margin: 0 auto; padding: 34px 30px; border: 1px solid rgba(43,212,122,.35); border-radius: 16px; background: rgba(15,17,19,.92); box-shadow: 0 30px 80px rgba(0,0,0,.5); }
html .cc .ath-login h1 { font-size: clamp(34px, 7vw, 46px); }
html .cc .ath-lede { color: var(--text-2); margin: 0 0 20px; }
html .cc .ath form { display: grid; gap: 8px; margin: 0 0 18px; }
html .cc .ath label { font-size: 13px; font-weight: 600; color: var(--text); margin-top: 6px; }
html .cc .ath input[type=text], html .cc .ath input[type=password] { width: 100%; box-sizing: border-box; font-size: 16px; padding: 13px 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,.18); background: #0b0d0f; color: #fff; }
html .cc .ath input[type=text]:focus, html .cc .ath input[type=password]:focus { outline: 2px solid var(--green, #2bd47a); outline-offset: 1px; border-color: transparent; }
html .cc .ath .ath-rem { display: flex; align-items: center; gap: 8px; font-weight: 500; color: var(--text-2); margin: 8px 0 6px; }
html .cc .ath .ath-rem input { width: 18px; height: 18px; accent-color: #12a150; }
html .cc .ath form .btn { width: 100%; justify-content: center; margin-top: 6px; }
html .cc .ath-err { padding: 12px 14px; border-radius: 10px; background: rgba(255,61,51,.12); border: 1px solid rgba(255,61,51,.4); color: #fff; font-size: 14px; }
html .cc .ath-help { font-size: 14px; color: var(--text-3); margin: 6px 0 0; }
html .cc .ath-help a, html .cc .ath-body a:not([class]) { color: var(--green-text, #2bd47a); }
/* ---- dashboard (logged in) ---- */
html .cc .ath-sec:has(.ath-hero) .ath { max-width: 1080px; }
/* Matteo 17 Nov: more room on laptops (it felt squeezed): bigger padding, wider text column, links in a row */
html .cc .ath-links { display: flex; flex-wrap: wrap; align-items: center; gap: 10px 22px; margin-top: 4px; }
html .cc .ath-links .ath-out { font-size: 15px; margin: 0 !important; } html .cc .ath-links form.ath-lang { margin: 0 !important; }
html .cc .ath-hero { position: relative; display: grid; grid-template-columns: minmax(0, 1fr) 290px; align-items: end; gap: 40px; padding: 46px 52px 0; margin: 0 0 18px; border-radius: 20px; overflow: hidden;
  background: radial-gradient(120% 140% at 100% 100%, rgba(18,161,80,.28), transparent 55%), radial-gradient(90% 120% at 0% 0%, rgba(255,61,51,.14), transparent 60%), rgba(12,14,16,.92); border: 1px solid rgba(43,212,122,.3); box-shadow: 0 30px 80px rgba(0,0,0,.45); }
html .cc .ath-hero-txt { padding-bottom: 44px; min-width: 0; align-self: center; }   /* Matteo 17 Nov: the text centred in the header (the photo still stands on the bottom) */
html .cc .ath-hero-txt:has(.ath-coach-tag) { align-self: end; padding-bottom: 64px; }   /* his own coach view: the text lower, at the bottom (Matteo 17 Nov: then ~half a cm back up) */
html .cc .ath-hero h1 { font-size: clamp(36px, 6.4vw, 66px); line-height: 1; margin: 8px 0 12px; }
html .cc .ath-hero h1 .ath-nm { font-family: var(--head); font-weight: 400; text-transform: uppercase; letter-spacing: inherit; color: #fff; }   /* the name keeps the Anton headline */
html .cc h1 .ath-greet { color: var(--green-text, #2bd47a); font-family: var(--head); }
html .cc h1 .ath-coach-tag { font-size: .45em; color: #b8bec8; letter-spacing: .04em; vertical-align: text-top; margin-right: .15em; }   /* raised, on the left of the name */   /* Matteo 17 Nov: a small "Coach" before his name, nothing else changed */
html .cc .ath-lede { color: var(--text-2); font-size: 17px; line-height: 1.55; margin: 0 0 22px; max-width: 600px; }
html .cc .ath-chips { display: flex; flex-wrap: wrap; gap: 10px; margin: 0 0 18px; }
html .cc .ath-chip { display: inline-flex; align-items: baseline; gap: 8px; padding: 9px 14px; border-radius: 999px; background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.12); color: var(--text-2); font-size: 13.5px; }
html .cc .ath-chip b { font-family: var(--head); font-weight: 400; font-size: 22px; line-height: 1; color: #fff; }
/* Matteo 17 Nov: live chips in the header (race countdown, what is new); links lift a little on hover */
html .cc .ath-live .ath-chip { font-size: 15px; color: #d0d6e0; align-items: center; text-decoration: none; max-width: 100%; transition: transform .15s ease, border-color .15s ease, background .15s ease; }
html .cc .ath-live a.ath-chip:hover { transform: translateY(-1px); border-color: rgba(255,255,255,.3); background: rgba(255,255,255,.09); }
html .cc .ath-live .ath-chip-go { border-color: rgba(43,212,122,.45); background: rgba(18,161,80,.14); }
html .cc .ath-live .ath-chip-go b { color: #2bd47a; }
html .cc .ath-live .ath-chip-ok { color: #2bd47a; border-color: rgba(43,212,122,.35); font-weight: 600; }
html .cc .ath-chip-race .ath-chip-nm::before { content: "· "; color: #b8bec8; font-weight: 400; }
html .cc .ath-chip-nm { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 22ch; color: #fff; font-weight: 600; }
html .cc .ath-pri { flex: none; display: inline-grid; place-items: center; width: 22px; height: 22px; border-radius: 50%; font: 700 12px/1 var(--body); font-style: normal; color: #1a1a1a; }
html .cc .ath-pri-a { background: linear-gradient(135deg,#F3D774,#D4AF37,#A8841F); }
html .cc .ath-pri-b { background: linear-gradient(135deg,#F2F3F5,#C0C4CC,#8E939C); }
html .cc .ath-pri-c { background: linear-gradient(135deg,#E9A86B,#CD7F32,#9A5A1F); }
@media (prefers-reduced-motion: no-preference) {
  /* Matteo 17 Nov: the greeting sweeps in from the left, then the name rises in (phone, tablet, laptop) */
  html .cc .ath-hero h1 .ath-gw { display: inline-block; animation: athSweep .8s cubic-bezier(.2,.8,.2,1) .1s both; }
  html .cc .ath-hero h1 .ath-nm { display: inline-block; animation: athIn .7s cubic-bezier(.2,.8,.2,1) .55s both; }
  html .cc .ath-live .ath-chip { animation: athIn .5s ease .85s both; }
  html .cc .ath-live .ath-chip:nth-child(2) { animation-delay: .97s; } html .cc .ath-live .ath-chip:nth-child(3) { animation-delay: 1.09s; } html .cc .ath-live .ath-chip:nth-child(n+4) { animation-delay: 1.2s; }
  html .cc .ath-live .ath-chip-race .ath-pri { animation: athPulse 2.4s ease-in-out 1s 2; }
}
/* Matteo 17 Nov: date and time boxes stayed wider than their box on phones (iPhone gives them a fixed inner width). Every form: full width, never wider */
html .cc :is(.gl, .av-chr, .nt-day, .rs-form, .rf) :is(input[type=date], input[type=time]) { display: block; width: 100%; max-width: 100%; min-width: 0; box-sizing: border-box; -webkit-appearance: none; appearance: none; min-height: 46px; line-height: 1.2; font: 16px var(--body); padding: 10px 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,.18); background: #0b0d0f; color: #fff; color-scheme: dark; }
html .cc :is(.gl, .av-chr, .nt-day, .rs-form, .rf) :is(input[type=date], input[type=time])::-webkit-date-and-time-value { text-align: left; }
html .cc :is(.gl-r, .av-chr, .gl) > label, html .cc .gl-r { min-width: 0; }
/* Final check 17 Nov: the last hub labels under 14px (50+ readers rule): header eyebrow, language label, report dates and badges, notes day, priority letters, reading times */
html .cc .ath-hero .eyebrow { font-size: 14px !important; }
html .cc form.ath-lang, html .cc form.ath-lang label { font-size: 14px !important; }
html .cc .rp-when, html .cc .rp-badge, html .cc .nt-day, html .cc .ath small { font-size: 14px !important; }
html .cc .gl-prio { font-size: 13px !important; width: 22px !important; height: 22px !important; }@keyframes athIn { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
@keyframes athSweep { from { opacity: 0; clip-path: inset(0 100% 0 0); transform: translateX(-10px); } to { opacity: 1; clip-path: inset(0 0 0 0); transform: none; } }
html .cc .ath-hero-txt:has(.ath-coach-tag) .ath-live { margin-top: 14px; }   /* Matteo 17 Nov: "All caught up" a little lower */
@keyframes athPulse { 0%,100% { box-shadow: 0 0 0 0 rgba(212,175,55,0); } 50% { box-shadow: 0 0 0 6px rgba(212,175,55,.25); } }
html .cc .ath-out { color: var(--text-3); font-size: 13px; text-decoration: underline; text-underline-offset: 3px; }
html .cc .ath-out:hover { color: #fff; }
html .cc .ath-hero-me { align-self: end; }
html .cc .ath-hero-me .sigph img { filter: drop-shadow(0 20px 40px rgba(0,0,0,.55)); }
html .cc .ath-coach { padding: 16px 18px; border-radius: 12px; border: 1px dashed rgba(255,255,255,.25); margin: 0 0 18px; font-size: 14px; color: var(--text-2); }
html .cc .ath-coach p { margin: 0 0 8px; }
html .cc .ath-list { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 !important; }
html .cc .ath-list a { padding: 6px 12px; border-radius: 999px; background: rgba(255,255,255,.08); color: #fff; text-decoration: none; font-size: 13px; }
html .cc .ath-list a[aria-current] { background: #12a150; }
html .cc .ath-list a { display: inline-flex; align-items: center; gap: 6px; }
html .cc .ath-list a { font-family: var(--body, Montserrat, sans-serif); font-size: 14.5px; font-weight: 600; letter-spacing: 0; padding: 8px 14px; }   /* Matteo 17 Nov: easier to read, like the coach tools */
/* Matteo 17 Nov: a bit of life on hover: the pill lifts, glows green and the flag pops */
html .cc .ath-list a { border: 1px solid transparent; transition: transform .18s ease, background-color .18s ease, border-color .18s ease, box-shadow .18s ease; }
html .cc .ath-list a > * { transition: transform .2s ease; }
html .cc .ath-list a:hover, html .cc .ath-list a:focus-visible { transform: translateY(-2px); background: rgba(18,161,80,.18); border-color: rgba(43,212,122,.55); box-shadow: 0 6px 18px rgba(18,161,80,.25); }
html .cc .ath-list a:hover > *, html .cc .ath-list a:focus-visible > * { transform: scale(1.18) rotate(-4deg); }
html .cc .ath-list a[aria-current]:hover { background: #12a150; }
@media (prefers-reduced-motion: reduce) { html .cc .ath-list a, html .cc .ath-list a > * { transition: none; } html .cc .ath-list a:hover, html .cc .ath-list a:hover > * { transform: none; } }
/* Matteo 17 Nov: the calmer roster: a grid of same-size rows, a search box, folded while he looks at one athlete */
html .cc .ath-coach { border-style: solid; border-color: rgba(255,255,255,.12); background: rgba(12,14,16,.6); }
html .cc .ath-roster > summary { list-style: none; cursor: pointer; display: flex; flex-wrap: wrap; align-items: center; gap: 10px 14px; margin: 0; }
html .cc .ath-roster > summary::-webkit-details-marker { display: none; }
html .cc .ath-ro-h { font-family: var(--head); font-size: 22px; letter-spacing: .02em; text-transform: uppercase; color: #fff; }
html .cc .ath-ro-h small { font-family: var(--body); font-size: 14px; font-weight: 700; color: #2bd47a; margin-left: 6px; vertical-align: middle; }
html .cc .ath-ro-cur { display: inline-flex; align-items: center; gap: 8px; font-size: 15px; font-weight: 600; color: #fff; }
html .cc .ath-ro-ch { margin-left: auto; font-size: 15px; font-weight: 600; color: #2bd47a; }
html .cc .ath-roster[open] .ath-ro-cur, html .cc .ath-roster[open] .ath-ro-ch { display: none; }
html .cc .ath-ro-q { display: block; width: 100%; max-width: 360px; margin: 14px 0 12px; padding: 10px 14px; font-size: 16px; color: #fff; background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.16); border-radius: 10px; }
html .cc .ath-ro-q:focus { outline: none; border-color: #12a150; }
html .cc .ath-roster .ath-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 6px; }
html .cc .ath-roster .ath-list a { display: flex; align-items: center; gap: 10px; min-width: 0; padding: 7px 10px; border-radius: 10px; background: transparent; font-size: 15px; }
html .cc .ath-roster .ath-list a:hover, html .cc .ath-roster .ath-list a:focus-visible { transform: none; box-shadow: none; background: rgba(18,161,80,.14); }
html .cc .ath-roster .ath-list a:hover > *, html .cc .ath-roster .ath-list a:focus-visible > * { transform: none; }
html .cc .ath-roster .ath-list a[aria-current] { background: rgba(18,161,80,.3); border-color: rgba(43,212,122,.6); }
html .cc .ath-roster .ath-list a[hidden] { display: none; }
html .cc .ath-ln { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
html .cc .ath-lf { border-width: 1.5px !important; box-shadow: none !important; }
html .cc .ath-lf .ph-ini { font-size: 12px; }
@media (max-width: 760px) { html .cc .ath-roster .ath-list { grid-template-columns: 1fr 1fr; } html .cc .ath-roster .ath-list a { padding: 6px 4px; font-size: 14px; gap: 8px; } html .cc .ath-ro-q { max-width: none; } }
html .cc .ath-flag-e { display: inline-grid; place-items: center; width: 14px; height: 14px; border-radius: 50%; overflow: hidden; box-shadow: 0 0 0 1px rgba(255,255,255,.35), 0 1px 4px rgba(0,0,0,.4); flex: none; }
html .cc .ath-flag-e span { font-size: 20px; line-height: 1; }
html .cc .ath form.ath-lang { display: inline-flex; align-items: center; gap: 8px; margin: 0 0 0 14px; vertical-align: middle; }
html .cc .ath-lang label { font-size: 13px; color: var(--text-3); margin: 0; }
html .cc .ath-lang select { font-size: 16px; padding: 5px 28px 5px 10px; min-height: 38px; height: auto; width: auto; border-radius: 8px; margin: 0; }   /* Matteo 17 Nov: as before, a touch slimmer; no fixed height so the language always shows */
html .cc img.ath-flag { width: 14px; height: 14px; aspect-ratio: 1 / 1; object-fit: cover; border-radius: 50%; box-shadow: 0 0 0 1px rgba(255,255,255,.35), 0 1px 4px rgba(0,0,0,.4); margin: 0; flex: none; }
html .cc .ath-coach-tools { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin: 14px 0 0; padding-top: 14px; border-top: 1px solid rgba(255,255,255,.1); }
html .cc .ath-coach-tl { flex-basis: 100%; font-size: 11px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--red-text, #ff3d33); }
html .cc .ath-coach-tools .av-boardlink { display: inline-flex; align-items: center; gap: 8px; margin: 0; padding: 9px 14px; border-radius: 999px; border: 1px solid rgba(255,255,255,.16); background: rgba(255,255,255,.05); color: #fff; font-size: 13.5px; font-weight: 600; text-decoration: none; }
html .cc .ath-coach-tools .av-boardlink:hover { border-color: #009a44; }
html .cc .ath-allposts { margin: 4px 0 18px; font-size: 14px; } html .cc .ath-allposts a { color: var(--green-text, #34c46a); }
html .cc .ath-jump { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 18px; padding: 2px; }   /* Matteo 17 Nov: the last pill ("Worth reading") ran off the right edge; the pills now wrap */
html .cc .ath-jump::-webkit-scrollbar { display: none; }
html .cc .ath-jump a { flex: none; padding: 9px 15px; border-radius: 999px; border: 1px solid rgba(255,255,255,.14); background: rgba(12,14,16,.85); color: var(--text-2); font-size: 15px; font-weight: 600; text-decoration: none; transition: border-color .2s, color .2s; }   /* Matteo 17 Nov: bigger (was 13px) */
html .cc .ath-jump a:hover { border-color: #12a150; color: #fff; }
html .cc .ath-s { padding: 28px 28px 30px; border-radius: 18px; background: rgba(13,15,17,.9); border: 1px solid rgba(255,255,255,.09); margin: 0 0 18px; scroll-margin-top: 100px; }
html .cc .ath-s.ath-mine { border-color: rgba(43,212,122,.4); background: linear-gradient(180deg, rgba(18,161,80,.1), rgba(13,15,17,.9) 60%); }
html .cc .ath-s > h2 { display: flex; align-items: center; gap: 12px; font-size: clamp(24px, 3.6vw, 30px); margin: 0 0 18px; }
html .cc .ath-hic { flex: none; display: grid; place-items: center; width: 40px; height: 40px; border-radius: 12px; background: rgba(18,161,80,.15); border: 1px solid rgba(43,212,122,.35); }
html .cc .ath-hic.ath-logo { background-repeat: no-repeat; background-position: center; background-size: 58%; }
html .cc .ath-hic.logo-vekta { background-color: #FFC20E; border-color: #FFC20E; }   /* Matteo 17 Nov: the Vekta mark on its yellow, like the Vekta tile */
html .cc .ath-hic svg, html .cc .ath-ic svg { width: 21px; height: 21px; fill: none; stroke: var(--green-text, #2bd47a); stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
html .cc .ath-body > :first-child { margin-top: 0; }
html .cc .ath-body > :last-child { margin-bottom: 0; }
html .cc .ath-body p { color: var(--text-2); }
html .cc .ath-body h2, html .cc .ath-body h3 { font-size: 15px; font-family: var(--body); font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--red-text, #ff3d33); margin: 24px 0 12px; }
html .cc .ath-body a:not([class]) { color: var(--green-text, #2bd47a); }
html .cc .ath-body .wp-block-buttons { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px; margin: 0 0 12px; }
html .cc .ath-body .ath-tools { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); }
html .cc .ath-tile, html .cc .ath-file { position: relative; display: flex; align-items: center; gap: 14px; padding: 16px 16px; border-radius: 14px; background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.1); color: #fff; text-decoration: none; transition: transform .25s cubic-bezier(.2,.8,.2,1), border-color .25s, background .25s, box-shadow .25s; }
html .cc .ath-tile:hover, html .cc .ath-file:hover, html .cc .ath-tile:focus-visible, html .cc .ath-file:focus-visible { transform: translateY(-3px); border-color: rgba(43,212,122,.6); background: rgba(18,161,80,.1); box-shadow: 0 14px 34px rgba(0,0,0,.4), 0 0 0 1px rgba(43,212,122,.2); }
html .cc .ath-ic { flex: none; display: grid; place-items: center; width: 46px; height: 46px; border-radius: 13px; background: linear-gradient(145deg, rgba(18,161,80,.28), rgba(18,161,80,.08)); border: 1px solid rgba(43,212,122,.35); transition: transform .25s; }
html .cc .ath-tile:hover .ath-ic, html .cc .ath-file:hover .ath-ic { transform: scale(1.08) rotate(-4deg); }
html .cc .ath-tt { display: grid; gap: 3px; min-width: 0; flex: 1; }
html .cc .ath-tt b { font-weight: 600; font-size: 15.5px; line-height: 1.25; }
html .cc .ath-tt small { color: var(--text-3); font-size: 13px; line-height: 1.35; }
html .cc .ath-go { color: var(--text-3); font-size: 18px; transition: transform .25s, color .25s; }
html .cc .ath-tile:hover .ath-go { transform: translateX(4px); color: var(--green-text, #2bd47a); }
html .cc .ath-tools .ath-tile { flex-direction: column; align-items: flex-start; gap: 12px; padding: 16px; }
html .cc .ath-tools .ath-ic { width: 40px; height: 40px; border-radius: 11px; }
html .cc .ath-tools .ath-tt b { font-size: 14.5px; }
html .cc .ath-tools .ath-go { position: absolute; top: 14px; right: 14px; font-size: 16px; }
html .cc .ath-file { margin: 0 0 10px; }
html .nl-band { display: none !important; }   /* Matteo 17 Nov: the site's English newsletter sign-up is not shown inside the athlete hub (clients, own language) */
html .cc .ath-ic.ath-logo { background-repeat: no-repeat; background-position: center; background-size: 60%; }
html .cc .ath-ic.logo-whatsapp { background-color: #25D366; border-color: #25D366; }
html .cc .ath-ic.logo-vekta { background-color: #FFC20E; border-color: #FFC20E; background-size: 54%; }
html .cc .ath-ic.logo-vivify { background-size: cover; border-color: #1C4650; }
html .cc .ath-ic.logo-tp { background-color: #010F31; border-color: #010F31; background-size: cover; }
html .cc .ath-ic.logo-skool { background-size: cover; border-color: rgba(255,255,255,.22); }
html .cc .ath-ic.logo-youtube { background-color: #FF0000; border-color: #FF0000; background-size: cover; }
html .cc .ath-ic.logo-instagram { background-size: cover; border: 0; }
html .cc .ath-body ol.wp-block-list, html .cc .ath-s ol.wp-block-list { margin-bottom: 20px; }   /* Matteo 17 Nov: space between the Share steps and the cards under them */
/* Matteo 17 Nov: availability and goals summaries in the hub, each with a button to its own page */
html .cc .av-sumbox { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 14px; padding: 16px; border-radius: 14px; background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.1); }
html .cc .av-sumt { margin: 0; flex: 1 1 260px; min-width: 0; } html .cc .av-sumt p { margin: 0 0 6px; }
html .cc .av-sumt small { display: block; color: var(--text-3); font-size: 13px; margin-top: 4px; }
html .cc .av-sumbox .btn { margin: 0; max-width: 100%; white-space: normal; height: auto; text-align: center; }
html .cc .gl-sumev { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
html .cc .gl-prio { display: inline-grid; place-items: center; width: 22px; height: 22px; border-radius: 50%; font: 700 12px/1 var(--body); color: #1a1a1a; flex: none; }
html .cc .gl-prio-a { background: linear-gradient(135deg, #F3D774, #D4AF37 55%, #A8841F); } html .cc .gl-prio-b { background: linear-gradient(135deg, #F2F3F5, #C0C4CC 55%, #8E939C); } html .cc .gl-prio-c { background: linear-gradient(135deg, #E9A86B, #CD7F32 55%, #9A5A1F); }
html .cc .ath-back { margin: 18px 0 0; }   /* Matteo 17 Nov: the back link was hard to see: now a green pill */
html .cc .ath-back a { display: inline-flex; align-items: center; gap: 8px; padding: 10px 18px; border-radius: 999px; background: rgba(1,138,68,.16); border: 1px solid rgba(52,196,106,.55); color: #34c46a; text-decoration: none; font-weight: 700; font-size: 15px; transition: background .2s, color .2s; }
html .cc .ath-back a:hover { background: #018a44; color: #fff; }
html .cc .ath-dl { flex: none; padding: 8px 16px; border-radius: 9px; background: #12a150; color: #fff; font-size: 14px; font-weight: 600; }
html .cc .ath-empty { display: flex; align-items: center; gap: 16px; padding: 18px; border-radius: 14px; border: 1px dashed rgba(43,212,122,.35); }
html .cc .ath-empty p { margin: 0; color: var(--text-2); }
html .cc .ath-reads { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 14px; margin: 0 0 8px; }
html .cc .ath-read { display: flex; flex-direction: column; border-radius: 14px; overflow: hidden; background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.1); color: #fff; text-decoration: none; transition: transform .25s cubic-bezier(.2,.8,.2,1), border-color .25s, box-shadow .25s; }
html .cc .ath-read:hover, html .cc .ath-read:focus-visible { transform: translateY(-4px); border-color: rgba(43,212,122,.6); box-shadow: 0 16px 36px rgba(0,0,0,.45); }
html .cc .ath-read-img { display: block; aspect-ratio: 16/10; background: #15181b center / cover no-repeat; transition: transform .5s; }
html .cc .ath-read:hover .ath-read-img { transform: scale(1.05); }
html .cc .ath-read-t { padding: 12px 14px 4px; font-weight: 600; font-size: 14.5px; line-height: 1.3; position: relative; background: inherit; }
html .cc .ath-read small { padding: 0 14px 14px; color: var(--text-3); font-size: 12.5px; margin-top: auto; }
html.ath-anim .cc .ath-s, html.ath-anim .cc .ath-hero { opacity: 0; transform: translateY(22px); transition: opacity .7s ease, transform .7s cubic-bezier(.2,.8,.2,1); }
html.ath-anim .cc .ath-s.in, html.ath-anim .cc .ath-hero.in { opacity: 1; transform: none; }
html.ath-anim .cc .ath-s.in .ath-tile, html.ath-anim .cc .ath-s.in .ath-read, html.ath-anim .cc .ath-s.in .ath-file { animation: ath-pop .55s cubic-bezier(.2,.8,.2,1) both; }
html.ath-anim .cc .ath-s.in :is(.ath-tile, .ath-read):nth-child(2) { animation-delay: .06s; } html.ath-anim .cc .ath-s.in :is(.ath-tile, .ath-read):nth-child(3) { animation-delay: .12s; }
html.ath-anim .cc .ath-s.in :is(.ath-tile, .ath-read):nth-child(4) { animation-delay: .18s; } html.ath-anim .cc .ath-s.in :is(.ath-tile, .ath-read):nth-child(n+5) { animation-delay: .24s; }
@keyframes ath-pop { from { opacity: 0; transform: translateY(12px) scale(.98); } to { opacity: 1; transform: none; } }
@media (max-width: 760px) {
  html .cc .ath-sec { padding-block: 24px 56px; }
  html .cc .ath-login { padding: 24px 18px; }
  html .cc .ath-hero { grid-template-columns: 1fr 152px; gap: 8px; padding: 24px 16px 0; }   /* Matteo 17 Nov: the signed photo bigger on phones (was 104px) */
  html .cc .ath-hero-me { align-self: end; margin-bottom: 0; min-width: 0; overflow: hidden; }   /* at the bottom again, kept inside its column (Matteo 17 Nov) */
  html .cc .ath-hero-txt { min-width: 0; position: relative; z-index: 1; }
  html .cc .ath form.ath-lang, html .cc .ath-links form.ath-lang { display: flex; flex-basis: 100%; margin: 6px 0 0 !important; }   /* on its own line, with room above it, under Change password / Log out */
  html .cc .ath-links { gap: 8px 18px; }
  html .cc .ath-hero h1 { font-size: clamp(32px, 10vw, 44px); }
  /* Matteo 17 Nov: "Good evening," on one line on phones, sized to the text column (fits "Buon pomeriggio," too) */
  html .cc .ath-hero-txt { container-type: inline-size; min-width: 0; }
  html .cc .ath-hero h1 { font-size: clamp(24px, 14cqi, 40px); }
  html .cc .ath-hero h1 .ath-greet, html .cc .ath-hero h1 .ath-gw { white-space: nowrap; }
  html .cc .ath-hero-txt { padding-bottom: 22px; }
  html .cc .ath-lede { font-size: 14.5px; }
  html .cc .ath-chips { gap: 8px; }
  html .cc .ath-chip { padding: 7px 11px; font-size: 12.5px; gap: 6px; }
  html .cc .ath-chip b { font-size: 18px; }
  html .cc .ath-live .ath-chip { font-size: 14px; padding: 7px 12px; white-space: nowrap; }   /* 14px minimum (50+ readers) */
  /* the race chip on two tidy lines: badge + days, then the race name */
  html .cc .ath-live .ath-chip-race { flex-wrap: wrap; row-gap: 2px; border-radius: 16px; }
  html .cc .ath-live .ath-chip-race .ath-chip-nm { flex-basis: 100%; max-width: 100%; }
  html .cc .ath-chip-race .ath-chip-nm::before { content: none; }
  html .cc .ath-hero-txt:has(.ath-coach-tag) { padding-bottom: 34px; }
  /* Matteo 17 Nov: the photo in line with "Good evening", and the line under it with some air */
  html .cc .ath-hero-txt .ath-hello { align-items: flex-start; }
  html .cc .ath-hero-txt .ath-hello h1 { margin-top: 6px !important; }
  html .cc .ath-hero-txt .ath-hello .ath-me-ph { margin-top: 8px; }   /* Matteo 17 Nov: the photo (and "Remove photo") ~2 mm lower on phones */
  html .cc .ath-hello ~ .ath-lede { margin-top: 18px; }
  /* Matteo 17 Nov: on phones the line under the greeting runs across the header (it was squeezed into the left column; the photo sits lower) */
  html .cc .ath-hero-txt .ath-lede { margin-right: -130px; max-width: none; }
  html .cc .ath-hero-txt .ath-lede.ath-lede-narrow { margin-right: 0; }   /* only if it would touch the photo (short header, long language) */
  html .cc .ath-s { padding: 22px 16px 24px; }
  html .cc .ath-body .ath-tools { grid-template-columns: 1fr 1fr; gap: 10px; }
  html .cc .ath-tools .ath-tile { padding: 14px 12px; }
  html .cc .ath-reads { display: flex; overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none; margin: 0 -16px 8px; padding: 2px 16px 6px; }
  html .cc .ath-reads::-webkit-scrollbar { display: none; }
  html .cc .ath-read { flex: 0 0 72%; scroll-snap-align: start; }
}
</style>
CSS;
});

/* ---------- the hub as a phone app (Matteo 17 Nov): "Add to home screen" ---------- */
// The icon is the site icon (Appearance > Customize > Site Identity: the square logo). The manifest makes it open full screen at /athletes/.
add_action('init', function () {
    if (!isset($_GET['cc_manifest'])) return;
    // Matteo 17 Nov: the app icon is the square Cigala Cycling Coaching logo, edge to edge (was the small site icon)
    $icons = []; foreach ([192, 512] as $s) $icons[] = ['src' => 'https://coaching.cigalacycling.com/wp-content/uploads/2026/11/cigala-hub-app-' . $s . '.png', 'sizes' => $s . 'x' . $s, 'type' => 'image/png', 'purpose' => 'any'];
    header('Content-Type: application/manifest+json; charset=utf-8'); header('Cache-Control: public, max-age=86400');
    echo wp_json_encode(['name' => 'Cigala Cycling Coaching: athlete hub', 'short_name' => 'Cigala Cycling', 'start_url' => '/' . CC_ATH_SLUG . '/?source=app', 'scope' => '/' . CC_ATH_SLUG . '/',
        'display' => 'standalone', 'background_color' => '#08090a', 'theme_color' => '#08090a', 'icons' => $icons], JSON_UNESCAPED_SLASHES);
    exit;
});
add_action('wp_head', function () {
    if (!is_page(CC_ATH_SLUG)) return;
    // Matteo 17 Nov: no website chat bubble (OpenWidget, loaded by the cookie banner after consent) inside the hub: athletes have
    // notes, voice notes and WhatsApp. Marking it "already loaded" first means the banner script never loads it here.
    echo '<script>window.__owLoaded=true;</script><style id="cc-hub-nochat">#cc-chat,#openwidget-container,[id^="openwidget"],iframe[src*="openwidget"]{display:none!important}</style>';
    echo '<link rel="manifest" href="' . esc_url(add_query_arg('cc_manifest', 1, home_url('/'))) . '"><meta name="apple-mobile-web-app-title" content="Cigala Cycling"><meta name="mobile-web-app-capable" content="yes">'
       . '<meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-status-bar-style" content="black"><meta name="theme-color" content="#08090a">'
       . '<link rel="apple-touch-icon" sizes="180x180" href="https://coaching.cigalacycling.com/wp-content/uploads/2026/11/cigala-hub-app-180.png">' . "\n";   // iPhone home-screen icon
});
add_filter('cc_ath_before_reports', function ($html, $view, $coach) {   // a small tip on phones, until they add it or tap "Not now"
    if ($coach || !$view) return $html;
    return '<div class="ath-a2hs" hidden><p><b>' . esc_html(cc_L('Add the hub to your home screen', 'Aggiungi l’area alla schermata Home')) . '</b>'
        . '<span class="a2hs-ios" hidden>' . esc_html(cc_L('On iPhone: tap Share, then “Add to Home Screen”.', 'Su iPhone: tocca Condividi, poi “Aggiungi alla schermata Home”.')) . '</span></p>'
        . '<button type="button" class="btn btn-go a2hs-go" hidden>' . esc_html(cc_L('Add to home screen', 'Aggiungi alla Home')) . '</button>'
        . '<button type="button" class="btn btn-ghost a2hs-no">' . esc_html(cc_L('Not now', 'Non ora')) . '</button></div>'
        . '<script>(function(){var b=document.querySelector(".ath-a2hs");if(!b)return;var k="cc_a2hs_no",ev=null;'
        . 'function no(){try{return localStorage.getItem(k)}catch(e){return null}}'
        . 'if(no()||matchMedia("(display-mode: standalone)").matches||navigator.standalone||!matchMedia("(max-width: 900px)").matches)return;'
        . 'if(window.matchMedia("(display-mode: standalone)").matches||navigator.standalone)return;'   // Matteo 17 Nov: already on the home screen: no "add to home screen" card
        . 'var ios=/iphone|ipad|ipod/i.test(navigator.userAgent);if(ios){b.querySelector(".a2hs-ios").hidden=false;b.hidden=false;}'
        . 'addEventListener("beforeinstallprompt",function(e){e.preventDefault();ev=e;b.querySelector(".a2hs-go").hidden=false;b.hidden=false;});'
        . 'b.querySelector(".a2hs-go").addEventListener("click",function(){if(ev){ev.prompt();ev.userChoice.then(function(){b.hidden=true;});}});'
        . 'b.querySelector(".a2hs-no").addEventListener("click",function(){try{localStorage.setItem(k,"1")}catch(e){}b.hidden=true;});})();</script>'
        . '<style>html .cc .ath-a2hs{display:flex;flex-wrap:wrap;align-items:center;gap:10px 14px;margin:0 0 14px;padding:12px 16px;border-radius:12px;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.04)}'
        . 'html .cc .ath-a2hs[hidden],html .cc .ath-a2hs [hidden]{display:none!important}html .cc .ath-a2hs .a2hs-ios{display:block}html .cc .ath-a2hs p{margin:0;flex:1 1 220px;font-size:14px;color:var(--text-2)}html .cc .ath-a2hs b{display:block;color:#fff}html .cc .ath-a2hs .btn{width:auto;margin:0}</style>' . $html;
}, 5, 3);
