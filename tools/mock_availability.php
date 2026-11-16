<?php
/* Renders the availability card, Matteo's board and his email from the real code with sample data, for the mock-up.
   php tools/mock_availability.php > coaching/athlete-area/mockup/parts.json   (used by tools/build_availability_mockup.py) */
define('ABSPATH', '/'); $H = [];
function add_action($h, $f, $p = 10) { global $H; $H[$h][] = $f; } function add_filter($h, $f, $p = 10) { global $H; $H[$h][] = $f; }
function add_shortcode() {} function remove_shortcode() {}
function run($h, ...$a) { global $H; $v = $a[0]; foreach ($H[$h] ?? [] as $f) { $a[0] = $v; $v = $f(...$a); } return $v; }
date_default_timezone_set('Europe/Dublin'); $NOW = strtotime('2026-11-18 09:30');
function current_time($f) { global $NOW; return date($f, $NOW); }
function esc_html($s) { return htmlspecialchars((string) $s, ENT_QUOTES); } function esc_attr($s) { return esc_html($s); } function esc_url($s) { return esc_html($s); }
function wp_json_encode($x) { return json_encode($x, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_HEX_TAG); } function wp_slash($s) { return $s; }
function rest_url($p) { return '/wp-json/' . $p; } function wp_create_nonce() { return 'mock'; } function home_url($p = '') { return 'https://coaching.cigalacycling.com' . $p; }
function add_query_arg($k, $v, $u) { return $u . '?' . $k . '=' . $v; } function current_user_can() { return true; } function get_current_user_id() { return 1; }
function is_user_logged_in() { return false; } function is_page() { return true; } function sanitize_key($s) { return $s; } function wp_trim_words($s, $n) { return $s; }
function human_time_diff($t) { global $NOW; $m = round(($NOW - $t) / 60); return $m < 60 ? "$m mins" : ($m < 1440 ? round($m / 60) . ' hours' : (($d = round($m / 1440)) == 1 ? '1 day' : "$d days")); }
function date_i18n($f, $t) { return date($f, $t); } function wp_get_attachment_url($id) { return '#voice-' . $id; }
function get_user_meta() { global $NOW; return $NOW - 3 * 86400; } function update_user_meta() {}
function content_url($p) { return 'LOGO_URL'; } function is_email() { return true; } function get_userdata($id) { return (object) ['user_email' => 'athlete@example.com']; }
$MAIL = null; function wp_mail($to, $sub, $body) { global $MAIL; $MAIL = ['to' => $to, 'subject' => $sub, 'html' => $body]; }
// sample athletes (made up for the mock-up)
$P = [101 => 'Anna Rossi', 102 => 'Ciarán Byrne', 103 => 'James Walsh', 104 => 'Sophie Martin'];
$wk = function ($m, $t, $w, $th, $f, $sa, $su) { $o = []; foreach (['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'] as $i => $k) { $x = func_get_args()[$i]; $o[$k] = ['h' => $x[0], 'w' => $x[1]]; } return $o; };
$META = [
 101 => ['cc_avail_updated' => $NOW - 2 * 3600, 'cc_avail' => ['week' => $wk(['1', ['pm']], ['1.5', ['am']], ['0', []], ['1.5', ['am']], ['1', ['mid']], ['4', ['am']], ['3', ['am']]),
         'changes' => [['from' => '2026-11-27', 'to' => '2026-11-29', 'type' => 'less', 'h' => '1', 'text' => 'Work trip to Milan, hotel gym only'], ['from' => '2026-11-24', 'to' => '2027-01-26', 'days' => ['tue'], 'type' => 'gym', 'h' => '1', 'text' => 'Strength block, 10 weeks'], ['from' => '2026-12-20', 'to' => '2026-12-28', 'type' => 'away', 'h' => '', 'text' => 'Christmas with family in Sicily']],
         'note' => 'Saturdays I ride with the club, so the long ride works best then.', 'voice' => [['id' => 9001, 'at' => $NOW - 7200, 'text' => 'Next weekend I am in Milan for work, only the hotel gym.']]],
         'cc_avail_vekta' => ['state' => 'ok']],
 102 => ['cc_avail_updated' => $NOW - 26 * 3600, 'cc_avail' => ['week' => $wk(['0', []], ['1', ['pm']], ['1', ['pm']], ['1', ['pm']], ['0', []], ['3', ['am']], ['2', ['am']]), 'changes' => [], 'note' => '']],
 103 => ['cc_avail_updated' => $NOW - 9 * 86400, 'cc_avail' => ['week' => $wk(['1', ['am']], ['1', ['am']], ['1', ['am']], ['1', ['am']], ['0', []], ['2', ['am']], ['2', ['am']]),
         'changes' => [['from' => '2026-12-01', 'to' => '', 'type' => 'less', 'h' => '1', 'days' => ['mon', 'tue', 'wed', 'thu'], 'text' => 'New job, early starts'], ['from' => '2026-12-05', 'to' => '2026-12-05', 'type' => 'more', 'h' => '4', 'text' => 'Day off work']], 'note' => '']],
 104 => [],
];
function get_post_meta($id, $k) { global $META; $v = $META[$id][$k] ?? ''; return is_array($v) ? json_encode($v) : $v; }
function update_post_meta() {} function get_the_title($id) { global $P; return $P[$id]; }
function get_posts($q) { global $P, $META; $o = []; foreach ($P as $id => $t) { if (($q['meta_key'] ?? '') === 'cc_avail_updated' && empty($META[$id]['cc_avail_updated'])) continue; $o[] = ($q['fields'] ?? '') === 'ids' ? $id : (object) ['ID' => $id, 'post_title' => $t]; } return $o; }
require __DIR__ . '/../coaching/athlete-area/athlete-area.php';
require __DIR__ . '/../coaching/athlete-area/availability.php';
$out = [];
$out['card'] = run('cc_ath_after_reports', '', 101, false);
$out['card_new'] = (function () { global $META; $keep = $META[101]; $META[101] = []; $h = run('cc_ath_after_reports', '', 101, false); $META[101] = $keep; return $h; })();
$out['links'] = run('cc_ath_coach_links', '');
$out['board'] = run('cc_ath_board', '', 'availability');
$old = cc_av_get(101); $new = $old; $new['week']['wed'] = ['h' => '1', 'w' => ['pm']];
$new['changes'][] = ['from' => '2026-12-06', 'to' => '2026-12-06', 'type' => 'away', 'h' => '', 'text' => 'Wedding'];
$new['note'] = $old['note'] . "\nNext weekend I am in Milan for work, only the hotel gym.";
$v = $old['voice']; $new = cc_av_clean($new, current_time('Y-m-d')); $new['voice'] = $v;
cc_av_email(101, 5, cc_av_diff($old, $new), $new, 9001);
$out['email'] = $MAIL;
$out['head'] = (function () { global $H; ob_start(); foreach ($H['wp_head'] as $f) $f(); return ob_get_clean(); })();
echo json_encode($out, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
