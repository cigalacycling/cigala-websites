<?php
/* "My goals & events" (Matteo, 16 Nov 2026): the athlete keeps their goals and events here (never in Vekta); Matteo gets an email
 * on every change; his Claude-Vekta session reads them (GET /wp-json/cc/v1/goals) for planning, periodization and calendar notes.
 * Starts from the rider form's goals. Shown after "My availability". Pushed with --availability. Needs availability.php (helpers).
 */
if (!defined('ABSPATH')) return;

const CC_G_TYPES = ['race' => 'Race', 'sportive' => 'Sportive / Gran Fondo', 'camp' => 'Camp or trip', 'other' => 'Other'];
/* Matteo 20 Nov: athletes add races only in the hub now, so each event carries what a Vekta event holds. 'disc' = Vekta's subSport
 * (road|gravel|mtb|tt|cx|track|other, '' = not chosen); the laptop sync reads it from GET /cc/v1/athletes goals.events. */
const CC_G_DISC = ['road' => 'Road', 'gravel' => 'Gravel', 'mtb' => 'MTB', 'tt' => 'Time trial', 'cx' => 'Cyclocross', 'track' => 'Track', 'other' => 'Other'];
/* The form's own words for these fields (athlete's hub language; English for any other) */
function cc_g_w($k, $lang) {
    static $W = [
        'more' => ['en' => 'More details (optional)', 'it' => 'Altri dettagli (facoltativi)', 'pt' => 'Mais detalhes (opcional)', 'sl' => 'Več podrobnosti (neobvezno)', 'sk' => 'Ďalšie podrobnosti (nepovinné)'],
        'moresub' => ['en' => 'Discipline, start time, distance, climbing, route', 'it' => 'Disciplina, orario di partenza, distanza, dislivello, percorso',
                      'pt' => 'Disciplina, hora de partida, distância, subida, percurso', 'sl' => 'Disciplina, čas starta, razdalja, vzpon, proga', 'sk' => 'Disciplína, čas štartu, vzdialenosť, prevýšenie, trať'],
        'disc' => ['en' => 'Discipline', 'it' => 'Disciplina', 'pt' => 'Disciplina', 'sl' => 'Disciplina', 'sk' => 'Disciplína'],
        'choose' => ['en' => 'Choose…', 'it' => 'Scegli…', 'pt' => 'Escolher…', 'sl' => 'Izberi…', 'sk' => 'Vyber…'],
        'road' => ['en' => 'Road', 'it' => 'Strada', 'pt' => 'Estrada', 'sl' => 'Cesta', 'sk' => 'Cesta'],
        'gravel' => ['en' => 'Gravel', 'it' => 'Gravel', 'pt' => 'Gravel', 'sl' => 'Gravel', 'sk' => 'Gravel'],
        'mtb' => ['en' => 'MTB', 'it' => 'MTB', 'pt' => 'BTT', 'sl' => 'MTB', 'sk' => 'MTB'],
        'tt' => ['en' => 'Time trial', 'it' => 'Cronometro', 'pt' => 'Contrarrelógio', 'sl' => 'Kronometer', 'sk' => 'Časovka'],
        'cx' => ['en' => 'Cyclocross', 'it' => 'Ciclocross', 'pt' => 'Ciclocrosse', 'sl' => 'Ciklokros', 'sk' => 'Cyklokros'],
        'track' => ['en' => 'Track', 'it' => 'Pista', 'pt' => 'Pista', 'sl' => 'Steza', 'sk' => 'Dráha'],
        'other' => ['en' => 'Other', 'it' => 'Altro', 'pt' => 'Outra', 'sl' => 'Drugo', 'sk' => 'Iné'],
        'dist' => ['en' => 'Distance (km)', 'it' => 'Distanza (km)', 'pt' => 'Distância (km)', 'sl' => 'Razdalja (km)', 'sk' => 'Vzdialenosť (km)'],
        'elev' => ['en' => 'Climbing (m)', 'it' => 'Dislivello (m)', 'pt' => 'Subida acumulada (m)', 'sl' => 'Vzpon (m)', 'sk' => 'Prevýšenie (m)'],
        'vk' => ['en' => 'These go to your Vekta calendar.', 'it' => 'Questi dati vanno nel tuo calendario Vekta.', 'pt' => 'Estes dados vão para o teu calendário Vekta.',
                 'sl' => 'Ti podatki gredo v tvoj koledar Vekta.', 'sk' => 'Tieto údaje sa prenesú do tvojho kalendára Vekta.'],
        'rs' => ['en' => 'From your route: %s', 'it' => 'Dal tuo percorso: %s', 'pt' => 'Do teu percurso: %s', 'sl' => 'Iz tvoje proge: %s', 'sk' => 'Z tvojej trate: %s'],
        'use' => ['en' => 'Use the route’s numbers: %s', 'it' => 'Usa i dati del percorso: %s', 'pt' => 'Usar os números do percurso: %s', 'sl' => 'Uporabi podatke proge: %s', 'sk' => 'Použiť údaje z trate: %s'],
        'fill' => ['en' => 'Distance and climbing filled in from your route.', 'it' => 'Distanza e dislivello presi dal tuo percorso.', 'pt' => 'Distância e subida preenchidas a partir do teu percurso.',
                   'sl' => 'Razdalja in vzpon sta izpolnjena iz tvoje proge.', 'sk' => 'Vzdialenosť a prevýšenie sú doplnené z tvojej trate.'],
    ];
    $l = isset($W[$k][$lang]) ? $lang : 'en';
    return $W[$k][$l] ?? $k;
}
function cc_r_date_safe($ts) { return function_exists('cc_r_date') ? cc_r_date($ts) : date_i18n('j M Y', $ts); }   // dates in the athlete's language (reports.php)
function cc_g_get($pid) { $g = json_decode((string) get_post_meta($pid, 'cc_goals', true), true); return is_array($g) ? $g : null; }
function cc_g_clean($in, $pid = 0) {
    $in = is_array($in) ? $in : [];
    $out = ['short' => cc_av_note($in['short'] ?? '', 1500), 'long' => cc_av_note($in['long'] ?? '', 1500), 'events' => []];
    foreach (array_slice((array) ($in['events'] ?? []), 0, 40) as $e) {
        $name = cc_av_str($e['name'] ?? '', 120); $date = cc_av_date($e['date'] ?? '');
        if ($name === '' || !$date) continue;
        $out['events'][] = ['name' => $name, 'date' => $date, 'type' => isset(CC_G_TYPES[$e['type'] ?? '']) ? $e['type'] : 'race',
            'prio' => in_array($e['prio'] ?? '', ['A', 'B', 'C'], true) ? $e['prio'] : 'B',
            'disc' => isset(CC_G_DISC[$e['disc'] ?? '']) ? $e['disc'] : '',
            'dist' => is_numeric($e['dist'] ?? '') ? 0 + $e['dist'] : '', 'elev' => is_numeric($e['elev'] ?? '') ? 0 + $e['elev'] : '', 'note' => cc_av_str($e['note'] ?? '', 300)]
            + cc_g_route_clean($e, $pid);
    }
    usort($out['events'], function ($a, $b) { return strcmp($a['date'], $b['date']); });
    return $out;
}
/* Matteo 17 Nov: each race can carry its route (an uploaded .gpx/.fit/.tcx, kept private, or a link) and a start time, so the laptop can
 * build the race day simulation. Fields: start "HH:MM", route_type gpx|fit|tcx|link, route_id (private file), route_name, route_link, route_at. */
