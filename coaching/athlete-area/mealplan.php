<?php
if (!defined('ABSPATH')) return;
/* ---------- Meal plans (Matteo, 19 Nov 2026) ----------
 * Marine Lenehan (role cc_nutritionist) keeps a private recipe library and day templates (option cc_mp_lib: {r: recipes, t: templates};
 * hers, kept when athletes leave). On a package athlete's review page she plans days (post meta cc_mp_YYYY-MM-DD: {i: planned items, n: her
 * daily plan note, tr: the athlete's own "Today's training" line}). Every recipe she plans is copied to the athlete (post meta cc_mp_rec) so
 * "My recipes from Marine" keeps working if she later deletes it; athletes never see her library or anyone else's plan.
 * In the diary each planned item shows in its slot with three answers: ate it (logged exactly as planned), different (amount or one
 * swapped ingredient), didn't eat it (optional reason). Logged lines carry pl = the planned item's id, so a changed answer replaces them.
 * Macros always come from the CURRENT food tables (same rule as the diary). Athlete plan data is deleted when coaching ends. */

const CC_MP_TAGS = ['Breakfast', 'Pre-ride', 'On the bike', 'Recovery', 'Lunch', 'Dinner', 'Snacks', 'High carb', 'High protein', 'Low fibre', 'Vegetarian', 'Vegan', 'Gluten-free', 'Dairy-free', 'Quick', 'Batch cook', 'Race day'];
const CC_MP_WHY = ['time', 'hungry', 'out', 'other'];

function cc_mp_w($k) {
    static $W = [
        'from_m' => ['From Marine', 'Da Marine', 'Da Marine', 'Od Marine', 'Od Marine'],
        'por_x' => ['Portion: %s', 'Porzione: %s', 'Porção: %s', 'Porcija: %s', 'Porcia: %s'],
        'ate' => ['Ate it', 'Mangiato', 'Comi', 'Pojedeno', 'Zjedené'],
        'diff' => ['Different', 'Diverso', 'Diferente', 'Drugače', 'Inak'],
        'skip' => ['Didn’t eat it', 'Non mangiato', 'Não comi', 'Ni pojedeno', 'Nezjedené'],
        'done_y' => ['Eaten · in your diary', 'Mangiato · nel tuo diario', 'Comido · no teu diário', 'Pojedeno · v tvojem dnevniku', 'Zjedené · v tvojom denníku'],
        'done_d' => ['Logged your way', 'Registrato a modo tuo', 'Registado à tua maneira', 'Zapisano po tvoje', 'Zapísané po svojom'],
        'done_n' => ['Noted, thanks', 'Annotato, grazie', 'Anotado, obrigado', 'Zabeleženo, hvala', 'Zaznamenané, ďakujeme'],
        'change' => ['Change', 'Cambia', 'Alterar', 'Spremeni', 'Zmeniť'],
        'amount' => ['How much did you have?', 'Quanto ne hai mangiato?', 'Quanto comeste?', 'Koliko je bilo?', 'Koľko to bolo?'],
        'custom_g' => ['Grams', 'Grammi', 'Gramas', 'Grami', 'Gramy'],
        'swap' => ['Swap an ingredient', 'Sostituisci un ingrediente', 'Trocar um ingrediente', 'Zamenjaj sestavino', 'Vymeniť ingredienciu'],
        'swap_f' => ['Swap for something else', 'Sostituisci con altro', 'Trocar por outra coisa', 'Zamenjaj z nečim drugim', 'Vymeniť za niečo iné'],
        'swap_which' => ['Which ingredient?', 'Quale ingrediente?', 'Qual ingrediente?', 'Katero sestavino?', 'Ktorú ingredienciu?'],
        'swap_for' => ['Swap %s for:', 'Sostituisci %s con:', 'Trocar %s por:', 'Zamenjaj %s z:', 'Vymeniť %s za:'],
        'log_it' => ['Log it', 'Registra', 'Registar', 'Zapiši', 'Zapísať'],
        'why' => ['What happened? (optional)', 'Cosa è successo? (facoltativo)', 'O que aconteceu? (opcional)', 'Kaj se je zgodilo? (neobvezno)', 'Čo sa stalo? (nepovinné)'],
        'r_time' => ['No time', 'Niente tempo', 'Sem tempo', 'Ni bilo časa', 'Nebol čas'],
        'r_hungry' => ['Not hungry', 'Niente fame', 'Sem fome', 'Brez apetita', 'Bez chuti do jedla'],
        'r_out' => ['Ate out', 'Mangiato fuori', 'Comi fora', 'Obrok zunaj', 'Jedlo vonku'],
        'r_other' => ['Other', 'Altro', 'Outro', 'Drugo', 'Iné'],
        'instead' => ['Log what I had instead', 'Registra cosa ho mangiato invece', 'Registar o que comi em vez disso', 'Zapiši, kaj je bilo namesto tega', 'Zapísať, čo bolo namiesto toho'],
        'myrec' => ['My recipes from Marine', 'Le mie ricette da Marine', 'As minhas receitas da Marine', 'Moji recepti od Marine', 'Moje recepty od Marine'],
        'myrec_l' => ['Every recipe Marine planned for you. Open one any time.', 'Tutte le ricette che Marine ha pianificato per te. Aprile quando vuoi.', 'Todas as receitas que a Marine planeou para ti. Abre-as quando quiseres.', 'Vsi recepti, ki jih je Marine načrtovala zate. Odpri jih kadar koli.', 'Všetky recepty, ktoré ti Marine naplánovala. Otvor si ich kedykoľvek.'],
        'per_portion' => ['Per portion', 'Per porzione', 'Por porção', 'Na porcijo', 'Na porciu'],
        'your_portion' => ['Your portion: %s', 'La tua porzione: %s', 'A tua porção: %s', 'Tvoja porcija: %s', 'Tvoja porcia: %s'],
        'method' => ['Method', 'Preparazione', 'Preparação', 'Priprava', 'Postup'],
        'makes' => ['Portions in the whole recipe: %s', 'Porzioni nella ricetta intera: %s', 'Porções na receita inteira: %s', 'Porcije v celem receptu: %s', 'Porcie v celom recepte: %s'],
        'close' => ['Close', 'Chiudi', 'Fechar', 'Zapri', 'Zavrieť'],
        'plan_today' => ['Marine’s plan for today', 'Il piano di Marine per oggi', 'O plano da Marine para hoje', 'Marinin načrt za danes', 'Plán od Marine na dnes'],
        'plan_day' => ['Marine’s plan for this day', 'Il piano di Marine per questo giorno', 'O plano da Marine para este dia', 'Marinin načrt za ta dan', 'Plán od Marine na tento deň'],
        'training' => ['Today’s training (optional)', 'Allenamento di oggi (facoltativo)', 'Treino de hoje (opcional)', 'Današnji trening (neobvezno)', 'Dnešný tréning (nepovinné)'],
        'training_d' => ['Training this day (optional)', 'Allenamento di questo giorno (facoltativo)', 'Treino deste dia (opcional)', 'Trening ta dan (neobvezno)', 'Tréning v tento deň (nepovinné)'],
        'training_ph' => ['e.g. 2h endurance, rest', 'es. 2h fondo, riposo', 'p. ex. 2h resistência, descanso', 'npr. 2 h vzdržljivost, počitek', 'napr. 2 h vytrvalosť, voľno'],
        'na' => ['This recipe isn’t available on your page. If you think it should be, write to Marine under any day of your food diary.', 'Questa ricetta non è disponibile nella tua pagina. Se pensi che dovrebbe esserci, scrivi a Marine sotto un giorno qualsiasi del tuo diario alimentare.', 'Esta receita não está disponível na tua página. Se achas que devia estar, escreve à Marine em qualquer dia do teu diário alimentar.', 'Ta recept ni na voljo na tvoji strani. Če misliš, da bi moral biti, piši Marine pod katerim koli dnem v prehranskem dnevniku.', 'Tento recept nie je na tvojej stránke dostupný. Ak si myslíš, že by mal byť, napíš Marine pod ktorýkoľvek deň v stravovacom denníku.'],
        'open_r' => ['Open recipe', 'Apri la ricetta', 'Abrir receita', 'Odpri recept', 'Otvoriť recept'],
    ];
    static $I = ['en' => 0, 'it' => 1, 'pt' => 2, 'sl' => 3, 'sk' => 4];
    $l = $GLOBALS['cc_ath_lang'] ?? 'en';
    return $W[$k][$I[$l] ?? 0] ?? $W[$k][0];
}

/* ---------- data ---------- */
function cc_mp_lib() { $a = json_decode((string) get_option('cc_mp_lib', ''), true); return ['r' => array_values(array_filter((array) ($a['r'] ?? []), 'is_array')), 't' => array_values(array_filter((array) ($a['t'] ?? []), 'is_array'))]; }
function cc_mp_lib_put($l) { update_option('cc_mp_lib', wp_json_encode(['r' => array_values($l['r']), 't' => array_values($l['t'])]), false); }
function cc_mp_newid($p) { return $p . strtolower(wp_generate_password(10, false)); }
function cc_mp_rid($v) { $v = (string) $v; return preg_match('/^[RT][A-Za-z0-9]{3,24}$/', $v) ? $v : ''; }
function cc_mp_uid($v) { $v = (string) $v; return preg_match('/^[a-z0-9]{4,20}$/', $v) ? $v : ''; }
function cc_mp_lib_idx() { static $ix = null; if ($ix === null) { $ix = []; foreach (cc_mp_lib()['r'] as $r) $ix[$r['id']] = $r; } return $ix; }
function cc_mp_recs($pid) { $a = json_decode((string) get_post_meta((int) $pid, 'cc_mp_rec', true), true); return is_array($a) ? $a : []; }
/* the recipe as the athlete gets it: the library version while it exists (Marine's edits show), else the copy made when she planned it */
function cc_mp_rec_for($pid, $rid) { $ix = cc_mp_lib_idx(); if (isset($ix[$rid])) return $ix[$rid]; $c = cc_mp_recs($pid); return $c[$rid] ?? null; }

/* per portion, from the current food table (by id) and the micronutrient table for iron */
function cc_mp_calc($r) {
    static $cache = []; $key = md5(wp_json_encode([$r['ing'] ?? [], $r['por'] ?? 1])); if (isset($cache[$key])) return $cache[$key];
    $por = max(1, (int) ($r['por'] ?? 1)); $t = ['k' => 0, 'c' => 0, 'p' => 0, 'f' => 0, 'fi' => 0, 'su' => 0]; $fe = 0; $fem = 0; $g = 0;
    foreach ((array) ($r['ing'] ?? []) as $i) {
        $i = cc_fd_fresh_item($i, []); $gr = (float) ($i['g'] ?? 0); if ($gr <= 0) continue; $g += $gr;
        foreach ($t as $f => $_) $t[$f] += (float) ($i[$f] ?? 0) * $gr / 100;
        $v = cc_fd_fe100((string) ($i['id'] ?? ''), []); if ($v === null) $fem += $gr; else $fe += $v * $gr / 100;
    }
    $o = []; foreach ($t as $f => $v) $o[$f] = round($v / $por, 1);
    $o['fe'] = round($fe / $por, 1); $o['fei'] = ($g > 0 && $fem / $g > 0.3) ? 1 : 0; $o['w'] = round($g / $por);
    return $cache[$key] = $o;
}
function cc_mp_photo_url($id) { return $id ? (string) wp_get_attachment_url((int) $id) : ''; }
function cc_mp_rec_out($r) {
    $r['mac'] = cc_mp_calc($r); $r['phu'] = cc_mp_photo_url($r['ph'] ?? 0);
    foreach ((array) ($r['ing'] ?? []) as $x => $i) $r['ing'][$x] = cc_fd_fresh_item($i, []);
    return $r;
}
function cc_mp_lib_out() { $l = cc_mp_lib(); return ['r' => array_map('cc_mp_rec_out', $l['r']), 't' => $l['t']]; }
function cc_mp_clean_rec($in) {
    if (!is_array($in)) return null;
    $o = ['id' => cc_mp_rid($in['id'] ?? '') ?: cc_mp_newid('R'), 'n' => cc_fd_txt($in['n'] ?? '', 120), 'tags' => [], 'ing' => [],
          'm' => mb_substr(trim(sanitize_textarea_field((string) ($in['m'] ?? ''))), 0, 6000), 'por' => max(1, min(50, (int) ($in['por'] ?? 1))), 'ph' => (int) ($in['ph'] ?? 0), 'u' => time()];
    foreach ((array) ($in['tags'] ?? []) as $t) if (in_array($t, CC_MP_TAGS, true) && !in_array($t, $o['tags'], true)) $o['tags'][] = $t;
    foreach (array_slice((array) ($in['ing'] ?? []), 0, 40) as $i) { $c = cc_fd_item($i); if ($c && $c['g'] > 0) { unset($c['m']); $o['ing'][] = $c; } }
    if ($o['ph'] && !get_post_meta($o['ph'], 'cc_mp_photo', true)) $o['ph'] = 0;
    return ($o['n'] === '' || !$o['ing']) ? null : $o;
}
/* one planned entry: a recipe with a portion multiplier, or one food in grams */
function cc_mp_clean_entry($e) {
    if (!is_array($e)) return null;
    if (($e['k'] ?? '') === 'r') { $rid = cc_mp_rid($e['rid'] ?? ''); if (!$rid) return null; return ['k' => 'r', 'rid' => $rid, 'x' => round(min(10, max(0.1, (float) str_replace(',', '.', (string) ($e['x'] ?? 1)))), 2)]; }
    $f = cc_fd_item($e['f'] ?? null); if (!$f || $f['g'] <= 0) return null; unset($f['m'], $f['pl']);
    return ['k' => 'f', 'f' => $f];
}
function cc_mp_clean_tpl($in) {
    if (!is_array($in)) return null;
    $o = ['id' => cc_mp_rid($in['id'] ?? '') ?: cc_mp_newid('T'), 'n' => cc_fd_txt($in['n'] ?? '', 120), 's' => []];
    foreach (CC_FD_SLOTS as $k) { $a = []; foreach (array_slice((array) ($in['s'][$k] ?? []), 0, 12) as $e) { $c = cc_mp_clean_entry($e); if ($c) $a[] = $c; } if ($a) $o['s'][$k] = $a; }
    return $o['n'] === '' ? null : $o;
}
function cc_mp_get($pid, $d) {
    $a = json_decode((string) get_post_meta((int) $pid, 'cc_mp_' . $d, true), true);
    return is_array($a) ? ['i' => array_values(array_filter((array) ($a['i'] ?? []), 'is_array')), 'n' => (string) ($a['n'] ?? ''), 'tr' => (string) ($a['tr'] ?? '')] : ['i' => [], 'n' => '', 'tr' => ''];
}
function cc_mp_put($pid, $d, $a) {
    if (!$a['i'] && $a['n'] === '' && $a['tr'] === '') delete_post_meta((int) $pid, 'cc_mp_' . $d);
    else update_post_meta((int) $pid, 'cc_mp_' . $d, wp_slash(wp_json_encode(['i' => array_values($a['i']), 'n' => $a['n'], 'tr' => $a['tr']])));
}
/* planned macros of one item (the portion she planned) */
function cc_mp_item_mac($pid, $it) {
    $o = ['k' => 0, 'c' => 0, 'p' => 0, 'f' => 0, 'fi' => 0, 'fe' => 0];
    if (($it['k'] ?? '') === 'r') { $r = cc_mp_rec_for($pid, $it['rid'] ?? ''); if (!$r) return $o; $m = cc_mp_calc($r); $x = (float) ($it['x'] ?? 1); foreach ($o as $f => $_) $o[$f] = (float) ($m[$f] ?? 0) * $x; return $o; }
    $f = cc_fd_fresh_item((array) ($it['f'] ?? []), []); $g = (float) ($f['g'] ?? 0) / 100;
    foreach (['k', 'c', 'p', 'f', 'fi'] as $k) $o[$k] = (float) ($f[$k] ?? 0) * $g;
    $v = cc_fd_fe100((string) ($f['id'] ?? ''), []); $o['fe'] = $v === null ? 0 : $v * $g;
    return $o;
}
function cc_mp_round($m) { if (!$m) return null; $o = []; foreach ($m as $k => $v) $o[$k] = round((float) $v, 1); return $o; }
/* what the athlete logged for one planned item (diary lines carrying its id), from the current tables; null when nothing */
function cc_mp_eaten($day, $u) {
    $a = []; foreach ((array) ($day['s'] ?? []) as $s) foreach ((array) ($s['i'] ?? []) as $it) if (($it['pl'] ?? '') === $u) $a[] = $it;
    if (!$a) return null; $t = cc_fd_tot($a); return ['k' => $t['k'], 'c' => $t['c'], 'p' => $t['p'], 'f' => $t['f']];
}
/* the diary lines an answer logs: the planned portion (or the athlete's amount), one ingredient possibly swapped */
function cc_mp_lines($pid, $it, $a) {
    $out = []; $s = $a['s'] ?? ''; if ($s !== 'y' && $s !== 'd') return [];
    $mk = function ($src, $g) use ($it) { $l = cc_fd_fresh_item($src, []); unset($l['m']); $l['g'] = round($g, 1); $l['pl'] = $it['u']; return $l; };
    if (($it['k'] ?? '') === 'r') {
        $r = cc_mp_rec_for($pid, $it['rid'] ?? ''); if (!$r) return [];
        $por = max(1, (int) ($r['por'] ?? 1)); $x = (float) ($it['x'] ?? 1); $fac = 1;
        if ($s === 'd') { if (!empty($a['g'])) { $w = (float) cc_mp_calc($r)['w'] * $x; $fac = $w > 0 ? (float) $a['g'] / $w : 1; } else $fac = (float) ($a['x'] ?? 1); }
        foreach ((array) $r['ing'] as $ix => $i) {
            $g = (float) ($i['g'] ?? 0) / $por * $x * $fac; if ($g <= 0) continue;
            $src = ($s === 'd' && !empty($a['sw']) && (int) $a['sw']['i'] === (int) $ix) ? $a['sw']['f'] : $i;
            $out[] = $mk($src, $g);
        }
        return $out;
    }
    $f = (array) ($it['f'] ?? []); $g = (float) ($f['g'] ?? 0);
    if ($s === 'd') { $g = !empty($a['g']) ? (float) $a['g'] : $g * (float) ($a['x'] ?? 1); if (!empty($a['sw'])) $f = $a['sw']['f']; }
    return $g > 0 ? [$mk($f, $g)] : [];
}
function cc_mp_days($pid) { $o = []; foreach (array_keys((array) get_post_meta((int) $pid)) as $k) if (preg_match('/^cc_mp_(\d{4}-\d{2}-\d{2})$/', $k, $m)) $o[] = $m[1]; rsort($o); return $o; }

