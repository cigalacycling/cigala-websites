<?php
/* Athlete availability (Matteo, 16 Nov 2026). PLANNED, NOT ON ANY SITE YET: goes live only after Matteo's OK, staging first.
 * Part of the athlete area (athlete-area.php). tools/coaching_athlete_area.py appends this file to the same Code Snippets
 * snippet when run with --availability. Spec: README.md, "Athlete area: availability".
 *
 * Athlete side (their own area at /athletes/): a "My availability" card with
 *   - the usual week: per day the time available (rest, 30 min ... 4h+) and when (morning, lunch, evening);
 *   - changes with dates ("12-19 Dec away", "gym only on Tuesdays from next week for 10 weeks", "from 1 Dec onwards, less time"),
 *     optionally only on some weekdays, with or without an end date; dated ones drop off by themselves once over;
 *   - a free note, plus a microphone: speech is typed into the note while they talk (browser speech recognition), and the
 *     recording is kept privately (uploads/cc-private, served only to that athlete and Matteo, like the reports).
 * On save: Matteo gets an email (what changed + transcript + "listen" link). Vekta (Matteo 16 Nov): his existing Claude-Vekta
 *   connection reads GET /wp-json/cc/v1/availability twice a day and writes the notes; the website holds no Vekta key.
 * Coach side: /athletes/?board=availability shows every athlete's availability with a "changed" badge.
 * Read access for Matteo's PC tools: GET /wp-json/cc/v1/availability (application password, editor or above).
 * Never shown to athletes: plans, warnings, compliance. The card only asks and thanks.
 */
if (!defined('ABSPATH')) return;

const CC_AV_DAYS = ['mon' => 'Monday', 'tue' => 'Tuesday', 'wed' => 'Wednesday', 'thu' => 'Thursday', 'fri' => 'Friday', 'sat' => 'Saturday', 'sun' => 'Sunday'];
const CC_AV_HOURS = ['' => 'Not set', '0' => 'Rest day', '0.5' => '30 min', '1' => '1h', '1.5' => '1h 30', '2' => '2h', '3' => '3h', '4' => '4h+'];
const CC_AV_WHEN = ['am' => 'Morning', 'mid' => 'Lunch', 'pm' => 'Evening'];
const CC_AV_TYPES = ['away' => 'Away, no riding', 'bike' => 'Away, bike with me', 'less' => 'Less time', 'more' => 'More time', 'gym' => 'Gym only', 'indoor' => 'Indoor only', 'other' => 'Other'];
const CC_AV_MAX_AUDIO = 8 * 1024 * 1024;   // ~8 minutes of phone speech

/* ---------- data: kept on the athlete's page (post meta cc_avail, JSON) ---------- */
function cc_av_str($s, $max) { $s = trim(preg_replace('/\s+/u', ' ', strip_tags((string) $s))); return function_exists('mb_substr') ? mb_substr($s, 0, $max) : substr($s, 0, $max); }
function cc_av_note($s, $max) {   // keeps line breaks
    $s = str_replace("\r", '', strip_tags((string) $s)); $s = trim(preg_replace("/\n{3,}/", "\n\n", $s));
    return function_exists('mb_substr') ? mb_substr($s, 0, $max) : substr($s, 0, $max);
}
function cc_av_date($d) { return is_string($d) && preg_match('/^\d{4}-\d{2}-\d{2}$/', $d) && checkdate((int) substr($d, 5, 2), (int) substr($d, 8, 2), (int) substr($d, 0, 4)) ? $d : ''; }
// what the browser sends -> a clean record (pure PHP, tested in tools/test_availability.php)
function cc_av_clean($in, $today) {
    $in = is_array($in) ? $in : [];
    $out = ['week' => [], 'changes' => [], 'note' => cc_av_note($in['note'] ?? '', 2000)];
    foreach (CC_AV_DAYS as $k => $_) {
        $d = $in['week'][$k] ?? [];
        $h = (string) ($d['h'] ?? ''); if (!array_key_exists($h, CC_AV_HOURS)) $h = '';
        $w = array_values(array_intersect(array_keys(CC_AV_WHEN), (array) ($d['w'] ?? [])));
        $out['week'][$k] = ['h' => $h, 'w' => $h === '0' ? [] : $w];
    }
    foreach (array_slice((array) ($in['changes'] ?? []), 0, 20) as $c) {
        $from = cc_av_date($c['from'] ?? ''); if (!$from) continue;
        $open = !empty($c['open']);                                   // "from ... onwards", no end date
        $to = $open ? '' : (cc_av_date($c['to'] ?? '') ?: $from); if ($to !== '' && $to < $from) [$from, $to] = [$to, $from];
        if ($to !== '' && $to < $today) continue;                     // over: drops off
        $days = array_values(array_intersect(array_keys(CC_AV_DAYS), (array) ($c['days'] ?? [])));   // empty = every day
        if (count($days) === 7) $days = [];
        $type = isset(CC_AV_TYPES[$c['type'] ?? '']) ? $c['type'] : 'other';
        $h = (string) ($c['h'] ?? ''); if (!array_key_exists($h, CC_AV_HOURS) || $type === 'away') $h = '';
        $out['changes'][] = ['from' => $from, 'to' => $to, 'days' => $days, 'type' => $type, 'h' => $h, 'text' => cc_av_str($c['text'] ?? '', 200)];
    }
    usort($out['changes'], function ($a, $b) { return strcmp($a['from'], $b['from']); });
    return $out;
}
function cc_av_get($pid, $today = null) {
    $a = json_decode((string) get_post_meta($pid, 'cc_avail', true), true);
    if (!is_array($a)) return null;
    $today = $today ?: current_time('Y-m-d');
    $a['changes'] = array_values(array_filter($a['changes'] ?? [], function ($c) use ($today) { return ($c['to'] ?? '') === '' || $c['to'] >= $today; }));
    return $a;
}

