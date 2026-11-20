<?php
if (!defined('ABSPATH')) return;
/* ---------- Nutrition plus (Matteo and Marine, 19 Nov 2026; vekta\athlete-hub\nutrition-backlog.md items 1-7) ----------
 * Works with food.php (diary) and mealplan.php (Marine's planning). Adds:
 *  - drink foods: the food table's family (column 12) says which foods are drinks; their grams count as ml of "Other drinks"
 *    (the Water family counts as water); see cc_np_drink(), used by food.php's cc_fd_fluids()
 *  - Marine's day targets (athlete-visible as positive progress): her explicit "Day targets" (post meta cc_np_tg {date: {k,c,p,f}}) win,
 *    then the meal-plan day total, then numbers in her nutrition-plan text (hub) or her Vekta nutrition note ("2000 kcal", "carbs 300 g")
 *  - Marine/coach only: carbs per hour and energy charts vs duration and intensity (12 weeks of sessions from Matteo's laptop sync),
 *    omega-3 per day (plant ALA vs marine/animal EPA+DPA+DHA) with a 7-day chart, and the food-family analysis
 *  - the "Food families" page (option cc_np_fam: {f: {family index: {s, c, fi}}, o: {food id: {n, s, c, fi}}}), empty until Marine fills it
 * English only on these staff screens. TrainingPeaks athletes: no Vekta data, nothing here names Vekta to them. */

const CC_NP_DIMS = [
    's' => ['Sugars', ['natural' => 'Natural sugars', 'free' => 'Free sugars']],
    'c' => ['Carbs', ['slow' => 'Slow carbs', 'fast' => 'Fast carbs']],
    'fi' => ['Fibre', ['soluble' => 'Soluble fibre', 'insoluble' => 'Insoluble fibre', 'mixed' => 'Mixed fibre']],
];

/* the food table's families: {v, families: [[name, drink]], fam: {id: index}}, kept in an option for the table version */
function cc_np_db() {
    static $D = null; if ($D !== null) return $D;
    $v = (string) get_option('cc_food_db_v', '');
    $c = json_decode((string) get_option('cc_np_famidx', ''), true);
    if (!is_array($c) || (string) ($c['v'] ?? '') !== $v) {
        $j = json_decode((string) get_option('cc_food_db', ''), true); $f = [];
        foreach ((array) ($j['foods'] ?? []) as $r) if (is_array($r) && isset($r[0], $r[12]) && is_int($r[12])) $f[(string) $r[0]] = $r[12];
        $c = ['v' => $v, 'families' => array_values((array) ($j['families'] ?? [])), 'fam' => (object) $f]; unset($j);
        update_option('cc_np_famidx', wp_json_encode($c), false);
        $c = json_decode(wp_json_encode($c), true);
    }
    $c['fam'] = (array) ($c['fam'] ?? []);
    return $D = $c;
}
function cc_np_famof($id) { $D = cc_np_db(); $i = $D['fam'][(string) $id] ?? null; return $i === null ? null : (int) $i; }
/* 'w' = water, 'd' = another drink, '' = food (own foods and recipes are food) */
function cc_np_drink($it) {
    if (!is_array($it) || !empty($it['m'])) return '';
    $i = cc_np_famof($it['id'] ?? ''); if ($i === null) return !empty($it['dr']) ? 'd' : '';
    $f = cc_np_db()['families'][$i] ?? null; if (!$f || empty($f[1])) return '';
    return $f[0] === 'Water' ? 'w' : 'd';
}

/* ---------- day targets ---------- */
function cc_np_tg_get($pid) { $a = json_decode((string) get_post_meta((int) $pid, 'cc_np_tg', true), true); return is_array($a) ? $a : []; }
/* kcal / carbs / protein / fat in a text: "2000 kcal", "2,000 calories", "carbs 300 g", "300 g carbs", "protein: 140g", "fat 70 g".
   Per-hour and per-kg numbers ("90 g carbs/h", "6 g/kg carbs") are left out. */
function cc_np_parse($txt) {
    $t = ' ' . strtolower(preg_replace('/(\d)[,.](\d{3})\b/', '$1$2', (string) $txt)) . ' '; $o = [];
    $not = '(?!\s*(?:\/\s*(?:h|hr|hour|kg)\b|per\s+(?:hour|kg)|an\s+hour|each\s+hour|every\s+hour|\/kg))';
    if (preg_match('/\b(\d{3,5})\s*(?:kcal|calories|cals?)\b/', $t, $m) || preg_match('/\b(?:kcal|calories|energy)\s*[:=]?\s*(\d{3,5})\b/', $t, $m)) $o['k'] = (int) $m[1];
    foreach (['c' => 'carbs?|carbohydrates?|cho', 'p' => 'proteins?', 'f' => 'fats?'] as $k => $w) {
        if (preg_match('/\b(?:' . $w . ')\s*[:=]?\s*(\d{1,4})\s*g(?:rams?)?\b' . $not . '/', $t, $m) || preg_match('/\b(\d{1,4})\s*g(?:rams?)?\s*(?:of\s+)?(?:' . $w . ')\b' . $not . '/', $t, $m)) {
            if ((int) $m[1] > 0) $o[$k] = (int) $m[1];
        }
    }
    return $o;
}
/* Marine's Vekta note, parsed on Matteo's laptop (vekta_inbox.py parse_note): {day: {k, c, p, f, fi}, slots: {slot: {c, p, f, w}}, bike: {ch, mlh}} */
function cc_np_clean_ntg($tg) {
    if (!is_array($tg)) return null; $o = [];
    $n = function ($v, $mx) { $v = (int) round((float) $v); return ($v > 0 && $v <= $mx) ? $v : 0; };
    foreach (['k' => 10000, 'c' => 2000, 'p' => 1000, 'f' => 1000, 'fi' => 200] as $k => $mx) if ($x = $n($tg['day'][$k] ?? 0, $mx)) $o['day'][$k] = $x;
    foreach ((array) ($tg['slots'] ?? []) as $s => $v) {
        $s = (string) $s; if (!in_array($s, array_merge(CC_FD_SLOTS, ['gym']), true) || !is_array($v)) continue;
        foreach (['c' => 1000, 'p' => 500, 'f' => 500, 'w' => 5000] as $k => $mx) if ($x = $n($v[$k] ?? 0, $mx)) $o['slots'][$s][$k] = $x;
    }
    foreach (['ch' => 200, 'mlh' => 3000] as $k => $mx) if ($x = $n($tg['bike'][$k] ?? 0, $mx)) $o['bike'][$k] = $x;
    return $o ?: null;
}
/* targets for a list of dates: {date: {k, c, p, f, src: {k: 'set'|'plan'|'text'|'note'}, sl: {slot: {c, p, f, w}}, bk: {ch, mlh}}} (only dates with a target).
   Day values: Marine's Day targets (hub) win, then the meal-plan total, then her plan text, then her Vekta note. Per-meal and on-the-bike targets: her Vekta note. */
function cc_np_targets($pid, $dates) {
    $set = cc_np_tg_get($pid); $tp = function_exists('cc_ath_tp') && cc_ath_tp($pid); $vx = $tp ? [] : cc_fd_vx($pid); $notes = []; $ntg = [];
    foreach ((array) ($vx['notes'] ?? []) as $n) if (!empty($n['d'])) {
        $notes[$n['d']] = ($notes[$n['d']] ?? '') . ' ' . ($n['t'] ?? '') . ' ' . ($n['c'] ?? '');
        if (!empty($n['tg']) && is_array($n['tg'])) $ntg[$n['d']] = $n['tg'];
    }
    $out = [];
    foreach ($dates as $d) {
        $o = []; $src = [];
        $put = function ($vals, $s) use (&$o, &$src) { foreach (['k', 'c', 'p', 'f'] as $k) if (!empty($vals[$k]) && $vals[$k] > 0) { $o[$k] = (int) round($vals[$k]); $src[$k] = $s; } };
        if (!empty($ntg[$d]['day'])) $put($ntg[$d]['day'], 'note'); elseif (isset($notes[$d])) $put(cc_np_parse($notes[$d]), 'note');
        if (function_exists('cc_mp_get')) {
            $pl = cc_mp_get($pid, $d);
            if ($pl['n'] !== '') $put(cc_np_parse($pl['n']), 'text');
            if ($pl['i'] && function_exists('cc_mp_item_mac')) { $t = ['k' => 0, 'c' => 0, 'p' => 0, 'f' => 0]; foreach ($pl['i'] as $it) { $m = cc_mp_item_mac($pid, $it); foreach ($t as $k => $_) $t[$k] += (float) ($m[$k] ?? 0); } $put($t, 'plan'); }
        }
        if (!empty($set[$d])) $put($set[$d], 'set');
        if ($o) $o['src'] = $src;
        if (!empty($ntg[$d]['day']['fi'])) $o['fi'] = (int) $ntg[$d]['day']['fi'];
        if (!empty($ntg[$d]['slots'])) $o['sl'] = $ntg[$d]['slots'];
        if (!empty($ntg[$d]['bike'])) $o['bk'] = $ntg[$d]['bike'];
        if ($o) $out[$d] = $o;
    }
    return $out;
}
function cc_np_dates($from, $n) { $o = []; $t = strtotime($from . ' 12:00'); for ($i = 0; $i < $n; $i++) $o[] = gmdate('Y-m-d', $t + $i * DAY_IN_SECONDS); return $o; }
add_filter('cc_fd_athlete_cfg', function ($cfg, $pid, $date) {
    $tg = cc_np_targets($pid, cc_np_dates(gmdate('Y-m-d', strtotime(current_time('Y-m-d') . ' 12:00') - 45 * DAY_IN_SECONDS), 54));
    $gh = (array) ($cfg['targets'] ?? []);
    foreach ($tg as $d => $t) {
        unset($tg[$d]['src']);
        if (!empty($t['bk']['ch']) && empty($gh[$d]['c'])) $gh[$d]['c'] = $t['bk']['ch'];   /* on-the-bike gauges */
        if (!empty($t['bk']['mlh']) && empty($gh[$d]['ml'])) $gh[$d]['ml'] = $t['bk']['mlh'];
    }
    $cfg['tg'] = (object) $tg; $cfg['targets'] = (object) $gh;
    return $cfg;
}, 10, 3);

