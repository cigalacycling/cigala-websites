<?php
/* Reports from Matteo's PC tools into the athlete hub (Matteo 16 Nov 2026). Pushed with --availability.
 * - His PC sessions send a page (HTML) or a PDF: POST /wp-json/cc/v1/report {email, type, title, html | pdf_base64}
 *   (application password, editor or above). It always arrives as a DRAFT that only Matteo sees.
 * - Matteo: /athletes/?board=reports. Preview, then Publish (with "Email the athlete": ticked by default for assessments,
 *   reviews, race plans and progress reports, unticked for season plan updates) or Delete.
 * - Athlete: "Your season" card (always the latest published season plan, "Updated" badge), report cards with "New" badges
 *   and "You have N new reports". Opening a report clears its badge.
 * - Files live in uploads/cc-private, attached to the report (never served by the cc_file link). Served by ?cc_report=ID after a
 *   login check; HTML pages are sandboxed (Content-Security-Policy: sandbox), so a report can never read the athlete's login.
 * - Only motivating, athlete-friendly reports (Matteo's rule): never the weekly plan, warnings or compliance counts.
 */
if (!defined('ABSPATH')) return;

const CC_R_TYPES = ['season' => ['Season plan', 'Piano di stagione', 'peaks'], 'assessment' => ['Assessment', 'Valutazione', 'gauge'],
    'review' => ['Review', 'Revisione', 'reports'], 'race-plan' => ['Race plan', 'Piano gara', 'bolt'], 'progress' => ['Progress report', 'Report dei progressi', 'reports'],
    'other' => ['Report', 'Report', 'doc']];
function cc_r_mail_default($type) { return $type !== 'season'; }   // season plan updates: no email unless Matteo ticks it
function cc_r_label($type, $it) { $t = CC_R_TYPES[$type] ?? CC_R_TYPES['other']; return $it ? $t[1] : $t[0]; }

add_action('init', function () {
    register_post_type('cc_report', ['labels' => ['name' => 'Athlete reports', 'singular_name' => 'Athlete report'], 'public' => false, 'publicly_queryable' => false,
        'exclude_from_search' => true, 'show_ui' => true, 'show_in_menu' => 'edit.php?post_type=cc_athlete', 'show_in_rest' => false, 'supports' => ['title'],
        'capability_type' => 'page', 'map_meta_cap' => true, 'rewrite' => false, 'query_var' => false]);
});

