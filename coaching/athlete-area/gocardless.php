<?php
if (!defined('ABSPATH')) return;
/* GoCardless → athlete hub (Matteo, 17 Nov 2026). Replaces the Google Sheets / Apps Script onboarding (4 emails with PDFs):
 * the hub IS the onboarding now (guides, Vekta, Marine, Skool, rider form, all in the athlete's language).
 *
 * GoCardless calls POST /wp-json/cc/v1/gocardless when a subscription is created (webhook, signed with Matteo's secret).
 * For a genuinely new coaching client (customer AND subscription created after the cut-off, active, email not in the hub yet):
 *   LIVE: create their login (role subscriber → their page), language and country from GoCardless, contract on their page,
 *         the hub welcome email in their language, and one email to Matteo with what to do (Skool, Vekta, assessment).
 *   TEST (default): nothing is created; Matteo gets the same email marked TEST, saying what would have happened.
 * Anything else (existing customer starting another subscription, already in the hub, not active) is logged and Matteo is told.
 * Commitment (Matteo, 17 Nov): whole months only. Signup on or before the 12th: ends at the end of the month 5 months later
 * (5 Nov → 30 Apr, 12 Feb → 31 Jul); after the 12th: 6 months later (13 Feb → 31 Aug, 20 Nov → 31 May).
 * Renewal: 15 days before the end, one email to Matteo (never to the athlete); also on the Contracts board and GET /cc/v1/contracts.
 * Secrets (webhook secret, read-only access token) are typed by Matteo on the Contracts board, never in code or chat. */

const CC_GC_API = 'https://api.gocardless.com';
const CC_GC_REMIND_DAYS = 15;

function cc_gc_end($ymd) {   // commitment end (Y-m-d) from the signup date (Y-m-d)
    $d = DateTime::createFromFormat('!Y-m-d', substr((string) $ymd, 0, 10)); if (!$d) return '';
    $add = (int) $d->format('j') <= 12 ? 5 : 6;
    $d->setDate((int) $d->format('Y'), (int) $d->format('n'), 1)->modify("+$add months");
    return $d->format('Y-m-t');
}
function cc_gc_local_date($iso) {   // GoCardless timestamps are UTC: the signup day in Ireland
    try { $d = new DateTime($iso); $d->setTimezone(new DateTimeZone('Europe/Dublin')); return $d->format('Y-m-d'); } catch (Exception $e) { return ''; }
}
function cc_gc_log($what, $data = []) {
    $l = get_option('cc_gc_log', []); $l = is_array($l) ? $l : [];
    array_unshift($l, ['at' => time(), 'what' => $what] + $data); update_option('cc_gc_log', array_slice($l, 0, 100), false);
}
function cc_gc_mode() { return get_option('cc_gc_mode', 'test') === 'live' ? 'live' : 'test'; }
function cc_gc_get($path) {
    $tok = (string) get_option('cc_gc_token', ''); if ($tok === '') return new WP_Error('cc_gc', 'No GoCardless access token saved');
    $r = wp_remote_get(CC_GC_API . $path, ['timeout' => 15, 'headers' => ['Authorization' => 'Bearer ' . $tok, 'GoCardless-Version' => '2015-07-06', 'Accept' => 'application/json']]);
    if (is_wp_error($r)) return $r;
    $c = wp_remote_retrieve_response_code($r); $j = json_decode(wp_remote_retrieve_body($r), true);
    if ($c !== 200 || !is_array($j)) return new WP_Error('cc_gc', 'GoCardless answered ' . $c . (isset($j['error']['message']) ? ': ' . $j['error']['message'] : ''));
    return $j;
}

/* ---------- the webhook ---------- */
add_action('rest_api_init', function () {
    register_rest_route('cc/v1', '/gocardless', ['methods' => 'POST', 'permission_callback' => '__return_true', 'callback' => function (WP_REST_Request $r) {
        $sec = (string) get_option('cc_gc_secret', ''); $raw = $r->get_body(); $sig = (string) $r->get_header('webhook_signature');
        if ($sec === '' || $sig === '' || !hash_equals(hash_hmac('sha256', $raw, $sec), strtolower($sig))) return new WP_REST_Response(['error' => 'invalid signature'], 401);   // (WordPress turns GoCardless' suggested 498 into 200)
        $j = json_decode($raw, true); $seen = get_option('cc_gc_seen', []); $seen = is_array($seen) ? $seen : [];
        foreach ((array) ($j['events'] ?? []) as $e) {
            $id = (string) ($e['id'] ?? ''); if ($id === '' || in_array($id, $seen, true)) continue;
            $seen[] = $id;
            if (($e['resource_type'] ?? '') === 'subscriptions' && ($e['action'] ?? '') === 'created' && !empty($e['links']['subscription'])) cc_gc_subscription((string) $e['links']['subscription']);
        }
        update_option('cc_gc_seen', array_slice($seen, -1000), false);
        return new WP_REST_Response(['ok' => true], 200);
    }]);
});