/* ---------- words: one line per day / change, used by the email, the coach board and Vekta ---------- */
function cc_av_day_text($d) {
    if (($d['h'] ?? '') === '') return 'not set';
    if ($d['h'] === '0') return 'rest day';
    $w = array_map(function ($k) { return strtolower(CC_AV_WHEN[$k]); }, $d['w'] ?? []);
    return CC_AV_HOURS[$d['h']] . ($w ? ', ' . implode(' or ', $w) : '');
}
function cc_av_range($c) {
    $f = strtotime($c['from'] . ' 12:00');
    if (($c['to'] ?? '') === '') $r = 'From ' . date('D j M', $f) . ' onwards';
    elseif ($c['from'] === $c['to']) $r = date('D j M', $f);
    else { $t = strtotime($c['to'] . ' 12:00'); $r = date('M', $f) === date('M', $t) ? date('j', $f) . '–' . date('j M', $t) : date('j M', $f) . ' – ' . date('j M', $t); }
    if (!empty($c['days'])) $r .= ', ' . implode(', ', array_map(function ($k) { return CC_AV_DAYS[$k] . 's'; }, $c['days'])) . ' only';
    return $r;
}
function cc_av_change_text($c) {
    $t = CC_AV_TYPES[$c['type']] ?? 'Change';
    if ($c['h'] !== '' && $c['type'] !== 'away') $t .= ' (' . CC_AV_HOURS[$c['h']] . ' a day)';
    return cc_av_range($c) . ': ' . $t . ($c['text'] !== '' ? ' · ' . $c['text'] : '');
}
function cc_av_hours_week($a) {   // the athlete sees this total as a friendly number, nothing more
    $s = 0; foreach ($a['week'] ?? [] as $d) $s += (float) ($d['h'] ?? 0); return $s;
}
// what changed between two saves, in words, for Matteo's email
function cc_av_diff($old, $new) {
    $out = [];
    foreach (CC_AV_DAYS as $k => $name) {
        $o = $old ? cc_av_day_text($old['week'][$k] ?? []) : 'not set'; $n = cc_av_day_text($new['week'][$k]);
        if ($o !== $n) $out[] = "$name: $o → $n";
    }
    $oc = $old ? array_map('cc_av_change_text', $old['changes'] ?? []) : []; $nc = array_map('cc_av_change_text', $new['changes']);
    foreach (array_diff($nc, $oc) as $x) $out[] = 'New: ' . $x;
    foreach (array_diff($oc, $nc) as $x) $out[] = 'Removed: ' . $x;
    if (trim($old['note'] ?? '') !== trim($new['note'])) $out[] = 'Note updated';
    return $out;
}

/* ---------- Vekta calendar notes: which days get a note (pure PHP; tested). Reference for the PC-side sync, not called here ----------
   Changes: one note on each day they cover (only their weekdays if chosen; ongoing ones for the next 8 weeks; max 60 each).
   A new usual week: one note on the next Monday. */
function cc_av_vekta_notes($old, $new, $today) {
    $notes = [];
    foreach ($new['changes'] as $c) {
        $d = max($c['from'], $today); $n = 0; $span = 0;
        $end = ($c['to'] ?? '') !== '' ? $c['to'] : date('Y-m-d', strtotime($today . ' 12:00 +55 days'));   // ongoing: the next 8 weeks
        while ($d <= $end && $n < 60 && $span++ < 190) {
            if (empty($c['days']) || in_array(strtolower(date('D', strtotime($d . ' 12:00'))), $c['days'], true)) { $notes[$d][] = cc_av_change_text($c); $n++; }
            $d = date('Y-m-d', strtotime($d . ' 12:00 +1 day'));
        }
    }
    $weekChanged = false;
    foreach (CC_AV_DAYS as $k => $_) if (!$old || cc_av_day_text($old['week'][$k] ?? []) !== cc_av_day_text($new['week'][$k])) $weekChanged = true;
    if ($weekChanged) {
        $mon = date('Y-m-d', strtotime($today . ' 12:00 next monday'));
        $l = []; foreach (CC_AV_DAYS as $k => $name) $l[] = substr($name, 0, 3) . ' ' . cc_av_day_text($new['week'][$k]);
        $notes[$mon][] = 'Usual week from now: ' . implode('; ', $l);
    }
    ksort($notes);
    return array_map(function ($x) { return 'Availability: ' . implode(' | ', array_unique($x)); }, $notes);
}

