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
    $o .= '<div class="ath-top"><div><p class="eyebrow">Athlete area</p><h1>Welcome, ' . esc_html($first) . '</h1></div>'
        . '<a class="btn btn-ghost" href="' . esc_url(wp_logout_url($url)) . '">Log out</a></div>';
    if ($coach) {
        $list = get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'orderby' => 'title', 'order' => 'ASC', 'meta_key' => 'cc_user']);
        $o .= '<div class="ath-coach"><p><b>Coach view.</b> You see the shared hub below. Choose an athlete to see their page as they see it, or add athletes in WordPress: Users &gt; Add New (role Subscriber).</p><p class="ath-list">';
        foreach ($list as $p) $o .= '<a href="' . esc_url(add_query_arg('view', $p->ID, $url)) . '"' . ($view === $p->ID ? ' aria-current="page"' : '') . '>' . esc_html($p->post_title) . '</a>';
        $o .= '</p></div>';
    }
    if ($view) {
        $c = trim(cc_ath_content($view));
        $o .= '<section class="ath-mine"><h2>Your reports</h2>' . ($c !== '' ? '<div class="ath-body">' . $c . '</div>'
             : '<p class="ath-empty">Your first assessment, reviews and progress reports will appear here.</p>') . '</section>';
    }
    $shared = cc_ath_shared_page();
    if ($shared) $o .= '<section class="ath-hub"><div class="ath-body">' . cc_ath_content($shared) . '</div></section>';
    return $o . '</div>';
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
html .cc .ath-help a, html .cc .ath-body a:not(.wp-block-button__link):not(.wp-block-file__button) { color: var(--green-text, #2bd47a); }
html .cc .ath-top { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; flex-wrap: wrap; margin-bottom: 24px; }
html .cc .ath-top h1 { margin-bottom: 0; }
html .cc .ath-coach { padding: 16px 18px; border-radius: 12px; border: 1px dashed rgba(255,255,255,.25); margin: 0 0 28px; font-size: 14px; color: var(--text-2); }
html .cc .ath-coach p { margin: 0 0 8px; }
html .cc .ath-list { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 !important; }
html .cc .ath-list a { padding: 6px 12px; border-radius: 999px; background: rgba(255,255,255,.08); color: #fff; text-decoration: none; font-size: 13px; }
html .cc .ath-list a[aria-current] { background: #12a150; }
html .cc .ath-mine, html .cc .ath-hub { padding: 28px 26px; border-radius: 16px; background: rgba(15,17,19,.88); border: 1px solid rgba(255,255,255,.1); margin: 0 0 22px; }
html .cc .ath-mine { border-color: rgba(43,212,122,.35); }
html .cc .ath-empty { color: var(--text-3); margin: 0; }
html .cc .ath-body h2 { margin-top: 30px; }
html .cc .ath-mine .ath-body h2, html .cc .ath-mine .ath-body h3 { font-size: 20px; margin: 22px 0 10px; }
html .cc .ath-body ul { columns: 2 260px; column-gap: 32px; padding-left: 18px; margin: 0 0 10px; }
html .cc .ath-body li { break-inside: avoid; margin: 0 0 8px; }
html .cc .ath-body li::marker { color: #12a150; }
html .cc .ath-body > :first-child { margin-top: 0; }
html .cc .ath-body > :last-child { margin-bottom: 0; }
html .cc .ath-body p, html .cc .ath-body li { color: var(--text-2); }
html .cc .ath-body .wp-block-buttons { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; margin: 0 0 8px; }
html .cc .ath-body .wp-block-button { margin: 0; }
html .cc .ath-body .ath-tools { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); }
html .cc .ath-body .ath-tools .wp-block-button__link { min-height: 46px; font-size: 14px; padding: 10px; }
html .cc .ath-body .wp-block-button__link { display: flex; align-items: center; justify-content: center; min-height: 52px; width: 100%; box-sizing: border-box; padding: 12px 16px; border-radius: 10px; background: #12a150; color: #fff; font-weight: 600; text-decoration: none; text-align: center; }
html .cc .ath-body .is-style-outline .wp-block-button__link { background: transparent; border: 1px solid rgba(255,255,255,.25); }
html .cc .ath-body .wp-block-button__link:hover { filter: brightness(1.1); }
html .cc .ath-body .wp-block-file { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; padding: 12px 14px; border-radius: 10px; background: rgba(255,255,255,.05); margin: 0 0 8px; }
html .cc .ath-body .wp-block-file a:first-child { color: #fff !important; font-weight: 600; }
html .cc .ath-body .wp-block-file__button { padding: 8px 14px; border-radius: 8px; background: #12a150; color: #fff; text-decoration: none; font-size: 14px; }
html .cc .ath-body .wp-block-file__embed { display: none; }
@media (max-width: 600px) { html .cc .ath-sec { padding-block: 110px 56px; } html .cc .ath-login, html .cc .ath-mine, html .cc .ath-hub { padding: 24px 18px; } }
</style>
CSS;
});
