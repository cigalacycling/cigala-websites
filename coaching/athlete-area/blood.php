<?php
/* ---------- Blood tests (Matteo, 18 Nov 2026) ----------
 * Included in the plan: athletes upload their blood test (PDF or photo) privately in the hub, with the date and a tick to share it
 * with the nutritionist. Files are private (served only through the login check), Matteo gets a notification and a "Blood tests" board.
 * Health data: deleted when coaching ends, like the health answers in the rider form. */

function cc_bt_w($k) {
    static $W = [
        'title' => ['en' => 'Blood tests', 'it' => 'Analisi del sangue', 'pt' => 'Análises ao sangue', 'sl' => 'Krvne preiskave'],
        'lede' => ['en' => 'Upload your blood test results here (PDF or photo). Only Matteo sees them, and the nutritionist if you tick the box. They are deleted when your coaching ends.',
                   'it' => 'Carica qui i risultati delle tue analisi del sangue (PDF o foto). Le vede solo Matteo, e la nutrizionista se spunti la casella. Vengono cancellate quando finisce il coaching.',
                   'pt' => 'Carrega aqui os resultados das tuas análises ao sangue (PDF ou foto). Só o Matteo os vê, e a nutricionista se marcares a caixa. São apagados quando o coaching termina.',
                   'sl' => 'Tukaj naloži izvide krvnih preiskav (PDF ali fotografijo). Vidi jih samo Matteo, in nutricionistka, če označiš polje. Izbrišejo se, ko se coaching konča.'],
        'file' => ['en' => 'Choose the file', 'it' => 'Scegli il file', 'pt' => 'Escolhe o ficheiro', 'sl' => 'Izberi datoteko'],
        'date' => ['en' => 'Date of the test', 'it' => 'Data delle analisi', 'pt' => 'Data das análises', 'sl' => 'Datum preiskave'],
        'share' => ['en' => 'Share with my nutritionist', 'it' => 'Condividi con la mia nutrizionista', 'pt' => 'Partilhar com a minha nutricionista', 'sl' => 'Deli z mojo nutricionistko'],
        'send' => ['en' => 'Upload', 'it' => 'Carica', 'pt' => 'Carregar', 'sl' => 'Naloži'],
        'sending' => ['en' => 'Uploading…', 'it' => 'Caricamento…', 'pt' => 'A carregar…', 'sl' => 'Nalaganje…'],
        'done' => ['en' => 'Uploaded. Thank you!', 'it' => 'Caricato. Grazie!', 'pt' => 'Carregado. Obrigado!', 'sl' => 'Naloženo. Hvala!'],
        'bad' => ['en' => 'Please choose a PDF or a photo (up to 10 MB).', 'it' => 'Scegli un PDF o una foto (fino a 10 MB).', 'pt' => 'Escolhe um PDF ou uma foto (até 10 MB).', 'sl' => 'Izberi PDF ali fotografijo (do 10 MB).'],
        'err' => ['en' => 'Not uploaded. Please try again.', 'it' => 'Non caricato. Riprova.', 'pt' => 'Não carregado. Tenta de novo.', 'sl' => 'Ni naloženo. Poskusi znova.'],
        'yours' => ['en' => 'Your uploads', 'it' => 'I tuoi caricamenti', 'pt' => 'Os teus envios', 'sl' => 'Tvoji nalaganja'],
        'open' => ['en' => 'Open', 'it' => 'Apri', 'pt' => 'Abrir', 'sl' => 'Odpri'],
        'del' => ['en' => 'Delete', 'it' => 'Elimina', 'pt' => 'Apagar', 'sl' => 'Izbriši'],
        'delq' => ['en' => 'Delete this blood test?', 'it' => 'Eliminare queste analisi?', 'pt' => 'Apagar estas análises?', 'sl' => 'Izbrišem to preiskavo?'],
        'shared' => ['en' => 'shared with the nutritionist', 'it' => 'condivise con la nutrizionista', 'pt' => 'partilhadas com a nutricionista', 'sl' => 'deljeno z nutricionistko'],
    ];
    $l = $GLOBALS['cc_ath_lang'] ?? 'en'; return $W[$k][$l] ?? $W[$k]['en'];
}
function cc_bt_get($pid) { $a = json_decode((string) get_post_meta((int) $pid, 'cc_blood', true), true); return is_array($a) ? $a : []; }
function cc_bt_put($pid, $a) { update_post_meta((int) $pid, 'cc_blood', wp_slash(wp_json_encode(array_values($a)))); }
function cc_bt_row($pid, $b, $forCoach) {
    $u = wp_get_attachment_url((int) $b['file']); if (!$u) return '';
    $when = $b['date'] ? date_i18n('j M Y', strtotime($b['date'] . ' 12:00')) : date_i18n('j M Y', (int) $b['at']);
    return '<div class="bt-row"><span class="bt-ic">🩸</span><span class="bt-t"><b>' . esc_html($when) . '</b>' . (!empty($b['share']) ? '<small>' . esc_html($forCoach ? 'shared with the nutritionist' : cc_bt_w('shared')) . '</small>' : '') . '</span>'
         . '<a class="btn btn-ghost" href="' . esc_url($u) . '" target="_blank" rel="noopener">' . esc_html($forCoach ? 'Open' : cc_bt_w('open')) . '</a>'
         . '<button type="button" class="bt-del" data-page="' . (int) $pid . '" data-at="' . (int) $b['at'] . '" data-q="' . esc_attr($forCoach ? 'Delete this blood test?' : cc_bt_w('delq')) . '">' . esc_html($forCoach ? 'Delete' : cc_bt_w('del')) . '</button></div>';
}
function cc_bt_assets() {
    static $done = false; if ($done) return ''; $done = true;
    $api = esc_url(rest_url('cc/v1/blood')); $nonce = esc_attr(wp_create_nonce('wp_rest'));
    return '<style>html .cc .bt-form{display:grid;gap:12px;max-width:520px}html .cc .bt-form label{display:grid;gap:6px;font-size:15px;color:#d0d6e0;font-weight:600}'
        . 'html .cc .bt-form input[type=file]{font:16px var(--body);color:#d0d6e0}html .cc .bt-tick{display:flex!important;align-items:center;gap:10px;font-weight:500!important}html .cc .bt-tick input{width:22px;height:22px;accent-color:#12a150}'
        . 'html .cc .bt-form .btn{justify-self:start;width:auto;margin:0}html .cc .bt-msg{font-size:15px;font-weight:600;color:#2bd47a;margin:0}html .cc .bt-msg.err{color:#ff7a73}html .cc .bt-msg:empty{display:none}'
        . 'html .cc .bt-row{display:flex;align-items:center;gap:12px;padding:10px 12px;margin:8px 0 0;border-radius:12px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.03)}'
        . 'html .cc .bt-ic{font-size:20px}html .cc .bt-t{display:grid;flex:1;min-width:0}html .cc .bt-t b{color:#fff;font-size:16px}html .cc .bt-t small{color:#b8bec8;font-size:14px}'
        . 'html .cc .bt-row .btn{width:auto;margin:0;padding:8px 14px}html .cc .bt-del{background:none;border:0;color:#b8bec8;text-decoration:underline;font-size:14px;cursor:pointer;padding:4px}</style>'
        . '<script>(function(){var f=document.querySelector(".bt-form");if(f){var m=f.querySelector(".bt-msg"),W=JSON.parse(f.dataset.w);f.addEventListener("submit",function(e){e.preventDefault();'
        . 'var fi=f.querySelector("input[type=file]").files[0];if(!fi||fi.size>10485760||!/pdf|jpe?g|png|heic|heif/i.test(fi.type+fi.name)){m.className="bt-msg err";m.textContent=W.bad;return;}'
        . 'var d=new FormData();d.append("file",fi);d.append("date",f.querySelector("input[type=date]").value);d.append("share",f.querySelector(".bt-tick input").checked?1:0);var b=f.querySelector(".btn");b.disabled=true;m.className="bt-msg";m.textContent=W.sending;'
        . 'fetch("' . $api . '",{method:"POST",body:d,credentials:"same-origin",headers:{"X-WP-Nonce":"' . $nonce . '"}}).then(function(r){if(!r.ok)throw 0;m.textContent=W.done;setTimeout(function(){var u=location.href.split("#")[0];location.replace(u+(u.indexOf("?")>-1?"&":"?")+"bt="+Date.now()+"#blood");},800);})'
        . '.catch(function(){b.disabled=false;m.className="bt-msg err";m.textContent=W.err;});});}'
        . 'document.addEventListener("click",function(e){var x=e.target.closest(".bt-del");if(!x||!confirm(x.dataset.q))return;var d=new FormData();d.append("page",x.dataset.page);d.append("at",x.dataset.at);'
        . 'fetch("' . esc_url(rest_url('cc/v1/blood-delete')) . '",{method:"POST",body:d,credentials:"same-origin",headers:{"X-WP-Nonce":"' . $nonce . '"}}).then(function(r){if(r.ok)x.closest(".bt-row").remove();});});})();</script>';
}

