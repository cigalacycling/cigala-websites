<?php
/* Routes for Matteo's laptop (Vekta "Season Plan" chat brief, 17 Nov 2026). Pushed with --availability. Documented in PC-TOOLS-HANDOVER.md.
 * Auth: Matteo's application password (Basic auth), admin/editor only. Read-only except setting the Vekta id / nationality after Matteo confirms.
 *   GET  /wp-json/cc/v1/athletes[?email=|?vekta_id=|?page=|?since=UNIX|&former=1]   everything per athlete
 *   POST /wp-json/cc/v1/athlete-meta {page|email|vekta_id, set: {vekta_id?, nationality?}}
 * Athlete matching: Vekta has no email, so the laptop matches by full name once, Matteo confirms, then stores cc_vekta_id here.
 */
if (!defined('ABSPATH')) return;

add_action('init', function () {
    register_meta('user', 'cc_vekta_id', ['type' => 'string', 'single' => true, 'show_in_rest' => true, 'auth_callback' => function () { return current_user_can('edit_users'); }]);
});
// Users > Edit: the Vekta id under "Athlete hub"
function cc_pc_vekta_field($user) {
    if (!($user instanceof WP_User)) return;
    echo '<table class="form-table" role="presentation"><tr><th><label for="cc_vekta_id">Vekta user id</label></th><td><input type="text" name="cc_vekta_id" id="cc_vekta_id" class="regular-text" value="'
       . esc_attr(get_user_meta($user->ID, 'cc_vekta_id', true)) . '"><p class="description">Links this login to the athlete in Vekta (set once; the laptop can fill it after you confirm the match).</p></td></tr></table>';
}
add_action('show_user_profile', 'cc_pc_vekta_field', 20); add_action('edit_user_profile', 'cc_pc_vekta_field', 20);
function cc_pc_vekta_save($uid) { if (isset($_POST['cc_vekta_id']) && current_user_can('edit_users')) update_user_meta($uid, 'cc_vekta_id', sanitize_text_field(wp_unslash($_POST['cc_vekta_id']))); }
add_action('edit_user_profile_update', 'cc_pc_vekta_save'); add_action('personal_options_update', 'cc_pc_vekta_save');