function cc_gc_subscription($sid) {   // fetch subscription → mandate → customer, then decide
    $s = cc_gc_get('/subscriptions/' . rawurlencode($sid)); if (is_wp_error($s)) { cc_gc_log('error', ['sub' => $sid, 'msg' => $s->get_error_message()]); cc_gc_tell_problem($sid, $s->get_error_message()); return; }
    $s = $s['subscriptions'] ?? [];
    $m = cc_gc_get('/mandates/' . rawurlencode((string) ($s['links']['mandate'] ?? ''))); if (is_wp_error($m)) { cc_gc_log('error', ['sub' => $sid, 'msg' => $m->get_error_message()]); cc_gc_tell_problem($sid, $m->get_error_message()); return; }
    $c = cc_gc_get('/customers/' . rawurlencode((string) ($m['mandates']['links']['customer'] ?? ''))); if (is_wp_error($c)) { cc_gc_log('error', ['sub' => $sid, 'msg' => $c->get_error_message()]); cc_gc_tell_problem($sid, $c->get_error_message()); return; }
    return cc_gc_handle($s, $c['customers'] ?? []);
}

/* the decision, shared by the webhook and the staging simulator. Returns what happened. */
function cc_gc_handle($s, $c, $sim = false, $force = false) {   // $force: Matteo asked for this existing client (skips the "new" and test-mode checks only)
    $since = (int) get_option('cc_gc_since', 0); $sid = (string) ($s['id'] ?? ''); $cid = (string) ($c['id'] ?? '');
    $email = sanitize_email((string) ($c['email'] ?? '')); $first = sanitize_text_field((string) ($c['given_name'] ?? '')); $last = sanitize_text_field((string) ($c['family_name'] ?? ''));
    $name = trim("$first $last") ?: ($email ?: $cid);
    $signup = cc_gc_local_date((string) ($s['created_at'] ?? '')); $end = cc_gc_end($signup);
    $fee = isset($s['amount']) ? round(((int) $s['amount']) / 100, 2) : null; $cur = strtoupper((string) ($s['currency'] ?? 'EUR'));
    $info = ['name' => $name, 'email' => $email, 'customer' => $cid, 'sub' => $sid, 'sub_name' => (string) ($s['name'] ?? ''), 'fee' => $fee, 'currency' => $cur, 'signup' => $signup, 'end' => $end,
             'country' => strtolower((string) ($c['country_code'] ?? '')), 'lang' => cc_gc_lang($c)];
    // done before (GoCardless retries, two events for one subscription)
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => 1, 'fields' => 'ids', 'meta_key' => 'cc_gc_sub', 'meta_value' => $sid]) as $p) { cc_gc_log('already done', $info); return ['result' => 'already done'] + $info; }
    $why = '';
    if (!$force && !$since) $why = 'no cut-off date set';
    elseif (!$force && strtotime((string) ($s['created_at'] ?? '')) <= $since) $why = 'subscription created before the cut-off';
    elseif (!$force && strtotime((string) ($c['created_at'] ?? '')) <= $since) $why = 'existing GoCardless customer starting another subscription';
    elseif (($s['status'] ?? '') !== 'active') $why = 'subscription status is ' . ($s['status'] ?? 'unknown');
    elseif (!is_email($email)) $why = 'no email address on the customer';
    elseif (($u = get_user_by('email', $email))) $why = 'this email already has a hub login (' . $u->display_name . ')';
    if ($why !== '') { cc_gc_log('skipped', $info + ['why' => $why]); cc_gc_tell($info, 'skipped', $why, $sim); return ['result' => 'skipped', 'why' => $why] + $info; }
    if (cc_gc_mode() !== 'live' && !$sim && !$force) { cc_gc_log('test', $info); cc_gc_tell($info, 'test', '', $sim); return ['result' => 'test'] + $info; }
    // LIVE: the login, their page, the contract, the welcome email
    $login = sanitize_user(strtolower(strtok($email, '@')), true) ?: 'athlete'; $base = $login; $n = 1; while (username_exists($login)) $login = $base . (++$n);
    $uid = wp_insert_user(['user_login' => $login, 'user_email' => $email, 'user_pass' => wp_generate_password(24), 'first_name' => $first, 'last_name' => $last, 'display_name' => $name, 'role' => 'subscriber']);
    if (is_wp_error($uid)) { cc_gc_log('error', $info + ['msg' => $uid->get_error_message()]); cc_gc_tell($info, 'error', $uid->get_error_message(), $sim); return ['result' => 'error', 'why' => $uid->get_error_message()] + $info; }
    update_user_meta($uid, 'cc_lang', $info['lang']);
    $pid = cc_ath_page_of($uid, true);
    if ($pid) {
        update_post_meta($pid, 'cc_gc_sub', $sid); update_post_meta($pid, 'cc_gc_customer', $cid);
        update_post_meta($pid, 'cc_contract', wp_slash(wp_json_encode(['fee' => $fee, 'currency' => $cur, 'signup' => $signup, 'end' => $end, 'source' => 'gocardless', 'sub_name' => $info['sub_name']])));
        if ($info['country'] !== '' && (!defined('CC_F_COUNTRIES') || isset(CC_F_COUNTRIES[$info['country']]))) update_post_meta($pid, 'cc_nat', $info['country']);   // the athlete confirms it in the rider form
    }
    $w = $sim ? cc_ath_welcome_mail($uid, null, true) : cc_ath_welcome_mail($uid);   // the simulator never emails anyone
    $info['welcome'] = is_wp_error($w) ? 'failed: ' . $w->get_error_message() : ($sim ? 'not sent (simulation)' : 'sent');
    $info['page'] = $pid; cc_gc_log('created', $info); cc_gc_tell($info, 'created', '', $sim);
    return ['result' => 'created', 'user' => $uid] + $info;
}
function cc_gc_lang($c) {   // GoCardless' customer language, else the country's
    $l = strtolower((string) ($c['language'] ?? '')); $cc = strtoupper((string) ($c['country_code'] ?? ''));
    if (in_array($l, ['it', 'pt', 'sl'], true)) return $l;
    $by = ['IT' => 'it', 'SM' => 'it', 'PT' => 'pt', 'BR' => 'pt', 'SI' => 'sl'];
    return $by[$cc] ?? 'en';
}