/* the athlete's hub: after Share a result (16) */
add_filter('cc_ath_after_reports', function ($html, $view, $coach) {
    if (!$view) return $html;
    $list = array_reverse(cc_bt_get($view));
    if ($coach) {
        if (!$list) return $html;
        return $html . '<section class="ath-s bt" id="blood"><h2>' . cc_ath_icon('sweat', 'ath-hic') . 'Blood tests</h2>' . implode('', array_map(function ($b) use ($view) { return cc_bt_row($view, $b, true); }, $list)) . '</section>' . cc_bt_assets();
    }
    $W = ['bad' => cc_bt_w('bad'), 'sending' => cc_bt_w('sending'), 'done' => cc_bt_w('done'), 'err' => cc_bt_w('err')];
    $o = '<section class="ath-s bt" id="blood"><h2>' . cc_ath_icon('sweat', 'ath-hic') . esc_html(cc_bt_w('title')) . '</h2><p class="av-lede">' . esc_html(cc_bt_w('lede')) . '</p>'
       . '<form class="bt-form" data-w="' . esc_attr(wp_json_encode($W)) . '"><label>' . esc_html(cc_bt_w('file')) . '<input type="file" accept="application/pdf,image/*" required></label>'
       . '<label>' . esc_html(cc_bt_w('date')) . '<input type="date" max="' . esc_attr(current_time('Y-m-d')) . '"></label>'
       . '<label class="bt-tick"><input type="checkbox"> ' . esc_html(cc_bt_w('share')) . '</label><button type="submit" class="btn btn-go">' . esc_html(cc_bt_w('send')) . '</button><p class="bt-msg" role="status"></p></form>';
    if ($list) $o .= '<h3 class="av-sub">' . esc_html(cc_bt_w('yours')) . '</h3>' . implode('', array_map(function ($b) use ($view) { return cc_bt_row($view, $b, false); }, $list));
    return $html . $o . '</section>' . cc_bt_assets();
}, 17, 3);
add_filter('cc_ath_nav', function ($nav, $view, $coach) { if ($view && !$coach) $nav[] = ['blood', cc_bt_w('title')]; return $nav; }, 31, 3);