/* ---------- PC tools: send a report (always a draft) ---------- */
add_action('rest_api_init', function () {
    register_rest_route('cc/v1', '/report', ['methods' => 'POST', 'callback' => 'cc_r_create', 'permission_callback' => 'cc_ath_is_coach']);
    register_rest_route('cc/v1', '/reports', ['methods' => 'GET', 'callback' => 'cc_r_list_rest', 'permission_callback' => 'cc_ath_is_coach']);
});
function cc_r_create(WP_REST_Request $r) {
    $u = get_user_by('email', (string) $r->get_param('email'));
    $pid = $u ? cc_ath_page_of($u->ID) : 0;
    if (!$pid) return new WP_Error('cc_none', 'No athlete with that email', ['status' => 404]);
    $type = isset(CC_R_TYPES[$r->get_param('type')]) ? $r->get_param('type') : 'other';
    $title = cc_av_str($r->get_param('title') ?: cc_r_label($type, false), 140);
    $html = (string) $r->get_param('html'); $pdf = (string) $r->get_param('pdf_base64');
    if ($html !== '') { if (strlen($html) > 12 * 1024 * 1024) return new WP_Error('cc_big', 'Report too big (12 MB max)', ['status' => 413]); $bytes = $html; $ext = 'html'; $mime = 'text/html'; }
    elseif ($pdf !== '') { $bytes = base64_decode($pdf, true); if ($bytes === false || strpos($bytes, '%PDF') !== 0) return new WP_Error('cc_pdf', 'Not a PDF', ['status' => 400]); $ext = 'pdf'; $mime = 'application/pdf'; }
    else return new WP_Error('cc_empty', 'Send html or pdf_base64', ['status' => 400]);
    $rid = wp_insert_post(['post_type' => 'cc_report', 'post_status' => 'draft', 'post_title' => $title, 'post_parent' => $pid,
        'meta_input' => ['cc_type' => $type, 'cc_note' => cc_av_str($r->get_param('note'), 300)]]);
    if (is_wp_error($rid) || !$rid) return new WP_Error('cc_fail', 'Could not save the report', ['status' => 500]);
    $fid = cc_f_store($rid, $bytes, 'report-' . $type, $ext, $mime, $title);
    update_post_meta($rid, 'cc_file', $fid);
    return ['ok' => true, 'id' => $rid, 'status' => 'draft', 'preview' => add_query_arg('cc_report', $rid, home_url('/' . CC_ATH_SLUG . '/')),
            'review' => add_query_arg('board', 'reports', home_url('/' . CC_ATH_SLUG . '/'))];
}
function cc_r_list_rest(WP_REST_Request $r) {
    $q = ['post_type' => 'cc_report', 'post_status' => ['draft', 'private'], 'numberposts' => 200, 'orderby' => 'date', 'order' => 'DESC'];
    if ($r->get_param('email')) { $u = get_user_by('email', (string) $r->get_param('email')); $q['post_parent'] = $u ? cc_ath_page_of($u->ID) : -1; }
    return array_map(function ($p) { return ['id' => $p->ID, 'athlete' => get_post_field('post_title', $p->post_parent), 'type' => get_post_meta($p->ID, 'cc_type', true), 'title' => $p->post_title,
        'status' => $p->post_status === 'private' ? 'published' : 'draft', 'created' => $p->post_date, 'published' => (int) get_post_meta($p->ID, 'cc_published', true) ?: null]; }, get_posts($q));
}

/* ---------- serving a report: /athletes/?cc_report=ID ---------- */
function cc_r_can_open($rid) {
    $p = get_post($rid); if (!$p || $p->post_type !== 'cc_report' || !is_user_logged_in()) return false;
    if (cc_ath_is_coach()) return true;
    $me = get_current_user_id();
    return $p->post_status === 'private' && (int) get_post_meta($p->post_parent, 'cc_user', true) === $me && (!function_exists('cc_f_open') || cc_f_open($me));
}
add_action('template_redirect', function () {
    if (!isset($_GET['cc_report'])) return;
    nocache_headers(); header('X-Robots-Tag: noindex, nofollow'); do_action('litespeed_control_set_nocache', 'athlete report');
    $rid = (int) $_GET['cc_report'];
    if (!is_user_logged_in()) { wp_safe_redirect(home_url('/' . CC_ATH_SLUG . '/')); exit; }
    if (!cc_r_can_open($rid)) { status_header(403); exit('This report is not part of your account.'); }
    $fid = (int) get_post_meta($rid, 'cc_file', true); $file = $fid ? get_attached_file($fid, true) : '';
    if (!$file || !file_exists($file)) { status_header(404); exit('Not found'); }
    if (!cc_ath_is_coach()) { $seen = (array) get_user_meta(get_current_user_id(), 'cc_seen_reports', true); if (!in_array($rid, $seen, true)) { $seen[] = $rid; update_user_meta(get_current_user_id(), 'cc_seen_reports', $seen); } }
    while (ob_get_level()) ob_end_clean();
    $mime = get_post_mime_type($fid) ?: 'application/octet-stream';
    header('Content-Type: ' . ($mime === 'text/html' ? 'text/html; charset=utf-8' : $mime));
    header('X-Content-Type-Options: nosniff');
    if ($mime === 'text/html') header("Content-Security-Policy: sandbox allow-scripts allow-popups allow-popups-to-escape-sandbox allow-downloads");   // no access to the site's cookies
    header('Content-Disposition: inline; filename="' . sanitize_file_name(get_post_field('post_title', $rid)) . '.' . ($mime === 'text/html' ? 'html' : 'pdf') . '"');
    header('Content-Length: ' . filesize($file));
    readfile($file); exit;
}, 1);
function cc_r_url($rid) { return add_query_arg('cc_report', $rid, home_url('/' . CC_ATH_SLUG . '/')); }