/* ---------- saving: POST /wp-json/cc/v1/availability (the athlete, logged in; FormData: data=JSON, audio=file, transcript) ---------- */
add_action('rest_api_init', function () {
    register_rest_route('cc/v1', '/availability', [
        ['methods' => 'POST', 'callback' => 'cc_av_save', 'permission_callback' => function () { return is_user_logged_in() && (bool) cc_ath_page_of(get_current_user_id()); }],
        // read access for the coach board and Matteo's PC tools (application password): all athletes, or ?email=
        ['methods' => 'GET', 'callback' => 'cc_av_list', 'permission_callback' => 'cc_ath_is_coach'],
    ]);
});
function cc_av_save(WP_REST_Request $r) {
    $uid = get_current_user_id(); $pid = cc_ath_page_of($uid);
    $data = json_decode((string) $r->get_param('data'), true);
    if (!is_array($data)) return new WP_Error('cc_bad', 'Something went wrong. Please try again.', ['status' => 400]);
    $today = current_time('Y-m-d');
    $old = cc_av_get($pid, $today); $new = cc_av_clean($data, $today);
    $new['voice'] = array_slice($old['voice'] ?? [], -9);
    $files = $r->get_file_params();
    if (!empty($files['audio']['tmp_name'])) {
        $vid = cc_av_store_audio($files['audio'], $pid, cc_av_str($r->get_param('transcript'), 2000));
        if (is_wp_error($vid)) return $vid;
        $new['voice'][] = ['id' => $vid, 'at' => time(), 'text' => cc_av_str($r->get_param('transcript'), 2000)];
    }
    $new['updated'] = time();
    $diff = cc_av_diff($old, $new);
    if (!$diff && empty($vid)) return ['ok' => true, 'unchanged' => true];
    update_post_meta($pid, 'cc_avail', wp_slash(wp_json_encode($new)));
    update_post_meta($pid, 'cc_avail_updated', $new['updated']);
    cc_av_email($pid, $uid, $diff, $new, $vid ?? 0);
    return ['ok' => true, 'updated' => $new['updated']];
}
// the recording: into uploads/cc-private, attached to the athlete page, so the athlete-area file check guards it
function cc_av_store_audio($f, $pid, $transcript) {
    if (($f['error'] ?? 1) !== UPLOAD_ERR_OK || !is_uploaded_file($f['tmp_name'])) return new WP_Error('cc_audio', 'The voice note did not upload. Please try again.', ['status' => 400]);
    if ($f['size'] > CC_AV_MAX_AUDIO) return new WP_Error('cc_audio', 'That voice note is too long. Please keep it under 5 minutes.', ['status' => 413]);
    $mime = function_exists('mime_content_type') ? mime_content_type($f['tmp_name']) : '';
    $ext = ['audio/webm' => 'webm', 'video/webm' => 'webm', 'audio/mp4' => 'm4a', 'video/mp4' => 'm4a', 'audio/x-m4a' => 'm4a', 'audio/ogg' => 'ogg', 'audio/mpeg' => 'mp3', 'audio/wav' => 'wav', 'audio/x-wav' => 'wav'][$mime] ?? '';
    if (!$ext) return new WP_Error('cc_audio', 'That recording format is not supported.', ['status' => 415]);
    $u = wp_get_upload_dir(); $dir = $u['basedir'] . '/cc-private'; wp_mkdir_p($dir);
    $name = 'availability-' . $pid . '-' . gmdate('Ymd-His') . '-' . wp_generate_password(8, false) . '.' . $ext;
    if (!move_uploaded_file($f['tmp_name'], $dir . '/' . $name)) return new WP_Error('cc_audio', 'The voice note could not be saved.', ['status' => 500]);
    $type = $ext === 'm4a' ? 'audio/mp4' : ($ext === 'webm' ? 'audio/webm' : $mime);
    $id = wp_insert_attachment(['post_title' => 'Voice note ' . current_time('j M Y H:i'), 'post_mime_type' => $type, 'post_status' => 'inherit',
                                'post_content' => $transcript], $dir . '/' . $name, $pid);
    return is_wp_error($id) || !$id ? new WP_Error('cc_audio', 'The voice note could not be saved.', ['status' => 500]) : (int) $id;
}
function cc_av_list(WP_REST_Request $r) {
    $out = [];
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'meta_key' => 'cc_user']) as $p) {
        $u = get_userdata((int) get_post_meta($p->ID, 'cc_user', true)); if (!$u) continue;
        if ($r->get_param('email') && strcasecmp($u->user_email, $r->get_param('email'))) continue;
        $a = cc_av_get($p->ID);
        $out[] = ['athlete' => $p->post_title, 'email' => $u->user_email, 'updated' => (int) get_post_meta($p->ID, 'cc_avail_updated', true),
                  'availability' => $a ? ['week' => $a['week'], 'changes' => $a['changes'], 'note' => $a['note'],
                  'voice' => array_map(function ($v) { return ['text' => $v['text'], 'at' => $v['at'], 'url' => wp_get_attachment_url($v['id'])]; }, $a['voice'] ?? [])] : null];
    }
    return $out;
}

/* ---------- Matteo's email ---------- */
function cc_av_notify_to() {   // on staging only to the address in the option cc_staging_notify (none by default), so tests never reach Matteo
    if (defined('CC_AVAIL_NOTIFY')) return CC_AVAIL_NOTIFY;
    if (strpos(home_url(), '//staging.') !== false) return (string) get_option('cc_staging_notify', '');
    return 'info@cigalacycling.com';
}
function cc_av_email($pid, $uid, $diff, $a, $vid) {
    $u = get_userdata($uid); $name = get_post_field('post_title', $pid);
    $board = add_query_arg('board', 'availability', home_url('/' . CC_ATH_SLUG . '/')) . '#av-' . $pid;
    $e = function ($s) { return esc_html($s); };
    $logo = content_url('/uploads/2026/11/cigala-coaching-logo-v2.webp');   // the site header logo
    $h = '<div style="font:15px/1.5 Montserrat,Arial,sans-serif;color:#111;max-width:560px">'
       . '<div style="background:#08090a;padding:14px 16px;border-radius:10px;margin:0 0 18px"><img src="' . esc_url($logo) . '" alt="Cigala Cycling Coaching" width="58" height="58" style="display:block;width:58px;height:58px"></div>'
       . '<p style="margin:0 0 4px;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#E10600;font-weight:600">Athlete availability</p>'
       . '<h2 style="margin:0 0 14px;font:400 26px/1.1 Anton,Impact,sans-serif;text-transform:uppercase;color:#111">' . $e($name) . ' updated their availability</h2>';
    if ($diff) { $h .= '<p style="margin:0 0 6px"><b style="color:#111">What changed</b></p><ul style="margin:0 0 16px;padding-left:18px">'; foreach ($diff as $d) $h .= '<li>' . $e($d) . '</li>'; $h .= '</ul>'; }
    if ($vid) {
        $v = end($a['voice']);
        $h .= '<p style="margin:0 0 6px"><b style="color:#111">Voice note</b></p><blockquote style="margin:0 0 10px;padding:10px 14px;background:#f2f4f3;border-left:3px solid #009a44">' . nl2br($e($v['text'] ?: '(no words picked up, listen to the recording)')) . '</blockquote>'
            . '<p style="margin:0 0 16px"><a href="' . esc_url(wp_get_attachment_url($vid)) . '" style="color:#009a44;font-weight:600">▶ Listen to the voice note</a> (opens when you are logged in)</p>';
    }
    if ($a['note'] !== '') $h .= '<p style="margin:0 0 6px"><b style="color:#111">Note</b></p><p style="margin:0 0 16px;white-space:pre-line">' . $e($a['note']) . '</p>';
    $h .= '<p style="margin:0 0 6px"><b style="color:#111">Usual week</b></p><table style="border-collapse:collapse;margin:0 0 16px">';
    foreach (CC_AV_DAYS as $k => $d) $h .= '<tr><td style="padding:2px 14px 2px 0;color:#555">' . $d . '</td><td style="padding:2px 0">' . $e(cc_av_day_text($a['week'][$k])) . '</td></tr>';
    $h .= '</table>';
    if ($a['changes']) { $h .= '<p style="margin:0 0 6px"><b style="color:#111">Changes to the usual week</b></p><ul style="margin:0 0 16px;padding-left:18px">'; foreach ($a['changes'] as $c) $h .= '<li>' . $e(cc_av_change_text($c)) . '</li>'; $h .= '</ul>'; }
    $h .= '<p style="margin:20px 0 0"><a href="' . esc_url($board) . '" style="display:inline-block;padding:12px 20px;border-radius:8px;background:#009a44;color:#fff;font-weight:600;text-decoration:none">Open all athletes’ availability</a></p></div>';
    $headers = ['Content-Type: text/html; charset=UTF-8'];
    if ($u && is_email($u->user_email)) $headers[] = 'Reply-To: ' . $name . ' <' . $u->user_email . '>';   // reply goes straight to the athlete
    if (function_exists('cc_ath_coach_wrap')) $h = cc_ath_coach_wrap($h);   // the branded design (athlete-area.php)
    if (cc_av_notify_to()) wp_mail(cc_av_notify_to(), 'Availability: ' . $name . ($diff ? ' – ' . $diff[0] : ' – voice note'), $h, $headers);
}

