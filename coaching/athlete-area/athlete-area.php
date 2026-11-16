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
function cc_ath_shared_page() {
    $q = get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'meta_key' => 'cc_shared', 'meta_value' => '1', 'numberposts' => 1, 'fields' => 'ids']);
    return $q ? (int) $q[0] : 0;
}
function cc_ath_is_coach() { return current_user_can('edit_pages'); }
function cc_ath_can_see($pid) {
    if (!$pid || get_post_type($pid) !== 'cc_athlete' || !is_user_logged_in()) return false;
    if (cc_ath_is_coach()) return true;
    $me = get_current_user_id();
    if (get_post_meta($pid, 'cc_shared', true)) return (bool) cc_ath_page_of($me);
    return (int) get_post_meta($pid, 'cc_user', true) === $me;
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
    echo $u ? esc_html($u->user_login . ' (' . $u->user_email . ')') : '—';
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

/* ---------- logins: athletes never see wp-admin and stay logged in for a year ---------- */
add_filter('show_admin_bar', function ($s) { return current_user_can('edit_posts') ? $s : false; });
add_action('admin_init', function () {
    if (!current_user_can('edit_posts') && !wp_doing_ajax() && is_user_logged_in()) { wp_safe_redirect(home_url('/' . CC_ATH_SLUG . '/')); exit; }
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
        $next = isset($_GET['next']) ? add_query_arg('cc_file', (int) $_GET['next'], $url) : $url;
        $o .= '<div class="ath-login"><p class="eyebrow">Coached athletes</p><h1>Athlete login</h1>'
            . '<p class="ath-lede">Your training guides, links and your own reports, all in one place.</p>';
        if (isset($_GET['login'])) $o .= '<p class="ath-err" role="alert">That username or password is not right. Try again, or message me and I will reset it.</p>';
        $o .= '<form method="post" action="' . esc_url(site_url('wp-login.php', 'login_post')) . '">'
            . '<label for="ath-u">Username or email</label><input id="ath-u" name="log" type="text" autocomplete="username" autocapitalize="none" required>'
            . '<label for="ath-p">Password</label><input id="ath-p" name="pwd" type="password" autocomplete="current-password" required>'
            . '<label class="ath-rem"><input name="rememberme" type="checkbox" value="forever" checked> Keep me logged in</label>'
            . '<input type="hidden" name="redirect_to" value="' . esc_url($next) . '">'
            . '<button type="submit" class="btn btn-go">Log in</button></form>'
            . '<p class="ath-help">Forgot your password? <a href="https://wa.me/message/WVBRO6XAMQMCH1" target="_blank" rel="noopener">WhatsApp me</a> or <a href="mailto:info@cigalacycling.com">email me</a> and I will send you a new one.</p>'
            . '<p class="ath-help">Not coached yet? <a href="' . esc_url(home_url('/individual-packages/')) . '">See the coaching packages</a>.</p></div>';
        return $o . '</div>';
    }
    $me = wp_get_current_user(); $mine = cc_ath_page_of($me->ID); $coach = cc_ath_is_coach();
    if (!$mine && !$coach) {
        return $o . '<h1>Athlete area</h1><p>This area is for athletes I coach. If you are one of them, message me and I will set up your login.</p>'
             . '<p><a class="btn btn-ghost" href="' . esc_url(wp_logout_url($url)) . '">Log out</a></p></div>';
    }
    $view = $mine;
    if ($coach && isset($_GET['view']) && get_post_type((int) $_GET['view']) === 'cc_athlete') $view = (int) $_GET['view'];
    $first = $me->first_name ?: $me->display_name;
    // personal numbers: days since the login was made, and reports in their page
    $vu = $view ? get_userdata((int) get_post_meta($view, 'cc_user', true)) : null;
    $since = $vu ? $vu->user_registered : $me->user_registered;
    $days = max(1, (int) floor((time() - strtotime($since . ' UTC')) / DAY_IN_SECONDS) + 1);
    $mineHtml = $view ? cc_ath_dress(trim(cc_ath_content($view))) : '';
    $nrep = substr_count($mineHtml, 'class="ath-file"');
    $o .= '<header class="ath-hero"><div class="ath-hero-txt"><p class="eyebrow">Athlete area' . ($coach ? ' · coach view' : '') . '</p>'
        . '<h1><span class="ath-greet">Welcome</span>, ' . esc_html($first) . '</h1>'
        . '<p class="ath-lede">Everything for your coaching in one place. Train smarter. Ride faster.</p>'
        . '<div class="ath-chips"><span class="ath-chip"><b class="ath-n" data-n="' . $days . '">' . $days . '</b> ' . ($days === 1 ? 'day' : 'days') . ' with Cigala Cycling</span>'
        . '<span class="ath-chip"><b class="ath-n" data-n="' . $nrep . '">' . $nrep . '</b> ' . ($nrep === 1 ? 'report' : 'reports') . ' in your folder</span></div>'
        . '<a class="ath-out" href="' . esc_url(wp_logout_url($url)) . '">Log out</a></div>'
        . '<div class="ath-hero-me">' . cc_ath_sig_photo() . '</div></header>';
    if ($coach) {
        $list = get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'orderby' => 'title', 'order' => 'ASC', 'meta_key' => 'cc_user']);
        $o .= '<div class="ath-coach"><p><b>Coach view.</b> You see what every athlete sees. Choose an athlete to see their own reports, or add one in WordPress: Users &gt; Add New (role Subscriber).</p><p class="ath-list">';
        foreach ($list as $p) $o .= '<a href="' . esc_url(add_query_arg('view', $p->ID, $url)) . '"' . ($view === $p->ID ? ' aria-current="page"' : '') . '>' . esc_html($p->post_title) . '</a>';
        $o .= $list ? '</p></div>' : '<span>No athletes yet.</span></p></div>';
    }
    $hub = ($shared = cc_ath_shared_page()) ? cc_ath_sections(cc_ath_dress(cc_ath_content($shared))) : ['', []];
    $nav = [['reports', 'Your reports']];
    foreach ($hub[1] as $s) $nav[] = $s;
    $o .= '<nav class="ath-jump" aria-label="Sections">';
    foreach ($nav as $n) $o .= '<a href="#' . esc_attr($n[0]) . '">' . esc_html($n[1]) . '</a>';
    $o .= '</nav>';
    $o .= '<section class="ath-s ath-mine" id="reports"><h2>' . cc_ath_icon('reports', 'ath-hic') . 'Your reports</h2>'
        . ($mineHtml !== '' ? '<div class="ath-body">' . $mineHtml . '</div>'
           : '<div class="ath-empty">' . cc_ath_icon('doc') . '<p>Your first assessment, reviews and progress reports will appear here. I will let you know when there is something new.</p></div>')
        . '</section>';
    $o .= $hub[0];
    return $o . '</div>' . cc_ath_js();
}

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
        'swim' => '<path d="M2 18c2 0 2-1.5 4-1.5S8 18 10 18s2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/><path d="M2 13c2 0 2-1.5 4-1.5S8 13 10 13s2-1.5 4-1.5 2 1.5 4 1.5 2-1.5 4-1.5"/><circle cx="16" cy="5" r="2"/><path d="M6 9l4-3 3 3"/>',
    ];
    return '<span class="' . $cls . '" aria-hidden="true"><svg viewBox="0 0 24 24">' . ($I[$k] ?? $I['link']) . '</svg></span>';
}
// what a link is, from where it goes: [icon, line under the title]; Matteo can edit the hub freely and the cards follow
function cc_ath_kind($href) {
    $m = [['calendly.com', 'calendar', 'Pick a time that suits you'], ['vivifysports', 'food', 'With Marine Lenehan, sports nutritionist'],
          ['wa.me', 'chat', 'I usually reply within a few hours'], ['skool.com', 'people', 'Chat with the Cigala community'],
          ['vekta', 'bolt', 'Your plan, workouts and analysis'], ['trainingpeaks', 'peaks', 'Your plan and workouts'],
          ['training-zones', 'zones', ''], ['carbs-per-hour', 'carbs', ''], ['critical-power', 'cp', ''], ['ftp-test', 'ftp', ''],
          ['sweat-rate', 'sweat', ''], ['climb-time', 'climb', ''], ['gear-speed', 'gear', ''], ['swim-pace', 'swim', ''], ['.pdf', 'doc', '']];
    foreach ($m as $x) if (stripos($href, $x[0]) !== false) return [$x[1], $x[2]];
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
        $href = cc_ath_attr($a[1], 'href'); $name = trim(wp_strip_all_tags($a[2])) ?: 'Document';
        return '<a class="ath-file" href="' . esc_url($href) . '" target="_blank" rel="noopener">' . cc_ath_icon('doc')
             . '<span class="ath-tt"><b>' . esc_html($name) . '</b><small>PDF · opens in a new tab</small></span><span class="ath-dl">Open</span></a>';
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
                  . '<span class="ath-read-t">' . wp_strip_all_tags($x[2]) . '</span>' . ($min ? '<small>' . $min . ' min read</small>' : '') . '</a>';
        }
        return '<div class="ath-reads">' . $out . '</div>';
    }, $html);
    return $html;
}
// split the hub at each H2 into its own animated card, with an icon and an anchor for the jump menu
function cc_ath_sections($html) {
    $parts = preg_split('#(<h2[^>]*>.*?</h2>)#s', $html, -1, PREG_SPLIT_DELIM_CAPTURE | PREG_SPLIT_NO_EMPTY);
    $out = ''; $nav = []; $open = false;
    $icons = [['quick', 'bolt'], ['app', 'phone'], ['guide', 'doc'], ['pdf', 'doc'], ['tool', 'gauge'], ['read', 'book'], ['blog', 'book']];
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
    return '<span class="sigph"><img src="' . esc_url($u . 'cigala-coaching-about-hero-matteo-photo.webp') . '" alt="Matteo Cigala, your coach, in the white Cigala Cycling jersey" width="720" height="933">'
         . '<img class="signature" src="' . esc_url($u . 'cigala-coaching-matteo-cigala-signature.webp') . '" alt="" aria-hidden="true" width="720" height="933"><span class="sig-anchor" aria-hidden="true"></span></span>';
}
function cc_ath_js() {
    return <<<'JS'
<script>(function(){
var g=document.querySelector('.ath-greet');if(g){var h=new Date().getHours();g.textContent=h<5?'Good evening':h<12?'Good morning':h<18?'Good afternoon':'Good evening';}
try{localStorage.setItem('cc_tools_ok','1');}catch(e){}   /* coached athletes skip the newsletter step on the free tools */
var rm=matchMedia('(prefers-reduced-motion: reduce)').matches,io='IntersectionObserver' in window;
document.querySelectorAll('.ath-n').forEach(function(el){var n=+el.getAttribute('data-n');if(rm||!n)return;var s=0;el.textContent='0';
 function f(t){if(!s)s=t;var p=Math.min(1,(t-s)/1400);el.textContent=Math.round(n*(1-Math.pow(1-p,3)));if(p<1)requestAnimationFrame(f);}setTimeout(function(){requestAnimationFrame(f);},350);});
if(!rm&&io){document.documentElement.classList.add('ath-anim');var o=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');o.unobserve(e.target);}});},{threshold:.06,rootMargin:'0px 0px -40px 0px'});
 document.querySelectorAll('.ath-s,.ath-hero').forEach(function(s){o.observe(s);});
 var sig=document.querySelectorAll('img.signature');if(sig.length){document.documentElement.classList.add('sig-ok');var so=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){so.unobserve(e.target);e.target._sig.classList.add('go');}});},{threshold:.5});
 sig.forEach(function(x){var t=x.nextElementSibling||x.parentElement;t._sig=x;so.observe(t);});}}
})();</script>
JS;
}
function cc_ath_shortcode() {   // in the site design: the .cc wrapper picks up the Coaching kit styles
    return '<div class="cc cc-page"><section class="ath-sec"><div class="in">' . cc_ath_inner() . '</div></section></div>';
}
add_shortcode('cc_athletes', 'cc_ath_shortcode');
add_action('wp_head', function () {
    if (!is_page(CC_ATH_SLUG)) return;
    echo <<<'CSS'
<style id="cc-athletes">
html .cc .ath-sec { padding-block: 140px 80px; min-height: 70vh; }
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
html .cc .ath-hero::after { content: ""; position: absolute; left: 0; right: 0; bottom: 0; height: 4px; background: linear-gradient(90deg, #12a150 0 33.3%, #fff 33.3% 66.6%, #e2231a 66.6%); opacity: .9; }
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
html .cc .ath-jump { display: flex; gap: 8px; overflow-x: auto; scrollbar-width: none; margin: 0 0 18px; padding: 2px; }
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
  html .cc .ath-sec { padding-block: 100px 56px; }
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