/* Matteo's board */
add_filter('cc_ath_coach_links', function ($html) {
    $seen = (int) get_user_meta(get_current_user_id(), 'cc_blood_seen', true); $n = 0;
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'meta_key' => 'cc_blood', 'fields' => 'ids']) as $p) foreach (cc_bt_get($p) as $b) if ($b['at'] > $seen) $n++;
    return $html . '<a class="av-boardlink" href="' . esc_url(add_query_arg('board', 'blood', home_url('/' . CC_ATH_SLUG . '/'))) . '">Blood tests' . ($n ? ' <span class="av-badge">' . $n . ' new</span>' : '') . '</a>';
}, 20);
add_filter('cc_ath_board', function ($html, $board) {
    if ($board !== 'blood' || !cc_ath_is_coach()) return $html;
    add_action('shutdown', function () { update_user_meta(get_current_user_id(), 'cc_blood_seen', time()); });
    $all = [];
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'meta_key' => 'cc_blood']) as $p) foreach (cc_bt_get($p->ID) as $b) $all[] = [$p, $b];
    usort($all, function ($a, $b) { return $b[1]['at'] <=> $a[1]['at']; });
    $o = '<section class="ath-s"><h2>Blood tests</h2><p class="av-lede">Blood tests your athletes uploaded, newest first. Private: only you (and the nutritionist when the athlete ticked "share") can open them. Deleted when coaching ends.</p>';
    if (!$all) $o .= '<p class="av-lede">None yet.</p>';
    foreach ($all as [$p, $b]) $o .= '<div class="nt-who">' . (function_exists('cc_ph_face') ? cc_ph_face($p->ID, 30) . ' ' : '') . '<b><a style="color:#fff" href="' . esc_url(add_query_arg('view', $p->ID, home_url('/' . CC_ATH_SLUG . '/'))) . '#blood">' . esc_html($p->post_title) . '</a></b>' . (function_exists('cc_ath_flag_for') ? cc_ath_flag_for($p->ID) : '') . '</div>' . cc_bt_row($p->ID, $b, true);
    return $o . '</section>' . cc_bt_assets() . (function_exists('cc_nt_css') ? cc_nt_css() : '');
}, 10, 2);