/* ---------- Matteo's email ---------- */
function cc_gc_tell($i, $kind, $why = '', $sim = false) {
    $e = 'esc_html'; $board = add_query_arg('board', 'contracts', home_url('/' . CC_ATH_SLUG . '/'));
    $title = ['created' => 'New athlete: ' . $i['name'], 'test' => 'TEST MODE · would create: ' . $i['name'], 'skipped' => 'GoCardless signup, nothing done: ' . $i['name'], 'error' => 'Problem creating ' . $i['name']][$kind];
    $rows = [['Email', $i['email']], ['Country', strtoupper($i['country'])], ['Hub language', $i['lang']], ['Subscription', trim($i['sub_name'] . ' · ' . ($i['fee'] !== null ? number_format((float) $i['fee'], 2) . ' ' . $i['currency'] . ' / month' : ''), ' ·')],
             ['Signed up', $i['signup'] ? date_i18n('j M Y', strtotime($i['signup'])) : ''], ['Commitment ends', $i['end'] ? date_i18n('j M Y', strtotime($i['end'])) : '']];
    $h = '<div style="font-family:Montserrat,Helvetica,Arial,sans-serif;font-size:16px;color:#222"><h2>' . $e($title) . '</h2>';
    if ($kind === 'test') $h .= '<p style="margin:0 0 12px"><b>Test mode is on: nothing was created and nobody was emailed.</b> In live mode their hub login and welcome email would have gone out now.</p>';
    if ($kind === 'skipped') $h .= '<p style="margin:0 0 12px">Not treated as a new athlete: <b>' . $e($why) . '</b>. Check GoCardless if that is not right.</p>';
    if ($kind === 'error') $h .= '<p style="margin:0 0 12px;color:#b00">' . $e($why) . '</p>';
    $h .= '<table style="border-collapse:collapse;margin:0 0 16px">'; foreach ($rows as $r) if ($r[1] !== '') $h .= '<tr><td style="padding:3px 16px 3px 0;color:#555">' . $e($r[0]) . '</td><td style="padding:3px 0"><b>' . $e($r[1]) . '</b></td></tr>'; $h .= '</table>';
    if ($kind === 'created' || $kind === 'test') {
        $h .= '<p style="margin:0 0 6px"><b>' . ($kind === 'created' ? 'Done by the hub' : 'The hub would do') . '</b></p><ul style="margin:0 0 14px;padding-left:18px"><li>Hub login and their own page' . ($kind === 'created' ? ' ✔' : '') . '</li><li>Welcome email in their language' . ($kind === 'created' ? ' (' . $e($i['welcome'] ?? '') . ')' : '') . '</li><li>Rider form first, then guides, Vekta, Marine and Skool in the hub</li></ul>'
            . '<p style="margin:0 0 6px"><b>Your to-do</b></p><ul style="margin:0 0 14px;padding-left:18px"><li>☐ Invite them to Skool (Cigala Cycling Collective)</li><li>☐ Add them in Vekta</li><li>☐ Assessment once their rider form is signed (the hub emails you when it is)</li></ul>';
    }
    $h .= '<p style="margin:20px 0 0"><a href="' . esc_url($board) . '" style="display:inline-block;padding:12px 20px;border-radius:8px;background:#009a44;color:#fff;font-weight:600;text-decoration:none">Open Contracts</a></p></div>';
    if ($sim) { $GLOBALS['cc_gc_last_mail'] = ['subject' => $title, 'html' => $h]; return; }
    $hd = ['Content-Type: text/html; charset=UTF-8']; if (is_email($i['email'])) $hd[] = 'Reply-To: ' . $i['name'] . ' <' . $i['email'] . '>';
    if (function_exists('cc_ath_coach_wrap')) $h = cc_ath_coach_wrap($h);
    if (function_exists('cc_av_notify_to') && cc_av_notify_to()) wp_mail(cc_av_notify_to(), $title, $h, $hd);
}
function cc_gc_tell_problem($sid, $msg) {
    if (!function_exists('cc_av_notify_to') || !cc_av_notify_to()) return;
    wp_mail(cc_av_notify_to(), 'GoCardless signup: could not read it', '<p>A GoCardless subscription (' . esc_html($sid) . ') was created, but the hub could not read it: ' . esc_html($msg) . '.</p><p>Check the access token on the Contracts board, and the customer in GoCardless.</p>', ['Content-Type: text/html; charset=UTF-8']);
}