/* ---------- the athlete's card (inside their area, after "Your reports") ---------- */
// the box speaks the athlete's report language (Matteo 16 Nov); Matteo's board and emails stay English
function cc_av_lang($view) { $uid = (int) get_post_meta($view, 'cc_user', true); return ($uid && function_exists('cc_ath_report_lang')) ? cc_ath_report_lang($uid) : 'en'; }
add_filter('cc_ath_nav', function ($nav, $view, $coach) { if ($view) array_splice($nav, 1, 0, [['availability', cc_av_words(cc_av_lang($view))['title']]]); return $nav; }, 10, 3);
add_filter('cc_ath_after_reports', function ($html, $view, $coach) {
    if (!$view) return $html;
    $a = cc_av_get($view);
    $data = $a ? ['week' => $a['week'], 'changes' => $a['changes'], 'note' => $a['note']] : null;
    $upd = (int) get_post_meta($view, 'cc_avail_updated', true);
    $ro = $coach && cc_ath_page_of(get_current_user_id()) !== $view;   // Matteo looking at an athlete: read only
    $lang = cc_av_lang($view); $W = cc_av_words($lang); $speech = CC_AV_SPEECH[$lang] ?? 'en-GB';
    $hours = CC_AV_HOURS; $hours[''] = $W['not_set']; $hours['0'] = $W['rest'];
    $types = []; foreach (CC_AV_TYPES as $k => $_) $types[$k] = $W[$k === 'more' ? 'more_t' : $k];
    return $html . '<section class="ath-s av" id="availability" lang="' . esc_attr($speech) . '">'
        . '<h2>' . cc_ath_icon('calendar', 'ath-hic') . esc_html($W['title']) . '</h2>'
        . '<p class="av-lede">' . esc_html($W['lede']) . '</p>'
        . '<div id="av-app" data-ro="' . ($ro ? 1 : 0) . '" data-updated="' . $upd . '" data-today="' . esc_attr(current_time('Y-m-d')) . '"'
        . ' data-api="' . esc_url(rest_url('cc/v1/availability')) . '" data-nonce="' . esc_attr(wp_create_nonce('wp_rest')) . '">'
        . '<noscript><p>' . esc_html($W['noscript']) . '</p></noscript></div>'
        . '<script type="application/json" id="av-data">' . wp_json_encode(['data' => $data, 'days' => CC_AV_DAYS, 'hours' => $hours, 'types' => $types, 'speech' => $speech,
              'when' => ['am' => $W['am'], 'mid' => $W['mid'], 'pm' => $W['pm']], 'w' => $W]) . '</script>'
        . '</section>' . cc_av_js();
}, 10, 3);

/* ---------- Matteo's board: /athletes/?board=availability ---------- */
add_filter('cc_ath_coach_links', function ($html) {
    $n = 0; $seen = (int) get_user_meta(get_current_user_id(), 'cc_avail_seen', true);
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'fields' => 'ids', 'meta_key' => 'cc_avail_updated']) as $p)
        if ((int) get_post_meta($p, 'cc_avail_updated', true) > $seen) $n++;
    return $html . '<a class="av-boardlink" href="' . esc_url(add_query_arg('board', 'availability', home_url('/' . CC_ATH_SLUG . '/'))) . '">Availability'
         . ($n ? ' <span class="av-badge">' . $n . ' changed</span>' : '') . '</a>';
});
add_filter('cc_ath_board', function ($html, $board) {
    if ($board !== 'availability' || !cc_ath_is_coach()) return $html;
    $me = get_current_user_id(); $seen = (int) get_user_meta($me, 'cc_avail_seen', true);
    $rows = [];
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'orderby' => 'title', 'order' => 'ASC', 'meta_key' => 'cc_user']) as $p) {
        $upd = (int) get_post_meta($p->ID, 'cc_avail_updated', true);
        $rows[] = [$upd > $seen ? 2 : ($upd ? 1 : 0), $upd, $p];
    }
    usort($rows, function ($x, $y) { return [$y[0], $y[1]] <=> [$x[0], $x[1]]; });   // changed first, then newest, then never filled in
    $o = '<section class="ath-s av-board"><h2>' . cc_ath_icon('calendar', 'ath-hic') . 'Availability</h2>'
       . '<p class="av-lede">Every athlete’s usual week and what is coming up. <b>Changed</b> means updated since you last opened this page.</p>'
       . '<div class="av-tbl" role="table" aria-label="Usual week per athlete"><div class="av-tr av-th" role="row"><span role="columnheader">Athlete</span>';
    foreach (CC_AV_DAYS as $k => $d) $o .= '<span role="columnheader">' . substr($d, 0, 3) . '</span>';
    $o .= '<span role="columnheader">Changes to the usual week</span></div>';
    foreach ($rows as [$state, $upd, $p]) {
        $a = cc_av_get($p->ID);
        $o .= '<div class="av-tr' . ($state === 2 ? ' is-new' : '') . '" role="row" id="av-' . $p->ID . '"><span role="cell" class="av-who"><b>' . esc_html($p->post_title) . '</b>'
            . ($state === 2 ? '<span class="av-badge">Changed</span>' : '')
            . '<small>' . ($upd ? 'Updated ' . esc_html(human_time_diff($upd) . ' ago') : 'Not filled in yet') . '</small></span>';
        foreach (CC_AV_DAYS as $k => $d) {
            $day = $a['week'][$k] ?? ['h' => '', 'w' => []];
            $o .= '<span role="cell" class="av-c av-h' . esc_attr(str_replace('.', '_', $day['h'] === '' ? 'x' : $day['h'])) . '" data-d="' . substr($d, 0, 3) . '">'
                . esc_html($day['h'] === '' ? '–' : ($day['h'] === '0' ? 'Rest' : CC_AV_HOURS[$day['h']]))
                . ($day['w'] ? '<small>' . esc_html(implode(' ', array_map(function ($w) { return ['am' => 'AM', 'mid' => 'Lunch', 'pm' => 'PM'][$w]; }, $day['w']))) . '</small>' : '') . '</span>';
        }
        $o .= '<span role="cell" class="av-up">';
        foreach ($a['changes'] ?? [] as $c) $o .= '<span class="av-chg av-' . esc_attr($c['type']) . '">' . esc_html(cc_av_change_text($c)) . '</span>';
        if (($a['note'] ?? '') !== '') $o .= '<span class="av-note">' . esc_html(wp_trim_words($a['note'], 30)) . '</span>';
        $v = !empty($a['voice']) ? end($a['voice']) : null;
        if ($v) $o .= '<a class="av-listen" href="' . esc_url(wp_get_attachment_url($v['id'])) . '" target="_blank" rel="noopener">▶ Voice note, ' . esc_html(date_i18n('j M', $v['at'])) . '</a>';
        $o .= '</span></div>';
    }
    $o .= '</div></section>';
    update_user_meta($me, 'cc_avail_seen', time());   // badges clear the next time
    return $o;
}, 10, 2);