add_action('rest_api_init', function () {
    $own = function (WP_REST_Request $r) { return cc_ath_is_coach() || (is_user_logged_in() && (int) ($r->get_param('page') ?: cc_ath_page_of(get_current_user_id())) === cc_ath_page_of(get_current_user_id())); };
    register_rest_route('cc/v1', '/blood', ['methods' => 'POST', 'permission_callback' => function () { return is_user_logged_in() && (bool) cc_ath_page_of(get_current_user_id()); }, 'callback' => function (WP_REST_Request $r) {
        $uid = get_current_user_id(); $pid = cc_ath_page_of($uid); $f = $r->get_file_params()['file'] ?? null;
        if (!$f || empty($f['tmp_name']) || $f['error'] || $f['size'] > 10485760) return new WP_Error('cc_bad', 'No file or too big', ['status' => 400]);
        $bytes = file_get_contents($f['tmp_name']); $ft = wp_check_filetype_and_ext($f['tmp_name'], $f['name']);
        $ext = strtolower((string) ($ft['ext'] ?: pathinfo($f['name'], PATHINFO_EXTENSION)));
        $ok = ['pdf' => 'application/pdf', 'jpg' => 'image/jpeg', 'jpeg' => 'image/jpeg', 'png' => 'image/png', 'heic' => 'image/heic', 'heif' => 'image/heif'];
        if (!isset($ok[$ext]) || ($ext === 'pdf' && substr($bytes, 0, 4) !== '%PDF')) return new WP_Error('cc_bad', 'PDF or photo only', ['status' => 400]);
        $id = cc_f_store($pid, $bytes, 'blood', $ext, $ok[$ext], 'Blood test');
        if (!$id) return new WP_Error('cc_fail', 'Could not save', ['status' => 500]);
        $a = cc_bt_get($pid); $a[] = ['at' => time(), 'date' => cc_av_date((string) $r->get_param('date')) ?: null, 'file' => $id, 'share' => $r->get_param('share') ? 1 : 0]; cc_bt_put($pid, $a);
        if (function_exists('cc_push_coaches')) cc_push_coaches('🩸 Blood test from ' . get_the_title($pid), 'New blood test uploaded' . ($r->get_param('share') ? ' (shared with the nutritionist)' : ''), add_query_arg('board', 'blood', home_url('/' . CC_ATH_SLUG . '/')), 'cc-blood', $pid);
        return ['ok' => true];
    }]);
    register_rest_route('cc/v1', '/blood-delete', ['methods' => 'POST', 'permission_callback' => $own, 'callback' => function (WP_REST_Request $r) {
        $pid = (int) ($r->get_param('page') ?: cc_ath_page_of(get_current_user_id())); $at = (int) $r->get_param('at'); $a = cc_bt_get($pid);
        foreach ($a as $k => $b) if ((int) $b['at'] === $at) { wp_delete_attachment((int) $b['file'], true); unset($a[$k]); cc_bt_put($pid, $a); return ['ok' => true]; }
        return new WP_Error('cc_none', 'Not found', ['status' => 404]);
    }]);
});
// health data: gone when coaching ends (login removed), unless the athlete stays coached (moved to Basic)
add_action('delete_user', function ($uid) {
    if (!empty($GLOBALS['cc_keep_record'])) return;
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'meta_key' => 'cc_user', 'meta_value' => (int) $uid, 'numberposts' => -1, 'fields' => 'ids']) as $pid) {
        foreach (cc_bt_get($pid) as $b) wp_delete_attachment((int) $b['file'], true);
        delete_post_meta($pid, 'cc_blood');
    }
}, 4);