/* ---------- contracts: board, renewal reminders, laptop route ---------- */
function cc_gc_contracts() {
    $out = [];
    // athletes with a hub login, plus Basic 12-week athletes (Matteo 17 Nov: no hub, only their end date and the reminder; page meta cc_basic, no login)
    $ps = get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'meta_key' => 'cc_user', 'orderby' => 'title', 'order' => 'ASC']);
    $ps = array_merge($ps, get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'meta_key' => 'cc_basic', 'meta_value' => '1']));
    $seen = [];
    foreach ($ps as $p) {
        if (isset($seen[$p->ID])) continue; $seen[$p->ID] = 1;
        $basic = (bool) get_post_meta($p->ID, 'cc_basic', true);
        if (!$basic && (!($uid = (int) get_post_meta($p->ID, 'cc_user', true)) || !get_userdata($uid))) continue;
        $k = json_decode((string) get_post_meta($p->ID, 'cc_contract', true), true) ?: [];
        $out[] = ['page' => $p->ID, 'name' => $p->post_title, 'fee' => $k['fee'] ?? null, 'currency' => $k['currency'] ?? 'EUR', 'signup' => $k['signup'] ?? '', 'end' => $k['end'] ?? '', 'source' => $k['source'] ?? '',
                  'days_left' => !empty($k['end']) ? (int) floor((strtotime($k['end']) - strtotime(current_time('Y-m-d'))) / DAY_IN_SECONDS) : null,
                  'reminded' => (string) get_post_meta($p->ID, 'cc_contract_reminded', true), 'tp' => (bool) get_post_meta($p->ID, 'cc_tp', true), 'basic' => $basic];
    }
    usort($out, function ($a, $b) { return [$a['end'] === '' ? 1 : 0, $a['end'], $a['name']] <=> [$b['end'] === '' ? 1 : 0, $b['end'], $b['name']]; });
    return $out;
}
add_action('init', function () { if (!wp_next_scheduled('cc_gc_daily')) wp_schedule_event(strtotime('tomorrow 07:00 Europe/Dublin') ?: time() + HOUR_IN_SECONDS, 'daily', 'cc_gc_daily'); });
add_action('cc_gc_daily', function () {   // 15 days before the end: one email to Matteo per contract end, never to the athlete
    foreach (cc_gc_contracts() as $k) {
        if ($k['days_left'] === null || $k['days_left'] < 0 || $k['days_left'] > CC_GC_REMIND_DAYS || $k['reminded'] === $k['end']) continue;
        $board = add_query_arg('board', 'contracts', home_url('/' . CC_ATH_SLUG . '/'));
        $h = '<div style="font-family:Montserrat,Helvetica,Arial,sans-serif;font-size:16px;color:#222"><h2>' . ($k['basic'] ? 'Basic 12 weeks ending: ' : 'Commitment ending: ') . esc_html($k['name']) . '</h2><p style="margin:0 0 12px">' . ($k['basic'] ? 'Their 12-week Basic block ends on <b>' : 'Their 6-month commitment ends on <b>') . esc_html(date_i18n('j M Y', strtotime($k['end']))) . '</b> (' . (int) $k['days_left'] . ' days). '
           . ($k['basic'] ? 'Time to talk about what comes next: another block, or the Advanced package.' : 'Time for their review and a chat about what comes next.') . '</p>'
           . '<p style="margin:20px 0 0"><a href="' . esc_url($board) . '" style="display:inline-block;padding:12px 20px;border-radius:8px;background:#009a44;color:#fff;font-weight:600;text-decoration:none">Open Contracts</a></p></div>';
        if (function_exists('cc_ath_coach_wrap')) $h = cc_ath_coach_wrap($h);
        if (function_exists('cc_av_notify_to') && cc_av_notify_to() && wp_mail(cc_av_notify_to(), ($k['basic'] ? 'Basic 12 weeks ending: ' : 'Commitment ending: ') . $k['name'] . ' (' . date_i18n('j M', strtotime($k['end'])) . ')', $h, ['Content-Type: text/html; charset=UTF-8']))
            update_post_meta($k['page'], 'cc_contract_reminded', $k['end']);
    }
});
add_action('rest_api_init', function () {
    register_rest_route('cc/v1', '/contracts', ['methods' => 'GET', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function () { return cc_gc_contracts(); }]);
    // Matteo's CSV import from the old CRM (laptop): [{page|name, signup?, end, fee?}] — sets the contract, keeps a GoCardless one unless "force"
    register_rest_route('cc/v1', '/contracts', ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        $done = [];
        foreach ((array) $r->get_param('items') as $it) {
            if (!empty($it['basic_name']) && empty($it['page'])) {   // a Basic 12-week athlete: a private record with no login (never emailed, not in the hub)
                $nm = sanitize_text_field((string) $it['basic_name']);
                $ex = get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => 1, 'fields' => 'ids', 'title' => $nm, 'meta_key' => 'cc_basic', 'meta_value' => '1']);
                $it['page'] = $ex ? (int) $ex[0] : (int) wp_insert_post(['post_type' => 'cc_athlete', 'post_status' => 'private', 'post_title' => $nm, 'post_content' => '', 'meta_input' => ['cc_basic' => 1]]);
                $it['force'] = 1;
            }
            if (!empty($it['basic']) && !empty($it['page'])) update_post_meta((int) $it['page'], 'cc_basic', 1);
            $pid = (int) ($it['page'] ?? 0); if (get_post_type($pid) !== 'cc_athlete') { $done[] = ['page' => $pid, 'ok' => false, 'why' => 'no such athlete page']; continue; }
            if (array_key_exists('tp', $it)) update_post_meta($pid, 'cc_tp', $it['tp'] ? 1 : 0);   // TrainingPeaks athlete
            if (!empty($it['tp_only'])) { $done[] = ['page' => $pid, 'ok' => true, 'tp' => (bool) $it['tp']]; continue; }
            $old = json_decode((string) get_post_meta($pid, 'cc_contract', true), true) ?: [];
            if (($old['source'] ?? '') === 'gocardless' && empty($it['force'])) { $done[] = ['page' => $pid, 'ok' => false, 'why' => 'kept the GoCardless contract']; continue; }
            $end = preg_match('~^\d{4}-\d{2}-\d{2}$~', (string) ($it['end'] ?? '')) ? $it['end'] : ''; $su = preg_match('~^\d{4}-\d{2}-\d{2}$~', (string) ($it['signup'] ?? '')) ? $it['signup'] : '';
            update_post_meta($pid, 'cc_contract', wp_slash(wp_json_encode(['fee' => isset($it['fee']) && $it['fee'] !== '' ? (float) $it['fee'] : ($old['fee'] ?? null), 'currency' => 'EUR', 'signup' => $su ?: ($old['signup'] ?? ''), 'end' => $end ?: ($old['end'] ?? ''), 'source' => $it['source'] ?? 'crm import'])));
            $done[] = ['page' => $pid, 'ok' => true];
        }
        return $done;
    }]);
    // staging only: run the decision with made-up GoCardless objects (no API, nobody emailed)
    register_rest_route('cc/v1', '/gc-simulate', ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        if (strpos(home_url(), '//staging.') === false) return new WP_Error('cc_gc', 'Simulation runs on staging only', ['status' => 403]);
        if ($r->get_param('since')) update_option('cc_gc_since', (int) $r->get_param('since'), false);
        if ($r->has_param('test_secret')) { update_option('cc_gc_secret', (string) $r->get_param('test_secret'), false); return ['secret_set' => (bool) get_option('cc_gc_secret')]; }   // made-up secret for the signed-webhook test
        if ($r->get_param('cleanup')) { foreach (get_users(['search' => '*@example.com', 'search_columns' => ['user_email']]) as $u) if (strpos($u->user_email, 'gc-') === 0) { require_once ABSPATH . 'wp-admin/includes/user.php'; wp_delete_user($u->ID); }
            delete_option('cc_gc_log'); return ['cleaned' => true]; }
        $GLOBALS['cc_gc_last_mail'] = null;
        $res = cc_gc_handle((array) $r->get_param('subscription'), (array) $r->get_param('customer'), true);
        return $res + ['matteo_email' => $GLOBALS['cc_gc_last_mail']];
    }]);
    // read-only: subscriptions created after a date, with their customer and whether they already have a hub login (gap check)
    register_rest_route('cc/v1', '/gc-recent', ['methods' => 'GET', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        $after = preg_match('~^\d{4}-\d{2}-\d{2}~', (string) $r['after']) ? substr($r['after'], 0, 10) . 'T00:00:00.000Z' : gmdate('Y-m-d\TH:i:s.000\Z', time() - 30 * DAY_IN_SECONDS);
        $out = []; $cur = '';
        for ($i = 0; $i < 10; $i++) {
            $j = cc_gc_get('/subscriptions?limit=100&created_at%5Bgt%5D=' . rawurlencode($after) . ($cur ? '&after=' . rawurlencode($cur) : '')); if (is_wp_error($j)) return $j;
            foreach ((array) ($j['subscriptions'] ?? []) as $s) {
                $m = cc_gc_get('/mandates/' . rawurlencode((string) ($s['links']['mandate'] ?? ''))); $c = is_wp_error($m) ? [] : cc_gc_get('/customers/' . rawurlencode((string) ($m['mandates']['links']['customer'] ?? '')));
                $c = is_wp_error($c) ? [] : ($c['customers'] ?? []); $u = !empty($c['email']) ? get_user_by('email', $c['email']) : null;
                $out[] = ['sub' => $s['id'], 'sub_name' => $s['name'] ?? '', 'status' => $s['status'] ?? '', 'created' => $s['created_at'] ?? '', 'amount' => isset($s['amount']) ? $s['amount'] / 100 : null,
                          'customer' => trim(($c['given_name'] ?? '') . ' ' . ($c['family_name'] ?? '')), 'customer_created' => $c['created_at'] ?? '', 'country' => $c['country_code'] ?? '', 'in_hub' => $u ? $u->display_name : null];
            }
            $cur = (string) ($j['meta']['cursors']['after'] ?? ''); if ($cur === '') break;
        }
        return $out;
    }]);
    // Matteo's yes for an existing paying client without a hub login: create it from their GoCardless subscription (login, page, contract, welcome email)
    register_rest_route('cc/v1', '/gc-create', ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        $sid = (string) $r['sub'];
        $s = cc_gc_get('/subscriptions/' . rawurlencode($sid)); if (is_wp_error($s)) return $s; $s = $s['subscriptions'] ?? [];
        $m = cc_gc_get('/mandates/' . rawurlencode((string) ($s['links']['mandate'] ?? ''))); if (is_wp_error($m)) return $m;
        $c = cc_gc_get('/customers/' . rawurlencode((string) ($m['mandates']['links']['customer'] ?? ''))); if (is_wp_error($c)) return $c;
        if ($r['any_status']) $s['status'] = 'active';   // e.g. coaching extended outside GoCardless (Brian McDonnell, 17 Nov 2026)
        $res = cc_gc_handle($s, $c['customers'] ?? [], (bool) $r['dry'] && strpos(home_url(), '//staging.') !== false, true);
        unset($res['email']); return $res;   // the email stays in the hub
    }]);
    register_rest_route('cc/v1', '/gc-end', ['methods' => 'GET', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) { return ['signup' => $r['d'], 'end' => cc_gc_end((string) $r['d'])]; }]);
    register_rest_route('cc/v1', '/gc-status', ['methods' => 'GET', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function () {
        return ['mode' => cc_gc_mode(), 'since' => (int) get_option('cc_gc_since', 0) ?: null, 'secret_set' => (bool) get_option('cc_gc_secret', ''), 'token_set' => (bool) get_option('cc_gc_token', ''),
                'webhook_url' => rest_url('cc/v1/gocardless'), 'log' => array_slice((array) get_option('cc_gc_log', []), 0, 20)];
    }]);
});