/* ---------- the card's script and style ---------- */
function cc_av_js() {
    return <<<'JS'
<script>(function(){
var app=document.getElementById('av-app');if(!app)return;var C=JSON.parse(document.getElementById('av-data').textContent);
var ro=app.dataset.ro==='1',today=app.dataset.today,D=C.data||{week:{},changes:[],note:''},_n=D.changes.forEach(function(c){c.open=!c.to;c.days=c.days||[];}),el=function(t,a,h){var e=document.createElement(t);for(var k in a)if(a[k]!=null)e.setAttribute(k,a[k]);if(h!=null)e.innerHTML=h;return e;};
var esc=function(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});};
var dirty=false,blob=null,saved=+app.dataset.updated,W=C.w,L=C.speech,t_=function(k,o){var s=W[k];for(var x in o)s=s.split('{'+x+'}').join(o[x]);return s;};
/* day names in the athlete's language, from the browser (1 Jan 2024 was a Monday) */
var DN={},DS={};Object.keys(C.days).forEach(function(k,i){var d=new Date(2024,0,1+i);try{DN[k]=d.toLocaleDateString(L,{weekday:'long'});DS[k]=d.toLocaleDateString(L,{weekday:'short'});}catch(x){DN[k]=C.days[k];DS[k]=C.days[k].slice(0,3);}var own=W.dn&&!(window.Intl&&Intl.DateTimeFormat.supportedLocalesOf([L]).length);if(own){DN[k]=W.dn.split(',')[i];DS[k]=W.ds.split(',')[i];}
 DN[k]=DN[k].charAt(0).toUpperCase()+DN[k].slice(1);DS[k]=(DS[k].charAt(0).toUpperCase()+DS[k].slice(1)).replace(/\.$/,'');});
function opts(sel){var o='';for(var k in C.hours)o+='<option value="'+k+'"'+(k===sel?' selected':'')+'>'+esc(C.hours[k])+'</option>';return o;}
function draw(){var h='<h3 class="av-sub av-first"><span class="av-n" aria-hidden="true">1</span>'+esc(W.week_h)+'</h3><p class="av-subp">'+esc(W.week_sub)+'</p><div class="av-week" role="group" aria-label="'+esc(W.week_aria)+'">';
 for(var k in C.days){var d=D.week[k]||{h:'',w:[]};h+='<div class="av-day'+(d.h==='0'?' is-rest':'')+'" data-k="'+k+'"><label class="av-dn" for="av-h-'+k+'">'+esc(DN[k])+'</label>'
  +'<select id="av-h-'+k+'" class="av-hsel"'+(ro?' disabled':'')+'>'+opts(d.h)+'</select><div class="av-when" role="group" aria-label="'+esc(DN[k])+'">';
  for(var w in C.when)h+='<button type="button" class="av-w" data-w="'+w+'" aria-pressed="'+(d.w.indexOf(w)>-1)+'"'+(ro||d.h==='0'?' disabled':'')+'>'+esc(C.when[w])+'</button>';h+='</div></div>';}
 h+='</div><p class="av-total" aria-live="polite"></p><div class="av-part"><h3 class="av-sub"><span class="av-n" aria-hidden="true">2</span>'+esc(W.changes)+'</h3><p class="av-subp">'+esc(W.changes_sub)+'</p><div class="av-chs"></div>';
 if(!ro)h+='<button type="button" class="btn btn-ghost av-add">'+esc(W.add)+'</button>';h+='</div>';
 h+='<div class="av-part"><h3 class="av-sub"><span class="av-n" aria-hidden="true">3</span>'+esc(W.more)+'</h3><div class="av-notew"><textarea id="av-note" rows="4" placeholder="'+esc(W.note_ph)+'"'+(ro?' readonly':'')+'>'+esc(D.note||'')+'</textarea>';
 if(!ro)h+='<button type="button" class="av-mic" aria-label="'+esc(W.mic)+'" aria-pressed="false"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/></svg></button>';
 h+='</div><p class="av-rec" hidden></p></div>';
 if(!ro)h+='<div class="av-save"><button type="button" class="btn btn-go av-go" disabled>'+esc(W.save)+'</button><span class="av-msg" role="status"></span></div>';
 app.innerHTML=h;drawChanges();total();msg(saved?t_('last',{d:new Date(saved*1000).toLocaleDateString(L,{day:'numeric',month:'short'})}):'');}
function drawChanges(){var w=app.querySelector('.av-chs'),h='';
 if(!D.changes.length)h='<p class="av-none">'+esc(W.none)+'</p>';
 D.changes.forEach(function(c,i){var t='';for(var k in C.types)t+='<option value="'+k+'"'+(k===c.type?' selected':'')+'>'+esc(C.types[k])+'</option>';
  h+='<div class="av-ch av-'+c.type+'" data-i="'+i+'">'
   +'<div class="av-chr av-chw"><label>'+esc(W.what)+'<select class="av-ty"'+(ro?' disabled':'')+'>'+t+'</select></label>'
   +'<label class="av-chh"'+(c.type==='away'?' hidden':'')+'>'+esc(W.time)+'<select class="av-hh"'+(ro?' disabled':'')+'>'+opts(c.h)+'</select></label></div>'
   +'<div class="av-chr"><label>'+esc(W.from)+'<input type="date" class="av-f" value="'+c.from+'" min="'+today+'"'+(ro?' readonly':'')+'></label>'
   +'<label>'+esc(W.to)+'<input type="date" class="av-t" value="'+(c.to||'')+'" min="'+today+'"'+(c.open||ro?' disabled':'')+'></label></div>'
   +'<label class="av-open"><input type="checkbox" class="av-o"'+(c.open?' checked':'')+(ro?' disabled':'')+'> '+esc(W.open)+'</label>'
   +'<div class="av-dsel" role="group" aria-label="'+esc(W.days_aria)+'">'+Object.keys(C.days).map(function(k){return '<button type="button" class="av-w av-dw" data-d="'+k+'" aria-label="'+esc(DN[k])+'" aria-pressed="'+((c.days||[]).indexOf(k)>-1)+'"'+(ro?' disabled':'')+'>'+esc(DS[k])+'</button>';}).join('')+'</div>'
   +'<p class="av-hint">'+esc(W.hint)+'</p>'
   +'<input type="text" class="av-tx" maxlength="200" placeholder="'+esc(W.text_ph)+'" value="'+esc(c.text||'')+'"'+(ro?' readonly':'')+'>'
   +(ro?'':'<button type="button" class="av-del">'+esc(W.remove)+'</button>')+'</div>';});
 w.innerHTML=h;}
function total(){var s=0;for(var k in D.week)s+=+(D.week[k].h||0);var n=0;for(k in D.week)if(+D.week[k].h>0)n++;
 var hs=(s%1?s.toFixed(1):String(s));if(L.slice(0,2)!=='en')hs=hs.replace('.',',');
 app.querySelector('.av-total').innerHTML=s?esc(t_(n===1?'total_one':'total',{h:'\u0001'+hs+'\u0002',n:'\u0001'+n+'\u0002'})).replace(/\u0001/g,'<b>').replace(/\u0002/g,'</b>'):'';}
function msg(t,bad){var m=app.querySelector('.av-msg');if(m){m.textContent=t;m.classList.toggle('bad',!!bad);}}
function touch(){dirty=true;var b=app.querySelector('.av-go');if(b)b.disabled=false;msg('');}
app.addEventListener('change',function(e){var t=e.target,day=t.closest('.av-day'),ch=t.closest('.av-ch');
 if(day&&t.classList.contains('av-hsel')){var k=day.dataset.k;D.week[k]=D.week[k]||{h:'',w:[]};D.week[k].h=t.value;var r=t.value==='0';if(r)D.week[k].w=[];
  day.classList.toggle('is-rest',r);day.querySelectorAll('.av-w').forEach(function(b){b.disabled=r;if(r)b.setAttribute('aria-pressed','false');});total();touch();return;}
 if(ch){var c=D.changes[+ch.dataset.i];if(t.classList.contains('av-f')){c.from=t.value;if(!c.open&&(!c.to||c.to<c.from))c.to=c.from;}if(t.classList.contains('av-t'))c.to=t.value;
  if(t.classList.contains('av-hh'))c.h=t.value;if(t.classList.contains('av-o')){c.open=t.checked;if(c.open)c.to='';else c.to=c.from;ch.querySelector('.av-t').disabled=c.open;ch.querySelector('.av-t').value=c.to;}if(t.classList.contains('av-ty')){c.type=t.value;if(c.type==='away')c.h='';drawChanges();}else if(t.classList.contains('av-f')&&!c.open)ch.querySelector('.av-t').value=c.to;touch();}});
app.addEventListener('input',function(e){if(e.target.id==='av-note'){D.note=e.target.value;touch();}if(e.target.classList.contains('av-tx')){D.changes[+e.target.closest('.av-ch').dataset.i].text=e.target.value;touch();}});
app.addEventListener('click',function(e){var b=e.target.closest('button');if(!b||ro)return;
 if(b.classList.contains('av-dw')){var c=D.changes[+b.closest('.av-ch').dataset.i],dd=c.days=c.days||[],j=dd.indexOf(b.dataset.d);if(j>-1)dd.splice(j,1);else dd.push(b.dataset.d);b.setAttribute('aria-pressed',j<0);touch();return;}
 if(b.classList.contains('av-w')){var k=b.closest('.av-day').dataset.k,d=D.week[k]=D.week[k]||{h:'',w:[]},w=b.dataset.w,i=d.w.indexOf(w);if(i>-1)d.w.splice(i,1);else d.w.push(w);b.setAttribute('aria-pressed',i<0);touch();}
 if(b.classList.contains('av-add')){D.changes.push({from:today,to:today,open:false,days:[],type:'away',h:'',text:''});drawChanges();touch();var l=app.querySelectorAll('.av-ch');l[l.length-1].querySelector('.av-f').focus();}
 if(b.classList.contains('av-del')){D.changes.splice(+b.closest('.av-ch').dataset.i,1);drawChanges();touch();}
 if(b.classList.contains('av-mic'))mic(b);
 if(b.classList.contains('av-go'))save(b);});
/* voice: record for Matteo + type the words into the note while they speak */
var rec=null,sr=null,chunks=[],base='',t0=0,tick=null;
function mic(b){if(rec){rec.stop();return;}
 if(!navigator.mediaDevices||!window.MediaRecorder){msg(W.mic_no,true);return;}
 navigator.mediaDevices.getUserMedia({audio:true}).then(function(st){
  var type=['audio/webm;codecs=opus','audio/mp4','audio/webm'].filter(function(t){return MediaRecorder.isTypeSupported&&MediaRecorder.isTypeSupported(t);})[0];
  rec=new MediaRecorder(st,type?{mimeType:type,audioBitsPerSecond:32000}:undefined);chunks=[];rec.ondataavailable=function(e){if(e.data.size)chunks.push(e.data);};
  rec.onstop=function(){st.getTracks().forEach(function(t){t.stop();});blob=new Blob(chunks,{type:rec.mimeType||'audio/mp4'});rec=null;if(sr)try{sr.stop();}catch(x){}
   clearInterval(tick);b.setAttribute('aria-pressed','false');b.classList.remove('on');var r=app.querySelector('.av-rec');r.hidden=false;
   r.innerHTML=esc(t_('rec_ready',{s:Math.round((Date.now()-t0)/1000)}))+' <button type="button" class="av-x">'+esc(W.rec_del)+'</button>';
   r.querySelector('.av-x').onclick=function(){blob=null;r.hidden=true;};touch();};
  rec.start(1000);t0=Date.now();b.setAttribute('aria-pressed','true');b.classList.add('on');var r=app.querySelector('.av-rec');r.hidden=false;
  tick=setInterval(function(){var s=Math.round((Date.now()-t0)/1000);r.textContent=t_('listening',{s:s});if(s>=300)rec&&rec.stop();},500);
  var SR=window.SpeechRecognition||window.webkitSpeechRecognition,ta=document.getElementById('av-note');base=ta.value?ta.value.replace(/\s*$/,'')+'\n':'';
  if(SR){sr=new SR();sr.lang=L;sr.continuous=true;sr.interimResults=true;
   sr.onresult=function(e){var s='';for(var i=0;i<e.results.length;i++)s+=e.results[i][0].transcript;ta.value=base+s.trim();D.note=ta.value;};
   sr.onend=function(){if(rec)try{sr.start();}catch(x){}};sr.onerror=function(){};try{sr.start();}catch(x){}}
 }).catch(function(){msg(W.mic_denied,true);});}
function save(b){b.disabled=true;msg(W.saving);var f=new FormData(),txt=document.getElementById('av-note').value;
 f.append('data',JSON.stringify({week:D.week,changes:D.changes,note:D.note}));
 if(blob){f.append('audio',blob,'voice.'+(/mp4/.test(blob.type)?'m4a':'webm'));f.append('transcript',txt.slice(base.length));}
 fetch(app.dataset.api,{method:'POST',body:f,credentials:'same-origin',headers:{'X-WP-Nonce':app.dataset.nonce}}).then(function(r){return r.json().then(function(j){return[r.ok,j];});})
 .then(function(x){if(!x[0])throw new Error(x[1].message||'');dirty=false;blob=null;var r=app.querySelector('.av-rec');r.hidden=true;
  msg(x[1].unchanged?W.nothing:W.saved);b.disabled=true;})
 .catch(function(){b.disabled=false;msg(W.err,true);});}
addEventListener('beforeunload',function(e){if(dirty&&!ro){e.preventDefault();e.returnValue='';}});
draw();})();</script>
JS;
}
add_action('wp_head', function () {
    if (!is_page(CC_ATH_SLUG)) return;
    echo <<<'CSS'
<style id="cc-availability">
html .cc .av-lede { color: var(--text-2); margin: -4px 0 18px; }
html .cc .av-week { display: grid; gap: 8px; }
html .cc .av-day { display: grid; grid-template-columns: 110px 130px 1fr; align-items: center; gap: 12px; padding: 10px 12px; border-radius: 12px; background: rgba(255,255,255,.035); border: 1px solid rgba(255,255,255,.08); }
html .cc .av-day.is-rest { opacity: .7; }
html .cc .av-dn { margin: 0 !important; font-weight: 600; font-size: 15px; color: #fff; }
html .cc .ath select, html .cc .ath textarea, html .cc .ath input[type=date], html .cc .ath .av-tx { width: 100%; box-sizing: border-box; font: 16px var(--body); padding: 10px 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,.18); background: #0b0d0f; color: #fff; color-scheme: dark; }
html .cc .ath :is(select, textarea, input):focus-visible { outline: 2px solid var(--green, #009a44); outline-offset: 1px; }
html .cc .av-when { display: flex; flex-wrap: wrap; gap: 6px; }
html .cc .av-w { font: 600 13px var(--body); padding: 9px 13px; min-height: 40px; border-radius: 999px; border: 1px solid rgba(255,255,255,.16); background: transparent; color: var(--text-2); cursor: pointer; }
html .cc .av-w[aria-pressed=true] { background: #009a44; border-color: #009a44; color: #fff; }
html .cc .av-w:disabled { opacity: .35; cursor: default; }
html .cc .av-total { min-height: 1.4em; margin: 12px 0 0; color: var(--text-2); font-size: 14px; }
html .cc .av-total b { color: var(--green-text, #34c46a); font-weight: 700; }
html .cc .ath .av-sub { display: flex; align-items: center; gap: 10px; font: 700 13px var(--body); letter-spacing: .12em; text-transform: uppercase; color: var(--red-text, #ff3d33); margin: 0 0 6px; }
html .cc .av-n { flex: none; display: grid; place-items: center; width: 26px; height: 26px; border-radius: 50%; background: #009a44; color: #fff; font: 700 13px/1 var(--body); letter-spacing: 0; }
html .cc .av-subp { margin: 0 0 14px 36px; color: var(--text-3); font-size: 14px; }
html .cc .av-part { margin-top: 30px; padding-top: 26px; border-top: 1px solid rgba(255,255,255,.1); }
html .cc .av-none { color: var(--text-3); font-size: 14px; margin: 0 0 12px; }
html .cc .av-ch { display: grid; gap: 10px; padding: 14px; margin: 0 0 10px; border-radius: 12px; border: 1px solid rgba(255,255,255,.1); border-left: 3px solid #8a8f98; background: rgba(255,255,255,.03); }
html .cc .av-ch.av-away { border-left-color: #E10600; } html .cc .av-ch.av-less { border-left-color: #b9895a; } html .cc .av-ch.av-more { border-left-color: #009a44; } html .cc .av-ch:is(.av-gym, .av-indoor) { border-left-color: #d0d6e0; }
html .cc .av-chr { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 10px; }
html .cc .av-ch label > * { min-width: 0; }
html .cc .av-ch label { display: grid; gap: 5px; margin: 0; font-size: 12.5px; color: var(--text-3); font-weight: 600; }
html .cc .av-open { display: flex !important; align-items: center; gap: 8px !important; font-size: 14px !important; color: var(--text-2) !important; font-weight: 500 !important; }
html .cc .av-open input { width: 18px; height: 18px; accent-color: #009a44; }
html .cc .av-dsel { display: grid; grid-template-columns: repeat(7, minmax(0, 1fr)); gap: 5px; } html .cc .av-dsel .av-w { padding: 8px 0; min-height: 38px; font-size: 12.5px; }
html .cc .av-chw { grid-template-columns: minmax(0, 1.3fr) minmax(0, 1fr) !important; }
html .cc .av-hint { font-size: 12.5px; color: var(--text-3); margin: -4px 0 0; }
html .cc .av-del, html .cc .av-x { justify-self: start; background: none; border: 0; padding: 4px 0; color: var(--text-3); font: 13px var(--body); text-decoration: underline; cursor: pointer; }
html .cc .av-add { margin: 0; max-width: 100%; white-space: normal; height: auto; text-align: center; }
html .cc .av-notew { position: relative; }
html .cc .av-notew textarea { padding-right: 64px; resize: vertical; min-height: 110px; line-height: 1.5; }
html .cc .av-mic { position: absolute; right: 10px; bottom: 12px; width: 46px; height: 46px; border-radius: 50%; border: 0; background: #009a44; display: grid; place-items: center; cursor: pointer; box-shadow: 0 6px 18px rgba(0,154,68,.35); }
html .cc .av-mic svg { width: 22px; height: 22px; fill: none; stroke: #fff; stroke-width: 2; stroke-linecap: round; }
html .cc .av-mic.on { background: #E10600; box-shadow: 0 0 0 0 rgba(225,6,0,.5); animation: av-pulse 1.4s infinite; }
@keyframes av-pulse { 70% { box-shadow: 0 0 0 14px rgba(225,6,0,0); } 100% { box-shadow: 0 0 0 0 rgba(225,6,0,0); } }
html .cc .av-rec { margin: 10px 0 0; font-size: 14px; color: var(--text-2); }
html .cc .av-save { display: flex; flex-wrap: wrap; align-items: center; gap: 14px; margin: 22px 0 0; }
html .cc .av-go:disabled { opacity: .5; cursor: default; }
html .cc .av-msg { font-size: 14px; color: var(--green-text, #34c46a); } html .cc .av-msg.bad { color: var(--red-text, #ff3d33); }
/* coach board */
html .cc .av-boardlink { display: inline-flex; align-items: center; gap: 8px; margin-top: 10px; color: #fff; font-weight: 600; font-size: 14px; }
html .cc .av-badge { display: inline-block; padding: 2px 9px; border-radius: 999px; background: #E10600; color: #fff; font: 700 11px/1.6 var(--body); letter-spacing: .06em; text-transform: uppercase; }
html .cc .av-tbl { display: grid; gap: 6px; font-size: 13px; }
html .cc .av-tr { display: grid; grid-template-columns: 150px repeat(7, minmax(40px, 1fr)) minmax(160px, 2fr); gap: 4px; align-items: start; padding: 8px; border-radius: 12px; background: rgba(255,255,255,.03); border: 1px solid rgba(255,255,255,.07); scroll-margin-top: 110px; }
html .cc .av-tr.is-new { border-color: rgba(225,6,0,.55); background: rgba(225,6,0,.06); }
html .cc .av-th { background: none; border: 0; color: var(--text-3); font-weight: 600; text-transform: uppercase; letter-spacing: .08em; font-size: 11px; padding-block: 0; }
html .cc .av-who { display: grid; gap: 3px; align-content: start; justify-items: start; } html .cc .av-who b { color: #fff; font-size: 14px; } html .cc .av-who small, html .cc .av-c small { color: var(--text-3); font-size: 11px; }
html .cc .av-c { display: grid; align-content: center; justify-items: center; text-align: center; min-height: 46px; padding: 6px 2px; border-radius: 8px; background: rgba(0,154,68,.18); color: #fff; font-weight: 600; }
html .cc .av-c.av-hx { background: transparent; color: var(--text-3); } html .cc .av-c.av-h0 { background: rgba(255,255,255,.05); color: var(--text-3); }
html .cc .av-c:is(.av-h2, .av-h3, .av-h4) { background: rgba(0,154,68,.42); }
html .cc .av-up { display: grid; gap: 4px; align-content: start; color: var(--text-2); }
html .cc .av-chg { padding-left: 8px; border-left: 3px solid #8a8f98; } html .cc .av-chg.av-away { border-color: #E10600; } html .cc .av-chg.av-less { border-color: #b9895a; } html .cc .av-chg.av-more { border-color: #009a44; } html .cc .av-chg:is(.av-gym, .av-indoor) { border-color: #d0d6e0; }
html .cc .av-note { font-style: italic; color: var(--text-3); } html .cc .av-listen { color: var(--green-text, #34c46a); font-weight: 600; }
html .cc .av-vk { color: var(--text-3); font-size: 11px; } html .cc .av-vk-error { color: var(--red-text, #ff3d33); }
@media (max-width: 760px) {
  html .cc .av-day { grid-template-columns: 1fr 120px; gap: 8px 10px; }
  html .cc .av-when { grid-column: 1 / -1; } html .cc .av-w { flex: 1; }
  html .cc .av-th { display: none; }
  html .cc .av-tr { grid-template-columns: repeat(7, 1fr); }
  html .cc .av-who, html .cc .av-up { grid-column: 1 / -1; }
  html .cc .av-c::before { content: attr(data-d); font-size: 10px; color: var(--text-3); font-weight: 600; text-transform: uppercase; }
  html .cc .av-c { font-size: 12px; padding: 5px 0; }
}
</style>
CSS;
});
