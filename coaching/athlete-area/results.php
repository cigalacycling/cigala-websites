<?php
if (!defined('ABSPATH')) return;
/* "Share a result" (Matteo, 17 Nov 2026): the athlete shares a photo and a few words about a result or a proud moment, optionally
 * tied to one of their races, with a tick "Cigala Cycling may share this on social media and Skool". Private between them and
 * Matteo (stored on their page, photo in uploads/cc-private). Matteo gets an email (photo attached) and a phone notification,
 * reacts (👏 🔥 💪 🏆) and/or replies on his Results board; the athlete sees it under their result and gets a phone notification.
 * Their results build a small trophy shelf in their hub. Page meta cc_results (newest last, at most 80). */

function cc_rs_w($k) {
    static $W = [
        'title' => ['en' => 'Share a result', 'it' => 'Condividi un risultato', 'pt' => 'Partilha um resultado', 'sl' => 'Deli rezultat', 'sk' => 'Pochváľ sa výsledkom'],
        'lede' => ['en' => 'A race result, a personal best, a ride you are proud of: share it with a photo. I love seeing them.',
                   'it' => 'Un risultato in gara, un record personale, un’uscita di cui sei fiero: condividilo con una foto. Mi piace vederli.',
                   'pt' => 'Um resultado em prova, um recorde pessoal, um treino de que te orgulhas: partilha-o com uma foto. Adoro vê-los.',
                   'sl' => 'Rezultat na tekmi, osebni rekord, vožnja, na katero si ponosen: deli jo s fotografijo. Rad jih vidim.', 'sk' => 'Výsledok z pretekov, osobný rekord, jazda, ktorá ťa teší: podeľ sa o ňu s fotkou. Rád sa na ne pozriem.'],
        'photo' => ['en' => 'Add a photo', 'it' => 'Aggiungi una foto', 'pt' => 'Adicionar uma foto', 'sl' => 'Dodaj fotografijo', 'sk' => 'Pridať fotku'],
        'date' => ['en' => 'Date', 'it' => 'Data', 'pt' => 'Data', 'sl' => 'Datum', 'sk' => 'Dátum'],   // 19 Nov: a visible label on the date box
        'change' => ['en' => 'Change the photo', 'it' => 'Cambia la foto', 'pt' => 'Mudar a foto', 'sl' => 'Zamenjaj fotografijo', 'sk' => 'Zmeniť fotku'],
        'ph' => ['en' => 'What happened? e.g. 3rd in my category, first 100 km, new 20-min power', 'it' => 'Cosa è successo? es. 3° di categoria, primi 100 km, nuovo record sui 20 minuti',
                 'pt' => 'O que aconteceu? ex. 3.º no escalão, primeiros 100 km, novo recorde aos 20 minutos', 'sl' => 'Kaj se je zgodilo? npr. 3. v kategoriji, prvih 100 km, nov rekord na 20 minut', 'sk' => 'Čo sa stalo? napr. 3. miesto v kategórii, prvých 100 km, nový rekord na 20 minút'],
        'race' => ['en' => 'Which race? (optional)', 'it' => 'Quale gara? (facoltativo)', 'pt' => 'Que prova? (opcional)', 'sl' => 'Katera tekma? (neobvezno)', 'sk' => 'Ktoré preteky? (nepovinné)'],
        'none' => ['en' => 'Not a race', 'it' => 'Non è una gara', 'pt' => 'Não é uma prova', 'sl' => 'Ni tekma', 'sk' => 'Nie sú to preteky'],
        'askshare' => ['en' => '📣 Can I share it publicly? (optional)', 'it' => '📣 Posso condividerlo pubblicamente? (facoltativo)', 'pt' => '📣 Posso partilhar publicamente? (opcional)', 'sl' => '📣 Ga lahko delim javno? (neobvezno)', 'sk' => '📣 Môžem to zdieľať verejne? (nepovinné)'],
        'ok' => ['en' => 'Yes, Cigala Cycling may post this on social media and in the Skool community. Leave it unticked to keep it just between us.',
                 'it' => 'Sì, Cigala Cycling può pubblicarlo sui social e nella community Skool. Lascialo vuoto per tenerlo solo tra noi.',
                 'pt' => 'Sim, a Cigala Cycling pode publicar isto nas redes sociais e na comunidade Skool. Deixa por marcar para ficar só entre nós.',
                 'sl' => 'Da, Cigala Cycling lahko to objavi na družbenih omrežjih in v skupnosti Skool. Pusti neoznačeno, da ostane samo med nama.', 'sk' => 'Áno, Cigala Cycling to môže zverejniť na sociálnych sieťach a v komunite Skool. Nechaj nezaškrtnuté, ak to má zostať len medzi nami.'],
        'send' => ['en' => 'Share with Matteo', 'it' => 'Condividi con Matteo', 'pt' => 'Partilhar com o Matteo', 'sl' => 'Deli z Matteom', 'sk' => 'Zdieľať s Matteom'],
        'sending' => ['en' => 'Sending…', 'it' => 'Invio…', 'pt' => 'A enviar…', 'sl' => 'Pošiljam…', 'sk' => 'Posielam…'],
        'sent' => ['en' => 'Brilliant, thank you for sharing!', 'it' => 'Fantastico, grazie per averlo condiviso!', 'pt' => 'Fantástico, obrigado por partilhares!', 'sl' => 'Odlično, hvala, da si delil!', 'sk' => 'Super, vďaka za zdieľanie!'],
        'empty' => ['en' => 'Add a photo or a few words first.', 'it' => 'Prima aggiungi una foto o qualche parola.', 'pt' => 'Primeiro adiciona uma foto ou algumas palavras.', 'sl' => 'Najprej dodaj fotografijo ali nekaj besed.', 'sk' => 'Najprv pridaj fotku alebo pár slov.'],
        'err' => ['en' => 'It did not send. Please try again.', 'it' => 'Non è stato inviato. Riprova.', 'pt' => 'Não foi enviado. Tenta outra vez.', 'sl' => 'Ni bilo poslano. Poskusi znova.', 'sk' => 'Neodoslalo sa. Skús to znova.'],
        'shelf' => ['en' => 'Your trophy shelf', 'it' => 'La tua bacheca', 'pt' => 'A tua vitrine', 'sl' => 'Tvoja vitrina', 'sk' => 'Tvoja vitrína trofejí'],
        'reacted' => ['en' => 'Matteo reacted to your result', 'it' => 'Matteo ha reagito al tuo risultato', 'pt' => 'O Matteo reagiu ao teu resultado', 'sl' => 'Matteo se je odzval na tvoj rezultat', 'sk' => 'Matteo zareagoval na tvoj výsledok'],
        'replied' => ['en' => 'Matteo replied', 'it' => 'Matteo ha risposto', 'pt' => 'O Matteo respondeu', 'sl' => 'Matteo je odgovoril', 'sk' => 'Matteo odpovedal'],
        'del' => ['en' => 'Delete', 'it' => 'Elimina', 'pt' => 'Apagar', 'sl' => 'Izbriši', 'sk' => 'Vymazať'],
        'you' => ['en' => 'You', 'it' => 'Tu', 'pt' => 'Tu', 'sl' => 'Ti', 'sk' => 'Ty'],
        'answer' => ['en' => 'Answer Matteo', 'it' => 'Rispondi a Matteo', 'pt' => 'Responder ao Matteo', 'sl' => 'Odgovori Matteu', 'sk' => 'Odpovedať Matteovi'],
        'ansph' => ['en' => 'Your answer…', 'it' => 'La tua risposta…', 'pt' => 'A tua resposta…', 'sl' => 'Tvoj odgovor…', 'sk' => 'Tvoja odpoveď…'],
        'delq' => ['en' => 'Delete this? It cannot be undone.', 'it' => 'Eliminarlo? Non si può annullare.', 'pt' => 'Apagar? Não é possível desfazer.', 'sl' => 'Izbrišem? Tega ni mogoče razveljaviti.', 'sk' => 'Vymazať? Nedá sa to vrátiť späť.'],
    ];
    $l = $GLOBALS['cc_ath_lang'] ?? 'en'; return $W[$k][$l] ?? $W[$k]['en'];
}
const CC_RS_REACTS = ['heart' => '❤️', 'clap' => '👏', 'fire' => '🔥', 'strong' => '💪', 'trophy' => '🏆'];   // ❤️ also by double-tapping the photo (Matteo 17 Nov)
function cc_rs_get($pid) { $a = json_decode((string) get_post_meta((int) $pid, 'cc_results', true), true); return is_array($a) ? $a : []; }
function cc_rs_files_gone($x) {   // a result's photo, reply photo and every photo/voice note in its conversation
    foreach (['photo', 'reply_photo'] as $f) if (!empty($x[$f])) wp_delete_attachment((int) $x[$f], true);
    foreach ((array) ($x['thread'] ?? []) as $e) foreach (['photo', 'audio'] as $f) if (!empty($e[$f])) wp_delete_attachment((int) $e[$f], true);
}
function cc_rs_put($pid, $a) {   // keeps the newest 80; older ones go, with their photos
    $a = array_values($a);
    foreach (array_slice($a, 0, max(0, count($a) - 80)) as $old) cc_rs_files_gone($old);
    update_post_meta((int) $pid, 'cc_results', wp_slash(wp_json_encode(array_slice($a, -80))));
}
function cc_rs_card($pid, $r, $forCoach) {
    $u = !empty($r['photo']) ? wp_get_attachment_url((int) $r['photo']) : '';
    // coach: double-tap the photo for ❤️ (a corner button opens it full size); athlete: tap opens it
    $ph = $u ? ($forCoach ? '<span class="rs-ph rs-dbl" title="Double-tap to like"><img src="' . esc_url($u) . '" alt="" loading="lazy"><a class="rs-full" href="' . esc_url($u) . '" target="_blank" rel="noopener" aria-label="Open the photo">⤢</a><i class="rs-heart">❤️</i></span>'
                         : '<a href="' . esc_url($u) . '" target="_blank" rel="noopener" class="rs-ph"><img src="' . esc_url($u) . '" alt="" loading="lazy"></a>') : '<span class="rs-ph rs-noph">🏆</span>';
    $o = '<div class="rs-card">' . $ph
       . '<div class="rs-b"><small>' . esc_html(date_i18n('j M Y', strtotime(($r['date'] ?: date('Y-m-d', $r['at'])) . ' 12:00'))) . ($r['race'] !== '' ? ' · ' . esc_html($r['race']) : '') . '</small>'
       . ($r['text'] !== '' ? '<p>' . nl2br(esc_html($r['text'])) . '</p>' : '')
       . ($forCoach ? '<p class="rs-ok">' . ($r['consent'] ? '✅ OK to share on social media / Skool' : '🔒 Private: not for social media') . '</p>' : '');
    if (!empty($r['react'])) $o .= '<p class="rs-react">' . esc_html(CC_RS_REACTS[$r['react']] ?? '') . ' <small>' . esc_html($forCoach ? 'your reaction' : 'Matteo') . '</small></p>';
    // Matteo 17 Nov: the conversation under a result: his replies (his photo) and the athlete's answers (their photo), text, voice, photo
    $thread = (array) ($r['thread'] ?? []);
    if (!empty($r['reply']) || !empty($r['reply_photo'])) array_unshift($thread, ['at' => (int) $r['at'], 'from' => 'coach', 'text' => (string) ($r['reply'] ?? ''), 'photo' => (int) ($r['reply_photo'] ?? 0)]);   // older single reply
    $me = '<img class="nt-me" src="https://coaching.cigalacycling.com/wp-content/uploads/2026/11/cigala-email-matteo-photo.jpg" width="30" height="30" alt="">';
    foreach ($thread as $e) {
        $coachSide = ($e['from'] ?? 'coach') === 'coach';
        $face = $coachSide ? $me : (function_exists('cc_ph_widget') ? cc_ph_widget($pid, 30, false, 'nt-me-a') : '');
        $label = $coachSide ? ($forCoach ? 'You' : cc_rs_w('replied')) : ($forCoach ? get_the_title($pid) : cc_rs_w('you'));
        $ph = !empty($e['photo']) ? wp_get_attachment_url((int) $e['photo']) : ''; $au = !empty($e['audio']) ? wp_get_attachment_url((int) $e['audio']) : '';
        $o .= '<div class="nt-rep' . ($coachSide ? '' : ' nt-rep-a') . '"><span class="nt-rh">' . $face . '<b>' . esc_html($label) . '</b></span>'
            . ($au && function_exists('cc_nt_player') ? cc_nt_player($au) : '') . (($e['text'] ?? '') !== '' ? '<p>' . nl2br(esc_html($e['text'])) . '</p>' : '')
            . ($ph ? '<a href="' . esc_url($ph) . '" target="_blank" rel="noopener"><img class="rs-rimg" src="' . esc_url($ph) . '" alt="" loading="lazy"></a>' : '') . '</div>';
    }
    $speech = defined('CC_AV_SPEECH') ? (CC_AV_SPEECH[$GLOBALS['cc_ath_lang'] ?? 'en'] ?? 'en-GB') : 'en-GB';
    if (function_exists('cc_nt_box')) {
        if ($forCoach) $o .= '<details class="nt-replyd"><summary>🎙 Reply with a voice note</summary>' . cc_nt_box(rest_url('cc/v1/result-reply'), ['page' => $pid, 'at' => (int) $r['at']], 'Your reply…', 'Send reply') . '</details>';
        elseif ($thread) $o .= '<details class="nt-replyd"><summary>' . esc_html(cc_rs_w('answer')) . '</summary>' . cc_nt_box(rest_url('cc/v1/result-reply'), ['page' => $pid, 'at' => (int) $r['at']], cc_rs_w('ansph'), cc_rs_w('send'), false, $speech) . '</details>';
    }
    if ($forCoach) {
        $act = esc_url(rest_url('cc/v1/result-react')); $n = esc_attr(wp_create_nonce('wp_rest'));
        $o .= '<div class="rs-acts" data-api="' . $act . '" data-nonce="' . $n . '" data-page="' . (int) $pid . '" data-at="' . (int) $r['at'] . '">';
        foreach (CC_RS_REACTS as $k => $e) $o .= '<button type="button" class="rs-rx' . (($r['react'] ?? '') === $k ? ' on' : '') . '" data-r="' . $k . '" aria-label="' . $k . '">' . $e . '</button>';
        // Matteo 17 Nov: a photo in the reply too (📷)
        $o .= '<input type="text" class="rs-rep" maxlength="600" placeholder="Reply…" value=""><button type="button" class="rs-cam" aria-label="Add a photo">📷</button><input type="file" accept="image/*" class="rs-cfile" hidden>'
            . '<img class="rs-cprev" alt="" hidden><button type="button" class="btn btn-go rs-send">Send</button></div>';
    }
    $o .= '<button type="button" class="nt-del rs-del" data-api="' . esc_url(rest_url('cc/v1/result-delete')) . '" data-nonce="' . esc_attr(wp_create_nonce('wp_rest')) . '" data-page="' . (int) $pid . '" data-at="' . (int) $r['at'] . '" data-q="' . esc_attr(cc_rs_w('delq')) . '">' . esc_html(cc_rs_w('del')) . '</button>';
    return $o . '</div></div>';
}
function cc_rs_css() {
    static $d = false; if ($d) return ''; $d = true;
    return '<style>html .cc .rs-cam{width:42px;height:42px;min-height:0;padding:0;border-radius:50%;border:1px solid rgba(255,255,255,.2);background:#0b0d0f;font-size:19px;cursor:pointer}'
        . 'html .cc .rs-cprev{width:48px;height:48px;border-radius:8px;object-fit:cover;border:2px solid #2bd47a;cursor:pointer}html .cc .rs-cprev[hidden]{display:none}html .cc .rs-rimg{display:block;max-width:260px;width:100%;border-radius:10px;margin-top:8px}'
        . 'html .cc .rs-dbl{position:relative;cursor:pointer;user-select:none;-webkit-user-select:none;touch-action:manipulation}html .cc .rs-full{position:absolute;right:6px;bottom:6px;width:28px;height:28px;border-radius:8px;background:rgba(0,0,0,.6);color:#fff;display:grid;place-items:center;text-decoration:none;font-size:15px}'
        . 'html .cc .rs-heart{position:absolute;left:50%;top:50%;font-size:56px;font-style:normal;transform:translate(-50%,-50%) scale(0);opacity:0;pointer-events:none}html .cc .rs-heart.go{animation:rsheart .9s ease-out}'
        . '@keyframes rsheart{0%{transform:translate(-50%,-50%) scale(0);opacity:0}25%{transform:translate(-50%,-50%) scale(1.25);opacity:1}55%{transform:translate(-50%,-50%) scale(1);opacity:1}100%{transform:translate(-50%,-50%) scale(1.1);opacity:0}}'
        . 'html .cc .rs-pw{position:relative;display:inline-block}html .cc .rs-x{position:absolute;top:-8px;right:-8px;width:30px;height:30px;min-height:0;padding:0;margin:0;border-radius:50%;border:2px solid #0b0d0f;background:#E10600;color:#fff;font:700 15px/1 var(--body);cursor:pointer}html .cc .rs-x[hidden]{display:none}'
        . 'html .cc .rs-form{display:grid;gap:12px}html .cc .rs-pick{display:flex;align-items:center;gap:0}html .cc .rs-prev{width:96px;height:96px;border-radius:14px;object-fit:cover;border:2px solid #2bd47a;display:none}html .cc .rs-prev.on{display:block}html .cc .rs-pw:has(.rs-prev.on){margin-right:14px}'
        . 'html .cc .rs-form textarea,html .cc .rs-form select,html .cc .rs-form input[type=date]{width:100%;font:16px var(--body);padding:12px 14px;border-radius:12px;border:1px solid rgba(255,255,255,.2);background:#0b0d0f;color:#fff;box-sizing:border-box}'
        // Matteo 17 Nov: the date box stayed wider than the card on iPhones (native date inputs keep their own width)
        . 'html .cc .rs-form input[type=date]{display:block;max-width:100%;min-width:0;-webkit-appearance:none;appearance:none;min-height:48px;line-height:1.2}html .cc .rs-form input[type=date]::-webkit-date-and-time-value{text-align:left}'
        . 'html .cc .rs-form label{display:grid;gap:6px;font-size:15px;color:#d0d6e0;font-weight:600;min-width:0}'
        . 'html .cc .rs-share{padding:12px 14px;border-radius:12px;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.03)}html .cc .rs-share b{display:block;color:#fff;font-size:16px;margin:0 0 8px}'
        . 'html .cc .rs-form .rs-tick{display:flex!important;gap:12px;align-items:flex-start;font-weight:500;font-size:16px;line-height:1.45;color:#e6e9ee;min-height:44px;cursor:pointer}html .cc .rs-tick input{width:26px;height:26px;flex:none;margin:0;accent-color:#12a150}'
        . 'html .cc .rs-form .btn{justify-self:start}html .cc .rs-msg{margin:0;font-size:16px;font-weight:600;color:#34c46a}html .cc .rs-msg.err{color:#ff7a73}html .cc .rs-msg:empty{display:none}'
        . 'html .cc .rs-shelf{display:grid;gap:12px;margin-top:10px}html .cc .rs-card{display:flex;gap:14px;align-items:flex-start;padding:12px;border-radius:14px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.03)}'
        . 'html .cc .rs-ph{flex:none;width:110px;height:110px;border-radius:12px;overflow:hidden;display:grid;place-items:center;background:rgba(18,161,80,.12);font-size:40px}html .cc .rs-ph img{width:100%;height:100%;object-fit:cover}'
        . 'html .cc .rs-b{flex:1;min-width:0}html .cc .rs-b small{color:#b8bec8;font-size:15px}html .cc .rs-b p{margin:6px 0 0;font-size:16px;color:#e6e9ee}html .cc .rs-ok{font-size:15px!important;color:#d0d6e0!important}html .cc .rs-react{font-size:22px!important}'
        . 'html .cc .rs-acts{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:10px}html .cc .rs-rx{width:42px;height:42px;min-height:0;padding:0;border-radius:50%;border:1px solid rgba(255,255,255,.2);background:#0b0d0f;font-size:20px;cursor:pointer}html .cc .rs-rx.on{border-color:#2bd47a;background:rgba(18,161,80,.25)}'
        . 'html .cc .rs-rep{flex:1 1 180px;font:16px var(--body);padding:10px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.2);background:#0b0d0f;color:#fff}html .cc .rs-acts .btn{width:auto;margin:0}'
        // Matteo 17 Nov: the photo stays beside the text on phones too (not on top); tap opens it full size
        . '@media (max-width:560px){html .cc .rs-card{gap:12px;padding:10px}html .cc .rs-ph{width:84px;height:84px;font-size:32px}}</style>';
}
function cc_rs_js() {
    static $d = false; if ($d) return ''; $d = true;
    return <<<'JS'
<script>(function(){var F=document.querySelector('.rs-form');if(F){var W=JSON.parse(F.dataset.w),file=F.querySelector('.rs-file'),pv=F.querySelector('.rs-prev'),pb=F.querySelector('.rs-pickb'),m=F.querySelector('.rs-msg'),img=null;
 function msg(t,e){m.textContent=t||'';m.classList.toggle('err',!!e);}
 pb.addEventListener('click',function(){file.click();});
 file.addEventListener('change',function(){var f=file.files&&file.files[0];if(!f)return;var i=new Image(),u=URL.createObjectURL(f);i.onload=function(){var s=Math.min(1,1600/Math.max(i.naturalWidth,i.naturalHeight)),c=document.createElement('canvas');c.width=Math.round(i.naturalWidth*s);c.height=Math.round(i.naturalHeight*s);
  c.getContext('2d').drawImage(i,0,0,c.width,c.height);URL.revokeObjectURL(u);img=c.toDataURL('image/jpeg',.85);pv.src=img;pv.classList.add('on');pb.textContent=W.change;F.querySelector('.rs-x').hidden=false;};i.src=u;file.value='';});
 /* Matteo 17 Nov: take the picked photo away again before sending */
 F.querySelector('.rs-x').addEventListener('click',function(){img=null;pv.removeAttribute('src');pv.classList.remove('on');this.hidden=true;pb.textContent=W.photo;});
 F.querySelector('.rs-go').addEventListener('click',function(){var b=this,t=F.querySelector('textarea').value.trim();if(!t&&!img){msg(W.empty,true);return;}b.disabled=true;msg(W.sending);
  var fd=new FormData();fd.append('text',t);fd.append('race',F.querySelector('select').value);fd.append('date',F.querySelector('input[type=date]').value);fd.append('consent',F.querySelector('.rs-tick input').checked?1:0);if(img)fd.append('img',img);
  fetch(F.dataset.api,{method:'POST',body:fd,credentials:'same-origin',headers:{'X-WP-Nonce':F.dataset.nonce}}).then(function(r){if(!r.ok)throw 0;msg(W.sent);setTimeout(function(){if(window.ccGo){window.ccGo('rs','#results');return;}var u=location.href.split('#')[0];location.replace(u+(u.indexOf('?')>-1?'&':'?')+'rs='+Date.now()+'#results');},1000);})
  .catch(function(){b.disabled=false;msg(W.err,true);});});}
/* coach: double-tap (or double-click) a photo = ❤️ */
document.querySelectorAll('.rs-dbl').forEach(function(P){var last=0,A=P.closest('.rs-card').querySelector('.rs-acts');if(!A)return;
 function like(){var h=P.querySelector('.rs-heart');h.classList.remove('go');void h.offsetWidth;h.classList.add('go');var x=A.querySelector('.rs-rx[data-r="heart"]');if(x)x.click();}
 P.addEventListener('pointerup',function(e){if(e.target.closest('.rs-full'))return;var t=Date.now();if(t-last<320){like();last=0;}else last=t;});
 P.addEventListener('dblclick',function(e){e.preventDefault();});});
document.querySelectorAll('.rs-acts').forEach(function(A){function post(d){var fd=new FormData();fd.append('page',A.dataset.page);fd.append('at',A.dataset.at);Object.keys(d).forEach(function(k){fd.append(k,d[k]);});
  return fetch(A.dataset.api,{method:'POST',body:fd,credentials:'same-origin',headers:{'X-WP-Nonce':A.dataset.nonce}}).then(function(r){if(!r.ok)throw 0;});}
 A.querySelectorAll('.rs-rx').forEach(function(x){x.addEventListener('click',function(){post({react:x.dataset.r}).then(function(){A.querySelectorAll('.rs-rx').forEach(function(y){y.classList.toggle('on',y===x);});}).catch(function(){if(window.ccErr)window.ccErr(A);});});});
 var pic=null,cf=A.querySelector('.rs-cfile'),cp=A.querySelector('.rs-cprev');
 A.querySelector('.rs-cam').addEventListener('click',function(){cf.click();});
 cf.addEventListener('change',function(){var f=cf.files&&cf.files[0];if(!f)return;var i=new Image(),u=URL.createObjectURL(f);i.onload=function(){var s=Math.min(1,1600/Math.max(i.naturalWidth,i.naturalHeight)),c=document.createElement('canvas');c.width=Math.round(i.naturalWidth*s);c.height=Math.round(i.naturalHeight*s);
  c.getContext('2d').drawImage(i,0,0,c.width,c.height);URL.revokeObjectURL(u);pic=c.toDataURL('image/jpeg',.85);cp.src=pic;cp.hidden=false;};i.src=u;cf.value='';});
 cp.addEventListener('click',function(){pic=null;cp.hidden=true;});
 A.querySelector('.rs-send').addEventListener('click',function(){var i=A.querySelector('.rs-rep'),d={};if(i.value.trim())d.reply=i.value.trim();if(pic)d.img=pic;if(!d.reply&&!d.img)return;var sb=this;sb.disabled=true;post(d).then(function(){var c=A.closest('.rs-card');if(window.ccGo){window.ccGo('rs',c&&c.id?'#'+c.id:'#results');}else location.reload();}).catch(function(){sb.disabled=false;if(window.ccErr)window.ccErr(A);});});});
document.addEventListener('click',function(e){var d=e.target.closest('.rs-del');if(!d)return;(window.ccAsk?window.ccAsk(d.dataset.q):Promise.resolve(confirm(d.dataset.q))).then(function(ok){if(!ok)return;var f=new FormData();f.append('page',d.dataset.page);f.append('at',d.dataset.at);
 fetch(d.dataset.api,{method:'POST',body:f,credentials:'same-origin',headers:{'X-WP-Nonce':d.dataset.nonce}}).then(function(r){if(!r.ok)throw 0;var c=d.closest('.rs-card');if(c){var w=c.previousElementSibling;if(w&&w.classList.contains('nt-who'))w.remove();c.remove();}}).catch(function(){if(window.ccErr)window.ccErr(d);});});});
})();</script>
JS;
}

