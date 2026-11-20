<?php
if (!defined('ABSPATH')) return;
/* ---------- Next week: Matteo's weekly plan review, in the hub (Matteo, 20 Nov 2026) ----------
 * Replaces the private claude.ai artifact "Weekly Athlete Plan" as the place where he reviews next week (the artifact stays as a fallback).
 * COACH ONLY: every route and the board check cc_ath_is_coach(). Athletes and the nutritionist never see any of it.
 * Data, all from Matteo's laptop (his Vekta key never leaves it):
 *  - POST /wp-json/cc/v1/week-plan {week: Monday, plan}: the week Claude drafted on Sunday (plans\working-WEEK.json, posted by
 *    vekta\hub\week_plan.py). Same week replaces it; the last 8 weeks are kept. GET /cc/v1/week-plan[?week=] reads it back.
 *  - POST /wp-json/cc/v1/week-daily {data}: each morning, per rider: Matteo's sessions in Vekta this week and next week (visible =
 *    planned, hidden = drafts), races in the next 14 days with A/B/C, Load-8/Load-2/Strain and the "ramping too fast" flag
 *    (vekta\hub\week_daily.py, no Claude). GET /cc/v1/week-daily reads it back.
 *  - Matteo's review, per rider and week: POST /cc/v1/week-review {week, uid, decision approve|change|hold|'', comment, days {date: text}}
 *    or {week, notes} for the whole week; the server stamps updatedAt (ISO UTC). Claude's side: POST /cc/v1/week-reply
 *    {week, uid, reply, outcome, handledAt}. GET /cc/v1/week-review?week= gives both, in the shape the artifact database had
 *    (plans\PLAN-REVIEW.md). Nothing here writes to Vekta: "Create as drafts" is his intent, Claude still asks for a yes in chat.
 * Board: ?board=week[&wk=YYYY-MM-DD]. */

function cc_wk_plans() { $p = get_option('cc_wk_plans', []); return is_array($p) ? $p : []; }
function cc_wk_reviews() { $r = get_option('cc_wk_review', []); return is_array($r) ? $r : []; }
function cc_wk_daily() { $d = get_option('cc_wk_daily', []); return is_array($d) ? $d : []; }
function cc_wk_now() { return gmdate('Y-m-d\TH:i:s') . '.000Z'; }
function cc_wk_is_week($w) { return is_string($w) && preg_match('/^\d{4}-\d{2}-\d{2}$/', $w) && strtotime($w . ' 12:00:00'); }
function cc_wk_url($wk = '') { $a = ['board' => 'week']; if ($wk !== '') $a['wk'] = $wk; return add_query_arg($a, home_url('/' . CC_ATH_SLUG . '/')); }
function cc_wk_clean($v, $depth = 0) {
    if ($depth > 8) return null;
    if (is_array($v)) { $o = []; foreach ($v as $k => $x) { $k = is_int($k) ? $k : sanitize_text_field((string) $k); $o[$k] = cc_wk_clean($x, $depth + 1); } return $o; }
    if (is_string($v)) return mb_substr(sanitize_textarea_field($v), 0, 4000);
    if (is_bool($v) || is_int($v) || is_float($v) || $v === null) return $v;
    return null;
}
/* the next Monday after today (Irish time), as the laptop computes it */
function cc_wk_next_monday() { $t = new DateTime('now', wp_timezone()); $t->modify('+' . (8 - (int) $t->format('N')) . ' days'); return $t->format('Y-m-d'); }
function cc_wk_this_monday() { $t = new DateTime('now', wp_timezone()); $t->modify('-' . ((int) $t->format('N') - 1) . ' days'); return $t->format('Y-m-d'); }
function cc_wk_review_of($week) { $r = cc_wk_reviews(); $w = $r[$week] ?? []; return ['athletes' => (array) ($w['athletes'] ?? []), 'notes' => (string) ($w['notes'] ?? ''), 'notesUpdatedAt' => (string) ($w['notesUpdatedAt'] ?? '')]; }
function cc_wk_label($d) {
    if (!$d) return ['Not reviewed', ''];
    $up = (string) ($d['updatedAt'] ?? ''); $h = (string) ($d['handledAt'] ?? '');
    $waiting = $up !== '' && ($h === '' || strcmp($up, $h) > 0);
    if (!empty($d['outcome']) && !$waiting) return [(string) $d['outcome'], 'done'];
    $dec = (string) ($d['decision'] ?? '');
    if ($dec === 'approve') return [$waiting ? 'Create as drafts: waiting for Claude' : 'Approved', $waiting ? 'wait' : 'approve'];
    if ($dec === 'hold') return ['On hold', ''];
    if ($waiting && ($dec === 'change' || !empty($d['comment']) || array_filter((array) ($d['days'] ?? [])))) return ['Change asked: waiting for Claude', 'wait'];
    if ($h !== '') return ['Revised by Claude', 'done'];
    return ['Not reviewed', ''];
}
/* how many draft weeks still wait for Matteo (badge on the coach tools link) */
function cc_wk_open_count() {
    $p = cc_wk_plans(); if (!$p) return 0;
    $w = cc_wk_next_monday(); if (!isset($p[$w])) return 0;
    $rv = cc_wk_review_of($w)['athletes']; $n = 0;
    foreach ((array) ($p[$w]['athletes'] ?? []) as $a) if (!empty($a['rows']) && empty($rv[$a['userId'] ?? '']['decision'])) $n++;
    return $n;
}