function cc_pc_nat($pid) {   // the athlete's own answer in the rider form wins; else what Matteo/the laptop set; else ''
    $p = json_decode((string) get_post_meta($pid, 'cc_profile', true), true) ?: [];
    return (string) (!empty($p['nat']) ? $p['nat'] : get_post_meta($pid, 'cc_nat', true));
}
function cc_pc_flag_emoji($code, $is_nat = true) {   // for the laptop's pages: the athlete's flag (nationality, else their language's country)
    $c = strtolower((string) $code); if (!$is_nat) $c = ['it' => 'it', 'sl' => 'si', 'sk' => 'sk', 'pt' => 'pt', 'es' => 'es', 'fr' => 'fr', 'hr' => 'hr', 'de' => 'de', 'nl' => 'nl', 'pl' => 'pl', 'cs' => 'cz', 'da' => 'dk', 'sv' => 'se', 'no' => 'no', 'fi' => 'fi', 'ga' => 'ie'][$c] ?? '';
    if (in_array($c, ['gb-eng', 'gb-sct', 'gb-wls'], true)) { $f = mb_chr(0x1F3F4, 'UTF-8'); foreach (str_split(str_replace('-', '', $c)) as $ch) $f .= mb_chr(0xE0000 + ord($ch), 'UTF-8'); return $f . mb_chr(0xE007F, 'UTF-8'); }
    if ($c === 'gb-nir') $c = 'gb';
    if (!preg_match('/^[a-z]{2}$/', $c)) return null;
    $f = ''; foreach (str_split(strtoupper($c)) as $ch) $f .= mb_chr(0x1F1E6 + ord($ch) - 65, 'UTF-8'); return $f;
}
function cc_pc_page_from(WP_REST_Request $r) {
    if ($r->get_param('page')) { $pid = (int) $r->get_param('page'); return get_post_type($pid) === 'cc_athlete' ? $pid : 0; }
    if ($r->get_param('email')) { $u = get_user_by('email', (string) $r->get_param('email')); return $u ? cc_ath_page_of($u->ID) : 0; }
    if ($r->get_param('vekta_id') !== null && $r->get_param('vekta_id') !== '') {
        $us = get_users(['meta_key' => 'cc_vekta_id', 'meta_value' => (string) $r->get_param('vekta_id'), 'number' => 2, 'fields' => 'ID']);
        return count($us) === 1 ? cc_ath_page_of((int) $us[0]) : 0;
    }
    return 0;
}
function cc_pc_one($p, $since) {
    $uid = (int) get_post_meta($p->ID, 'cc_user', true); $u = $uid ? get_userdata($uid) : null;
    $av = function_exists('cc_av_get') ? cc_av_get($p->ID) : null; $avu = (int) get_post_meta($p->ID, 'cc_avail_updated', true);
    $g = function_exists('cc_g_get') ? cc_g_get($p->ID) : null; $gu = (int) ($g['updated'] ?? 0);
    $coach = get_current_user_id();
    $avseen = (int) get_user_meta($coach, 'cc_avail_seen', true); $gseen = (int) get_user_meta($coach, 'cc_goals_seen', true);
    if ($since && max($avu, $gu, $uid ? (int) get_user_meta($uid, 'cc_form_done', true) : 0) <= $since) return null;
    $signed = json_decode((string) get_post_meta($p->ID, 'cc_form_signed', true), true) ?: [];
    $nat = cc_pc_nat($p->ID);
    $live = [];
    foreach (defined('CC_R_LIVE') ? CC_R_LIVE : ['season'] as $t) {
        $x = get_posts(['post_type' => 'cc_report', 'post_status' => 'private', 'post_parent' => $p->ID, 'numberposts' => 1, 'orderby' => 'meta_value_num', 'meta_key' => 'cc_published', 'order' => 'DESC', 'meta_query' => [['key' => 'cc_type', 'value' => $t]]]);
        $live[$t] = ['published' => $x ? ['id' => $x[0]->ID, 'at' => (int) get_post_meta($x[0]->ID, 'cc_published', true)] : null, 'auto' => function_exists('cc_r_auto') && cc_r_auto($p->ID, $t)];
    }
    $season = $live['season']['published'] ?? null;
    return [
        'page' => $p->ID, 'status' => $u ? 'active' : 'former', 'ended' => (int) get_post_meta($p->ID, 'cc_ended', true) ?: null,
        'name' => preg_replace('/^Former athlete: /', '', get_post_field('post_title', $p->ID)), 'first_name' => $u ? $u->first_name : null, 'last_name' => $u ? $u->last_name : null,
        'email' => $u ? $u->user_email : null, 'vekta_id' => $u ? ((string) get_user_meta($uid, 'cc_vekta_id', true) ?: null) : null,
        'language' => $u ? cc_ath_lang_code($uid) : null, 'language_name' => $u ? (CC_REPORT_LANGS[cc_ath_lang_code($uid)] ?? null) : null,
        'nationality' => $nat !== '' ? strtoupper($nat) : null, 'flag_emoji' => cc_pc_flag_emoji($nat !== '' ? $nat : ($u ? cc_ath_lang_code($uid) : ''), $nat !== ''),
        'nationality_name' => $nat !== '' && defined('CC_F_COUNTRIES') ? (CC_F_COUNTRIES[$nat] ?? null) : null,
        'photo' => function_exists('cc_ph_url') ? (cc_ph_url($p->ID) ?: null) : null,   // Matteo 18 Nov: the athlete's face on their reports
        'form' => ['status' => $u && function_exists('cc_f_status') ? cc_f_status($uid) : null, 'signed_at' => $signed['at'] ?? null, 'kind' => $signed['kind'] ?? null],
        'availability' => $av ? ['data' => $av, 'updated' => $avu ?: null, 'status' => $avu > $avseen ? 'new' : 'seen'] : null,
        'goals' => $g ? ['short' => $g['short'] ?? '', 'long' => $g['long'] ?? '', 'events' => array_map(function ($e) {   // Matteo 17 Nov: route for the race day simulation (file: GET /cc/v1/route?id=route_id; link: route_link)
                             if (($e['route_type'] ?? '') === 'link') $e['route_url'] = $e['route_link'] ?? null;
                             elseif (!empty($e['route_id'])) { $e['route_url'] = wp_get_attachment_url((int) $e['route_id']); $e['route_file_api'] = rest_url('cc/v1/route?id=' . (int) $e['route_id']); }
                             return $e; }, $g['events'] ?? []), 'from_form' => $g['from_form'] ?? '',
                         'updated' => $gu ?: null, 'changed_by' => !empty($g['by_coach']) && (int) $g['by_coach'] === $gu ? 'matteo' : 'athlete', 'status' => $gu > $gseen ? 'new' : 'seen'] : null,
        // Matteo 18 Nov (hub announcement): who already has their login details
        'login' => $u ? ['user' => $uid, 'welcome_sent' => (string) get_user_meta($uid, 'cc_welcome_sent', true) ?: null, 'password_set' => (string) get_user_meta($uid, 'cc_pw_set', true) ?: null,
                         'registered' => $u->user_registered, 'last_login' => (int) get_user_meta($uid, 'cc_last_login', true) ?: null] : null,
        'season_published' => $season, 'live_pages' => $live,   // live_pages: season / prediction / snapshot, latest published + whether new versions go live automatically
    ];
}
add_action('rest_api_init', function () {
    register_rest_route('cc/v1', '/athletes', ['methods' => 'GET', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        $one = $r->get_param('page') || $r->get_param('email') || ($r->get_param('vekta_id') !== null && $r->get_param('vekta_id') !== '');
        if ($one) { $pid = cc_pc_page_from($r); if (!$pid) return new WP_Error('cc_none', 'No such athlete', ['status' => 404]); return array_values(array_filter([cc_pc_one(get_post($pid), 0)])); }
        $out = []; $since = (int) $r->get_param('since');
        foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'orderby' => 'title', 'order' => 'ASC']) as $p) {
            if (get_post_meta($p->ID, 'cc_shared', true)) continue;
            if (!get_post_meta($p->ID, 'cc_user', true) && !$r->get_param('former')) continue;
            if ($x = cc_pc_one($p, $since)) $out[] = $x;
        }
        return $out;
    }]);
    register_rest_route('cc/v1', '/athlete-meta', ['methods' => 'POST', 'permission_callback' => function () { return current_user_can('edit_users'); }, 'callback' => function (WP_REST_Request $r) {
        $pid = cc_pc_page_from($r); $uid = $pid ? (int) get_post_meta($pid, 'cc_user', true) : 0;
        if (!$uid) return new WP_Error('cc_none', 'No such active athlete', ['status' => 404]);
        $set = (array) $r->get_param('set');
        if (array_key_exists('vekta_id', $set)) {
            $v = sanitize_text_field((string) $set['vekta_id']);
            if ($v !== '' && array_diff(get_users(['meta_key' => 'cc_vekta_id', 'meta_value' => $v, 'fields' => 'ID']), [$uid])) return new WP_Error('cc_dup', 'That Vekta id is already on another athlete', ['status' => 409]);
            update_user_meta($uid, 'cc_vekta_id', $v);
        }
        if (array_key_exists('nationality', $set)) {   // only when the athlete has not answered it in the rider form (their answer wins)
            $n = strtolower((string) $set['nationality']);
            if ($n !== '' && defined('CC_F_COUNTRIES') && !isset(CC_F_COUNTRIES[$n])) return new WP_Error('cc_nat', 'Unknown nationality code', ['status' => 400]);
            update_post_meta($pid, 'cc_nat', $n);
        }
        return cc_pc_one(get_post($pid), 0);
    }]);
});
