<?php
/* ---------- Blood tests (Matteo, 18 Nov 2026) ----------
 * Included in the plan: athletes upload their blood test (PDF or photo) privately in the hub, with the date and a tick to share it
 * with the nutritionist. Files are private (served only through the login check), Matteo gets a notification and a "Blood tests" board.
 * Health data: deleted when coaching ends, like the health answers in the rider form. */

function cc_bt_w($k) {
    static $W = [
        'title' => ['en' => 'Blood tests', 'it' => 'Analisi del sangue', 'pt' => 'Análises ao sangue', 'sl' => 'Krvne preiskave', 'sk' => 'Krvné testy'],
        // Matteo 18 Nov: Marine reviews shared tests, but she is not the athlete's own nutritionist: one-to-one nutrition is a separate sign-up
        'lede' => ['en' => 'Upload your blood test results here (PDF or photo). Your files are private and kept here as your history, so we can follow how your values change over time. Only Matteo sees them, and Marine Lenehan, our sports nutritionist, if you tick the box: she can take a look and reply to you right here. Working one-to-one with Marine on your nutrition is a separate service: just ask if you would like it.',
                   'it' => 'Carica qui i risultati delle tue analisi del sangue (PDF o foto). I tuoi file sono privati e restano qui come tuo storico, così possiamo seguire come cambiano i valori nel tempo. Li vede solo Matteo, e Marine Lenehan, la nostra nutrizionista sportiva, se spunti la casella: può darci un’occhiata e risponderti direttamente qui. Lavorare individualmente con Marine sulla tua alimentazione è un servizio a parte: chiedi pure se ti interessa.',
                   'pt' => 'Carrega aqui os resultados das tuas análises ao sangue (PDF ou foto). Os teus ficheiros são privados e ficam aqui como o teu histórico, para acompanharmos como os valores mudam ao longo do tempo. Só o Matteo os vê, e a Marine Lenehan, a nossa nutricionista desportiva, se marcares a caixa: ela pode dar uma vista de olhos e responder-te aqui mesmo. Trabalhar individualmente com a Marine na tua alimentação é um serviço à parte: pergunta se tiveres interesse.',
                   'sl' => 'Tukaj naloži izvide krvnih preiskav (PDF ali fotografijo). Tvoje datoteke so zasebne in ostanejo tukaj kot tvoja zgodovina, da lahko spremljamo, kako se vrednosti spreminjajo. Vidi jih samo Matteo, in Marine Lenehan, naša športna nutricionistka, če označiš polje: lahko jih pregleda in ti odgovori kar tukaj. Individualno delo z Marine na tvoji prehrani je ločena storitev: vprašaj, če te zanima.', 'sk' => 'Sem nahraj výsledky krvných testov (PDF alebo fotku). Tvoje súbory sú súkromné a zostávajú tu ako tvoja história, aby sme mohli sledovať, ako sa hodnoty časom menia. Vidí ich len Matteo a Marine Lenehan, naša športová nutričná poradkyňa, ak zaškrtneš políčko: môže sa na ne pozrieť a odpovedať ti priamo tu. Individuálna spolupráca s Marine na tvojej výžive je samostatná služba: ak ťa zaujíma, stačí sa opýtať.'],
        'reply' => ['en' => 'Reply', 'it' => 'Rispondi', 'pt' => 'Responder', 'sl' => 'Odgovori', 'sk' => 'Odpovedať'],
        'send_r' => ['en' => 'Send', 'it' => 'Invia', 'pt' => 'Enviar', 'sl' => 'Pošlji', 'sk' => 'Odoslať'],
        'you' => ['en' => 'You', 'it' => 'Tu', 'pt' => 'Tu', 'sl' => 'Ti', 'sk' => 'Ty'],
        'marine_rep' => ['en' => 'Marine replied about your blood test', 'it' => 'Marine ha risposto sulle tue analisi', 'pt' => 'A Marine respondeu sobre as tuas análises', 'sl' => 'Marine je odgovorila glede tvojih izvidov', 'sk' => 'Marine odpovedala na tvoj krvný test'],
        'matteo_rep' => ['en' => 'Matteo replied about your blood test', 'it' => 'Matteo ha risposto sulle tue analisi', 'pt' => 'O Matteo respondeu sobre as tuas análises', 'sl' => 'Matteo je odgovoril glede tvojih izvidov', 'sk' => 'Matteo odpovedal na tvoj krvný test'],
        'file' => ['en' => 'Choose the file', 'it' => 'Scegli il file', 'pt' => 'Escolhe o ficheiro', 'sl' => 'Izberi datoteko', 'sk' => 'Vybrať súbor'],
        // 19 Nov: a styled file button (the phone's own "Choose File" box ran off the screen and was always in English)
        'pick' => ['en' => 'Choose a PDF or photo', 'it' => 'Scegli un PDF o una foto', 'pt' => 'Escolher um PDF ou foto', 'sl' => 'Izberi PDF ali fotografijo', 'sk' => 'Vybrať PDF alebo fotku'],
        'nofile' => ['en' => 'No file chosen yet', 'it' => 'Nessun file scelto', 'pt' => 'Ainda nenhum ficheiro escolhido', 'sl' => 'Datoteka še ni izbrana', 'sk' => 'Zatiaľ nie je vybraný žiadny súbor'],
        'date' => ['en' => 'Date of the test', 'it' => 'Data delle analisi', 'pt' => 'Data das análises', 'sl' => 'Datum preiskave', 'sk' => 'Dátum testu'],
        'share' => ['en' => 'Share with Marine, our sports nutritionist, so she can take a look', 'it' => 'Condividi con Marine, la nostra nutrizionista sportiva, per un suo parere', 'pt' => 'Partilhar com a Marine, a nossa nutricionista desportiva, para ela dar uma vista de olhos', 'sl' => 'Deli z Marine, našo športno nutricionistko, da jih pregleda', 'sk' => 'Zdieľať s Marine, našou športovou nutričnou poradkyňou, aby sa na to pozrela'],
        'send' => ['en' => 'Upload', 'it' => 'Carica', 'pt' => 'Carregar', 'sl' => 'Naloži', 'sk' => 'Nahrať'],
        'sending' => ['en' => 'Uploading…', 'it' => 'Caricamento…', 'pt' => 'A carregar…', 'sl' => 'Nalaganje…', 'sk' => 'Nahrávam…'],
        'done' => ['en' => 'Uploaded. Thank you!', 'it' => 'Caricato. Grazie!', 'pt' => 'Carregado. Obrigado!', 'sl' => 'Naloženo. Hvala!', 'sk' => 'Nahrané. Ďakujem!'],
        'bad' => ['en' => 'Please choose a PDF or a photo (up to 10 MB).', 'it' => 'Scegli un PDF o una foto (fino a 10 MB).', 'pt' => 'Escolhe um PDF ou uma foto (até 10 MB).', 'sl' => 'Izberi PDF ali fotografijo (do 10 MB).', 'sk' => 'Vyber PDF alebo fotku (do 10 MB).'],
        'err' => ['en' => 'Not uploaded. Please try again.', 'it' => 'Non caricato. Riprova.', 'pt' => 'Não carregado. Tenta de novo.', 'sl' => 'Ni naloženo. Poskusi znova.', 'sk' => 'Nenahralo sa. Skús to znova.'],
        'yours' => ['en' => 'Your uploads', 'it' => 'I tuoi caricamenti', 'pt' => 'Os teus envios', 'sl' => 'Tvoji nalaganja', 'sk' => 'Tvoje nahrané súbory'],
        'open' => ['en' => 'Open', 'it' => 'Apri', 'pt' => 'Abrir', 'sl' => 'Odpri', 'sk' => 'Otvoriť'],
        'del' => ['en' => 'Delete', 'it' => 'Elimina', 'pt' => 'Apagar', 'sl' => 'Izbriši', 'sk' => 'Vymazať'],
        'delq' => ['en' => 'Delete this blood test?', 'it' => 'Eliminare queste analisi?', 'pt' => 'Apagar estas análises?', 'sl' => 'Izbrišem to preiskavo?', 'sk' => 'Vymazať tento krvný test?'],
        'shared' => ['en' => 'shared with Marine', 'it' => 'condivise con Marine', 'pt' => 'partilhadas com a Marine', 'sl' => 'deljeno z Marine', 'sk' => 'zdieľané s Marine'],
    ];
    $l = $GLOBALS['cc_ath_lang'] ?? 'en'; return $W[$k][$l] ?? $W[$k]['en'];
}
function cc_bt_get($pid) { $a = json_decode((string) get_post_meta((int) $pid, 'cc_blood', true), true); return is_array($a) ? $a : []; }
function cc_bt_put($pid, $a) { update_post_meta((int) $pid, 'cc_blood', wp_slash(wp_json_encode(array_values($a)))); }
/* Marine (or any nutritionist): a login with only the 'cc_nutrition' capability. She sees the blood tests athletes chose to share, nothing else. */
add_action('init', function () { if (!get_role('cc_nutritionist')) add_role('cc_nutritionist', 'Nutritionist', ['read' => true, 'cc_nutrition' => true]); });
function cc_bt_is_nutri() { return is_user_logged_in() && current_user_can('cc_nutrition') && !cc_ath_is_coach(); }
add_filter('cc_ath_file_ok', function ($ok, $id) {   // she may open a file only if it is a SHARED blood test
    if ($ok || !cc_bt_is_nutri()) return $ok;
    $pid = wp_get_post_parent_id($id); foreach (cc_bt_get($pid) as $b) if ((int) $b['file'] === (int) $id && !empty($b['share'])) return true;
    return false;
}, 10, 2);
// the conversation under a test: Matteo, Marine and the athlete
function cc_bt_thread($pid, $b, $viewer) {   // $viewer: coach | nutri | athlete
    $o = '';
    foreach ((array) ($b['replies'] ?? []) as $r) {
        $who = $r['from'] ?? 'coach';
        $face = $who === 'athlete' ? (function_exists('cc_ph_widget') ? cc_ph_widget($pid, 30, false, 'nt-me-a') : '')
              : '<img class="nt-me" src="' . esc_url($who === 'nutri' ? 'https://coaching.cigalacycling.com/wp-content/uploads/2026/11/vivify-tile.png' : 'https://coaching.cigalacycling.com/wp-content/uploads/2026/11/cigala-email-matteo-photo.jpg') . '" width="30" height="30" alt="">';
        $label = $who === 'athlete' ? ($viewer === 'athlete' ? cc_bt_w('you') : get_the_title($pid)) : ($who === 'nutri' ? 'Marine' : 'Matteo');
        $o .= '<div class="nt-rep' . ($who === 'athlete' ? ' nt-rep-a' : '') . '"><span class="nt-rh">' . $face . '<b>' . esc_html($label) . '</b> <small>' . esc_html(cc_r_dm((int) $r['at'], true)) . '</small></span><p>' . nl2br(esc_html($r['text'])) . '</p></div>';
    }
    $can = $viewer !== 'nutri' || !empty($b['share']);
    if ($can && ($viewer !== 'athlete' || !empty($b['replies'])))
        $o .= '<details class="nt-replyd"><summary>' . esc_html($viewer === 'athlete' ? cc_bt_w('reply') : 'Reply') . '</summary><div class="bt-r" data-page="' . (int) $pid . '" data-at="' . (int) $b['at'] . '"><textarea rows="3"></textarea><button type="button" class="btn btn-go bt-send">'
            . esc_html($viewer === 'athlete' ? cc_bt_w('send_r') : 'Send') . '</button></div></details>';
    return $o;
}
function cc_bt_row($pid, $b, $forCoach, $viewer = null) {
    $viewer = $viewer ?: ($forCoach ? 'coach' : 'athlete');
    $u = wp_get_attachment_url((int) $b['file']); if (!$u) return '';
    $when = $b['date'] ? cc_r_date(strtotime($b['date'] . ' 12:00')) : cc_r_date((int) $b['at']);
    return '<div class="bt-row"><span class="bt-ic">🩸</span><span class="bt-t"><b>' . esc_html($when) . '</b>' . (!empty($b['share']) ? '<small>' . esc_html($forCoach ? 'shared with the nutritionist' : cc_bt_w('shared')) . '</small>' : '') . '</span>'
         . '<a class="btn btn-ghost" href="' . esc_url($u) . '" target="_blank" rel="noopener">' . esc_html($forCoach ? 'Open' : cc_bt_w('open')) . '</a>'
         . ($viewer === 'nutri' ? '' : '<button type="button" class="bt-del" data-page="' . (int) $pid . '" data-at="' . (int) $b['at'] . '" data-q="' . esc_attr($forCoach ? 'Delete this blood test?' : cc_bt_w('delq')) . '">' . esc_html($forCoach ? 'Delete' : cc_bt_w('del')) . '</button>')
         . '</div><div class="bt-th">' . ($viewer === 'athlete' ? cc_bt_thread($pid, $b, $viewer) : cc_bt_thread_fold($pid, $b, $viewer)) . '</div>';
}
/* Matteo 20 Nov: with 100+ tests and conversations the coach view gets long. Comments fold ("Show comments (N)"), open by themselves only
   when the athlete wrote last (waiting for an answer); tests beyond the newest 5 fold under "Show older tests (N)"; the whole section folds
   (closed when nothing is new, remembered per coach in this browser). The athlete's view is unchanged. */