/* ---------- omega-3 (micronutrient table columns ala and n3m, g per 100 g) ---------- */
function cc_np_m100($id, $rec, $col, $depth = 0) {
    $M = cc_fd_micro_db(); $j = array_search($col, $M['cols'], true); if ($j === false) return null;
    if (isset($M['m'][$id])) { $v = $M['m'][$id][$j] ?? null; return $v === null ? null : (float) $v; }
    $r = $rec[$id] ?? null; if (!$r || $depth > 2) return null;
    $w = (float) ($r['cw'] ?? 0); $sum = 0; $x = 0;
    foreach ((array) ($r['ing'] ?? []) as $i) { $g = (float) ($i[1] ?? 0); $sum += $g; if ($g <= 0) continue; $v = cc_np_m100($i[0] ?? '', $rec, $col, $depth + 1); if ($v === null) return null; $x += $v * $g / 100; }
    if ($w <= 0) $w = $sum; return $w > 0 ? $x * 100 / $w : null;
}
/* a day's omega-3: ala, n3m (g), the foods giving most, and the foods left out (no data) */
function cc_np_o3($day, $mine) {
    $rec = (array) cc_fd_recipes($mine); $o = ['ala' => 0, 'n3m' => 0, 'top' => [], 'miss' => [], 'g' => 0, 'mg' => 0];
    foreach ((array) ($day['s'] ?? []) as $s) foreach ((array) ($s['i'] ?? []) as $it) {
        $g = (float) ($it['g'] ?? 0); if ($g <= 0) continue; $o['g'] += $g;
        $a = cc_np_m100($it['id'] ?? '', $rec, 'ala'); $m = cc_np_m100($it['id'] ?? '', $rec, 'n3m');
        if ($a === null && $m === null) { $o['miss'][$it['n']] = 1; $o['mg'] += $g; continue; }
        $va = $a === null ? 0 : $a * $g / 100; $vm = $m === null ? 0 : $m * $g / 100;
        $o['ala'] += $va; $o['n3m'] += $vm; $o['top'][$it['n']] = ($o['top'][$it['n']] ?? 0) + $va + $vm;
        if ($a === null || $m === null) $o['part'][$it['n']] = 1;
    }
    arsort($o['top']); $o['top'] = array_slice(array_filter($o['top'], function ($x) { return $x >= 0.01; }), 0, 3, true);
    return $o;
}
function cc_np_g($x) { $x = (float) $x; return $x >= 10 ? number_format($x, 1) : ($x >= 0.01 ? number_format($x, 2) : ($x > 0 ? number_format($x, 3) : '0')); }
function cc_np_o3_html($o) {
    if ($o['g'] <= 0) return '';
    $tot = $o['ala'] + $o['n3m'];
    $h = '<div class="np-o3"><p><b>Omega-3 ' . cc_np_g($tot) . ' g</b> · plant (ALA) ' . cc_np_g($o['ala']) . ' g · marine/animal (EPA+DPA+DHA) ' . cc_np_g($o['n3m']) . ' g</p>';
    if ($o['top']) { $t = []; foreach ($o['top'] as $n => $v) $t[] = esc_html($n) . ' ' . cc_np_g($v) . ' g'; $h .= '<p class="np-sub">Most from: ' . implode(' · ', $t) . '</p>'; }
    if ($o['miss']) $h .= '<p class="np-sub">Left out (no omega-3 data, ' . round($o['mg'] / $o['g'] * 100) . ' % of the grams): ' . esc_html(implode(', ', array_slice(array_keys($o['miss']), 0, 6))) . (count($o['miss']) > 6 ? '…' : '') . '</p>';
    if (!empty($o['part'])) $h .= '<p class="np-sub">Partly known (ALA or EPA+DPA+DHA missing): ' . esc_html(implode(', ', array_slice(array_keys($o['part']), 0, 4))) . (count($o['part']) > 4 ? '…' : '') . '</p>';
    return $h . '</div>';
}
/* 7 days of omega-3 as stacked bars (plant / marine-animal), drawn on the server */
function cc_np_o3_week($pid, $end, $bare = false) {
    $mine = cc_fd_mine($pid); $t0 = strtotime($end . ' 12:00'); $rows = []; $mx = 0; $any = false;
    for ($i = 6; $i >= 0; $i--) { $d = gmdate('Y-m-d', $t0 - $i * DAY_IN_SECONDS); $o = cc_np_o3(cc_fd_get($pid, $d), $mine); $rows[] = [$d, $o]; $mx = max($mx, $o['ala'] + $o['n3m']); if ($o['g'] > 0) $any = true; }
    if (!$any) return $bare ? '<p class="fd-muted">Nothing logged in these 7 days.</p>' : '<div class="fd-box np-o3w"><h3>Omega-3 · last 7 days</h3><p class="fd-muted">Nothing logged in the last 7 days.</p></div>';
    $W = 560; $H = 230; $pb = 44; $pt = 30; $bw = 46; $gap = ($W - 7 * $bw) / 8; $mx = $mx > 0 ? $mx * 1.15 : 1;
    $s = '<svg viewBox="0 0 ' . $W . ' ' . $H . '" role="img" aria-label="Omega-3 per day, last 7 days">';
    $s .= '<line x1="0" y1="' . ($H - $pb) . '" x2="' . $W . '" y2="' . ($H - $pb) . '" stroke="rgba(255,255,255,.18)"/>';
    foreach ($rows as $k => $r) {
        [$d, $o] = $r; $x = $gap + $k * ($bw + $gap); $base = $H - $pb; $ha = ($o['ala'] / $mx) * ($H - $pb - $pt); $hm = ($o['n3m'] / $mx) * ($H - $pb - $pt);
        if ($o['g'] > 0) {
            $s .= '<rect x="' . round($x, 1) . '" y="' . round($base - $ha, 1) . '" width="' . $bw . '" height="' . round($ha, 1) . '" fill="#5cc8c2" rx="3"><title>' . esc_attr(date_i18n('D j M', strtotime($d . ' 12:00')) . ': plant (ALA) ' . cc_np_g($o['ala']) . ' g') . '</title></rect>';
            $s .= '<rect x="' . round($x, 1) . '" y="' . round($base - $ha - $hm, 1) . '" width="' . $bw . '" height="' . round($hm, 1) . '" fill="#7fb2ff" rx="3"><title>' . esc_attr(date_i18n('D j M', strtotime($d . ' 12:00')) . ': marine/animal ' . cc_np_g($o['n3m']) . ' g') . '</title></rect>';
            $s .= '<text x="' . round($x + $bw / 2, 1) . '" y="' . round($base - $ha - $hm - 8, 1) . '" text-anchor="middle" font-size="15" fill="#e6e9ee">' . cc_np_g($o['ala'] + $o['n3m']) . '</text>';
        } else $s .= '<text x="' . round($x + $bw / 2, 1) . '" y="' . ($base - 8) . '" text-anchor="middle" font-size="14" fill="#b8bec8">–</text>';
        $s .= '<text x="' . round($x + $bw / 2, 1) . '" y="' . ($H - 24) . '" text-anchor="middle" font-size="15" fill="#d0d6e0">' . esc_html(date_i18n('D', strtotime($d . ' 12:00'))) . '</text>';
        $s .= '<text x="' . round($x + $bw / 2, 1) . '" y="' . ($H - 6) . '" text-anchor="middle" font-size="14" fill="#b8bec8">' . esc_html(date_i18n('j M', strtotime($d . ' 12:00'))) . '</text>';
    }
    $s .= '</svg>';
    $in = '<p class="fd-muted">Grams per day from the foods with omega-3 data (– = nothing logged).</p>' . $s
        . '<p class="np-leg"><span><i style="background:#5cc8c2"></i>Plant (ALA)</span><span><i style="background:#7fb2ff"></i>Marine/animal (EPA+DPA+DHA)</span></p>';
    return $bare ? $in : '<div class="fd-box np-o3w"><h3>Omega-3 · last 7 days</h3>' . $in . '</div>';
}

/* ---------- carbs per hour and energy vs duration and intensity (12 weeks) ---------- */
function cc_np_sport($s) {
    $s = strtolower((string) $s);
    if (preg_match('/cycl|ride|bik|mtb|gravel|velo/', $s)) return 'ride';
    if (preg_match('/run|jog/', $s)) return 'run';
    if (preg_match('/train|strength|gym|weight|core|crossfit|mobility|yoga|pilates/', $s)) return 'gym';
    if (preg_match('/hik|walk|trek/', $s)) return 'hike';
    return 'other';
}
function cc_np_sessions($pid, $vx) {
    $by = []; foreach ((array) ($vx['acts'] ?? []) as $a) if (!empty($a['d']) && (int) ($a['s'] ?? 0) >= 600) $by[$a['d']][] = $a;
    $out = []; $nofood = 0;
    foreach ($by as $d => $list) {
        usort($list, function ($a, $b) { $ra = cc_np_sport($a['sp'] ?? '') === 'ride'; $rb = cc_np_sport($b['sp'] ?? '') === 'ride'; return $ra !== $rb ? ($ra ? -1 : 1) : (int) $b['s'] - (int) $a['s']; });   /* the day's longest ride first */
        $bike = cc_fd_get($pid, $d)['s']['bike'] ?? null; $carb = ($bike && !empty($bike['i'])) ? cc_fd_tot($bike['i'])['c'] : null;
        foreach ($list as $ix => $a) {
            $h = (int) $a['s'] / 3600; $kc = $a['kc'] ?? null; $ks = 'cal';
            if (!$kc && !empty($a['kj'])) { $kc = (int) $a['kj']; $ks = 'kj'; }
            $g = ($ix === 0 && $carb !== null) ? round($carb / $h, 1) : null;
            if ($ix === 0 && $carb === null) $nofood++;
            $out[] = ['d' => $d, 'n' => (string) ($a['n'] ?? ''), 'sp' => cc_np_sport($a['sp'] ?? ''), 'h' => round($h, 2), 'i' => isset($a['i']) && is_numeric($a['i']) ? (float) $a['i'] : null, 'g' => $g, 'k' => $kc ? (int) $kc : null, 'ks' => $ks];
        }
    }
    return ['s' => $out, 'nofood' => $nofood];
}
/* ---------- "Diet and fuelling analysis" (Matteo, 20 Nov 2026): every analysis piece for Marine and Matteo in one section of the review,
 * each one foldable: macro split (kcal and %, day + 7-day average), carbs per hour during exercise, energy burned, omega-3 (day + 7 days),
 * food families (day + 7 days) and the 12-week trends. Nothing of this is repeated under the days any more. Never shown to athletes. */