// the section in the athlete's hub (after the notes): the form and their trophy shelf
add_filter('cc_ath_after_reports', function ($html, $view, $coach) {
    if (!$view) return $html;
    $rs = array_reverse(cc_rs_get($view));
    if ($coach) {
        if (!$rs) return $html;
        $o = '<section class="ath-s" id="results"><h2>' . cc_ath_icon('trophy', 'ath-hic') . 'Results</h2><div class="rs-shelf">';
        foreach (array_slice($rs, 0, 12) as $r) $o .= cc_rs_card($view, $r, true);
        return $html . $o . '</div></section>' . cc_rs_css() . cc_rs_js() . (function_exists('cc_nt_css') ? cc_nt_css() . cc_nt_js() : '');
    }
    $g = function_exists('cc_g_get') ? (cc_g_get($view) ?: []) : []; $opts = '<option value="">' . esc_html(cc_rs_w('none')) . '</option>';
    $ev = (array) ($g['events'] ?? []); usort($ev, function ($a, $b) { return strcmp($b['date'], $a['date']); });
    foreach ($ev as $e) if ($e['date'] <= current_time('Y-m-d', false) || $e['date'] <= date('Y-m-d', strtotime('+3 days'))) $opts .= '<option value="' . esc_attr($e['name']) . '" data-d="' . esc_attr($e['date']) . '">' . esc_html($e['name'] . ' · ' . cc_r_date(strtotime($e['date'] . ' 12:00'))) . '</option>';
    $W = []; foreach (['change', 'photo', 'sending', 'sent', 'empty', 'err'] as $k) $W[$k] = cc_rs_w($k);
    $o = '<section class="ath-s" id="results"><h2>' . cc_ath_icon('trophy', 'ath-hic') . esc_html(cc_rs_w('title')) . '</h2><p class="av-lede">' . esc_html(cc_rs_w('lede')) . '</p>'
       . '<div class="rs-form" data-api="' . esc_url(rest_url('cc/v1/result')) . '" data-nonce="' . esc_attr(wp_create_nonce('wp_rest')) . '" data-w="' . esc_attr(wp_json_encode($W)) . '">'
       . '<div class="rs-pick"><span class="rs-pw"><img class="rs-prev" alt=""><button type="button" class="rs-x" hidden aria-label="' . esc_attr(cc_rs_w('del')) . '">✕</button></span><button type="button" class="btn btn-ghost rs-pickb">' . esc_html(cc_rs_w('photo')) . '</button><input type="file" accept="image/*" class="rs-file" hidden></div>'
       . '<textarea rows="3" maxlength="1500" placeholder="' . esc_attr(cc_rs_w('ph')) . '" aria-label="' . esc_attr(cc_rs_w('title')) . '"></textarea>'
       . '<label>' . esc_html(cc_rs_w('race')) . '<select>' . $opts . '</select></label>'
       . '<label>' . esc_html(cc_rs_w('date')) . '<input type="date" max="' . esc_attr(current_time('Y-m-d')) . '" value="' . esc_attr(current_time('Y-m-d')) . '"></label>'
       // unticked: sharing publicly is their active choice; a heading says what the tick is for
       . '<div class="rs-share"><b>' . esc_html(cc_rs_w('askshare')) . '</b><label class="rs-tick"><input type="checkbox"> <span>' . esc_html(cc_rs_w('ok')) . '</span></label></div>'
       . '<button type="button" class="btn btn-go rs-go">' . esc_html(cc_rs_w('send')) . '</button><p class="rs-msg" role="status"></p></div>';
    if ($rs) { $o .= '<h3 class="av-sub" style="margin-top:28px">' . esc_html(cc_rs_w('shelf')) . '</h3><div class="rs-shelf">'; foreach (array_slice($rs, 0, 12) as $r) $o .= cc_rs_card($view, $r, false); $o .= '</div>'; }
    return $html . $o . '</section>' . cc_rs_css() . cc_rs_js() . (function_exists('cc_nt_css') ? cc_nt_css() . cc_nt_js() : '');
}, 16, 3);
add_filter('cc_ath_nav', function ($nav, $view, $coach) { if ($view && !$coach) $nav[] = ['results', cc_rs_w('title')]; return $nav; }, 30, 3);