const CC_G_ROUTE_EXT = ['gpx' => 'application/gpx+xml', 'fit' => 'application/vnd.ant.fit', 'tcx' => 'application/vnd.garmin.tcx+xml'];
function cc_g_route_clean($e, $pid) {
    $o = [];
    if (preg_match('/^([01]\d|2[0-3]):[0-5]\d$/', (string) ($e['start'] ?? ''))) $o['start'] = $e['start'];
    $id = (int) ($e['route_id'] ?? 0);
    if ($id && $pid && get_post_type($id) === 'attachment' && (int) get_post_field('post_parent', $id) === (int) $pid && function_exists('cc_ath_is_private_file') && cc_ath_is_private_file($id)) {
        $ext = strtolower(pathinfo((string) get_attached_file($id), PATHINFO_EXTENSION));
        if (isset(CC_G_ROUTE_EXT[$ext])) {
            $o += ['route_type' => $ext, 'route_id' => $id, 'route_name' => cc_av_str($e['route_name'] ?? get_the_title($id), 120)];
            /* 20 Nov: distance and climbing the browser read from the route file (shown under the route) */
            if (is_numeric($e['route_km'] ?? '') && $e['route_km'] > 0 && $e['route_km'] < 2000) $o['route_km'] = round((float) $e['route_km'], 1);
            if (is_numeric($e['route_m'] ?? '') && $e['route_m'] >= 0 && $e['route_m'] < 30000) $o['route_m'] = (int) round((float) $e['route_m']);
        }
    } elseif (($l = esc_url_raw(trim((string) ($e['route_link'] ?? '')), ['https', 'http'])) !== '') {
        $o += ['route_type' => 'link', 'route_link' => substr($l, 0, 500), 'route_name' => cc_av_str(wp_parse_url($l, PHP_URL_HOST) ?: 'link', 120)];
    }
    if (!empty($o['route_type'])) $o['route_at'] = (int) ($e['route_at'] ?? 0) ?: time();
    return $o;
}
function cc_g_event_text($e) {
    return $e['name'] . ' · ' . date_i18n('D j M Y', strtotime($e['date'] . ' 12:00')) . ' · ' . $e['prio'] . ' ' . strtolower(CC_G_TYPES[$e['type']])
         . (!empty($e['disc']) && isset(CC_G_DISC[$e['disc']]) ? ' · ' . strtolower(CC_G_DISC[$e['disc']]) : '')
         . ($e['dist'] !== '' ? ' · ' . $e['dist'] . ' km' : '') . ($e['elev'] !== '' ? ' · ' . $e['elev'] . ' m' : '') . ($e['note'] !== '' ? ' · ' . $e['note'] : '')
         . (!empty($e['start']) ? ' · start ' . $e['start'] : '') . (!empty($e['route_type']) ? ' · route: ' . ($e['route_type'] === 'link' ? ($e['route_link'] ?? '') : ($e['route_name'] ?? '') . ' (' . $e['route_type'] . ')') : '');
}
function cc_g_diff($old, $new) {
    $d = [];
    if (trim($old['short'] ?? '') !== $new['short']) $d[] = 'Short-term goal: ' . ($new['short'] ?: '(cleared)');
    if (trim($old['long'] ?? '') !== $new['long']) $d[] = 'Long-term goal: ' . ($new['long'] ?: '(cleared)');
    $o = array_map('cc_g_event_text', $old['events'] ?? []); $n = array_map('cc_g_event_text', $new['events']);
    foreach (array_diff($n, $o) as $x) $d[] = 'New or changed event: ' . $x;
    foreach (array_diff($o, $n) as $x) $d[] = 'Removed: ' . $x;
    return $d;
}
// the form's goals start the box (only when it is still empty)
function cc_g_from_form($pid, $a) {
    if (cc_g_get($pid)) return;
    $g = ['short' => $a['goal_short'] ?? '', 'long' => $a['goal_long'] ?? '', 'events' => cc_g_clean(['events' => $a['events'] ?? []])['events'],
          'from_form' => trim(($a['races'] ?? '') . (($a['race_a'] ?? '') !== '' ? "\nMain one: " . $a['race_a'] : '')), 'updated' => time()];   // races/race_a: old paper forms
    update_post_meta($pid, 'cc_goals', wp_slash(wp_json_encode($g)));
}