add_action('rest_api_init', function () {
    $coach = 'cc_ath_is_coach';
    register_rest_route('cc/v1', '/week-plan', [
        ['methods' => 'POST', 'permission_callback' => $coach, 'callback' => function (WP_REST_Request $r) {
            $week = (string) $r['week']; $plan = $r['plan'];
            if (!cc_wk_is_week($week)) return new WP_Error('cc_wk_week', 'week must be YYYY-MM-DD (a Monday).', ['status' => 400]);
            if (!is_array($plan) || !isset($plan['athletes'])) return new WP_Error('cc_wk_plan', 'No plan.', ['status' => 400]);
            if (strlen(wp_json_encode($plan)) > 1500000) return new WP_Error('cc_wk_big', 'Plan too large.', ['status' => 413]);
            $p = cc_wk_plans(); $plan = cc_wk_clean($plan); $plan['postedAt'] = time(); $p[$week] = $plan;
            krsort($p); $p = array_slice($p, 0, 8, true);
            update_option('cc_wk_plans', $p, false);
            return ['ok' => true, 'week' => $week, 'athletes' => count((array) $plan['athletes']), 'board' => cc_wk_url($week)];
        }],
        ['methods' => 'GET', 'permission_callback' => $coach, 'callback' => function (WP_REST_Request $r) {
            $p = cc_wk_plans(); $w = (string) ($r['week'] ?? '');
            return ['weeks' => array_keys($p), 'plan' => ($w !== '' ? ($p[$w] ?? null) : null)];
        }],
    ]);
    register_rest_route('cc/v1', '/week-daily', [
        ['methods' => 'POST', 'permission_callback' => $coach, 'callback' => function (WP_REST_Request $r) {
            $d = $r['data'];
            if (!is_array($d) || !isset($d['athletes']) || !cc_wk_is_week((string) ($d['nextWeek'] ?? ''))) return new WP_Error('cc_wk_daily', 'Bad data.', ['status' => 400]);
            if (strlen(wp_json_encode($d)) > 800000) return new WP_Error('cc_wk_big', 'Too large.', ['status' => 413]);
            $d = cc_wk_clean($d); $d['postedAt'] = time();
            update_option('cc_wk_daily', $d, false);
            return ['ok' => true, 'athletes' => count((array) $d['athletes']), 'board' => cc_wk_url()];
        }],
        ['methods' => 'GET', 'permission_callback' => $coach, 'callback' => function () { return cc_wk_daily(); }],
    ]);
    register_rest_route('cc/v1', '/week-review', [
        ['methods' => 'GET', 'permission_callback' => $coach, 'callback' => function (WP_REST_Request $r) {
            $w = (string) $r['week']; if (!cc_wk_is_week($w)) return new WP_Error('cc_wk_week', 'week=YYYY-MM-DD', ['status' => 400]);
            return ['week' => $w] + cc_wk_review_of($w);
        }],
        /* Matteo's own clicks on the board */
        ['methods' => 'POST', 'permission_callback' => $coach, 'callback' => function (WP_REST_Request $r) {
            $w = (string) $r['week']; if (!cc_wk_is_week($w)) return new WP_Error('cc_wk_week', 'week=YYYY-MM-DD', ['status' => 400]);
            $all = cc_wk_reviews(); $wk = $all[$w] ?? ['athletes' => []]; $now = cc_wk_now();
            if ($r->has_param('notes') && !$r->has_param('uid')) {
                $wk['notes'] = mb_substr(sanitize_textarea_field((string) $r['notes']), 0, 4000); $wk['notesUpdatedAt'] = $now;
                $all[$w] = $wk; update_option('cc_wk_review', $all, false);
                return ['ok' => true, 'notes' => $wk['notes'], 'notesUpdatedAt' => $now];
            }
            $uid = sanitize_text_field((string) $r['uid']);
            if (!preg_match('/^[A-Za-z0-9_-]{4,64}$/', $uid)) return new WP_Error('cc_wk_uid', 'Bad athlete id.', ['status' => 400]);
            $doc = (array) ($wk['athletes'][$uid] ?? ['decision' => '', 'comment' => '', 'days' => []]);
            if ($r->has_param('decision')) { $dv = (string) $r['decision']; if (!in_array($dv, ['', 'approve', 'change', 'hold'], true)) return new WP_Error('cc_wk_dec', 'Bad decision.', ['status' => 400]); $doc['decision'] = $dv; }
            if ($r->has_param('comment')) $doc['comment'] = mb_substr(sanitize_textarea_field((string) $r['comment']), 0, 3000);
            if ($r->has_param('days')) {
                $days = [];
                foreach ((array) $r['days'] as $k => $t) { $t = trim(mb_substr(sanitize_text_field((string) $t), 0, 500)); if (cc_wk_is_week((string) $k) && $t !== '') $days[(string) $k] = $t; }
                $doc['days'] = (object) $days;
            }
            $doc['updatedAt'] = $now; $doc['week'] = $w; if ($r->has_param('name')) $doc['name'] = sanitize_text_field((string) $r['name']);
            $wk['athletes'][$uid] = $doc; $all[$w] = $wk;
            krsort($all); update_option('cc_wk_review', array_slice($all, 0, 12, true), false);
            [$t, $k] = cc_wk_label($doc);
            return ['ok' => true, 'doc' => $doc, 'label' => $t, 'k' => $k];
        }],
    ]);
    /* Claude's side ("process my plan review"): never touches Matteo's decision, comment or day edits */
    register_rest_route('cc/v1', '/week-reply', ['methods' => 'POST', 'permission_callback' => $coach, 'callback' => function (WP_REST_Request $r) {
        $w = (string) $r['week']; $uid = sanitize_text_field((string) $r['uid']);
        if (!cc_wk_is_week($w) || !preg_match('/^[A-Za-z0-9_-]{4,64}$/', $uid)) return new WP_Error('cc_wk_bad', 'week and uid needed.', ['status' => 400]);
        $all = cc_wk_reviews(); $wk = $all[$w] ?? ['athletes' => []];
        $doc = (array) ($wk['athletes'][$uid] ?? ['decision' => '', 'comment' => '', 'days' => (object) []]);
        if ($r->has_param('ifUpdatedAt') && (string) $r['ifUpdatedAt'] !== (string) ($doc['updatedAt'] ?? '')) return new WP_Error('cc_wk_changed', 'Matteo changed this review since you read it: read it again.', ['status' => 409]);
        foreach (['reply', 'outcome'] as $k) if ($r->has_param($k)) $doc[$k] = mb_substr(sanitize_textarea_field((string) $r[$k]), 0, 3000);
        $h = (string) ($r['handledAt'] ?? ''); $doc['handledAt'] = preg_match('/^\d{4}-\d{2}-\d{2}T[\d:.]+Z$/', $h) ? $h : cc_wk_now();
        $wk['athletes'][$uid] = $doc; $all[$w] = $wk; update_option('cc_wk_review', $all, false);
        return ['ok' => true, 'doc' => $doc];
    }]);
});

add_filter('cc_ath_coach_links', function ($html) {
    if (!cc_ath_is_coach()) return $html;
    $n = cc_wk_open_count();
    return $html . '<a class="av-boardlink" href="' . esc_url(cc_wk_url()) . '">Next week' . ($n ? ' <span class="av-badge">' . $n . '</span>' : '') . '</a>';
}, 4);