function cc_np_analysis($pid) {
    $tp = cc_ath_tp($pid); $vx = $tp ? [] : cc_fd_vx($pid); $mine = cc_fd_mine($pid); $kg = cc_fd_kgv($pid)['kg']; $today = current_time('Y-m-d');
    $day = cc_fd_date($_GET['an'] ?? '');
    if (!$day || $day > $today) { $day = $today; foreach (cc_fd_days($pid) as $dd) if ($dd <= $today) { $day = $dd; break; } }
    $t0 = strtotime($day . ' 12:00'); $lbl = date_i18n('D j M', $t0); $sum = ['k' => 0, 'c' => 0, 'p' => 0, 'f' => 0, 'fi' => 0, 'su' => 0]; $alc = 0; $n = 0; $dd0 = null; $t1 = null; $a1 = 0;
    for ($i = 0; $i < 7; $i++) {
        $dd = cc_fd_get($pid, gmdate('Y-m-d', $t0 - $i * DAY_IN_SECONDS)); $t = cc_fd_daytot($dd); $a = $t['k'] > 0 ? cc_np_alc($dd, $mine) : 0;
        if ($i === 0) { $dd0 = $dd; $t1 = $t; $a1 = $a; }
        if ($t['k'] > 0) { $n++; foreach ($sum as $k => $_) $sum[$k] += (float) $t[$k]; $alc += $a; }
    }
    $fold = function ($k, $title, $body, $open = false, $cls = '') { return '<details class="np-anp' . ($cls ? ' ' . $cls : '') . '" data-k="' . $k . '"' . ($open ? ' open' : '') . '><summary>' . $title . '</summary><div class="np-anb">' . $body . '</div></details>'; };
    $keep = ''; foreach (['food', 'board', 'ath', 'fo'] as $q) if (isset($_GET[$q])) $keep .= '<input type="hidden" name="' . $q . '" value="' . esc_attr(sanitize_key($_GET[$q])) . '">';
    $o = '<section class="fd-box np-an" id="fd-analysis"><h3>Diet and fuelling analysis</h3>'
       . '<form method="get" action="#fd-analysis" class="np-anf">' . $keep . '<label>Day <input type="date" name="an" value="' . esc_attr($day) . '" max="' . esc_attr($today) . '"></label><button type="submit" class="btn btn-ghost">Show</button>'
       . '<span class="np-sub">Day pieces use ' . esc_html($lbl) . '; 7-day pieces the 7 days up to it.</span></form>';
    // 1. macro split
    $b = ($t1 && $t1['k'] > 0) ? '<p class="np-anl">' . esc_html($lbl) . '</p><div class="fd-rtot">' . cc_np_macro_spans($t1, $kg, $a1) . '<span>Fibre ' . round($t1['fi']) . ' g</span><span>Sugars ' . round($t1['su']) . ' g</span></div>' : '<p class="fd-muted">Nothing logged on ' . esc_html($lbl) . '.</p>';
    if ($n) { $avg = []; foreach ($sum as $k => $v) $avg[$k] = $v / $n; $b .= '<p class="np-anl">7-day average (' . $n . ' logged day' . ($n === 1 ? '' : 's') . ')</p><div class="fd-rtot">' . cc_np_macro_spans($avg, $kg, $alc / $n) . '<span>Fibre ' . round($avg['fi']) . ' g</span><span>Sugars ' . round($avg['su']) . ' g</span></div>'; }
    $o .= $fold('mac', 'Macro split · kcal and %', $b, true);
    // 2 + 3. carbs per hour and energy burned (12 weeks)
    if (!$tp) {
        if (empty($vx['acts'])) $o .= $fold('cph', 'Carbs per hour during exercise · 12 weeks', '<p class="fd-muted">No sessions yet: they arrive with the next sync from Matteo’s laptop.</p>', true);
        else {
            $S = cc_np_sessions($pid, $vx);
            $o .= $fold('cph', 'Carbs per hour during exercise · 12 weeks', '<p class="fd-muted">One dot per session: duration across, carbs per hour from the athlete’s “On the bike” foods that day (given to the day’s longest ride, else its longest session). Colour = Vekta intensity; shape = sport. Tap or hover a dot.'
                . ($S['nofood'] ? ' ' . $S['nofood'] . ' training day' . ($S['nofood'] === 1 ? '' : 's') . ' without “On the bike” food logged are not shown.' : '') . '</p><div class="np-sc" data-kind="g" data-sc="' . esc_attr(wp_json_encode($S['s'])) . '"></div>', true, 'np-ch');
            $o .= $fold('kcal', 'Energy burned · 12 weeks', '<p class="fd-muted">One dot per session: duration across, kcal burned up (Vekta calories; if missing, work in kJ ≈ kcal, ringed dot). Colour = Vekta intensity; shape = sport.</p><div class="np-sc" data-kind="k" data-sc="' . esc_attr(wp_json_encode($S['s'])) . '"></div>', false, 'np-ch');
        }
    }
    // 4. omega-3
    $o3 = $dd0 ? cc_np_o3_html(cc_np_o3($dd0, $mine)) : '';
    $o .= $fold('o3', 'Omega-3 · day and 7 days', '<p class="np-anl">' . esc_html($lbl) . '</p>' . ($o3 ?: '<p class="fd-muted">Nothing logged this day.</p>') . '<p class="np-anl">7 days up to ' . esc_html($lbl) . '</p>' . cc_np_o3_week($pid, $day, true), false, 'np-o3w');
    // 4b. supplements (20 Nov 2026): which ones, on how many of the 7 days, and the doses (never in kcal or macros)
    if (function_exists('cc_fd_supp_clean')) {
        $sp = [];
        for ($i = 0; $i < 7; $i++) {
            foreach (cc_fd_supp_clean(cc_fd_get($pid, gmdate('Y-m-d', $t0 - $i * DAY_IN_SECONDS))['sp'] ?? []) as $x) {
                $lb = cc_fd_supp_label($x); $key = mb_strtolower($lb); $sp[$key]['n'] = $lb; $sp[$key]['days'][$i] = 1;
                $ds = cc_fd_supp_dose($x); if ($ds !== '') $sp[$key]['dose'][$ds] = ($sp[$key]['dose'][$ds] ?? 0) + 1;
            }
        }
        uasort($sp, function ($a, $b) { return count($b['days']) <=> count($a['days']) ?: strcmp($a['n'], $b['n']); });
        if ($sp) {
            $tb = '<table class="np-spt"><thead><tr><th>Supplement</th><th>Days</th><th>Doses</th></tr></thead><tbody>';
            foreach ($sp as $x) { $dz = []; foreach ((array) ($x['dose'] ?? []) as $ds => $c) $dz[] = esc_html($ds) . ($c > 1 ? ' ×' . $c : '');
                $tb .= '<tr><td>' . esc_html($x['n']) . '</td><td>' . count($x['days']) . ' of 7</td><td>' . ($dz ? implode(' · ', $dz) : '–') . '</td></tr>'; }
            $b = '<p class="fd-muted">7 days up to ' . esc_html($lbl) . '. Logged by the athlete; not counted in kcal or macros.</p>' . $tb . '</tbody></table>';
        } else $b = '<p class="fd-muted">No supplements logged in the 7 days up to ' . esc_html($lbl) . '.</p>';
        $o .= $fold('sup', 'Supplements · 7 days', $b . '<style>html .cc .np-spt{width:100%;border-collapse:collapse;font-size:15px;color:#d0d6e0}html .cc .np-spt th{text-align:left;color:#b8bec8;font-size:14px;font-weight:700;padding:6px 8px;border-bottom:1px solid rgba(255,255,255,.15)}'
            . 'html .cc .np-spt td{padding:7px 8px;border-bottom:1px solid rgba(255,255,255,.08);vertical-align:top;overflow-wrap:anywhere}html .cc .np-spt td:first-child{color:#fff;font-weight:600}</style>', false);
    }
    // 5. food families
    $o .= $fold('fam', 'Food families · sugars, carbs, fibre (day and 7 days)', cc_np_fam_html($pid, $day, $mine, true), false, 'np-fa');
    // 6. 12-week trends (weight, HRV, resting HR)
    if (!$tp) {
        $fem = cc_fd_female($pid, $vx); $cy = $fem ? cc_fd_cycle($pid) : null; if ($cy && empty($cy['on'])) $cy = null;
        $tb = preg_replace('#<h3>.*?</h3>#', '', cc_fd_trends_box($pid, $vx, $cy), 1);
        $o .= $fold('tr', 'Trends · weight, HRV, resting HR (12 weeks)', $tb, false, 'fd-trd');
    }
    return $o . '</section>';
}
add_filter('cc_fd_review_top', function ($html, $pid, $viewer) {
    return $html . cc_np_analysis($pid) . cc_np_css() . cc_np_js();
}, 10, 3);

/* ---------- Marine's day targets form (next 7 days, after the meal plan) ---------- */
add_filter('cc_fd_review_plan', function ($html, $pid, $viewer) {
    if (!cc_fd_on($pid)) return $html;
    $dates = cc_np_dates(current_time('Y-m-d'), 8); $set = cc_np_tg_get($pid); $auto = cc_np_targets($pid, $dates); $rows = '';
    $lbl = ['set' => 'your day targets', 'plan' => 'meal plan total', 'text' => 'your plan text', 'note' => 'your Vekta note'];
    foreach ($dates as $d) {
        $cur = $set[$d] ?? []; $a = $auto[$d] ?? []; $inp = '';
        foreach (['k' => 'kcal', 'c' => 'Carbs g', 'p' => 'Protein g', 'f' => 'Fat g'] as $k => $n) {
            $ph = (!isset($cur[$k]) && !empty($a[$k])) ? (string) $a[$k] : '';
            $inp .= '<label>' . $n . '<input type="number" inputmode="numeric" min="0" max="' . ($k === 'k' ? 10000 : 2000) . '" step="1" data-d="' . esc_attr($d) . '" data-k="' . $k . '" value="' . esc_attr($cur[$k] ?? '') . '" placeholder="' . esc_attr($ph) . '"></label>';
        }
        $src = []; foreach ((array) ($a['src'] ?? []) as $k => $s) if ($s !== 'set') $src[$s] = 1;
        $rows .= '<div class="np-tgr"><b>' . esc_html(date_i18n('D j M', strtotime($d . ' 12:00'))) . '</b><div class="np-tgi">' . $inp . '</div>'
            . ($src ? '<small>Grey numbers: from ' . esc_html(implode(' + ', array_map(function ($s) use ($lbl) { return $lbl[$s]; }, array_keys($src)))) . ' (used unless you type your own).</small>' : '') . '</div>';
    }
    return $html . '<div class="fd-box np-tg" id="np-tg" data-page="' . (int) $pid . '" data-url="' . esc_attr(esc_url_raw(rest_url('cc/v1/np-targets'))) . '" data-nonce="' . esc_attr(wp_create_nonce('wp_rest')) . '">'
        . '<h3>Day targets</h3><p class="fd-muted">The athlete sees progress towards these under their day (e.g. “1,250 of 2,000 kcal · 750 to go”, positive wording only). Your numbers here win; otherwise the meal-plan total, then numbers in your plan text or Vekta nutrition note (e.g. “2000 kcal, carbs 300 g, protein 140 g”). Leave a box empty to use those.</p>'
        . $rows . '<p class="fd-row"><button type="button" class="btn btn-go np-tgsave">Save day targets</button><span class="fd-msg" role="status"></span></p></div>' . cc_np_css() . cc_np_js();
}, 20, 3);

