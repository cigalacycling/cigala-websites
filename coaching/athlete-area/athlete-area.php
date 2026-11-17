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
    static $IMG = ['be' => 'UklGRowAAABXRUJQVlA4IIAAAACwBwCdASp4AFoAPjEWiUMiISEUX1wAIAMEsoBrrIAfgBpgPwA/YAA4opcUbfcnT1aw7HffvwsZ9lixkE66tkwWXKNi8ETAAP7+pWydvGl/xmH//8obF6o5hgXWtWIArfUo7n0rJ4lol9xygFRr0/7dkACnFhD+cqK4dpmL1nAAAA==', 'ch' => 'UklGRnQCAABXRUJQVlA4IGgCAACQEwCdASp4AFoAPjEYiUMiIaEVrwwAIAMEoA1fG3/qv5Aa41zP8Zfy06SHbnthxyFAf138t/7v7s/6B0gH6Hf47dAfqr+t3ux/wD/Yf13sAP1a6wD0Cf1c9Hr/W/7L4P/2+9F/Vq+ksygTwp/o/UAF5oqYyxGuzEoavrzMlS/C9mF3ILGAqmQvx9SJEgZnU4+dcJzpRIITfmD1R4SnbqWS6E397mAA/vIiS3zgStlpn5ep0+p09ShCngI1L1PJn29vl0XBoNGVafmPLG7HFoHUN02B/Ai2UaNqZr5nffz+zFT+NJp721rjK9flf1nW6IEWzcuLvcBbQySxwzvNZo/FqfQgnYYh9RH8N6bOrwkUJWR/Ojuhf+E2EAXGcfxAAjLlZl8Y+7RBK/vAf3cZv/GQKixGfYxtpQf06iNZJkXO6vn5RLYgVpNwkj33YJrvn84cS9KPLweu5cCzB6TWHdlJNnkVI3X7MMG3PBdPRS9rsT8lrQ46+vPA9lo3pK/mvb/53//7SdAEp9pO03pzIvK1+MH+E62afekR8tq+08g6rEGr+PV9H+mf/nsVxzslf11v5/eDPGR93zhaekuifdAL51nzXEdICpuOmnZtXljrpIdebYXEF0lJZODOR8fq96NnsKkCC6JynuVBxr9h1L6Z/+exXHOyym0L0DHfjjP5NVeb1n2qRBylGpbhbatqGVKzglwLixbE3M+pqbFrzTJ9fCp8MWEndZS/0YP6uMjs6y2fRdyAMqZXidWze0VTCPXTJvhOtDGOKpPJGFz4PXRDoWZoKvGM3soQHKMC3JfMBIoNAAAAAAAA', 'cy' => 'UklGRvoFAABXRUJQVlA4IO4FAABQIgCdASp4AFoAPjEWiUOiISEUqbyYIAMEoA1mkAPwA2C3mf44fir8vls/xn3k5zO0f8l9rvvA9Rv23eoz/N/zG7QHmA/k39u/4H9E94r0T+gB/Q/9N1hXoAeVL+4HwO/t3+yXwC/r3qtniXrk/tH5Ada71o9Y84r9UPwnCDtM/3X8ndlz4tHzD/C/mRzGfUfzSv8jxg1AD+Tf2T/b+xv/F/8z7mfZl88f8n3A/5D/P/8p+bX+O/////8i37JeyX+qRYp4oEU02xHmv9C7bFs8QKhNQvzI8F//ZiBT/EyZ3t5VkZHQsBZ6NK5Txam47G1SkFtB+yDbRhjSY5i1pNIStYMkURKMyI4U+L7JMhxbOFqcf5oy4VH92kCYAP7+3XgjDH7E1bNc0J3mQM3gVJfvs45WJ15drJ2zby2m+t2dxEKAFfsIxa3ACK/YNf/8T+nGcLSxu/RQlM+ZwhiAk0J/xvt3p72pyqkS7pD7eLx6X1QM4B+tDZh9UqRKgTyx/Bov9XL3VDYjv0kx7NAPf/PqtumGxHTKbOh19FU9Jhg4EMVc7qbG90dGgyy01UvcVsiqy6rpwBRbUmvcObKygc/iRB3aMnzAE+s258oJcQ7zKbxPwxzcDoX2ftiHBq4ZiGJ2ccoXDlAeBw+JRkp36n/Z6Q3+ZCmUxrHpmZsIcsf9S9Kd7w+vMyigRK2B8k+3CaNh9yUuPA8rz6GPvGsthllfhk2+y1phEM0tGuAg2KbhKtbCRCa07iEYr4r64MP2jQ71jxXJAKXNGfeZu43V1+yKU5h+hJVTz4KGHdyMlm/cSpB5JfHWpo6WiOCvY0VbKzBe7u0D2YpQhev6hpVw3uQRNGYO0UXmuekhOP9obYIi/BwPlHL8obe1Kr2DR76qbgWoRMseTZ9Xi0eShQf0Pyh204vpP4AD9IaAsFjrkc1ddfsLO42O84Rutndmnl3dPuBI4CsbhXqUHVQAams/8E0uNtoH4dKE2J7yRU/TuZg/chRy+sGw8LC6IzFvx8mXKKIQ3MeeP0Kk74B4n0+NQuLBVvRKqf3EwafHLIb4Hdg+RE5P8yusXzk7Wrgxtpdt6xdv5bUNr5FpSS/7o+PXcz31nEj4t5zWNtrmmWjh+6d59jjOvOBOOsnqfTi31Baw0qHmrMyToSXfbkY/We0q2r7x+s1n/z7GP1ct/t/ydlH+2G+kHwCxy9Rs5EHty7Lr6IO4JJyL+KNRWQiR6vmvxTgMb7zjK6+BY0jY7J+x4raKCt4iYz//7+2CvPgk2blZC2BKnO7fKpoyKz6I1cD75UwwTCNaf5DOmERt+TlUHVcpkFlRcomlQSijZt51/7bQlLx260OV+muaDaIrTnLMGPXAwGW1rqWxXMgICrLB9vNu75jp0rWfOq8NWiCmiannKJa2lX5L4Bz2mMCEhvEy8oZDNqY8YQ0bj4MqJlQtWHeLTouf7C00YHxmElIgEkIsD/kVSiL7Poyc9hBcY02Bzt2kYGBR/Rf+SS5Be7B1BNANumxmNUf7j/5rBWZ1gXQFS3TyKkFU/E3x0YBo33CMPFrfssWZz3PboU86UdTbMVET0AYmz/TOrQElkXHum2oVG2rthfWB4qUM9jB/oM4JpGE7R+SN0I5V7Lt9Rr7m3vnwMHs2zmOmAA2ubKltCRT+Wb1F/WGv0PP1Ex8sZDGFXKpuO/bzRCpRx5mP14UO2XGOmP0W/2iZDxCPorJWtLOl44mNF65iCpYh7uUGilf10HxiSGTlxDwXaz686PNfwPb/VE/Bzi7f+SYxqlgyEV3QxAz6tmvK/iKLvGHFejGy7KC1hhOj2l57P86/HqTbf/epseHaD7FDVYjgRb7MFBhEa2dTszwGaAXKBJCkrpHQyj5KojR8+W9HlVUiBeFoQ2rrx/kFnLnlpEv2geCARqKLi7HvNpFQ9voSNXewkr819Gigg7M5MEzzLolRauaBlqkoba94N1X/dP3nuiTHJ1Vv//u+tXkkHlHMjX5Q4N4MViZcD6H9RbUwGmxgAAAAAAA=', 'es' => 'UklGRtQAAABXRUJQVlA4IMgAAADQCgCdASp4AFoAPjEWiUMiISEVpAAgAwSxgEoAfiBtJHFvwY/ZnmDNAu0FoA/gH5AYoB6/92Af4AC0GMA3Og37cku9uD5hjdyQj4CCxgG/jaMdhuoE5hjdT9+3zavK8AD++ajvvsUNPG/Dy9kCJyTgcz5//nVcP/dgVNIO9xPnxLh7ifV7mE/6+4FtBWsldoM7gtW1UZasutWXWszEAAPn/CKpvgnKwj5DrYP3SPDeziL22MGEoYWZ2KGhpvAUs2/roQhwAAAAAA==', 'fr' => 'UklGRogAAABXRUJQVlA4IHwAAADwBwCdASp4AFoAPjEWiUMiISEUVAAgAwSygEqB/APxV1QrgH4m/qTXfgG56NQSXaFbY19yg/lPH3J5TnfYz7/KePuTynO+uAAA/v37iyu1UHj/lAGles/itnj//619A6kWzXlpfsviADJFLc7qj2xFxj/dYAAAAAAAAAAA', 'gr' => 'UklGRtYCAABXRUJQVlA4IMoCAACQFwCdASp4AFoAPjESiEKiISEXWR+IIAMEtBZgAcd5gH4gbQjwD8O/xz6w/Vzvzk//L190+2v3ifxP7WesA3AH6Af2z+6e+V/Zv4B1gH9y/s3ozeyB6AH6q+ib+qvwa/uZ6MP//zgD+Mfg1GgH0APAA1QL8A/E3+AeYAPIC490U8QTxZlawbu1jjsIDO8NZY5RtUVjdY8/YEXw/fu+kwUVu5uM0PYgWHPVPFPJFqa+h3Fs5lczBhYEROhZjEYcV3NuaewBQAD++ajvU6fj4fxgPxgPxDPrhrL2uv9NW8//83UXiEkajmLCxpCEczylgG1+43aNSKoGDWJStxy1heDW27YA2oaGfv17/ymf9S4V2jvOdVNrSXpc8n0NFLzyltt7mNgdhQ0QtlKsifkdXvx8hLbmb4qHH+lChBvg3E37kvcvaibPq704qMNMgx81HueJA1HHlnuGLoYu3No8oIlc8elP/tDWrd78cjH5mM4mVzdZZKQuY+378x+FAbFnbVQ25bMPjiFiTi502mXEJiQoci4wMFJFODl9C6hmwiyL5Ljhvw4F/ZmaLSD+MXfh0o8Oj5BRLalZv//AINyi2XUbhc6WMEaEOt5X2CcwIGvjAC3hFvz53lA7d+NOcS78Ml42nk63Rra9Dzo0as746Kl1n+NzQ+RAKG4B3gNqjuwBzvgILvvVOIG+p6zadqk8GRbgNVpHew6LAPMpBflWkOuP41xID+zKfzk3tMHzEDhQk0k7+g+ecbemDQeAzLK1/z3+G6g9UIsBFUIsCPjVf4ZHya1kIq4Y3T/907mGMq1bPwCsqK/S7tNdX9f0Krwyo8snovHxW7stm8oRIieWIoyN1E8mOod61J+4eSnfaU0hJ+1xqYj9nnccdc7VRemI/6Mc5YPK7EaEUEl5LkM5OQyMADY+p+XjAfj4fxgPxgPuTnB027KXU5YAAAA=', 'hr' => 'UklGRmQEAABXRUJQVlA4IFgEAABQHgCdASp4AFoAPjEYikOiIaESCV2EIAMEsQBqntv/VfxV2sztP4x/hBylfgfJ2+R37L+Q/ss/xf5GdRF/gPyd+AHOA/Rz/M/5n3a/65+pPYAfzD/KdYB6AH7Gejh/nf7n8Fv64f9r/i/Aj+qWaAfwD8AO/H+efh3+s3S4ngXyX8IPwx9wP4B+AG2c3PH+AfgB+//OAawB/AP5T9onvi/j/5Kf0T//+ph6FH9D/LX+08gB+jZXOixO9FR2oQARKZxC9GAfaVt5+fqmPaxg/igk/B37A3C3BWFv4Aq9E+MycISJteOYtiY5rM4fNP8y70A2mj1Xm3qxPslJgAD++U82mmvOp/y08eT/0BP/QE/8/8AAn0UZQ6EbJXIDrPoFqNpZJRLwu4l02PnSwr3ukvisdFgzQN/27QZ4UQZOy2RTW5j795QI3DE96KbY/k5mzQl/oX/gVEvLPuVJzIMQPZkKXDtnetdMwSLLxrqoMBbGgyoUi9vjBQCHCsxC3nbdQzFy5NAo7lSdEh4iFQkavCuttlKkxTqoUPDjO5Os9a1yS56FGY4lNT5w3OOYVf7BU36yr7Qzpo009mUMfLiTu2DCjOoELmKRpsMC2NBlQpF7fGChd5OU44snZkKbSF1cskhsxOtz57D9qi09xA87YT4unClZEM2/If/WbuRHbzUhTAqb+3vctYqTmHYlH3Qx5bGo+bKvo4jZjJQ+wXKO/5yJydCMbQ/KA1BQES41NEOVKM4d2HAHnVFP6KfV/Qbn9WBf7Wj+JiUiThzKGiLVWv7m1+IlApdGOBuldqGuiP1xNVMqQAO/+NYVwN8Zk6xx4FwfWLccFFCaFF3+qCl9oJPdQDDTcfl8KqPBR2MB4zrInCV/nIlK+NHMXeRMgZukKVLneno8RFF1+eBnQE1nPilG2VNADY3PsAHdIAkUDuwLhRJkP0csvl/No+Tq6tUhGd38F/5abuMKwWo75EINra5VE/P66SpK/vb9hkY9Agmfdb2h2FP/S4x7PBkEzuLu5XUeZR96dnesH+jft7S/8+Mmh0yLmjp1VpO+FZXRunh/xf//C8IOi58ULdtalKqRv2Cy+WaFOc1M8N7aO7CCuTl0fTRT7QObg/10kOEiZKPZGkMn3N15ZbSgPpNAO39RtIVnN3kCOr/+N/IgSvExBIwCfq0yWX3LTWSDlnrRuDfpInaYFaUgR+IBlHiK9IJzLP1PKvtAGYPiPYUF5fBTHpkhJ3QXCZiWq3y0ioii03aG/FwA9JaVbVaX2KZ3xyA9U7JVZW0wdcV8I0Lyyr7vEdAIE2OWcQDKPEV6QTuzuVPKvhzu2f35aueLA3B/3FgPG4gOEnDvyyl57k8beez8L+Cf+o6p+p1PSzi8Id6etqk8tgVxG2s7x0e7vBIRa9qet47kNP3mCnz0UMT5D3DV6Ej4VCQxKqI//SDxIDi5ZbQd8K6zsfepO5XYQAAyauhiCG0+w3AAAAAAAA==', 'ie' => 'UklGRooAAABXRUJQVlA4IH4AAAAQCACdASp4AFoAPjEYikOiIaEUX1wAIAMEsoBKgf1X8ANUK6b+AH4k1/4Cqe7aOZmlwRYyCddWyYLLlGxeCPaeCrq27ngixj8gAP7tztA2S3JgizqML/aNf0aH//yhNXm+S1No+vDNoVsiXfv6eg/TBAcEB/wAAAAAAAAAAAA=', 'it' => 'UklGRpgAAABXRUJQVlA4IIwAAAAQCACdASp4AFoAPjEWiUMiISEUVAAgAwSygGs1Dj8A/FXZ8OAfib+pNd+Aqn6X7+aJFiyiS7QrbGvuUH8p4+5PKc77Gff5Tx7QAP7xlW60w71OO1rg2l/wyFZdet9f/+kUR0zbzUt28gV/ntxawIjukh+PcGPD/oLlJ8HPDVCbXtvZuLL1YW7jk1XAAA==', 'pt' => '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', 'si' => 'UklGRsgDAABXRUJQVlA4ILwDAADQGACdASp4AFoAPjEYikOiIaERVYwgAwSxAGr4gBmgHsRWB+nfhH8TcuV4p/z32k+8T+jfiBqGPMB+pv+k9u30I/kB7gH9J/mfWS+gB+u/pLf7X+0/Bp+yf7Jezj/7rxZ+oV2f9VzLuOt/tmdAcwNG1/sfT9/ufLL8x/7f3Av47/O/9P+aHwgesD0RCQdAX6p4eJlarwOySdToxhtOa4dk+MfSKI4lrBrIW8YDeG+Eh1o6E4gYxHsgPSwKyRkT9Eqi+MpSTo+VrQLZTIemmoAA/v60Ir+dfP7rSZpGjKdPPz/9Mf9HblomL8tZw1PX/NfzxLw/6O420iuv/JhJke5EZ0E1Tt1xXQrzYf+MJQn+Ke/CxbaUPSh20HX+Y3liw64bs5NTkRNW6Dp80O+eLnOrbEfuiNP91ZRIJ6BZazTpBEEMyj//YOA/1eqcOOQcMye0rjigKyoThveRvEHjcP7mxqcv/0N51yO0pLX9KKDIh6ZT2rHpTmb8KCU0QU0HvQPdavxur2Mg9mD5T4dQXN4ryQ7em/KILpl9a/fomQEVTzlR2//Ox+p4CiQ7tt8ZOxS8wGMKFp7DMTmsVf6YZuDRo+KmeqMJxvYqX5+x7F8WAGzTYLPdF0JVqd8TbHlDb/s2eDDIuDe/8aTfx0bX4PvFZ/ZHvokEv/SbwyvEimu87tAPUMvlvETmaa27RtLQ4zYmH/joVn/wKDfhcZhTHMf3g9X2r8rsxggoOSouWj4Ro22vuKcHi3LIA0C1aWLgNSfKSar+fVvIf1K1+nOdwU/xhfVeu2BOUsiQTMH9ijzCdAX2AfON/8b9+F5qAR3/iAHfKaZpH9FN8Hj6ym/hrrsdFCQOuNR42BOqxlHx5OgjJ7lCsV+gOLw36pnwvNbyzhxDFO0P/25Qcer+dW4Qh8ncef/wTYyoDim+IA5vTi+BZnKBxmRQ2EC1AEJwyb11O3/9fdLU5JlhH2yHCWp+waHd+tkRsDCXsWW3R0mU7GeLUjYc2H//Xvq1thZFQl+QBd/+poSMH+iX60nbrte2MWmzTBy9ABxzvh1zk5JeBhpxQxT6mG+oSIBdVV/PwvMLNIrIN81j1EZ79jmS2df/qT+2X/6pY6i3OFP8wvkwzH3lRQXb+1ygJxmfy1ZxzR403xbfgo5urQMsBOvsP7mfmL/0F79/MPle+ESOuX3cijTuQOS5ZeLzgXCh+wCBq44FZ8t+6P/moYhE8T/81DEInbP/4+qR6+v/+PqkevgADcTFOXCPFKRxYnQ3ICekAA=='];
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
        . '<h1><span class="ath-greet" data-l="' . $lang . '" data-g="' . esc_attr(wp_json_encode([cc_L('Good morning', 'Buongiorno'), cc_L('Good afternoon', 'Buon pomeriggio'), cc_L('Good evening', 'Buonasera')])) . '">' . cc_t('Welcome') . '</span>, ' . esc_html($first) . '</h1>'
        . '<p class="ath-lede">' . cc_t('Everything for your coaching in one place. Train smarter. Ride faster.') . '</p>'
        . ($nrep ? '<div class="ath-chips"><span class="ath-chip"><b class="ath-n" data-n="' . $nrep . '">' . $nrep . '</b> ' . esc_html(cc_Ln($nrep, 'report in your folder', 'report nella tua cartella', 'reports in your folder', 'report nella tua cartella')) . '</span></div>' : '')
        . '<a class="ath-out" href="' . esc_url(wp_logout_url($url)) . '">' . cc_t('Log out') . '</a>' . apply_filters('cc_ath_hero_links', '', $coach) . '</div>'
        . '<div class="ath-hero-me">' . cc_ath_sig_photo() . '</div></header>';
    // Matteo 17 Nov: "Change my availability" / "Add or change my goals & events" open their own page (?my=availability|goals); the hub shows a short summary
    $sub = (!$coach && $view && isset($_GET['my'])) ? sanitize_key($_GET['my']) : '';
    if ($sub !== '' && ($sp = apply_filters('cc_ath_subpage', '', $sub, $view)) !== '')
        return $o . '<p class="ath-back"><a href="' . esc_url($url) . '">← ' . esc_html(cc_ath_w('back')) . '</a></p>' . $sp . '</div>' . cc_ath_js();
    if ($coach) {
        $list = get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'orderby' => 'title', 'order' => 'ASC', 'meta_key' => 'cc_user']);
        $o .= '<div class="ath-coach"><p><b>Coach view.</b> You see what every athlete sees. Choose an athlete to see their own reports, or add one in WordPress: Users &gt; Add New (role Subscriber).</p><p class="ath-list">';
        foreach ($list as $p) $o .= '<a href="' . esc_url(add_query_arg('view', $p->ID, $url)) . '"' . ($view === $p->ID ? ' aria-current="page"' : '') . '>' . esc_html($p->post_title)
            . cc_ath_flag_for($p->ID) . '</a>';
        $o .= ($list ? '</p>' : '<span>No athletes yet.</span></p>') . (($tl = apply_filters('cc_ath_coach_links', '')) !== '' ? '<div class="ath-coach-tools"><span class="ath-coach-tl">Your coach tools</span>' . $tl . '</div>' : '') . '</div>';
        // coach-only pages (e.g. ?board=availability, from availability.php); empty unless a module adds one
        $board = isset($_GET['board']) ? sanitize_key($_GET['board']) : '';
        if ($board !== '' && ($b = apply_filters('cc_ath_board', '', $board)) !== '') return $o . $b . '</div>' . cc_ath_js();
    }
    $hub = ($shared = cc_ath_shared_page($lang)) ? cc_ath_sections(cc_ath_dress(cc_ath_content($shared))) : ['', []];
    $nav = [['reports', cc_t('Your reports')]];
    foreach ($hub[1] as $s) $nav[] = $s;
    $nav = apply_filters('cc_ath_nav', $nav, $view, $coach);   // modules add their own sections (availability.php)
    $o .= '<nav class="ath-jump" aria-label="' . cc_t('Sections') . '">';
    foreach ($nav as $n) $o .= '<a href="#' . esc_attr($n[0]) . '">' . esc_html($n[1]) . '</a>';
    $o .= '</nav>';
    $o .= apply_filters('cc_ath_before_reports', '', $view, $coach);   // reports.php: "Your season" card, "N new reports"
    $rx = apply_filters('cc_ath_reports_html', '', $view, $coach);      // reports.php: reports sent from Matteo's PC tools
    $o .= '<section class="ath-s ath-mine" id="reports"><h2>' . cc_ath_icon('reports', 'ath-hic') . cc_t('Your reports') . '</h2>'
        . ($mineHtml !== '' || $rx !== '' ? $rx . ($mineHtml !== '' ? '<div class="ath-body">' . $mineHtml . '</div>' : '')
           : '<div class="ath-empty">' . cc_ath_icon('doc') . '<p>' . cc_t('Your first assessment, reviews and progress reports will appear here. I will let you know when there is something new.') . '</p></div>')
        . '</section>';
    $o .= apply_filters('cc_ath_after_reports', '', $view, $coach);
    $o .= $hub[0];
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
        'food' => '<path d="M12 7.5c-1.6-1.4-4.3-1.9-5.8-.2C4 9.8 5 15.4 7.9 19.2c1.3 1.6 2.7 1.9 4.1.9 1.4 1 2.8.7 4.1-.9 2.9-3.8 3.9-9.4 1.7-11.9-1.5-1.7-4.2-1.2-5.8.2z"/><path d="M12 7.5c0-2.2.9-4 3-4.5"/>',
        'chat' => '<path d="M20.5 11.5a8.5 8.5 0 0 1-12.4 7.6L3.5 20.5l1.4-4.4A8.5 8.5 0 1 1 20.5 11.5z"/><path d="M8.5 11.5h.01M12 11.5h.01M15.5 11.5h.01"/>',
        'people' => '<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6M15.5 14.6c2.8.2 5 2.2 5 5.4"/>',
        'bolt' => '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
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
        'logo-vekta' => 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHhtbG5zOnhsaW5rPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rIiB2aWV3Qm94PSItNCAwIDYwIDcxIj48aW1hZ2Ugd2lkdGg9IjI4MCIgaGVpZ2h0PSI3MSIgaHJlZj0iZGF0YTppbWFnZS93ZWJwO2Jhc2U2NCxVa2xHUm1ZSkFBQlhSVUpRVmxBNFdBb0FBQUFRQUFBQUZ3RUFSZ0FBUVV4UVNORUdBQUFCOEliOS8vbEcvdi9kTTlucFRMRlRqMjNiS0ZkanJHMVVZOXUyamJWdGU4ZTI3Wm5WSU4zZDluRWhyK2Y5K1h3OVUrUjl2SzlFeEFUQTVUWGk4L2w4Ti9kTzhDREkrSktvbXdZdEpENW84WFhRUW9JWERZTVd6WU1XemY2SDRaMDZ6bmw2aUEzZUtlT2NweFV2L0JRVGRZUU5JYUtPTHZ5RUVPRjJSZjJmMVdNYi9yajBVY3NneERaeG5CRjArRVNVRHdRWktvbjZjcEFoaTVESXd0MDZxaVdBMFV6Tnd0MWlxaWVBRjVpd3d0MG9hZ3FBZU9JNENuZjNVVWNCNEVWVlVzSEhRNFRuUlZVb3FRc0Ezemlsd2NKS3lRbk95YVZNcENZNEo3YldTUjcyMG8rNzl1MVovODZrSGhGMk5VNU1VSFlNOVV2cGtFcDA2cERnbkJLaFZ6ZDkrYmM3OXUxZC8vYTQyeDF1VFVsd1RHempGcml0ZnVqMTNibmpyMWFGamZWRi9hR0JUcUplVEQyMlh2Z2pRNzMydEJCeVBRQzhMSVpiYU5SYW15UDBCdzJBZHFLODZkcG5sUFQxcy9tNFNneDhTcFFoUm9qSkZVVXQ4ZVFRMXdHZ2w1aHVTdFhkS3ZvL0ZHK291dWphdlp4MHR5eUxlRVRMSStxZFVMYTdLWWFmdE9OWEllc0FpQlliVm92Wk1mWkFRMGJiNVNWKzAzcUtlRnd4UmN4L1lzTWdJUWNDd0RFTElzNkwyeGJNMHBCVEhXM0NweW9KMDlsR3dQa3RjWE9mZTdXRS9Ca0Fsb2w3SmNYOWkwK21weGw4NGNIMnNTcXZqa2p1aDJQU05OUHZpelNXU2d6U2lCWDFHMDVyeGQzdHJsMG4vZ1dBdThTOW9qazJYQlBUdWQ5bGh2bGh1SmJaajB3aFczVlVZd1RSMHVFSmNYdTVTNThKMlJSQW1GaXdYMnk0YU16L3V4WUFjTllHK2R0cmFMWktLblBuVkgvRFAxSTBmM2w1MVl2Zi84TkphMWVlRVhJc0FKeDNwYVhETU9IUGY3cDYxWnU3TEJQWldoa29iWVg4Wktnc01ZdXFMZXF4RGw5U0h6V0JjNDNWMUVVM0tnaTVCUUJDU3NjNFJwVW1xa1RGT01kNS9VS0ZIaDRPNTI3NzdSS1pCblMzUW1xWXdWN1ZOV29oRWUxWFhVaGZZN0NsVHhIeW9BdVhtU0orcEpjb0FjM0Z6S2VnbjdaTTl0K0NEQ3VHR0hwV0phMlpiTlVtK0w5Sy9CMEN6VDNFVVhPdkM5a09taUZFbEk2UUs2RFptTHZrbm1USDRua2I1aG9DOFFxUktPcjdIWVFzQlcyZlNxcVl1bGZJR2RBdFp1eFJZajIwdTFGN0xCQ0p4VzBXekRIMXJrcUl0d240ZHlRR1F6K0JHR01vUnNpOTBBNG5RalcrSUNMMDhEVXp3NHBySGtUdERwUjJSRStWcUY5MFdFUXNXYkJJZXhxeHdkQkpKbFF2ekppb1g0VEJXa3lFRmJJVndPTTVnWUcvVk44cUhpQWFPbXdsWERhelJNamJZVTFwb3FVSm5DWFEzUW9aQ2dEcDV3Tmlra3B1Y2ZwRmRRR08yYmFFbTdoRHlNV3c1eTRDUmhjemFISEJCb21DZjcyWmg4d3RNaFpIcERtRWlucW9rOWhhejBDb2tFZGgwZk9xSTJhZXBvRDZUNlduOFZtek51bDk3T0JmN2M0bjBreG10VE9HcmFxOUR2MklVSWN3YTVJTjdHV2liQnFoK3M1TWlvYlJJbU4wcElMSy9rZFZVc3J2aU9wSE9NWlowMUZ2aXBEZFlkTUUxWWRtV3JrSGhPelFXQnM0SU1ZREtDZnE3azdSMXR5bDFVcllENjBhcC9yWVRHc2JnQzg1Q2FCWFZWY0JURlBsd3RsalRUdU5VT1JROHFSTkExUy9tT2xrQjQ1d2R3Wk9jNVhVQi81VUxWT0FPSC8wbUp1WEsydmdWOUVzWmRIRHFrdG0rbGtTeHkwTEhGeFdMVWR6VWRkVW5WY05oUHZNQk5FOVkxRnpsWGlOdkcwSlZsTUhBbWlVU3JCT2RSenFUMVg3clRLNHpFQzRLUS9SeTBpT0xkVW9DYUJJb3NOL3FuN0VZSlZVQ2loSjBTdHVDcWRWbTB4MEYxdHdqU29ST1BoRmRWblVSWWlxeExlQkpVVzFRSlRRV0tDU05nWXUyZk1kVlN1QTdsR1JYNEE5cjVJSHRSb0thV3pLZjhRV0YrcHBOQ0o4ZWl2RW5wZXBaZ0VFQTNkU0F3aTVTNk82a0MrYVdvOHVoQXpUT3FrYXBJSFRLam5wMFpncUZyMllWNnpTK2djOEk3T3BER0hMbWdMd0NpRTFkRDVSWmVzOFJFaDJDaFB4bzlqMFVsNVJUMnV1eGdCR1pHWXpqMStkRVg4SSt4b010UVNBSzhRMW5SRXErYXVUWDZrSFAzREFHVUxrd0hQbC9jSTd2aTJhK1FYTzZGVFN3Q25LLzIvUjloaWFEUCtxaEx5dlVZc1FrV3U1SWlKT2pTai9mMitJd1h4am9NWis2SmJTMGsrRW1WMXc3ay9JZ3h6T1VNNjFIREJaeDJ5K0VhcnhnaFlTWGVvTFF5RUtyQ2NrbXJ2ZndDTk8rTExnZ0c4NEdMemRsWUV3bEF4MUVlWTRoNzE2OHhUNHF1RFFtWHJmQkdyN3pIV0ZvWVZna3dtWng0WHIvYXJDN0FJRGNwaEVJOENMaGpaSHdkQVI4RXNKYVUraGxFOG5oMERidjQyY2V5QWZXa2pjaE9rSzd4dllrd0tlS3FHQk00UVVwWUIzTkNTU0FES3U2UTFDYzlXVi9LUGErY1BPcDRZWUE0cGwva3dkbmxvVnVpSG5EanVmNlE3ZGNtY1BLMCs5cUlHYXIrY1NwMFo0S1NEbGxiK1k3eDhFMFBqOFljY2pHL01QZXl0MWZHSEkrQkZaOXpSQUhscTFaKy9SNDRjOGt4QUtrMUZKVHc4YU55S3JadzFZbmg4VmxJTVhxNElXbVVHTGtLQUZoZ1l0TURkb2dRWnZuc3YyK1h3K2FWcklBZ0JXVURnZ2JnSUFBQkFXQUowQktoZ0JSd0ErTVJpTFE2SWhvUkpkakpBZ0F3U3l0M0M2MzBBRitDZkFQd2QyYVBpdjR5YzVscS80QXliUGtDK28va0IvTy9jQi9GdnlNN0FEOURQOE4rVFBBQS9TbiszZngzM29QNEIvQU9zQS9UbjBBUFlBOUFEK0FmeHowWmY4UC9BUGdPL1lqOXh2Y1cvbG4vREFjbmxpV0RRTWJWQ0pOaVVoTW13NFNsUk81TDg2WlV6bkw5OXp5cENBQWtmTXFtOE1ZelBMeDc4dEMyVldXVkpOUkpScVMya0prMkpTRWxuQ2p4UXp4UXRsVmxrQUFQNy80TDBuWHZYLy94QTJsZWpKaVR0OFREYjQ4NmpDYXNSRFNLZm5EcGlIeWVyZXJvK2hzdmJQejlGQXpOVFVndFEwdU5lR0J5ckdwbndyTFNYLzhzUlE5cGdBVHpwdXYrZUswUm9BUUdLelAvLzhDM0NleXY5a1g5cE9WNGRFNTgxNktQdDhXaDI2dUlreEtXb2dDenJDVk5nQjJQNFR4OUN0ZjNrWUxpOXlZUTcvL3hqR0tQd0hwVW1yNGp3blB0NlJYRjllczNRdFlubFBWVWdiVHJNM09mRHA4VWk4SGR0WjBsZW9DUWU1RUtXWXJlblVFWUsvTm44QVpIL1R2TnJlNDROSXUwYWg2dEthc2xLWTdlUjd4eXEvVDZmVlRxVlhvdG5RWkRaWjg5QXNUVlQvbE1vNC9CRVhKc0JkTXdoU2lsUFFrYWZPcmVsVXZKd2FmZEZVSE9TYnhreFFpVHZVOTNVZjZJL1NOT1JOWUVVUWQrU1dDMFhtVlZZQWFlNDBXczNLd1dDQTM3YjkrSHp0OWNTNm9RMVZWTUJHRFFEeEpGaFVaUmMraGJ5dHIyOTZJZUFWaFRPR0QzL2ZLL0pUMVliY09LbjhWYjF2Ly92SHZHWHUza1hGRWZCRW1ZcEhXWGlVWXd4NUlrL2VITVp4OFczUUhMY2VnckN2MSt0RFlJck5hRG5GVE12MTVoZGVQWUdrVGYvN0NnWmlBd3lzdkpnMUpURGdCM3QzejR3bHIyK05rS2wydUUwQjY2cEFBQUE9IiB4bGluazpocmVmPSJkYXRhOmltYWdlL3dlYnA7YmFzZTY0LFVrbEdSbVlKQUFCWFJVSlFWbEE0V0FvQUFBQVFBQUFBRndFQVJnQUFRVXhRU05FR0FBQUI4SWI5Ly9sRy92L2RNOW5wVExGVGoyM2JLRmRqckcxVVk5dTJqYlZ0ZThlMjdablZJTjNkOW5FaHIrZjkrWHc5VStSOXZLOUV4QVRBNVRYaTgvbDhOL2RPOENESStKS29td1l0SkQ1bzhYWFFRb0lYRFlNV3pZTVd6ZjZINFowNnpubDZpQTNlS2VPY3B4VXYvQlFUZFlRTklhS09MdnlFRU9GMlJmMmYxV01iL3JqMFVjc2d4RFp4bkJGMCtFU1VEd1FaS29uNmNwQWhpNURJd3QwNnFpV0EwVXpOd3QxaXFpZUFGNWl3d3Qwb2FncUFlT0k0Q25mM1VVY0I0RVZWVXNISFE0VG5SVlVvcVFzQTN6aWx3Y0pLeVFuT3lhVk1wQ1k0SjdiV1NSNzIwbys3OXUxWi84NmtIaEYyTlU1TVVIWU05VXZwa0VwMDZwRGduQktoVnpkOStiYzc5dTFkLy9hNDJ4MXVUVWx3VEd6akZyaXRmdWoxM2JuanIxYUZqZlZGL2FHQlRxSmVURDIyWHZnalE3MzJ0QkJ5UFFDOExJWmJhTlJhbXlQMEJ3MkFkcUs4NmRwbmxQVDFzL200U2d4OFNwUWhSb2pKRlVVdDhlUVExd0dnbDVodVN0WGRLdm8vRkcrb3V1amF2WngwdHl5TGVFVExJK3FkVUxhN0tZYWZ0T05YSWVzQWlCWWJWb3ZaTWZaQVEwYmI1U1YrMDNxS2VGd3hSY3gvWXNNZ0lRY0N3REVMSXM2TDJ4Yk0wcEJUSFczQ3B5b0owOWxHd1BrdGNYT2ZlN1dFL0JrQWxvbDdKY1g5aTArbXB4bDg0Y0gyc1NxdmpranVoMlBTTk5Qdml6U1dTZ3pTaUJYMUcwNXJ4ZDN0cmwwbi9nV0F1OFM5b2prMlhCUFR1ZDlsaHZsaHVKYlpqMHdoVzNWVVl3VFIwdUVKY1h1NVM1OEoyUlJBbUZpd1gyeTRhTXovdXhZQWNOWUcrZHRyYUxaS0tuUG5WSC9EUDFJMGYzbDUxWXZmLzhOSmExZWVFWElzQUp4M3BhWERNT0hQZjdwNjFadTdMQlBaV2hrb2JZWDhaS2dzTVl1cUxlcXhEbDlTSHpXQmM0M1YxRVUzS2dpNUJRQkNTc2M0UnBVbXFrVEZPTWQ1L1VLRkhoNE81Mjc3N1JLWkJuUzNRbXFZd1Y3Vk5Xb2hFZTFYWFVoZlk3Q2xUeEh5b0F1WG1TSitwSmNvQWMzRnpLZWduN1pNOXQrQ0RDdUdHSHBXSmEyWmJOVW0rTDlLL0IwQ3pUM0VVWE92QzlrT21pRkVsSTZRSzZEWm1MdmtubVRING5rYjVob0M4UXFSS09yN0hZUXNCVzJmU3FxWXVsZklHZEF0WnV4UllqMjB1MUY3TEJDSnhXMFd6REgxcmtxSXR3bjRkeVFHUXorQkdHTW9Sc2k5MEE0blFqVytJQ0wwOERVenc0cHJIa1R0RHBSMlJFK1ZxRjkwV0VRc1diQklleHF4d2RCSkpsUXZ6SmlvWDRUQldreUVGYklWd09NNWdZRy9WTjhxSGlBYU9td2xYRGF6Uk1qYllVMXBvcVVKbkNYUTNRb1pDZ0RwNXdOaWtrcHVjZnBGZFFHTzJiYUVtN2hEeU1XdzV5NENSaGN6YUhIQkJvbUNmNzJaaDh3dE1oWkhwRG1FaW5xb2s5aGF6MENva0VkaDBmT3FJMmFlcG9ENlQ2V244Vm16TnVsOTdPQmY3YzRuMGt4bXRUT0dyYXE5RHYySVVJY3dhNUlON0dXaWJCcWgrczVNaW9iUkltTjBwSUxLL2tkVlVzcnZpT3BIT01aWjAxRnZpcERkWWRNRTFZZG1XcmtIaE96UVdCczRJTVlES0NmcTdrN1IxdHlsMVVyWUQ2MGFwL3JZVEdzYmdDODVDYUJYVlZjQlRGUGx3dGxqVFR1TlVPUlE4cVJOQTFTL21PbGtCNDV3ZHdaT2M1WFVCLzVVTFZPQU9ILzBtSnVYSzJ2Z1Y5RXNaZEhEcWt0bStsa1N4eTBMSEZ4V0xVZHpVZGRVblZjTmhQdk1CTkU5WTFGemxYaU52RzBKVmxNSEFtaVVTckJPZFJ6cVQxWDdyVEs0ekVDNEtRL1J5MGlPTGRVb0NhQklvc04vcW43RVlKVlVDaWhKMFN0dUNxZFZtMHgwRjF0d2pTb1JPUGhGZFZuVVJZaXF4TGVCSlVXMVFKVFFXS0NTTmdZdTJmTWRWU3VBN2xHUlg0QTlyNUlIdFJvS2FXektmOFFXRitwcE5DSjhlaXZFbnBlcFpnRUVBM2RTQXdpNVM2TzZrQythV284dWhBelRPcWthcElIVEtqbnAwWmdxRnIyWVY2elMrZ2M4STdPcERHSExtZ0x3Q2lFMWRENVJaZXM4UkVoMkNoUHhvOWowVWw1UlQydXV4Z0JHWkdZemoxK2RFWDhJK3hvTXRRU0FLOFExblJFcSthdVRYNmtIUDNEQUdVTGt3SFBsL2NJN3ZpMmErUVhPNkZUU3dDbksvMi9SOWhpYURQK3FoTHl2VVlzUWtXdTVJaUpPalNqL2YyK0l3WHhqb01aKzZKYlMwaytFbVYxdzdrL0lneHpPVU02MUhEQlp4MnkrRWFyeGdoWVNYZW9MUXlFS3JDY2ttcnZmd0NOTytMTGdnRzg0R0x6ZGxZRXdsQXgxRWVZNGg3MTY4eFQ0cXVEUW1YcmZCR3I3ekhXRm9ZVmdrd21aeDRYci9hckM3QUlEY3BoRUk4Q0xoalpId2RBUjhFc0phVStobEU4bmgwRGJ2NDJjZXlBZldramNoT2tLN3h2WWt3S2VLcUdCTTRRVXBZQjNOQ1NTQURLdTZRMUNjOVdWL0tQYStjUE9wNFlZQTRwbC9rd2RubG9WdWlIbkRqdWY2UTdkY21jUEswKzlxSUdhcitjU3AwWjRLU0RsbGIrWTd4OEUwUGo4WWNjakcvTVBleXQxZkdISStCRlo5elJBSGxxMVorL1I0NGM4a3hBS2sxRkpUdzhhTnlLclp3MVluaDhWbElNWHE0SVdtVUdMa0tBRmhnWXRNRGRvZ1Fadm5zdjIrWHcrYVZySUFnQldVRGdnYmdJQUFCQVdBSjBCS2hnQlJ3QStNUmlMUTZJaG9SSmRqSkFnQXdTeXQzQzYzMEFGK0NmQVB3ZDJhUGl2NHljNWxxLzRBeWJQa0Mrby9rQi9PL2NCL0Z2eU03QUQ5RFA4TitUUEFBL1NuKzNmeDMzb1A0Qi9BT3NBL1RuMEFQWUE5QUQrQWZ4ejBaZjhQL0FQZ08vWWo5eHZjVy9sbi9EQWNubGlXRFFNYlZDSk5pVWhNbXc0U2xSTzVMODZaVXpuTDk5enlwQ0FBa2ZNcW04TVl6UEx4Nzh0QzJWV1dWSk5SSlJxUzJrSmsySlNFbG5DanhRenhRdGxWbGtBQVA3LzRMMG5YdlgvL3hBMmxlakppVHQ4VERiNDg2akNhc1JEU0tmbkRwaUh5ZXJlcm8raHN2YlB6OUZBek5UVWd0UTB1TmVHQnlyR3Bud3JMU1gvOHNSUTlwZ0FUenB1ditlSzBSb0FRR0t6UC8vOEMzQ2V5djlrWDlwT1Y0ZEU1ODE2S1B0OFdoMjZ1SWt4S1dvZ0N6ckNWTmdCMlA0VHg5Q3RmM2tZTGk5eVlRNy8veGpHS1B3SHBVbXI0anduUHQ2UlhGOWVzM1F0WW5sUFZVZ2JUck0zT2ZEcDhVaThIZHRaMGxlb0NRZTVFS1dZcmVuVUVZSy9ObjhBWkgvVHZOcmU0NE5JdTBhaDZ0S2FzbEtZN2VSN3h5cS9UNmZWVHFWWG90blFaRFpaODlBc1RWVC9sTW80L0JFWEpzQmRNd2hTaWxQUWthZk9yZWxVdkp3YWZkRlVIT1NieGt4UWlUdlU5M1VmNkkvU05PUk5ZRVVRZCtTV0MwWG1WVllBYWU0MFdzM0t3V0NBMzdiOStIenQ5Y1M2b1ExVlZNQkdEUUR4SkZoVVpSYytoYnl0cjI5NkllQVZoVE9HRDMvZksvSlQxWWJjT0tuOFZiMXYvL3ZIdkdYdTNrWEZFZkJFbVlwSFdYaVVZd3g1SWsvZUhNWng4VzNRSExjZWdyQ3YxK3REWUlyTmFEbkZUTXYxNWhkZVBZR2tUZi83Q2daaUF3eXN2SmcxSlREZ0IzdDN6NHdscjIrTmtLbDJ1RTBCNjZwQUFBQT0iLz48L3N2Zz4=',
        'logo-whatsapp' => 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAzMiAzMiI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTE2IDNDOC44IDMgMyA4LjcgMyAxNS44YzAgMi41LjcgNC45IDIgN0wzIDI5bDYuNC0yYzIgMS4xIDQuMyAxLjcgNi42IDEuNyA3LjIgMCAxMy01LjcgMTMtMTIuOFMyMy4yIDMgMTYgM3ptMCAyMy40Yy0yLjEgMC00LjEtLjYtNS45LTEuN2wtLjQtLjMtMy44IDEuMiAxLjItMy43LS4zLS40QzUuNiAxOS44IDUgMTcuOCA1IDE1LjggNSA5LjkgOS45IDUuMiAxNiA1LjJzMTEgNC43IDExIDEwLjYtNC45IDEwLjYtMTEgMTAuNnoiLz48cGF0aCBmaWxsPSIjZmZmIiBkPSJNMjIuMSAxOC42Yy0uMy0uMi0yLTEtMi4zLTEuMS0uMy0uMS0uNS0uMi0uNy4yLS4yLjMtLjggMS0xIDEuMi0uMi4yLS40LjItLjcuMS0uMy0uMi0xLjQtLjUtMi43LTEuNi0xLS45LTEuNy0yLTEuOS0yLjMtLjItLjMgMC0uNS4xLS43bC41LS42Yy4yLS4yLjItLjMuMy0uNi4xLS4yIDAtLjQgMC0uNmwtMS0yLjRjLS4zLS42LS41LS41LS43LS41aC0uNmMtLjIgMC0uNi4xLS45LjQtLjMuMy0xLjIgMS4xLTEuMiAyLjhzMS4yIDMuMiAxLjQgMy41Yy4yLjIgMi40IDMuNiA1LjggNSAuOC4zIDEuNC41IDEuOS43LjguMyAxLjYuMiAyLjIuMS43LS4xIDItLjggMi4zLTEuNi4zLS44LjMtMS41LjItMS42LS4xLS4yLS4zLS4zLS42LS40eiIvPjwvc3ZnPg==',
        'logo-vivify' => 'data:image/png;base64,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',
    ];
    if (isset($LOGO[$k])) return '<span class="' . $cls . ' ath-logo ' . $k . '" aria-hidden="true" style="background-image:url(' . $LOGO[$k] . ')"></span>';
    return '<span class="' . $cls . '" aria-hidden="true"><svg viewBox="0 0 24 24">' . ($I[$k] ?? $I['link']) . '</svg></span>';
}
// what a link is, from where it goes: [icon, line under the title]; Matteo can edit the hub freely and the cards follow
function cc_ath_kind($href) {
    $m = [['cal.com/', 'calendar', 'Pick a time that suits you'], ['calendly.com', 'calendar', 'Pick a time that suits you'], ['vivifysports', 'logo-vivify', 'Your one-off consult with Marine Lenehan, sports nutritionist'],
          ['wa.me', 'logo-whatsapp', 'I usually reply within a few hours'], ['skool.com', 'people', 'Free for coaching clients'],
          ['vekta', 'logo-vekta', 'Your plan, workouts and analysis'], ['trainingpeaks', 'peaks', 'Your plan and workouts'],
          ['training-zones', 'zones', ''], ['carbs-per-hour', 'carbs', ''], ['critical-power', 'cp', ''], ['ftp-test', 'ftp', ''],
          ['sweat-rate', 'sweat', ''], ['climb-time', 'climb', ''], ['gear-speed', 'gear', ''], ['swim-pace', 'swim', ''], ['.pdf', 'doc', ''],
          ['youtube.com/playlist', 'play', 'YouTube'], ['instagram.com/reel/', 'play', 'Instagram'], ['instagram.com', 'insta', '@cigalacycling']];
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
function cc_ath_sig_photo() {
    $u = content_url('/uploads/2026/11/');
    return '<span class="sigph"><img src="' . esc_url($u . 'cigala-coaching-about-hero-matteo-photo.webp') . '" alt="' . esc_attr(cc_t('Matteo Cigala, your coach, in the white Cigala Cycling jersey')) . '" width="720" height="933">'
         . '<img class="signature" src="' . esc_url($u . 'cigala-coaching-matteo-cigala-signature.webp') . '" alt="" aria-hidden="true" width="720" height="933"><span class="sig-anchor" aria-hidden="true"></span></span>';
}
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
       . ($bye === false ? '' : '<p style="margin:0">' . $bye . '<br><strong>Matteo</strong></p>') . '</td></tr>'
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
function cc_ath_mail_small($html) { return '<p style="margin:22px 0 10px;font-size:14px;color:#454a52">' . $html . '</p>'; }
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
    $h = cc_ath_mail_shell($T['hi'], $T['p1'], $T['btn'], $link, '<p style="margin:22px 0 10px;font-size:14px;color:#454a52">' . $T['p2'] . '</p><p style="margin:0 0 22px;font-size:14px;color:#454a52">' . $T['p3'] . '</p>', $T['bye'], $T['eb']);
    if ($dry) return ['to' => $to ?: $u->user_email, 'subject' => $T['subj'], 'link' => $link, 'html' => $h];
    $ok = wp_mail($to ?: $u->user_email, $T['subj'], $h, ['Content-Type: text/html; charset=UTF-8', 'From: Matteo Cigala <noreply@cigalacycling.com>', 'Reply-To: Matteo Cigala <matteo@cigalacycling.com>']);
    if ($ok && !$to) update_user_meta($u->ID, 'cc_welcome_sent', current_time('mysql'));
    return $ok ? ['sent' => true, 'to' => $to ?: $u->user_email] : new WP_Error('mail', 'wp_mail failed');
}
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
html .cc .ath-hero { position: relative; display: grid; grid-template-columns: 1fr 250px; align-items: end; gap: 24px; padding: 34px 36px 0; margin: 0 0 18px; border-radius: 20px; overflow: hidden;
  background: radial-gradient(120% 140% at 100% 100%, rgba(18,161,80,.28), transparent 55%), radial-gradient(90% 120% at 0% 0%, rgba(255,61,51,.14), transparent 60%), rgba(12,14,16,.92); border: 1px solid rgba(43,212,122,.3); box-shadow: 0 30px 80px rgba(0,0,0,.45); }