/* ---------- saving, reacting, deleting ---------- */
add_action('rest_api_init', function () {
    $own = function (WP_REST_Request $r) { return cc_ath_is_coach() || (is_user_logged_in() && (int) $r->get_param('page') === cc_ath_page_of(get_current_user_id())); };
    register_rest_route('cc/v1', '/result', ['methods' => 'POST', 'permission_callback' => function () { return is_user_logged_in() && cc_ath_page_of(get_current_user_id()) && !cc_ath_is_coach(); }, 'callback' => 'cc_rs_save']);
    register_rest_route('cc/v1', '/result-react', ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => 'cc_rs_react']);
    // the conversation: Matteo or the athlete (own page), text and/or voice
    register_rest_route('cc/v1', '/result-reply', ['methods' => 'POST', 'permission_callback' => $own, 'callback' => function (WP_REST_Request $r) {
        $pid = (int) $r->get_param('page'); $at = (int) $r->get_param('at'); $a = cc_rs_get($pid); $coach = cc_ath_is_coach();
        foreach ($a as $k => $x) {
            if ((int) $x['at'] !== $at) continue;
            $text = cc_av_note((string) $r->get_param('text'), 1500); $aid = 0; $files = $r->get_file_params();
            if (!empty($files['audio']['tmp_name'])) { $aid = cc_av_store_audio($files['audio'], $pid, cc_av_str($r->get_param('transcript'), 2000)); if (is_wp_error($aid)) return $aid; }
            if ($text === '' && !$aid) return new WP_Error('cc_empty', 'Empty', ['status' => 400]);
            $a[$k]['thread'][] = ['at' => time(), 'from' => $coach ? 'coach' : 'athlete', 'text' => $text, 'audio' => (int) $aid]; cc_rs_put($pid, $a);
            $url = home_url('/' . CC_ATH_SLUG . '/') . '#results';
            if ($coach) { $uid = (int) get_post_meta($pid, 'cc_user', true);
                if ($uid && function_exists('cc_push_user')) { $keep = $GLOBALS['cc_ath_lang'] ?? 'en'; $GLOBALS['cc_ath_lang'] = cc_ath_user_lang($uid); cc_push_user($uid, cc_rs_w('replied'), $text !== '' ? wp_trim_words($text, 18) : '🎙', $url, 'cc-result-' . $at); $GLOBALS['cc_ath_lang'] = $keep; } }
            else { update_post_meta($pid, 'cc_results_updated', time());
                if (function_exists('cc_push_coaches')) cc_push_coaches('Reply on a result from ' . get_the_title($pid), $text !== '' ? wp_trim_words($text, 18) : '🎙 Voice note', add_query_arg('board', 'results', home_url('/' . CC_ATH_SLUG . '/')), 'cc-result', $pid); }
            return ['ok' => true];
        }
        return new WP_Error('cc_none', 'No such result', ['status' => 404]);
    }]);
    register_rest_route('cc/v1', '/result-delete', ['methods' => 'POST', 'permission_callback' => $own, 'callback' => function (WP_REST_Request $r) {
        $pid = (int) $r->get_param('page'); $at = (int) $r->get_param('at'); $a = cc_rs_get($pid);
        foreach ($a as $k => $x) if ((int) $x['at'] === $at) { cc_rs_files_gone($x); unset($a[$k]); cc_rs_put($pid, $a); return ['ok' => true]; }
        return new WP_Error('cc_none', 'No such result', ['status' => 404]);
    }]);
    register_rest_route('cc/v1', '/results', ['methods' => 'GET', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function () {   // Matteo's tools (e.g. social posts): consent included
        $out = []; foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'meta_key' => 'cc_results']) as $p) {
            $uid = (int) get_post_meta($p->ID, 'cc_user', true); $vid = $uid ? (string) get_user_meta($uid, 'cc_vekta_id', true) : '';   // for the Vekta sync
            foreach (cc_rs_get($p->ID) as $x)
            $out[] = ['page' => $p->ID, 'athlete' => $p->post_title, 'vekta_id' => $vid ?: null, 'react' => $x['react'] ?? '', 'reply' => $x['reply'] ?? '', 'at' => $x['at'], 'date' => $x['date'], 'race' => $x['race'], 'text' => $x['text'], 'consent' => (bool) $x['consent'], 'photo' => !empty($x['photo']) ? wp_get_attachment_url((int) $x['photo']) : null];
        }
        usort($out, function ($a, $b) { return $b['at'] <=> $a['at']; }); return $out;
    }]);
});
function cc_rs_save(WP_REST_Request $r) {
    $uid = get_current_user_id(); $pid = cc_ath_page_of($uid); $a = cc_rs_get($pid);
    $today = 0; foreach ($a as $x) if ($x['at'] > time() - DAY_IN_SECONDS) $today++; if ($today >= 8) return new WP_Error('cc_many', 'Too many today', ['status' => 429]);
    $text = cc_av_note((string) $r->get_param('text'), 1500); $pidPhoto = 0;
    if (preg_match('#^data:image/jpeg;base64,([A-Za-z0-9+/=]+)$#', (string) $r->get_param('img'), $m)) {
        $bytes = base64_decode($m[1], true); $sz = $bytes ? @getimagesizefromstring($bytes) : false;
        if (!$bytes || strlen($bytes) > 3000000 || !$sz || $sz[2] !== IMAGETYPE_JPEG) return new WP_Error('cc_bad', 'Photo not accepted', ['status' => 400]);
        $pidPhoto = (int) cc_f_store($pid, $bytes, 'result', 'jpg', 'image/jpeg', 'Result photo');
    }
    if ($text === '' && !$pidPhoto) return new WP_Error('cc_empty', 'Empty', ['status' => 400]);
    $date = cc_av_date((string) $r->get_param('date')) ?: current_time('Y-m-d'); if ($date > current_time('Y-m-d')) $date = current_time('Y-m-d');
    $x = ['at' => time(), 'text' => $text, 'race' => cc_av_str($r->get_param('race'), 120), 'date' => $date, 'photo' => $pidPhoto, 'consent' => (bool) $r->get_param('consent'), 'react' => '', 'reply' => ''];
    $a[] = $x; cc_rs_put($pid, $a); update_post_meta($pid, 'cc_results_updated', time());
    // Matteo: email with the photo attached, and his phone
    $name = get_the_title($pid); $board = add_query_arg('board', 'results', home_url('/' . CC_ATH_SLUG . '/'));
    if (function_exists('cc_av_notify_to') && cc_av_notify_to()) {
        $h = '<div style="font-family:Montserrat,Helvetica,Arial,sans-serif;font-size:16px;color:#222"><h2>🏆 Result from ' . esc_html($name) . '</h2>'
           . '<p style="margin:0 0 10px">' . esc_html(cc_r_date(strtotime($date . ' 12:00'))) . ($x['race'] !== '' ? ' · <b>' . esc_html($x['race']) . '</b>' : '') . '</p>'
           . ($text !== '' ? '<blockquote style="margin:0 0 16px;padding:10px 14px;background:#f2f4f3;border-left:3px solid #009a44;white-space:pre-line">' . esc_html($text) . '</blockquote>' : '')
           . '<p style="margin:0 0 10px">' . ($x['consent'] ? '✅ OK to share on social media and Skool.' : '🔒 Private: they did not tick social media.') . ($pidPhoto ? ' Photo attached.' : '') . '</p>'
           . '<p style="margin:20px 0 0"><a href="' . esc_url($board) . '" style="display:inline-block;padding:12px 20px;border-radius:8px;background:#009a44;color:#fff;font-weight:600;text-decoration:none">React in the hub</a></p></div>';
        $u = get_userdata($uid); $hd = ['Content-Type: text/html; charset=UTF-8']; if ($u && is_email($u->user_email)) $hd[] = 'Reply-To: ' . $name . ' <' . $u->user_email . '>';
        if (function_exists('cc_ath_coach_wrap')) $h = cc_ath_coach_wrap($h);
        wp_mail(cc_av_notify_to(), '🏆 Result from ' . $name, $h, $hd, $pidPhoto ? array_filter([get_attached_file($pidPhoto)]) : []);
    }
    if (function_exists('cc_push_coaches')) cc_push_coaches('🏆 Result from ' . $name, $text !== '' ? wp_trim_words($text, 18) : 'New photo', $board, 'cc-result', $pid);
    return ['ok' => true];
}
function cc_rs_react(WP_REST_Request $r) {   // Matteo: a reaction and/or a short reply; the athlete's phone is told
    $pid = (int) $r->get_param('page'); $at = (int) $r->get_param('at'); $a = cc_rs_get($pid);
    foreach ($a as $k => $x) {
        if ((int) $x['at'] !== $at) continue;
        $react = (string) $r->get_param('react'); $reply = cc_av_note((string) $r->get_param('reply'), 600);
        if (isset(CC_RS_REACTS[$react])) $a[$k]['react'] = $react;
        $pic = 0;
        if (preg_match('#^data:image/jpeg;base64,([A-Za-z0-9+/=]+)$#', (string) $r->get_param('img'), $m)) {   // Matteo's photo in the reply
            $bytes = base64_decode($m[1], true); $sz = $bytes ? @getimagesizefromstring($bytes) : false;
            if (!$bytes || strlen($bytes) > 3000000 || !$sz || $sz[2] !== IMAGETYPE_JPEG) return new WP_Error('cc_bad', 'Photo not accepted', ['status' => 400]);
            $pic = (int) cc_f_store($pid, $bytes, 'result-reply', 'jpg', 'image/jpeg', 'Reply photo');
        }
        if ($reply !== '' || $pic) $a[$k]['thread'][] = ['at' => time(), 'from' => 'coach', 'text' => $reply, 'photo' => $pic];   // a reply joins the conversation
        cc_rs_put($pid, $a);
        $uid = (int) get_post_meta($pid, 'cc_user', true);
        if ($uid && function_exists('cc_push_user')) {
            $keep = $GLOBALS['cc_ath_lang'] ?? 'en'; $GLOBALS['cc_ath_lang'] = cc_ath_user_lang($uid);
            cc_push_user($uid, ($reply !== '' || $pic) ? cc_rs_w('replied') : cc_rs_w('reacted') . ' ' . (CC_RS_REACTS[$react] ?? ''), $reply !== '' ? wp_trim_words($reply, 18) : ($pic ? '📷' : ''), home_url('/' . CC_ATH_SLUG . '/') . '#results', 'cc-result-' . $at);
            $GLOBALS['cc_ath_lang'] = $keep;
        }
        return ['ok' => true];
    }
    return new WP_Error('cc_none', 'No such result', ['status' => 404]);
}