function cc_wk_dshort($d) { $t = strtotime($d . ' 12:00:00'); return $t ? date_i18n('D j M', $t) : ''; }
function cc_wk_pri($p) {
    $p = strtoupper((string) $p);
    return in_array($p, ['A', 'B', 'C'], true) ? '<i class="wk-pri wk-pri-' . strtolower($p) . '" title="' . $p . ' race">' . $p . '</i>' : '<i class="wk-pri wk-pri-n" title="Priority not set">?</i>';
}
function cc_wk_race_html($races) {
    if (!$races) return '';
    $today = current_time('Y-m-d'); $o = '';
    foreach (array_slice((array) $races, 0, 3) as $r) {
        $days = (int) round((strtotime($r['date'] . ' 12:00:00') - strtotime($today . ' 12:00:00')) / DAY_IN_SECONDS);
        $when = $days === 0 ? 'today' : ($days === 1 ? 'tomorrow' : 'in ' . $days . ' days');
        $o .= '<span class="wk-race">' . cc_wk_pri($r['pri'] ?? '') . '<b>' . esc_html($r['name']) . '</b> <small>' . esc_html(cc_wk_dshort($r['date']) . ' · ' . $when . (empty($r['pri']) ? ' · priority not set' : '')) . '</small></span>';
    }
    return $o;
}
function cc_wk_load_html($l, $compact = false) {
    if (!$l) return '';
    $nums = 'Load-8 ' . round((float) $l['l8']) . ' · Load-2 ' . round((float) $l['l2']) . ' · Strain ' . round((float) $l['st']);
    if (!empty($l['flag'])) return '<span class="wk-load on"><b>Load ramping fast</b> <small>' . esc_html($l['why']) . '</small></span>';
    return $compact ? '' : '<span class="wk-load"><small>' . esc_html($nums) . '</small></span>';
}
function cc_wk_stim($s) {
    $m = ['threshold' => 'THR', 'vo2max' => 'VO2', 'neuromuscular' => 'NM', 'tempo' => 'TEMPO', 'anaerobic' => 'ANA', 'aerobic' => 'AER', 'recovery' => 'REC', 'durability' => 'DUR', 'activation' => 'ACT', 'test' => 'TEST', 'race' => 'RACE'];
    if (!$s) return '';
    $hard = in_array($s, ['threshold', 'vo2max', 'neuromuscular'], true);
    return '<span class="wk-stim' . ($hard ? ' hard' : '') . '">' . esc_html($m[$s] ?? strtoupper(substr($s, 0, 5))) . '</span>';
}
function cc_wk_card($a, $dy, $wk, $rv) {
    $uid = (string) $a['userId']; $pid = (int) ($dy['page'] ?? $a['page'] ?? 0);
    $face = ($pid && function_exists('cc_ph_face')) ? cc_ph_face($pid, 34) : '';
    $nm = esc_html($dy['name'] ?? $a['name']);
    $nm = $pid ? '<a href="' . esc_url(add_query_arg('view', $pid, home_url('/' . CC_ATH_SLUG . '/'))) . '">' . $nm . '</a>' : $nm;
    $o = '<article class="wk-card" id="wk-' . esc_attr($uid) . '" data-uid="' . esc_attr($uid) . '" data-name="' . esc_attr($a['name'] ?? '') . '">'
        . '<header class="wk-hd"><span class="wk-who">' . $face . '<b>' . $nm . '</b></span></header>';
    $chips = cc_wk_race_html($dy['races'] ?? []) . cc_wk_load_html($dy['load'] ?? null);
    if ($chips !== '') $o .= '<div class="wk-chips">' . $chips . '</div>';
    $rows = (array) ($a['rows'] ?? []);
    if (!$rows) return cc_wk_mini($a, $dy, $rv, $face, $nm, $chips);
    {
        $pct = isset($a['pct']) && $a['pct'] !== null ? sprintf(' (%+.1f%%)', (float) $a['pct']) : '';
        $hard = count(array_unique(array_map(function ($r) { return $r['date']; }, array_filter($rows, function ($r) { return in_array($r['stim'] ?? '', ['threshold', 'vo2max', 'neuromuscular'], true); }))));
        $meta = ['<span><b>Cycle</b> ' . esc_html(($a['cycle'] ?? '') ?: 'not set') . '</span>',
                 '<span><b>Hours</b> ' . esc_html(($a['baselineH'] ?? '–') . ' → ' . ($a['totalH'] ?? '–') . $pct) . '</span>',
                 '<span><b>Hard days</b> ' . $hard . ' of 3</span>'];
        if (!empty($a['hist'])) $meta[] = '<span><b>Ridden</b> ' . esc_html(implode(' · ', array_map(function ($h) { return round((float) $h, 1); }, (array) $a['hist']))) . ' h <small>(last 4 weeks)</small></span>';
        $o .= '<div class="wk-meta">' . implode('', $meta) . '</div><ul class="wk-days">';
        $ws = strtotime($wk . ' 12:00:00');
        for ($i = 0; $i < 7; $i++) {
            $d = gmdate('Y-m-d', $ws + $i * DAY_IN_SECONDS); $dn = date_i18n('D', $ws + $i * DAY_IN_SECONDS); $dd = (int) gmdate('j', $ws + $i * DAY_IN_SECONDS);
            $day = array_values(array_filter($rows, function ($r) use ($d) { return ($r['date'] ?? '') === $d; }));
            $o .= '<li><span class="wk-dd">' . esc_html($dn) . '<small>' . $dd . '</small></span><span class="wk-ss">';
            if (!$day) $o .= '<span class="wk-t wk-rest">—</span>';
            foreach ($day as $r) {
                $rest = in_array($r['kind'] ?? '', ['rest', 'restnote'], true) || (empty($r['min']) && ($r['stim'] ?? '') !== 'race');
                $need = strpos((string) ($r['title'] ?? ''), '??') === 0 || strpos((string) ($r['why'] ?? ''), 'NOT AVAILABLE') !== false;
                $o .= '<span class="wk-row' . ($rest ? ' rest' : '') . ($need ? ' need' : '') . '"><span class="wk-t">' . esc_html(ltrim((string) $r['title'], '? ')) . '</span>'
                    . '<span class="wk-mm">' . (!empty($r['min']) ? (int) $r['min'] . '′' : '') . cc_wk_stim($r['stim'] ?? '') . '</span>'
                    . (!empty($r['why']) ? '<span class="wk-w">' . esc_html($r['why']) . '</span>' : '') . '</span>';
            }
            $o .= '<input class="wk-dayedit" data-date="' . esc_attr($d) . '" placeholder="Change ' . esc_attr($dn) . ': e.g. easy spin, travelling" aria-label="Change for ' . esc_attr(date_i18n('l', $ws + $i * DAY_IN_SECONDS)) . '" hidden></span></li>';
        }
        $o .= '</ul>';
        $attn = (array) ($a['attn'] ?? []); $info = (array) ($a['info'] ?? []);
        if ($attn) $o .= '<div class="wk-attn"><p class="wk-eb">Needs your call</p><ul>' . implode('', array_map(function ($f) { return '<li>' . esc_html($f) . '</li>'; }, $attn)) . '</ul></div>';
        if ($info) $o .= '<details class="wk-info"><summary>' . count($info) . ' notes on the picks</summary><ul>' . implode('', array_map(function ($f) { return '<li>' . esc_html($f) . '</li>'; }, $info)) . '</ul></details>';
        $ch = (array) ($a['changes'] ?? []);
        if ($ch) $o .= '<details class="wk-info"><summary>What Claude changed (' . count($ch) . ')</summary><ul>' . implode('', array_map(function ($c) { return '<li><b>' . esc_html($c['date'] ?? '') . '</b> ' . esc_html($c['what'] ?? '') . (!empty($c['why']) ? ' · ' . esc_html($c['why']) : '') . '</li>'; }, $ch)) . '</ul></details>';
    }
    $d = (array) ($rv[$uid] ?? []); [$lt, $lk] = cc_wk_label($d);
    $o .= '<div class="wk-rv" data-state="' . esc_attr(wp_json_encode($d ?: new stdClass())) . '">'
        . '<div class="wk-rvh"><span class="wk-eb">Your review</span><span class="wk-st" data-k="' . esc_attr($lk) . '">' . esc_html($lt) . '</span></div>'
        . '<div class="wk-reply"' . (empty($d['reply']) ? ' hidden' : '') . '><small>Claude</small><p>' . esc_html($d['reply'] ?? '') . '</p></div>'
        . '<div class="wk-btns" role="group" aria-label="Decision for ' . esc_attr($a['name'] ?? '') . '">'
        . ($rows ? '<button type="button" class="wk-b wk-go" data-d="approve" aria-pressed="false">Create as drafts</button>' : '')
        . '<button type="button" class="wk-b" data-d="change" aria-pressed="false">' . ($rows ? 'Change' : 'Plan this rider') . '</button>'
        . '<button type="button" class="wk-b" data-d="hold" aria-pressed="false">Hold</button>'
        . ($rows ? '<button type="button" class="wk-b wk-ed" aria-expanded="false">Edit days</button>' : '') . '</div>'
        . '<textarea rows="2" placeholder="What should I change, or what should I know? e.g. No sprints, knee sore." aria-label="Comment for Claude"></textarea>'
        . '<div class="wk-bt2"><button type="button" class="wk-b wk-dict" aria-pressed="false">🎙 Dictate</button><span class="wk-saved" role="status"></span></div></div>';
    return $o . '</article>';
}
/* Matteo 20 Nov: a rider with no draft week is one compact row; the comment box opens only on "Plan this rider" or "Add a note" */
function cc_wk_mini($a, $dy, $rv, $face, $nm, $chips) {
    $uid = (string) $a['userId'];
    $l = $dy['load'] ?? null;
    if ($l && empty($l['flag'])) $chips = cc_wk_race_html($dy['races'] ?? []) . '<span class="wk-nums">Load-8 ' . round((float) $l['l8']) . ' · Load-2 ' . round((float) $l['l2']) . ' · Strain ' . round((float) $l['st']) . '</span>';
    $note = implode(' ', array_filter(array_merge(array_map(function ($c) { return (string) ($c['what'] ?? ''); }, (array) ($a['changes'] ?? [])), array_map('strval', (array) ($a['flags'] ?? [])))));
    $d = (array) ($rv[$uid] ?? []); [$lt, $lk] = cc_wk_label($d);
    return '<article class="wk-card wk-mini" id="wk-' . esc_attr($uid) . '" data-uid="' . esc_attr($uid) . '" data-name="' . esc_attr($a['name'] ?? '') . '">'
        . '<div class="wk-rv" data-state="' . esc_attr(wp_json_encode($d ?: new stdClass())) . '">'
        . '<div class="wk-mrow"><span class="wk-who">' . $face . '<b>' . $nm . '</b></span><span class="wk-st" data-k="' . esc_attr($lk) . '">' . esc_html($lt === 'Not reviewed' ? '' : $lt) . '</span></div>'
        . ($chips !== '' ? '<div class="wk-chips">' . $chips . '</div>' : '')
        . ($note !== '' ? '<p class="wk-mnote">' . esc_html(wp_trim_words($note, 28)) . '</p>' : '')
        . '<div class="wk-reply"' . (empty($d['reply']) ? ' hidden' : '') . '><small>Claude</small><p>' . esc_html($d['reply'] ?? '') . '</p></div>'
        . '<div class="wk-btns" role="group" aria-label="Decision for ' . esc_attr($a['name'] ?? '') . '">'
        . '<button type="button" class="wk-b wk-open" data-d="change" aria-pressed="false">Plan this rider</button>'
        . '<button type="button" class="wk-b" data-d="hold" aria-pressed="false">Hold</button>'
        . '<button type="button" class="wk-b wk-open wk-note" aria-label="Add a note" title="Add a note">+ Note</button><span class="wk-saved" role="status"></span></div>'
        . '<div class="wk-cbox" hidden><textarea rows="2" placeholder="What should I know or plan for this rider?" aria-label="Note for Claude"></textarea>'
        . '<div class="wk-bt2"><button type="button" class="wk-b wk-dict" aria-pressed="false">🎙 Dictate</button></div></div>'
        . '</div></article>';
}
function cc_wk_compact($dy, $wk, $what, $cls = '') {
    $pid = (int) ($dy['page'] ?? 0);
    $face = ($pid && function_exists('cc_ph_face')) ? cc_ph_face($pid, 28) : '';
    $nm = esc_html($dy['name'] ?? '');
    if ($pid) $nm = '<a href="' . esc_url(add_query_arg('view', $pid, home_url('/' . CC_ATH_SLUG . '/'))) . '">' . $nm . '</a>';
    $extra = cc_wk_race_html($dy['races'] ?? []) . cc_wk_load_html($dy['load'] ?? null, true);
    return '<div class="wk-line ' . $cls . '"><span class="wk-who">' . $face . '<b>' . $nm . '</b></span><span class="wk-what">' . $what . '</span>' . ($extra !== '' ? '<div class="wk-chips">' . $extra . '</div>' : '') . '</div>';
}