/* ---------- the athlete's hub ---------- */
function cc_r_published($pid) {
    return get_posts(['post_type' => 'cc_report', 'post_status' => 'private', 'post_parent' => $pid, 'numberposts' => 100, 'orderby' => 'meta_value_num', 'meta_key' => 'cc_published', 'order' => 'DESC']);
}
function cc_r_unseen($uid, $rid) { return !in_array($rid, (array) get_user_meta($uid, 'cc_seen_reports', true), true); }
add_filter('cc_ath_before_reports', function ($html, $view, $coach) {
    if (!$view) return $html;
    $uid = (int) get_post_meta($view, 'cc_user', true); $it = ($GLOBALS['cc_ath_lang'] ?? 'en') === 'it';
    $all = cc_r_published($view); $season = null; $new = 0;
    foreach ($all as $p) { $t = get_post_meta($p->ID, 'cc_type', true); if ($t === 'season') { if (!$season) $season = $p; } elseif ($uid && cc_r_unseen($uid, $p->ID)) $new++; }
    if ($new) $html .= '<p class="rp-new" role="status"><b>' . $new . '</b> ' . esc_html($it ? ($new === 1 ? 'nuovo report per te' : 'nuovi report per te') : ($new === 1 ? 'new report for you' : 'new reports for you')) . ' <a href="#reports">' . esc_html($it ? 'Vedi' : 'See') . ' →</a></p>';
    if ($season) {
        $when = (int) get_post_meta($season->ID, 'cc_published', true);
        $html .= '<section class="ath-s rp-season" id="season"><h2>' . cc_ath_icon('peaks', 'ath-hic') . esc_html($it ? 'La tua stagione' : 'Your season') . '</h2>'
            . '<p class="av-lede">' . esc_html($it ? 'Il tuo piano di stagione: blocchi, gare e obiettivi. Lo aggiorno ogni volta che il piano cambia; gli allenamenti di ogni giorno restano su Vekta.' : 'Your season plan: the blocks, your races and your goals. I update it whenever the plan changes; your day-to-day sessions stay in Vekta.') . '</p>'
            . '<div class="rp-season-row"><a class="btn btn-go" href="' . esc_url(cc_r_url($season->ID)) . '" target="_blank" rel="noopener">' . esc_html($it ? 'Apri il mio piano di stagione' : 'Open my season plan') . '</a>'
            . '<span class="rp-when">' . esc_html(($it ? 'Aggiornato il ' : 'Updated ') . date_i18n('j M Y', $when)) . ($uid && cc_r_unseen($uid, $season->ID) ? ' <span class="rp-badge">' . esc_html($it ? 'Aggiornato' : 'Updated') . '</span>' : '') . '</span></div></section>';
    }
    return $html;
}, 10, 3);
add_filter('cc_ath_reports_html', function ($html, $view, $coach) {
    if (!$view) return $html;
    $uid = (int) get_post_meta($view, 'cc_user', true); $it = ($GLOBALS['cc_ath_lang'] ?? 'en') === 'it'; $o = '';
    foreach (cc_r_published($view) as $p) {
        $t = get_post_meta($p->ID, 'cc_type', true); if ($t === 'season') continue;
        $new = $uid && cc_r_unseen($uid, $p->ID);
        $o .= '<a class="ath-file rp-card' . ($new ? ' is-new' : '') . '" href="' . esc_url(cc_r_url($p->ID)) . '" target="_blank" rel="noopener">' . cc_ath_icon(CC_R_TYPES[$t][2] ?? 'doc')
            . '<span class="ath-tt"><b>' . esc_html($p->post_title) . ($new ? ' <span class="rp-badge">' . esc_html($it ? 'Nuovo' : 'New') . '</span>' : '') . '</b><small>' . esc_html(cc_r_label($t, $it) . ' · ' . date_i18n('j M Y', (int) get_post_meta($p->ID, 'cc_published', true))) . '</small></span>'
            . '<span class="ath-dl">' . esc_html($it ? 'Apri' : 'Open') . '</span></a>';
    }
    return $html . ($o ? '<div class="ath-body rp-list">' . $o . '</div>' : '');
}, 10, 3);
add_filter('cc_ath_nav', function ($nav, $view) {
    if ($view && get_posts(['post_type' => 'cc_report', 'post_status' => 'private', 'post_parent' => $view, 'numberposts' => 1, 'fields' => 'ids', 'meta_key' => 'cc_type', 'meta_value' => 'season']))
        array_unshift($nav, ['season', ($GLOBALS['cc_ath_lang'] ?? 'en') === 'it' ? 'La tua stagione' : 'Your season']);
    return $nav;
}, 30, 2);