add_action('rest_api_init', function () {
    register_rest_route('cc/v1', '/goals/route', ['methods' => 'POST', 'callback' => 'cc_g_route_upload',
        'permission_callback' => function () { return is_user_logged_in() && (cc_ath_is_coach() || (bool) cc_ath_page_of(get_current_user_id())); }]);
    register_rest_route('cc/v1', '/route', ['methods' => 'GET', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {   // the laptop: the file itself, base64
        $id = (int) $r->get_param('id'); $f = get_attached_file($id, true);
        if (get_post_type($id) !== 'attachment' || !$f || !is_readable($f) || !cc_ath_is_private_file($id)) return new WP_Error('cc_none', 'No such route file', ['status' => 404]);
        return ['id' => $id, 'name' => get_the_title($id), 'type' => strtolower(pathinfo($f, PATHINFO_EXTENSION)), 'size' => filesize($f), 'base64' => base64_encode(file_get_contents($f))];
    }]);
    register_rest_route('cc/v1', '/goals', [
        ['methods' => 'POST', 'callback' => 'cc_g_save', 'permission_callback' => function () { return is_user_logged_in() && (cc_ath_is_coach() || (bool) cc_ath_page_of(get_current_user_id())); }],   // Matteo can edit an athlete's (?page=)
        ['methods' => 'GET', 'callback' => 'cc_g_list', 'permission_callback' => 'cc_ath_is_coach'],
    ]);
});
function cc_g_save(WP_REST_Request $r) {
    $coach = cc_ath_is_coach();
    if ($coach) { $pid = (int) $r->get_param('page'); if (get_post_type($pid) !== 'cc_athlete' || !get_post_meta($pid, 'cc_user', true)) return new WP_Error('cc_none', 'No such athlete', ['status' => 404]); $uid = (int) get_post_meta($pid, 'cc_user', true); }
    else { $uid = get_current_user_id(); $pid = cc_ath_page_of($uid); }
    $old = cc_g_get($pid) ?: []; $new = cc_g_clean($r->get_json_params()['goals'] ?? null, $pid);
    $rk = function ($e) { return ($e['route_id'] ?? 0) . '|' . ($e['route_link'] ?? ''); };
    foreach ($new['events'] as &$ne) { if (empty($ne['route_type'])) continue; $ne['route_at'] = time();
        foreach ($old['events'] ?? [] as $oe) if ($rk($oe) === $rk($ne) && !empty($oe['route_at'])) { $ne['route_at'] = (int) $oe['route_at']; break; } }
    unset($ne);
    $new['from_form'] = $old['from_form'] ?? '';
    $diff = cc_g_diff($old, $new); $auto = (bool) $r->get_param('auto');
    if (!$diff) {   // 20 Nov: the Save button after autosaves sends the email autosave kept back
        if (!$coach && !$auto && ($b = cc_mail_take($pid, 'gl')) && ($d2 = cc_g_diff($b['old'], $old))) cc_g_email($pid, $uid, $d2, $old);
        return ['ok' => true, 'unchanged' => true];
    }
    $new['updated'] = time();
    if ($coach) $new['by_coach'] = time();   // Matteo changed them (from a WhatsApp, a call…): no email to himself
    update_post_meta($pid, 'cc_goals', wp_slash(wp_json_encode($new)));
    if ($coach) return ['ok' => true, 'updated' => $new['updated']];
    if ($auto) { cc_mail_hold($pid, 'gl', $old, $uid); return ['ok' => true, 'updated' => $new['updated'], 'auto' => true]; }   // one email ~10 min after the last change
    if ($b = cc_mail_take($pid, 'gl')) { $d2 = cc_g_diff($b['old'], $new); if ($d2) $diff = $d2; }
    cc_g_email($pid, $uid, $diff, $new);
    return ['ok' => true, 'updated' => $new['updated']];
}
function cc_g_email($pid, $uid, $diff, $new) {
    $u = get_userdata($uid); $name = get_post_field('post_title', $pid);
    $h = '<div style="font:15px/1.5 Montserrat,Arial,sans-serif;color:#111;max-width:560px"><p style="margin:0 0 4px;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#E10600;font-weight:600">Goals &amp; events</p>'
       . '<h2 style="margin:0 0 14px;color:#111">' . esc_html($name) . ' updated their goals and events</h2><ul>' . implode('', array_map(function ($x) { return '<li>' . esc_html($x) . '</li>'; }, $diff)) . '</ul>'
       . (!empty($new['events']) ? '<p style="margin:16px 0 6px"><b style="color:#111">All their events</b></p><ul>' . implode('', array_map(function ($e) { return '<li>' . esc_html(cc_g_event_text($e)) . '</li>'; }, $new['events'])) . '</ul>' : '')
       . '<p style="margin:20px 0 0"><a href="' . esc_url(add_query_arg('board', 'goals', home_url('/' . CC_ATH_SLUG . '/'))) . '" style="display:inline-block;padding:12px 20px;border-radius:8px;background:#009a44;color:#fff;font-weight:600;text-decoration:none">Open all athletes’ goals</a></p></div>';
    $hd = ['Content-Type: text/html; charset=UTF-8']; if ($u && is_email($u->user_email)) $hd[] = 'Reply-To: ' . $name . ' <' . $u->user_email . '>';
    if (function_exists('cc_ath_coach_wrap')) $h = cc_ath_coach_wrap($h);
    if (cc_av_notify_to()) wp_mail(cc_av_notify_to(), 'Goals & events: ' . $name . ' – ' . $diff[0], $h, $hd);
}
function cc_g_route_upload(WP_REST_Request $r) {
    if (cc_ath_is_coach()) { $pid = (int) $r->get_param('page'); if (get_post_type($pid) !== 'cc_athlete') return new WP_Error('cc_none', 'No such athlete', ['status' => 404]); }
    else $pid = cc_ath_page_of(get_current_user_id());
    $f = ($r->get_file_params())['file'] ?? null;
    if (!$f || ($f['error'] ?? 1) !== UPLOAD_ERR_OK || !is_uploaded_file($f['tmp_name'])) return new WP_Error('cc_route', 'upload', ['status' => 400]);
    if ($f['size'] > 15 * 1024 * 1024) return new WP_Error('cc_route', 'size', ['status' => 413]);
    $ext = strtolower(pathinfo((string) $f['name'], PATHINFO_EXTENSION)); $head = (string) file_get_contents($f['tmp_name'], false, null, 0, 4096);
    $ok = ($ext === 'gpx' && stripos($head, '<gpx') !== false) || ($ext === 'tcx' && stripos($head, 'TrainingCenterDatabase') !== false) || ($ext === 'fit' && substr($head, 8, 4) === '.FIT');
    if (!isset(CC_G_ROUTE_EXT[$ext]) || !$ok) return new WP_Error('cc_route', 'type', ['status' => 415]);
    $name = cc_av_str(pathinfo((string) $f['name'], PATHINFO_FILENAME), 100) ?: 'route';
    $id = cc_f_store($pid, file_get_contents($f['tmp_name']), 'route', $ext, CC_G_ROUTE_EXT[$ext], $name . '.' . $ext);
    return $id ? ['ok' => true, 'route_id' => $id, 'route_name' => $name . '.' . $ext, 'route_type' => $ext] : new WP_Error('cc_route', 'save', ['status' => 500]);
}
function cc_g_list(WP_REST_Request $r) {
    $out = [];
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'meta_key' => 'cc_user']) as $p) {
        $u = get_userdata((int) get_post_meta($p->ID, 'cc_user', true)); if (!$u) continue;
        if ($r->get_param('email') && strcasecmp($u->user_email, $r->get_param('email'))) continue;
        $out[] = ['athlete' => $p->post_title, 'email' => $u->user_email, 'goals' => cc_g_get($p->ID)];
    }
    return $out;
}