/* ---------- under each day of the review: target vs eaten, omega-3, food-family analysis ---------- */
function cc_np_fam_set() { $a = json_decode((string) get_option('cc_np_fam', ''), true); return ['f' => (array) ($a['f'] ?? []), 'o' => (array) ($a['o'] ?? [])]; }
/* the classified entries eaten on a day: [dim => [value => [label => 1]]] (families, or foods with their own setting) */
function cc_np_fam_day($day, $mine, $set) {
    $D = cc_np_db(); $own = cc_fd_own_idx($mine); $o = []; $ids = [];
    foreach ((array) ($day['s'] ?? []) as $s) foreach ((array) ($s['i'] ?? []) as $it) {
        if (($it['g'] ?? 0) <= 0) continue;
        if (($it['m'] ?? '') === 'r' && !empty($own[$it['id']]['ing'])) { foreach ($own[$it['id']]['ing'] as $i) $ids[] = [(string) ($i['id'] ?? ''), (string) ($i['n'] ?? '')]; }
        else $ids[] = [(string) ($it['id'] ?? ''), (string) ($it['n'] ?? '')];
    }
    foreach ($ids as [$id, $nm]) {
        $ov = $set['o'][$id] ?? null; $fi = cc_np_famof($id); $fs = $fi === null ? null : ($set['f'][$fi] ?? null);
        foreach (CC_NP_DIMS as $dim => $_) {
            if ($ov && !empty($ov[$dim])) $o[$dim][$ov[$dim]][$nm . ' (own setting)'] = 1;
            elseif ($fs && !empty($fs[$dim])) $o[$dim][$fs[$dim]][$D['families'][$fi][0] ?? '?'] = 1;
        }
    }
    return $o;
}
function cc_np_fam_html($pid, $date, $mine, $bare = false) {
    $set = cc_np_fam_set(); $link = esc_url(cc_ath_is_coach() ? add_query_arg('board', 'families', cc_fd_hub()) : add_query_arg('ff', '1', cc_fd_hub()));
    $none = '<p class="fd-muted">No food families classified yet. Set sugars, carbs and fibre per family on the <a href="' . $link . '">Food families</a> page; the analysis then lists the families eaten under each one (no quantities).</p>';
    if (!$set['f'] && !$set['o']) return $bare ? $none : '<details class="np-fa"><summary>Food-family analysis</summary>' . $none . '</details>';
    $today = cc_np_fam_day(cc_fd_get($pid, $date), $mine, $set);
    $wk = []; $t0 = strtotime($date . ' 12:00');
    for ($i = 0; $i < 7; $i++) { $dd = cc_np_fam_day(cc_fd_get($pid, gmdate('Y-m-d', $t0 - $i * DAY_IN_SECONDS)), $mine, $set); foreach ($dd as $dim => $vals) foreach ($vals as $v => $labs) foreach ($labs as $l => $_) $wk[$dim][$v][$l] = ($wk[$dim][$v][$l] ?? 0) + 1; }
    $h = '';
    foreach (CC_NP_DIMS as $dim => [$title, $vals]) {
        $rows = '';
        foreach ($vals as $v => $vn) {
            $l = array_keys($today[$dim][$v] ?? []); $w = $wk[$dim][$v] ?? []; arsort($w);
            if (!$l && !$w) continue;
            $rows .= '<li><b>' . esc_html($vn) . ':</b> ' . ($l ? esc_html(implode(', ', $l)) : '<span class="fd-muted">none this day</span>')
                . ($w ? '<small>7 days: ' . esc_html(implode(', ', array_map(function ($k, $n) { return $k . ' ' . $n . '/7'; }, array_keys($w), $w))) . '</small>' : '') . '</li>';
        }
        if ($rows) $h .= '<h5>' . esc_html($title) . '</h5><ul>' . $rows . '</ul>';
    }
    $in = ($h ?: '<p class="fd-muted">None of the foods eaten this week belong to a classified family yet.</p>') . '<p class="np-sub"><a href="' . $link . '">Food families settings</a></p>';
    return $bare ? $in : '<details class="np-fa"><summary>Food-family analysis</summary>' . $in . '</details>';
}
add_filter('cc_fd_review_day_extra', function ($html, $pid, $date, $viewer) {
    $day = cc_fd_get($pid, $date); $has = false; foreach ((array) ($day['s'] ?? []) as $s) if (!empty($s['i'])) $has = true;
    $tg = cc_np_targets($pid, [$date])[$date] ?? null; $o = '';
    if ($tg) {
        $t = cc_fd_daytot($day); $lbl = ['set' => 'your day targets', 'plan' => 'meal plan', 'text' => 'your plan text', 'note' => 'your Vekta note'];
        $bar = function ($v, $mx, $big = false) { $pc = $mx > 0 ? min(100, $v / $mx * 100) : 0; return '<div class="fd-tgb' . ($big === true ? ' big' : ($big ? ' ' . $big : '')) . '"><i' . ($v >= $mx ? ' class="ok"' : '') . ' style="width:' . round($pc, 1) . '%"></i></div>'; };
        $h = '';
        if (!empty($tg['k'])) { $k = round($t['k']); $h .= '<p class="np-tgk"><b>' . number_format($k) . '</b> of ' . number_format($tg['k']) . ' kcal' . ($k >= $tg['k'] ? ' · <span class="ok">reached ✓</span>' : ' · ' . number_format($tg['k'] - $k) . ' to go') . ' <small>(' . round($k / $tg['k'] * 100) . ' %)</small></p>' . $bar($k, $tg['k'], true); }
        $m = '';
        foreach (['c' => 'Carbs', 'p' => 'Protein', 'f' => 'Fat'] as $k => $nm) if (!empty($tg[$k])) { $v = round($t[$k]); $m .= '<div><span class="mc-' . $k . '">' . $nm . '</span>' . $bar($v, $tg[$k], 'mc-' . $k) . '<small>' . number_format($v) . ' of ' . number_format($tg[$k]) . ' g' . ($v >= $tg[$k] ? ' ✓' : '') . '</small></div>'; }
        if ($m) $h .= '<div class="fd-tgm">' . $m . '</div>';
        $src = array_unique(array_values((array) ($tg['src'] ?? [])));
        if ($h) $o .= '<div class="fd-tgt np-tgt">' . $h . '<p class="np-sub">Day target from ' . esc_html(implode(' + ', array_map(function ($s) use ($lbl) { return $lbl[$s]; }, $src))) . (!empty($tg['fi']) ? ' · fibre at least ' . (int) $tg['fi'] . ' g (eaten ' . round($t['fi']) . ' g)' : '') . '.</p></div>';
        if (!empty($tg['sl']) || !empty($tg['bk'])) {
            $rows = '';
            foreach (array_merge(CC_FD_SLOTS, ['gym']) as $sk) {
                $st = $tg['sl'][$sk] ?? null; if (!$st) continue;
                $s = $day['s'][$sk] ?? ['i' => []]; $et = cc_fd_tot($s['i'] ?? []); $fl = cc_fd_fluids(['s' => [$s]]); $p = [];
                foreach (['c' => 'C', 'p' => 'P', 'f' => 'F'] as $k => $ab) if (!empty($st[$k])) $p[] = cc_fd_mlbl($k, $ab) . ' ' . round($et[$k]) . '/' . (int) $st[$k] . ' g';
                if (!empty($st['w'])) $p[] = 'water ' . ($fl[0] + $fl[1]) . '/' . (int) $st['w'] . ' ml';
                $rows .= '<li><span class="fd-sicw">' . cc_fd_icon($sk) . '</span><b>' . esc_html($sk === 'gym' ? 'Gym' : cc_fd_w($sk)) . '</b> <span>' . implode(' · ', $p) . '</span></li>';
            }
            if (!empty($tg['bk'])) $rows .= '<li><b>On the bike, per hour</b> ' . esc_html(implode(' · ', array_filter([!empty($tg['bk']['ch']) ? $tg['bk']['ch'] . ' g carbs' : '', !empty($tg['bk']['mlh']) ? $tg['bk']['mlh'] . ' ml' : '']))) . ' <small>(eaten: see On the bike above)</small></li>';
            $o .= '<details class="np-fa" open><summary>Targets by meal (eaten / your note)</summary><ul class="np-sl">' . $rows . '</ul></details>';
        }
    }
    return $html . ($o ? '<div class="np-day">' . $o . '</div>' . cc_np_css() : '');
}, 20, 4);

/* ---------- macro split for Marine and Matteo (19 Nov 2026): each macro's kcal and share; athletes keep grams only ---------- */
function cc_np_alc($day, $mine) {
    $rec = (array) cc_fd_recipes($mine); $a = 0;
    foreach ((array) ($day['s'] ?? []) as $s) foreach ((array) ($s['i'] ?? []) as $it) { $g = (float) ($it['g'] ?? 0); if ($g <= 0) continue; $v = cc_np_m100($it['id'] ?? '', $rec, 'alc'); if ($v) $a += $v * $g / 100; }
    return $a;
}
/* "Carbs 438 g · 1,752 kcal (75 %) (6.0 g/kg)" ... and "Total 2,341 kcal": 4/4/9 (alcohol 7) kcal per g; the % use the sum of the macro kcal so they add up to 100 */
function cc_np_macro_spans($t, $kg, $alc = 0) {
    $rows = [['Carbs', $t['c'], 4, 'c'], ['Protein', $t['p'], 4, 'p'], ['Fat', $t['f'], 9, 'f']]; if ($alc >= 0.5) $rows[] = ['Alcohol', $alc, 7, ''];
    $sum = 0; foreach ($rows as $r) $sum += $r[1] * $r[2];
    $o = '';
    foreach ($rows as $r) {
        $kc = $r[1] * $r[2];
        $o .= '<span>' . ($r[3] ? cc_fd_mlbl($r[3], $r[0]) : $r[0]) . ' ' . number_format(round($r[1])) . ' g · ' . number_format(round($kc)) . ' kcal' . ($sum > 0 ? ' (' . round($kc / $sum * 100) . ' %)' : '') . ($kg && $r[0] !== 'Alcohol' ? ' (' . number_format($r[1] / $kg, 1) . ' g/kg)' : '') . '</span>';
    }
    return $o . '<span><b>Total ' . number_format(round($sum)) . ' kcal</b>' . (abs($sum - $t['k']) >= 20 ? ' <small>(food tables: ' . number_format(round($t['k'])) . ' kcal)</small>' : '') . '</span>';
}
/* ---------- the Food families page (Marine and Matteo) ---------- */
function cc_np_fam_page($viewer) {
    $GLOBALS['cc_ath_lang'] = 'en';
    $D = cc_np_db(); $set = cc_np_fam_set();
    $cfg = ['fams' => $D['families'], 'set' => ['f' => (object) $set['f'], 'o' => (object) $set['o']], 'dims' => CC_NP_DIMS, 'nonce' => wp_create_nonce('wp_rest'),
            'foods' => esc_url_raw(add_query_arg('v', get_option('cc_food_db_v', '0'), rest_url('cc/v1/foods'))), 'u' => esc_url_raw(rest_url('cc/v1/np-fam'))];
    $back = $viewer === 'nutri' ? cc_fd_hub() : add_query_arg('board', 'food', cc_fd_hub());
    return '<section class="ath-s fd-rv np-ff" id="food-families"><p class="fd-back"><a href="' . esc_url($back) . '">← ' . ($viewer === 'nutri' ? 'Home' : 'Food diaries') . '</a></p>'
        . '<h2>' . cc_ath_icon('food', 'ath-hic') . 'Food families</h2>'
        . '<p class="fd-lede">Every food family in the food tables (CIQUAL, USDA, CoFID), in one list. Set for each family how its sugars, carbs and fibre count in your analysis; all start as “not classified yet”. Under each day of a food diary, the folded “Food-family analysis” then lists the families eaten under each heading (no quantities), with how often in the last 7 days. Only you and Matteo see this.</p>'
        . '<div class="np-ffapp" data-cfg="' . esc_attr(wp_json_encode($cfg)) . '"><p class="fd-muted">Loading…</p></div></section>' . cc_fd_css() . cc_np_css() . cc_np_js();
}
add_filter('cc_ath_nutritionist', function ($html, $me) {
    if (!user_can($me, 'cc_nutrition')) return $html;
    if (!empty($_GET['ff'])) return cc_np_fam_page('nutri');
    if (!empty($_GET['food']) || isset($_GET['mp'])) return $html;
    $card = '<section class="ath-s np-home" id="food-families-card"><h2>' . cc_ath_icon('food', 'ath-hic') . 'Food families</h2><p class="fd-lede">Classify food families (sugars natural / free, carbs slow / fast, fibre soluble / insoluble / mixed) for the food-family analysis under each diary day.</p>'
        . '<p><a class="btn btn-go" href="' . esc_url(add_query_arg('ff', '1', cc_fd_hub())) . '">Open food families</a></p></section>';
    $pos = strpos($html, '<section class="ath-s fd-rv" id="food-diaries">');
    return $pos === false ? $html . $card : substr_replace($html, $card, $pos, 0);
}, 22, 2);
add_filter('cc_ath_coach_links', function ($html) { return $html . '<a class="av-boardlink" href="' . esc_url(add_query_arg('board', 'families', cc_fd_hub())) . '">Food families</a>'; }, 23);
add_filter('cc_ath_board', function ($html, $board) { return ($board === 'families' && cc_ath_is_coach()) ? cc_np_fam_page('coach') : $html; }, 10, 2);

