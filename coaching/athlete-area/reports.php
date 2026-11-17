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
    'race-sim' => ['Race day simulator', 'Simulatore di gara', 'bolt'], 'prediction' => ['Race prediction', 'Previsione gara', 'gauge'], 'snapshot' => ['Training snapshot', 'Panoramica allenamento', 'reports'],
    'race-recap' => ['Race recap', 'Resoconto della gara', 'bolt'], 'milestones' => ['Since you joined', 'Da quando hai iniziato', 'peaks'],   // Matteo 17 Nov
    'guide' => ['Guide', 'Guida', 'book'], 'other' => ['Report', 'Report', 'doc']];
/* Matteo 17 Nov: pages the athlete opens often, always the latest one: season plan (periodisation), race prediction, training snapshot.
 * One current page per kind. After Matteo has published the first one with "Keep it updated automatically", the laptop's new versions go
 * live straight away (no email); otherwise each one waits for him as a draft. */
const CC_R_LIVE = ['season', 'snapshot', 'prediction'];
const CC_R_ONTOP = ['race-plan', 'race-sim', 'race-recap'];
/* Matteo 17 Nov: the training response report (progress) and race plans also keep themselves up to date once he publishes the first one
 * with "Keep it updated automatically" (one current per athlete + key; no email). Shown where they always were (Your reports). */
const CC_R_AUTO = ['season', 'snapshot', 'prediction', 'progress', 'race-sim', 'race-plan', 'race-recap', 'milestones'];
/* Matteo 17 Nov: pages made by automatic processes that need no review from him: they publish themselves when his switch is on */
const CC_R_SELF = ['race-sim', 'race-plan', 'race-recap', 'milestones', 'progress'];   // Matteo 17 Nov: he approves only reviews, assessments and season plans   // one per race: all stay on top
function cc_r_auto($pid, $type = null) { $a = (array) get_post_meta($pid, 'cc_auto', true); return $type === null ? $a : in_array($type, $a, true); }
function cc_r_set_auto($pid, $type, $on) { $a = array_values(array_diff(cc_r_auto($pid), [$type])); if ($on) $a[] = $type; update_post_meta($pid, 'cc_auto', $a); }
function cc_r_go_live($rid) {   // publish; a live kind replaces the athlete's previous one (season plans are kept as history)
    $p = get_post($rid); $t = get_post_meta($rid, 'cc_type', true);
    wp_update_post(['ID' => $rid, 'post_status' => 'private']); update_post_meta($rid, 'cc_published', time());
    if (in_array($t, CC_R_LIVE, true) && $t !== 'season')
        foreach (get_posts(['post_type' => 'cc_report', 'post_status' => 'private', 'post_parent' => $p->post_parent, 'numberposts' => -1, 'exclude' => [$rid], 'meta_key' => 'cc_type', 'meta_value' => $t, 'fields' => 'ids']) as $old) cc_r_delete($old);
    foreach (cc_r_same_key($rid, 'private') as $old) cc_r_delete($old);   // same athlete + kind + key (one race, the training report): the new one replaces it
}
/* Optional `key` from the laptop (Matteo 17 Nov): one current report per athlete + kind + key, e.g. a race slug for race-sim / race-plan,
 * "training-report" for the Training Response Report. A newer draft replaces an unpublished one; publishing it replaces the published one. */
function cc_r_key($k) { return substr(sanitize_title((string) $k), 0, 80); }
function cc_r_same_key($rid, $status) {
    $k = (string) get_post_meta($rid, 'cc_key', true); if ($k === '') return [];
    return get_posts(['post_type' => 'cc_report', 'post_status' => $status, 'post_parent' => get_post($rid)->post_parent, 'numberposts' => -1, 'exclude' => [$rid], 'fields' => 'ids',
        'meta_query' => [['key' => 'cc_type', 'value' => get_post_meta($rid, 'cc_type', true)], ['key' => 'cc_key', 'value' => $k]]]);
}   // guide: a resource for this athlete (Vekta brief 17 Nov)
function cc_r_mail_default($type) { return !in_array($type, CC_R_AUTO, true); }   // pages that keep changing (season plan, prediction, snapshot): no email unless Matteo ticks it
function cc_r_label($type, $it = null) { $t = CC_R_TYPES[$type] ?? CC_R_TYPES['other']; return $it === false ? $t[0] : cc_L($t[0], $t[1]); }   // false: English (coach board)

add_action('init', function () {
    register_post_type('cc_report', ['labels' => ['name' => 'Athlete reports', 'singular_name' => 'Athlete report'], 'public' => false, 'publicly_queryable' => false,
        'exclude_from_search' => true, 'show_ui' => true, 'show_in_menu' => 'edit.php?post_type=cc_athlete', 'show_in_rest' => false, 'supports' => ['title'],
        'capability_type' => 'page', 'map_meta_cap' => true, 'rewrite' => false, 'query_var' => false]);
});

