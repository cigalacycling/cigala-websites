<?php
if (!defined('ABSPATH')) return;
/* "Leave me a note" (Matteo, 17 Nov 2026): next to My availability, the athlete types or records a voice note for Matteo
 * ("this week I feel…, I didn't sleep well…"), instead of a catch-up call. Up to 5 minutes; the words are written out while
 * they speak (browser speech-to-text, nothing sent anywhere else). Matteo gets each note by email with the recording attached,
 * and a "Notes" board. Stored privately on the athlete page (meta cc_notes, newest last, at most 60; audio in uploads/cc-private). */

function cc_nt_w($k) {
    static $W = [
        'title' => ['en' => 'Leave me a note', 'it' => 'Lasciami un messaggio', 'pt' => 'Deixa-me uma mensagem', 'sl' => 'Pusti mi sporočilo'],
        'lede' => ['en' => 'How is your week going? How you feel, your sleep, work, a niggle… Type it, or record a voice note (up to 5 minutes). I listen to every one.',
                   'it' => 'Come va la settimana? Come ti senti, il sonno, il lavoro, un piccolo fastidio… Scrivilo, oppure registra un messaggio vocale (fino a 5 minuti). Li ascolto tutti.',
                   'pt' => 'Como está a correr a tua semana? Como te sentes, o sono, o trabalho, uma pequena dor… Escreve, ou grava uma mensagem de voz (até 5 minutos). Ouço todas.',
                   'sl' => 'Kako gre tvoj teden? Kako se počutiš, spanec, služba, kakšna bolečina… Napiši ali posnemi glasovno sporočilo (do 5 minut). Poslušam vsakega.'],
        'ph' => ['en' => 'Your note…', 'it' => 'Il tuo messaggio…', 'pt' => 'A tua mensagem…', 'sl' => 'Tvoje sporočilo…'],
        'rec' => ['en' => 'Record a voice note', 'it' => 'Registra un vocale', 'pt' => 'Gravar mensagem de voz', 'sl' => 'Posnemi glasovno sporočilo'],
        'stop' => ['en' => 'Stop recording', 'it' => 'Ferma la registrazione', 'pt' => 'Parar a gravação', 'sl' => 'Ustavi snemanje'],
        'listening' => ['en' => 'Recording… {s} s', 'it' => 'Registrazione… {s} s', 'pt' => 'A gravar… {s} s', 'sl' => 'Snemam… {s} s'],
        'ready' => ['en' => 'Voice note ready ({s} s)', 'it' => 'Vocale pronto ({s} s)', 'pt' => 'Mensagem de voz pronta ({s} s)', 'sl' => 'Glasovno sporočilo pripravljeno ({s} s)'],
        'del' => ['en' => 'Delete', 'it' => 'Elimina', 'pt' => 'Apagar', 'sl' => 'Izbriši'],
        'send' => ['en' => 'Send to Matteo', 'it' => 'Invia a Matteo', 'pt' => 'Enviar ao Matteo', 'sl' => 'Pošlji Matteu'],
        'sending' => ['en' => 'Sending…', 'it' => 'Invio…', 'pt' => 'A enviar…', 'sl' => 'Pošiljam…'],
        'sent' => ['en' => 'Thank you! Your note reached me.', 'it' => 'Grazie! Il tuo messaggio mi è arrivato.', 'pt' => 'Obrigado! A tua mensagem chegou até mim.', 'sl' => 'Hvala! Tvoje sporočilo je prišlo do mene.'],
        'empty' => ['en' => 'Type something or record a voice note first.', 'it' => 'Prima scrivi qualcosa o registra un vocale.', 'pt' => 'Primeiro escreve algo ou grava uma mensagem de voz.', 'sl' => 'Najprej nekaj napiši ali posnemi sporočilo.'],
        'err' => ['en' => 'It did not send. Please try again.', 'it' => 'Non è stato inviato. Riprova.', 'pt' => 'Não foi enviado. Tenta outra vez.', 'sl' => 'Ni bilo poslano. Poskusi znova.'],
        'mic_no' => ['en' => 'Recording isn’t possible in this browser. You can type your note instead.', 'it' => 'In questo browser non si può registrare. Puoi scrivere il messaggio.', 'pt' => 'Não é possível gravar neste navegador. Podes escrever a mensagem.', 'sl' => 'V tem brskalniku snemanje ni mogoče. Sporočilo lahko napišeš.'],
        'mic_denied' => ['en' => 'Allow the microphone to record a voice note.', 'it' => 'Consenti l’uso del microfono per registrare.', 'pt' => 'Permite o microfone para gravar.', 'sl' => 'Dovoli mikrofon za snemanje.'],
    ];
    $l = $GLOBALS['cc_ath_lang'] ?? 'en';
    return $W[$k][$l] ?? $W[$k]['en'];
}
function cc_nt_get($pid) { $a = json_decode((string) get_post_meta($pid, 'cc_notes', true), true); return is_array($a) ? $a : []; }