/* ---------- REST ---------- */
add_action('rest_api_init', function () {
    register_rest_route('cc/v1', '/np-targets', ['methods' => 'POST', 'permission_callback' => 'cc_fd_staff', 'callback' => function (WP_REST_Request $r) {
        $pid = (int) $r->get_param('page');
        if (!$pid || get_post_type($pid) !== 'cc_athlete' || (cc_fd_is_nutri() && !cc_fd_on($pid))) return new WP_Error('cc_no', 'Not allowed', ['status' => 403]);
        $in = json_decode((string) $r->get_param('data'), true); if (!is_array($in)) return new WP_Error('cc_bad', 'Data needed', ['status' => 400]);
        $cur = cc_np_tg_get($pid); $now = strtotime(current_time('Y-m-d') . ' 12:00');
        foreach ($in as $d => $v) {
            $d = cc_fd_date($d); if (!$d || abs(strtotime($d . ' 12:00') - $now) > 400 * DAY_IN_SECONDS) continue;
            $o = []; foreach (['k' => 10000, 'c' => 2000, 'p' => 2000, 'f' => 2000] as $k => $mx) { $x = (int) round(cc_fd_num($v[$k] ?? 0, $mx)); if ($x > 0) $o[$k] = $x; }
            if ($o) $cur[$d] = $o; else unset($cur[$d]);
        }
        ksort($cur); if (count($cur) > 500) $cur = array_slice($cur, -500, null, true);
        if ($cur) update_post_meta($pid, 'cc_np_tg', wp_slash(wp_json_encode($cur))); else delete_post_meta($pid, 'cc_np_tg');
        return ['ok' => true, 'tg' => (object) $cur];
    }]);
    register_rest_route('cc/v1', '/np-fam', ['methods' => 'POST', 'permission_callback' => 'cc_fd_staff', 'callback' => function (WP_REST_Request $r) {
        $in = json_decode((string) $r->get_param('data'), true); if (!is_array($in)) return new WP_Error('cc_bad', 'Data needed', ['status' => 400]);
        $n = count(cc_np_db()['families']); $o = ['f' => [], 'o' => []];
        $clean = function ($v) { $c = []; foreach (CC_NP_DIMS as $dim => [$_, $vals]) if (isset($v[$dim]) && isset($vals[$v[$dim]])) $c[$dim] = $v[$dim]; return $c; };
        foreach ((array) ($in['f'] ?? []) as $i => $v) { $i = (int) $i; if ($i < 0 || $i >= $n || !is_array($v)) continue; $c = $clean($v); if ($c) $o['f'][$i] = $c; }
        foreach (array_slice((array) ($in['o'] ?? []), 0, 500, true) as $id => $v) {
            $id = mb_substr(preg_replace('/[^A-Za-z0-9_-]/', '', (string) $id), 0, 40); if ($id === '' || !is_array($v)) continue;
            $c = $clean($v); if ($c) $o['o'][$id] = ['n' => cc_fd_txt($v['n'] ?? '', 200)] + $c;
        }
        update_option('cc_np_fam', wp_json_encode(['f' => (object) $o['f'], 'o' => (object) $o['o']]), false);
        return ['ok' => true, 'set' => ['f' => (object) $o['f'], 'o' => (object) $o['o']]];
    }]);
});