function cc_bt_waiting($b) { $r = (array) ($b['replies'] ?? []); $l = end($r); return $l && ($l['from'] ?? '') === 'athlete'; }
function cc_bt_new($b) { return cc_bt_waiting($b) || (int) ($b['at'] ?? 0) > (int) get_user_meta(get_current_user_id(), 'cc_blood_seen', true); }
function cc_bt_thread_fold($pid, $b, $viewer) {
    $n = count((array) ($b['replies'] ?? []));
    if (!$n) return cc_bt_thread($pid, $b, $viewer);
    return '<details class="bt-cm"' . (cc_bt_waiting($b) ? ' open' : '') . '><summary><span class="bt-cms">Show comments (' . $n . ')</span><span class="bt-cmh">Hide comments</span>' . (cc_bt_waiting($b) ? ' <span class="bt-new">reply waiting</span>' : '') . '</summary>' . cc_bt_thread($pid, $b, $viewer) . '</details>';
}
function cc_bt_rows_fold($rows, $keep = 5) {   // $rows: html per test, newest first
    if (count($rows) <= $keep) return implode('', $rows);
    return implode('', array_slice($rows, 0, $keep)) . '<details class="bt-older"><summary>Show older tests (' . (count($rows) - $keep) . ')</summary>' . implode('', array_slice($rows, $keep)) . '</details>';
}
function cc_bt_section_fold($key, $list, $body) {   // $list: the tests shown
    $n = count($list); $new = 0; foreach ($list as $b) if (cc_bt_new($b)) $new++;
    return '<details class="bt-fold" data-k="' . esc_attr($key) . '"' . ($new ? ' open data-new="1"' : '') . '><summary><span>' . $n . ' test' . ($n === 1 ? '' : 's') . '</span>' . ($new ? ' <span class="bt-new">' . $new . ' new</span>' : '') . '<span class="bt-fh">Show</span><span class="bt-fs">Hide</span></summary>' . $body . '</details>';
}
function cc_bt_assets($again = false) {   // $again: the food diary review prints them again when Marine's blood list (which printed them) is not shown
    static $done = false; if ($done && !$again) return ''; $done = true;
    $api = esc_url(rest_url('cc/v1/blood')); $nonce = esc_attr(wp_create_nonce('wp_rest'));
    return '<style>html .cc .bt-form{display:grid;grid-template-columns:minmax(0,1fr);gap:12px;max-width:520px}html .cc .bt-form input[type=file]{max-width:100%}html .cc .bt-fw{display:grid;gap:8px;min-width:0}html .cc .bt-fl{font-size:15px;color:#d0d6e0;font-weight:600}html .cc .bt-form label.bt-pick{position:relative;display:inline-flex!important;align-items:center;justify-content:center;justify-self:start;width:auto!important;max-width:100%;min-height:44px;margin:0;padding:10px 18px;font-size:15px;color:#fff;cursor:pointer;white-space:normal;text-align:center}html .cc .bt-pick .bt-file{position:absolute;inset:0;width:100%;height:100%;opacity:0;cursor:pointer;font-size:16px}html .cc .bt-pick:focus-within{outline:2px solid #009a44;outline-offset:2px}html .cc .bt-fn{font-size:15px;color:#b8bec8;overflow-wrap:anywhere;min-width:0}html .cc .bt-fn.on{color:#fff}html .cc .bt-form label{display:grid;gap:6px;font-size:15px;color:#d0d6e0;font-weight:600}'
        . 'html .cc .bt-form input[type=file]{font:16px var(--body);color:#d0d6e0}html .cc .bt-tick{display:flex!important;align-items:flex-start;gap:12px;font-weight:500!important;white-space:normal;line-height:1.45;min-height:44px;padding:8px 0;cursor:pointer}html .cc .bt-tick input{flex:none;width:24px;height:24px;margin:0;accent-color:#12a150}html .cc .bt-tick span{flex:1;min-width:0;overflow-wrap:anywhere}'
        . 'html .cc .bt-form input[type=date]{width:100%;max-width:230px;box-sizing:border-box;padding:10px 12px;font:16px var(--body);border-radius:10px}'
        . 'html .cc .bt-form .btn{justify-self:start;width:auto;margin:0}html .cc .bt-msg{font-size:15px;font-weight:600;color:#2bd47a;margin:0}html .cc .bt-msg.err{color:#ff7a73}html .cc .bt-msg:empty{display:none}'
        . 'html .cc .bt-row{display:flex;align-items:center;gap:12px;padding:10px 12px;margin:8px 0 0;border-radius:12px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.03)}'
        . 'html .cc .bt-ic{font-size:20px}html .cc .bt-t{display:grid;flex:1;min-width:0}html .cc .bt-t b{color:#fff;font-size:16px}html .cc .bt-t small{color:#b8bec8;font-size:14px}'
        . 'html .cc .bt-row .btn{width:auto;margin:0;padding:8px 14px}html .cc .bt-del{background:none;border:0;color:#b8bec8;text-decoration:underline;font-size:15px;cursor:pointer;padding:0 8px;min-height:44px;min-width:44px}'
        . 'html .cc .bt-th{margin:0 0 6px 14px}html .cc .bt-r{display:grid;gap:8px}html .cc .bt-r textarea{width:100%;box-sizing:border-box;font:16px var(--body);padding:10px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.18);background:#0b0d0f;color:#fff}html .cc .bt-r .btn{justify-self:start;width:auto;margin:0}'
        . 'html .cc .bt-fold>summary,html .cc .bt-older>summary,html .cc .bt-cm>summary{cursor:pointer;min-height:44px;display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;list-style:none}html .cc .bt-fold>summary::-webkit-details-marker,html .cc .bt-older>summary::-webkit-details-marker,html .cc .bt-cm>summary::-webkit-details-marker{display:none}'
        . 'html .cc .bt-fold>summary{color:#e6e9ee;font-size:16px;font-weight:600;padding:4px 0}html .cc .bt-fold>summary .bt-fh,html .cc .bt-fold>summary .bt-fs{margin-left:auto;color:#2bd47a;font-size:15px}html .cc .bt-fold[open]>summary .bt-fh,html .cc .bt-fold:not([open])>summary .bt-fs{display:none}'
        . 'html .cc .bt-new{display:inline-block;padding:1px 10px;border-radius:999px;background:rgba(18,161,80,.2);border:1px solid rgba(43,212,122,.5);color:#c9f3da;font-size:14px;font-weight:700}'
        . 'html .cc .bt-older{margin:8px 0 0}html .cc .bt-older>summary,html .cc .bt-cm>summary{color:#2bd47a;font-size:15px;font-weight:600}html .cc .bt-cm[open]>summary .bt-cms,html .cc .bt-cm:not([open])>summary .bt-cmh{display:none}</style>'
        . '<script>(function(){function k(d){return "ccBtFold:"+d.dataset.k;}document.querySelectorAll("details.bt-fold").forEach(function(d){if(!d.dataset.new){try{var v=localStorage.getItem(k(d));if(v==="1"){d.open=true;}}catch(x){}}d.addEventListener("toggle",function(){try{localStorage.setItem(k(d),d.open?"1":"0");}catch(x){}});});})();</script>'
        . '<script>document.addEventListener("click",function(e){var b=e.target.closest(".bt-send");if(!b)return;var r=b.closest(".bt-r"),t=r.querySelector("textarea");if(!t.value.trim())return;b.disabled=true;var d=new FormData();d.append("page",r.dataset.page);d.append("at",r.dataset.at);d.append("text",t.value);'
        . 'fetch("' . esc_url(rest_url('cc/v1/blood-reply')) . '",{method:"POST",body:d,credentials:"same-origin",headers:{"X-WP-Nonce":"' . $nonce . '"}}).then(function(x){if(!x.ok)throw 0;location.reload();}).catch(function(){b.disabled=false;alert("Not sent. Please try again.");});});</script>'
        . '<script>(function(){var f=document.querySelector(".bt-form");if(f){var m=f.querySelector(".bt-msg"),W=JSON.parse(f.dataset.w),fn=f.querySelector(".bt-fn"),fz=f.querySelector("input[type=file]");'
        . 'if(fn&&fz){var n0=fn.textContent;fz.addEventListener("change",function(){var x=fz.files&&fz.files[0];fn.textContent=x?x.name:n0;fn.classList.toggle("on",!!x);});}f.addEventListener("submit",function(e){e.preventDefault();'
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
        $rows = array_map(function ($b) use ($view) { return cc_bt_row($view, $b, true); }, $list);
        return $html . '<section class="ath-s bt" id="blood"><h2>' . cc_ath_icon('sweat', 'ath-hic') . 'Blood tests</h2>' . cc_bt_section_fold('p' . (int) $view, $list, cc_bt_rows_fold($rows)) . '</section>' . cc_bt_assets();
    }
    $W = ['bad' => cc_bt_w('bad'), 'sending' => cc_bt_w('sending'), 'done' => cc_bt_w('done'), 'err' => cc_bt_w('err')];
    $o = '<section class="ath-s bt" id="blood"><h2>' . cc_ath_icon('sweat', 'ath-hic') . esc_html(cc_bt_w('title')) . '</h2><p class="av-lede">' . esc_html(cc_bt_w('lede')) . '</p>'
       . '<form class="bt-form" data-w="' . esc_attr(wp_json_encode($W)) . '"><div class="bt-fw"><span class="bt-fl" id="bt-fl">' . esc_html(cc_bt_w('file')) . '</span>'
       . '<label class="btn btn-ghost bt-pick"><input type="file" class="bt-file" accept="application/pdf,image/*" aria-labelledby="bt-fl"><span>' . esc_html(cc_bt_w('pick')) . '</span></label>'
       . '<span class="bt-fn" aria-live="polite">' . esc_html(cc_bt_w('nofile')) . '</span></div>'
       . '<label>' . esc_html(cc_bt_w('date')) . '<input type="date" max="' . esc_attr(current_time('Y-m-d')) . '"></label>'
       . '<label class="bt-tick"><input type="checkbox"><span>' . esc_html(cc_bt_w('share')) . '</span></label><button type="submit" class="btn btn-go">' . esc_html(cc_bt_w('send')) . '</button><p class="bt-msg" role="status"></p></form>';
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
    foreach ($all as [$p, $b]) $o .= '<div class="nt-who">' . (function_exists('cc_ph_face') ? cc_ph_face($p->ID, 30) . ' ' : '') . '<b><a style="color:#fff" href="' . esc_url(add_query_arg('view', $p->ID, home_url('/' . CC_ATH_SLUG . '/'))) . '#blood">' . esc_html($p->post_title) . '</a></b>' . '</div>' . cc_bt_row($p->ID, $b, true);
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
        // Matteo 18 Nov: a shared test also reaches the nutritionist (email, plus her phone if she turned notifications on)
        if ($r->get_param('share')) foreach (get_users(['role' => 'cc_nutritionist']) as $n) {
            if (function_exists('cc_push_user')) cc_push_user($n->ID, '🩸 Blood test shared by ' . get_the_title($pid), 'Open it in the hub and reply there.', home_url('/' . CC_ATH_SLUG . '/'), 'cc-blood');
            $to = strpos(home_url(), '//staging.') !== false ? (string) get_option('cc_staging_notify', '') : $n->user_email;   // staging: never a real person
            if (is_email($to) && function_exists('cc_ath_mail_shell')) { $GLOBALS['cc_ath_lang'] = 'en';
                wp_mail($to, 'New blood test shared with you: ' . get_the_title($pid), cc_ath_mail_shell('Hi ' . esc_html($n->first_name ?: $n->display_name) . ',', esc_html(get_the_title($pid)) . ' has shared a new blood test with you in the Cigala Cycling Coaching hub. Open it there and reply under it: the athlete and Matteo will see your reply.', 'Open the hub', home_url('/' . CC_ATH_SLUG . '/'), '', 'Thank you,', 'Nutrition'),
                        ['Content-Type: text/html; charset=UTF-8', 'From: Matteo Cigala <coaching@cigalacycling.com>', 'Reply-To: Matteo Cigala <matteo@cigalacycling.com>']); }
        }
        return ['ok' => true];
    }]);
    register_rest_route('cc/v1', '/blood-delete', ['methods' => 'POST', 'permission_callback' => $own, 'callback' => function (WP_REST_Request $r) {
        $pid = (int) ($r->get_param('page') ?: cc_ath_page_of(get_current_user_id())); $at = (int) $r->get_param('at'); $a = cc_bt_get($pid);
        foreach ($a as $k => $b) if ((int) $b['at'] === $at) { wp_delete_attachment((int) $b['file'], true); unset($a[$k]); cc_bt_put($pid, $a); return ['ok' => true]; }
        return new WP_Error('cc_none', 'Not found', ['status' => 404]);
    }]);
});
/* Marine's own view of the hub: the blood tests shared with her, newest first, with the conversation under each */
add_filter('cc_ath_nutritionist', function ($html, $me) {
    if (!user_can($me, 'cc_nutrition')) return $html;
    $GLOBALS['cc_ath_lang'] = 'en'; $all = [];
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'meta_key' => 'cc_blood']) as $p)
        if (get_post_meta($p->ID, 'cc_user', true)) foreach (cc_bt_get($p->ID) as $b) if (!empty($b['share'])) $all[] = [$p, $b];
    usort($all, function ($a, $b) { return $b[1]['at'] <=> $a[1]['at']; });
    $o = '<section class="ath-s"><p class="eyebrow">Cigala Cycling Coaching · nutrition</p><h1>Hi ' . esc_html($me->first_name ?: $me->display_name) . '</h1>'
       . '<p class="av-lede">Blood tests Matteo\'s athletes chose to share with you, newest first. Open the file, then reply under it: the athlete and Matteo see your reply in the hub.</p>'
       . '<p><a class="btn btn-ghost" href="' . esc_url(wp_logout_url(home_url('/' . CC_ATH_SLUG . '/'))) . '">Log out</a></p>';
    if (!$all) $o .= '<p class="av-lede">Nothing shared yet. You will get an email when an athlete shares a blood test with you.</p>';
    foreach ($all as [$p, $b]) $o .= '<div class="nt-who">' . (function_exists('cc_ph_face') ? cc_ph_face($p->ID, 30) . ' ' : '') . '<b>' . esc_html($p->post_title) . '</b>' . '</div>' . cc_bt_row($p->ID, $b, false, 'nutri');
    return $html . $o . '</section>' . cc_bt_assets() . (function_exists('cc_nt_css') ? cc_nt_css() : '') . (function_exists('cc_ph_assets') ? cc_ph_assets() : '');
}, 10, 2);
add_action('rest_api_init', function () {
    // a reply under a test: Matteo, the nutritionist (shared tests only) or the athlete (own tests)
    register_rest_route('cc/v1', '/blood-reply', ['methods' => 'POST', 'permission_callback' => 'is_user_logged_in', 'callback' => function (WP_REST_Request $r) {
        $pid = (int) $r->get_param('page'); $at = (int) $r->get_param('at'); $text = trim(sanitize_textarea_field((string) $r->get_param('text')));
        if ($text === '' || mb_strlen($text) > 3000) return new WP_Error('cc_bad', 'Empty or too long', ['status' => 400]);
        $from = cc_ath_is_coach() ? 'coach' : (cc_bt_is_nutri() ? 'nutri' : ((int) cc_ath_page_of(get_current_user_id()) === $pid ? 'athlete' : ''));
        if ($from === '') return new WP_Error('cc_no', 'Not allowed', ['status' => 403]);
        $a = cc_bt_get($pid);
        foreach ($a as $k => $b) {
            if ((int) $b['at'] !== $at) continue;
            if ($from === 'nutri' && empty($b['share'])) return new WP_Error('cc_no', 'Not shared', ['status' => 403]);
            $a[$k]['replies'][] = ['at' => time(), 'from' => $from, 'text' => $text]; cc_bt_put($pid, $a);
            $uid = (int) get_post_meta($pid, 'cc_user', true); $url = home_url('/' . CC_ATH_SLUG . '/') . '#blood';
            if ($from !== 'athlete' && $uid && function_exists('cc_push_user')) { $keep = $GLOBALS['cc_ath_lang'] ?? 'en'; $GLOBALS['cc_ath_lang'] = cc_ath_user_lang($uid);
                cc_push_user($uid, cc_bt_w($from === 'nutri' ? 'marine_rep' : 'matteo_rep'), wp_trim_words($text, 18), $url, 'cc-blood-' . $at);
                // Matteo 18 Nov: and an email, so a reply about their blood test is never missed
                $au = get_userdata($uid); $to = strpos(home_url(), '//staging.') !== false ? (string) get_option('cc_staging_notify', '') : ($au ? $au->user_email : '');
                if (is_email($to) && function_exists('cc_ath_mail_shell'))
                    wp_mail($to, cc_bt_w($from === 'nutri' ? 'marine_rep' : 'matteo_rep'), cc_ath_mail_shell(sprintf(cc_L('Hi %s,', 'Ciao %s,'), esc_html($au->first_name ?: $au->display_name)), nl2br(esc_html($text)), cc_bt_w('open'), $url),
                            ['Content-Type: text/html; charset=UTF-8', 'From: Matteo Cigala <coaching@cigalacycling.com>', 'Reply-To: Matteo Cigala <matteo@cigalacycling.com>']);
                $GLOBALS['cc_ath_lang'] = $keep; }
            if ($from === 'athlete' && !empty($b['share'])) foreach (get_users(['role' => 'cc_nutritionist']) as $nu) {   // the athlete answered: the nutritionist gets an email
                $to = strpos(home_url(), '//staging.') !== false ? (string) get_option('cc_staging_notify', '') : $nu->user_email; $GLOBALS['cc_ath_lang'] = 'en';
                if (is_email($to) && function_exists('cc_ath_mail_shell')) wp_mail($to, get_the_title($pid) . ' replied on a blood test', cc_ath_mail_shell('Hi ' . esc_html($nu->first_name ?: $nu->display_name) . ',', '<b>' . esc_html(get_the_title($pid)) . '</b> wrote: ' . nl2br(esc_html($text)), 'Open the hub', home_url('/' . CC_ATH_SLUG . '/'), '', 'Thank you,', 'Nutrition'),
                    ['Content-Type: text/html; charset=UTF-8', 'From: Matteo Cigala <coaching@cigalacycling.com>', 'Reply-To: Matteo Cigala <matteo@cigalacycling.com>']);
            }
            if ($from !== 'coach' && function_exists('cc_push_coaches')) cc_push_coaches(($from === 'nutri' ? 'Marine' : get_the_title($pid)) . ' on a blood test (' . get_the_title($pid) . ')', wp_trim_words($text, 18), add_query_arg('board', 'blood', home_url('/' . CC_ATH_SLUG . '/')), 'cc-blood', $pid);
            if ($from === 'athlete' && !empty($b['share'])) foreach (get_users(['role' => 'cc_nutritionist']) as $n) if (function_exists('cc_push_user')) cc_push_user($n->ID, get_the_title($pid) . ' replied on a blood test', wp_trim_words($text, 18), home_url('/' . CC_ATH_SLUG . '/'), 'cc-blood');
            return ['ok' => true];
        }
        return new WP_Error('cc_none', 'Not found', ['status' => 404]);
    }]);
    // Matteo: create a nutritionist login and (send=1) email her the "choose your password" link
    register_rest_route('cc/v1', '/nutritionist', ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        $email = sanitize_email((string) $r['email']); if (!is_email($email)) return new WP_Error('cc_bad', 'Email needed', ['status' => 400]);
        $u = get_user_by('email', $email);
        if (!$u) { $id = wp_insert_user(['user_login' => sanitize_user(strstr($email, '@', true) . '-nutrition', true), 'user_email' => $email, 'user_pass' => wp_generate_password(24),
                                         'first_name' => sanitize_text_field((string) $r['first']), 'last_name' => sanitize_text_field((string) $r['last']), 'display_name' => trim($r['first'] . ' ' . $r['last']), 'role' => 'cc_nutritionist']);
            if (is_wp_error($id)) return $id; $u = get_userdata($id); }
        elseif (!user_can($u, 'cc_nutrition')) return new WP_Error('cc_exists', 'That email already belongs to another account', ['status' => 409]);
        $out = ['user' => $u->ID, 'login' => $u->user_login];
        if ($r['send']) {
            $key = get_password_reset_key($u); if (is_wp_error($key)) return $key;
            $link = add_query_arg(['cc_set' => $key, 'u' => rawurlencode($u->user_login)], home_url('/' . CC_ATH_SLUG . '/'));
            $GLOBALS['cc_ath_lang'] = 'en';
            $h = cc_ath_mail_shell('Hi ' . esc_html($u->first_name ?: $u->display_name) . ',', 'Matteo has set up your login to the Cigala Cycling Coaching hub. Here you will see the blood tests his athletes choose to share with you, and you can reply to each of them right there.',
                                   'Choose your password', $link, '<p style="margin:22px 0 10px;font-size:16px;color:#454a52">You log in with <strong>' . esc_html($u->user_email) . '</strong>. The button works for 7 days; after that, use “Forgot your password?” on the login page.</p>', 'Thank you,', 'Nutrition');
            $out['sent'] = wp_mail($u->user_email, 'Your Cigala Cycling Coaching hub login', $h, ['Content-Type: text/html; charset=UTF-8', 'From: Matteo Cigala <coaching@cigalacycling.com>', 'Reply-To: Matteo Cigala <matteo@cigalacycling.com>']);
        }
        return $out;
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