// the box, right after My availability (availability 10, goals 20)
add_filter('cc_ath_after_reports', function ($html, $view, $coach) {
    if (!$view) return $html;
    if ($coach) {   // Matteo on an athlete's page: their notes, newest first
        $ns = array_reverse(cc_nt_get($view)); if (!$ns) return $html;
        $o = '<section class="ath-s nt" id="notes"><h2>' . cc_ath_icon('mic', 'ath-hic') . 'Notes</h2>';
        foreach (array_slice($ns, 0, 10) as $n) $o .= cc_nt_row($n);
        return $html . $o . '</section>' . cc_nt_css();
    }
    $api = esc_url(rest_url('cc/v1/note')); $nonce = wp_create_nonce('wp_rest');
    $W = []; foreach (['listening', 'ready', 'del', 'rec', 'stop', 'sending', 'sent', 'empty', 'err', 'mic_no', 'mic_denied'] as $k) $W[$k] = cc_nt_w($k);
    $speech = defined('CC_AV_SPEECH') ? (CC_AV_SPEECH[$GLOBALS['cc_ath_lang'] ?? 'en'] ?? 'en-GB') : 'en-GB';
    return $html . '<section class="ath-s nt" id="notes"><h2>' . cc_ath_icon('mic', 'ath-hic') . esc_html(cc_nt_w('title')) . '</h2>'
        . '<p class="av-lede">' . esc_html(cc_nt_w('lede')) . '</p>'
        . '<div id="nt-app" data-api="' . $api . '" data-nonce="' . esc_attr($nonce) . '" data-lang="' . esc_attr($speech) . '" data-w="' . esc_attr(wp_json_encode($W)) . '">'
        . '<textarea id="nt-text" rows="4" maxlength="3000" placeholder="' . esc_attr(cc_nt_w('ph')) . '" aria-label="' . esc_attr(cc_nt_w('title')) . '"></textarea>'
        . '<div class="nt-row"><button type="button" class="btn btn-ghost nt-rec" aria-pressed="false">' . cc_ath_icon('mic', 'nt-ic') . '<span>' . esc_html(cc_nt_w('rec')) . '</span></button>'
        . '<span class="nt-st" role="status"></span></div>'
        . '<button type="button" class="btn btn-go nt-send">' . esc_html(cc_nt_w('send')) . '</button><p class="nt-msg" role="status"></p></div></section>'
        . cc_nt_css() . cc_nt_js();
}, 15, 3);
function cc_nt_row($n) {
    $u = !empty($n['audio']) ? wp_get_attachment_url((int) $n['audio']) : '';
    return '<div class="nt-item"><small>' . esc_html(date_i18n('j M Y, H:i', (int) $n['at'])) . '</small>'
        . ($u ? '<audio controls preload="none" src="' . esc_url($u) . '"></audio>' : '')
        . (($n['text'] ?? '') !== '' ? '<p>' . nl2br(esc_html($n['text'])) . '</p>' : '') . '</div>';
}
function cc_nt_css() {
    return '<style>html .cc .nt #nt-app{display:grid;gap:12px}html .cc .nt textarea{width:100%;min-height:110px;font:16px var(--body);padding:12px 14px;border-radius:12px;border:1px solid rgba(255,255,255,.2);background:#0b0d0f;color:#fff;box-sizing:border-box}'
        . 'html .cc .nt-row{display:flex;flex-wrap:wrap;align-items:center;gap:10px 14px}html .cc .nt-rec{display:inline-flex;align-items:center;gap:10px}html .cc .nt-rec .nt-ic svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:2}'
        . 'html .cc .nt-rec.on{background:#ca212a!important;border-color:#ca212a!important;color:#fff!important;animation:ntpulse 1.2s ease-in-out infinite}@keyframes ntpulse{0%,100%{box-shadow:0 0 0 0 rgba(202,33,42,.6)}50%{box-shadow:0 0 0 8px rgba(202,33,42,0)}}'
        . 'html .cc .nt-st{font-size:15px;color:#d0d6e0}html .cc .nt-st button{background:none;border:0;color:#ff7a73;text-decoration:underline;font:inherit;cursor:pointer;padding:0;margin-left:8px}'
        . 'html .cc .nt .nt-send{justify-self:start}html .cc .nt-msg{margin:0;font-size:16px;font-weight:600;color:#34c46a}html .cc .nt-msg.err{color:#ff7a73}html .cc .nt-msg:empty{display:none}'
        . 'html .cc .nt-item{padding:12px 0;border-top:1px solid rgba(255,255,255,.1)}html .cc .nt-item small{color:#b8bec8;font-size:15px}html .cc .nt-item audio{display:block;width:100%;max-width:420px;margin:8px 0}html .cc .nt-item p{margin:6px 0 0;font-size:16px;color:#e6e9ee}</style>';
}
function cc_nt_js() {
    return <<<'JS'
<script>(function(){var A=document.getElementById('nt-app');if(!A)return;var W=JSON.parse(A.dataset.w),L=A.dataset.lang,ta=document.getElementById('nt-text'),
b=A.querySelector('.nt-rec'),st=A.querySelector('.nt-st'),go=A.querySelector('.nt-send'),m=A.querySelector('.nt-msg'),rec=null,sr=null,chunks=[],blob=null,base='',t0=0,tick=null;
function msg(t,e){m.textContent=t||'';m.classList.toggle('err',!!e);}
function lab(t){b.querySelector('span').textContent=t;}
b.addEventListener('click',function(){if(rec){rec.stop();return;}msg('');
 if(!navigator.mediaDevices||!window.MediaRecorder){msg(W.mic_no,true);return;}
 navigator.mediaDevices.getUserMedia({audio:true}).then(function(s){
  var type=['audio/webm;codecs=opus','audio/mp4','audio/webm'].filter(function(t){return MediaRecorder.isTypeSupported&&MediaRecorder.isTypeSupported(t);})[0];
  rec=new MediaRecorder(s,type?{mimeType:type,audioBitsPerSecond:32000}:undefined);chunks=[];rec.ondataavailable=function(e){if(e.data.size)chunks.push(e.data);};
  rec.onstop=function(){s.getTracks().forEach(function(t){t.stop();});blob=new Blob(chunks,{type:rec.mimeType||'audio/mp4'});rec=null;if(sr)try{sr.stop();}catch(x){}
   clearInterval(tick);b.classList.remove('on');b.setAttribute('aria-pressed','false');lab(W.rec);
   st.textContent=W.ready.replace('{s}',Math.round((Date.now()-t0)/1000));var x=document.createElement('button');x.type='button';x.textContent=W.del;x.onclick=function(){blob=null;st.textContent='';};st.appendChild(x);};
  rec.start(1000);t0=Date.now();b.classList.add('on');b.setAttribute('aria-pressed','true');lab(W.stop);
  tick=setInterval(function(){var n=Math.round((Date.now()-t0)/1000);st.textContent=W.listening.replace('{s}',n);if(n>=300&&rec)rec.stop();},500);
  var SR=window.SpeechRecognition||window.webkitSpeechRecognition;base=ta.value?ta.value.replace(/\s*$/,'')+'\n':'';
  if(SR){sr=new SR();sr.lang=L;sr.continuous=true;sr.interimResults=true;
   sr.onresult=function(e){var t='';for(var i=0;i<e.results.length;i++)t+=e.results[i][0].transcript;ta.value=base+t.trim();};
   sr.onend=function(){if(rec)try{sr.start();}catch(x){}};sr.onerror=function(){};try{sr.start();}catch(x){}}
 }).catch(function(){msg(W.mic_denied,true);});});
go.addEventListener('click',function(){if(rec){rec.stop();}var txt=ta.value.trim();if(!txt&&!blob){msg(W.empty,true);return;}
 go.disabled=true;msg(W.sending);var f=new FormData();f.append('text',txt);if(blob){f.append('audio',blob,'voice.'+(/mp4/.test(blob.type)?'m4a':'webm'));f.append('transcript',txt.slice(base.length));}
 fetch(A.dataset.api,{method:'POST',body:f,credentials:'same-origin',headers:{'X-WP-Nonce':A.dataset.nonce}}).then(function(r){return r.json().then(function(j){return[r.ok,j];});})
 .then(function(x){if(!x[0])throw new Error();ta.value='';blob=null;base='';st.textContent='';msg(W.sent);go.disabled=false;})
 .catch(function(){go.disabled=false;msg(W.err,true);});});
})();</script>
JS;
}