html .cc .ath-hero-txt { padding-bottom: 34px; min-width: 0; }
html .cc .ath-hero h1 { font-size: clamp(36px, 6.4vw, 66px); line-height: 1; margin: 8px 0 12px; }
html .cc h1 .ath-greet { color: var(--green-text, #2bd47a); font-family: var(--head); }
html .cc .ath-lede { color: var(--text-2); font-size: 16px; margin: 0 0 18px; max-width: 520px; }
html .cc .ath-chips { display: flex; flex-wrap: wrap; gap: 10px; margin: 0 0 18px; }
html .cc .ath-chip { display: inline-flex; align-items: baseline; gap: 8px; padding: 9px 14px; border-radius: 999px; background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.12); color: var(--text-2); font-size: 13.5px; }
html .cc .ath-chip b { font-family: var(--head); font-weight: 400; font-size: 22px; line-height: 1; color: #fff; }
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
html .cc .ath-flag-e { display: inline-grid; place-items: center; width: 14px; height: 14px; border-radius: 50%; overflow: hidden; box-shadow: 0 0 0 1px rgba(255,255,255,.35), 0 1px 4px rgba(0,0,0,.4); flex: none; }
html .cc .ath-flag-e span { font-size: 20px; line-height: 1; }
html .cc .ath form.ath-lang { display: inline-flex; align-items: center; gap: 8px; margin: 0 0 0 14px; vertical-align: middle; }
html .cc .ath-lang label { font-size: 13px; color: var(--text-3); margin: 0; }
html .cc .ath-lang select { font-size: 16px; padding: 6px 30px 6px 10px; min-height: 40px; width: auto; border-radius: 8px; margin: 0; }
html .cc img.ath-flag { width: 14px; height: 14px; aspect-ratio: 1 / 1; object-fit: cover; border-radius: 50%; box-shadow: 0 0 0 1px rgba(255,255,255,.35), 0 1px 4px rgba(0,0,0,.4); margin: 0; flex: none; }
html .cc .ath-coach-tools { display: flex; flex-wrap: wrap; align-items: center; gap: 8px; margin: 14px 0 0; padding-top: 14px; border-top: 1px solid rgba(255,255,255,.1); }
html .cc .ath-coach-tl { flex-basis: 100%; font-size: 11px; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--red-text, #ff3d33); }
html .cc .ath-coach-tools .av-boardlink { display: inline-flex; align-items: center; gap: 8px; margin: 0; padding: 9px 14px; border-radius: 999px; border: 1px solid rgba(255,255,255,.16); background: rgba(255,255,255,.05); color: #fff; font-size: 13.5px; font-weight: 600; text-decoration: none; }
html .cc .ath-coach-tools .av-boardlink:hover { border-color: #009a44; }
html .cc .ath-allposts { margin: 4px 0 18px; font-size: 14px; } html .cc .ath-allposts a { color: var(--green-text, #34c46a); }
html .cc .ath-jump { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 18px; padding: 2px; }   /* Matteo 17 Nov: the last pill ("Worth reading") ran off the right edge; the pills now wrap */
html .cc .ath-jump::-webkit-scrollbar { display: none; }
html .cc .ath-jump a { flex: none; padding: 9px 15px; border-radius: 999px; border: 1px solid rgba(255,255,255,.14); background: rgba(12,14,16,.85); color: var(--text-2); font-size: 13px; font-weight: 600; text-decoration: none; transition: border-color .2s, color .2s; }
html .cc .ath-jump a:hover { border-color: #12a150; color: #fff; }
html .cc .ath-s { padding: 28px 28px 30px; border-radius: 18px; background: rgba(13,15,17,.9); border: 1px solid rgba(255,255,255,.09); margin: 0 0 18px; scroll-margin-top: 100px; }
html .cc .ath-s.ath-mine { border-color: rgba(43,212,122,.4); background: linear-gradient(180deg, rgba(18,161,80,.1), rgba(13,15,17,.9) 60%); }
html .cc .ath-s > h2 { display: flex; align-items: center; gap: 12px; font-size: clamp(24px, 3.6vw, 30px); margin: 0 0 18px; }
html .cc .ath-hic { flex: none; display: grid; place-items: center; width: 40px; height: 40px; border-radius: 12px; background: rgba(18,161,80,.15); border: 1px solid rgba(43,212,122,.35); }
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
html .cc .ath-ic.ath-logo { background-repeat: no-repeat; background-position: center; background-size: 62%; }
html .cc .ath-ic.logo-whatsapp { background-color: #25D366; border-color: #25D366; background-size: 60%; }
html .cc .ath-ic.logo-vekta { background-color: #111; border-color: rgba(255,255,255,.25); background-size: 64%; }
html .cc .ath-ic.logo-vivify { background-color: #111; border-color: rgba(255,255,255,.25); background-size: 70%; }
/* Matteo 17 Nov: availability and goals summaries in the hub, each with a button to its own page */
html .cc .av-sumbox { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 14px; padding: 16px; border-radius: 14px; background: rgba(255,255,255,.04); border: 1px solid rgba(255,255,255,.1); }
html .cc .av-sumt { margin: 0; flex: 1 1 260px; min-width: 0; } html .cc .av-sumt p { margin: 0 0 6px; }
html .cc .av-sumt small { display: block; color: var(--text-3); font-size: 13px; margin-top: 4px; }
html .cc .av-sumbox .btn { margin: 0; max-width: 100%; white-space: normal; height: auto; text-align: center; }
html .cc .gl-sumev { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
html .cc .gl-prio { display: inline-grid; place-items: center; width: 22px; height: 22px; border-radius: 50%; font: 700 12px/1 var(--body); color: #1a1a1a; flex: none; }
html .cc .gl-prio-a { background: linear-gradient(135deg, #F3D774, #D4AF37 55%, #A8841F); } html .cc .gl-prio-b { background: linear-gradient(135deg, #F2F3F5, #C0C4CC 55%, #8E939C); } html .cc .gl-prio-c { background: linear-gradient(135deg, #E9A86B, #CD7F32 55%, #9A5A1F); }
html .cc .ath-back { margin: 18px 0 0; } html .cc .ath-back a { color: var(--text-2, #cfd3d8); text-decoration: none; font-weight: 600; } html .cc .ath-back a:hover { color: #fff; }
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
  html .cc .ath-hero { grid-template-columns: 1fr 104px; gap: 8px; padding: 24px 16px 0; }
  html .cc .ath-hero h1 { font-size: clamp(32px, 10vw, 44px); }
  html .cc .ath-hero-txt { padding-bottom: 22px; }
  html .cc .ath-lede { font-size: 14.5px; }
  html .cc .ath-chips { gap: 8px; }
  html .cc .ath-chip { padding: 7px 11px; font-size: 12.5px; gap: 6px; }
  html .cc .ath-chip b { font-size: 18px; }
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
    $ic = function ($s) { return function_exists('get_site_icon_url') ? get_site_icon_url($s) : ''; };
    $icons = []; foreach ([192, 512] as $s) if ($u = $ic($s)) $icons[] = ['src' => $u, 'sizes' => $s . 'x' . $s, 'type' => 'image/png', 'purpose' => 'any'];
    header('Content-Type: application/manifest+json; charset=utf-8'); header('Cache-Control: public, max-age=86400');
    echo wp_json_encode(['name' => 'Cigala Cycling Coaching: athlete hub', 'short_name' => 'Cigala Hub', 'start_url' => '/' . CC_ATH_SLUG . '/?source=app', 'scope' => '/' . CC_ATH_SLUG . '/',
        'display' => 'standalone', 'background_color' => '#08090a', 'theme_color' => '#08090a', 'icons' => $icons], JSON_UNESCAPED_SLASHES);
    exit;
});
add_action('wp_head', function () {
    if (!is_page(CC_ATH_SLUG)) return;
    echo '<link rel="manifest" href="' . esc_url(add_query_arg('cc_manifest', 1, home_url('/'))) . '"><meta name="apple-mobile-web-app-title" content="Cigala Hub"><meta name="mobile-web-app-capable" content="yes">'
       . '<meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-status-bar-style" content="black"><meta name="theme-color" content="#08090a">' . "\n";
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
        . 'var ios=/iphone|ipad|ipod/i.test(navigator.userAgent);if(ios){b.querySelector(".a2hs-ios").hidden=false;b.hidden=false;}'
        . 'addEventListener("beforeinstallprompt",function(e){e.preventDefault();ev=e;b.querySelector(".a2hs-go").hidden=false;b.hidden=false;});'
        . 'b.querySelector(".a2hs-go").addEventListener("click",function(){if(ev){ev.prompt();ev.userChoice.then(function(){b.hidden=true;});}});'
        . 'b.querySelector(".a2hs-no").addEventListener("click",function(){try{localStorage.setItem(k,"1")}catch(e){}b.hidden=true;});})();</script>'
        . '<style>html .cc .ath-a2hs{display:flex;flex-wrap:wrap;align-items:center;gap:10px 14px;margin:0 0 14px;padding:12px 16px;border-radius:12px;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.04)}'
        . 'html .cc .ath-a2hs[hidden],html .cc .ath-a2hs [hidden]{display:none!important}html .cc .ath-a2hs .a2hs-ios{display:block}html .cc .ath-a2hs p{margin:0;flex:1 1 220px;font-size:14px;color:var(--text-2)}html .cc .ath-a2hs b{display:block;color:#fff}html .cc .ath-a2hs .btn{width:auto;margin:0}</style>' . $html;
}, 5, 3);