/* ---------- look ---------- */
function cc_np_css() {
    static $done = false; if ($done) return ''; $done = true;
    return '<style>'
        . 'html .cc .np-top{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,420px),1fr));gap:12px;margin:12px 0}'
        . 'html .cc .np-sc{position:relative;width:100%;min-height:270px;touch-action:pan-y}html .cc .np-sc>svg{display:block;width:100%;height:auto;touch-action:pan-y}html .cc .np-leg svg{display:inline-block;width:18px!important;height:18px!important;flex:none}'
        . 'html .cc .np-tip{position:absolute;z-index:3;pointer-events:none;max-width:260px;padding:8px 10px;border-radius:10px;background:#0b0d0f;border:1px solid rgba(255,255,255,.25);color:#e6e9ee;font-size:14px;line-height:1.4;box-shadow:0 6px 20px rgba(0,0,0,.4)}'
        . 'html .cc .np-tip b{color:#fff}html .cc .np-leg{display:flex;flex-wrap:wrap;gap:6px 14px;margin:8px 0 0;font-size:14px;color:#d0d6e0}html .cc .np-leg span{display:inline-flex;align-items:center;gap:6px}'
        . 'html .cc .np-leg i{display:inline-block;width:12px;height:12px;border-radius:3px}'
        . 'html .cc .np-o3w svg{display:block;width:100%;height:auto}'
        . 'html .cc .np-day{margin:10px 0 0;padding:10px 12px;border-radius:12px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08);display:grid;gap:6px}'
        . 'html .cc .np-day p{margin:0;font-size:15px;color:#d0d6e0;line-height:1.5}html .cc .np-day p b{color:#fff}html .cc .np-day small,html .cc .np-sub{color:#b8bec8;font-size:14px}'
        . 'html .cc .np-fa summary{cursor:pointer;color:#2bd47a;font-weight:600;font-size:15px;min-height:40px;display:flex;align-items:center}'
        . 'html .cc .np-fa h5{margin:8px 0 4px;font-size:15px;color:#fff}html .cc .np-fa ul{margin:0;padding-left:18px;display:grid;gap:4px}html .cc .np-fa li{font-size:15px;color:#d0d6e0}html .cc .np-fa li small{display:block}'
        . 'html .cc .np-an{margin:8px 0 18px;display:grid;gap:10px;padding:14px 16px}html .cc .ath .np-an>h3{font:400 24px/1.15 var(--head,Anton),sans-serif!important;color:#fff;margin:0;letter-spacing:.01em}'
        . 'html .cc .np-anf{display:flex;flex-wrap:wrap;align-items:end;gap:8px 12px;margin:0}html .cc .np-anf label{display:grid;gap:4px;font-size:14px;color:#b8bec8}html .cc .np-anf input{width:auto!important;max-width:220px;font:16px var(--body);min-height:44px;padding:8px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.2);background:#0b0d0f;color:#fff;box-sizing:border-box}html .cc .np-anf .btn{min-height:44px;margin:0;width:auto!important;flex:none}html .cc .np-anf .np-sub{flex-basis:100%}'
        . 'html .cc .np-anp{border-top:1px solid rgba(255,255,255,.1)}html .cc .np-anp>summary{cursor:pointer;min-height:48px;display:flex;align-items:center;gap:8px;color:#fff;font:700 17px var(--body);list-style:none}html .cc .np-anp>summary::-webkit-details-marker{display:none}'
        . 'html .cc .np-anp>summary::before{content:"›";display:inline-grid;place-items:center;width:24px;color:#2bd47a;font-size:22px;transition:transform .2s}html .cc .np-anp[open]>summary::before{transform:rotate(90deg)}'
        . 'html .cc .np-anb{display:grid;gap:8px;padding:0 0 14px;min-width:0}html .cc .np-anl{margin:4px 0 0;color:#fff;font-size:15px;font-weight:700}html .cc .np-anb .fd-box{border:0;padding:0;background:none}'
        . 'html .cc .np-anb .fd-rtot{margin:0}html .cc .np-anlink{margin:6px 0 0;font-size:15px}html .cc .np-anlink a{color:#2bd47a}'
        . 'html .cc .np-tgt{margin:0}html .cc .np-tgk{font-size:16px!important;text-align:left}html .cc .np-tgk b{font-size:22px;color:#fff}html .cc .np-tgk .ok{color:#2bd47a;font-weight:700}html .cc .np-sl{list-style:none;padding:0!important}html .cc .np-sl li b{color:#fff}'
        . 'html .cc .np-tg{margin:12px 0}html .cc .np-tgr{display:grid;gap:6px;padding:10px 0;border-top:1px solid rgba(255,255,255,.08)}html .cc .np-tgr b{color:#fff;font-size:15px}html .cc .np-tgr small{color:#b8bec8;font-size:14px}'
        . 'html .cc .np-tgi{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}html .cc .np-tgi label{display:grid;gap:4px;font-size:14px;color:#b8bec8;min-width:0}'
        . 'html .cc .np-tgi input{width:100%;min-width:0;font:16px var(--body);padding:8px 10px;border-radius:10px;border:1px solid rgba(255,255,255,.2);background:#0b0d0f;color:#fff;box-sizing:border-box}'
        . 'html .cc .np-tgi input::placeholder{color:#8f97a3}'
        . 'html .cc .np-ff select,html .cc .np-ffs input{font:16px var(--body);min-height:44px;padding:8px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.2);background:#0b0d0f;color:#fff;box-sizing:border-box;max-width:100%}'
        . 'html .cc .np-fl{display:grid;gap:10px;margin:12px 0}html .cc .np-fc{padding:12px;border-radius:12px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.03);display:grid;gap:8px;min-width:0}'
        . 'html .cc .np-fc.on{border-color:rgba(43,212,122,.4)}html .cc .np-fch{display:flex;flex-wrap:wrap;align-items:baseline;justify-content:space-between;gap:4px 10px}html .cc .np-fch b{color:#fff;font-size:16px}html .cc .np-fch small{color:#b8bec8;font-size:14px}'
        . 'html .cc .np-fs{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}html .cc .np-fs label{display:grid;gap:4px;font-size:14px;color:#b8bec8;min-width:0}html .cc .np-fs select{width:100%}'
        . 'html .cc .np-ffbar{position:sticky;bottom:0;z-index:5;display:flex;flex-wrap:wrap;gap:10px;align-items:center;padding:10px 0;background:rgba(10,12,14,.94)}'
        . 'html .cc .np-ffs{display:grid;gap:8px;margin:8px 0}html .cc .np-ffs input{width:100%}html .cc .np-ffr{list-style:none;margin:0;padding:0;display:grid;gap:6px}'
        . 'html .cc .np-ffr button{width:100%;text-align:left;padding:10px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.03);color:#e6e9ee;font:15px var(--body);cursor:pointer}'
        . 'html .cc .np-ffr small{display:block;color:#b8bec8;font-size:14px}html .cc .np-ffx{flex:none;width:40px;height:40px;display:grid;place-items:center;padding:0;border-radius:10px;border:1px solid rgba(255,255,255,.15);background:none;color:#d0d6e0;cursor:pointer;font-size:20px}'
        . 'html .cc .np-ffm{color:#c9f3da;font-size:15px;font-weight:600}html .cc .np-ffm.err{color:#ffb4a8}'
        . '@media (max-width:560px){html .cc .np-fs{grid-template-columns:1fr;gap:6px}html .cc .np-fs label{grid-template-columns:64px minmax(0,1fr);align-items:center;font-size:15px;color:#d0d6e0}html .cc .np-tgi{grid-template-columns:repeat(2,minmax(0,1fr))}}'
        . '</style>';
}
function cc_np_js() {
    static $done = false; if ($done) return ''; $done = true;
    $js = <<<'JS'
(function(){
function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c];});}
function post(u,data,nonce){var f=new FormData();for(var k in data){f.append(k,data[k]);}return fetch(u,{method:"POST",body:f,credentials:"same-origin",headers:{"X-WP-Nonce":nonce}}).then(function(r){if(!r.ok){throw r;}return r.json();});}
function n0(x){return Math.round(+x||0).toLocaleString("en");}
function n1(x){return (Math.round((+x||0)*10)/10).toLocaleString("en");}
var IC=[["Easy (intensity < 25)","#3f9c96"],["Moderate (25–39)","#7fd6cf"],["Hard (40+)","#eaf8f6"],["No intensity","#8f97a3"]];
function icls(i){if(i==null){return 3;}return i<25?0:(i<40?1:2);}
var SP={ride:"Ride",run:"Run",gym:"Gym",hike:"Hike",other:"Other"};
function shape(sp,x,y,r,col,ring){var st=ring?' fill="none" stroke="'+col+'" stroke-width="2.5"':' fill="'+col+'" stroke="#0b0d0f" stroke-width="1"';
if(sp==="run"){return '<path d="M'+x+' '+(y-r-1)+'L'+(x+r+1)+' '+(y+r)+'L'+(x-r-1)+' '+(y+r)+'Z"'+st+'/>';}
if(sp==="gym"){return '<rect x="'+(x-r)+'" y="'+(y-r)+'" width="'+(2*r)+'" height="'+(2*r)+'"'+st+'/>';}
if(sp==="hike"){return '<path d="M'+x+' '+(y-r-2)+'L'+(x+r+2)+' '+y+'L'+x+' '+(y+r+2)+'L'+(x-r-2)+' '+y+'Z"'+st+'/>';}
if(sp==="other"){return '<path d="M'+(x-r)+' '+(y-r)+'L'+(x+r)+' '+(y+r)+'M'+(x+r)+' '+(y-r)+'L'+(x-r)+' '+(y+r)+'" stroke="'+col+'" stroke-width="3" fill="none"/>';}
return '<circle cx="'+x+'" cy="'+y+'" r="'+r+'"'+st+'/>';}
function nice(mx){var s=[1,2,5,10,20,25,50,100,200,250,500,1000,2000];for(var i=0;i<s.length;i++){if(mx/s[i]<=6){return s[i];}}return 5000;}
function scatter(el){var all=JSON.parse(el.dataset.sc||"[]"),kind=el.dataset.kind,pts=all.filter(function(p){return kind==="g"?p.g!=null:p.k!=null;});
if(!pts.length){el.innerHTML='<p class="fd-muted">'+(kind==="g"?"No session yet with “On the bike” food logged on its day.":"No energy values yet.")+'</p>';el.style.minHeight="0";return;}
var w=Math.max(280,Math.round(el.clientWidth||320)),h=270,pl=66,pr=12,pt=14,pb=46,xm=0,ym=0;pts.forEach(function(p){xm=Math.max(xm,p.h);ym=Math.max(ym,kind==="g"?p.g:p.k);});
xm=Math.max(1,Math.ceil(xm*1.1*2)/2);var ys=nice(ym*1.1),ymax=Math.max(ys,Math.ceil(ym*1.1/ys)*ys),xs=xm<=3?0.5:(xm<=6?1:2);
function X(v){return pl+v/xm*(w-pl-pr);}function Y(v){return pt+(1-v/ymax)*(h-pt-pb);}
var s='<svg viewBox="0 0 '+w+' '+h+'" width="'+w+'" height="'+h+'" role="img" aria-label="'+(kind==="g"?"Carbs per hour by session duration":"Energy burned by session duration")+'">';
for(var v=0;v<=ymax+1e-9;v+=ys){s+='<line x1="'+pl+'" x2="'+(w-pr)+'" y1="'+Y(v).toFixed(1)+'" y2="'+Y(v).toFixed(1)+'" stroke="rgba(255,255,255,'+(v?0.08:0.2)+')"/><text x="'+(pl-8)+'" y="'+(Y(v)+5).toFixed(1)+'" text-anchor="end" font-size="14" fill="#b8bec8">'+n0(v)+'</text>';}
for(var u=0;u<=xm+1e-9;u+=xs){s+='<text x="'+X(u).toFixed(1)+'" y="'+(h-pb+20)+'" text-anchor="middle" font-size="14" fill="#b8bec8">'+u+' h</text>';}
s+='<text x="'+(pl+(w-pl-pr)/2)+'" y="'+(h-6)+'" text-anchor="middle" font-size="14" fill="#d0d6e0">Session duration</text>';
s+='<text x="11" y="'+(pt+(h-pt-pb)/2)+'" text-anchor="middle" font-size="14" fill="#d0d6e0" transform="rotate(-90 11 '+(pt+(h-pt-pb)/2)+')">'+(kind==="g"?"Carbs g/h":"kcal")+'</text>';
var q=pts.map(function(p){return [X(p.h),Y(kind==="g"?p.g:p.k),p];});
q.forEach(function(a){s+=shape(a[2].sp,Math.round(a[0]*10)/10,Math.round(a[1]*10)/10,6,IC[icls(a[2].i)][1],kind==="k"&&a[2].ks==="kj");});
s+='<circle class="np-hl" r="11" fill="none" stroke="#fff" stroke-width="2" style="display:none"/></svg>';
var leg='<p class="np-leg">'+IC.map(function(c){return '<span><i style="background:'+c[1]+'"></i>'+esc(c[0])+'</span>';}).join("")+'</p><p class="np-leg">'+Object.keys(SP).map(function(k){return '<span><svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true">'+shape(k,9,9,6,"#d0d6e0",false)+'</svg>'+SP[k]+'</span>';}).join("")+'</p>';
el.innerHTML=s+'<div class="np-tip" hidden></div>'+leg;var svg=el.querySelector("svg"),tip=el.querySelector(".np-tip"),hl=el.querySelector(".np-hl");
function show(cx,cy){var r=svg.getBoundingClientRect(),mx=(cx-r.left)*w/r.width,my=(cy-r.top)*h/r.height,b=null,bd=1e9;q.forEach(function(a){var d=Math.pow(a[0]-mx,2)+Math.pow(a[1]-my,2);if(d<bd){bd=d;b=a;}});
if(!b||bd>40*40){tip.hidden=true;hl.style.display="none";return;}var p=b[2],dt=new Date(p.d+"T12:00:00").toLocaleDateString("en-IE",{weekday:"short",day:"numeric",month:"short"});
tip.innerHTML='<b>'+esc(dt)+'</b> · '+esc(SP[p.sp])+'<br>'+esc(p.n||"Session")+'<br>'+n1(p.h)+' h · intensity '+(p.i==null?"–":n0(p.i))+'<br>'+(kind==="g"?'<b>'+n0(p.g)+' g carbs/h</b> ('+n0(p.g*p.h)+' g on the bike)':'<b>'+n0(p.k)+' kcal</b>'+(p.ks==="kj"?" (work kJ ≈ kcal)":"")+' · '+n0(p.k/p.h)+' kcal/h');
tip.hidden=false;hl.setAttribute("cx",b[0]);hl.setAttribute("cy",b[1]);hl.style.display="";var px=b[0]*r.width/w,py=b[1]*r.height/h,tw=tip.offsetWidth||200;tip.style.left=Math.max(0,Math.min(r.width-tw,px-tw/2))+"px";tip.style.top=Math.max(0,py-(tip.offsetHeight||80)-14)+"px";}
svg.addEventListener("pointermove",function(e){show(e.clientX,e.clientY);});svg.addEventListener("pointerdown",function(e){show(e.clientX,e.clientY);});
svg.addEventListener("touchmove",function(e){if(e.touches[0]){show(e.touches[0].clientX,e.touches[0].clientY);}},{passive:true});
svg.addEventListener("pointerleave",function(e){if(e.pointerType==="mouse"){tip.hidden=true;hl.style.display="none";}});}
function scAll(){document.querySelectorAll(".np-sc[data-sc]").forEach(function(el){if(el.offsetParent!==null&&!el.dataset.done){el.dataset.done=1;scatter(el);}});}
scAll();document.addEventListener("toggle",function(e){if(e.target.open&&e.target.classList&&e.target.classList.contains("np-anp")){scAll();}},true);var rt=null;addEventListener("resize",function(){clearTimeout(rt);rt=setTimeout(function(){document.querySelectorAll(".np-sc[data-done]").forEach(function(el){scatter(el);});},250);});
document.querySelectorAll(".np-tg").forEach(function(box){var b=box.querySelector(".np-tgsave"),m=box.querySelector(".fd-msg");b.addEventListener("click",function(){var d={};box.querySelectorAll("input[data-d]").forEach(function(i){var x=d[i.dataset.d]||(d[i.dataset.d]={});x[i.dataset.k]=i.value;});
b.disabled=true;m.textContent="Saving…";post(box.dataset.url,{page:box.dataset.page,data:JSON.stringify(d)},box.dataset.nonce).then(function(){m.textContent="✓ Saved. The athlete sees it on their next visit.";b.disabled=false;}).catch(function(){m.textContent="Not saved. Try again.";b.disabled=false;});});});
var A=document.querySelector(".np-ffapp");if(!A){return;}
var C=JSON.parse(A.dataset.cfg),SET={f:C.set.f||{},o:C.set.o||{}},DB=null,CNT={},Q="",RES=[],dirty=false;
function norm(s){return String(s||"").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"");}
function sel(dim,val,attrs){var vals=C.dims[dim][1],h='<select '+attrs+'><option value="">Not classified yet</option>';Object.keys(vals).forEach(function(k){h+='<option value="'+k+'"'+(val===k?" selected":"")+'>'+esc(vals[k])+'</option>';});return h+'</select>';}
function selRow(o,attr){return '<div class="np-fs">'+Object.keys(C.dims).map(function(dim){return '<label>'+esc(C.dims[dim][0])+sel(dim,o&&o[dim],attr+' data-dim="'+dim+'"')+'</label>';}).join("")+'</div>';}
function render(){var nc=Object.keys(SET.f).length,h='<p class="np-sub">'+nc+' of '+C.fams.length+' families classified · '+Object.keys(SET.o).length+' per-food setting'+(Object.keys(SET.o).length===1?"":"s")+'.</p><div class="np-fl">';
C.fams.forEach(function(f,i){var o=SET.f[i];h+='<div class="np-fc'+(o&&Object.keys(o).length?" on":"")+'"><div class="np-fch"><b>'+esc(f[0])+'</b><small>'+(DB?n0(CNT[i]||0)+" foods":"")+(f[1]?" · drink":"")+'</small></div>'+selRow(o,'data-f="'+i+'"')+'</div>';});
h+='</div><h3>Per-food settings</h3><p class="fd-muted">A food set here follows its own setting instead of its family’s.</p><div class="np-ffs"><input type="search" class="np-q" placeholder="Search a food, e.g. dates, sports drink" value="'+esc(Q)+'" autocomplete="off"><ul class="np-ffr">'+resHtml()+'</ul></div><div class="np-fl">';
Object.keys(SET.o).forEach(function(id){var o=SET.o[id];h+='<div class="np-fc on"><div class="np-fch"><b>'+esc(o.n||id)+'</b><button type="button" class="np-ffx" data-rm="'+esc(id)+'" aria-label="Remove this food setting">×</button></div>'+selRow(o,'data-o="'+esc(id)+'"')+'</div>';});
h+='</div><div class="np-ffbar"><button type="button" class="btn btn-go np-save">Save</button><span class="np-ffm" role="status"></span></div>';A.innerHTML=h;}
function resHtml(){if(!Q.trim()){return "";}if(!DB){return '<li class="fd-muted">Loading foods…</li>';}var ws=norm(Q).split(/\s+/).filter(Boolean);RES=[];
for(var i=0;i<DB.length&&RES.length<12;i++){var r=DB[i],n=norm(r[2]);if(ws.every(function(w){return n.indexOf(w)>-1;})){RES.push(r);}}
if(!RES.length){return '<li class="fd-muted">No food found.</li>';}return RES.map(function(r,i){return '<li><button type="button" data-add="'+i+'">'+esc(r[2])+'<small>'+esc(r[12]!=null&&C.fams[r[12]]?C.fams[r[12]][0]:"")+'</small></button></li>';}).join("");}
function msg(t,err){var m=A.querySelector(".np-ffm");if(m){m.textContent=t;m.className="np-ffm"+(err?" err":"");}}
A.addEventListener("change",function(e){var s=e.target;if(s.tagName!=="SELECT"){return;}var dim=s.dataset.dim,tgt=null;
if(s.dataset.f!=null){tgt=SET.f[s.dataset.f]||(SET.f[s.dataset.f]={});}else if(s.dataset.o!=null){tgt=SET.o[s.dataset.o];}if(!tgt){return;}
if(s.value){tgt[dim]=s.value;}else{delete tgt[dim];}if(s.dataset.f!=null&&!Object.keys(tgt).length){delete SET.f[s.dataset.f];}
var c=s.closest(".np-fc");if(c&&s.dataset.f!=null){c.classList.toggle("on",!!SET.f[s.dataset.f]);}dirty=true;msg("Not saved yet");});
A.addEventListener("input",function(e){if(!e.target.classList.contains("np-q")){return;}Q=e.target.value;var ul=A.querySelector(".np-ffr");if(ul){ul.innerHTML=resHtml();}});
A.addEventListener("click",function(e){var b=e.target.closest("button");if(!b){return;}
if(b.dataset.add!=null){var r=RES[+b.dataset.add];if(!r){return;}if(!SET.o[r[0]]){SET.o[r[0]]={n:r[2]};}Q="";dirty=true;render();msg("Set the food’s headings, then Save");return;}
if(b.dataset.rm!=null){delete SET.o[b.dataset.rm];dirty=true;render();msg("Not saved yet");return;}
if(b.classList.contains("np-save")){b.disabled=true;msg("Saving…");post(C.u,{data:JSON.stringify(SET)},C.nonce).then(function(j){SET={f:j.set.f||{},o:j.set.o||{}};dirty=false;render();msg("✓ Saved");}).catch(function(){b.disabled=false;msg("Not saved. Try again.",true);});}});
addEventListener("beforeunload",function(e){if(dirty){e.preventDefault();e.returnValue="";}});
render();fetch(C.foods,{credentials:"omit"}).then(function(r){return r.json();}).then(function(d){DB=d.foods||[];DB.forEach(function(r){if(r[12]!=null){CNT[r[12]]=(CNT[r[12]]||0)+1;}});var y=scrollY;render();scrollTo(0,y);}).catch(function(){});
})();
JS;
    return '<script>' . str_replace(["\r", "\n"], ['', ' '], $js) . '</script>';
}
/* the shared text parser (voice logging in the diary, recipe import in the meal-plan library): numbers, units and everyday food words
   in en / it / pt / sl / sk to the English names of the food tables, plus portion choice. No paid service; runs in the browser. */