add_filter('cc_ath_board', function ($html, $board) {
    if ($board !== 'week' || !cc_ath_is_coach()) return $html;
    $plans = cc_wk_plans(); $daily = cc_wk_daily();
    $next = (string) ($daily['nextWeek'] ?? '') ?: cc_wk_next_monday();
    if (strcmp($next, cc_wk_this_monday()) <= 0) $next = cc_wk_next_monday();   /* old daily data: still the coming week */
    $weeks = array_unique(array_merge([$next], array_keys($plans))); rsort($weeks);
    $weeks = array_slice($weeks, 0, 5);
    $newest = $plans ? (string) array_key_first($plans) : '';
    $def = ($newest !== '' && strcmp($newest, cc_wk_this_monday()) >= 0) ? $newest : $next;
    $wk = isset($_GET['wk']) ? sanitize_text_field(wp_unslash($_GET['wk'])) : '';
    if (!in_array($wk, $weeks, true)) $wk = $def;
    $plan = $plans[$wk] ?? null; $rv = cc_wk_review_of($wk);
    $we = gmdate('Y-m-d', strtotime($wk . ' 12:00:00') + 6 * DAY_IN_SECONDS);
    $byId = []; foreach ((array) ($daily['athletes'] ?? []) as $x) if (!empty($x['vekta_id'])) $byId[$x['vekta_id']] = $x;
    $prop = []; foreach ((array) ($plan['athletes'] ?? []) as $a) if (!empty($a['userId'])) $prop[$a['userId']] = $a;

    $toplan = $planned = $drafts = $skipped = [];
    $ids = array_unique(array_merge(array_keys($byId), array_keys($prop)));
    foreach ($ids as $id) {
        $dy = $byId[$id] ?? ['vekta_id' => $id, 'name' => $prop[$id]['name'] ?? '', 'page' => $prop[$id]['page'] ?? 0];
        $w = $dy['weeks'][$wk] ?? null;
        if (isset($prop[$id])) { $toplan[] = [$prop[$id], $dy, $w]; continue; }
        if ($w && (int) $w['visible'] > 0) { $planned[] = [$dy, $w]; continue; }
        if ($w && (int) $w['hidden'] > 0) { $drafts[] = [$dy, $w]; continue; }
        if (!empty($dy['skip'])) { $skipped[] = $dy; continue; }
        if ($w !== null) $toplan[] = [['userId' => $id, 'name' => $dy['name'], 'rows' => []], $dy, $w];
    }
    $sortn = function ($x, $y) { return strcasecmp($x['name'] ?? '', $y['name'] ?? ''); };
    /* drafted weeks first; then riders racing in 14 days or with a load flag; then by name */
    $rank = function ($t) { if (!empty($t[0]['rows'])) return 0; return (!empty($t[1]['races']) || !empty($t[1]['load']['flag'])) ? 1 : 2; };
    usort($toplan, function ($x, $y) use ($rank) { return $rank($x) <=> $rank($y) ?: strcasecmp($x[0]['name'] ?? '', $y[0]['name'] ?? ''); });
    usort($planned, function ($x, $y) use ($sortn) { return $sortn($x[0], $y[0]); });
    usort($drafts, function ($x, $y) use ($sortn) { return $sortn($x[0], $y[0]); });
    usort($skipped, $sortn);
    $nr = 0; $nf = 0; foreach ($byId as $x) { if (!empty($x['races'])) $nr++; if (!empty($x['load']['flag'])) $nf++; }

    $o = '<section class="ath-s wk-wrap"><h2>Next week</h2><p class="av-lede">Every rider for the week of <b>' . esc_html(cc_wk_dshort($wk) . ' – ' . cc_wk_dshort($we)) . '</b>: Claude\'s draft week for those you haven\'t planned yet, their races in the next 14 days and a flag when load is ramping too fast. Only you can see this page.</p>';
    if (count($weeks) > 1) {
        $o .= '<div class="wk-tabs" role="tablist">';
        foreach ($weeks as $w) $o .= '<a role="tab" class="wk-tab' . ($w === $wk ? ' on' : '') . '" href="' . esc_url(cc_wk_url($w)) . '"' . ($w === $wk ? ' aria-selected="true"' : '') . '>' . esc_html(cc_wk_dshort($w)) . ($w === $next ? ' · next week' : (strcmp($w, cc_wk_this_monday()) === 0 ? ' · this week' : '')) . '</a>';
        $o .= '</div>';
    }
    $sync = [];
    $sync[] = !empty($daily['postedAt']) ? 'Races, load and "planned" updated ' . esc_html(human_time_diff((int) $daily['postedAt'], time())) . ' ago from your laptop (each morning).' : 'Races and load arrive after the next morning run on your laptop.';
    $sync[] = $plan ? 'Draft week from Claude, posted ' . esc_html(date_i18n('D j M H:i', (int) $plan['postedAt'] + (int) (get_option('gmt_offset') * HOUR_IN_SECONDS))) . '.' : 'No draft week from Claude for this week yet: the Sunday 18:00 run drafts it (or ask Claude "plan next week").';
    if ($plan && $wk !== $next) $sync[] = '<b>This is not next week:</b> use it for reference.';
    $o .= '<p class="wk-sync">' . implode(' ', $sync) . '</p>';
    $o .= '<div class="wk-kpis"><span><b>' . count($toplan) . '</b>to plan</span><span><b>' . count($planned) . '</b>planned</span>'
        . '<span><b>' . $nr . '</b>racing in 14 days</span><span class="' . ($nf ? 'red' : '') . '"><b>' . $nf . '</b>load flags</span></div>';

    $o .= '<h3 class="wk-h">To plan</h3>';
    if (!$toplan) $o .= '<p class="wk-ok">✓ Every rider has your sessions for this week.</p>';
    $mini = false;
    foreach ($toplan as [$a, $dy, $w]) {
        if (empty($a['rows']) && !$mini) { $mini = true; $o .= '<p class="wk-sub wk-minih">No draft week yet: racing or load flags first. Tap <b>Plan this rider</b> to ask Claude for a week.</p><div class="wk-minis">'; }
        $o .= cc_wk_card($a, $dy, $wk, $rv['athletes']);
    }
    if ($mini) $o .= '</div>';
    if ($drafts) {
        $o .= '<h3 class="wk-h">Drafts in Vekta (hidden)</h3><p class="wk-sub">Created, waiting for you to unhide them in the Vekta calendar.</p><div class="wk-lines">';
        foreach ($drafts as [$dy, $w]) $o .= cc_wk_compact($dy, $wk, '<span class="wk-draft">' . (int) $w['hidden'] . ' hidden · ' . esc_html($w['hiddenHours']) . ' h</span>');
        $o .= '</div>';
    }
    $o .= '<h3 class="wk-h">Planned ✓</h3>';
    if (!$planned) $o .= '<p class="wk-sub">Nobody has your visible sessions for this week yet.</p>';
    else { $o .= '<div class="wk-lines">'; foreach ($planned as [$dy, $w]) $o .= cc_wk_compact($dy, $wk, '<span class="wk-done">✓ ' . (int) $w['visible'] . ' sessions · ' . esc_html($w['hours']) . ' h</span>'); $o .= '</div>'; }
    if ($skipped) {
        $o .= '<h3 class="wk-h">Not planned on purpose</h3><div class="wk-lines">';
        foreach ($skipped as $dy) $o .= cc_wk_compact($dy, $wk, '<span class="wk-skip">' . esc_html($dy['skip']) . '</span>');
        $o .= '</div>';
    }
    $o .= '<div class="wk-notes"><label for="wk-notes" class="wk-eb">Notes for the whole week</label><textarea id="wk-notes" rows="2" placeholder="Anything Claude should know for everyone this week">' . esc_textarea($rv['notes']) . '</textarea><span class="wk-saved" id="wk-notes-s" role="status"></span></div>';
    $R = (array) ($daily['rules'] ?? []);
    $o .= '<div class="wk-how"><p><b>How it works.</b> Tap <b>Create as drafts</b>, <b>Change</b> (write what to change, or <b>Edit days</b>) or <b>Hold</b>. It saves at once. Then tell Claude <q>process my plan review</q>: Claude re-plans what you asked, answers on the card, and lists the weeks you approved. Nothing goes to Vekta until you say yes in that chat, and then only as hidden drafts that you unhide in Vekta.</p>'
        . '<p><b>Load ramping fast</b> (red) when, up to yesterday, Load-2 (2-week load) is at least ' . esc_html(round(((float) ($R['ratio'] ?? 1.3) - 1) * 100)) . '% above Load-8 (8-week load), with Load-8 of ' . esc_html($R['minLoad8'] ?? 5) . ' or more so tiny numbers don\'t flag; or Strain went up ' . esc_html(round((float) ($R['strainJump'] ?? .3) * 100)) . '% or more in 7 days, to ' . esc_html($R['minStrain'] ?? 20) . ' or more. Same formulas as Vekta and the Season Plan. A cautious line: it flags well before the usual 1.5 danger zone.</p>'
        . '<p><b>Races</b>: events in Vekta in the next 14 days, plus events riders added in their hub that aren\'t in Vekta yet. Priority A/B/C comes from the hub ("Priority X (athlete\'s)"); ? = not set. <b>Planned</b> = at least one of your visible sessions that week; hidden plans count as drafts. TrainingPeaks riders and plan templates are left out.</p></div>';
    $o .= '</section>' . cc_wk_assets($wk) . (function_exists('cc_ph_assets') ? cc_ph_assets() : '');
    return $o;
}, 10, 2);