add_filter('cc_ath_coach_links', function ($html) {
    $n = 0; foreach (cc_gc_contracts() as $k) if ($k['days_left'] !== null && $k['days_left'] >= 0 && $k['days_left'] <= CC_GC_REMIND_DAYS) $n++;
    return $html . '<a class="av-boardlink" href="' . esc_url(add_query_arg('board', 'contracts', home_url('/' . CC_ATH_SLUG . '/'))) . '">Contracts' . ($n ? ' <span class="av-badge">' . $n . ' ending soon</span>' : '') . '</a>';
}, 35);
add_filter('cc_ath_board', function ($html, $board) {
    if ($board !== 'contracts' || !cc_ath_is_coach()) return $html;
    $r = sanitize_key($_GET['gc'] ?? ''); $f = function ($d) { return $d ? esc_html(date_i18n('j M Y', strtotime($d))) : '—'; };
    $o = '<section class="ath-s"><h2>Contracts</h2><p class="av-lede">Every athlete with their fee and 6-month commitment, the soonest ending first. 15 days before an end you get an email (the athlete never does). New GoCardless signups appear here by themselves.</p>';
    $o .= '<div class="gc-tw"><table class="gc-t"><thead><tr><th>Athlete</th><th>Fee / month</th><th>Signed up</th><th>Commitment ends</th><th></th><th>TrainingPeaks</th></tr></thead><tbody>';
    foreach (cc_gc_contracts() as $k) {
        $soon = $k['days_left'] !== null && $k['days_left'] >= 0 && $k['days_left'] <= CC_GC_REMIND_DAYS; $past = $k['days_left'] !== null && $k['days_left'] < 0;
        $hasHub = (bool) get_post_meta($k['page'], 'cc_user', true);
        $o .= '<tr' . ($soon ? ' class="soon"' : '') . '><td>' . ($hasHub ? '<a href="' . esc_url(add_query_arg('view', $k['page'], home_url('/' . CC_ATH_SLUG . '/'))) . '">' . esc_html($k['name']) . '</a>' : esc_html($k['name']))
            . ($k['basic'] ? ' <small>Basic 12 weeks' . ($hasHub ? '' : ' · no hub') . '</small>' : '') . '</td><td>' . ($k['fee'] !== null ? esc_html(number_format((float) $k['fee'], 2) . ' ' . $k['currency']) : '—') . '</td><td>' . $f($k['signup']) . '</td><td>' . $f($k['end'])
            . ($soon ? ' <span class="av-badge">' . (int) $k['days_left'] . ' days</span>' : ($past ? ' <small>past: rolling monthly</small>' : '')) . '</td>'
            . '<td><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" class="gc-ed"><input type="hidden" name="action" value="cc_gc_end"><input type="hidden" name="page" value="' . (int) $k['page'] . '">' . wp_nonce_field('cc_gc_end', '_wpnonce', false, false)
            . '<input type="date" name="end" value="' . esc_attr($k['end']) . '" aria-label="Commitment end for ' . esc_attr($k['name']) . '"><button class="btn btn-ghost" type="submit">Save</button></form></td>'
            . '<td><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="cc_gc_tp"><input type="hidden" name="page" value="' . (int) $k['page'] . '">' . wp_nonce_field('cc_gc_tp', '_wpnonce', false, false)
            . '<label class="gc-tp"><input type="checkbox" name="tp" value="1"' . ($k['tp'] ? ' checked' : '') . ' onchange="this.form.submit()" aria-label="' . esc_attr($k['name']) . ' trains in TrainingPeaks"> TP</label></form></td></tr>';
    }
    $o .= '</tbody></table></div></section>';
    // GoCardless connection
    $mode = cc_gc_mode(); $since = (int) get_option('cc_gc_since', 0); $sec = (bool) get_option('cc_gc_secret', ''); $tok = (bool) get_option('cc_gc_token', '');
    $msg = ['saved' => 'Saved.', 'live' => 'Live: new signups now get their login and welcome email automatically.', 'test' => 'Test mode: signups only send you an email.', 'ok' => 'Connected to GoCardless: ', 'bad' => 'GoCardless did not accept the token: '][$r] ?? '';
    $o .= '<section class="ath-s gc-set"><h3 class="av-sub" style="margin-top:0">GoCardless connection</h3><p class="av-lede">Mode: <b style="color:' . ($mode === 'live' ? '#34c46a' : '#f0b429') . '">' . ($mode === 'live' ? 'LIVE' : 'TEST (nothing is created, you only get an email)') . '</b>'
        . ($since ? ' · signups after ' . esc_html(date_i18n('j M Y H:i', $since)) . ' count as new' : '') . '</p>'
        . '<p class="av-lede">In GoCardless: Developers → Create → <b>Webhook endpoint</b>, URL <code>' . esc_html(rest_url('cc/v1/gocardless')) . '</code>, then copy its secret here. Developers → Create → <b>Access token</b>, <b>read-only</b>, and paste it here.</p>'
        . '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" class="rp-smtp-f" autocomplete="off"><input type="hidden" name="action" value="cc_gc_set">' . wp_nonce_field('cc_gc_set', '_wpnonce', false, false)
        . '<label>Webhook secret <input type="password" name="secret" autocomplete="new-password" placeholder="' . ($sec ? 'Saved · type only to change it' : 'From the webhook endpoint') . '"></label>'
        . '<label>Read-only access token <input type="password" name="token" autocomplete="new-password" placeholder="' . ($tok ? 'Saved · type only to change it' : 'Starts with live_') . '"></label>'
        . '<input type="hidden" name="act" value="save"><span class="rp-acts"><button class="btn btn-go" type="submit">Save and check</button>'
        . ($sec && $tok ? ($mode === 'live' ? '<button class="btn btn-ghost" type="submit" onclick="this.form.act.value=\'test\'">Back to test mode</button>' : '<button class="btn btn-ghost" type="submit" onclick="if(!confirm(\'Go live? From now on a new GoCardless signup gets a hub login and the welcome email straight away.\'))return false;this.form.act.value=\'live\'">Go live</button>') : '') . '</span></form>'
        . ($msg ? '<p class="rp-smtp-m"' . ($r === 'bad' ? ' style="color:#ff4a3d"' : '') . '>' . esc_html($msg . (string) get_transient('cc_gc_msg')) . '</p>' : '');
    $log = array_slice((array) get_option('cc_gc_log', []), 0, 10);
    if ($log) { $o .= '<h3 class="av-sub">Latest signups</h3><ul class="gc-log">'; foreach ($log as $l) $o .= '<li><small>' . esc_html(date_i18n('j M H:i', (int) $l['at'])) . '</small> <b>' . esc_html($l['what']) . '</b> ' . esc_html(($l['name'] ?? '') . (!empty($l['why']) ? ' · ' . $l['why'] : '') . (!empty($l['msg']) ? ' · ' . $l['msg'] : '')) . '</li>'; $o .= '</ul>'; }
    $o .= '</section><style>html .cc .gc-tw{overflow-x:auto}html .cc .gc-t{width:100%;border-collapse:collapse;font-size:16px}html .cc .gc-t th{text-align:left;font-size:14px;color:#b8bec8;font-weight:600;padding:8px 10px;border-bottom:1px solid rgba(255,255,255,.15)}'
        . 'html .cc .gc-t td{padding:10px;border-bottom:1px solid rgba(255,255,255,.08);vertical-align:middle}html .cc .gc-t td a{color:#fff}html .cc .gc-t tr.soon td{background:rgba(240,180,41,.08)}html .cc .gc-t small{color:#b8bec8;font-size:14px}'
        . 'html .cc .gc-ed{display:flex;gap:8px;align-items:center}html .cc .gc-ed input{font:16px var(--body);padding:8px 10px;border-radius:10px;border:1px solid rgba(255,255,255,.2);background:#0b0d0f;color:#fff}'
        . 'html .cc .gc-tp{display:flex;gap:8px;align-items:center;font-size:15px;color:#d0d6e0;white-space:nowrap}html .cc .gc-tp input{width:20px;height:20px}html .cc .gc-log{margin:0;padding-left:18px;font-size:15px;color:#d0d6e0}html .cc .gc-log small{color:#b8bec8}html .cc .gc-set code{font-size:14px;word-break:break-all}</style>';
    return $o;
}, 10, 2);
add_action('admin_post_cc_gc_tp', function () {   // TrainingPeaks athlete: no Availability / Goals / Vekta section in their hub, a TrainingPeaks card instead
    if (!cc_ath_is_coach() || !wp_verify_nonce($_POST['_wpnonce'] ?? '', 'cc_gc_tp')) wp_die('Not allowed');
    $pid = (int) ($_POST['page'] ?? 0); if (get_post_type($pid) === 'cc_athlete') update_post_meta($pid, 'cc_tp', empty($_POST['tp']) ? 0 : 1);
    wp_safe_redirect(add_query_arg('board', 'contracts', home_url('/' . CC_ATH_SLUG . '/'))); exit;
});
add_action('admin_post_cc_gc_end', function () {
    if (!cc_ath_is_coach() || !wp_verify_nonce($_POST['_wpnonce'] ?? '', 'cc_gc_end')) wp_die('Not allowed');
    $pid = (int) ($_POST['page'] ?? 0); $end = sanitize_text_field($_POST['end'] ?? '');
    if (get_post_type($pid) === 'cc_athlete') { $k = json_decode((string) get_post_meta($pid, 'cc_contract', true), true) ?: []; $k['end'] = preg_match('~^\d{4}-\d{2}-\d{2}$~', $end) ? $end : ''; update_post_meta($pid, 'cc_contract', wp_slash(wp_json_encode($k))); }
    wp_safe_redirect(add_query_arg('board', 'contracts', home_url('/' . CC_ATH_SLUG . '/'))); exit;
});
add_action('admin_post_cc_gc_set', function () {
    if (!cc_ath_is_coach() || !wp_verify_nonce($_POST['_wpnonce'] ?? '', 'cc_gc_set')) wp_die('Not allowed');
    $act = sanitize_key($_POST['act'] ?? 'save'); $r = 'saved';
    $s = trim(wp_unslash((string) ($_POST['secret'] ?? ''))); $t = trim(wp_unslash((string) ($_POST['token'] ?? '')));
    if ($s !== '') update_option('cc_gc_secret', $s, false);
    if ($t !== '') update_option('cc_gc_token', $t, false);
    if (!get_option('cc_gc_since')) update_option('cc_gc_since', time(), false);   // from the first save on, new signups count as new
    if ($act === 'live' && get_option('cc_gc_secret') && get_option('cc_gc_token')) { update_option('cc_gc_mode', 'live', false); $r = 'live'; }
    elseif ($act === 'test') { update_option('cc_gc_mode', 'test', false); $r = 'test'; }
    elseif (get_option('cc_gc_token')) { $c = cc_gc_get('/creditors?limit=1'); if (is_wp_error($c)) { $r = 'bad'; set_transient('cc_gc_msg', $c->get_error_message(), 120); } else { $r = 'ok'; set_transient('cc_gc_msg', (string) ($c['creditors'][0]['name'] ?? ''), 120); } }
    wp_safe_redirect(add_query_arg(['board' => 'contracts', 'gc' => $r], home_url('/' . CC_ATH_SLUG . '/'))); exit;
});