/* ---------- the athlete's box ---------- */
add_filter('cc_ath_nav', function ($nav, $view, $coach) { if ($view && !cc_ath_tp($view)) { cc_f_set_lang((int) get_post_meta($view, 'cc_user', true)); array_splice($nav, 2, 0, [['goals', cc_f('My goals & events')]]); } return $nav; }, 20, 3);
/* Matteo 17 Nov: in the athlete's hub a short summary (next events, short-term goal) with "Add or change" opening its own page (?my=goals). Coach view: the full box (he can edit). */
add_filter('cc_ath_after_reports', function ($html, $view, $coach) {
    if (!$view || cc_ath_tp($view)) return $html;   // TrainingPeaks athletes add races and goals there
    if ($coach) return $html . cc_g_section($view, $coach);
    $lang = function_exists('cc_av_lang') ? cc_av_lang($view) : 'en';
    cc_f_set_lang((int) get_post_meta($view, 'cc_user', true));
    $g = cc_g_get($view) ?: ['short' => '', 'events' => []];
    $today = current_time('Y-m-d'); $ev = array_values(array_filter($g['events'] ?? [], function ($e) use ($today) { return $e['date'] >= $today; }));
    $o = '<section class="ath-s gl gl-sum" id="goals"><h2>' . cc_ath_icon('peaks', 'ath-hic') . esc_html(cc_f('My goals & events')) . '</h2><div class="av-sumbox"><div class="av-sumt">';
    if ($ev) {
        $show = array_slice($ev, 0, 2);   // the next two, but the next A race (the main goal) always shows (Matteo 18 Nov)
        $nextA = null; foreach ($ev as $e) if ($e['prio'] === 'A') { $nextA = $e; break; }
        if ($nextA && !in_array($nextA, $show, true)) $show = [$ev[0], $nextA];
        foreach ($show as $i => $e)
            $o .= '<p class="gl-sumev"><span class="gl-prio ' . esc_attr($e['prio']) . '">' . esc_html($e['prio']) . '</span><b>' . esc_html($e['name']) . '</b> <span class="gl-sumd">· ' . esc_html(cc_r_date_safe(strtotime($e['date'] . ' 12:00'))) . '</span></p>';
        if (count($ev) > 2) $o .= '<small>' . esc_html(sprintf(cc_ath_w('gl_more', $lang), count($ev) - 2)) . '</small>';
    } else $o .= '<p>' . esc_html(cc_ath_w('gl_none', $lang)) . '</p>';
    if (($g['short'] ?? '') !== '') $o .= '<small>' . esc_html(cc_f('Short-term goal (1 year)')) . ': ' . esc_html(wp_trim_words($g['short'], 18)) . '</small>';
    $o .= '<p class="gl-racehint">' . cc_ath_icon('bolt', 'gl-rhic') . '<span>' . esc_html(cc_ath_w('rc_hint', $lang)) . '</span></p>';   // Matteo 17 Nov: one place: the race day plan invite lives here, no separate card
    $o .= '</div><a class="btn btn-ghost" href="' . esc_url(add_query_arg('my', 'goals', home_url('/' . CC_ATH_SLUG . '/'))) . '">' . esc_html(cc_ath_w('gl_change', $lang)) . '</a></div></section>';
    return $html . $o;
}, 12, 3);   // Matteo 17 Nov: right after availability (10), before messages (15) and results (16)
add_filter('cc_ath_subpage', function ($html, $sub, $view) { return $sub === 'goals' && !cc_ath_tp($view) ? cc_g_section($view, false) : $html; }, 10, 3);
function cc_g_section($view, $coach) {
    $html = '';
    $g = cc_g_get($view) ?: ['short' => '', 'long' => '', 'events' => [], 'from_form' => ''];
    $today = current_time('Y-m-d'); $g['events'] = array_values(array_filter($g['events'], function ($e) use ($today) { return $e['date'] >= $today; }));
    $ed = $coach && get_post_meta($view, 'cc_user', true);   // Matteo 17 Nov: he can edit them from the coach view too
    $ro = false;
    cc_f_set_lang((int) get_post_meta($view, 'cc_user', true));
    $W = []; foreach (['My goals & events', 'Short-term goal (1 year)', 'Long-term goal (more than 1 year)', 'Events coming up', 'No events yet. Add your races, sportives and camps: I plan your training around them.',
        'Event', 'Date', 'Type', 'Priority', 'A = your main goal, B = important, C = for training or fun', 'Distance (km)', 'Climbing (m)', 'Note', 'Remove', '+ Add an event', 'Save my goals & events', 'Saving…',
        'Saved. Thanks, I will plan around it.', 'Nothing new to save.', 'That did not save. Please try again.', 'days to go', 'Today!', 'Tomorrow', 'From your form', 'optional',
        'Where you want to get to, and the events on the way. Keep them up to date: your plan is built around them.'] as $s) $W[$s] = cc_f($s);
    $lang = function_exists('cc_av_lang') ? cc_av_lang($view) : 'en';
    foreach (['rt_ask', 'rt_upload', 'rt_link', 'rt_start', 'rt_remove', 'rt_up', 'rt_bad', 'rt_ok'] as $k) $W[$k] = cc_ath_w($k, $lang);   // Matteo 17 Nov: the route question in each race
    foreach (['more', 'moresub', 'disc', 'choose', 'dist', 'elev', 'vk', 'rs', 'use', 'fill'] as $k) $W['g_' . $k] = cc_g_w($k, $lang);   // 20 Nov: the Vekta event fields
    $disc = []; foreach (CC_G_DISC as $k => $v) $disc[$k] = cc_g_w($k, $lang);
    $vk = !(function_exists('cc_ath_tp') && cc_ath_tp($view));   // TrainingPeaks athletes never see Vekta
    $types = []; foreach (CC_G_TYPES as $k => $v) $types[$k] = cc_f($v);
    $speech = CC_AV_SPEECH[$lang] ?? 'en-GB';
    $route_api = $ed ? add_query_arg('page', $view, rest_url('cc/v1/goals/route')) : rest_url('cc/v1/goals/route');
    return $html . '<section class="ath-s gl" id="goals" lang="' . esc_attr($speech) . '"><h2>' . cc_ath_icon('peaks', 'ath-hic') . esc_html($W['My goals & events']) . '</h2>'
        . '<p class="av-lede">' . esc_html($W['Where you want to get to, and the events on the way. Keep them up to date: your plan is built around them.']) . '</p>'
        . ($ed ? '<p class="rf-note"><b>Coach view.</b> You can change these for the athlete (for example a race they told you about on WhatsApp). They see your changes in their hub; you get no email for your own changes.</p>' : '')
        . '<div id="gl-app" data-ro="' . ($ro ? 1 : 0) . '" data-today="' . esc_attr($today) . '" data-api="' . esc_url($ed ? add_query_arg('page', $view, rest_url('cc/v1/goals')) : rest_url('cc/v1/goals')) . '" data-route="' . esc_url($route_api) . '" data-nonce="' . esc_attr(wp_create_nonce('wp_rest')) . '"></div>'
        . '<script type="application/json" id="gl-data">' . wp_json_encode(['g' => $g, 'w' => $W, 'types' => $types, 'disc' => $disc, 'vk' => $vk, 'L' => $speech]) . '</script></section>' . cc_g_js();
}

/* ---------- Matteo's board: /athletes/?board=goals ---------- */
add_filter('cc_ath_coach_links', function ($html) { return $html . '<a class="av-boardlink" href="' . esc_url(add_query_arg('board', 'goals', home_url('/' . CC_ATH_SLUG . '/'))) . '">Goals &amp; events</a>'; }, 15);
add_filter('cc_ath_board', function ($html, $board) {
    if ($board !== 'goals' || !cc_ath_is_coach()) return $html;
    add_action('shutdown', function () { update_user_meta(get_current_user_id(), 'cc_goals_seen', time()); });   // "seen by Matteo" for the laptop route (pc-api.php)
    $today = current_time('Y-m-d'); $rows = [];
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'orderby' => 'title', 'order' => 'ASC', 'meta_key' => 'cc_user']) as $p) {
        $g = cc_g_get($p->ID) ?: ['short' => '', 'long' => '', 'events' => []];
        $ev = array_values(array_filter($g['events'], function ($e) use ($today) { return $e['date'] >= $today; }));
        $a = array_values(array_filter($ev, function ($e) { return $e['prio'] === 'A'; }));
        $rows[] = [$a ? $a[0]['date'] : '9999', $p, $g, $ev, $a ? $a[0] : null];
    }
    usort($rows, function ($x, $y) { return strcmp($x[0], $y[0]); });   // next A race first
    $o = '<section class="ath-s"><h2>' . cc_ath_icon('peaks', 'ath-hic') . 'Goals &amp; events</h2><p class="av-lede">Every athlete’s goals and coming events, next A race first.</p><div class="gl-board">';
    foreach ($rows as [$k, $p, $g, $ev, $a]) {
        $o .= '<div class="gl-row"><div class="gl-who"><b>' . esc_html($p->post_title) . '</b>' . (!empty($g['updated']) ? '<small>Updated ' . esc_html(human_time_diff($g['updated']) . ' ago') . '</small>' : '<small>Not filled in yet</small>') . '</div>'
            . '<div class="gl-a">' . ($a ? '<span class="gl-prio A">A</span> ' . esc_html($a['name']) . ' · ' . esc_html(date_i18n('j M Y', strtotime($a['date']))) . ' · <b>' . (int) round((strtotime($a['date']) - strtotime($today)) / DAY_IN_SECONDS) . ' days</b>' : '<span class="gl-none">No A race</span>') . '</div>'
            . '<div class="gl-goals">' . ($g['short'] !== '' ? '<p><small>Short term</small> ' . esc_html($g['short']) . '</p>' : '') . ($g['long'] !== '' ? '<p><small>Long term</small> ' . esc_html($g['long']) . '</p>' : '')
            . ($ev ? '<ul>' . implode('', array_map(function ($e) { return '<li><span class="gl-prio ' . $e['prio'] . '">' . $e['prio'] . '</span> ' . esc_html(cc_g_event_text($e)) . '</li>'; }, $ev)) . '</ul>' : '')
            . (!empty($g['from_form']) ? '<p class="gl-ff"><small>From the form</small> ' . esc_html($g['from_form']) . '</p>' : '') . '</div></div>';
    }
    return $o . '</div></section>';
}, 10, 2);