/* ---------- saving: POST /wp-json/cc/v1/note (the athlete; FormData text, audio, transcript) ---------- */
add_action('rest_api_init', function () {
    register_rest_route('cc/v1', '/note', ['methods' => 'POST', 'callback' => 'cc_nt_save', 'permission_callback' => function () { return is_user_logged_in() && (bool) cc_ath_page_of(get_current_user_id()) && !cc_ath_is_coach(); }]);
    register_rest_route('cc/v1', '/notes', ['methods' => 'GET', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function () {   // Matteo's laptop: everyone's notes
        $out = []; foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'meta_key' => 'cc_notes']) as $p)
            foreach (cc_nt_get($p->ID) as $n) $out[] = ['page' => $p->ID, 'athlete' => $p->post_title, 'at' => $n['at'], 'text' => $n['text'] ?? '', 'audio' => !empty($n['audio']) ? wp_get_attachment_url((int) $n['audio']) : null];
        usort($out, function ($a, $b) { return $b['at'] <=> $a['at']; }); return $out;
    }]);
});
function cc_nt_save(WP_REST_Request $r) {
    $uid = get_current_user_id(); $pid = cc_ath_page_of($uid);
    $ns = cc_nt_get($pid); $today = 0; foreach ($ns as $n) if ($n['at'] > time() - DAY_IN_SECONDS) $today++;
    if ($today >= 10) return new WP_Error('cc_many', 'Too many notes today.', ['status' => 429]);
    $text = cc_av_note((string) $r->get_param('text'), 3000); $aid = 0;
    $files = $r->get_file_params();
    if (!empty($files['audio']['tmp_name'])) { $aid = cc_av_store_audio($files['audio'], $pid, cc_av_str($r->get_param('transcript'), 2000)); if (is_wp_error($aid)) return $aid; }
    if ($text === '' && !$aid) return new WP_Error('cc_empty', 'Empty note', ['status' => 400]);
    $n = ['at' => time(), 'text' => $text, 'audio' => (int) $aid]; $ns[] = $n;
    update_post_meta($pid, 'cc_notes', wp_slash(wp_json_encode(array_slice($ns, -60)))); update_post_meta($pid, 'cc_notes_updated', time());
    cc_nt_mail($pid, $uid, $n);
    return ['ok' => true];
}
function cc_nt_mail($pid, $uid, $n) {
    if (!function_exists('cc_av_notify_to') || !cc_av_notify_to()) return;
    $u = get_userdata($uid); $name = get_the_title($pid); $board = add_query_arg('board', 'notes', home_url('/' . CC_ATH_SLUG . '/'));
    $h = '<div style="font-family:Montserrat,Helvetica,Arial,sans-serif;font-size:16px;color:#222"><h2>Note from ' . esc_html($name) . '</h2>'
       . ($n['audio'] ? '<p style="margin:0 0 10px"><b>🎙 Voice note attached</b>: open the attachment to listen.</p>' : '')
       . ($n['text'] !== '' ? '<blockquote style="margin:0 0 16px;padding:10px 14px;background:#f2f4f3;border-left:3px solid #009a44;white-space:pre-line">' . esc_html($n['text']) . '</blockquote>' : '')
       . '<p style="margin:20px 0 0"><a href="' . esc_url($board) . '" style="display:inline-block;padding:12px 20px;border-radius:8px;background:#009a44;color:#fff;font-weight:600;text-decoration:none">Open all notes</a></p></div>';
    $hd = ['Content-Type: text/html; charset=UTF-8']; if ($u && is_email($u->user_email)) $hd[] = 'Reply-To: ' . $name . ' <' . $u->user_email . '>';
    if (function_exists('cc_ath_coach_wrap')) $h = cc_ath_coach_wrap($h);
    $att = $n['audio'] ? [get_attached_file((int) $n['audio'])] : [];
    wp_mail(cc_av_notify_to(), 'Note from ' . $name . ($n['audio'] ? ' (voice)' : ''), $h, $hd, array_filter($att));
}