/* ---------- Matteo: /athletes/?board=reports ---------- */
add_filter('cc_ath_coach_links', function ($html) {
    $n = count(get_posts(['post_type' => 'cc_report', 'post_status' => 'draft', 'numberposts' => -1, 'fields' => 'ids']));
    return $html . '<a class="av-boardlink" href="' . esc_url(add_query_arg('board', 'reports', home_url('/' . CC_ATH_SLUG . '/'))) . '">Reports' . ($n ? ' <span class="av-badge">' . $n . ' to review</span>' : '') . '</a>';
}, 7);
function cc_r_btn($rid, $act, $text, $go = false, $extra = '') {
    return '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" class="rf-act rp-act"><input type="hidden" name="action" value="cc_report_admin"><input type="hidden" name="rid" value="' . $rid . '">'
         . '<input type="hidden" name="act" value="' . $act . '">' . wp_nonce_field('cc_report_' . $rid, '_wpnonce', false, false) . $extra . '<button class="btn ' . ($go ? 'btn-go' : 'btn-ghost') . '">' . esc_html($text) . '</button></form>';
}
add_filter('cc_ath_board', function ($html, $board) {
    if ($board !== 'reports' || !cc_ath_is_coach()) return $html;
    $o = '<section class="ath-s"><h2>' . cc_ath_icon('reports', 'ath-hic') . 'Reports</h2><p class="av-lede">Reports your PC tools send arrive here as drafts. Nothing reaches an athlete until you publish it. '
       . 'Preview, then publish (tick “Email the athlete” if you want them told by email) or delete. To add a PDF by hand, upload it inside the athlete’s page, as before.</p>';
    $drafts = get_posts(['post_type' => 'cc_report', 'post_status' => 'draft', 'numberposts' => -1, 'orderby' => 'date', 'order' => 'DESC']);
    $o .= '<h3 class="av-sub">To review</h3>';
    if (!$drafts) $o .= '<p class="av-none">Nothing waiting.</p>';
    foreach ($drafts as $p) {
        $t = get_post_meta($p->ID, 'cc_type', true); $chk = cc_r_mail_default($t) ? ' checked' : '';
        $o .= '<div class="rp-row"><div class="rp-what"><b>' . esc_html($p->post_title) . '</b><small>' . esc_html(get_post_field('post_title', $p->post_parent) . ' · ' . cc_r_label($t, false) . ' · sent ' . human_time_diff(strtotime(get_gmt_from_date($p->post_date) . ' UTC')) . ' ago')
            . ($t === 'season' ? ' · replaces their current season plan' : '') . '</small></div><div class="rp-acts"><a class="btn btn-ghost" href="' . esc_url(cc_r_url($p->ID)) . '" target="_blank" rel="noopener">Preview</a>'
            . cc_r_btn($p->ID, 'publish', 'Publish', true, '<label class="rp-mail"><input type="checkbox" name="mail" value="1"' . $chk . '> Email the athlete</label>') . cc_r_btn($p->ID, 'delete', 'Delete') . '</div></div>';
    }
    $pub = get_posts(['post_type' => 'cc_report', 'post_status' => 'private', 'numberposts' => 30, 'orderby' => 'meta_value_num', 'meta_key' => 'cc_published', 'order' => 'DESC']);
    if ($pub) {
        $o .= '<h3 class="av-sub" style="margin-top:22px">Published</h3>';
        foreach ($pub as $p) { $t = get_post_meta($p->ID, 'cc_type', true); $uid = (int) get_post_meta($p->post_parent, 'cc_user', true);
            $o .= '<div class="rp-row"><div class="rp-what"><b>' . esc_html($p->post_title) . '</b><small>' . esc_html(get_post_field('post_title', $p->post_parent) . ' · ' . cc_r_label($t, false) . ' · published ' . date_i18n('j M Y', (int) get_post_meta($p->ID, 'cc_published', true))
                . (get_post_meta($p->ID, 'cc_mailed', true) ? ' · emailed' : '') . ($uid ? (cc_r_unseen($uid, $p->ID) ? ' · not opened yet' : ' · opened') : '')) . '</small></div><div class="rp-acts"><a class="btn btn-ghost" href="' . esc_url(cc_r_url($p->ID)) . '" target="_blank" rel="noopener">Open</a>'
                . cc_r_btn($p->ID, 'unpublish', 'Unpublish') . '</div></div>'; }
    }
    return $o . '</section>';
}, 10, 2);
add_action('admin_post_cc_report_admin', function () {
    $rid = (int) ($_POST['rid'] ?? 0); $act = sanitize_key($_POST['act'] ?? '');
    if (!cc_ath_is_coach() || !wp_verify_nonce($_POST['_wpnonce'] ?? '', 'cc_report_' . $rid) || get_post_type($rid) !== 'cc_report') wp_die('Not allowed');
    if ($act === 'publish') {
        wp_update_post(['ID' => $rid, 'post_status' => 'private']); update_post_meta($rid, 'cc_published', time());
        if (!empty($_POST['mail'])) { cc_r_mail($rid); update_post_meta($rid, 'cc_mailed', time()); }
    } elseif ($act === 'unpublish') { wp_update_post(['ID' => $rid, 'post_status' => 'draft']);
    } elseif ($act === 'delete') { $fid = (int) get_post_meta($rid, 'cc_file', true); if ($fid) wp_delete_attachment($fid, true); wp_delete_post($rid, true); }
    wp_safe_redirect(add_query_arg('board', 'reports', home_url('/' . CC_ATH_SLUG . '/'))); exit;
});
function cc_r_mail($rid) {   // "your new report is ready", in the hub language (English or Italian)
    $p = get_post($rid); $u = get_userdata((int) get_post_meta($p->post_parent, 'cc_user', true)); if (!$u || !is_email($u->user_email)) return;
    $it = cc_ath_user_lang($u->ID) === 'it'; $first = esc_html($u->first_name ?: $u->display_name); $t = get_post_meta($rid, 'cc_type', true);
    $link = home_url('/' . CC_ATH_SLUG . '/') . ($t === 'season' ? '#season' : '#reports');
    $h = '<div style="font-family:Montserrat,Helvetica,Arial,sans-serif;font-size:16px;line-height:1.6;color:#16181b;max-width:520px"><p style="font-weight:700">' . ($it ? "Ciao $first," : "Hi $first,") . '</p>'
       . '<p>' . ($it ? 'nella tua area atleta c’è qualcosa di nuovo per te:' : 'There is something new for you in your athlete hub:') . '</p>'
       . '<p style="padding:12px 16px;border-left:3px solid #12a150;background:#f2f4f3"><b style="color:#111">' . esc_html($p->post_title) . '</b><br><span style="font-size:14px;color:#454a52">' . esc_html(cc_r_label($t, $it)) . '</span></p>'
       . '<p style="margin:22px 0"><a href="' . esc_url($link) . '" style="display:inline-block;padding:14px 24px;border-radius:10px;background:#12a150;color:#fff;font-weight:700;text-decoration:none">' . ($it ? 'Aprilo nella mia area' : 'Open it in my hub') . '</a></p>'
       . '<p>' . ($it ? 'A presto in bici,' : 'See you on the road,') . '<br><strong>Matteo</strong></p></div>';
    $to = strpos(home_url(), '//staging.') !== false ? (string) get_option('cc_staging_notify', '') : $u->user_email;   // staging: never an athlete
    if (!is_email($to)) return;
    wp_mail($to, $it ? 'È pronto il tuo nuovo report: ' . $p->post_title : 'Your new report is ready: ' . $p->post_title, $h,
        ['Content-Type: text/html; charset=UTF-8', 'From: Matteo Cigala <noreply@cigalacycling.com>', 'Reply-To: Matteo Cigala <matteo@cigalacycling.com>']);
}
add_action('wp_head', function () {
    if (!is_page(CC_ATH_SLUG)) return;
    echo "<style id=\"cc-reports\">html .cc .rp-new{margin:0 0 14px;padding:12px 16px;border-radius:12px;background:rgba(0,154,68,.14);border:1px solid rgba(52,196,106,.45);color:#fff;font-size:14.5px}"
       . "html .cc .rp-new b{font:400 22px/1 var(--head);color:#34c46a;margin-right:4px}html .cc .rp-new a{color:#34c46a;font-weight:600;margin-left:6px}"
       . "html .cc .rp-season{border-color:rgba(43,212,122,.4);background:linear-gradient(180deg,rgba(18,161,80,.12),rgba(13,15,17,.9) 60%)}html .cc .rp-season-row{display:flex;flex-wrap:wrap;align-items:center;gap:10px 16px}"
       . "html .cc .rp-when{font-size:13.5px;color:var(--text-3)}html .cc .rp-badge{display:inline-block;padding:2px 9px;border-radius:999px;background:#E10600;color:#fff;font:700 11px/1.6 var(--body);letter-spacing:.06em;text-transform:uppercase;vertical-align:middle}"
       . "html .cc .rp-list{margin:0 0 14px}html .cc .rp-card.is-new{border-color:rgba(52,196,106,.6)}"
       . "html .cc .rp-row{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px 16px;padding:12px 14px;margin:0 0 8px;border-radius:12px;background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.08)}"
       . "html .cc .rp-what{display:grid;gap:2px;min-width:0}html .cc .rp-what b{color:#fff}html .cc .rp-what small{color:var(--text-3);font-size:12.5px}"
       . "html .cc .rp-acts{display:flex;flex-wrap:wrap;align-items:center;gap:8px}html .cc .rp-act{display:flex;align-items:center;gap:10px;margin:0}html .cc .rp-mail{display:flex;align-items:center;gap:6px;font-size:13px;color:var(--text-2);margin:0!important}"
       . "html .cc .rp-mail input{width:18px;height:18px;accent-color:#009a44}html .cc .ath form.rp-act .btn{width:auto;margin:0}html .cc .ath form.rp-act{display:flex;flex-direction:row;align-items:center;gap:12px;margin:0}html .cc .ath .rp-acts .btn{min-height:44px;margin:0}@media (max-width:560px){html .cc .rp-acts{display:grid;grid-template-columns:1fr 1fr;width:100%}html .cc .rp-acts>.rp-act:has(.rp-mail){grid-column:1/-1;order:-1;justify-content:space-between}html .cc .rp-acts .btn,html .cc .ath form.rp-act .btn{width:100%;justify-content:center}html .cc .ath form.rp-act:not(:has(.rp-mail)){display:block}html .cc .rp-act:has(.rp-mail) .btn{width:auto;flex:1 1 auto}}</style>\n";
});