/* ---------- PC tools: send a report (always a draft) ---------- */
add_action('rest_api_init', function () {
    register_rest_route('cc/v1', '/report', ['methods' => 'POST', 'callback' => 'cc_r_create', 'permission_callback' => 'cc_ath_is_coach']);
    register_rest_route('cc/v1', '/report-testmail', ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        $rid = (int) $r->get_param('id'); $me = wp_get_current_user();
        if (get_post_type($rid) !== 'cc_report' || !is_email($me->user_email)) return new WP_Error('cc_none', 'No such report', ['status' => 404]);
        if ($r->get_param('dry')) return cc_r_mail($rid, $me->user_email, true);   // preview, nothing sent
        cc_r_mail($rid, $me->user_email); return ['ok' => true, 'sent_to_yourself' => true];
    }]);
    register_rest_route('cc/v1', '/reports', ['methods' => 'GET', 'callback' => 'cc_r_list_rest', 'permission_callback' => 'cc_ath_is_coach']);
    // Matteo 17 Nov: the hub chat can clear DRAFTS its tools made (e.g. the retired Training snapshot). Published reports are never deleted this way.
    register_rest_route('cc/v1', '/report/(?P<id>\d+)', ['methods' => 'DELETE', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        $id = (int) $r['id'];
        if (get_post_type($id) !== 'cc_report') return new WP_Error('cc_none', 'No such report', ['status' => 404]);
        if (get_post_status($id) !== 'draft') return new WP_Error('cc_published', 'Only drafts can be deleted here; published reports are Matteo’s to remove', ['status' => 409]);
        cc_r_delete($id); return ['ok' => true, 'deleted' => $id];
    }]);
});
function cc_r_create(WP_REST_Request $r) {
    if (function_exists('cc_pc_page_from')) $pid = cc_pc_page_from($r);   // email, vekta_id or page (pc-api.php)
    else { $u = get_user_by('email', (string) $r->get_param('email')); $pid = $u ? cc_ath_page_of($u->ID) : 0; }
    if (!$pid || !get_post_meta($pid, 'cc_user', true)) return new WP_Error('cc_none', 'No active athlete with that email / vekta_id / page', ['status' => 404]);
    $type = isset(CC_R_TYPES[$r->get_param('type')]) ? $r->get_param('type') : 'other';
    $title = cc_av_str($r->get_param('title') ?: cc_r_label($type, false) . ' · ' . date_i18n('F Y'), 140);
    $html = (string) $r->get_param('html'); $pdf = (string) $r->get_param('pdf_base64'); $link = esc_url_raw((string) $r->get_param('url'), ['https']);
    if ($link !== '' && $html === '' && $pdf === '') { $bytes = null; }   // a link to a page that lives elsewhere (opens after the login check)
    elseif ($html !== '') { if (strlen($html) > 12 * 1024 * 1024) return new WP_Error('cc_big', 'Report too big (12 MB max)', ['status' => 413]); $bytes = $html; $ext = 'html'; $mime = 'text/html'; }
    elseif ($pdf !== '') { $bytes = base64_decode($pdf, true); if ($bytes === false || strpos($bytes, '%PDF') !== 0) return new WP_Error('cc_pdf', 'Not a PDF', ['status' => 400]); $ext = 'pdf'; $mime = 'application/pdf'; }
    else return new WP_Error('cc_empty', 'Send html, pdf_base64 or url (https)', ['status' => 400]);
    $rid = wp_insert_post(['post_type' => 'cc_report', 'post_status' => 'draft', 'post_title' => $title, 'post_parent' => $pid,
        'meta_input' => ['cc_type' => $type, 'cc_note' => cc_av_str($r->get_param('note'), 300), 'cc_autotitle' => $r->get_param('title') ? 0 : 1, 'cc_key' => $type === 'season' ? '' : cc_r_key($r->get_param('key'))]]);   // season plans keep their history
    if (is_wp_error($rid) || !$rid) return new WP_Error('cc_fail', 'Could not save the report', ['status' => 500]);
    if ($bytes === null) update_post_meta($rid, 'cc_url', $link);
    else { $fid = cc_f_store($rid, $bytes, 'report-' . $type, $ext, $mime, $title); update_post_meta($rid, 'cc_file', $fid); }
    $replaced = [];
    if (in_array($type, CC_R_LIVE, true)) foreach (get_posts(['post_type' => 'cc_report', 'post_status' => 'draft', 'post_parent' => $pid, 'numberposts' => -1, 'exclude' => [$rid], 'meta_key' => 'cc_type', 'meta_value' => $type, 'fields' => 'ids']) as $old) {
        cc_r_delete($old); $replaced[] = $old;   // one draft per live kind: a newer one replaces an unpublished older one
    }
    foreach (cc_r_same_key($rid, 'draft') as $old) { cc_r_delete($old); $replaced[] = $old; }   // same key: one draft
    $auto = in_array($type, CC_R_AUTO, true) && cc_r_auto($pid, $type);
    if (in_array($type, CC_R_SELF, true) && get_option('cc_r_race_auto')) $auto = true;   // Matteo 17 Nov: his switch "Publish race plans automatically" (no draft step, no email)
    if ($auto) cc_r_go_live($rid);   // Matteo switched on automatic updates for this athlete and kind
    return ['ok' => true, 'id' => $rid, 'status' => $auto ? 'published' : 'draft', 'auto' => $auto, 'replaced_drafts' => $replaced, 'preview' => add_query_arg('cc_report', $rid, home_url('/' . CC_ATH_SLUG . '/')),
            'review' => add_query_arg('board', 'reports', home_url('/' . CC_ATH_SLUG . '/'))];
}
function cc_r_sweep() {   // reports whose athlete page no longer exists (deleted athlete): delete them and their file
    foreach (get_posts(['post_type' => 'cc_report', 'post_status' => 'any', 'numberposts' => -1]) as $p) if (!$p->post_parent || get_post_type($p->post_parent) !== 'cc_athlete') cc_r_delete($p->ID);
}
add_action('cc_f_retention', 'cc_r_sweep');
function cc_r_list_rest(WP_REST_Request $r) {
    cc_r_sweep();
    $q = ['post_type' => 'cc_report', 'post_status' => ['draft', 'private'], 'numberposts' => 200, 'orderby' => 'date', 'order' => 'DESC'];
    if ($r->get_param('email')) { $u = get_user_by('email', (string) $r->get_param('email')); $q['post_parent'] = $u ? cc_ath_page_of($u->ID) : -1; }
    return array_map(function ($p) { return ['id' => $p->ID, 'athlete' => get_post_field('post_title', $p->post_parent), 'type' => get_post_meta($p->ID, 'cc_type', true), 'title' => $p->post_title,
        'key' => (string) get_post_meta($p->ID, 'cc_key', true) ?: null, 'status' => $p->post_status === 'private' ? 'published' : 'draft', 'created' => $p->post_date, 'published' => (int) get_post_meta($p->ID, 'cc_published', true) ?: null]; }, get_posts($q));
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
    $ext = (string) get_post_meta($rid, 'cc_url', true);
    if ($ext === '' && (!$file || !file_exists($file))) { status_header(404); exit('Not found'); }
    if (!cc_ath_is_coach()) { $seen = (array) get_user_meta(get_current_user_id(), 'cc_seen_reports', true); if (!in_array($rid, $seen, true)) { $seen[] = $rid; update_user_meta(get_current_user_id(), 'cc_seen_reports', $seen); } }
    if ($ext !== '') { wp_redirect($ext); exit; }
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
function cc_r_date($ts, $long = false) {   // "17 Nov 2026" in the hub language (the site itself is in English)
    static $M = ['it' => ['gen','feb','mar','apr','mag','giu','lug','ago','set','ott','nov','dic'], 'pt' => ['jan','fev','mar','abr','mai','jun','jul','ago','set','out','nov','dez'],
                 'sl' => ['jan.','feb.','mar.','apr.','maj','jun.','jul.','avg.','sep.','okt.','nov.','dec.']];
    static $F = ['it' => ['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'],
                 'pt' => ['janeiro','fevereiro','março','abril','maio','junho','julho','agosto','setembro','outubro','novembro','dezembro'],
                 'sl' => ['januar','februar','marec','april','maj','junij','julij','avgust','september','oktober','november','december']];
    $l = $GLOBALS['cc_ath_lang'] ?? 'en';
    if ($long) return isset($F[$l]) ? $F[$l][(int) date_i18n('n', $ts) - 1] . ' ' . date_i18n('Y', $ts) : date_i18n('F Y', $ts);   // "May 2027"
    if (!isset($M[$l])) return date_i18n('j M Y', $ts);
    return ($l === 'sl' ? date_i18n('j.', $ts) : date_i18n('j', $ts)) . ' ' . $M[$l][(int) date_i18n('n', $ts) - 1] . ' ' . date_i18n('Y', $ts);
}
function cc_r_unseen($uid, $rid) { return !in_array($rid, (array) get_user_meta($uid, 'cc_seen_reports', true), true); }
add_filter('cc_ath_before_reports', function ($html, $view, $coach) {
    if (!$view) return $html;
    $uid = (int) get_post_meta($view, 'cc_user', true); $it = ($GLOBALS['cc_ath_lang'] ?? 'en') === 'it';
    $all = cc_r_published($view); $season = null; $new = 0;
    $live = [];
    foreach ($all as $p) { $t = get_post_meta($p->ID, 'cc_type', true); if (in_array($t, CC_R_LIVE, true) && $t !== 'season') { if (!isset($live[$t])) $live[$t] = $p; continue; } if ($t === 'season') { if (!$season) $season = $p; } elseif ($uid && cc_r_unseen($uid, $p->ID)) $new++; }
    if ($new) $html .= '<p class="rp-new" role="status"><b>' . $new . '</b> ' . esc_html(cc_Ln($new, 'new report for you', 'nuovo report per te', 'new reports for you', 'nuovi report per te')) . ' <a href="#reports">' . esc_html(cc_L('See', 'Vedi')) . ' →</a></p>';
    $cards = ''; foreach (['prediction', 'snapshot'] as $t) if (isset($live[$t])) $cards .= cc_r_card($live[$t], $uid);
    if (!$season && $cards !== '') $html .= '<section class="ath-s rp-season" id="season"><h2>' . cc_ath_icon('peaks', 'ath-hic') . esc_html(cc_L('Your training', 'Il tuo allenamento')) . '</h2><div class="ath-body rp-list">' . $cards . '</div></section>';
    if ($season) {   // Vekta brief 17 Nov: the season page shown in the hub, scripts on (zoom, hover), in a sandbox with no access to the login
        $when = (int) get_post_meta($season->ID, 'cc_published', true); $url = cc_r_url($season->ID); $fid = (int) get_post_meta($season->ID, 'cc_file', true);
        $html .= '<section class="ath-s rp-season" id="season"><h2>' . cc_ath_icon('peaks', 'ath-hic') . esc_html(cc_L('Your season', 'La tua stagione')) . '</h2>'
            . '<p class="av-lede">' . esc_html(cc_L('Your season plan: the blocks, your races and your goals. I update it whenever the plan changes; your day-to-day sessions stay in Vekta.', 'Il tuo piano di stagione: blocchi, gare e obiettivi. Lo aggiorno ogni volta che il piano cambia; gli allenamenti di ogni giorno restano su Vekta.')) . '</p>'
            . ($fid && get_post_mime_type($fid) === 'text/html' ? '<div class="rp-frame"><iframe src="' . esc_url($url) . '" title="' . esc_attr(cc_L('Your season plan', 'Il tuo piano di stagione')) . '" loading="lazy" sandbox="allow-scripts allow-popups allow-popups-to-escape-sandbox" referrerpolicy="same-origin"></iframe></div>' : '')
            . '<div class="rp-season-row"><a class="btn btn-go" href="' . esc_url($url) . '" target="_blank" rel="noopener">' . esc_html($fid && get_post_mime_type($fid) === 'text/html' ? cc_L('Open full screen', 'Apri a schermo intero') : cc_L('Open my season plan', 'Apri il mio piano di stagione')) . '</a>'
            . '<span class="rp-when">' . esc_html(cc_L('Updated ', 'Aggiornato il ') . cc_r_date($when)) . ($uid && cc_r_unseen($uid, $season->ID) ? ' <span class="rp-badge">' . esc_html(cc_L('Updated', 'Aggiornato')) . '</span>' : '') . '</span></div>'
            . ($cards !== '' ? '<h3 class="av-sub" style="margin-top:20px">' . esc_html(cc_L('Always up to date', 'Sempre aggiornati')) . '</h3><div class="ath-body rp-list">' . $cards . '</div>' : '') . '</section>';
    }
    return $html;
}, 10, 3);
function cc_r_title($p) {   // a report sent without a title is named by its kind and month, in the reader's language ("Revisão · maio 2027")
    if (!get_post_meta($p->ID, 'cc_autotitle', true)) return $p->post_title;
    return cc_r_label(get_post_meta($p->ID, 'cc_type', true)) . ' · ' . cc_r_date(strtotime(get_gmt_from_date($p->post_date) . ' UTC'), true);
}
function cc_r_card($p, $uid) {
    $t = get_post_meta($p->ID, 'cc_type', true); $new = $uid && cc_r_unseen($uid, $p->ID);
    return '<a class="ath-file rp-card' . ($new ? ' is-new' : '') . '" href="' . esc_url(cc_r_url($p->ID)) . '" target="_blank" rel="noopener">' . cc_ath_icon(CC_R_TYPES[$t][2] ?? 'doc')
        . '<span class="ath-tt"><b>' . esc_html(cc_r_title($p)) . ($new ? ' <span class="rp-badge">' . esc_html(cc_L('New', 'Nuovo')) . '</span>' : '') . '</b><small>' . esc_html((get_post_meta($p->ID, 'cc_autotitle', true) ? '' : cc_r_label($t) . ' · ') . cc_r_date((int) get_post_meta($p->ID, 'cc_published', true))) . '</small></span>'
        . '<span class="ath-dl">' . esc_html(cc_L('Open', 'Apri')) . '</span></a>';
}
add_filter('cc_ath_reports_html', function ($html, $view, $coach) {   // Matteo 17 Nov: the latest of each kind on top, earlier ones folded underneath with their dates
    if (!$view) return $html;
    $uid = (int) get_post_meta($view, 'cc_user', true); $top = ''; $old = []; $seen = []; $first = true;
    foreach (cc_r_published($view) as $p) {
        $t = get_post_meta($p->ID, 'cc_type', true);
        if ($t === 'season') { if ($first) { $first = false; continue; } $old[] = $p; continue; }   // the latest season plan is the "Your season" card
        if (in_array($t, CC_R_LIVE, true)) continue;   // prediction, snapshot: in "Your season", always the latest
        if (isset($seen[$t]) && !in_array($t, CC_R_ONTOP, true)) { $old[] = $p; continue; }   // every race plan / race simulator stays on top (one per race)
        $seen[$t] = 1; $top .= cc_r_card($p, $uid);
    }
    $o = $top ? '<div class="ath-body rp-list">' . $top . '</div>' : '';
    if ($old) { $l = ''; foreach ($old as $p) $l .= cc_r_card($p, $uid);
        $o .= '<details class="rp-old"><summary>' . esc_html(sprintf(cc_L('Earlier reports (%s)', 'Report precedenti (%s)'), count($old))) . '</summary><div class="ath-body rp-list">' . $l . '</div></details>'; }
    return $html . $o;
}, 10, 3);
add_filter('cc_ath_nav', function ($nav, $view) {
    if ($view && get_posts(['post_type' => 'cc_report', 'post_status' => 'private', 'post_parent' => $view, 'numberposts' => 1, 'fields' => 'ids', 'meta_query' => [['key' => 'cc_type', 'value' => CC_R_LIVE, 'compare' => 'IN']]]))
        array_unshift($nav, ['season', cc_L('Your season', 'La tua stagione')]);
    return $nav;
}, 30, 2);

/* ---------- Matteo: /athletes/?board=reports ---------- */
add_filter('cc_ath_coach_links', function ($html) {
    $n = count(get_posts(['post_type' => 'cc_report', 'post_status' => 'draft', 'numberposts' => -1, 'fields' => 'ids']));
    return $html . '<a class="av-boardlink" href="' . esc_url(add_query_arg('board', 'reports', home_url('/' . CC_ATH_SLUG . '/'))) . '">Reports' . ($n ? ' <span class="av-badge">' . $n . ' to review</span>' : '') . '</a>';
}, 7);
function cc_r_btn($rid, $act, $text, $go = false, $extra = '') {
    return '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" class="rf-act rp-act"><input type="hidden" name="action" value="cc_report_admin"><input type="hidden" name="rid" value="' . $rid . '">'
         . '<input type="hidden" name="act" value="' . $act . '">' . wp_nonce_field('cc_report_' . $rid, '_wpnonce', false, false) . $extra . '<button class="btn ' . ($go ? 'btn-go' : 'btn-ghost') . '"' . ($act === 'delete' ? ' onclick="return confirm(\'Delete this report for good?\')"' : '') . '>' . esc_html($text) . '</button></form>';
}
add_filter('cc_ath_board', function ($html, $board) {
    if ($board !== 'reports' || !cc_ath_is_coach()) return $html;
    cc_r_sweep();
    $o = '<section class="ath-s"><h2>' . cc_ath_icon('reports', 'ath-hic') . 'Reports</h2><p class="av-lede">Reports your PC tools send arrive here as drafts. Nothing reaches an athlete until you publish it. '
       . 'Preview, then publish (tick “Email the athlete” if you want them told by email) or delete. To add a PDF by hand, upload it inside the athlete’s page, as before.</p>';
    if (function_exists('cc_smtp_box')) $o .= cc_smtp_box();   // Matteo 17 Nov: emails through Register365 so they don't land in spam
    $o .= '<form class="rp-set" method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="cc_report_settings">' . wp_nonce_field('cc_report_settings', '_wpnonce', false, false)
        . '<label class="rp-mail"><input type="checkbox" name="race_auto" value="1"' . (get_option('cc_r_race_auto') ? ' checked' : '') . ' onchange="this.form.submit()"> <span style="flex:1;min-width:0"><b>Publish automatic pages automatically</b>: training reports, race day plans, race recaps and “Since you joined” milestones go straight into the athlete’s hub, the first one too, without waiting here (no email). Reviews, assessments and season plans always wait for you. Untick to review everything first.</span></label></form>';
    $drafts = get_posts(['post_type' => 'cc_report', 'post_status' => 'draft', 'numberposts' => -1, 'orderby' => 'date', 'order' => 'DESC']);
    $pub = get_posts(['post_type' => 'cc_report', 'post_status' => 'private', 'numberposts' => 60, 'orderby' => 'meta_value_num', 'meta_key' => 'cc_published', 'order' => 'DESC']);
    if ($drafts || $pub) $o .= '<form id="rp-bulk" class="rp-bulk" method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="cc_report_bulk">' . wp_nonce_field('cc_report_bulk', '_wpnonce', false, false)
        . '<label class="rp-mail"><input type="checkbox" id="rp-all"> Select all</label><span class="rp-acts"><button class="btn btn-go" name="act" value="publish" title="Publishes the ticked drafts, kept updated automatically, without emailing the athletes">Publish selected</button><button class="btn btn-ghost" name="act" value="unpublish">Unpublish selected</button>'
        . '<button class="btn btn-ghost rp-del" name="act" value="delete">Delete selected</button></span></form>'
        . '<script>(function(){var f=document.getElementById("rp-bulk"),a=document.getElementById("rp-all");if(!f)return;function p(){return document.querySelectorAll("input.rp-pick")}'
        . 'a.addEventListener("change",function(){p().forEach(function(c){c.checked=a.checked})});'
        . 'f.addEventListener("submit",function(e){var n=[].filter.call(p(),function(c){return c.checked}).length,d=e.submitter&&e.submitter.value==="delete";'
        . 'if(!n){e.preventDefault();alert("Tick the reports first.");return}if(d&&!confirm("Delete "+n+" report"+(n>1?"s":"")+" for good? This cannot be undone."))e.preventDefault();})})();</script>';
    $pick = function ($p) { return '<input type="checkbox" class="rp-pick" name="rids[]" value="' . $p->ID . '" form="rp-bulk" aria-label="' . esc_attr('Select ' . $p->post_title) . '">'; };
    $o .= '<h3 class="av-sub">To review</h3>';
    if (!$drafts) $o .= '<p class="av-none">Nothing waiting.</p>';
    foreach ($drafts as $p) {
        $t = get_post_meta($p->ID, 'cc_type', true); $chk = cc_r_mail_default($t) ? ' checked' : '';
        $o .= '<div class="rp-row">' . $pick($p) . '<div class="rp-what"><b>' . esc_html($p->post_title) . '</b><small>' . esc_html(get_post_field('post_title', $p->post_parent) . ' · ' . cc_r_label($t, false) . ' · sent ' . human_time_diff(strtotime(get_gmt_from_date($p->post_date) . ' UTC')) . ' ago')
            . ($t === 'season' ? ' · replaces their current season plan' : '') . '</small></div><div class="rp-acts"><a class="btn btn-ghost" href="' . esc_url(cc_r_url($p->ID)) . '" target="_blank" rel="noopener">Preview</a>'
            . cc_r_btn($p->ID, 'publish', 'Publish', true, '<label class="rp-mail"><input type="checkbox" name="mail" value="1"' . $chk . '> Email the athlete</label>'
                . (in_array($t, CC_R_AUTO, true) ? '<label class="rp-mail"><input type="checkbox" name="auto" value="1" checked> Keep it updated automatically</label>' : '')) . cc_r_btn($p->ID, 'delete', 'Delete') . '</div></div>';
    }
    if ($pub) {
        $o .= '<h3 class="av-sub" style="margin-top:22px">Published</h3>';
        foreach ($pub as $p) { $t = get_post_meta($p->ID, 'cc_type', true); $uid = (int) get_post_meta($p->post_parent, 'cc_user', true);
            $o .= '<div class="rp-row">' . $pick($p) . '<div class="rp-what"><b>' . esc_html($p->post_title) . '</b><small>' . esc_html(get_post_field('post_title', $p->post_parent) . ' · ' . cc_r_label($t, false) . ' · published ' . date_i18n('j M Y', (int) get_post_meta($p->ID, 'cc_published', true))
                . (get_post_meta($p->ID, 'cc_mailed', true) ? ' · emailed' : '') . (in_array($t, CC_R_AUTO, true) && cc_r_auto($p->post_parent, $t) ? ' · updates automatically' : '') . ($uid ? (cc_r_unseen($uid, $p->ID) ? ' · not opened yet' : ' · opened') : '')) . '</small></div><div class="rp-acts"><a class="btn btn-ghost" href="' . esc_url(cc_r_url($p->ID)) . '" target="_blank" rel="noopener">Open</a>'
                . (in_array($t, CC_R_AUTO, true) && cc_r_auto($p->post_parent, $t) ? cc_r_btn($p->ID, 'stopauto', 'Stop automatic updates') : '')
                . cc_r_btn($p->ID, 'testmail', 'Send me a test email') . cc_r_btn($p->ID, 'unpublish', 'Unpublish') . cc_r_btn($p->ID, 'delete', 'Delete') . '</div></div>'; }
    }
    return $o . '</section>';
}, 10, 2);
add_action('admin_post_cc_report_admin', function () {
    $rid = (int) ($_POST['rid'] ?? 0); $act = sanitize_key($_POST['act'] ?? '');
    if (!cc_ath_is_coach() || !wp_verify_nonce($_POST['_wpnonce'] ?? '', 'cc_report_' . $rid) || get_post_type($rid) !== 'cc_report') wp_die('Not allowed');
    if ($act === 'publish') {
        cc_r_go_live($rid); $t = get_post_meta($rid, 'cc_type', true);
        if (in_array($t, CC_R_AUTO, true)) cc_r_set_auto(get_post($rid)->post_parent, $t, !empty($_POST['auto']));
        if (!empty($_POST['mail'])) { cc_r_mail($rid); update_post_meta($rid, 'cc_mailed', time()); }
    } elseif ($act === 'stopauto') { cc_r_set_auto(get_post($rid)->post_parent, get_post_meta($rid, 'cc_type', true), false);
    } elseif ($act === 'testmail') { $me = wp_get_current_user(); if (is_email($me->user_email)) cc_r_mail($rid, $me->user_email);
    } elseif ($act === 'unpublish') { wp_update_post(['ID' => $rid, 'post_status' => 'draft']);
    } elseif ($act === 'delete') { cc_r_delete($rid); }
    wp_safe_redirect(add_query_arg('board', 'reports', home_url('/' . CC_ATH_SLUG . '/'))); exit;
});
add_action('admin_post_cc_report_settings', function () {   // Matteo 17 Nov: his switch, only he changes it
    if (!cc_ath_is_coach() || !wp_verify_nonce($_POST['_wpnonce'] ?? '', 'cc_report_settings')) wp_die('Not allowed');
    update_option('cc_r_race_auto', empty($_POST['race_auto']) ? 0 : 1, false);
    wp_safe_redirect(add_query_arg('board', 'reports', home_url('/' . CC_ATH_SLUG . '/'))); exit;
});
add_action('admin_post_cc_report_bulk', function () {   // Matteo 17 Nov: tick several, then Publish, Unpublish or Delete them together
    if (!cc_ath_is_coach() || !wp_verify_nonce($_POST['_wpnonce'] ?? '', 'cc_report_bulk')) wp_die('Not allowed');
    $act = sanitize_key($_POST['act'] ?? '');
    foreach (array_map('intval', (array) ($_POST['rids'] ?? [])) as $rid) {
        if (get_post_type($rid) !== 'cc_report') continue;
        if ($act === 'delete') { cc_r_delete($rid); } elseif ($act === 'unpublish') { wp_update_post(['ID' => $rid, 'post_status' => 'draft']); }
        elseif ($act === 'publish' && get_post_status($rid) === 'draft') {   // Matteo 17 Nov: publish many at once (no email; pages that change keep themselves updated)
            cc_r_go_live($rid); $t = get_post_meta($rid, 'cc_type', true);
            if (in_array($t, CC_R_AUTO, true)) cc_r_set_auto(get_post($rid)->post_parent, $t, true);
        }
    }
    wp_safe_redirect(add_query_arg('board', 'reports', home_url('/' . CC_ATH_SLUG . '/'))); exit;
});
function cc_r_delete($rid) { $fid = (int) get_post_meta($rid, 'cc_file', true); if ($fid) wp_delete_attachment($fid, true); wp_delete_post($rid, true); }
function cc_r_mail($rid, $test_to = null, $dry = false) {   // "your new report is ready": the branded email in the athlete's language; $test_to: Matteo's "Send me a test email" (only to him)
    $p = get_post($rid); $u = get_userdata((int) get_post_meta($p->post_parent, 'cc_user', true)); if (!$u || !is_email($u->user_email)) return;
    $GLOBALS['cc_ath_lang'] = cc_ath_user_lang($u->ID); $it = $GLOBALS['cc_ath_lang'] === 'it'; $first = esc_html($u->first_name ?: $u->display_name); $t = get_post_meta($rid, 'cc_type', true);
    $link = home_url('/' . CC_ATH_SLUG . '/') . ($t === 'season' ? '#season' : '#reports');
    $h = cc_ath_mail_shell(sprintf(cc_L('Hi %s,', 'Ciao %s,'), $first),
        cc_L('There is something new for you in your athlete hub:', 'nella tua area atleta c’è qualcosa di nuovo per te:')
          . '</p><table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:0 0 22px"><tr><td style="padding:14px 18px;border-left:3px solid #12a150;background:#f2f4f3;font-family:Montserrat,Helvetica,Arial,sans-serif">'
          . '<b style="color:#111;font-size:16px">' . esc_html(cc_r_title($p)) . '</b><br><span style="font-size:14px;color:#454a52">' . esc_html(get_post_meta($rid, 'cc_autotitle', true) ? cc_r_date((int) get_post_meta($rid, 'cc_published', true) ?: time()) : cc_r_label($t)) . '</span></td></tr></table><p style="margin:0">',
        cc_L('Open it in my hub', 'Aprilo nella mia area'), $link);
    if ($dry) return ['subject' => cc_L('Your new report is ready: ', 'È pronto il tuo nuovo report: ') . cc_r_title($p), 'html' => $h];
    $to = $test_to ?: (strpos(home_url(), '//staging.') !== false ? (string) get_option('cc_staging_notify', '') : $u->user_email);   // staging: never an athlete
    if (!is_email($to)) return;
    wp_mail($to, cc_L('Your new report is ready: ', 'È pronto il tuo nuovo report: ') . cc_r_title($p), $h,
        ['Content-Type: text/html; charset=UTF-8', 'From: Matteo Cigala <coaching@cigalacycling.com>', 'Reply-To: Matteo Cigala <matteo@cigalacycling.com>']);
}
add_action('wp_head', function () {
    if (!is_page(CC_ATH_SLUG)) return;
    echo "<style id=\"cc-reports\">html .cc .rp-new{margin:0 0 14px;padding:12px 16px;border-radius:12px;background:rgba(0,154,68,.14);border:1px solid rgba(52,196,106,.45);color:#fff;font-size:14.5px}"
       . "html .cc .rp-new b{font:400 22px/1 var(--head);color:#34c46a;margin-right:4px}html .cc .rp-new a{color:#34c46a;font-weight:600;margin-left:6px}"
       . "html .cc .rp-season{border-color:rgba(43,212,122,.4);background:linear-gradient(180deg,rgba(18,161,80,.12),rgba(13,15,17,.9) 60%)}html .cc .rp-season-row{display:flex;flex-wrap:wrap;align-items:center;gap:10px 16px}"
       . "html .cc .rp-frame{margin:0 0 14px;border-radius:12px;overflow:hidden;border:1px solid rgba(255,255,255,.1);background:#08090a}html .cc .rp-frame iframe{display:block;width:100%;height:min(80vh,860px);min-height:520px;border:0}html .cc .rp-when{font-size:13.5px;color:var(--text-3)}html .cc .rp-badge{display:inline-block;padding:2px 9px;border-radius:999px;background:#E10600;color:#fff;font:700 11px/1.6 var(--body);letter-spacing:.06em;text-transform:uppercase;vertical-align:middle}"
       . "html .cc .rp-list{margin:0 0 14px}html .cc .rp-card.is-new{border-color:rgba(52,196,106,.6)}"
       . "html .cc .rp-row{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px 16px;padding:12px 14px;margin:0 0 8px;border-radius:12px;background:rgba(255,255,255,.035);border:1px solid rgba(255,255,255,.08)}"
       . "html .cc .rp-what{display:grid;gap:2px;min-width:0;flex:1 1 220px}html .cc .rp-pick{width:20px;height:20px;accent-color:#009a44;flex:none;margin:0}html .cc .ath form.rp-bulk{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px;margin:0 0 14px;padding:10px 14px;border-radius:12px;border:1px dashed rgba(255,255,255,.14)}html .cc .rp-old{margin:4px 0 14px}html .cc .rp-old summary{cursor:pointer;color:var(--text-2);font-weight:600;font-size:14px;padding:10px 0;min-height:44px}html .cc .rp-old[open] summary{color:#fff}html .cc .rp-what b{color:#fff}html .cc .rp-what small{color:var(--text-3);font-size:12.5px}"
       . "html .cc .rp-acts{display:flex;flex-wrap:wrap;align-items:center;gap:8px}html .cc .rp-act{display:flex;align-items:center;gap:10px;margin:0}html .cc .rp-mail{display:flex;align-items:center;gap:6px;font-size:13px;color:var(--text-2);margin:0!important}"
       . "html .cc .rp-mail input{width:18px;height:18px;accent-color:#009a44}html .cc .ath form.rp-act .btn{width:auto;margin:0}html .cc .ath form.rp-bulk .btn{width:auto;margin:0;white-space:normal;min-width:0;padding-left:12px;padding-right:12px}html .cc .ath form.rp-bulk .rp-del{border-color:rgba(225,6,0,.5)}html .cc .ath form.rp-act{display:flex;flex-direction:row;align-items:center;gap:12px;margin:0}html .cc .ath .rp-acts .btn{min-height:44px;margin:0}@media (max-width:560px){html .cc .rp-acts{display:grid;grid-template-columns:1fr 1fr;width:100%}html .cc .rp-acts>.rp-act:has(.rp-mail){grid-column:1/-1;order:-1;justify-content:space-between}html .cc .rp-acts .btn,html .cc .ath form.rp-act .btn{width:100%;justify-content:center}html .cc .ath form.rp-act:not(:has(.rp-mail)){display:block}html .cc .rp-act:has(.rp-mail) .btn{width:auto;flex:1 1 auto}}</style>\n";
});