function cc_wk_assets($wk) {
    $css = 'html .cc .wk-wrap{max-width:900px}html .cc .wk-wrap b{color:#fff}'
        . 'html .cc .wk-sync{color:#b8bec8;font-size:15px;margin:0 0 14px;line-height:1.5}'
        . 'html .cc .wk-tabs{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}'
        . 'html .cc .wk-tab{padding:9px 16px;border-radius:999px;border:1px solid rgba(255,255,255,.18);color:#d7dbe2;text-decoration:none;font-weight:600;font-size:15px}'
        . 'html .cc .wk-tab.on{background:rgba(18,161,80,.18);border-color:rgba(43,212,122,.55);color:#fff}'
        . 'html .cc .wk-kpis{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:0 0 8px}'
        . 'html .cc .wk-kpis span{padding:12px 14px;border-radius:12px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.03);font-size:14px;color:#b8bec8;font-weight:600}'
        . 'html .cc .wk-kpis b{display:block;font-family:Anton,Impact,sans-serif;font-weight:400;font-size:30px;line-height:1.1;color:#fff}html .cc .wk-kpis .red b{color:#ff4a3d}'
        . 'html .cc .wk-h{font-family:Anton,Impact,sans-serif!important;font-weight:400!important;font-size:24px!important;letter-spacing:.02em!important;text-transform:uppercase;color:#f7f8f8!important;margin:26px 0 10px!important}'
        . 'html .cc .wk-sub,html .cc .wk-ok{color:#b8bec8;font-size:15px;margin:0 0 10px}html .cc .wk-ok{color:#2bd47a;font-weight:600;font-size:16px}'
        . 'html .cc .wk-card{padding:16px;margin:0 0 14px;border-radius:14px;border:1px solid rgba(255,255,255,.1);background:rgba(15,16,17,.88);display:grid;gap:12px}'
        . 'html .cc .wk-who{display:flex;align-items:center;gap:10px;font-size:18px;min-width:0}html .cc .wk-who a{color:#fff;text-decoration:none}'
        . 'html .cc .wk-chips{display:flex;flex-wrap:wrap;gap:8px}'
        . 'html .cc .wk-race,html .cc .wk-load{display:inline-flex;align-items:center;gap:8px;padding:6px 12px;border-radius:10px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);font-size:15px;color:#e6e9ee;flex-wrap:wrap}'
        . 'html .cc .wk-race small,html .cc .wk-load small{font-size:14px;color:#b8bec8}'
        . 'html .cc .wk-load.on{border-color:rgba(255,74,61,.6);background:rgba(202,33,42,.12)}html .cc .wk-load.on b{color:#ff4a3d}html .cc .wk-load.on small{color:#e6e9ee}'
        . 'html .cc .wk-pri{flex:none;display:inline-grid;place-items:center;width:24px;height:24px;border-radius:50%;font:700 13px/1 Montserrat,sans-serif;font-style:normal;color:#1a1406}'
        . 'html .cc .wk-pri-a{background:linear-gradient(135deg,#F3D774,#D4AF37 55%,#A8841F)}html .cc .wk-pri-b{background:linear-gradient(135deg,#F2F3F5,#C0C4CC 55%,#8E939C)}html .cc .wk-pri-c{background:linear-gradient(135deg,#E9A86B,#CD7F32 55%,#9A5A1F)}'
        . 'html .cc .wk-pri-n{background:transparent;border:1px dashed #b8bec8;color:#b8bec8}'
        . 'html .cc .wk-meta{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:15px;color:#d0d6e0}html .cc .wk-meta b{color:#b8bec8;font-weight:700;font-size:14px;text-transform:uppercase;letter-spacing:.05em;margin-right:4px}html .cc .wk-meta small{color:#b8bec8;font-size:14px}'
        . 'html .cc .wk-days{list-style:none;margin:0;padding:0}html .cc .wk-days li{display:grid;grid-template-columns:46px minmax(0,1fr);gap:10px;padding:10px 0;border-top:1px solid rgba(255,255,255,.06);margin:0}'
        . 'html .cc .wk-dd{font-weight:700;color:#fff;font-size:15px}html .cc .wk-dd small{display:block;color:#b8bec8;font-weight:500;font-size:14px}'
        . 'html .cc .wk-ss{display:grid;gap:8px;min-width:0}html .cc .wk-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:2px 10px}'
        . 'html .cc .wk-t{color:#fff;font-size:16px;font-weight:600;overflow-wrap:anywhere}html .cc .wk-rest,html .cc .wk-row.rest .wk-t{color:#b8bec8;font-weight:500}html .cc .wk-row.need .wk-t{color:#ff4a3d}'
        . 'html .cc .wk-mm{white-space:nowrap;font-size:15px;color:#d0d6e0;font-weight:600;text-align:right}html .cc .wk-w{grid-column:1/-1;font-size:14px;color:#b8bec8;line-height:1.45}'
        . 'html .cc .wk-stim{display:inline-block;margin-left:6px;font-size:13px;font-weight:700;padding:2px 6px;border-radius:6px;border:1px solid rgba(255,255,255,.2);color:#d0d6e0}html .cc .wk-stim.hard{border-color:rgba(255,255,255,.6);color:#fff;background:rgba(255,255,255,.08)}'
        . 'html .cc .wk-dayedit,html .cc .wk-rv textarea,html .cc .wk-notes textarea{width:100%;box-sizing:border-box;font:16px Montserrat,sans-serif;padding:10px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.18);background:#0b0d0f;color:#fff;line-height:1.45}'
        . 'html .cc .wk-attn{border:1px solid rgba(255,74,61,.4);background:rgba(202,33,42,.07);border-radius:10px;padding:10px 14px}'
        . 'html .cc .wk-attn ul,html .cc .wk-info ul{margin:4px 0 0;padding-left:18px;font-size:15px;line-height:1.5;color:#d0d6e0}'
        . 'html .cc .wk-info summary{cursor:pointer;font-size:15px;font-weight:600;color:#b8bec8}'
        . 'html .cc .wk-eb{display:block;margin:0;font-size:14px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#b8bec8}'
        . 'html .cc .wk-none{margin:0;font-size:15px;color:#b8bec8;line-height:1.5}'
        . 'html .cc .wk-rv{display:grid;gap:10px;border-top:1px solid rgba(255,255,255,.08);padding-top:12px}html .cc .wk-rvh{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;align-items:center}'
        . 'html .cc .wk-st{font-size:15px;font-weight:600;color:#b8bec8}html .cc .wk-st[data-k=approve],html .cc .wk-st[data-k=done]{color:#2bd47a}html .cc .wk-st[data-k=wait]{color:#f0bf00}'
        . 'html .cc .wk-reply{border:1px solid rgba(43,212,122,.4);background:rgba(18,161,80,.08);border-radius:10px;padding:10px 14px}html .cc .wk-reply small{color:#2bd47a;font-weight:700;font-size:14px;text-transform:uppercase;letter-spacing:.06em}html .cc .wk-reply p{margin:4px 0 0;color:#fff;font-size:16px;white-space:pre-wrap}'
        . 'html .cc .wk-btns,html .cc .wk-bt2{display:flex;flex-wrap:wrap;gap:8px;align-items:center}'
        . 'html .cc .wk-b{font:600 15px Montserrat,sans-serif;padding:10px 16px;min-height:44px;border-radius:999px;border:1px solid rgba(255,255,255,.22);background:transparent;color:#e6e9ee;cursor:pointer}'
        . 'html .cc .wk-b.wk-go{border-color:rgba(43,212,122,.7);color:#2bd47a}html .cc .wk-b[aria-pressed=true]{background:#12a150;border-color:#12a150;color:#fff}'
        . 'html .cc .wk-b[aria-pressed=true]:not(.wk-go):not(.wk-dict){background:rgba(255,255,255,.14);border-color:#fff}html .cc .wk-b:disabled{opacity:.5}'
        . 'html .cc .wk-saved{font-size:14px;color:#b8bec8}html .cc .wk-saved.err{color:#ff7a73}'
        . 'html .cc .wk-lines{display:grid;gap:8px}html .cc .wk-line{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:6px 12px;align-items:center;padding:10px 14px;border-radius:12px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08)}'
        . 'html .cc .wk-line .wk-who{font-size:16px}html .cc .wk-line .wk-chips{grid-column:1/-1}html .cc .wk-what{font-size:15px;text-align:right}'
        . 'html .cc .wk-done{color:#2bd47a;font-weight:600}html .cc .wk-draft{color:#f0bf00;font-weight:600}html .cc .wk-skip{color:#b8bec8}'
        . 'html .cc .wk-notes{display:grid;gap:8px;margin:26px 0 0}'
        . 'html .cc .wk-how{margin:22px 0 0;font-size:15px;color:#b8bec8;line-height:1.55}html .cc .wk-how q{color:#2bd47a;font-weight:600}'
        . 'html .cc .wk-minis{display:grid;gap:8px}html .cc .wk-minih{margin:18px 0 8px}'
        . 'html .cc .wk-card.wk-mini{padding:10px 14px;margin:0;gap:0;border-radius:12px;background:rgba(255,255,255,.03)}'
        . 'html .cc .wk-mini .wk-rv{border-top:0;padding-top:0;gap:8px}html .cc .wk-mrow{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}'
        . 'html .cc .wk-mini .wk-who{font-size:16px}html .cc .wk-nums{font-size:14px;color:#b8bec8;align-self:center}'
        . 'html .cc .wk-mini .wk-race,html .cc .wk-mini .wk-load{padding:4px 10px}html .cc .wk-mnote{margin:0;font-size:14px;color:#b8bec8;line-height:1.45}'
        . 'html .cc .wk-mini .wk-b{padding:8px 11px;font-size:14px;min-height:44px}html .cc .wk-mini .wk-btns{gap:6px}html .cc .wk-mini .wk-saved:empty{display:none}html .cc .wk-mini .wk-saved{flex-basis:100%}html .cc .wk-mini .wk-cbox{display:grid;gap:8px}html .cc .wk-mini .wk-cbox[hidden]{display:none}'
        . '@media(max-width:640px){html .cc .wk-kpis{grid-template-columns:repeat(2,minmax(0,1fr))}html .cc .wk-line{grid-template-columns:1fr}html .cc .wk-what{text-align:left}html .cc .wk-card{padding:14px 12px}}';
    $js = '(function(){var API=' . wp_json_encode(rest_url('cc/v1/week-review')) . ',N=' . wp_json_encode(wp_create_nonce('wp_rest')) . ',WEEK=' . wp_json_encode($wk) . ';'
        . 'function lab(d){if(!d||!Object.keys(d).length)return["Not reviewed",""];var w=d.updatedAt&&(!d.handledAt||d.updatedAt>d.handledAt);if(d.outcome&&!w)return[d.outcome,"done"];'
        . 'if(d.decision==="approve")return[w?"Create as drafts: waiting for Claude":"Approved",w?"wait":"approve"];if(d.decision==="hold")return["On hold",""];'
        . 'var dy=d.days||{};if(w&&(d.decision==="change"||d.comment||Object.keys(dy).some(function(k){return dy[k];})))return["Change asked: waiting for Claude","wait"];if(d.handledAt)return["Revised by Claude","done"];return["Not reviewed",""];}'
        . 'function st(c){var r=c.querySelector(".wk-rv");try{return JSON.parse(r.dataset.state||"{}")||{};}catch(e){return{};}}'
        . 'function draw(c,d){var r=c.querySelector(".wk-rv");r.dataset.state=JSON.stringify(d);var l=lab(d),s=r.querySelector(".wk-st");s.textContent=(l[0]==="Not reviewed"&&c.classList.contains("wk-mini"))?"":l[0];s.dataset.k=l[1];'
        . 'r.querySelectorAll("[data-d]").forEach(function(b){b.setAttribute("aria-pressed",String(d.decision===b.dataset.d));});'
        . 'var t=r.querySelector("textarea");if(document.activeElement!==t)t.value=d.comment||"";var any=false;'
        . 'c.querySelectorAll(".wk-dayedit").forEach(function(i){var v=(d.days||{})[i.dataset.date]||"";if(document.activeElement!==i)i.value=v;if(v){i.hidden=false;any=true;}});'
        . 'var e=c.querySelector(".wk-ed");if(e&&any)e.setAttribute("aria-expanded","true");var cb=c.querySelector(".wk-cbox");if(cb&&d.comment)cb.hidden=false;}'
        . 'document.addEventListener("click",function(ev){var b=ev.target.closest(".wk-open");if(!b)return;var cb=b.closest(".wk-card").querySelector(".wk-cbox");if(cb&&cb.hidden){cb.hidden=false;var t=cb.querySelector("textarea");if(t&&!b.dataset.d)t.focus();}});'
        . 'var q={};function save(c,patch){var uid=c.dataset.uid,m=c.querySelector(".wk-rv .wk-saved");m.className="wk-saved";m.textContent="Saving…";'
        . 'var body=Object.assign({week:WEEK,uid:uid,name:c.dataset.name},patch);q[uid]=(q[uid]||Promise.resolve()).then(function(){return fetch(API,{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json","X-WP-Nonce":N},body:JSON.stringify(body)})'
        . '.then(function(r){if(!r.ok)throw 0;return r.json();}).then(function(j){draw(c,j.doc);m.textContent="Saved. When you are done, tell Claude: “process my plan review”.";})'
        . '.catch(function(){m.className="wk-saved err";m.textContent="Not saved. Check your connection and try again.";});});}'
        . 'var tm={};function later(k,f){clearTimeout(tm[k]);tm[k]=setTimeout(f,1000);}'
        . 'document.querySelectorAll(".wk-card").forEach(function(c){draw(c,st(c));var t=c.querySelector(".wk-rv textarea");'
        . 'c.querySelectorAll(".wk-rv [data-d]").forEach(function(b){b.addEventListener("click",function(){var d=st(c);save(c,{decision:d.decision===b.dataset.d?"":b.dataset.d});});});'
        . 'var e=c.querySelector(".wk-ed");if(e)e.addEventListener("click",function(){var o=e.getAttribute("aria-expanded")!=="true";e.setAttribute("aria-expanded",String(o));c.querySelectorAll(".wk-dayedit").forEach(function(i){i.hidden=!o&&!i.value;});if(o){var f=c.querySelector(".wk-dayedit");if(f)f.focus();}});'
        . 'function cm(){var d=st(c),v=t.value.trim();if((d.comment||"")===v)return;save(c,{comment:v,decision:d.decision||(v?"change":"")});}'
        . 't.addEventListener("input",function(){later("c"+c.dataset.uid,cm);});t.addEventListener("blur",function(){clearTimeout(tm["c"+c.dataset.uid]);cm();});'
        . 'c.querySelectorAll(".wk-dayedit").forEach(function(i){function cd(){var d=st(c),days=Object.assign({},d.days||{}),v=i.value.trim();if((days[i.dataset.date]||"")===v)return;if(v)days[i.dataset.date]=v;else delete days[i.dataset.date];save(c,{days:days,decision:d.decision||"change"});}'
        . 'i.addEventListener("input",function(){later("d"+c.dataset.uid+i.dataset.date,cd);});i.addEventListener("blur",function(){clearTimeout(tm["d"+c.dataset.uid+i.dataset.date]);cd();});});});'
        . 'var wn=document.getElementById("wk-notes"),ws=document.getElementById("wk-notes-s"),last=wn?wn.value.trim():"";function sn(){var v=wn.value.trim();if(v===last)return;ws.className="wk-saved";ws.textContent="Saving…";'
        . 'fetch(API,{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json","X-WP-Nonce":N},body:JSON.stringify({week:WEEK,notes:v})}).then(function(r){if(!r.ok)throw 0;last=v;ws.textContent="Saved.";}).catch(function(){ws.className="wk-saved err";ws.textContent="Not saved. Try again.";});}'
        . 'if(wn){wn.addEventListener("input",function(){later("notes",sn);});wn.addEventListener("blur",function(){clearTimeout(tm.notes);sn();});}'
        /* dictation into the comment box (English; Claude reads it) */
        . 'var SR=window.SpeechRecognition||window.webkitSpeechRecognition,cur=null;document.addEventListener("click",function(ev){var b=ev.target.closest(".wk-dict");if(!b)return;var c=b.closest(".wk-card"),t=c.querySelector(".wk-rv textarea"),m=c.querySelector(".wk-rv .wk-saved");'
        . 'if(!SR){m.textContent="Dictation is not available here: tap the box and use the microphone on your keyboard.";t.focus();return;}if(cur){cur.stop();return;}var r=new SR();cur=r;r.lang="en-IE";r.continuous=true;r.interimResults=false;'
        . 'b.setAttribute("aria-pressed","true");b.textContent="■ Stop";r.onresult=function(e){for(var i=e.resultIndex;i<e.results.length;i++)if(e.results[i].isFinal){var x=e.results[i][0].transcript.trim();if(x)t.value=(t.value.trim()?t.value.trim()+" ":"")+x;}};'
        . 'r.onend=function(){cur=null;b.setAttribute("aria-pressed","false");b.textContent="🎙 Dictate";t.dispatchEvent(new Event("blur"));};r.onerror=function(){m.textContent="Dictation stopped. Try again.";};try{r.start();}catch(x){cur=null;}});})();';
    return '<style>' . $css . '</style><script>' . $js . '</script>';
}