function cc_g_js() {
    return <<<'JS'
<script>(function(){
var A=document.getElementById('gl-app');if(!A)return;var C=JSON.parse(document.getElementById('gl-data').textContent),W=C.w,G=C.g,ro=A.dataset.ro==='1',today=A.dataset.today,dirty=false;
var esc=function(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});};
function days(d){return Math.round((new Date(d+'T12:00')-new Date(today+'T12:00'))/864e5);}
function cd(d){var n=days(d);return n===0?W['Today!']:n===1?W['Tomorrow']:'<b>'+n+'</b> '+esc(W['days to go']);}
function draw(){var h='<div class="gl-goals2"><label for="gl-s">'+esc(W['Short-term goal (1 year)'])+'</label><textarea id="gl-s" rows="2"'+(ro?' readonly':'')+'>'+esc(G.short)+'</textarea>'
 +'<label for="gl-l">'+esc(W['Long-term goal (more than 1 year)'])+'</label><textarea id="gl-l" rows="2"'+(ro?' readonly':'')+'>'+esc(G.long)+'</textarea></div>'
 +(G.from_form?'<p class="gl-ff"><small>'+esc(W['From your form'])+'</small> '+esc(G.from_form)+'</p>':'')
 +'<h3 class="av-sub">'+esc(W['Events coming up'])+'</h3><div class="gl-evs">';
 if(!G.events.length)h+='<p class="av-none">'+esc(W['No events yet. Add your races, sportives and camps: I plan your training around them.'])+'</p>';
 G.events.forEach(function(e,i){var t='';for(var k in C.types)t+='<option value="'+k+'"'+(k===e.type?' selected':'')+'>'+esc(C.types[k])+'</option>';
  h+='<div class="gl-ev gl-'+e.prio+'" data-i="'+i+'"><div class="gl-top">'+(e.date?'<span class="gl-cd">'+cd(e.date)+'</span>':'')+'</div>'
   +'<div class="gl-r"><label>'+esc(W.Event)+'<input type="text" class="gl-n" maxlength="120" value="'+esc(e.name)+'"'+(ro?' readonly':'')+'></label><label>'+esc(W.Date)+'<input type="date" class="gl-d" value="'+esc(e.date)+'" min="'+today+'"'+(ro?' readonly':'')+'></label></div>'
   +'<div class="gl-r"><label>'+esc(W.Type)+'<select class="gl-t"'+(ro?' disabled':'')+'>'+t+'</select></label><fieldset><legend>'+esc(W.Priority)+'</legend><div class="gl-p">'
   +['A','B','C'].map(function(p){return '<button type="button" class="gl-pb" data-p="'+p+'" aria-pressed="'+(e.prio===p)+'"'+(ro?' disabled':'')+'>'+p+'</button>';}).join('')+'</div></fieldset></div>'
   +'<label>'+esc(W.Note)+' <small>('+esc(W.optional)+')</small><input type="text" class="gl-no" maxlength="300" value="'+esc(e.note)+'"'+(ro?' readonly':'')+'></label>'
   +'<details class="gl-more"'+(isOpen(e)?' open':'')+'><summary><span>'+esc(W.g_more)+'</span><small>'+esc(W.g_moresub)+'</small></summary>'
   +vkb(e)+((e.type==='race'||e.type==='sportive')?route(e):'')+'</details>'
   +(ro?'':'<button type="button" class="av-del gl-del">'+esc(W.Remove)+'</button>')+'</div>';});
 h+='</div><p class="gl-hint">'+esc(W['A = your main goal, B = important, C = for training or fun'])+'</p>';
 if(!ro)h+='<button type="button" class="btn btn-ghost gl-add">'+esc(W['+ Add an event'])+'</button><div class="av-save"><button type="button" class="btn btn-go gl-go">'+esc(W['Save my goals & events'])+'</button><span class="av-msg gl-msg" role="status"></span></div>';
 A.innerHTML=h;}
/* Matteo 17 Nov: the route question inside each race (file or link + start time) for the race day simulation */
function route(e){var f=e.route_type&&e.route_type!=='link';
 return '<div class="gl-route"><p class="gl-rq">'+esc(W.rt_ask)+'</p>'
  +(f?'<p class="gl-rf"><span>📍 '+esc(e.route_name||'')+'</span>'+(ro?'':' <button type="button" class="av-del gl-rx">'+esc(W.rt_remove)+'</button>')+'</p>'
     :(ro?'':'<label class="gl-up"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 16V4M6 10l6-6 6 6M4 20h16"/></svg>'+esc(W.rt_upload)+'<input type="file" class="gl-file" accept=".gpx,.fit,.tcx" hidden></label>')
      +'<label>'+esc(W.rt_link)+'<input type="url" class="gl-ln" inputmode="url" placeholder="https://" value="'+esc(e.route_link||'')+'"'+(ro?' readonly':'')+'></label>')
  +(f&&e.route_km?'<p class="gl-rs">'+esc(W.g_rs.replace('%s',rnum(e)))+'</p>'
     +(!ro&&(String(e.dist)!==String(e.route_km)||(e.route_m!=null&&String(e.elev)!==String(e.route_m)))?'<button type="button" class="gl-use">'+esc(W.g_use.replace('%s',rnum(e)))+'</button>':''):'')
  +'<span class="gl-rmsg" role="status"></span></div>';}
/* 20 Nov (Matteo: athletes add races only in the hub, so everything Vekta's event holds): discipline, start time, distance, climbing */
function vkb(e){var o='<option value="">'+esc(W.g_choose)+'</option>';for(var k in C.disc)o+='<option value="'+k+'"'+(k===e.disc?' selected':'')+'>'+esc(C.disc[k])+'</option>';
 return '<div class="gl-vkb">'+(C.vk?'<p class="gl-vkh"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>'+esc(W.g_vk)+'</p>':'')
  +'<div class="gl-r"><label>'+esc(W.g_disc)+opt+'<select class="gl-ds"'+(ro?' disabled':'')+'>'+o+'</select></label>'
  +'<label>'+esc(W.rt_start)+opt+'<input type="time" class="gl-st" value="'+esc(e.start||'')+'"'+(ro?' readonly':'')+'></label></div>'
  +'<div class="gl-r"><label>'+esc(W.g_dist)+opt+'<input type="number" inputmode="decimal" step="any" min="0" class="gl-km" value="'+esc(e.dist)+'"'+(ro?' readonly':'')+'></label>'
  +'<label>'+esc(W.g_elev)+opt+'<input type="number" inputmode="numeric" step="any" min="0" class="gl-m" value="'+esc(e.elev)+'"'+(ro?' readonly':'')+'></label></div></div>';}
/* Matteo 20 Nov: name, date and priority are all that is needed; the rest sits in one light fold, closed until something is in it */
var OP=[],opt=' <small>('+esc(W.optional)+')</small>';
function isOpen(e){return OP.indexOf(e)>-1||!!(e.disc||e.start||(e.dist!==''&&e.dist!=null)||(e.elev!==''&&e.elev!=null)||e.route_type);}
A.addEventListener('toggle',function(ev){var d=ev.target;if(!d.classList||!d.classList.contains('gl-more'))return;var x=G.events[+d.closest('.gl-ev').dataset.i],k=OP.indexOf(x);if(d.open&&k<0)OP.push(x);if(!d.open&&k>-1)OP.splice(k,1);},true);
function nf(n,d){try{return Number(n).toLocaleString(C.L||'en',{minimumFractionDigits:d,maximumFractionDigits:d});}catch(_){return String(n);}}
function rnum(e){return nf(e.route_km,1)+' km'+(e.route_m!=null?' · '+nf(e.route_m,0)+' m':'');}
/* read a .gpx/.tcx in the browser: distance (haversine sum) and climbing (light smoothing, 3 m threshold so GPS noise does not count) */
function rstats(txt){var d=new DOMParser().parseFromString(txt,'application/xml');if(d.getElementsByTagName('parsererror').length)return null;
 var P=[],q=function(n){return d.getElementsByTagNameNS('*',n);},tx=function(el,n){var c=el.getElementsByTagNameNS('*',n)[0];return c?parseFloat(c.textContent):NaN;};
 var L=q('trkpt');if(!L.length)L=q('rtept');
 if(L.length){for(var i=0;i<L.length;i++)P.push([parseFloat(L[i].getAttribute('lat')),parseFloat(L[i].getAttribute('lon')),tx(L[i],'ele')]);}
 else{L=q('Trackpoint');for(i=0;i<L.length;i++)P.push([tx(L[i],'LatitudeDegrees'),tx(L[i],'LongitudeDegrees'),tx(L[i],'AltitudeMeters')]);}
 P=P.filter(function(p){return isFinite(p[0])&&isFinite(p[1]);});if(P.length<2)return null;
 var km=0,r=Math.PI/180;for(i=1;i<P.length;i++){var a=P[i-1],b=P[i],dl=(b[0]-a[0])*r,dn=(b[1]-a[1])*r,h=Math.sin(dl/2)*Math.sin(dl/2)+Math.cos(a[0]*r)*Math.cos(b[0]*r)*Math.sin(dn/2)*Math.sin(dn/2);km+=12742.0176*Math.atan2(Math.sqrt(h),Math.sqrt(1-h));}
 var E=P.map(function(p){return p[2];}).filter(isFinite),m=null;
 if(E.length>1){var S=E.map(function(v,j){var lo=Math.max(0,j-2),hi=Math.min(E.length-1,j+2),s=0;for(var k=lo;k<=hi;k++)s+=E[k];return s/(hi-lo+1);}),ref=S[0];m=0;
  for(i=1;i<S.length;i++){if(S[i]-ref>=3){m+=S[i]-ref;ref=S[i];}else if(ref-S[i]>=3)ref=S[i];}m=Math.round(m);}
 return km>0?{km:Math.round(km*10)/10,m:m}:null;}
function upload(inp){var x=ev(inp),box=inp.closest('.gl-route'),m=box.querySelector('.gl-rmsg'),f=inp.files[0];if(!f)return;
 m.textContent=W.rt_up;m.classList.remove('bad');var fd=new FormData();fd.append('file',f);
 var sp=/\.(gpx|tcx)$/i.test(f.name)&&f.text?f.text().then(function(t){try{return rstats(t);}catch(_){return null;}},function(){return null;}):Promise.resolve(null);
 fetch(A.dataset.route,{method:'POST',credentials:'same-origin',headers:{'X-WP-Nonce':A.dataset.nonce},body:fd})
 .then(function(r){if(!r.ok)throw 0;return r.json();}).then(function(j){return sp.then(function(s){return [j,s];});}).then(function(js){var j=js[0],s=js[1],fill=false;
   x.route_id=j.route_id;x.route_name=j.route_name;x.route_type=j.route_type;delete x.route_link;delete x.route_at;delete x.route_km;delete x.route_m;
   if(s){x.route_km=s.km;if(s.m!=null)x.route_m=s.m;if(x.dist===''||x.dist==null){x.dist=s.km;fill=true;}if(s.m!=null&&(x.elev===''||x.elev==null)){x.elev=s.m;fill=true;}}
   var i=G.events.indexOf(x);draw();touch();if(fill){var bx=A.querySelector('.gl-ev[data-i="'+i+'"] .gl-rmsg');if(bx)bx.textContent='✓ '+W.g_fill;}
   var s=A.querySelector('.gl-go');if(x.name&&x.date&&s)s.click();})   /* saved straight away when the race already has a name and a date */
 .catch(function(){m.textContent=W.rt_bad;m.classList.add('bad');inp.value='';});}
/* 20 Nov (smoothness): changes save themselves a moment later ("Saving… / Saved ✓"); the button stays as a fallback */
var SV={en:'Saved',it:'Salvato',pt:'Guardado',sl:'Shranjeno',sk:'Uložené'}[String(C.L||'en').slice(0,2)]||'Saved',at_=null,busy=false,again=false,ver=0;
function touch(){dirty=true;ver++;var b=A.querySelector('.gl-go');if(b)b.disabled=false;if(!ro){var m0=A.querySelector('.gl-msg');if(m0){m0.textContent=W['Saving…'];m0.classList.remove('bad');}clearTimeout(at_);at_=setTimeout(function(){put(true);},1500);}}
document.addEventListener('visibilitychange',function(){if(document.visibilityState==='hidden'&&dirty&&!ro){clearTimeout(at_);put(true);}});
function put(auto){if(busy){again=true;return;}busy=true;var v0=ver,b=A.querySelector('.gl-go'),m=A.querySelector('.gl-msg');if(b&&!auto)b.disabled=true;if(m){m.textContent=W['Saving…'];m.classList.remove('bad');}
 fetch(A.dataset.api,{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-WP-Nonce':A.dataset.nonce},body:JSON.stringify({goals:G,auto:auto?1:0})})
 .then(function(r){if(!r.ok)throw 0;return r.json();}).then(function(j){busy=false;if(ver===v0)dirty=false;m=A.querySelector('.gl-msg');if(m)m.textContent=auto?'✓ '+SV:W['Saved. Thanks, I will plan around it.'];if(again){again=false;if(dirty)put(true);}})
 .catch(function(){busy=false;again=false;var b2=A.querySelector('.gl-go');if(b2)b2.disabled=false;m=A.querySelector('.gl-msg');if(m){m.textContent=W['That did not save. Please try again.'];m.classList.add('bad');}});}
function ev(t){return G.events[+t.closest('.gl-ev').dataset.i];}
A.addEventListener('input',function(e){var t=e.target;if(t.id==='gl-s')G.short=t.value;else if(t.id==='gl-l')G.long=t.value;else if(t.closest('.gl-ev')){var x=ev(t);
 if(t.classList.contains('gl-ln')){x.route_link=t.value.trim();if(x.route_link){x.route_type='link';}else{delete x.route_type;}delete x.route_at;}
 if(t.classList.contains('gl-n'))x.name=t.value;if(t.classList.contains('gl-km'))x.dist=t.value;if(t.classList.contains('gl-m'))x.elev=t.value;if(t.classList.contains('gl-no'))x.note=t.value;}touch();});
A.addEventListener('change',function(e){var t=e.target;if(!t.closest('.gl-ev'))return;var x=ev(t);if(t.classList.contains('gl-d')){x.date=t.value;var c=t.closest('.gl-ev').querySelector('.gl-top');c.innerHTML=x.date?'<span class="gl-cd">'+cd(x.date)+'</span>':'';}
 if(t.classList.contains('gl-st'))x.start=t.value;if(t.classList.contains('gl-ds'))x.disc=t.value;if(t.classList.contains('gl-file')){upload(t);return;}
 if(t.classList.contains('gl-t')){x.type=t.value;draw();}touch();});
A.addEventListener('click',function(e){var b=e.target.closest('button');if(!b||ro)return;
 if(b.classList.contains('gl-pb')){var x=ev(b);x.prio=b.dataset.p;var r=b.closest('.gl-ev');r.className='gl-ev gl-'+x.prio;r.querySelectorAll('.gl-pb').forEach(function(y){y.setAttribute('aria-pressed',y===b);});touch();}
 if(b.classList.contains('gl-add')){G.events.push({name:'',date:'',type:'race',prio:'B',disc:'',dist:'',elev:'',note:''});draw();touch();var l=A.querySelectorAll('.gl-n');l[l.length-1].focus();}
 if(b.classList.contains('gl-rx')){var y=ev(b);delete y.route_id;delete y.route_name;delete y.route_type;delete y.route_at;delete y.route_km;delete y.route_m;draw();touch();}
 if(b.classList.contains('gl-use')){var u=ev(b);u.dist=u.route_km;if(u.route_m!=null)u.elev=u.route_m;draw();touch();}
 if(b.classList.contains('gl-del')){G.events.splice(+b.closest('.gl-ev').dataset.i,1);draw();touch();}
 if(b.classList.contains('gl-go')){clearTimeout(at_);put(false);}});
addEventListener('beforeunload',function(e){if(dirty&&!ro){e.preventDefault();e.returnValue='';}});
draw();})();</script>
JS;
}
add_action('wp_head', function () {
    if (!is_page(CC_ATH_SLUG)) return;
    echo <<<'CSS'
<style id="cc-goals">
html .cc .gl .av-sub { margin-top: 24px; } html .cc .gl-goals2 { display: grid; gap: 6px; } html .cc .gl-goals2 label, html .cc .gl-ev label, html .cc .gl-ev legend { display: grid; gap: 5px; margin: 8px 0 0; font-size: 15px; color: var(--text-3); font-weight: 600; padding: 0; }
html .cc .gl-goals2 label { color: var(--text); font-size: 15px; } html .cc .gl-ev fieldset { border: 0; margin: 0; padding: 0; min-width: 0; }
html .cc .ath :is(.gl-goals2 textarea, .gl-ev input, .gl-ev select) { width: 100%; box-sizing: border-box; font: 16px var(--body); padding: 10px 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,.18); background: #0b0d0f; color: #fff; color-scheme: dark; min-width: 0; }
html .cc .gl-ff { margin: 12px 0 0; font-size: 14px; color: var(--text-2); } html .cc .gl-ff small { display: block; color: var(--text-3); font-size: 14px; text-transform: uppercase; letter-spacing: .08em; }
html .cc .gl-evs { display: grid; gap: 10px; margin: 0 0 10px; }
html .cc .gl-ev { display: grid; gap: 4px; padding: 14px; border-radius: 12px; border: 1px solid rgba(255,255,255,.1); border-left: 3px solid #8a8f98; background: rgba(255,255,255,.03); }
html .cc .gl-ev.gl-A { border-left-color: #009a44; background: linear-gradient(90deg, rgba(0,154,68,.12), rgba(255,255,255,.03) 50%); } html .cc .gl-ev.gl-B { border-left-color: #d0d6e0; }
html .cc .gl-top:empty { display: none; } html .cc .gl-cd { font-size: 14px; color: var(--text-2); } html .cc .gl-cd b { font: 400 26px/1 var(--head); color: #34c46a; margin-right: 4px; }
html .cc .gl-r { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 10px; }
@media (max-width: 480px) { html .cc .gl-r { grid-template-columns: minmax(0, 1fr); gap: 4px; } }   /* 19 Nov: event name and type were cut off on phones: one column */
html .cc .gl-p { display: flex; gap: 6px; } html .cc .gl-pb { flex: 1; font: 700 15px var(--body); min-height: 44px; border-radius: 10px; border: 1px solid rgba(255,255,255,.16); background: transparent; color: var(--text-2); cursor: pointer; }
html .cc .gl-pb[aria-pressed=true] { background: #009a44; border-color: #009a44; color: #fff; } html .cc .gl-hint { font-size: 15px; color: var(--text-3); margin: 0 0 12px; }
html .cc .gl-del { justify-self: start; }
html .cc .gl-board { display: grid; gap: 8px; } html .cc .gl-row { display: grid; grid-template-columns: 170px minmax(0, 1fr); gap: 6px 16px; padding: 12px 14px; border-radius: 12px; background: rgba(255,255,255,.03); border: 1px solid rgba(255,255,255,.08); font-size: 14px; }
html .cc .gl-who { display: grid; gap: 2px; align-content: start; } html .cc .gl-who b { color: #fff; } html .cc .gl-who small { color: var(--text-3); font-size: 14px; }
html .cc .gl-a { color: #fff; } html .cc .gl-a b { color: #34c46a; } html .cc .gl-none { color: var(--text-3); }
html .cc .gl-goals { grid-column: 2; color: var(--text-2); } html .cc .gl-goals p { margin: 4px 0; } html .cc .gl-goals small { color: var(--text-3); margin-right: 6px; } html .cc .gl-goals ul { margin: 6px 0 0; padding: 0; list-style: none; display: grid; gap: 3px; }
html .cc .gl-prio { display: inline-grid; place-items: center; width: 20px; height: 20px; border-radius: 6px; background: rgba(255,255,255,.12); font: 700 11px var(--body); color: #fff; } html .cc .gl-prio.A { background: #009a44; }
/* Race priority colours (Matteo 17 Nov, everywhere in Cigala + Vekta): A gold, B silver, C bronze */
html .cc .gl-ev.gl-A { border-left-color: #D4AF37 !important; background: linear-gradient(90deg, rgba(212,175,55,.14), rgba(255,255,255,.03) 50%) !important; }
html .cc .gl-ev.gl-B { border-left-color: #C0C4CC !important; background: linear-gradient(90deg, rgba(192,196,204,.10), rgba(255,255,255,.03) 50%) !important; }
html .cc .gl-ev.gl-C { border-left-color: #CD7F32 !important; background: linear-gradient(90deg, rgba(205,127,50,.12), rgba(255,255,255,.03) 50%) !important; }
html .cc .gl-pb[data-p=A][aria-pressed=true] { background: linear-gradient(135deg, #F3D774, #D4AF37 55%, #A8841F); border-color: #D4AF37; color: #1a1406; }
html .cc .gl-pb[data-p=B][aria-pressed=true] { background: linear-gradient(135deg, #F2F3F5, #C0C4CC 55%, #8E939C); border-color: #C0C4CC; color: #15171a; }
html .cc .gl-pb[data-p=C][aria-pressed=true] { background: linear-gradient(135deg, #E9A86B, #CD7F32 55%, #9A5A1F); border-color: #CD7F32; color: #1c1006; }
html .cc .gl-prio.A { background: linear-gradient(135deg, #F3D774, #D4AF37 55%, #A8841F) !important; color: #1a1406 !important; }
html .cc .gl-prio.B { background: linear-gradient(135deg, #F2F3F5, #C0C4CC 55%, #8E939C) !important; color: #15171a !important; }
html .cc .gl-prio.C { background: linear-gradient(135deg, #E9A86B, #CD7F32 55%, #9A5A1F) !important; color: #1c1006 !important; }
/* Matteo 17 Nov: the route question inside each race */
html .cc .gl-route { margin: 14px 0 6px; padding: 18px; border-radius: 12px; border: 1px dashed rgba(52,196,106,.45); background: rgba(1,138,68,.07); display: grid; gap: 8px; }
html .cc .gl-rq { margin: 0; color: #fff; font-weight: 700; font-size: 16px; line-height: 1.45; }
html .cc .gl-ev label.gl-up, html .cc .gl-up { justify-self: start; display: inline-flex; align-items: center; gap: 10px; cursor: pointer; margin: 4px 0; max-width: 100%; white-space: normal; padding: 13px 20px; border-radius: 999px; background: #018a44; color: #fff; font: 600 15px var(--body); line-height: 1.3; box-shadow: 0 4px 14px rgba(1,138,68,.35); transition: background .2s, transform .2s; }
html .cc .gl-ev label.gl-up:hover, html .cc .gl-up:hover { background: #12a150; transform: translateY(-1px); } html .cc .gl-up svg { width: 20px; height: 20px; flex: none; fill: none; stroke: #fff; stroke-width: 2.2; stroke-linecap: round; stroke-linejoin: round; }   /* Matteo 17 Nov: the upload was hard to see */
html .cc .gl-rf { margin: 0; display: flex; flex-wrap: wrap; align-items: center; gap: 10px; color: #34c46a; font-weight: 600; font-size: 15px; } html .cc .gl-rf span { overflow-wrap: anywhere; }
html .cc .gl-rmsg { font-size: 14px; color: var(--text-2); } html .cc .gl-rmsg.bad { color: #ff4a3d; } html .cc .gl-rmsg:empty { display: none; }
/* 20 Nov: the Vekta event fields (discipline, start, distance, climbing), plainly visible; numbers read from the route file */
html .cc .gl-more { margin: 10px 0 2px; border-radius: 12px; border: 1px solid rgba(255,255,255,.1); background: rgba(255,255,255,.02); }
html .cc .gl-more > summary { list-style: none; cursor: pointer; min-height: 44px; box-sizing: border-box; padding: 10px 40px 10px 14px; position: relative; display: grid; gap: 2px; align-content: center; }
html .cc .gl-more > summary::-webkit-details-marker { display: none; }
html .cc .gl-more > summary span { font: 600 15px/1.35 var(--body); color: #e8ebef; } html .cc .gl-more > summary small { font-size: 14px; line-height: 1.35; color: #b8bec8; }
html .cc .gl-more > summary::after { content: ''; position: absolute; right: 16px; top: 50%; width: 9px; height: 9px; margin-top: -7px; border: solid #34c46a; border-width: 0 2px 2px 0; transform: rotate(45deg); transition: transform .2s; }
html .cc .gl-more[open] > summary::after { transform: rotate(-135deg); margin-top: -2px; }
html .cc .gl-more > :not(summary) { margin-left: 12px; margin-right: 12px; } html .cc .gl-more > :last-child { margin-bottom: 12px; }
html .cc .gl-more .gl-vkb { margin-top: 0; }
html .cc .gl-vkb small { font-weight: 400; color: #b8bec8; font-size: 14px; }
html .cc .gl-vkb { margin: 10px 0 2px; padding: 12px 14px 14px; border-radius: 12px; background: rgba(255,255,255,.035); border: 1px solid rgba(255,255,255,.1); display: grid; gap: 2px; }
html .cc .gl-vkh { margin: 0 0 2px; display: flex; align-items: center; gap: 8px; font-size: 15px; color: #c9ced6; line-height: 1.4; }
html .cc .gl-vkh svg { width: 18px; height: 18px; flex: none; fill: none; stroke: #34c46a; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
html .cc .gl-vkb label { color: #e8ebef !important; } html .cc .ath :is(.gl-ev input:not([type=file]), .gl-ev select) { min-height: 44px; }
html .cc .gl-rs { margin: 0; font-size: 15px; color: #e8ebef; font-weight: 600; }
html .cc .gl-use { justify-self: start; max-width: 100%; min-height: 44px; padding: 10px 16px; border-radius: 999px; border: 1px solid #34c46a; background: rgba(1,138,68,.14); color: #fff; font: 600 15px/1.3 var(--body); text-align: left; cursor: pointer; white-space: normal; }
html .cc .gl-use:hover { background: rgba(1,138,68,.28); }
@media (max-width: 760px) { html .cc .av-sumbox .gl-racehint { margin-top: 24px; } }   /* Matteo 17 Nov: a little lower on phones */
html .cc .gl-racehint { display: flex; gap: 10px; align-items: flex-start; margin: 28px 0 0; padding: 12px 14px; border-radius: 10px; background: rgba(1,138,68,.10); border: 1px solid rgba(52,196,106,.35); color: #e8ebef; font-size: 15px; line-height: 1.45; }
html .cc .gl-racehint .gl-rhic svg { width: 20px; height: 20px; fill: none; stroke: #34c46a; stroke-width: 2; margin-top: 2px; } html .cc .gl-racehint .gl-rhic { flex: none; display: inline-flex; }
@media (max-width: 640px) { html .cc .gl-row { grid-template-columns: 1fr; } html .cc .gl-goals { grid-column: 1; } }
</style>
CSS;
});