/* ---------- what the athlete gets ---------- */
function cc_mp_rec_ath($r) {
    $m = cc_mp_calc($r); $ing = [];
    foreach ((array) $r['ing'] as $i) $ing[] = ['n' => (string) $i['n'], 'g' => (float) $i['g'], 'st' => (string) ($i['st'] ?? '')];
    return ['id' => $r['id'], 'n' => $r['n'], 'phu' => cc_mp_photo_url($r['ph'] ?? 0), 'ing' => $ing, 'm' => (string) ($r['m'] ?? ''), 'por' => max(1, (int) ($r['por'] ?? 1)),
            'mac' => ['k' => $m['k'], 'c' => $m['c'], 'p' => $m['p'], 'f' => $m['f'], 'fi' => $m['fi']], 'w' => $m['w']];
}
function cc_mp_ath_day($pid, $d) {
    $pl = cc_mp_get($pid, $d); $items = []; $recs = [];
    foreach ($pl['i'] as $it) {
        $o = ['u' => $it['u'], 'sl' => $it['sl'], 'k' => $it['k'], 'a' => $it['a'] ?? null, 'pm' => cc_mp_round(cc_mp_item_mac($pid, $it))];
        if ($it['k'] === 'r') { $r = cc_mp_rec_for($pid, $it['rid']); if (!$r) continue; $o['rid'] = $it['rid']; $o['x'] = (float) $it['x']; $recs[$it['rid']] = cc_mp_rec_ath($r); }
        else $o['f'] = cc_fd_fresh_item($it['f'], []);
        $items[] = $o;
    }
    return ['plan' => ['d' => $d, 'i' => $items, 'n' => $pl['n'], 'tr' => $pl['tr']], 'recs' => (object) $recs];
}
function cc_mp_ath_recs($pid) { $o = []; foreach (cc_mp_recs($pid) as $rid => $c) { $r = cc_mp_rec_for($pid, $rid); if ($r) $o[$rid] = cc_mp_rec_ath($r); } return $o; }

/* the athlete's diary: planned items, the note, the training line and "My recipes from Marine" (food.php calls this filter after the diary) */
add_filter('cc_fd_after_app', function ($html, $pid, $date) {
    $W = []; foreach (['from_m', 'por_x', 'ate', 'diff', 'skip', 'done_y', 'done_d', 'done_n', 'change', 'amount', 'custom_g', 'swap', 'swap_f', 'swap_which', 'swap_for', 'log_it', 'why', 'r_time', 'r_hungry', 'r_out', 'r_other',
                       'instead', 'myrec', 'myrec_l', 'per_portion', 'your_portion', 'method', 'makes', 'close', 'plan_today', 'plan_day', 'training', 'training_d', 'training_ph', 'open_r'] as $k) $W[$k] = cc_mp_w($k);
    foreach (['save', 'cancel', 'saved', 'err', 'carbs', 'protein', 'fat', 'fibre', 'ingredients', 'search', 'loading', 'noresults', 'closest', 'ask_rc', 'w_raw', 'w_cooked', 'grams', 'addit', 'b_raw', 'b_cooked', 'c_ab', 'p_ab', 'f_ab'] as $k) $W[$k] = cc_fd_w($k);
    $today = current_time('Y-m-d'); $d1 = cc_mp_ath_day($pid, $date); $recs = cc_mp_ath_recs($pid);
    foreach ((array) $d1['recs'] as $k => $v) $recs[$k] = $v;
    $days = [$d1['plan']]; if ($date !== $today) { $d2 = cc_mp_ath_day($pid, $today); $days[] = $d2['plan']; foreach ((array) $d2['recs'] as $k => $v) $recs[$k] = $v; }
    $open = ''; $rq = cc_mp_rid($_GET['mpr'] ?? ''); if ($rq && isset($recs[$rq])) $open = $rq;
    $vx = cc_ath_tp($pid) ? [] : cc_fd_vx($pid);
    $cfg = ['page' => (int) $pid, 'today' => $today, 'lang' => $GLOBALS['cc_ath_lang'] ?? 'en', 'nonce' => wp_create_nonce('wp_rest'), 'w' => $W, 'days' => $days, 'recs' => (object) $recs, 'open' => $open,
            'trf' => (cc_ath_tp($pid) || !$vx) ? 1 : 0, 'foods' => esc_url_raw(add_query_arg('v', get_option('cc_food_db_v', '0'), rest_url('cc/v1/foods'))),
            'u' => ['day' => esc_url_raw(rest_url('cc/v1/mp-day')), 'ans' => esc_url_raw(rest_url('cc/v1/mp-answer')), 'tr' => esc_url_raw(rest_url('cc/v1/mp-tr'))]];
    return $html . '<div class="mp-acfg" hidden data-cfg="' . esc_attr(wp_json_encode($cfg)) . '"></div>' . cc_mp_css() . cc_mp_search_js() . cc_mp_ajs();
}, 10, 3);
/* a recipe link (?mpr=) that is not this athlete's: a polite line, nothing else */
add_filter('cc_ath_after_reports', function ($html, $view, $coach) {
    $rq = cc_mp_rid($_GET['mpr'] ?? ''); if (!$rq || $coach || !$view) return $html;
    if (cc_fd_on($view) && isset(cc_mp_recs($view)[$rq])) return $html;
    return $html . '<section class="ath-s mp-nas"><p class="fd-lede" role="status">' . esc_html(cc_mp_w('na')) . '</p></section>';
}, 17, 3);
/* recipe photos: Marine and Matteo; an athlete only for a recipe planned for them */
add_filter('cc_ath_file_ok', function ($ok, $id) {
    if ($ok || !get_post_meta($id, 'cc_mp_photo', true)) return $ok;
    if (cc_fd_staff()) return true;
    $p = cc_ath_page_of(get_current_user_id()); if (!$p || !cc_fd_on($p)) return false;
    foreach (array_keys(cc_mp_recs($p)) as $rid) { $r = cc_mp_rec_for($p, $rid); if ($r && (int) ($r['ph'] ?? 0) === (int) $id) return true; $c = cc_mp_recs($p)[$rid] ?? []; if ((int) ($c['ph'] ?? 0) === (int) $id) return true; }
    return false;
}, 12, 2);

/* ---------- Marine's and Matteo's screens (English) ---------- */
function cc_mp_lib_page($viewer) {
    $GLOBALS['cc_ath_lang'] = 'en';
    $slots = []; foreach (CC_FD_SLOTS as $k) $slots[] = [$k, cc_fd_w($k)];
    $cfg = ['lib' => cc_mp_lib_out(), 'tags' => CC_MP_TAGS, 'slots' => $slots, 'nonce' => wp_create_nonce('wp_rest'),
            'foods' => esc_url_raw(add_query_arg('v', get_option('cc_food_db_v', '0'), rest_url('cc/v1/foods'))), 'micro' => cc_fd_micro_url(),
            'u' => ['lib' => esc_url_raw(rest_url('cc/v1/mp-lib')), 'photo' => esc_url_raw(rest_url('cc/v1/mp-photo'))]];
    $back = $viewer === 'nutri' ? cc_fd_hub() : add_query_arg('board', 'food', cc_fd_hub());
    return '<section class="ath-s fd-rv mp" id="mp-lib"><p class="fd-back"><a href="' . esc_url($back) . '">← ' . ($viewer === 'nutri' ? 'Home' : 'Food diaries') . '</a></p>'
        . '<h2>' . cc_ath_icon('food', 'ath-hic') . 'Recipes &amp; meal plans</h2>'
        . '<p class="fd-lede">Your recipe library and day templates. Only you and Matteo see this library; athletes only see the recipes you plan for them, on the days you plan them (and later under “My recipes from Marine”). Plan days on each athlete’s food diary page.</p>'
        . '<div class="mp-lib" data-cfg="' . esc_attr(wp_json_encode($cfg)) . '"></div></section>' . cc_fd_css() . cc_mp_css() . cc_mp_search_js() . cc_mp_sjs();
}
add_filter('cc_ath_nutritionist', function ($html, $me) {
    if (!user_can($me, 'cc_nutrition')) return $html;
    if (isset($_GET['mp'])) return cc_mp_lib_page('nutri');
    if (!empty($_GET['food'])) return $html;
    $l = cc_mp_lib();
    $card = '<section class="ath-s mp mp-home" id="meal-plans"><h2>' . cc_ath_icon('food', 'ath-hic') . 'Recipes &amp; meal plans</h2>'
        . '<p class="fd-lede">' . count($l['r']) . ' recipe' . (count($l['r']) === 1 ? '' : 's') . ' · ' . count($l['t']) . ' day template' . (count($l['t']) === 1 ? '' : 's') . '. Build recipes and day templates here, then plan them on an athlete’s food diary page.</p>'
        . '<p><a class="btn btn-go" href="' . esc_url(add_query_arg('mp', 'lib', cc_fd_hub())) . '">Open recipes &amp; meal plans</a></p></section>';
    $pos = strpos($html, '<section class="ath-s fd-rv" id="food-diaries">');
    return $pos === false ? $html . $card . cc_mp_css() : substr_replace($html, $card, $pos, 0) . cc_mp_css();
}, 21, 2);
add_filter('cc_ath_coach_links', function ($html) { return $html . '<a class="av-boardlink" href="' . esc_url(add_query_arg('board', 'mealplans', cc_fd_hub())) . '">Meal plans</a>'; }, 22);
add_filter('cc_ath_board', function ($html, $board) { return ($board === 'mealplans' && cc_ath_is_coach()) ? cc_mp_lib_page('coach') : $html; }, 10, 2);