function cc_np_pjs() {
    static $done = false; if ($done) return ''; $done = true;
    $js = <<<'JS'
(function(){if(window.ccNpParse){return;}
function norm(s){return String(s||"").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"");}
var VN={en:{a:1,an:1,one:1,half:0.5,two:2,couple:2,three:3,four:4,five:5,six:6,seven:7,eight:8,nine:9,ten:10,twelve:12},
it:{un:1,uno:1,una:1,mezzo:0.5,mezza:0.5,due:2,tre:3,quattro:4,cinque:5,sei:6,sette:7,otto:8,nove:9,dieci:10,cento:100,duecento:200,trecento:300},
pt:{um:1,uma:1,meio:0.5,meia:0.5,dois:2,duas:2,tres:3,quatro:4,cinco:5,seis:6,sete:7,oito:8,nove:9,dez:10,cem:100,duzentos:200,trezentos:300},
sl:{en:1,ena:1,eno:1,eden:1,pol:0.5,dva:2,dve:2,tri:3,stiri:4,pet:5,sest:6,sedem:7,osem:8,devet:9,deset:10,sto:100,dvesto:200,tristo:300},
sk:{jeden:1,jedna:1,jedno:1,jednu:1,pol:0.5,dva:2,dve:2,tri:3,styri:4,pat:5,sest:6,sedem:7,osem:8,devat:9,desat:10,sto:100,dvesto:200,tristo:300}};
var VC={en:["and","plus","with","then"],it:["e","ed","con","poi","piu"],pt:["e","com","mais","depois"],sl:["in","ter","z","s","pa"],sk:["a","s","so","plus","potom"]};
var VF={en:["to","taste","optional","i","a","an","had","ate","have","eaten","drank","some","of","the","my","for","breakfast","lunch","dinner","about","around","also","just","bit"],
it:["q.b.","qb","q.b","a","piacere","ho","mangiato","bevuto","un","po","di","del","della","dello","dei","degli","delle","il","lo","la","i","gli","le","circa","anche","per","colazione","pranzo","cena","d"],
pt:["comi","bebi","de","do","da","dos","das","o","a","os","as","cerca","tambem","ao","um","pouco","almoco","jantar"],
sl:["sem","jedel","jedla","pojedel","pojedla","popil","popila","malo","priblizno","okoli","tudi","za","zajtrk","kosilo","vecerjo","od","iz"],
sk:["som","jedol","jedla","zjedol","zjedla","vypil","vypila","trochu","asi","okolo","aj","na","ranajky","obed","veceru","z","zo"]};
var VU=[["tsp",/\b(teaspoons?|tsp|cucchiain[oi]|colher(es)? de cha|cajn[aei] zlick[aei]|zlick[aei]|cajov[aeu] lyzick[aeuy]|lyzick[aeuy])\b/],
["tbsp",/\b(tablespoons?|tbsp|cucchiai[o]?|colher(es)?( de sopa)?|jediln[aei] zlic[aei]|zlic[aei]|polievkov[aeu] lyzic[aeuy]|lyzic[aeuy])\b/],
["g",/\b(g|gr|grams?|grammi|grammo|gramas?|gramov|grami|gramy|ml|millilitri|mililitros|mililitrov|mililitre)\b/],
["sl",/\b(slices?|fett[ae]|fatias?|rezin[aei]?|platk[ayo]v?|platok)\b/],["cup",/\b(cups?|tazz[ae]|chavenas?|xicaras?|skodelic[aei]|salk[ayu])\b/],
["pot",/\b(pots?|tubs?|vasett[oi]|copos?|potes?|lonck[aei]|loncek|teglik[ya]?|teglikov)\b/],["can",/\b(cans?|lattin[ae]|latas?|plocevink[aei]|plechovk[ayu])\b/],
["btl",/\b(bottles?|bottigli[ae]|garrafas?|steklenic[aei]|flas[ayu]|flias[ayu])\b/],["u",/\b(cloves?|spicchi[oa]?|dentes?|strok[aiov]?|struk[ya]?|units?|pieces?|pezz[oi]|unita|unidades?|pecas?|kos[a]?|kosov|kus[y]?|kusov)\b/],
["s",/\b(small|piccol[oaie]|pequen[oa]s?|majhn?[aei]?n?|mal[aeyu])\b/],["m",/\b(medium|medi[oaie]|srednj[aei]|stredn[aeyu])\b/],["l",/\b(large|big|grand[ei]|velik[aei]?|velk[aeyu])\b/]];
/* everyday food words in it / pt / sl / sk to the English names the food tables use (the search adds its own aliases) */
var VD={en:{"salt and pepper to taste":"salt","to taste":"",toast:"bread toasted",toasts:"bread toasted","brown bread":"bread wholemeal","white bread":"bread white",gel:"energy gel",gels:"energy gel",bar:"energy bar",bars:"energy bar","rice cake":"rice cakes",oats:"porridge oats",porridge:"porridge oats",eggs:"egg whole",egg:"egg whole",spuds:"potato"},it:{secchi:"",secco:"",secca:"",fresco:"",fresca:"",freschi:"",fresche:"",spicchio:"",spicchi:"",tritato:"",tritata:"",grattugiato:"",grattugiata:"",sale:"salt",pepe:"black pepper",farina:"wheat flour",lievito:"baking powder","olio extravergine oliva":"olive oil","olio extravergine":"olive oil","olio oliva":"olive oil","olio evo":"olive oil",aglio:"garlic",cipolla:"onion",basilico:"basil","passata pomodoro":"tomato puree",passata:"tomato puree","pomodori pelati":"tomatoes canned",spaghetti:"spaghetti",penne:"pasta",zucchine:"courgette",zucchina:"courgette",melanzana:"aubergine","yogurt greco":"greek yogurt","frutti bosco":"mixed berries",cannella:"cinnamon",uvette:"raisins",pane:"bread","pane tostato":"bread toasted",toast:"bread toasted",fetta:"",banana:"banana",banane:"banana",mela:"apple",mele:"apple",arancia:"orange",arance:"orange",pera:"pear",uva:"grapes",fragole:"strawberries",mirtilli:"blueberries",uovo:"egg whole",uova:"egg whole",latte:"milk",yogurt:"yogurt",avena:"oats","fiocchi d avena":"oats",porridge:"porridge",riso:"rice",pasta:"pasta",patate:"potato",patata:"potato",pollo:"chicken breast",manzo:"beef",carne:"beef",pesce:"fish",salmone:"salmon",tonno:"tuna",formaggio:"cheese",parmigiano:"parmesan",mozzarella:"mozzarella",burro:"butter salted",miele:"honey",marmellata:"jam",caffe:"coffee infusion",te:"tea",acqua:"water",succo:"juice","succo d arancia":"orange juice",birra:"beer",vino:"wine",zucchero:"sugar",cioccolato:"chocolate",biscotti:"biscuits",biscotto:"biscuit",torta:"cake",pizza:"pizza",insalata:"salad",pomodoro:"tomato",pomodori:"tomato",carote:"carrot",carota:"carrot",broccoli:"broccoli",spinaci:"spinach",fagioli:"beans",lenticchie:"lentils",ceci:"chickpeas",noci:"walnuts",mandorle:"almonds","burro di arachidi":"peanut butter",olio:"olive oil","olio d oliva":"olive oil",prosciutto:"ham",salame:"salami",salsiccia:"sausage",gel:"energy gel",barretta:"energy bar","bevanda sportiva":"sports drink",cornetto:"croissant",brioche:"croissant",cereali:"breakfast cereal",muesli:"muesli",granola:"granola",avocado:"avocado",datteri:"dates",uvetta:"raisins","gallette di riso":"rice cakes",galletta:"rice cake",panino:"sandwich",zuppa:"soup",minestra:"soup",bistecca:"beef steak",tacchino:"turkey",tofu:"tofu",hummus:"hummus",cappuccino:"cappuccino",espresso:"espresso",fette:"",biscottate:"rusks","fette biscottate":"rusks",ricotta:"ricotta",piadina:"wrap",crackers:"crackers",frutta:"fruit",verdura:"vegetables",verdure:"vegetables"},
pt:{pao:"bread",torrada:"bread toasted",torradas:"bread toasted",banana:"banana",bananas:"banana",maca:"apple",macas:"apple",laranja:"orange",pera:"pear",uvas:"grapes",morangos:"strawberries",mirtilos:"blueberries",ovo:"egg whole",ovos:"egg whole",leite:"milk",iogurte:"yogurt",aveia:"oats","flocos de aveia":"oats",papas:"porridge",arroz:"rice",massa:"pasta",esparguete:"spaghetti",batata:"potato",batatas:"potato",frango:"chicken breast",vaca:"beef",carne:"beef",peixe:"fish",salmao:"salmon",atum:"tuna",queijo:"cheese",manteiga:"butter salted",mel:"honey",doce:"jam",compota:"jam",cafe:"coffee infusion",cha:"tea",agua:"water",sumo:"juice","sumo de laranja":"orange juice",cerveja:"beer",vinho:"wine",acucar:"sugar",chocolate:"chocolate",bolachas:"biscuits",bolacha:"biscuit",bolo:"cake",pizza:"pizza",salada:"salad",tomate:"tomato",cenoura:"carrot",brocolos:"broccoli",espinafres:"spinach",feijao:"beans",lentilhas:"lentils","grao de bico":"chickpeas",grao:"chickpeas",nozes:"walnuts",amendoas:"almonds","manteiga de amendoim":"peanut butter",azeite:"olive oil",fiambre:"ham",presunto:"ham",chourico:"sausage",salsicha:"sausage",gel:"energy gel",barra:"energy bar","bebida desportiva":"sports drink",croissant:"croissant",cereais:"breakfast cereal",muesli:"muesli",granola:"granola",abacate:"avocado",tamaras:"dates",passas:"raisins","bolachas de arroz":"rice cakes",sandes:"sandwich",sanduiche:"sandwich",sopa:"soup",bife:"beef steak",peru:"turkey",tofu:"tofu",hummus:"hummus",galao:"latte",meia:"",fruta:"fruit",legumes:"vegetables",fatia:""},
sl:{kruh:"bread",kruha:"bread",toast:"bread toasted",banana:"banana",banano:"banana",banane:"banana",jabolko:"apple",jabolka:"apple",pomaranca:"orange",pomarance:"orange",hruska:"pear",grozdje:"grapes",jagode:"strawberries",borovnice:"blueberries",jajce:"egg whole",jajca:"egg whole",jajci:"egg whole",mleko:"milk",mleka:"milk",jogurt:"yogurt",jogurta:"yogurt",ovseni:"oats",kosmici:"oats","ovseni kosmici":"oats",kasa:"porridge",riz:"rice",riza:"rice",testenine:"pasta",spageti:"spaghetti",krompir:"potato",krompirja:"potato",piscanec:"chicken breast",piscanca:"chicken breast",govedina:"beef",meso:"beef",riba:"fish",losos:"salmon",tuna:"tuna",sir:"cheese",sira:"cheese",maslo:"butter salted",masla:"butter salted",maslom:"butter salted",medom:"honey",mlekom:"milk",jogurtom:"yogurt",med:"honey",medu:"honey",marmelada:"jam",marmelado:"jam",kava:"coffee infusion",kavo:"coffee infusion",caj:"tea",voda:"water",vode:"water",vodo:"water",sok:"juice","pomarancni sok":"orange juice",pivo:"beer",vino:"wine",sladkor:"sugar",cokolada:"chocolate",cokolado:"chocolate",piskoti:"biscuits",piskot:"biscuit",torta:"cake",pica:"pizza",solata:"salad",solato:"salad",paradiznik:"tomato",korenje:"carrot",brokoli:"broccoli",spinaca:"spinach",fizol:"beans",leca:"lentils",cicerika:"chickpeas",orehi:"walnuts",mandlji:"almonds","arasidovo maslo":"peanut butter",olje:"olive oil","olivno olje":"olive oil",sunka:"ham",prsut:"ham",klobasa:"sausage",gel:"energy gel",ploscica:"energy bar","sportni napitek":"sports drink",rogljic:"croissant",kosmice:"breakfast cereal",musli:"muesli",granola:"granola",avokado:"avocado",datlji:"dates",rozine:"raisins","rizevi vaflji":"rice cakes",sendvic:"sandwich",juha:"soup",juho:"soup",zrezek:"beef steak",puran:"turkey",tofu:"tofu",humus:"hummus",sadje:"fruit",zelenjava:"vegetables",rezina:"",rezini:"",rezine:""},
sk:{chlieb:"bread",chleba:"bread",chleb:"bread",toast:"bread toasted",banan:"banana",banany:"banana",jablko:"apple",jablka:"apple",pomaranc:"orange",hruska:"pear",hrozno:"grapes",jahody:"strawberries",cucoriedky:"blueberries",vajce:"egg whole",vajcia:"egg whole",vajicko:"egg whole",mlieko:"milk",mlieka:"milk",jogurt:"yogurt",ovsene:"oats",vlocky:"oats","ovsene vlocky":"oats",kasa:"porridge",ryza:"rice",ryzu:"rice",cestoviny:"pasta",spagety:"spaghetti",zemiaky:"potato",zemiak:"potato",kura:"chicken breast",kuracie:"chicken breast",hovadzie:"beef",maso:"beef",ryba:"fish",losos:"salmon",tuniak:"tuna",syr:"cheese",maslo:"butter salted",maslom:"butter salted",med:"honey",medom:"honey",dzem:"jam","ovsenych vlociek":"oats",vlociek:"oats",mliekom:"milk",dzemom:"jam",kava:"coffee infusion",kavu:"coffee infusion",caj:"tea",voda:"water",vodu:"water",dzus:"juice","pomarancovy dzus":"orange juice",pivo:"beer",vino:"wine",cukor:"sugar",cokolada:"chocolate",cokoladu:"chocolate",kekse:"biscuits",suska:"biscuit",kolac:"cake",torta:"cake",pizza:"pizza",salat:"salad",paradajka:"tomato",paradajky:"tomato",mrkva:"carrot",brokolica:"broccoli",spenat:"spinach",fazula:"beans",sosovica:"lentils",cicer:"chickpeas",orechy:"walnuts",mandle:"almonds","arasidove maslo":"peanut butter",olej:"olive oil","olivovy olej":"olive oil",sunka:"ham",klobasa:"sausage",gel:"energy gel",tycinka:"energy bar","sportovy napoj":"sports drink",croissant:"croissant",rozok:"bread roll",cerealie:"breakfast cereal",musli:"muesli",granola:"granola",avokado:"avocado",datle:"dates",hrozienka:"raisins","ryzove chlebiky":"rice cakes",sendvic:"sandwich",polievka:"soup",steak:"beef steak",morka:"turkey",tofu:"tofu",hummus:"hummus",ovocie:"fruit",zelenina:"vegetables"}};
function vNum(w,L){if(/^\d+([.,]\d+)?$/.test(w)){return parseFloat(w.replace(",","."));}var m=w.match(/^(\d+)\/(\d+)$/);if(m){return (+m[1])/(+m[2]);}var t=VN[L]||VN.en;return t.hasOwnProperty(w)?t[w]:null;}
function vTrans(ws,L){var d=VD[L];if(!d){return ws.join(" ");}var whole=ws.join(" ");if(d.hasOwnProperty(whole)){return d[whole];}var out=[],i=0;
while(i<ws.length){if(i+2<ws.length&&d.hasOwnProperty(ws.slice(i,i+3).join(" "))){out.push(d[ws.slice(i,i+3).join(" ")]);i+=3;continue;}if(i+1<ws.length&&d.hasOwnProperty(ws[i]+" "+ws[i+1])){out.push(d[ws[i]+" "+ws[i+1]]);i+=2;continue;}out.push(d.hasOwnProperty(ws[i])?d[ws[i]]:ws[i]);i++;}
return out.filter(Boolean).join(" ");}
var FR={"½":0.5,"¼":0.25,"¾":0.75,"⅓":0.333,"⅔":0.667,"⅛":0.125};
var MULT=[[/^(kg|kilos?|kilograms?|chili|chilogrammi|quilos?|kilogramov)$/,1000,"g"],[/^(l|litres?|liters?|litri|litro|litros|litrov?)$/,1000,"g"],[/^(dl|decilitri)$/,100,"g"],[/^(cl|centilitri)$/,10,"g"]];
function prep(text){return String(text||"").replace(/[   \t]/g," ").replace(/(\d)\s*([½¼¾⅓⅔⅛])/g,function(m,a,b){return String(+a+FR[b]);}).replace(/[½¼¾⅓⅔⅛]/g,function(c){return String(FR[c]);}).replace(/(\d)([a-zA-Z])/g,"$1 $2");}
function one(ch,L){ch=ch.trim();if(!ch){return null;}var unit=null,mult=1;
var w0=ch.split(/\s+/);for(var k=0;k<w0.length;k++){for(var m=0;m<MULT.length;m++){if(MULT[m][0].test(w0[k])&&k>0&&vNum(w0[k-1],L)!=null){mult=MULT[m][1];unit="g";w0.splice(k,1);ch=w0.join(" ");break;}}if(unit){break;}}
if(!unit){for(var i=0;i<VU.length;i++){if(VU[i][1].test(ch)){unit=VU[i][0];ch=ch.replace(VU[i][1]," ");break;}}}
var ws=ch.split(/\s+/).filter(Boolean),q=null,rest=[];
ws.forEach(function(w){var n=vNum(w,L);if(n!=null&&q==null&&!(L==="en"&&(w==="a"||w==="an")&&rest.length)){q=n;return;}if(n!=null&&q!=null&&(w==="half"||w==="mezzo"||w==="mezza"||w==="meio"||w==="meia"||w==="pol")){q+=0.5;return;}if(n!=null&&q!=null&&rest.length===0&&w!=="a"&&w!=="an"){if(n<1){q+=n;}return;}if((VF[L]||[]).indexOf(w)>-1){return;}rest.push(w);});
if(!rest.length){return null;}if(q!=null){q=q*mult;}var word=rest.join(" ");return {word:word,query:vTrans(rest,L)||word,q:q,unit:unit};}
function chunks(text,L){L=VC[L]?L:"en";var t=norm(prep(text)).replace(/[’']/g," ").replace(/[.;!?:]+(?!\d)/g,",").replace(/(\d),(\d)/g,"$1.$2");
var cj=new RegExp("[ ](?:"+VC[L].join("|")+")[ ]","g");t=(" "+t+" ").replace(cj," , ");var o=[];t.split(",").forEach(function(ch){var r=one(ch,L);if(r){o.push(r);}});return o;}
function line(text,L){L=VC[L]?L:"en";var t=norm(prep(text)).replace(/[’']/g," ").replace(/\([^)]*\)/g," ").replace(/(\d),(\d)/g,"$1.$2").replace(/[,;:]+/g," ");return one(t,L);}
function porG(po,u){if(!po){return 0;}for(var i=0;i<po.length;i++){if(po[i][0]===u){return +po[i][1];}}return 0;}
function best(res,unit,porOf){if(unit&&unit!=="g"&&unit!=="tsp"&&unit!=="tbsp"&&res.length&&!(porG(porOf(res[0]),unit)>0)){for(var i=1;i<Math.min(res.length,8);i++){if(porG(porOf(res[i]),unit)>0){res.unshift(res.splice(i,1)[0]);break;}}}return res;}
function unitFor(po,q,unit){var GEN={tsp:5,tbsp:15};
if(unit==="g"){return {u:"g",q:q||100};}
if(unit&&porG(po,unit)>0){return {u:unit,q:q||1};}
if(unit&&GEN[unit]){return {u:"g",q:Math.round((q||1)*GEN[unit])};}
if(po&&po.length){var pref=["m","u","sl","pot","cup"],k=po[0][0];for(var i=0;i<pref.length;i++){if(porG(po,pref[i])>0){k=pref[i];break;}}return {u:k,q:q||1};}
return {u:"g",q:(q&&q>=20)?q:100};}
function lang(text){var t=norm(text);var sc={it:/\b(ingredienti|procedimento|preparazione|cucchiai|cucchiaio|porzioni|di|con|q\.?b\.?|grammi)\b/g,pt:/\b(ingredientes|preparacao|modo de preparo|colher|porcoes|de|com)\b/g,sl:/\b(sestavine|postopek|priprava|zlica|porcije|in|z)\b/g,sk:/\b(ingrediencie|postup|lyzica|porcie|a|so)\b/g},b="en",bn=(t.match(/\b(ingredients|method|tbsp|tsp|cup|serves|and|with|the|of)\b/g)||[]).length;
for(var k in sc){var n=(t.match(sc[k])||[]).length;if(n>bn){bn=n;b=k;}}return b;}
window.ccNpParse={norm:norm,chunks:chunks,line:line,porG:porG,best:best,unitFor:unitFor,lang:lang,num:vNum};
})();
JS;
    return '<script>' . str_replace(["\r", "\n"], ['', ' '], $js) . '</script>';
}