/* ---------- Matteo's board: /athletes/?board=results ---------- */
add_filter('cc_ath_coach_links', function ($html) {
    $seen = (int) get_user_meta(get_current_user_id(), 'cc_results_seen', true); $n = 0;
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'meta_key' => 'cc_results_updated', 'fields' => 'ids']) as $p) foreach (cc_rs_get($p) as $x) if ($x['at'] > $seen) $n++;
    return $html . '<a class="av-boardlink" href="' . esc_url(add_query_arg('board', 'results', home_url('/' . CC_ATH_SLUG . '/'))) . '">Results' . ($n ? ' <span class="av-badge">' . $n . ' new</span>' : '') . '</a>';
}, 13);
add_filter('cc_ath_board', function ($html, $board) {
    if ($board !== 'results' || !cc_ath_is_coach()) return $html;
    add_action('shutdown', function () { update_user_meta(get_current_user_id(), 'cc_results_seen', time()); });
    $all = []; foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'meta_key' => 'cc_results_updated']) as $p) foreach (cc_rs_get($p->ID) as $x) $all[] = [$p, $x];
    usort($all, function ($a, $b) { return $b[1]['at'] <=> $a[1]['at']; });
    $o = '<section class="ath-s"><h2>' . cc_ath_icon('trophy', 'ath-hic') . 'Results</h2><p class="av-lede">What your athletes are proud of, newest first. ✅ means they agreed you can share it on social media and Skool. React or reply: they see it in their hub and on their phone.</p><div class="rs-shelf">';
    if (!$all) $o .= '<p class="av-lede">No results yet.</p>';
    foreach (array_slice($all, 0, 60) as [$p, $x]) $o .= '<div class="nt-who">' . (function_exists('cc_ph_face') ? cc_ph_face($p->ID, 30) . ' ' : '') . '<b><a style="color:#fff" href="' . esc_url(add_query_arg('view', $p->ID, home_url('/' . CC_ATH_SLUG . '/'))) . '">' . esc_html($p->post_title) . '</a></b>' . '</div>' . cc_rs_card($p->ID, $x, true);
    return $o . '</div></section>' . cc_rs_css() . cc_rs_js() . (function_exists('cc_nt_css') ? cc_nt_css() . cc_nt_js() : '');
}, 10, 2);