/* training lines for a day: Vekta (done, else planned) or the athlete's own line (TrainingPeaks / no Vekta) */
function cc_mp_train_html($vx, $tp, $d, $tr) {
    $o = [];
    if (!$tp && $vx) {
        $done = cc_fd_vx_day($vx, $d, 'done');
        foreach ($done as $a) $o[] = '✓ ' . esc_html($a['n'] ?: 'Session') . ($a['min'] ? ' · ' . esc_html(cc_fd_hm($a['min'] * 60)) : '');
        if (!$done) foreach (cc_fd_vx_day($vx, $d, 'plan') as $p) $o[] = 'Planned: ' . cc_fd_plan_line($p);
    }
    if ($tr !== '') $o[] = 'Athlete: “' . esc_html($tr) . '”';
    if (!$o) $o[] = '<span class="fd-muted">' . ($tp || !$vx ? 'No training line from the athlete' : 'Rest / nothing planned') . '</span>';
    return $o;
}
function cc_mp_staff_day($pid, $d, $vx, $tp) {
    $pl = cc_mp_get($pid, $d); $day = cc_fd_get($pid, $d); $items = [];
    foreach ($pl['i'] as $it) {
        $o = $it; $o['pm'] = cc_mp_round(cc_mp_item_mac($pid, $it)); $o['em'] = cc_mp_round(cc_mp_eaten($day, $it['u']));
        if ($it['k'] === 'r') { $r = cc_mp_rec_for($pid, $it['rid']); $o['rn'] = $r ? $r['n'] : 'Recipe'; $o['phu'] = $r ? cc_mp_photo_url($r['ph'] ?? 0) : ''; }
        else $o['f'] = cc_fd_fresh_item($it['f'], []);
        $items[] = $o;
    }
    $ts = strtotime($d . ' 12:00');
    return ['d' => $d, 'lbl' => date_i18n('D j M', $ts), 'dow' => date_i18n('D', $ts), 'i' => $items, 'n' => $pl['n'], 'tr' => $pl['tr'], 'train' => cc_mp_train_html($vx, $tp, $d, $pl['tr'])];
}
/* the 7 days ending $end: meals followed, share of planned carbs eaten, and where it breaks down */
function cc_mp_week_stats($pid, $end) {
    $Y = 0; $X = 0; $pc = 0; $ec = 0; $skip = []; $na = []; $t0 = strtotime($end . ' 12:00');
    for ($i = 0; $i < 7; $i++) {
        $d = gmdate('Y-m-d', $t0 - $i * DAY_IN_SECONDS); $pl = cc_mp_get($pid, $d); if (!$pl['i']) continue; $day = cc_fd_get($pid, $d);
        foreach ($pl['i'] as $it) {
            $Y++; $s = $it['a']['s'] ?? ''; if ($s === 'y' || $s === 'd') $X++;
            $pc += cc_mp_item_mac($pid, $it)['c']; $e = cc_mp_eaten($day, $it['u']); $ec += $e ? $e['c'] : 0;
            if ($s === 'n') $skip[$it['sl']][$d] = 1; elseif ($s === '' && $d < $end) $na[$it['sl']][$d] = 1;
        }
    }
    $h = [];
    foreach (CC_FD_SLOTS as $k) {
        if (count($skip[$k] ?? []) >= 2) $h[] = cc_fd_w($k) . ' skipped on ' . count($skip[$k]) . ' days';
        if (count($na[$k] ?? []) >= 2) $h[] = cc_fd_w($k) . ' not answered on ' . count($na[$k]) . ' days';
    }
    return ['Y' => $Y, 'X' => $X, 'pc' => $pc, 'ec' => $ec, 'hints' => $h];
}
function cc_mp_week_html($pid) {
    $GLOBALS['cc_ath_lang'] = 'en'; $s = cc_mp_week_stats($pid, current_time('Y-m-d'));
    if (!$s['Y']) return '<p class="fd-muted mp-wl">Last 7 days: no meals planned yet.</p>';
    return '<p class="mp-wl">Last 7 days · Meal plan followed: <b>' . $s['X'] . ' of ' . $s['Y'] . ' meals</b> · <b>' . ($s['pc'] > 0 ? round($s['ec'] / $s['pc'] * 100) : 0) . ' %</b> of planned carbs eaten</p>'
        . ($s['hints'] ? '<p class="mp-hint">Where it breaks down: ' . esc_html(implode(' · ', $s['hints'])) . '</p>' : '');
}
/* the planning section on the athlete's review page (food.php calls this filter) */
add_filter('cc_fd_review_plan', function ($html, $pid, $viewer) {
    if (!cc_fd_on($pid)) return $html;
    $start = cc_fd_date($_GET['mpd'] ?? '') ?: current_time('Y-m-d');
    $tp = cc_ath_tp($pid); $vx = $tp ? [] : cc_fd_vx($pid); $kg = cc_fd_kgv($pid)['kg'];
    $days = []; $t0 = strtotime($start . ' 12:00'); for ($i = 0; $i < 7; $i++) $days[] = cc_mp_staff_day($pid, gmdate('Y-m-d', $t0 + $i * DAY_IN_SECONDS), $vx, $tp);
    $lib = cc_mp_lib_out(); $rs = [];
    foreach ($lib['r'] as $r) $rs[] = ['id' => $r['id'], 'n' => $r['n'], 'tags' => $r['tags'], 'mac' => $r['mac'], 'phu' => $r['phu']];
    $slots = []; foreach (CC_FD_SLOTS as $k) $slots[] = [$k, cc_fd_w($k)];
    $cfg = ['page' => (int) $pid, 'kg' => $kg, 'today' => current_time('Y-m-d'), 'r' => $rs, 't' => $lib['t'], 'days' => $days, 'slots' => $slots, 'nonce' => wp_create_nonce('wp_rest'),
            'first' => strtok(trim((string) get_the_title($pid)), ' ') ?: 'the athlete', 'link' => cc_fd_hub(),
            'foods' => esc_url_raw(add_query_arg('v', get_option('cc_food_db_v', '0'), rest_url('cc/v1/foods'))), 'micro' => cc_fd_micro_url(),
            'u' => ['plan' => esc_url_raw(rest_url('cc/v1/mp-plan'))]];
    $keep = ''; foreach (['food', 'board', 'ath'] as $q) if (isset($_GET[$q])) $keep .= '<input type="hidden" name="' . $q . '" value="' . esc_attr(sanitize_key($_GET[$q])) . '">';
    $sh = function ($n) use ($t0) { return esc_url(add_query_arg('mpd', gmdate('Y-m-d', $t0 + $n * DAY_IN_SECONDS)) . '#mp-plan'); };
    $lib_url = $viewer === 'nutri' ? add_query_arg('mp', 'lib', cc_fd_hub()) : add_query_arg('board', 'mealplans', cc_fd_hub());
    return $html . '<div class="mp mp-plan-s" id="mp-plan"><h3>Meal plan</h3>'
        . '<p class="fd-lede">Drag a recipe onto a meal, or a day template onto a day. On a phone: tap a recipe or template, then tap “Add to …”. The athlete sees each planned item in that meal of their diary and answers ✓ / ✎ / ✗; your nutrition plan text shows at the top of their day. Carbs per kg are shown to you only. <a href="' . esc_url($lib_url) . '">Edit recipes and templates</a></p>'
        . cc_mp_week_html($pid)
        . '<div class="mp-wnav"><a class="btn btn-ghost" href="' . $sh(-7) . '">← Earlier</a><form method="get" action="#mp-plan" class="mp-jump">' . $keep . '<label>Start from <input type="date" name="mpd" value="' . esc_attr($start) . '"></label><button type="submit" class="btn btn-ghost">Show</button></form><a class="btn btn-ghost" href="' . $sh(7) . '">Later →</a></div>'
        . '<div class="mp-plan" data-cfg="' . esc_attr(wp_json_encode($cfg)) . '"></div></div>' . cc_mp_css() . cc_mp_search_js() . cc_mp_sjs();
}, 10, 3);
/* under each day of the review: planned vs eaten, item by item */
add_filter('cc_fd_review_day_extra', function ($html, $pid, $date, $viewer) {
    if (!cc_fd_on($pid)) return $html;
    $pl = cc_mp_get($pid, $date); if (!$pl['i'] && $pl['n'] === '' && $pl['tr'] === '') return $html;
    $day = cc_fd_get($pid, $date); $past = $date <= current_time('Y-m-d'); $li = ''; $pt = ['k' => 0, 'c' => 0]; $et = ['k' => 0, 'c' => 0];
    $why = ['time' => 'no time', 'hungry' => 'not hungry', 'out' => 'ate out', 'other' => 'other'];
    foreach ($pl['i'] as $it) {
        $m = cc_mp_item_mac($pid, $it); $e = cc_mp_eaten($day, $it['u']); $a = $it['a'] ?? []; $s = $a['s'] ?? '';
        $pt['k'] += $m['k']; $pt['c'] += $m['c']; if ($e) { $et['k'] += $e['k']; $et['c'] += $e['c']; }
        if ($it['k'] === 'r') { $r = cc_mp_rec_for($pid, $it['rid']); $nm = ($r ? $r['n'] : 'Recipe') . ' × ' . cc_fd_f1($it['x']); } else $nm = $it['f']['n'] . ' · ' . cc_fd_f1($it['f']['g']) . ' g';
        $st = $s === 'y' ? ['y', '✓', 'Ate it'] : ($s === 'd' ? ['d', '✎', 'Different' . (!empty($a['g']) ? ' (' . cc_fd_f1($a['g']) . ' g)' : (!empty($a['x']) ? ' (' . cc_fd_f1($a['x']) . '×)' : '')) . (!empty($a['sw']['f']['n']) ? ' · swapped in ' . $a['sw']['f']['n'] : '')]
            : ($s === 'n' ? ['n', '✗', 'Didn’t eat it' . (!empty($a['why']) ? ' (' . ($why[$a['why']] ?? '') . ')' : '')] : ['o', '○', $past ? 'Not answered' : 'Planned']));
        $li .= '<li class="mp-a-' . $st[0] . '"><span class="mp-ic" aria-hidden="true">' . $st[1] . '</span><span><b>' . esc_html(cc_fd_w($it['sl']) . ' · ' . $nm) . '</b><small>' . esc_html($st[2]) . ' · planned ' . round($m['k']) . ' kcal, C ' . round($m['c']) . ' g'
            . ($e ? ' · eaten ' . round($e['k']) . ' kcal, C ' . round($e['c']) . ' g' : '') . '</small></span></li>';
    }
    return $html . '<div class="mp mp-adh"><h4>Meal plan</h4>'
        . ($pl['n'] !== '' ? '<p class="mp-adn"><b>Your plan:</b> ' . nl2br(esc_html($pl['n'])) . '</p>' : '')
        . ($pl['tr'] !== '' ? '<p class="mp-adn"><b>Athlete’s training:</b> ' . esc_html($pl['tr']) . '</p>' : '')
        . ($li ? '<ul class="mp-al">' . $li . '</ul><p class="mp-adt">Planned <b>' . number_format(round($pt['k'])) . ' kcal · C ' . round($pt['c']) . ' g</b> · eaten from the plan <b>' . number_format(round($et['k'])) . ' kcal · C ' . round($et['c']) . ' g</b></p>' : '') . '</div>';
}, 10, 4);

/* ---------- REST ---------- */
add_action('rest_api_init', function () {
    $own = function (WP_REST_Request $r) {   // the athlete's own page with the package (Matteo may act on any page, e.g. his demo page)
        if (cc_ath_is_coach()) return true;
        $p = cc_ath_page_of(get_current_user_id());
        return $p && (int) ($r->get_param('page') ?: $p) === $p && cc_fd_on($p);
    };
    $page = function (WP_REST_Request $r) { return cc_ath_is_coach() ? (int) $r->get_param('page') : cc_ath_page_of(get_current_user_id()); };
    register_rest_route('cc/v1', '/mp-lib', ['methods' => 'GET', 'permission_callback' => 'cc_fd_staff', 'callback' => function () { return cc_mp_lib_out(); }]);
    register_rest_route('cc/v1', '/mp-lib', ['methods' => 'POST', 'permission_callback' => 'cc_fd_staff', 'callback' => function (WP_REST_Request $r) {
        $kind = $r->get_param('kind') === 't' ? 't' : 'r'; $act = (string) $r->get_param('act'); $l = cc_mp_lib(); $in = json_decode((string) $r->get_param('data'), true);
        if ($act === 'del') { $id = cc_mp_rid($in['id'] ?? ''); $l[$kind] = array_values(array_filter($l[$kind], function ($x) use ($id) { return ($x['id'] ?? '') !== $id; })); }
        elseif ($act === 'save') {
            $c = $kind === 'r' ? cc_mp_clean_rec($in) : cc_mp_clean_tpl($in);
            if (!$c) return new WP_Error('cc_bad', $kind === 'r' ? 'A name and at least one ingredient are needed' : 'A name is needed', ['status' => 400]);
            $done = false; foreach ($l[$kind] as $x => $old) if (($old['id'] ?? '') === $c['id']) { $l[$kind][$x] = $c; $done = true; }
            if (!$done) $l[$kind][] = $c;
            usort($l[$kind], function ($a, $b) { return strcasecmp($a['n'], $b['n']); });
        } else return new WP_Error('cc_bad', 'Unknown action', ['status' => 400]);
        cc_mp_lib_put($l);
        return ['ok' => true, 'lib' => cc_mp_lib_out()];
    }]);
    register_rest_route('cc/v1', '/mp-photo', ['methods' => 'POST', 'permission_callback' => 'cc_fd_staff', 'callback' => function (WP_REST_Request $r) {
        $f = $r->get_file_params()['file'] ?? null;
        if (!$f || empty($f['tmp_name']) || $f['error'] || $f['size'] > 10485760) return new WP_Error('cc_bad', 'No file or too big', ['status' => 400]);
        $bytes = file_get_contents($f['tmp_name']); $ft = wp_check_filetype_and_ext($f['tmp_name'], $f['name']); $ext = strtolower((string) ($ft['ext'] ?: pathinfo($f['name'], PATHINFO_EXTENSION)));
        $ok = ['jpg' => 'image/jpeg', 'jpeg' => 'image/jpeg', 'png' => 'image/png', 'webp' => 'image/webp'];
        if (!isset($ok[$ext]) || !@getimagesizefromstring($bytes)) return new WP_Error('cc_bad', 'Photo only (JPG, PNG or WebP)', ['status' => 400]);
        $id = cc_f_store(0, $bytes, 'recipe', $ext, $ok[$ext], 'Recipe photo'); if (!$id) return new WP_Error('cc_fail', 'Could not save', ['status' => 500]);
        update_post_meta($id, 'cc_mp_photo', 1);
        return ['ok' => true, 'id' => $id, 'url' => wp_get_attachment_url($id)];
    }]);
    // Marine plans one day of a package athlete: the whole day's items + her note; answers already given stay with their item
    register_rest_route('cc/v1', '/mp-plan', ['methods' => 'POST', 'permission_callback' => 'cc_fd_staff', 'callback' => function (WP_REST_Request $r) {
        $pid = (int) $r->get_param('page'); $d = cc_fd_date($r->get_param('date')); $in = json_decode((string) $r->get_param('data'), true);
        if (!$pid || get_post_type($pid) !== 'cc_athlete' || !cc_fd_on($pid)) return new WP_Error('cc_no', 'Not a Nutrition package athlete', ['status' => 403]);
        if (!$d || !is_array($in)) return new WP_Error('cc_bad', 'Date and data needed', ['status' => 400]);
        $cur = cc_mp_get($pid, $d); $old = []; foreach ($cur['i'] as $it) $old[$it['u']] = $it;
        $items = []; $seen = [];
        foreach (array_slice((array) ($in['i'] ?? []), 0, 40) as $e) {
            $sl = (string) ($e['sl'] ?? ''); if (!in_array($sl, CC_FD_SLOTS, true)) continue;
            $c = cc_mp_clean_entry($e); if (!$c) continue;
            $u = cc_mp_uid($e['u'] ?? ''); if (!$u || isset($seen[$u])) $u = strtolower(wp_generate_password(10, false)); $seen[$u] = 1;
            $c = ['u' => $u, 'sl' => $sl] + $c; if (!empty($old[$u]['a'])) $c['a'] = $old[$u]['a'];
            $items[] = $c;
        }
        $note = array_key_exists('n', $in) ? mb_substr(trim(sanitize_textarea_field((string) $in['n'])), 0, 3000) : $cur['n'];
        $recs = cc_mp_recs($pid); $ix = cc_mp_lib_idx(); $ch = false;
        foreach ($items as $it) if ($it['k'] === 'r' && isset($ix[$it['rid']])) { $recs[$it['rid']] = $ix[$it['rid']]; $ch = true; }
        if ($ch) update_post_meta($pid, 'cc_mp_rec', wp_slash(wp_json_encode($recs)));
        cc_mp_put($pid, $d, ['i' => $items, 'n' => $note, 'tr' => $cur['tr']]);
        $tp = cc_ath_tp($pid);
        return ['ok' => true, 'day' => cc_mp_staff_day($pid, $d, $tp ? [] : cc_fd_vx($pid), $tp), 'week' => cc_mp_week_html($pid)];
    }]);
    register_rest_route('cc/v1', '/mp-day', ['methods' => 'GET', 'permission_callback' => function (WP_REST_Request $r) use ($own) { return cc_fd_is_nutri() ? cc_fd_on((int) $r->get_param('page')) : $own($r); }, 'callback' => function (WP_REST_Request $r) use ($page) {
        $pid = cc_fd_is_nutri() ? (int) $r->get_param('page') : $page($r); $d = cc_fd_date($r->get_param('date'));
        if (!$pid || !$d) return new WP_Error('cc_bad', 'Page and date needed', ['status' => 400]);
        return cc_mp_ath_day($pid, $d);
    }]);
    // the athlete answers a planned item: y = ate it (logged as planned), d = different (amount / one swap), n = didn't eat it (optional reason)
    register_rest_route('cc/v1', '/mp-answer', ['methods' => 'POST', 'permission_callback' => $own, 'callback' => function (WP_REST_Request $r) use ($page) {
        $pid = $page($r); $d = cc_fd_date($r->get_param('date')); $u = cc_mp_uid($r->get_param('u')); $s = (string) $r->get_param('s');
        if (!$pid || !$d || !$u || !in_array($s, ['y', 'd', 'n'], true)) return new WP_Error('cc_bad', 'Date, item and answer needed', ['status' => 400]);
        $pl = cc_mp_get($pid, $d); $ix = -1; foreach ($pl['i'] as $x => $it) if ($it['u'] === $u) $ix = $x;
        if ($ix < 0) return new WP_Error('cc_none', 'This item is no longer planned', ['status' => 404]);
        $a = ['s' => $s, 'at' => time()];
        if ($s === 'd') {
            $x = (float) str_replace(',', '.', (string) $r->get_param('x')); if ($x > 0) $a['x'] = round(min(5, $x), 2);
            $g = cc_fd_num($r->get_param('g'), 5000); if ($g > 0) { $a['g'] = $g; unset($a['x']); }
            $sw = json_decode((string) $r->get_param('sw'), true);
            if (is_array($sw) && isset($sw['i'])) { $f = cc_fd_item(($sw['f'] ?? []) + ['g' => 100]); if ($f) { unset($f['m'], $f['pl']); $a['sw'] = ['i' => (int) $sw['i'], 'f' => $f]; } }
        }
        if ($s === 'n') { $w = (string) $r->get_param('why'); if (in_array($w, CC_MP_WHY, true)) $a['why'] = $w; }
        $it = $pl['i'][$ix]; $it['a'] = $a; $pl['i'][$ix] = $it; cc_mp_put($pid, $d, $pl);
        // the diary: lines of an earlier answer go, the new ones are added to the planned meal
        $day = cc_fd_get($pid, $d); $day['s'] = (array) ($day['s'] ?? []);
        foreach ($day['s'] as $k => $sl) $day['s'][$k]['i'] = array_values(array_filter((array) ($sl['i'] ?? []), function ($l) use ($u) { return ($l['pl'] ?? '') !== $u; }));
        $lines = cc_mp_lines($pid, $it, $a);
        if ($lines) { $k = $it['sl']; if (empty($day['s'][$k])) $day['s'][$k] = ['t' => '', 'n' => '', 'i' => []]; foreach ($lines as $l) $day['s'][$k]['i'][] = $l; }
        $day['u'] = time(); cc_fd_put($pid, $d, $day);
        $o = cc_mp_ath_day($pid, $d);
        return ['ok' => true, 'day' => cc_fd_out($pid, $d), 'plan' => $o['plan'], 'recs' => $o['recs']];
    }]);
    // the athlete's own "Today's training" line (TrainingPeaks / no Vekta), shown to Marine
    register_rest_route('cc/v1', '/mp-tr', ['methods' => 'POST', 'permission_callback' => $own, 'callback' => function (WP_REST_Request $r) use ($page) {
        $pid = $page($r); $d = cc_fd_date($r->get_param('date')); if (!$pid || !$d) return new WP_Error('cc_bad', 'Date needed', ['status' => 400]);
        $pl = cc_mp_get($pid, $d); $pl['tr'] = cc_fd_txt($r->get_param('tr'), 120); cc_mp_put($pid, $d, $pl);
        return ['ok' => true, 'tr' => $pl['tr']];
    }]);
});
// coaching ends (login removed): the athlete's plans, answers and recipe copies go with the diary; Marine's library stays hers
add_action('delete_user', function ($uid) {
    if (!empty($GLOBALS['cc_keep_record'])) return;
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'meta_key' => 'cc_user', 'meta_value' => (int) $uid, 'numberposts' => -1, 'fields' => 'ids']) as $pid) {
        foreach (cc_mp_days($pid) as $d) delete_post_meta($pid, 'cc_mp_' . $d);
        delete_post_meta($pid, 'cc_mp_rec');
    }
}, 4);