/* ---------- Matteo's board: /athletes/?board=notes ---------- */
add_filter('cc_ath_coach_links', function ($html) {
    $seen = (int) get_user_meta(get_current_user_id(), 'cc_notes_seen', true); $n = 0;
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'meta_key' => 'cc_notes_updated', 'fields' => 'ids']) as $p)
        foreach (cc_nt_get($p) as $x) if ($x['at'] > $seen) $n++;
    return $html . '<a class="av-boardlink" href="' . esc_url(add_query_arg('board', 'notes', home_url('/' . CC_ATH_SLUG . '/'))) . '">Notes' . ($n ? ' <span class="av-badge">' . $n . ' new</span>' : '') . '</a>';
}, 12);
add_filter('cc_ath_board', function ($html, $board) {
    if ($board !== 'notes' || !cc_ath_is_coach()) return $html;
    add_action('shutdown', function () { update_user_meta(get_current_user_id(), 'cc_notes_seen', time()); });
    $all = [];
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'meta_key' => 'cc_notes_updated']) as $p) foreach (cc_nt_get($p->ID) as $n) $all[] = [$p, $n];
    usort($all, function ($a, $b) { return $b[1]['at'] <=> $a[1]['at']; });
    $o = '<section class="ath-s nt"><h2>' . cc_ath_icon('mic', 'ath-hic') . 'Notes</h2><p class="av-lede">Notes and voice notes from your athletes, newest first. Each one also came to you by email, the recording attached.</p>';
    if (!$all) return $o . '<p class="av-lede">No notes yet.</p></section>' . cc_nt_css();
    foreach (array_slice($all, 0, 80) as [$p, $n]) $o .= '<div class="nt-item"><b><a style="color:#fff" href="' . esc_url(add_query_arg('view', $p->ID, home_url('/' . CC_ATH_SLUG . '/'))) . '">' . esc_html($p->post_title) . '</a></b>' . (function_exists('cc_ath_flag_for') ? cc_ath_flag_for($p->ID) : '') . substr(cc_nt_row($n), strlen('<div class="nt-item">'));
    return $o . '</section>' . cc_nt_css();
}, 10, 2);