/* ---------- look ---------- */
function cc_mp_css() {
    static $done = false; if ($done) return ''; $done = true;
    $css = <<<'CSS'
html .cc .mp .btn{width:auto;margin:0;min-height:44px}
html .cc .mp input[type=text],html .cc .mp input[type=number],html .cc .mp input[type=search],html .cc .mp input[type=date],html .cc .mp textarea,html .cc .mp select,html .cc .mp-pi input,html .cc .mp-trl input{font:16px var(--body);padding:9px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.2);background:#0b0d0f;color:#fff;box-sizing:border-box;max-width:100%}
html .cc .mp textarea{width:100%}html .cc .mp label{display:grid;gap:6px;color:#d0d6e0;font-size:15px;font-weight:600;margin:0}
html .cc .mp h3{font-size:20px!important;margin:0 0 8px}html .cc .mp h4{font:700 16px var(--body);color:#fff;margin:0;letter-spacing:.01em;text-transform:none}
html .cc .mp-msg{margin:0;font-size:15px;font-weight:600;color:#2bd47a;min-height:0}html .cc .mp-msg.err{color:#ff7a73}html .cc .mp-msg:empty{display:none}
html .cc .mp-row{display:flex;flex-wrap:wrap;align-items:center;gap:10px 14px}
html .cc .mp-x0{flex:none;box-sizing:border-box;width:40px;height:40px;min-width:40px;display:grid;place-items:center;padding:0;border-radius:10px;border:1px solid rgba(255,255,255,.15);background:none;color:#d0d6e0;cursor:pointer}html .cc .mp-x0 svg{display:block;pointer-events:none}
html .cc .mp-tabs{display:flex;gap:8px;margin:0 0 14px;flex-wrap:wrap}html .cc .mp-tab{min-height:44px;padding:8px 16px;border-radius:999px;border:1px solid rgba(255,255,255,.2);background:rgba(255,255,255,.04);color:#fff;font:600 16px var(--body);cursor:pointer}html .cc .mp-tab.on{background:#12a150;border-color:#12a150}
html .cc .mp-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr));gap:10px;margin-top:12px}
html .cc .mp-card{display:grid;grid-template-columns:72px 1fr;gap:12px;padding:12px;border-radius:14px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.03);min-width:0}
html .cc .mp-card>div{min-width:0;display:grid;gap:4px;align-content:start}html .cc .mp-card b{color:#fff;font-size:17px;overflow-wrap:anywhere}html .cc .mp-card small{color:#b8bec8;font-size:14px}
html .cc .mp-card .mp-row{gap:4px 14px;margin-top:4px}html .cc .mp-card.mp-tc{grid-template-columns:1fr}
html .cc .mp-img{width:72px;height:72px;border-radius:12px;object-fit:cover;display:grid;place-items:center;background:rgba(255,255,255,.06);color:#b8bec8}
html .cc .mp-tags{display:flex;flex-wrap:wrap;gap:4px}html .cc .mp-tg{display:inline-block;padding:1px 8px;border-radius:999px;border:1px solid rgba(255,255,255,.18);color:#d0d6e0;font-size:14px;white-space:nowrap}
html .cc .mp-ed{display:grid;gap:14px;padding:14px;border-radius:14px;border:1px solid rgba(43,212,122,.35);background:rgba(18,161,80,.05)}
html .cc .mp-chips{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
html .cc .mp-chip{min-height:40px;padding:6px 14px;border-radius:999px;border:1px solid rgba(255,255,255,.22);background:rgba(255,255,255,.05);color:#fff;font:600 15px var(--body);cursor:pointer;display:inline-flex;align-items:center;justify-content:center}html .cc .mp-chip.on{background:#12a150;border-color:#12a150;color:#fff}
html .cc .mp-ings{list-style:none;margin:0;padding:0;display:grid;gap:8px}html .cc .mp-ings li{display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:12px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08);flex-wrap:wrap}
html .cc .mp-ings .mp-in{flex:1 1 180px;min-width:0;display:grid;gap:2px}html .cc .mp-ings b{color:#fff;font-size:16px;font-weight:600;overflow-wrap:anywhere}html .cc .mp-ings small{color:#b8bec8;font-size:14px}
html .cc .mp-g{display:flex!important;align-items:center;gap:6px;flex:none;font-weight:500!important}html .cc .mp .mp-g input{width:86px}
html .cc .mp-tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px}html .cc .mp-tiles div{padding:8px 10px;border-radius:12px;background:rgba(0,0,0,.25);display:grid;gap:2px}html .cc .mp-tiles b{color:#fff;font-size:19px}html .cc .mp-tiles span{color:#b8bec8;font-size:14px}
html .cc .mp-phw{display:flex;flex-wrap:wrap;align-items:center;gap:12px}html .cc .mp-phw img{width:110px;height:110px;object-fit:cover;border-radius:12px}
html .cc .mp-search{display:grid;gap:8px;padding:12px;border-radius:12px;border:1px solid rgba(43,212,122,.35);background:rgba(18,161,80,.06)}html .cc .mp-search .mp-q{width:100%}
html .cc .mp-pick{display:grid;gap:10px}html .cc .mp-pick b{color:#fff;font-size:16px}
html .cc .mp-tslot{display:grid;gap:8px;padding:10px 0;border-top:1px solid rgba(255,255,255,.08)}html .cc .mp-tslot>b{color:#fff;font-size:16px}
html .cc .mp-tot{padding:10px 12px;border-radius:12px;background:rgba(18,161,80,.08);border:1px solid rgba(43,212,122,.3);font-size:15px;color:#d0d6e0}html .cc .mp-tot b{color:#fff}
html .cc .mp-home .btn{margin:0}
html .cc .mp-plan-s{margin:6px 0 20px;padding:14px 0 0;border-top:1px solid rgba(255,255,255,.12)}html .cc .mp-plan-s .fd-lede a{color:#2bd47a}
html .cc .mp-wl{margin:0 0 6px;font-size:16px;color:#e6e9ee}html .cc .mp-hint{margin:0 0 10px;padding:8px 12px;border-radius:12px;border:1px solid rgba(240,180,90,.3);background:rgba(240,180,90,.06);color:#f3e2c4;font-size:15px}
html .cc .mp-wnav{display:flex;flex-wrap:wrap;align-items:end;gap:8px 10px;margin:10px 0 12px}html .cc .mp-jump{display:flex;flex-wrap:wrap;align-items:end;gap:8px;margin:0;order:3;flex-basis:100%}html .cc .mp-jump .btn{min-height:44px;padding:8px 16px}html .cc .mp-jump label{display:grid;gap:4px}
html .cc .mp-pl{display:grid;gap:14px}html .cc .mp-side{display:grid;gap:8px;padding:12px;border-radius:14px;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.03);min-width:0;align-content:start}
html .cc .mp-side p{margin:0;color:#b8bec8;font-size:14px}html .cc .mp-side .mp-sl{color:#b8bec8;font-size:14px;font-weight:700;margin-top:4px}
html .cc .mp-ch{display:flex;align-items:center;gap:10px;width:100%;min-height:44px;padding:6px 10px;border-radius:12px;border:1px solid rgba(255,255,255,.15);background:rgba(255,255,255,.04);color:#fff;font:500 15px var(--body);text-align:left;cursor:grab;box-sizing:border-box}
html .cc .mp-ch img,html .cc .mp-ch .mp-dot{flex:none;width:32px;height:32px;border-radius:8px;object-fit:cover;background:rgba(255,255,255,.08)}html .cc .mp-ch span{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
html .cc .mp-ch.on{border-color:#2bd47a;background:rgba(18,161,80,.2)}html .cc .mp-chs{display:grid;gap:6px;max-height:420px;overflow:auto}
html .cc .mp-days{display:grid;gap:12px;min-width:0}
html .cc .mp-day{border:1px solid rgba(255,255,255,.12);border-radius:14px;padding:12px;background:rgba(255,255,255,.03);min-width:0;display:grid;gap:10px}html .cc .mp-day.drop{border-color:#2bd47a;background:rgba(18,161,80,.08)}
html .cc .mp-dh{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 10px}html .cc .mp-dh b{color:#fff;font-size:18px}html .cc .mp-dh small{color:#2bd47a;font-size:14px;font-weight:600}
html .cc .mp-train{margin:0;padding:0;list-style:none;display:grid;gap:2px;font-size:15px;color:#e6e9ee}
html .cc .mp-sr{display:grid;gap:6px;padding:8px;border-radius:10px;border-top:1px solid rgba(255,255,255,.07)}html .cc .mp-sr.mp-empty{display:none}html .cc .mp-showall .mp-sr.mp-empty{display:grid}html .cc .mp-sr.drop{background:rgba(18,161,80,.15);outline:1px dashed #2bd47a}
html .cc .mp-sr>b{color:#d0d6e0;font-size:14px;font-weight:700;letter-spacing:.02em}
html .cc .mp-it{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;padding:8px 10px;border-radius:12px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08)}
html .cc .mp-it .mp-in{flex:1 1 160px;min-width:0;display:grid;gap:2px}html .cc .mp-it b{color:#fff;font-size:16px;font-weight:600;overflow-wrap:anywhere}html .cc .mp-it small{color:#b8bec8;font-size:14px}
html .cc .mp .mp-xin{width:84px}html .cc .mp-st{flex:none;display:inline-grid;place-items:center;width:30px;height:30px;border-radius:50%;font-size:16px;font-weight:700;border:1px solid rgba(255,255,255,.2);color:#d0d6e0}
html .cc .mp-st.s-y,html .cc .mp-st.s-d{background:#12a150;border-color:#12a150;color:#fff}html .cc .mp-st.s-n{border-color:#ff7a73;color:#ff7a73}
html .cc .mp-add{justify-self:start;min-height:40px;padding:6px 12px;border-radius:10px;border:1px dashed rgba(43,212,122,.6);background:rgba(18,161,80,.1);color:#c9f3da;font:600 15px var(--body);cursor:pointer;text-align:left}
html .cc .mp-dt{margin:0;padding:8px 10px;border-radius:12px;background:rgba(18,161,80,.08);border:1px solid rgba(43,212,122,.3);font-size:15px;color:#d0d6e0;display:grid;gap:2px}html .cc .mp-dt b{color:#fff}
html .cc .mp-cp{display:grid;gap:8px;padding:10px;border-radius:12px;background:rgba(0,0,0,.25)}html .cc .mp-cp label{display:flex;align-items:center;gap:8px;font-weight:500}html .cc .mp-cp input{width:20px;height:20px}
html .cc .fd-link.mp-lk{font-size:15px}html .cc .mp .fd-link,html .cc .mp-pi .fd-link,html .cc .mp-my .fd-link,html .cc .mp-plan .fd-link{background:none!important;border:0!important;box-shadow:none!important;border-radius:0!important;color:#2bd47a!important;padding:4px 2px!important;min-height:40px;width:auto!important;text-decoration:underline;font:600 15px var(--body)!important;cursor:pointer}
html .cc .mp-adh{margin:10px 0 0;padding:10px 12px;border-radius:12px;border:1px solid rgba(43,212,122,.3);background:rgba(18,161,80,.05)}html .cc .mp-adh h4{margin:0 0 6px;font-size:14px;color:#b8bec8;text-transform:uppercase;letter-spacing:.06em}
html .cc .mp-al{list-style:none;margin:0;padding:0;display:grid;gap:6px}html .cc .mp-al li{display:flex;gap:10px;align-items:flex-start}html .cc .mp-al li>span:last-child{display:grid;gap:1px}html .cc .mp-al b{color:#fff;font-size:15px;font-weight:600}html .cc .mp-al small{color:#b8bec8;font-size:14px}
html .cc .mp-ic{flex:none;display:inline-grid;place-items:center;width:26px;height:26px;border-radius:50%;font-size:14px;font-weight:700;border:1px solid rgba(255,255,255,.2);color:#d0d6e0}html .cc .mp-a-y .mp-ic,html .cc .mp-a-d .mp-ic{background:#12a150;border-color:#12a150;color:#fff}html .cc .mp-a-n .mp-ic{border-color:#ff7a73;color:#ff7a73}
html .cc .mp-adt,html .cc .mp-adn{margin:8px 0 0;font-size:15px;color:#d0d6e0}html .cc .mp-adt b,html .cc .mp-adn b{color:#fff}
html .cc .mp-pis{display:grid;gap:8px}
html .cc .mp-pi{border:1px solid rgba(43,212,122,.4);background:rgba(18,161,80,.08);border-radius:12px;padding:10px;display:grid;gap:10px}
html .cc .mp-pih{display:flex;align-items:center;gap:12px;background:none;border:0;padding:0;margin:0;color:#fff;text-align:left;cursor:pointer;font:inherit;width:100%;min-height:44px;min-width:0;max-width:100%;box-sizing:border-box;white-space:normal;overflow:hidden}html .cc .mp-pi{min-width:0;max-width:100%;box-sizing:border-box}
html .cc .mp-th{flex:none;width:56px;height:56px;border-radius:10px;object-fit:cover;display:grid;place-items:center;background:rgba(255,255,255,.07);color:#b8bec8}html .cc .mp-th svg{display:block}
html .cc .mp-pit{display:grid;gap:2px;min-width:0;flex:1}html .cc .mp-pit small{color:#d0d6e0;font-size:14px}html .cc .mp-pit .mp-fm{color:#c9f3da;font-weight:700}html .cc .mp-pit b{font-size:16px;color:#fff;overflow-wrap:anywhere}
html .cc .mp-chev{flex:none;color:#b8bec8;font-size:20px}
html .cc .mp-acts{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px}html .cc .fd .mp-acts .btn{min-height:44px;margin:0;width:100%;justify-self:stretch;padding:8px 6px;font-size:15px;line-height:1.2;white-space:normal;text-align:center}
html .cc .mp-done{margin:0;font-size:15px;font-weight:600;color:#2bd47a;display:flex;flex-wrap:wrap;gap:4px 12px;align-items:center}html .cc .mp-done.mp-dn{color:#d0d6e0}
html .cc .mp-pan{display:grid;gap:10px;padding:10px;border-radius:10px;background:rgba(0,0,0,.28)}html .cc .mp-pan p{margin:0;color:#fff;font-size:16px;font-weight:600}html .cc .mp-pan .mp-sub{color:#b8bec8;font-size:14px;font-weight:500}
html .cc .mp-cg{display:flex!important;align-items:center;gap:8px;color:#d0d6e0;font-size:15px;font-weight:600}html .cc .mp-pi .mp-cg input{width:100px}
html .cc .mp-sw{margin:0;font-size:15px;color:#e6e9ee}html .cc .mp-sw b{color:#fff}
html .cc .mp-iw{display:grid;gap:6px}html .cc .mp-iw button{text-align:left}
html .cc .mp-note{margin:0 0 10px;padding:12px 14px;border-radius:14px;border:1px solid rgba(43,212,122,.4);background:rgba(18,161,80,.08)}html .cc .mp-note b{color:#c9f3da;font-size:15px}html .cc .mp-note p{margin:4px 0 0;color:#fff;font-size:16px;line-height:1.5}
html .cc .mp-trl{display:grid;gap:6px;margin:0 0 10px;color:#d0d6e0;font-size:15px;font-weight:600}html .cc .mp-trl input{width:100%}
html .cc .mp-my{margin:14px 0 0;border:1px solid rgba(255,255,255,.1);border-radius:14px;background:rgba(255,255,255,.03)}html .cc .mp-my>summary{padding:14px 16px;cursor:pointer;color:#fff;font-weight:700;font-size:17px}html .cc .mp-my>div{padding:0 16px 16px;display:grid;gap:8px}html .cc .mp-my p{margin:0;color:#b8bec8;font-size:15px}
html .cc .mp-my .mp-pih{padding:6px;border-radius:12px;border:1px solid rgba(255,255,255,.08)}
html .cc .mp-modal{position:fixed;inset:0;z-index:99999;background:rgba(0,0,0,.72);display:flex;align-items:flex-start;justify-content:center;overflow:auto;padding:16px;box-sizing:border-box}
html .cc .mp-mbox,.mp-mbox{position:relative;width:100%;max-width:560px;margin:auto 0;background:#121518;border:1px solid rgba(255,255,255,.14);border-radius:16px;padding:16px;box-sizing:border-box;display:grid;gap:12px;color:#d0d6e0;font:16px/1.5 var(--body)}
.mp-mbox img.mp-hero{width:100%;max-height:260px;object-fit:cover;border-radius:12px;display:block}.mp-mbox h3{margin:0;padding-right:48px;color:#fff;font:400 26px/1.15 var(--head,Anton),sans-serif;letter-spacing:.01em}
.mp-mbox .mp-mh{margin:4px 0 0;color:#fff;font:700 16px var(--body);letter-spacing:.01em;text-transform:none}.mp-mbox p{margin:0}.mp-mbox ul{margin:0;padding-left:20px;display:grid;gap:4px;color:#e6e9ee}.mp-mbox small{color:#b8bec8;font-size:14px}
.mp-mbox .mp-close{position:absolute;top:10px;right:10px;width:44px;height:44px;display:grid;place-items:center;padding:0;border-radius:12px;border:1px solid rgba(255,255,255,.2);background:#121518;color:#fff;cursor:pointer}.mp-mbox .mp-close svg{display:block}
.mp-mbox .mp-tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(96px,1fr));gap:8px}.mp-mbox .mp-tiles div{padding:8px 10px;border-radius:12px;background:rgba(255,255,255,.05);display:grid;gap:2px}.mp-mbox .mp-tiles b{color:#fff;font-size:18px}.mp-mbox .mp-tiles span{color:#b8bec8;font-size:14px}
.mp-mbox .fd-rc{display:inline-block;margin-left:6px;padding:1px 7px;border-radius:6px;border:1px solid rgba(255,255,255,.28);color:#e6e9ee;font-size:14px;font-weight:700}
@media (min-width:900px){html .cc .mp-pl{grid-template-columns:260px minmax(0,1fr);align-items:start}html .cc .mp-side{position:sticky;top:84px;max-height:calc(100vh - 100px);overflow:auto}}
CSS;
    return '<style>' . str_replace(["\r", "\n"], '', $css) . '</style>';
}

/* the food search shared by Marine's recipe editor and the athlete's "swap an ingredient" (same table, aliases and raw/cooked staples as the diary) */
function cc_mp_search_js() {
    static $done = false; if ($done) return ''; $done = true;
    $js = <<<'JS'
(function(){if(window.ccMpS){return;}
var DB=null,DBP=null,BYID={},STAP=[],M=null,MP=null;
function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c];});}
function norm(s){return String(s||"").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"");}
var ALIAS={rasher:"bacon",rashers:"bacon",crisps:"potato chips",crisp:"potato chips",porridge:"oats",courgette:"zucchini",courgettes:"zucchini",aubergine:"eggplant",aubergines:"eggplant",biscuit:"cookie",biscuits:"cookies",chips:"french fries",coriander:"cilantro",rocket:"arugula",prawn:"shrimp",prawns:"shrimp",sweets:"candy",treacle:"molasses",swede:"rutabaga",cornflour:"cornstarch",yoghurt:"yogurt",isotonic:"sports drink",krispies:"rice crisp",nutella:"hazelnut spread",preserve:"jam",conserve:"jam",brack:"barmbrack"};
function load(url){if(DBP){return DBP;}DBP=fetch(url,{credentials:"omit"}).then(function(r){if(!r.ok){throw r;}return r.json();}).then(function(d){
DB=d.foods.map(function(r){return {id:r[0],n:r[2],fr:r[3]||"",k:r[4],c:r[5],p:r[6],f:r[7],fi:r[8]==null?0:r[8],su:r[9]==null?0:r[9],na:r[10]==null?null:r[10],st:r[11]||"",q:norm(r[2]+" | "+(r[3]||"")),qn:norm(r[2])};});
BYID={};DB.forEach(function(f){BYID[f.id]=f;});STAP=(d.staples||[]).map(function(s){return {re:new RegExp(s.rx),raw:s.raw,cooked:s.cooked};});return DB;}).catch(function(e){DBP=null;DB=null;throw e;});return DBP;}
function micro(url){if(!MP){MP=fetch(url,{credentials:"omit"}).then(function(r){if(!r.ok){throw r;}return r.json();}).then(function(j){M=j;return j;}).catch(function(e){MP=null;throw e;});}return MP;}
function fe(id){if(!M||!M.m){return null;}var j=M.cols.indexOf("fe"),row=M.m[id];if(j<0||!row){return null;}return row[j]==null?null:+row[j];}
function scoreOf(f,ws){for(var j=0;j<ws.length;j++){if(f.q.indexOf(ws[j])<0){return -1;}}var whole=ws.join(" ");
return f.qn.indexOf(whole)===0?0:(f.qn.indexOf(ws[0])===0?1:(ws.every(function(w){return new RegExp("(^|[^a-z0-9])"+w.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")).test(f.qn);})?2:3));}
function search(q){var ws=norm(q).split(/[\s,]+/).filter(Boolean),out=[],near=false;if(!ws.length||!DB){return {res:[],near:false};}
var wa=[];ws.forEach(function(w){wa=wa.concat((ALIAS[w]||w).split(" "));});var alt=wa.join(" ")!==ws.join(" ");
for(var i=0;i<DB.length;i++){var f=DB[i],sc=scoreOf(f,ws);if(sc<0&&alt){sc=scoreOf(f,wa);if(sc>-1){sc+=4;}}if(sc<0){continue;}out.push([sc,f.n.length,f]);}
if(!out.length&&ws.length>1){var any=[];ws.concat(wa).forEach(function(w){if(w.length>2&&any.indexOf(w)<0){any.push(w);}});
for(var i2=0;i2<DB.length;i2++){var f2=DB[i2],n2=0,st=1;for(var j2=0;j2<any.length;j2++){if(f2.q.indexOf(any[j2])>-1){n2++;if(f2.qn.indexOf(any[j2])===0){st=0;}}}if(n2>0){out.push([-n2*10+st,f2.n.length,f2]);}}near=out.length>0;}
out.sort(function(a,b){return a[0]-b[0]||a[1]-b[1];});return {res:out.slice(0,40).map(function(x){return x[2];}),near:near};}
function staple(f){if(!f||(f.st!=="r"&&f.st!=="c")){return null;}for(var i=0;i<STAP.length;i++){if(STAP[i].re.test(f.qn)){return STAP[i];}}return null;}
function alt(f,want){var sp=staple(f);return (f.st===want||!sp)?f:(BYID[want==="r"?sp.raw:sp.cooked]||f);}
function r1(x){return Math.round((+x||0)*10)/10;}
function rcb(st,W){return st==="r"||st==="c"?' <span class="fd-rc fd-rc-'+st+'">'+esc(st==="r"?W.b_raw:W.b_cooked)+'</span>':"";}
function m100(f,W){return Math.round(+f.k||0)+" kcal · "+(W.c_ab||"C")+" "+r1(f.c)+" · "+(W.p_ab||"P")+" "+r1(f.p)+" · "+(W.f_ab||"F")+" "+r1(f.f)+" / 100 g";}
function resHtml(st,W){if(!DB){return '<p class="fd-muted">'+esc(W.loading)+'</p>';}if(!st.q.trim()){return "";}var r=search(st.q);st.res=r.res;
if(!r.res.length){return '<p class="fd-muted">'+esc(W.noresults)+'</p>';}
return (r.near?'<p class="fd-muted">'+esc(W.closest)+'</p>':'')+'<ul class="fd-rl">'+r.res.map(function(f,ix){return '<li><button type="button" data-mp="pick" data-rx="'+ix+'"><span>'+esc(f.n)+rcb(f.st,W)+'</span>'+(f.fr?'<i>'+esc(f.fr)+'</i>':'')+'<small>'+esc(m100(f,W))+'</small></button></li>';}).join("")+'</ul>';}
function pickHtml(st,W){
if(st.ask){return '<div class="mp-search"><div class="fd-ask"><b>'+esc(st.ask.n)+rcb(st.ask.st,W)+'</b><p>'+esc(W.ask_rc)+'</p><div class="mp-row"><button type="button" class="btn btn-go" data-mp="rc" data-v="r">'+esc(W.w_raw)+'</button><button type="button" class="btn btn-go" data-mp="rc" data-v="c">'+esc(W.w_cooked)+'</button><button type="button" class="fd-link" data-mp="unpick">'+esc(W.cancel)+'</button></div></div></div>';}
if(st.pick&&!st.nog){var p=st.pick,g=parseFloat(st.g)||0;return '<div class="mp-search"><div class="mp-pick"><b>'+esc(p.n)+rcb(p.st,W)+'</b><label class="mp-g">'+esc(W.grams)+' <input type="number" class="mp-pg" inputmode="decimal" min="1" max="5000" step="1" value="'+esc(st.g)+'"></label><small class="mp-pp">'+esc(Math.round(p.k*g/100)+" kcal · "+(W.c_ab||"C")+" "+r1(p.c*g/100)+" · "+(W.p_ab||"P")+" "+r1(p.p*g/100)+" · "+(W.f_ab||"F")+" "+r1(p.f*g/100))+'</small><div class="mp-row"><button type="button" class="btn btn-go" data-mp="pickadd">'+esc(W.addit)+'</button><button type="button" class="fd-link" data-mp="unpick">'+esc(W.cancel)+'</button></div></div></div>';}
return '<div class="mp-search">'+(st.head?'<p class="mp-sub">'+esc(st.head)+'</p>':'')+'<input type="search" class="mp-q" placeholder="'+esc(W.search)+'" value="'+esc(st.q)+'" autocomplete="off" enterkeyhint="search"><div class="mp-res">'+resHtml(st,W)+'</div><button type="button" class="fd-link" data-mp="scancel" style="justify-self:start">'+esc(W.cancel)+'</button></div>';}
function pickAct(st,a,b){if(a==="pick"){var f=st.res[+b.dataset.rx];if(!f){return false;}if(staple(f)){st.ask=f;}else{st.pick=f;}}
else if(a==="rc"){st.pick=alt(st.ask,b.dataset.v);st.ask=null;}else if(a==="unpick"){st.pick=null;st.ask=null;}return !!(st.pick&&st.nog);}
function food(f,g){var o={id:f.id,n:f.n,g:Math.round((+g||0)*10)/10,k:f.k,c:f.c,p:f.p,f:f.f,fi:f.fi||0,su:f.su||0};if(f.na!=null&&f.na!==""){o.na=f.na;}if(f.st){o.st=f.st;}return o;}
function send(url,data,nonce,method){var o={method:method||"POST",credentials:"same-origin",headers:{"X-WP-Nonce":nonce}};
if(o.method==="GET"){url+=(url.indexOf("?")>-1?"&":"?")+new URLSearchParams(data).toString();}else if(data instanceof FormData){o.body=data;}else{var fd=new FormData();for(var k in data){fd.append(k,data[k]);}o.body=fd;}
return fetch(url,o).then(function(r){return r.json().catch(function(){return {};}).then(function(j){if(!r.ok){throw j;}return j;});});}
window.ccMpS={load:load,micro:micro,fe:fe,search:search,staple:staple,alt:alt,resHtml:resHtml,pickHtml:pickHtml,pickAct:pickAct,food:food,esc:esc,rcb:rcb,send:send,r1:r1,ready:function(){return !!DB;}};
})();
JS;
    return '<script>' . str_replace(["\r", "\n"], '', $js) . '</script>';
}

/* the athlete's side: hooks called by the diary (food.php) */
function cc_mp_ajs() {
    static $done = false; if ($done) return ''; $done = true;
    $js = <<<'JS'
(function(){
var A=document.querySelector(".mp-acfg"),F=window.ccFd,S=window.ccMpS;if(!A||!F||!S){return;}
var C=JSON.parse(A.getAttribute("data-cfg")),W=C.w,root=F.root,esc=S.esc,P={plans:{},recs:C.recs||{},pend:{},ed:{},myOpen:false,busy:false};
C.days.forEach(function(d){P.plans[d.d]=d;});
var XI='<svg width="16" height="16" viewBox="0 0 14 14" aria-hidden="true" focusable="false"><path d="M2.5 2.5l9 9M11.5 2.5l-9 9" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>';
var BOWL='<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true" focusable="false"><path d="M3 11h18a9 9 0 0 1-18 0z"/><path d="M8 7c0-1.5 1-2 1-3.5M12 7c0-1.5 1-2 1-3.5M16 7c0-1.5 1-2 1-3.5"/></svg>';
function f0(x){return Math.round(+x||0).toLocaleString(C.lang);}
function f1(x){return (Math.round((+x||0)*10)/10).toLocaleString(C.lang,{maximumFractionDigits:2});}
function xs(x){return f1(x)+"×";}
function send(u,d,m){return S.send(u,d,C.nonce,m);}
function items(d,k){var p=P.plans[d];return p?(p.i||[]).filter(function(it){return it.sl===k;}):[];}
function find(d,u){var p=P.plans[d];if(!p){return null;}for(var i=0;i<p.i.length;i++){if(p.i[i].u===u){return p.i[i];}}return null;}
function th(r){return r&&r.phu?'<img class="mp-th" src="'+esc(r.phu)+'" alt="" loading="lazy">':'<span class="mp-th">'+BOWL+'</span>';}
function macs(m){return m?f0(m.k)+" kcal · "+W.c_ab+" "+f0(m.c)+" g · "+W.p_ab+" "+f0(m.p)+" g · "+W.f_ab+" "+f0(m.f)+" g":"";}
window.ccMpHas=function(d,k){return items(d,k).length>0;};
window.ccMpTag=function(it){return it&&it.pl?' <span class="fd-tag">'+esc(W.from_m)+'</span>':"";};
window.ccMpSlot=function(d,k){var a=items(d,k);if(!a.length){return "";}return '<div class="mp-pis">'+a.map(function(it){return card(d,it);}).join("")+'</div>';};
function card(d,it){var r=it.k==="r"?P.recs[it.rid]:null,a=it.a||{},e=P.ed[it.u],nm=r?r.n:(it.f?it.f.n:""),sub=it.k==="r"?W.por_x.replace("%s",xs(it.x)):f0(it.f.g)+" g";
var h='<div class="mp-pi" data-u="'+esc(it.u)+'" data-d="'+esc(d)+'">';
var inner=(it.k==="r"?th(r):'<span class="mp-th">'+BOWL+'</span>')+'<span class="mp-pit"><small class="mp-fm">'+esc(W.from_m)+'</small><b>'+esc(nm)+'</b><small>'+esc(sub)+(it.pm?" · "+esc(f0(it.pm.k))+" kcal":"")+'</small></span>';
h+=it.k==="r"?'<button type="button" class="mp-pih" data-mp="open" aria-label="'+esc(W.open_r+": "+nm)+'">'+inner+'<span class="mp-chev" aria-hidden="true">›</span></button>':'<div class="mp-pih" style="cursor:default">'+inner+'</div>';
if(e&&e.mode==="d"){h+=diffHtml(it,e);}
else if(e&&e.mode==="n"){h+=skipHtml(e);}
else if(a.s&&!(e&&e.mode==="menu")){h+='<p class="mp-done'+(a.s==="n"?" mp-dn":"")+'">'+esc(a.s==="y"?"✓ "+W.done_y:(a.s==="d"?"✓ "+W.done_d:W.done_n))+' <button type="button" class="fd-link" data-mp="chg">'+esc(W.change)+'</button></p>';}
else{h+='<div class="mp-acts"><button type="button" class="btn btn-go" data-mp="y">✓ '+esc(W.ate)+'</button><button type="button" class="btn btn-ghost" data-mp="d">✎ '+esc(W.diff)+'</button><button type="button" class="btn btn-ghost" data-mp="n">✗ '+esc(W.skip)+'</button></div>';}
return h+'</div>';}
function ingName(it,i){if(it.k!=="r"){return it.f.n;}var r=P.recs[it.rid];return r&&r.ing[i]?r.ing[i].n:"";}
function diffHtml(it,e){var h='<div class="mp-pan"><p>'+esc(W.amount)+'</p><div class="mp-chips">'+[0.5,1,1.5].map(function(x){var on=!e.g&&e.x===x;return '<button type="button" class="mp-chip'+(on?" on":"")+'" data-mp="dx" data-x="'+x+'" aria-pressed="'+(on?"true":"false")+'">'+esc(xs(x))+'</button>';}).join("")+'<label class="mp-cg">'+esc(W.custom_g)+' <input type="number" class="mp-gi" inputmode="decimal" min="1" max="5000" step="1" value="'+esc(e.g||"")+'"></label></div>';
if(e.sw){h+='<p class="mp-sw">'+esc(ingName(it,e.sw.i))+' → <b>'+esc(e.sw.f.n)+'</b> <button type="button" class="fd-link" data-mp="swx">'+esc(W.cancel)+'</button></p>';}
else if(e.pk){h+=S.pickHtml(e.pk,W);}
else if(e.pi===-1){var r=P.recs[it.rid];h+='<div class="mp-iw"><p class="mp-sub">'+esc(W.swap_which)+'</p><div class="mp-chips">'+(r?r.ing:[]).map(function(i,ix){return '<button type="button" class="mp-chip" data-mp="swi" data-i="'+ix+'">'+esc(i.n)+'</button>';}).join("")+'</div><button type="button" class="fd-link" data-mp="swx" style="justify-self:start">'+esc(W.cancel)+'</button></div>';}
else{h+='<button type="button" class="fd-link" data-mp="swo" style="justify-self:start">'+esc(it.k==="r"?W.swap:W.swap_f)+'</button>';}
return h+'<div class="mp-row"><button type="button" class="btn btn-go" data-mp="dsave">'+esc(W.log_it)+'</button><button type="button" class="fd-link" data-mp="ecancel">'+esc(W.cancel)+'</button></div></div>';}
function skipHtml(e){return '<div class="mp-pan"><p class="mp-sub">'+esc(W.why)+'</p><div class="mp-chips">'+["time","hungry","out","other"].map(function(w){var on=e.why===w;return '<button type="button" class="mp-chip'+(on?" on":"")+'" data-mp="why" data-w="'+w+'" aria-pressed="'+(on?"true":"false")+'">'+esc(W["r_"+w])+'</button>';}).join("")+'</div>'
+'<div class="mp-row"><button type="button" class="btn btn-go" data-mp="nsave">'+esc(W.save)+'</button><button type="button" class="fd-link" data-mp="ecancel">'+esc(W.cancel)+'</button></div><button type="button" class="fd-link" data-mp="inst" style="justify-self:start">'+esc(W.instead)+'</button></div>';}
window.ccMpTop=function(d){var p=P.plans[d],h="";if(p&&p.n){h+='<div class="mp-note"><b>'+esc(d===C.today?W.plan_today:W.plan_day)+'</b><p>'+esc(p.n).replace(/\n/g,"<br>")+'</p></div>';}
if(C.trf){h+='<label class="mp-trl">'+esc(d===C.today?W.training:W.training_d)+'<input type="text" class="mp-tri" maxlength="120" placeholder="'+esc(W.training_ph)+'" value="'+esc(p?p.tr:"")+'"></label>';}return h;};
var mybox=document.createElement("div");mybox.className="mp-mybox";var mb=root.querySelector(".fd-minebox");if(mb){root.insertBefore(mybox,mb);}else{root.appendChild(mybox);}
function renderMy(){var ids=Object.keys(P.recs);if(!ids.length){mybox.innerHTML="";return;}ids.sort(function(a,b){return String(P.recs[a].n).localeCompare(P.recs[b].n);});
mybox.innerHTML='<details class="mp-my"'+(P.myOpen?" open":"")+'><summary>'+esc(W.myrec)+'</summary><div><p>'+esc(W.myrec_l)+'</p>'+ids.map(function(id){var r=P.recs[id];return '<button type="button" class="mp-pih" data-mp="ropen" data-rid="'+esc(id)+'">'+th(r)+'<span class="mp-pit"><b>'+esc(r.n)+'</b><small>'+esc(W.per_portion+": "+macs(r.mac))+'</small></span><span class="mp-chev" aria-hidden="true">›</span></button>';}).join("")+'</div></details>';}
mybox.addEventListener("toggle",function(e){if(e.target.classList.contains("mp-my")){P.myOpen=e.target.open;}},true);
window.ccMpAfter=function(d){if(!P.plans[d]&&!P.pend[d]){P.pend[d]=1;send(C.u.day,{page:C.page,date:d},"GET").then(function(j){P.plans[d]=j.plan;Object.assign(P.recs,j.recs||{});delete P.pend[d];if(F.date()===d){F.render();}}).catch(function(){delete P.pend[d];});}
renderMy();if(C.open&&!P.opened){P.opened=1;modal(C.open,1,false);}};
function tile(v,l){return '<div><b>'+esc(v)+'</b><span>'+esc(l)+'</span></div>';}
function modal(rid,x,fromPlan){var r=P.recs[rid];if(!r){return;}x=+x||1;var por=Math.max(1,+r.por||1),m=r.mac||{};
var h='<div class="mp-mbox"><button type="button" class="mp-close" data-mp="close" aria-label="'+esc(W.close)+'">'+XI+'</button>'+(r.phu?'<img class="mp-hero" src="'+esc(r.phu)+'" alt="">':'')+'<h3>'+esc(r.n)+'</h3>'
+'<p class="mp-mh">'+esc(fromPlan?W.your_portion.replace("%s",xs(x)):W.per_portion)+'</p><div class="mp-tiles">'+tile(f0(m.k*x),"kcal")+tile(f0(m.c*x)+" g",W.carbs)+tile(f0(m.p*x)+" g",W.protein)+tile(f0(m.f*x)+" g",W.fat)+tile(f0(m.fi*x)+" g",W.fibre)+'</div>'
+'<p class="mp-mh">'+esc(W.ingredients)+'</p><ul>'+r.ing.map(function(i){return '<li>'+esc(f0(i.g/por*x))+' g '+esc(i.n)+S.rcb(i.st,W)+'</li>';}).join("")+'</ul>'
+(r.m?'<p class="mp-mh">'+esc(W.method)+'</p><p>'+esc(r.m).replace(/\n/g,"<br>")+'</p>':'')+'<small>'+esc(W.makes.replace("%s",por))+'</small></div>';
var ov=document.createElement("div");ov.className="mp-modal";ov.setAttribute("role","dialog");ov.setAttribute("aria-modal","true");ov.setAttribute("aria-label",r.n);ov.innerHTML=h;
var wrap=document.querySelector(".cc")||document.body;wrap.appendChild(ov);document.documentElement.style.overflow="hidden";var cb=ov.querySelector(".mp-close");if(cb){cb.focus();}
ov.addEventListener("click",function(e){if(e.target===ov||e.target.closest(".mp-close")){closeM(ov);}});}
function closeM(ov){ov.remove();document.documentElement.style.overflow="";}
document.addEventListener("keydown",function(e){if(e.key==="Escape"){var ov=document.querySelector(".mp-modal");if(ov){closeM(ov);}}});
function answer(d,u,data){var it=find(d,u);if(!it||P.busy){return;}P.busy=true;var b=Object.assign({page:C.page,date:d,u:u},data);
F.flush().then(function(){return send(C.u.ans,b);}).then(function(j){P.busy=false;P.plans[d]=j.plan;Object.assign(P.recs,j.recs||{});delete P.ed[u];F.setDay(j.day);F.status(W.saved);})
.catch(function(){P.busy=false;F.status(W.err,true);});}
function rr(){F.render();}
root.addEventListener("click",function(e){var b=e.target.closest("[data-mp]");if(!b||!root.contains(b)){return;}var a=b.dataset.mp;
if(a==="ropen"){modal(b.dataset.rid,1,false);return;}
var c=b.closest(".mp-pi");if(!c){return;}var d=c.dataset.d,u=c.dataset.u,it=find(d,u);if(!it){return;}var ed=P.ed[u];
if(a==="open"){modal(it.rid,it.x,true);}
else if(a==="y"){answer(d,u,{s:"y"});}
else if(a==="d"){P.ed[u]={mode:"d",x:1,g:"",sw:null,pk:null,pi:null};rr();}
else if(a==="n"){P.ed[u]={mode:"n",why:""};rr();}
else if(a==="chg"){P.ed[u]={mode:"menu"};rr();}
else if(a==="ecancel"){delete P.ed[u];rr();}
else if(a==="dx"){ed.x=+b.dataset.x;ed.g="";rr();}
else if(a==="why"){ed.why=ed.why===b.dataset.w?"":b.dataset.w;rr();}
else if(a==="swo"){if(it.k==="r"){ed.pi=-1;rr();}else{ed.pi=0;ed.pk={q:"",res:[],nog:true,head:W.swap_for.replace("%s",it.f.n)};rr();S.load(C.foods).then(function(){var r=root.querySelector('.mp-pi[data-u="'+u+'"] .mp-res');if(r){r.innerHTML=S.resHtml(ed.pk,W);}});focusQ(u);}}
else if(a==="swi"){ed.pi=+b.dataset.i;ed.pk={q:"",res:[],nog:true,head:W.swap_for.replace("%s",ingName(it,ed.pi))};rr();S.load(C.foods).then(function(){var r=root.querySelector('.mp-pi[data-u="'+u+'"] .mp-res');if(r){r.innerHTML=S.resHtml(ed.pk,W);}});focusQ(u);}
else if(a==="swx"){ed.sw=null;ed.pk=null;ed.pi=null;rr();}
else if(a==="scancel"){ed.pk=null;ed.pi=null;rr();}
else if(a==="pick"||a==="rc"||a==="unpick"){if(S.pickAct(ed.pk,a,b)){ed.sw={i:ed.pi,f:S.food(ed.pk.pick,100)};ed.pk=null;}rr();}
else if(a==="dsave"){var dd={s:"d"};if(ed.g){dd.g=ed.g;}else{dd.x=ed.x||1;}if(ed.sw){dd.sw=JSON.stringify(ed.sw);}answer(d,u,dd);}
else if(a==="nsave"){answer(d,u,{s:"n",why:ed.why||""});}
else if(a==="inst"){var sl=it.sl;P.busy=false;var bb={page:C.page,date:d,u:u,s:"n",why:ed.why||""};F.flush().then(function(){return send(C.u.ans,bb);}).then(function(j){P.plans[d]=j.plan;delete P.ed[u];F.setDay(j.day);F.add(sl);}).catch(function(){F.status(W.err,true);});}
});
function focusQ(u){var q=root.querySelector('.mp-pi[data-u="'+u+'"] .mp-q');if(q){q.focus();}}
var qt=null,tt=null;
root.addEventListener("input",function(e){var el=e.target;
if(el.classList.contains("mp-tri")){var d=F.date(),v=el.value;if(!P.plans[d]){P.plans[d]={d:d,i:[],n:"",tr:""};}P.plans[d].tr=v;clearTimeout(tt);tt=setTimeout(function(){send(C.u.tr,{page:C.page,date:d,tr:v}).then(function(){F.status(W.saved);}).catch(function(){F.status(W.err,true);});},800);return;}
var c=el.closest(".mp-pi");if(!c){return;}var ed=P.ed[c.dataset.u];if(!ed){return;}
if(el.classList.contains("mp-gi")){ed.g=parseFloat(String(el.value).replace(",","."))||"";c.querySelectorAll('[data-mp="dx"]').forEach(function(x){x.classList.toggle("on",!ed.g&&+x.dataset.x===ed.x);});return;}
if(el.classList.contains("mp-q")&&ed.pk){ed.pk.q=el.value;clearTimeout(qt);qt=setTimeout(function(){var r=c.querySelector(".mp-res");if(r){r.innerHTML=S.resHtml(ed.pk,W);}},120);}});
root.addEventListener("keydown",function(e){if(e.key==="Enter"&&e.target.classList.contains("mp-q")){e.preventDefault();var f=e.target.closest(".mp-pi").querySelector('.fd-rl [data-mp="pick"]');if(f){f.click();}}});
F.render();
})();
JS;
    return '<script>' . str_replace(["\r", "\n"], '', $js) . '</script>';
}

/* Marine's library and the planning view (English) */
function cc_mp_sjs() {
    static $done = false; if ($done) return ''; $done = true;
    $js = <<<'JS'
(function(){var S=window.ccMpS;if(!S){return;}var esc=S.esc,r1=S.r1;
var WS={search:"Search a food, e.g. oats, banana",loading:"Loading foods…",noresults:"No food found. Try another word.",closest:"No exact match. Closest foods:",ask_rc:"Raw or cooked weight?",w_raw:"Raw / dry",w_cooked:"Cooked",grams:"Amount (g)",addit:"Add",cancel:"Cancel",b_raw:"RAW / DRY",b_cooked:"COOKED",c_ab:"C",p_ab:"P",f_ab:"F"};
var XI='<svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true" focusable="false"><path d="M2.5 2.5l9 9M11.5 2.5l-9 9" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>';
var BOWL='<svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" aria-hidden="true" focusable="false"><path d="M3 11h18a9 9 0 0 1-18 0z"/><path d="M8 7c0-1.5 1-2 1-3.5M12 7c0-1.5 1-2 1-3.5M16 7c0-1.5 1-2 1-3.5"/></svg>';
function f0(x){return Math.round(+x||0).toLocaleString("en");}
function uid(){return Math.random().toString(36).slice(2,12)+"x";}
function macLine(m){return m?f0(m.k)+" kcal · C "+f0(m.c)+" g · P "+f0(m.p)+" g · F "+f0(m.f)+" g":"";}
function fmac(f,x){var g=(+f.g||0)/100*(x||1),o={};["k","c","p","f","fi","su"].forEach(function(k){o[k]=(+f[k]||0)*g;});var v=S.fe(f.id);o.fe=v==null?0:v*g;return o;}
function add(t,m){if(!m){return;}["k","c","p","f","fi","fe"].forEach(function(k){t[k]=(t[k]||0)+(+m[k]||0);});}
function zero(){return {k:0,c:0,p:0,f:0,fi:0,fe:0};}
function tiles(m,iron,inc){return '<div class="mp-tiles"><div><b>'+f0(m.k)+'</b><span>kcal</span></div><div><b>'+f0(m.c)+' g</b><span>Carbs</span></div><div><b>'+f0(m.p)+' g</b><span>Protein</span></div><div><b>'+f0(m.f)+' g</b><span>Fat</span></div><div><b>'+r1(m.fi)+' g</b><span>Fibre</span></div>'+(iron?'<div><b>'+r1(m.fe)+' mg</b><span>Iron'+(inc?" (incomplete)":"")+'</span></div>':'')+'</div>';}

/* ===== library ===== */
var LR=document.querySelector(".mp-lib");
if(LR){(function(){var C=JSON.parse(LR.getAttribute("data-cfg")),L={lib:C.lib,tab:"r",ed:null,te:null,pk:null,msg:"",err:false};
function send(u,d){return S.send(u,d,C.nonce);}
function RB(){var o={};L.lib.r.forEach(function(r){o[r.id]=r;});return o;}
function rcalc(e){var t={k:0,c:0,p:0,f:0,fi:0,su:0,fe:0},miss=0,g=0,por=Math.max(1,parseInt(e.por,10)||1);(e.ing||[]).forEach(function(i){var gr=+i.g||0;if(gr<=0){return;}g+=gr;["k","c","p","f","fi","su"].forEach(function(x){t[x]+=(+i[x]||0)*gr/100;});var v=S.fe(i.id);if(v==null){miss+=gr;}else{t.fe+=v*gr/100;}});
for(var x in t){t[x]=t[x]/por;}t.w=g/por;t.inc=g>0&&miss/g>0.3;return t;}
function emac(e,rb){if(e.k==="r"){var r=rb[e.rid];if(!r||!r.mac){return null;}var m={};["k","c","p","f","fi","fe"].forEach(function(x){m[x]=(+r.mac[x]||0)*(+e.x||1);});return m;}return fmac(e.f,1);}
function msg(){return '<p class="mp-msg'+(L.err?" err":"")+'" role="status">'+esc(L.msg)+'</p>';}
function render(){var h='<div class="mp-tabs" role="tablist"><button type="button" class="mp-tab'+(L.tab==="r"?" on":"")+'" data-mp="tab" data-t="r" role="tab" aria-selected="'+(L.tab==="r")+'">Recipes ('+L.lib.r.length+')</button><button type="button" class="mp-tab'+(L.tab==="t"?" on":"")+'" data-mp="tab" data-t="t" role="tab" aria-selected="'+(L.tab==="t")+'">Day templates ('+L.lib.t.length+')</button></div>';
if(L.tab==="r"){h+=L.ed?recEd():recList();}else{h+=L.te?tplEd():tplList();}LR.innerHTML=h;}
function recList(){var h='<div class="mp-row"><button type="button" class="btn btn-go" data-mp="rnew">New recipe</button></div>'+msg();
if(!L.lib.r.length){return h+'<p class="fd-muted">No recipes yet. Start with one you give most often.</p>';}
return h+'<div class="mp-cards">'+L.lib.r.map(function(r){return '<div class="mp-card">'+(r.phu?'<img class="mp-img" src="'+esc(r.phu)+'" alt="" loading="lazy">':'<span class="mp-img">'+BOWL+'</span>')+'<div><b>'+esc(r.n)+'</b>'+(r.tags.length?'<span class="mp-tags">'+r.tags.map(function(t){return '<span class="mp-tg">'+esc(t)+'</span>';}).join("")+'</span>':'')+'<small>Per portion ('+f0(r.mac.w)+' g): '+esc(macLine(r.mac))+' · fibre '+r1(r.mac.fi)+' g · iron '+r1(r.mac.fe)+' mg'+(r.mac.fei?" (incomplete)":"")+'</small><small>'+r.ing.length+' ingredient'+(r.ing.length===1?"":"s")+' · '+r.por+' portion'+(r.por===1?"":"s")+'</small><div class="mp-row"><button type="button" class="fd-link" data-mp="redit" data-id="'+esc(r.id)+'">Edit</button><button type="button" class="fd-link" data-mp="rdup" data-id="'+esc(r.id)+'">Duplicate</button><button type="button" class="fd-link" data-mp="rdel" data-id="'+esc(r.id)+'">Delete</button></div></div></div>';}).join("")+'</div>';}
function recEd(){var e=L.ed,t=rcalc(e),h='<div class="mp-ed"><h3>'+(e.id?"Edit recipe":"New recipe")+'</h3><label>Name<input type="text" data-e="n" value="'+esc(e.n)+'" maxlength="120"></label>';
h+='<div class="mp-phw">'+(e.phu?'<img src="'+esc(e.phu)+'" alt="">':'<span class="mp-img">'+BOWL+'</span>')+'<label class="btn btn-ghost" style="display:inline-flex;align-items:center;cursor:pointer">'+(e.phu?"Change photo":"Add a photo")+'<input type="file" accept="image/jpeg,image/png,image/webp" hidden data-e="ph"></label>'+(e.phu?'<button type="button" class="fd-link" data-mp="phdel">Remove photo</button>':'')+'</div>';
h+='<div><h4 style="margin-bottom:6px">Tags</h4><div class="mp-chips">'+C.tags.map(function(tg){var on=e.tags.indexOf(tg)>-1;return '<button type="button" class="mp-chip'+(on?" on":"")+'" data-mp="tag" data-t="'+esc(tg)+'" aria-pressed="'+on+'">'+esc(tg)+'</button>';}).join("")+'</div></div>';
h+='<label style="max-width:220px">Number of portions<input type="number" data-e="por" min="1" max="50" step="1" value="'+esc(e.por)+'"></label>';
h+='<h4>Ingredients (whole recipe)</h4>';
if(e.ing.length){h+='<ul class="mp-ings">'+e.ing.map(function(i,ix){return '<li><div class="mp-in"><b>'+esc(i.n)+S.rcb(i.st,WS)+'</b><small data-ii="'+ix+'">'+esc(macLine(fmac(i,1)))+'</small></div><label class="mp-g"><input type="number" inputmode="decimal" min="0" max="5000" step="1" data-e="ig" data-ix="'+ix+'" value="'+esc(i.g)+'" aria-label="Grams of '+esc(i.n)+'"> g</label><button type="button" class="mp-x0" data-mp="irm" data-ix="'+ix+'" aria-label="Remove '+esc(i.n)+'">'+XI+'</button></li>';}).join("")+'</ul>';}
h+=(L.pk&&L.pk.ctx==="ing")?S.pickHtml(L.pk,WS):'<button type="button" class="btn btn-ghost" data-mp="iadd" style="justify-self:start">Add an ingredient</button>';
h+='<label>Method<textarea rows="5" data-e="m" placeholder="Steps, timing, tips…">'+esc(e.m)+'</textarea></label>';
h+='<div class="mp-tot" data-live><b>Per portion'+(t.w?" ("+f0(t.w)+" g)":"")+'</b>'+tiles(t,true,t.inc)+'</div>';
return h+msg()+'<div class="mp-row"><button type="button" class="btn btn-go" data-mp="rsave">Save recipe</button><button type="button" class="fd-link" data-mp="rcancel">Cancel</button></div></div>';}
function liveRec(){var el=LR.querySelector("[data-live]");if(!el||!L.ed){return;}var t=rcalc(L.ed);el.innerHTML='<b>Per portion'+(t.w?" ("+f0(t.w)+" g)":"")+'</b>'+tiles(t,true,t.inc);}
function tplList(){var rb=RB(),h='<div class="mp-row"><button type="button" class="btn btn-go" data-mp="tnew">New day template</button></div>'+msg();
if(!L.lib.t.length){return h+'<p class="fd-muted">No day templates yet, e.g. “Long ride day”, “Rest day”, “Race day”.</p>';}
return h+'<div class="mp-cards">'+L.lib.t.map(function(t){var tt=zero(),parts=[];C.slots.forEach(function(sv){var a=(t.s&&t.s[sv[0]])||[];if(a.length){parts.push(sv[1]+": "+a.map(function(e){return e.k==="r"?((rb[e.rid]||{}).n||"Recipe")+" ×"+e.x:e.f.n+" "+f0(e.f.g)+" g";}).join(", "));}a.forEach(function(e){add(tt,emac(e,rb));});});
return '<div class="mp-card mp-tc"><div><b>'+esc(t.n)+'</b><small>'+esc(macLine(tt))+'</small>'+parts.map(function(p){return '<small>'+esc(p)+'</small>';}).join("")+'<div class="mp-row"><button type="button" class="fd-link" data-mp="tedit" data-id="'+esc(t.id)+'">Edit</button><button type="button" class="fd-link" data-mp="tdup" data-id="'+esc(t.id)+'">Duplicate</button><button type="button" class="fd-link" data-mp="tdel" data-id="'+esc(t.id)+'">Delete</button></div></div></div>';}).join("")+'</div>';}
function tplEd(){var e=L.te,rb=RB(),tt=zero(),h='<div class="mp-ed"><h3>'+(e.id?"Edit day template":"New day template")+'</h3><label>Name<input type="text" data-t="n" value="'+esc(e.n)+'" maxlength="120" placeholder="e.g. Long ride day"></label>';
C.slots.forEach(function(sv){var k=sv[0],a=e.s[k]||[];h+='<div class="mp-tslot"><b>'+esc(sv[1])+'</b>';
if(a.length){h+='<ul class="mp-ings">'+a.map(function(x,ix){add(tt,emac(x,rb));var nm=x.k==="r"?((rb[x.rid]||{}).n||"Recipe (deleted)"):x.f.n;return '<li><div class="mp-in"><b>'+esc(nm)+(x.k==="f"?S.rcb(x.f.st,WS):"")+'</b><small>'+esc(macLine(emac(x,rb)))+'</small></div><label class="mp-g">'+(x.k==="r"?'<input type="number" inputmode="decimal" min="0.25" max="10" step="0.25" data-t="x" data-k="'+k+'" data-ix="'+ix+'" value="'+esc(x.x)+'" aria-label="Portions"> ×':'<input type="number" inputmode="decimal" min="1" max="5000" step="1" data-t="g" data-k="'+k+'" data-ix="'+ix+'" value="'+esc(x.f.g)+'" aria-label="Grams"> g')+'</label><button type="button" class="mp-x0" data-mp="trm" data-k="'+k+'" data-ix="'+ix+'" aria-label="Remove">'+XI+'</button></li>';}).join("")+'</ul>';}
if(L.pk&&L.pk.ctx==="tf"&&L.pk.k===k){h+=S.pickHtml(L.pk,WS);}
else{h+='<div class="mp-row"><select data-t="sel" data-k="'+k+'" aria-label="Recipe for '+esc(sv[1])+'"><option value="">Add a recipe…</option>'+L.lib.r.map(function(r){return '<option value="'+esc(r.id)+'">'+esc(r.n)+'</option>';}).join("")+'</select><button type="button" class="fd-link" data-mp="tfood" data-k="'+k+'">+ Single food</button></div>';}
h+='</div>';});
h+='<div class="mp-tot" data-tlive><b>Day total</b>'+tiles(tt,true,false)+'</div>';
return h+msg()+'<div class="mp-row"><button type="button" class="btn btn-go" data-mp="tsave">Save template</button><button type="button" class="fd-link" data-mp="tcancel">Cancel</button></div></div>';}
function setMsg(m,err){L.msg=m;L.err=!!err;var el=LR.querySelector(".mp-msg");if(el){el.textContent=m;el.className="mp-msg"+(err?" err":"");}}
function save(kind,act,data){setMsg("Saving…");return send(C.u.lib,{kind:kind,act:act,data:JSON.stringify(data)}).then(function(j){L.lib=j.lib;L.msg="✓ Saved";L.err=false;return j;}).catch(function(e){setMsg((e&&e.message)||"Not saved. Please try again.",true);throw e;});}
function clone(o){return JSON.parse(JSON.stringify(o));}
LR.addEventListener("click",function(e){var b=e.target.closest("[data-mp]");if(!b){return;}var a=b.dataset.mp;
if(a==="tab"){L.tab=b.dataset.t;L.msg="";render();}
else if(a==="rnew"){L.ed={id:"",n:"",tags:[],ing:[],m:"",por:1,ph:0,phu:""};L.pk=null;L.msg="";render();S.micro(C.micro).then(liveRec).catch(function(){});}
else if(a==="redit"||a==="rdup"){var r=L.lib.r.filter(function(x){return x.id===b.dataset.id;})[0];if(!r){return;}L.ed=clone(r);if(a==="rdup"){L.ed.id="";L.ed.n=r.n+" (copy)";}L.pk=null;L.msg="";render();S.micro(C.micro).then(liveRec).catch(function(){});}
else if(a==="rdel"){var r2=L.lib.r.filter(function(x){return x.id===b.dataset.id;})[0];if(!r2||!confirm("Delete “"+r2.n+"” from your library? Athletes it was planned for keep their copy.")){return;}save("r","del",{id:r2.id}).then(render);}
else if(a==="rcancel"){L.ed=null;L.pk=null;L.msg="";render();}
else if(a==="tag"){var t=b.dataset.t,ix=L.ed.tags.indexOf(t);if(ix>-1){L.ed.tags.splice(ix,1);}else{L.ed.tags.push(t);}b.classList.toggle("on");b.setAttribute("aria-pressed",ix<0);}
else if(a==="irm"){L.ed.ing.splice(+b.dataset.ix,1);render();}
else if(a==="iadd"){L.pk={ctx:"ing",q:"",res:[],g:100};render();focusQ();S.load(C.foods).then(refreshRes).catch(function(){});}
else if(a==="tfood"){L.pk={ctx:"tf",k:b.dataset.k,q:"",res:[],g:100};render();focusQ();S.load(C.foods).then(refreshRes).catch(function(){});}
else if(a==="scancel"){L.pk=null;render();}
else if(a==="pick"||a==="rc"||a==="unpick"){S.pickAct(L.pk,a,b);render();var g=LR.querySelector(".mp-pg");if(g){g.focus();g.select();}else{focusQ();}}
else if(a==="pickadd"){var g2=parseFloat(String(L.pk.g).replace(",","."))||0;if(!(g2>0)){return;}var fd=S.food(L.pk.pick,g2);if(L.pk.ctx==="ing"){L.ed.ing.push(fd);}else{var k=L.pk.k;(L.te.s[k]=L.te.s[k]||[]).push({k:"f",f:fd});}L.pk=null;render();}
else if(a==="phdel"){L.ed.ph=0;L.ed.phu="";render();}
else if(a==="rsave"){var e2=L.ed;if(!String(e2.n).trim()||!e2.ing.length){setMsg("Add a name and at least one ingredient.",true);return;}save("r","save",{id:e2.id,n:e2.n,tags:e2.tags,ing:e2.ing,m:e2.m,por:e2.por,ph:e2.ph}).then(function(){L.ed=null;L.pk=null;render();});}
else if(a==="tnew"){L.te={id:"",n:"",s:{}};L.pk=null;L.msg="";render();S.micro(C.micro).catch(function(){});}
else if(a==="tedit"||a==="tdup"){var t2=L.lib.t.filter(function(x){return x.id===b.dataset.id;})[0];if(!t2){return;}L.te=clone(t2);if(!L.te.s||Array.isArray(L.te.s)){L.te.s={};}if(a==="tdup"){L.te.id="";L.te.n=t2.n+" (copy)";}L.pk=null;L.msg="";render();}
else if(a==="tdel"){var t3=L.lib.t.filter(function(x){return x.id===b.dataset.id;})[0];if(!t3||!confirm("Delete the day template “"+t3.n+"”? Days already planned stay as they are.")){return;}save("t","del",{id:t3.id}).then(render);}
else if(a==="tcancel"){L.te=null;L.pk=null;L.msg="";render();}
else if(a==="trm"){L.te.s[b.dataset.k].splice(+b.dataset.ix,1);render();}
else if(a==="tsave"){if(!String(L.te.n).trim()){setMsg("Give the template a name.",true);return;}save("t","save",L.te).then(function(){L.te=null;L.pk=null;render();});}
});
LR.addEventListener("change",function(e){var el=e.target;
if(el.dataset.t==="sel"&&el.value){var k=el.dataset.k;(L.te.s[k]=L.te.s[k]||[]).push({k:"r",rid:el.value,x:1});render();return;}
if(el.dataset.e==="ph"){var fi=el.files[0];if(!fi){return;}if(fi.size>10485760){setMsg("Please choose a photo up to 10 MB.",true);return;}setMsg("Uploading…");var fd=new FormData();fd.append("file",fi);
S.send(C.u.photo,fd,C.nonce).then(function(j){L.ed.ph=j.id;L.ed.phu=j.url;L.msg="";render();}).catch(function(err){setMsg((err&&err.message)||"Photo not uploaded.",true);});}
if(el.dataset.t==="x"||el.dataset.t==="g"){render();}});
var qt=null;
LR.addEventListener("input",function(e){var el=e.target;
if(el.classList.contains("mp-q")&&L.pk){L.pk.q=el.value;clearTimeout(qt);qt=setTimeout(refreshRes,120);return;}
if(el.classList.contains("mp-pg")&&L.pk){L.pk.g=el.value;var p=L.pk.pick,pp=LR.querySelector(".mp-pp"),g=parseFloat(el.value)||0;if(pp&&p){pp.textContent=macLine(fmac(Object.assign({},p,{g:g}),1));}return;}
if(L.ed&&el.dataset.e){var k=el.dataset.e;if(k==="ig"){var i=L.ed.ing[+el.dataset.ix];i.g=parseFloat(el.value)||0;var sm=LR.querySelector('[data-ii="'+el.dataset.ix+'"]');if(sm){sm.textContent=macLine(fmac(i,1));}}else if(k!=="ph"){L.ed[k]=el.value;}liveRec();return;}
if(L.te&&el.dataset.t){var t=el.dataset.t;if(t==="n"){L.te.n=el.value;}else if(t==="x"){L.te.s[el.dataset.k][+el.dataset.ix].x=parseFloat(el.value)||1;}else if(t==="g"){L.te.s[el.dataset.k][+el.dataset.ix].f.g=parseFloat(el.value)||0;}
if(t!=="n"&&t!=="sel"){var tt=zero(),rb=RB();C.slots.forEach(function(sv){(L.te.s[sv[0]]||[]).forEach(function(x){add(tt,emac(x,rb));});});var tl=LR.querySelector("[data-tlive]");if(tl){tl.innerHTML="<b>Day total</b>"+tiles(tt,true,false);}}}});
LR.addEventListener("keydown",function(e){if(e.key==="Enter"&&e.target.classList.contains("mp-pg")){e.preventDefault();var b=LR.querySelector('[data-mp="pickadd"]');if(b){b.click();}}if(e.key==="Enter"&&e.target.classList.contains("mp-q")){e.preventDefault();var f=LR.querySelector('.fd-rl [data-mp="pick"]');if(f){f.click();}}});
function focusQ(){var q=LR.querySelector(".mp-q");if(q){q.focus();}}
function refreshRes(){var r=LR.querySelector(".mp-res");if(r&&L.pk){r.innerHTML=S.resHtml(L.pk,WS);}}
render();})();}

/* ===== planning on the athlete's page ===== */
var PR=document.querySelector(".mp-plan");
if(PR){(function(){var C=JSON.parse(PR.getAttribute("data-cfg")),P={days:{},order:[],sel:null,drag:null,copy:null,addf:null,flt:"",msg:{}},RBm={},TBm={};
C.days.forEach(function(d){P.days[d.d]=d;P.order.push(d.d);});C.r.forEach(function(r){RBm[r.id]=r;});C.t.forEach(function(t){TBm[t.id]=t;});var SL={};C.slots.forEach(function(s){SL[s[0]]=s[1];});
function send(u,d){return S.send(u,d,C.nonce);}
function dTot(day){var t=zero(),e=zero(),ans=false;day.i.forEach(function(it){add(t,it.pm);if(it.em){add(e,it.em);}if(it.a&&it.a.s){ans=true;}});return {p:t,e:e,ans:ans};}
function gkg(c){return C.kg?" ("+r1(c/C.kg)+" g/kg)":"";}
function stIc(it,past){var s=it.a&&it.a.s;if(s==="y"){return '<span class="mp-st s-y" title="Ate it" aria-label="Ate it">✓</span>';}if(s==="d"){return '<span class="mp-st s-d" title="Different" aria-label="Different">✎</span>';}if(s==="n"){return '<span class="mp-st s-n" title="Didn’t eat it" aria-label="Didn’t eat it">✗</span>';}return past?'<span class="mp-st" title="Not answered" aria-label="Not answered">○</span>':"";}
function side(){var q=P.flt.toLowerCase(),h='<aside class="mp-side"><h4>Recipes &amp; templates</h4><p>Drag onto a meal or a day. Phone: tap one, then “Add to …”.</p><input type="search" class="mp-flt" placeholder="Filter, e.g. oats, recovery" value="'+esc(P.flt)+'" aria-label="Filter recipes">';
var ts=C.t.filter(function(t){return !q||t.n.toLowerCase().indexOf(q)>-1;}),rs=C.r.filter(function(r){return !q||(r.n+" "+r.tags.join(" ")).toLowerCase().indexOf(q)>-1;});
h+='<p class="mp-sl">DAY TEMPLATES</p><div class="mp-chs">'+(ts.length?ts.map(function(t){var on=P.sel&&P.sel.k==="t"&&P.sel.id===t.id;return '<button type="button" class="mp-ch'+(on?" on":"")+'" draggable="true" data-mp="sel" data-k="t" data-id="'+esc(t.id)+'" aria-pressed="'+on+'"><span class="mp-dot" aria-hidden="true"></span><span>'+esc(t.n)+'</span></button>';}).join(""):'<p>None yet.</p>')+'</div>';
h+='<p class="mp-sl">RECIPES</p><div class="mp-chs">'+(rs.length?rs.map(function(r){var on=P.sel&&P.sel.k==="r"&&P.sel.id===r.id;return '<button type="button" class="mp-ch'+(on?" on":"")+'" draggable="true" data-mp="sel" data-k="r" data-id="'+esc(r.id)+'" aria-pressed="'+on+'" title="'+esc(macLine(r.mac))+'">'+(r.phu?'<img src="'+esc(r.phu)+'" alt="">':'<span class="mp-dot" aria-hidden="true"></span>')+'<span>'+esc(r.n)+'</span></button>';}).join(""):'<p>None yet.</p>')+'</div>';
if(P.sel){h+='<button type="button" class="fd-link" data-mp="unsel" style="justify-self:start">Clear selection</button>';}return h+'</aside>';}
function dayHtml(d){var day=P.days[d],past=d<=C.today,sel=P.sel,dn=day.dow,h='<section class="mp-day" data-d="'+d+'" aria-label="'+esc(day.lbl)+'"><div class="mp-dh"><b>'+esc(day.lbl)+'</b>'+(d===C.today?'<small>today</small>':'')+'</div><ul class="mp-train">'+day.train.map(function(t){return '<li>'+t+'</li>';}).join("")+'</ul>';
if(sel&&sel.k==="t"&&TBm[sel.id]){h+='<button type="button" class="mp-add" data-mp="apply">+ Apply “'+esc(TBm[sel.id].n)+'” to '+esc(dn)+'</button>';}
h+='<label>Nutrition plan (shown to '+esc(C.first)+' at the top of this day)<textarea rows="2" class="mp-note-in" data-d="'+d+'" placeholder="e.g. 90 g carbs/h on the bike, rice-based dinner">'+esc(day.n)+'</textarea></label>';
C.slots.forEach(function(sv){var k=sv[0],a=day.i.filter(function(it){return it.sl===k;});
h+='<div class="mp-sr'+(a.length?"":" mp-empty")+'" data-sl="'+k+'"><b>'+esc(sv[1].toUpperCase())+'</b>';
a.forEach(function(it){var nm=it.k==="r"?it.rn:it.f.n,a2=it.a||{};h+='<div class="mp-it" data-u="'+esc(it.u)+'">'+stIc(it,past)+'<div class="mp-in"><b>'+esc(nm)+'</b><small>Planned '+esc(macLine(it.pm))+'</small>'+(it.em?'<small>Eaten '+esc(macLine(it.em))+'</small>':'')+(a2.s==="n"&&a2.why?'<small>Reason: '+esc({time:"no time",hungry:"not hungry",out:"ate out",other:"other"}[a2.why]||"")+'</small>':'')+(a2.s==="d"&&a2.sw?'<small>Swapped in '+esc(a2.sw.f.n)+'</small>':'')+'</div>'
+(it.k==="r"?'<label class="mp-g"><input type="number" class="mp-xin" inputmode="decimal" min="0.25" max="10" step="0.25" data-u="'+esc(it.u)+'" value="'+esc(it.x)+'" aria-label="Portions"> ×</label><button type="button" class="fd-link mp-lk" data-mp="link" data-rid="'+esc(it.rid)+'">Copy link</button>':'<label class="mp-g"><input type="number" class="mp-gin" inputmode="decimal" min="1" max="5000" step="1" data-u="'+esc(it.u)+'" value="'+esc(it.f.g)+'" aria-label="Grams"> g</label>')
+'<button type="button" class="mp-x0" data-mp="rm" data-u="'+esc(it.u)+'" aria-label="Remove '+esc(nm)+'">'+XI+'</button></div>';});
if(sel&&sel.k==="r"&&RBm[sel.id]){h+='<button type="button" class="mp-add" data-mp="addr" data-sl="'+k+'">+ Add to '+esc(dn)+' · '+esc(sv[1])+'</button>';}
h+='</div>';});
var t=dTot(day);if(day.i.length){h+='<p class="mp-dt"><span>Planned: <b>'+f0(t.p.k)+' kcal</b> · Carbs <b>'+f0(t.p.c)+' g'+gkg(t.p.c)+'</b> · Protein '+f0(t.p.p)+' g'+gkg(t.p.p)+' · Fat '+f0(t.p.f)+' g · Fibre '+f0(t.p.fi)+' g</span>'+(t.ans?'<span>Eaten from the plan: <b>'+f0(t.e.k)+' kcal</b> · Carbs <b>'+f0(t.e.c)+' g'+gkg(t.e.c)+'</b> · Protein '+f0(t.e.p)+' g · Fat '+f0(t.e.f)+' g</span>':'')+'</p>';}
if(P.addf&&P.addf.d===d){h+='<div class="mp-cp"><label>Meal<select class="mp-afsl">'+C.slots.map(function(sv){return '<option value="'+sv[0]+'"'+(P.addf.sl===sv[0]?" selected":"")+'>'+esc(sv[1])+'</option>';}).join("")+'</select></label>'+S.pickHtml(P.addf.pk,WS)+'</div>';}
if(P.copy===d){h+='<div class="mp-cp"><b>Copy '+esc(day.lbl)+' to:</b>'+P.order.filter(function(x){return x!==d;}).map(function(x){return '<label><input type="checkbox" class="mp-cpx" value="'+x+'"> '+esc(P.days[x].lbl)+'</label>';}).join("")+'<p class="fd-muted" style="margin:0">Unanswered items on those days are replaced; answered ones stay.</p><div class="mp-row"><button type="button" class="btn btn-go" data-mp="docopy">Copy</button><button type="button" class="fd-link" data-mp="nocopy">Cancel</button></div></div>';}
h+='<div class="mp-row">'+(P.addf&&P.addf.d===d?'':'<button type="button" class="fd-link" data-mp="addf">+ Single food</button>')+(day.i.length||day.n?'<button type="button" class="fd-link" data-mp="copy">Copy this day to…</button>':'')+(day.i.some(function(it){return !(it.a&&it.a.s);})?'<button type="button" class="fd-link" data-mp="clear">Clear planned items</button>':'')+'</div>';
var m=P.msg[d];return h+'<p class="mp-msg'+(m&&m.err?" err":"")+'" role="status">'+esc(m?m.t:"")+'</p></section>';}
function render(){PR.innerHTML='<div class="mp-pl'+(P.sel&&P.sel.k==="r"?" mp-showall":"")+'">'+side()+'<div class="mp-days">'+P.order.map(dayHtml).join("")+'</div></div>';}
function renderDay(d){var el=PR.querySelector('.mp-day[data-d="'+d+'"]');if(!el){render();return;}var w=document.createElement("div");w.innerHTML=dayHtml(d);el.replaceWith(w.firstChild);}
function out(it){var o={u:it.u,sl:it.sl,k:it.k};if(it.k==="r"){o.rid=it.rid;o.x=it.x;}else{o.f=it.f;}return o;}
function save(d,quiet){var day=P.days[d];P.msg[d]={t:"Saving…"};if(!quiet){renderDay(d);}
return send(C.u.plan,{page:C.page,date:d,data:JSON.stringify({i:day.i.map(out),n:day.n})}).then(function(j){P.days[d]=j.day;P.msg[d]={t:"✓ Saved"};if(!quiet){renderDay(d);}else{var m=PR.querySelector('.mp-day[data-d="'+d+'"] .mp-msg');if(m){m.textContent="✓ Saved";m.className="mp-msg";}}var wl=document.querySelector(".mp-plan-s .mp-wl");if(wl&&j.week){var tmp=document.createElement("div");tmp.innerHTML=j.week;var hint=document.querySelector(".mp-plan-s .mp-hint");if(hint){hint.remove();}wl.replaceWith.apply(wl,Array.prototype.slice.call(tmp.childNodes));}})
.catch(function(e){P.msg[d]={t:(e&&e.message)||"Not saved. Please try again.",err:true};renderDay(d);});}
function newR(rid,sl,x){var r=RBm[rid];return {u:uid(),sl:sl,k:"r",rid:rid,x:x||1,rn:r?r.n:"",pm:r?scale(r.mac,x||1):null};}
function scale(m,x){var o={};["k","c","p","f","fi","fe"].forEach(function(k){o[k]=(+m[k]||0)*x;});return o;}
function addR(d,sl,rid){P.days[d].i.push(newR(rid,sl,1));save(d);}
function applyT(d,tid){var t=TBm[tid];if(!t){return;}var day=P.days[d],keep=day.i.filter(function(it){return it.a&&it.a.s;});
if(day.i.length>keep.length&&!confirm("Replace the unanswered items on "+day.lbl+" with “"+t.n+"”?")){return;}
var add2=[];C.slots.forEach(function(sv){((t.s&&t.s[sv[0]])||[]).forEach(function(e){if(e.k==="r"){add2.push(newR(e.rid,sv[0],e.x));}else{add2.push({u:uid(),sl:sv[0],k:"f",f:JSON.parse(JSON.stringify(e.f))});}});});
day.i=keep.concat(add2);save(d);}
function copyTo(src,dsts){var s=P.days[src];dsts.forEach(function(d){var day=P.days[d],keep=day.i.filter(function(it){return it.a&&it.a.s;});day.i=keep.concat(s.i.map(function(it){var c=JSON.parse(JSON.stringify(it));c.u=uid();delete c.a;delete c.em;return c;}));if(!day.n&&s.n){day.n=s.n;}save(d);});}
function copyLink(rid,b){var u=C.link+(C.link.indexOf("?")>-1?"&":"?")+"mpr="+encodeURIComponent(rid);var done=function(){var d=b.closest(".mp-day").dataset.d;P.msg[d]={t:"✓ Link copied. Paste it into your Vekta note: "+u};var m=b.closest(".mp-day").querySelector(".mp-msg");if(m){m.textContent=P.msg[d].t;m.className="mp-msg";}};
if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(u).then(done,function(){prompt("Copy this link:",u);});}else{prompt("Copy this link:",u);}}
PR.addEventListener("click",function(e){var b=e.target.closest("[data-mp]");if(!b){return;}var a=b.dataset.mp,dEl=b.closest(".mp-day"),d=dEl?dEl.dataset.d:null;
if(a==="sel"){var k=b.dataset.k,id=b.dataset.id;P.sel=(P.sel&&P.sel.k===k&&P.sel.id===id)?null:{k:k,id:id};render();return;}
if(a==="unsel"){P.sel=null;render();return;}
if(!d){return;}var day=P.days[d];
if(a==="addr"&&P.sel){addR(d,b.dataset.sl,P.sel.id);}
else if(a==="apply"&&P.sel){applyT(d,P.sel.id);}
else if(a==="rm"){day.i=day.i.filter(function(it){return it.u!==b.dataset.u;});save(d);}
else if(a==="link"){copyLink(b.dataset.rid,b);}
else if(a==="copy"){P.copy=d;renderDay(d);}
else if(a==="nocopy"){P.copy=null;renderDay(d);}
else if(a==="docopy"){var ds=Array.prototype.map.call(dEl.querySelectorAll(".mp-cpx:checked"),function(x){return x.value;});if(!ds.length){return;}P.copy=null;renderDay(d);copyTo(d,ds);}
else if(a==="clear"){if(!confirm("Remove the unanswered planned items on "+day.lbl+"?")){return;}day.i=day.i.filter(function(it){return it.a&&it.a.s;});save(d);}
else if(a==="addf"){P.addf={d:d,sl:"bike",pk:{q:"",res:[],g:100}};renderDay(d);var q=PR.querySelector('.mp-day[data-d="'+d+'"] .mp-q');if(q){q.focus();}S.load(C.foods).then(function(){var r=PR.querySelector('.mp-day[data-d="'+d+'"] .mp-res');if(r&&P.addf){r.innerHTML=S.resHtml(P.addf.pk,WS);}}).catch(function(){});}
else if(a==="scancel"){P.addf=null;renderDay(d);}
else if(a==="pick"||a==="rc"||a==="unpick"){S.pickAct(P.addf.pk,a,b);renderDay(d);var g=PR.querySelector('.mp-day[data-d="'+d+'"] .mp-pg');if(g){g.focus();g.select();}}
else if(a==="pickadd"){var pk=P.addf.pk,g2=parseFloat(String(pk.g).replace(",","."))||0;if(!(g2>0)){return;}day.i.push({u:uid(),sl:P.addf.sl,k:"f",f:S.food(pk.pick,g2),pm:fmac(S.food(pk.pick,g2),1)});P.addf=null;save(d);}
});
var nt={},qt=null;
PR.addEventListener("input",function(e){var el=e.target;
if(el.classList.contains("mp-flt")){P.flt=el.value;var pos=el.selectionStart;render();var f=PR.querySelector(".mp-flt");if(f){f.focus();try{f.setSelectionRange(pos,pos);}catch(x){}}return;}
var dEl=el.closest(".mp-day");if(!dEl){return;}var d=dEl.dataset.d;
if(el.classList.contains("mp-note-in")){P.days[d].n=el.value;clearTimeout(nt[d]);nt[d]=setTimeout(function(){save(d,true);},900);return;}
if(el.classList.contains("mp-q")&&P.addf){P.addf.pk.q=el.value;clearTimeout(qt);qt=setTimeout(function(){var r=dEl.querySelector(".mp-res");if(r){r.innerHTML=S.resHtml(P.addf.pk,WS);}},120);return;}
if(el.classList.contains("mp-pg")&&P.addf){P.addf.pk.g=el.value;var pp=dEl.querySelector(".mp-pp"),p=P.addf.pk.pick;if(pp&&p){pp.textContent=macLine(fmac(Object.assign({},p,{g:parseFloat(el.value)||0}),1));}}});
PR.addEventListener("change",function(e){var el=e.target,dEl=el.closest(".mp-day");if(!dEl){return;}var d=dEl.dataset.d,day=P.days[d];
if(el.classList.contains("mp-afsl")&&P.addf){P.addf.sl=el.value;return;}
var it=day.i.filter(function(x){return x.u===el.dataset.u;})[0];if(!it){return;}
if(el.classList.contains("mp-xin")){var x=parseFloat(String(el.value).replace(",","."));if(x>0){it.x=Math.min(10,x);save(d);}}
else if(el.classList.contains("mp-gin")){var g=parseFloat(String(el.value).replace(",","."));if(g>0){it.f.g=Math.min(5000,g);save(d);}}});
PR.addEventListener("keydown",function(e){if(e.key==="Enter"&&e.target.classList.contains("mp-q")){e.preventDefault();var f=e.target.closest(".mp-day").querySelector('.fd-rl [data-mp="pick"]');if(f){f.click();}}if(e.key==="Enter"&&e.target.classList.contains("mp-pg")){e.preventDefault();var b=e.target.closest(".mp-day").querySelector('[data-mp="pickadd"]');if(b){b.click();}}});
PR.addEventListener("dragstart",function(e){var b=e.target.closest&&e.target.closest(".mp-ch");if(!b){return;}P.drag={k:b.dataset.k,id:b.dataset.id};try{e.dataTransfer.setData("text/plain",b.dataset.k+":"+b.dataset.id);e.dataTransfer.effectAllowed="copy";}catch(x){}if(P.drag.k==="r"){var pl=PR.querySelector(".mp-pl");if(pl){pl.classList.add("mp-showall");}}});
PR.addEventListener("dragend",function(){P.drag=null;PR.querySelectorAll(".drop").forEach(function(x){x.classList.remove("drop");});var pl=PR.querySelector(".mp-pl");if(pl&&!(P.sel&&P.sel.k==="r")){pl.classList.remove("mp-showall");}});
function target(e){if(!P.drag){return null;}return P.drag.k==="r"?e.target.closest(".mp-sr"):e.target.closest(".mp-day");}
PR.addEventListener("dragover",function(e){var t=target(e);if(!t){return;}e.preventDefault();try{e.dataTransfer.dropEffect="copy";}catch(x){}PR.querySelectorAll(".drop").forEach(function(x){if(x!==t){x.classList.remove("drop");}});t.classList.add("drop");});
PR.addEventListener("drop",function(e){var t=target(e);if(!t){return;}e.preventDefault();var dr=P.drag,d=t.closest(".mp-day").dataset.d;P.drag=null;t.classList.remove("drop");
if(dr.k==="r"){addR(d,t.dataset.sl,dr.id);}else{applyT(d,dr.id);}var pl=PR.querySelector(".mp-pl");if(pl&&!(P.sel&&P.sel.k==="r")){pl.classList.remove("mp-showall");}});
render();})();}
})();
JS;
    return '<script>' . str_replace(["\r", "\n"], '', $js) . '</script>';
}
