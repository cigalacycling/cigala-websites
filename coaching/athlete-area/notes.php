<?php
if (!defined('ABSPATH')) return;
/* "Leave me a note" (Matteo, 17 Nov 2026): next to My availability, the athlete types or records a voice note for Matteo
 * ("this week I feel…, I didn't sleep well…"), instead of a catch-up call. Up to 5 minutes.
 * - While they record, nothing appears in their text box: the words are written out invisibly, only for Matteo's email.
 * - "Is this about a session?": an optional day. The hub→Vekta sync then puts the note in their Vekta calendar on that day
 *   (type training, visible to Matteo only), with the words and a link to the recording.
 * - Matteo replies on his Notes board (or the athlete's page), typing or recording; the athlete sees the reply under their
 *   note in the hub and gets an email in their language.
 * Stored on the athlete page (meta cc_notes, newest last, at most 60; audio in uploads/cc-private, guarded). */

function cc_nt_w($k) {
    static $W = [
        'title' => ['en' => 'Leave me a note', 'it' => 'Lasciami un messaggio', 'pt' => 'Deixa-me uma mensagem', 'sl' => 'Pusti mi sporočilo', 'sk' => 'Nechaj mi správu'],
        'lede' => ['en' => 'How is your week going? How you feel, your sleep, work, a niggle… Type it, or record a voice note (up to 5 minutes).',
                   'it' => 'Come va la settimana? Come ti senti, il sonno, il lavoro, un piccolo fastidio… Scrivilo, oppure registra un messaggio vocale (fino a 5 minuti).',
                   'pt' => 'Como está a correr a tua semana? Como te sentes, o sono, o trabalho, uma pequena dor… Escreve, ou grava uma mensagem de voz (até 5 minutos).',
                   'sl' => 'Kako gre tvoj teden? Kako se počutiš, spanec, služba, kakšna bolečina… Napiši ali posnemi glasovno sporočilo (do 5 minut).', 'sk' => 'Ako ti ide týždeň? Ako sa cítiš, spánok, práca, nejaká bolestička… Napíš to alebo nahraj hlasovú správu (do 5 minút).'],
        'ph' => ['en' => 'Your note…', 'it' => 'Il tuo messaggio…', 'pt' => 'A tua mensagem…', 'sl' => 'Tvoje sporočilo…', 'sk' => 'Tvoja správa…'],
        'rec' => ['en' => 'Record a voice note', 'it' => 'Registra un vocale', 'pt' => 'Gravar mensagem de voz', 'sl' => 'Posnemi glasovno sporočilo', 'sk' => 'Nahrať hlasovú správu'],
        'stop' => ['en' => 'Stop recording', 'it' => 'Ferma la registrazione', 'pt' => 'Parar a gravação', 'sl' => 'Ustavi snemanje', 'sk' => 'Zastaviť nahrávanie'],
        'listening' => ['en' => 'Recording… {s} s', 'it' => 'Registrazione… {s} s', 'pt' => 'A gravar… {s} s', 'sl' => 'Snemam… {s} s', 'sk' => 'Nahrávam… {s} s'],
        'ready' => ['en' => 'Voice note ready ({s} s)', 'it' => 'Vocale pronto ({s} s)', 'pt' => 'Mensagem de voz pronta ({s} s)', 'sl' => 'Glasovno sporočilo pripravljeno ({s} s)', 'sk' => 'Hlasová správa je pripravená ({s} s)'],
        'del' => ['en' => 'Delete', 'it' => 'Elimina', 'pt' => 'Apagar', 'sl' => 'Izbriši', 'sk' => 'Vymazať'],
        'day' => ['en' => 'Is this about a session? Pick the day (optional)', 'it' => 'Riguarda un allenamento? Scegli il giorno (facoltativo)', 'pt' => 'É sobre um treino? Escolhe o dia (opcional)', 'sl' => 'Gre za trening? Izberi dan (neobvezno)', 'sk' => 'Týka sa to tréningu? Vyber deň (nepovinné)'],
        'send' => ['en' => 'Send to Matteo', 'it' => 'Invia a Matteo', 'pt' => 'Enviar ao Matteo', 'sl' => 'Pošlji Matteu', 'sk' => 'Poslať Matteovi'],
        'sending' => ['en' => 'Sending…', 'it' => 'Invio…', 'pt' => 'A enviar…', 'sl' => 'Pošiljam…', 'sk' => 'Posielam…'],
        'sent' => ['en' => 'Thank you! Your note reached me.', 'it' => 'Grazie! Il tuo messaggio mi è arrivato.', 'pt' => 'Obrigado! A tua mensagem chegou até mim.', 'sl' => 'Hvala! Tvoje sporočilo je prišlo do mene.', 'sk' => 'Ďakujem! Tvoja správa ku mne dorazila.'],
        'empty' => ['en' => 'Type something or record a voice note first.', 'it' => 'Prima scrivi qualcosa o registra un vocale.', 'pt' => 'Primeiro escreve algo ou grava uma mensagem de voz.', 'sl' => 'Najprej nekaj napiši ali posnemi sporočilo.', 'sk' => 'Najprv niečo napíš alebo nahraj hlasovú správu.'],
        'err' => ['en' => 'It did not send. Please try again.', 'it' => 'Non è stato inviato. Riprova.', 'pt' => 'Não foi enviado. Tenta outra vez.', 'sl' => 'Ni bilo poslano. Poskusi znova.', 'sk' => 'Neodoslalo sa. Skús to znova.'],
        'mic_no' => ['en' => 'Recording isn’t possible in this browser. You can type your note instead.', 'it' => 'In questo browser non si può registrare. Puoi scrivere il messaggio.', 'pt' => 'Não é possível gravar neste navegador. Podes escrever a mensagem.', 'sl' => 'V tem brskalniku snemanje ni mogoče. Sporočilo lahko napišeš.', 'sk' => 'V tomto prehliadači sa nedá nahrávať. Správu môžeš napísať.'],
        'mic_denied' => ['en' => 'Allow the microphone to record a voice note.', 'it' => 'Consenti l’uso del microfono per registrare.', 'pt' => 'Permite o microfone para gravar.', 'sl' => 'Dovoli mikrofon za snemanje.', 'sk' => 'Na nahranie hlasovej správy povoľ mikrofón.'],
        'yours' => ['en' => 'Your notes', 'it' => 'I tuoi messaggi', 'pt' => 'As tuas mensagens', 'sl' => 'Tvoja sporočila', 'sk' => 'Tvoje správy'],
        'voice' => ['en' => 'Voice note', 'it' => 'Messaggio vocale', 'pt' => 'Mensagem de voz', 'sl' => 'Glasovno sporočilo', 'sk' => 'Hlasová správa'],
        'about' => ['en' => 'About the session on %s', 'it' => 'Sull’allenamento del %s', 'pt' => 'Sobre o treino de %s', 'sl' => 'O treningu %s', 'sk' => 'K tréningu: %s'],
        'reply' => ['en' => 'Matteo replied', 'it' => 'Matteo ha risposto', 'pt' => 'O Matteo respondeu', 'sl' => 'Matteo je odgovoril', 'sk' => 'Matteo odpovedal'],
        // Matteo 18 Nov: a message he starts himself
        'from_m' => ['en' => 'Matteo', 'it' => 'Matteo', 'pt' => 'Matteo', 'sl' => 'Matteo', 'sk' => 'Matteo'],
        'new_subj' => ['en' => 'A new message from Matteo', 'it' => 'Un nuovo messaggio da Matteo', 'pt' => 'Uma nova mensagem do Matteo', 'sl' => 'Novo sporočilo od Mattea', 'sk' => 'Nová správa od Mattea'],
        'new_p' => ['en' => 'Matteo sent you a message in your athlete hub. Open it to read or listen, and answer him there.', 'it' => 'Matteo ti ha mandato un messaggio nella tua area atleta. Aprila per leggerlo o ascoltarlo e rispondergli lì.',
                    'pt' => 'O Matteo enviou-te uma mensagem na tua área de atleta. Abre-a para ler ou ouvir e responder-lhe aí.', 'sl' => 'Matteo ti je poslal sporočilo v tvojem središču. Odpri ga, da ga prebereš ali poslušaš, in mu odgovori tam.', 'sk' => 'Matteo ti poslal správu do tvojej zóny pre športovcov. Otvor ju, prečítaj si ju alebo vypočuj a odpovedz mu tam.'],
        'mail_subj' => ['en' => 'Matteo replied to your note', 'it' => 'Matteo ha risposto al tuo messaggio', 'pt' => 'O Matteo respondeu à tua mensagem', 'sl' => 'Matteo je odgovoril na tvoje sporočilo', 'sk' => 'Matteo odpovedal na tvoju správu'],
        'mail_p' => ['en' => 'I replied to your note in your athlete hub.', 'it' => 'ho risposto al tuo messaggio nella tua area atleta.', 'pt' => 'respondi à tua mensagem na tua área de atleta.', 'sl' => 'odgovoril sem na tvoje sporočilo v tvojem središču za športnike.', 'sk' => 'odpovedal som na tvoju správu v tvojej zóne pre športovcov.'],
        'you' => ['en' => 'You', 'it' => 'Tu', 'pt' => 'Tu', 'sl' => 'Ti', 'sk' => 'Ty'],
        'answer' => ['en' => 'Answer Matteo', 'it' => 'Rispondi a Matteo', 'pt' => 'Responder ao Matteo', 'sl' => 'Odgovori Matteu', 'sk' => 'Odpovedať Matteovi'],
        'delq' => ['en' => 'Delete this? It cannot be undone.', 'it' => 'Eliminarlo? Non si può annullare.', 'pt' => 'Apagar? Não é possível desfazer.', 'sl' => 'Izbrišem? Tega ni mogoče razveljaviti.', 'sk' => 'Vymazať? Nedá sa to vrátiť späť.'],
        'mail_btn' => ['en' => 'Open my hub', 'it' => 'Apri la mia area', 'pt' => 'Abrir a minha área', 'sl' => 'Odpri moje središče', 'sk' => 'Otvoriť moju zónu'],
        // Matteo 19 Nov: double tap to like, like on Instagram
        'liked_m' => ['en' => 'Matteo liked your message', 'it' => 'A Matteo piace il tuo messaggio', 'pt' => 'O Matteo gostou da tua mensagem', 'sl' => 'Matteu je všeč tvoje sporočilo', 'sk' => 'Matteovi sa páči tvoja správa'],
        'hint' => ['en' => 'Double tap a message to ❤️ it', 'it' => 'Tocca due volte un messaggio per mettere ❤️', 'pt' => 'Toca duas vezes numa mensagem para dar ❤️', 'sl' => 'Dvakrat tapni sporočilo za ❤️', 'sk' => 'Dvakrát ťukni na správu a daj jej ❤️'],
    ];
    $l = $GLOBALS['cc_ath_lang'] ?? 'en';
    return $W[$k][$l] ?? $W[$k]['en'];
}
// the little ❤️ under a message: who liked it ("Matteo", "You", or the athlete's name in the coach view)
function cc_nt_likes($lk, $forCoach, $name = '') {
    $lk = (array) $lk; $who = [];
    if (!empty($lk['coach'])) $who[] = $forCoach ? 'You' : cc_nt_w('from_m');
    if (!empty($lk['athlete'])) $who[] = $forCoach ? ($name ?: 'Athlete') : cc_nt_w('you');
    return '<span class="nt-like"' . ($who ? '' : ' hidden') . '>❤️ <small>' . esc_html(implode(' · ', $who)) . '</small></span>';
}
function cc_nt_get($pid) { $a = json_decode((string) get_post_meta($pid, 'cc_notes', true), true); return is_array($a) ? $a : []; }
function cc_nt_put($pid, $ns) {   // keeps the newest 60; older ones go, with their recordings (Matteo 17 Nov: no files left behind)
    $ns = array_values($ns);
    foreach (array_slice($ns, 0, max(0, count($ns) - 60)) as $old) foreach (array_merge([$old], (array) ($old['replies'] ?? [])) as $x) if (!empty($x['audio'])) wp_delete_attachment((int) $x['audio'], true);
    update_post_meta($pid, 'cc_notes', wp_slash(wp_json_encode(array_slice($ns, -60))));
}
function cc_nt_url($aid) { return $aid ? wp_get_attachment_url((int) $aid) : ''; }
function cc_nt_words() { $W = []; foreach (['listening', 'ready', 'del', 'rec', 'stop', 'sending', 'sent', 'empty', 'err', 'mic_no', 'mic_denied'] as $k) $W[$k] = cc_nt_w($k); return $W; }

// one composer (textarea + record + send), for the athlete's note and for Matteo's replies
function cc_nt_box($api, $extra, $ph, $send, $withDay = false, $lang = 'en-GB') {
    return '<div class="nt-box" data-api="' . esc_url($api) . '" data-nonce="' . esc_attr(wp_create_nonce('wp_rest')) . '" data-lang="' . esc_attr($lang) . '" data-extra="' . esc_attr(wp_json_encode($extra)) . '" data-w="' . esc_attr(wp_json_encode(cc_nt_words())) . '">'
        . '<textarea rows="3" maxlength="3000" placeholder="' . esc_attr($ph) . '" aria-label="' . esc_attr($ph) . '"></textarea>'
        // Matteo 17 Nov: a green microphone on the left of the button, sized and coloured in the icon itself (always visible)
        . '<div class="nt-row"><button type="button" class="btn btn-ghost nt-rec" aria-pressed="false"><svg class="nt-mic" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#2bd47a" stroke-width="2" stroke-linecap="round" aria-hidden="true" style="width:20px;height:20px;flex:none;display:inline-block"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3M9 21h6"/></svg><span>' . esc_html(cc_nt_w('rec')) . '</span></button><span class="nt-st" role="status"></span></div>'
        . ($withDay ? '<label class="nt-day">' . esc_html(cc_nt_w('day')) . '<input type="date" max="' . esc_attr(current_time('Y-m-d')) . '"></label>' : '')
        . '<button type="button" class="btn btn-go nt-send">' . esc_html($send) . '</button><p class="nt-msg" role="status"></p></div>';
}
// Matteo 17 Nov: a player in the hub's style (round green play button, green progress bar you can tap or drag, time) instead of the browser's
function cc_nt_player($u) {
    return '<div class="nt-pl" data-src="' . esc_url($u) . '"><button type="button" class="nt-pb" aria-label="Play"><svg viewBox="0 0 24 24" class="nt-play"><path d="M8 5.5v13l11-6.5z"/></svg>'
         . '<svg viewBox="0 0 24 24" class="nt-pause"><path d="M7 5h3.5v14H7zM13.5 5H17v14h-3.5z"/></svg></button>'
         . '<div class="nt-bar" role="slider" tabindex="0" aria-label="Position" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><i></i><b></b></div><span class="nt-t">0:00</span></div>';
}
// a delete button (Matteo 17 Nov: the athlete for their own note or reply, Matteo for anything)
function cc_nt_delbtn($pid, $at, $ri = -1) {
    return '<button type="button" class="nt-del" data-api="' . esc_url(rest_url('cc/v1/note-delete')) . '" data-nonce="' . esc_attr(wp_create_nonce('wp_rest')) . '" data-page="' . (int) $pid . '" data-at="' . (int) $at . '" data-ri="' . (int) $ri . '" data-q="' . esc_attr(cc_nt_w('delq')) . '">' . esc_html(cc_nt_w('del')) . '</button>';
}
function cc_nt_item($n, $forCoach, $pid = 0) {
    $who = $forCoach && $pid ? get_the_title($pid) : '';
    $byMe = ($n['from'] ?? '') === 'coach';   // a message Matteo started himself (Matteo 18 Nov)
    $o = '<div class="nt-item' . ($byMe ? ' nt-bym' : '') . '"' . ($pid ? ' id="nt-' . (int) $pid . '-' . (int) $n['at'] . '"' : '') . ($pid ? ' data-lp="' . (int) $pid . '" data-la="' . (int) $n['at'] . '" data-lr="-1"' : '') . '>' . ($byMe ? '<span class="nt-rh"><img class="nt-me" src="https://coaching.cigalacycling.com/wp-content/uploads/2026/11/cigala-email-matteo-photo.jpg" width="30" height="30" alt=""><b>' . esc_html($forCoach ? 'Your message' : cc_nt_w('from_m')) . '</b></span>' : '') . '<small>' . esc_html(date_i18n('j M Y, H:i', (int) $n['at'])) . (!empty($n['day']) ? ' · ' . esc_html(sprintf(cc_nt_w('about'), date_i18n('j M', strtotime($n['day'] . ' 12:00')))) : '') . '</small>'
       . ($pid ? cc_nt_delbtn($pid, $n['at']) : '');
    if (($u = cc_nt_url($n['audio'] ?? 0))) $o .= cc_nt_player($u);
    if (($n['text'] ?? '') !== '') $o .= '<p>' . nl2br(esc_html($n['text'])) . '</p>';
    if ($forCoach && ($n['tr'] ?? '') !== '') $o .= '<p class="nt-tr"><i>Written out from the voice note:</i> ' . esc_html($n['tr']) . '</p>';
    $o .= cc_nt_likes($n['likes']['n'] ?? [], $forCoach, $who);
    foreach (array_values((array) ($n['replies'] ?? [])) as $ri => $r) {
        $mine = ($r['from'] ?? 'coach') === 'coach';   // Matteo's reply, or the athlete answering in the thread
        $label = $mine ? ($forCoach ? 'Your reply' : cc_nt_w('reply')) : ($forCoach ? $who : cc_nt_w('you'));
        // Matteo's photo by his replies (athlete view); the athlete's own photo (or initials) by theirs (both views)
        // Matteo 17 Nov: the face always beside the name (never on top), his own photo in his coach view too
        $face = $mine ? '<img class="nt-me" src="https://coaching.cigalacycling.com/wp-content/uploads/2026/11/cigala-email-matteo-photo.jpg" width="30" height="30" alt="">'
                      : ($pid && function_exists('cc_ph_widget') ? cc_ph_widget($pid, 30, false, 'nt-me-a') : '');
        $o .= '<div class="nt-rep' . ($mine ? '' : ' nt-rep-a') . '"' . ($pid ? ' data-lp="' . (int) $pid . '" data-la="' . (int) $n['at'] . '" data-lr="' . (int) $ri . '"' : '') . '><span class="nt-rh">' . $face
            . '<b>' . esc_html($label) . '</b> <small>' . esc_html(date_i18n('j M, H:i', (int) $r['at'])) . '</small></span>'
            . ($pid && ($forCoach || !$mine) ? cc_nt_delbtn($pid, $n['at'], $ri) : '');
        if (($u = cc_nt_url($r['audio'] ?? 0))) $o .= cc_nt_player($u);
        if (($r['text'] ?? '') !== '') $o .= '<p>' . nl2br(esc_html($r['text'])) . '</p>';
        $o .= cc_nt_likes($n['likes']['r' . $ri] ?? [], $forCoach, $who) . '</div>';
    }
    if ($pid && $forCoach) $o .= '<details class="nt-replyd"><summary>Reply</summary>' . cc_nt_box(rest_url('cc/v1/note-reply'), ['page' => $pid, 'at' => (int) $n['at']], 'Your reply…', 'Send reply') . '</details>';
    elseif ($pid && (!empty($n['replies']) || $byMe)) {   // the athlete answers in the same thread once Matteo has replied (or wrote first)
        $speech = defined('CC_AV_SPEECH') ? (CC_AV_SPEECH[$GLOBALS['cc_ath_lang'] ?? 'en'] ?? 'en-GB') : 'en-GB';
        $o .= '<details class="nt-replyd"><summary>' . esc_html(cc_nt_w('answer')) . '</summary>' . cc_nt_box(rest_url('cc/v1/note-reply'), ['page' => $pid, 'at' => (int) $n['at']], cc_nt_w('ph'), cc_nt_w('send'), false, $speech) . '</details>';
    }
    return $o . '</div>';
}

// the box, right after My availability (availability 10, goals 20); their last notes with my replies under it
add_filter('cc_ath_after_reports', function ($html, $view, $coach) {
    if (!$view) return $html;
    $ns = array_reverse(cc_nt_get($view));
    if ($coach) {
        // Matteo 18 Nov: he can start a conversation himself, text or voice (only when looking at one athlete)
        $first = ($u = get_userdata((int) get_post_meta($view, 'cc_user', true))) ? ($u->first_name ?: $u->display_name) : get_the_title($view);
        $o = '<section class="ath-s nt" id="notes"><h2>' . cc_ath_icon('mic', 'ath-hic') . 'Notes</h2>';
        if ($u) $o .= '<h3 class="av-sub">Send ' . esc_html($first) . ' a message</h3>' . cc_nt_box(rest_url('cc/v1/coach-note'), ['page' => $view], 'Your message to ' . $first . '…', 'Send message');
        foreach (array_slice($ns, 0, 10) as $n) $o .= cc_nt_item($n, true, $view);
        return $html . $o . '</section>' . cc_nt_css() . cc_nt_js();
    }
    $speech = defined('CC_AV_SPEECH') ? (CC_AV_SPEECH[$GLOBALS['cc_ath_lang'] ?? 'en'] ?? 'en-GB') : 'en-GB';
    $o = '<section class="ath-s nt" id="notes"><h2>' . cc_ath_icon('mic', 'ath-hic') . esc_html(cc_nt_w('title')) . '</h2><p class="av-lede">' . esc_html(cc_nt_w('lede')) . '</p>'
       . cc_nt_box(rest_url('cc/v1/note'), new stdClass(), cc_nt_w('ph'), cc_nt_w('send'), true, $speech);
    // Matteo 17 Nov: the hub shows their notes of the last 30 days (at most 5); everything stays on his Notes board
    $recent = array_slice(array_values(array_filter($ns, function ($n) { return $n['at'] > time() - 30 * DAY_IN_SECONDS; })), 0, 5);
    if ($recent) { $o .= '<h3 class="av-sub nt-yours">' . esc_html(cc_nt_w('yours')) . '</h3><p class="nt-hint">' . esc_html(cc_nt_w('hint')) . '</p>'; foreach ($recent as $n) $o .= cc_nt_item($n, false, $view); }
    return $html . $o . '</section>' . cc_nt_css() . cc_nt_js();
}, 15, 3);
function cc_nt_css() {
    static $done = false; if ($done) return ''; $done = true;
    // Matteo 19 Nov: a notification opens the exact note (#nt-<page>-<time>): scrolled to the middle of the screen and highlighted
    $jump = '<style>html .cc .nt-item.nt-hl{box-shadow:0 0 0 3px rgba(43,212,122,.55);border-radius:12px;transition:box-shadow .4s}</style>'
        . '<script>(function(){function go(){var h=location.hash;if(h.indexOf("#nt-")!==0)return;var el=document.getElementById(h.slice(1));if(!el)return;'
        . 'var d=el.closest("details");if(d)d.open=true;el.scrollIntoView({block:"center"});el.classList.add("nt-hl");setTimeout(function(){el.classList.remove("nt-hl");},5000);}'
        . 'if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",function(){go();setTimeout(go,700);});else{go();setTimeout(go,700);}addEventListener("hashchange",go);})();</script>';
    return $jump . '<style>html .cc .nt-box{display:grid;gap:12px}html .cc .nt-box textarea{width:100%;min-height:96px;font:16px var(--body);padding:12px 14px;border-radius:12px;border:1px solid rgba(255,255,255,.2);background:#0b0d0f;color:#fff;box-sizing:border-box}'
        . 'html .cc .nt-row{display:flex;flex-wrap:wrap;align-items:center;gap:10px 14px}html .cc .nt-rec{display:inline-flex;align-items:center;gap:10px}'
        // Matteo 17 Nov: dark button as before, only the microphone in green
        . 'html .cc .nt-rec .nt-mic{display:inline-block!important}html .cc .nt-rec.on .nt-mic{stroke:#fff}html .cc .nt-rec .nt-ic svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:2}'
        . 'html .cc .nt-rec.on{background:#ca212a!important;border-color:#ca212a!important;color:#fff!important;animation:ntpulse 1.2s ease-in-out infinite}@keyframes ntpulse{0%,100%{box-shadow:0 0 0 0 rgba(202,33,42,.6)}50%{box-shadow:0 0 0 8px rgba(202,33,42,0)}}'
        . 'html .cc .nt-st{font-size:15px;color:#d0d6e0}html .cc .nt-st button{background:none;border:0;color:#ff7a73;text-decoration:underline;font:inherit;cursor:pointer;padding:0;margin-left:8px}'
        . 'html .cc .nt-day{display:grid;gap:6px;font-size:15px;color:#d0d6e0;font-weight:600}html .cc .nt-day input{font:16px var(--body);padding:10px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.2);background:#0b0d0f;color:#fff;max-width:220px}'
        . 'html .cc .nt-send{justify-self:start}html .cc .nt-msg{margin:0;font-size:16px;font-weight:600;color:#34c46a}html .cc .nt-msg.err{color:#ff7a73}html .cc .nt-msg:empty{display:none}'
        . 'html .cc .nt-item{padding:14px 0;border-top:1px solid rgba(255,255,255,.1)}html .cc .nt-item small{color:#b8bec8;font-size:15px}html .cc .nt-item audio{display:block;width:100%;max-width:420px;margin:8px 0}html .cc .nt-item p{margin:6px 0 0;font-size:16px;color:#e6e9ee}'
        . 'html .cc .nt-tr{color:#b8bec8!important;font-size:15px!important}html .cc .nt-rep{margin:10px 0 0 14px;padding:10px 12px;border-left:3px solid #12a150;background:rgba(18,161,80,.08);border-radius:0 10px 10px 0}html .cc .nt-rep b{color:#34c46a}'
        // Matteo 17 Nov: less space under "Answer Matteo" / "Reply" while closed
        . 'html .cc .nt-replyd{margin-top:8px}html .cc .nt-replyd summary{cursor:pointer;color:#34c46a;font-weight:600;font-size:15px;margin:0;padding:2px 0;line-height:1.3}html .cc .nt-replyd[open] summary{margin-bottom:10px}'
        . '@media (max-width:760px){html .cc .nt-item{padding:10px 0}html .cc .nt-replyd{margin-top:6px}}'
        . 'html .cc .nt-del{float:right;background:none;border:0;padding:2px 0;margin:0 0 0 10px;min-height:0;font:600 14px var(--body);color:#b8bec8;text-decoration:underline;cursor:pointer}html .cc .nt-del:hover{color:#ff7a73}'
        . 'html .cc .nt-rep-a{border-left-color:#b8bec8;background:rgba(255,255,255,.05);margin-left:28px}html .cc .nt-rep-a b{color:#fff!important}'
        . 'html .cc .nt-rep .nt-me-a{display:inline-grid;vertical-align:middle;margin:0 8px 0 0;border-width:2px;box-shadow:none}html .cc .nt-rep .nt-me-a .ph-ini{font-size:12px}'
        . 'html .cc .nt-me{width:30px;height:30px;border-radius:50%;object-fit:cover;vertical-align:middle;margin:0 8px 0 0;border:2px solid #12a150}'
        // the face beside the name, the name and time beside it on one line where they fit
        . 'html .cc .nt-rh{display:flex;align-items:center;flex-wrap:nowrap;gap:8px;margin:0 0 4px}html .cc .nt-rh .nt-me,html .cc .nt-rh .nt-me-a{flex:none;margin:0!important}html .cc .nt-rh b{min-width:0;line-height:1.25}html .cc .nt-rh small{flex:none}'
        . '@media (max-width:560px){html .cc .rs-card .nt-rep{margin-left:0}}'
        . 'html .cc .nt-box textarea[hidden]{display:none}html .cc .nt .nt-yours{margin-top:30px}'
        // the player
        . 'html .cc .nt-pl{display:flex;align-items:center;gap:12px;max-width:440px;margin:10px 0;padding:8px 14px 8px 8px;border-radius:999px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12)}'
        . 'html .cc .nt-pb{flex:none;width:44px;height:44px;min-height:0;padding:0;margin:0;border:0;border-radius:50%;background:#12a150;display:grid;place-items:center;cursor:pointer;box-shadow:0 4px 14px rgba(18,161,80,.35);transition:transform .15s ease,background .15s ease}'
        . 'html .cc .nt-pb:hover{transform:scale(1.06);background:#16b85c}html .cc .nt-pb svg{width:20px;height:20px;fill:#fff}html .cc .nt-pb .nt-pause,html .cc .nt-pl.on .nt-play{display:none}html .cc .nt-pl.on .nt-pause{display:block}'
        . 'html .cc .nt-bar{position:relative;flex:1;height:6px;border-radius:999px;background:rgba(255,255,255,.15);cursor:pointer;touch-action:none}'
        . 'html .cc .nt-bar i{position:absolute;inset:0 auto 0 0;width:0;border-radius:999px;background:linear-gradient(90deg,#12a150,#2bd47a)}'
        . 'html .cc .nt-bar b{position:absolute;top:50%;left:0;width:14px;height:14px;margin:-7px 0 0 -7px;border-radius:50%;background:#fff;box-shadow:0 1px 4px rgba(0,0,0,.5);opacity:0;transition:opacity .15s}'
        . 'html .cc .nt-pl.on .nt-bar b,html .cc .nt-bar:hover b{opacity:1}html .cc .nt-t{flex:none;min-width:42px;text-align:right;font:600 14px var(--body);color:#d0d6e0;font-variant-numeric:tabular-nums}</style>';
}
// Matteo 19 Nov: double tap (or double click) a message to ❤️ it, like on Instagram; again to take it back
function cc_nt_like_js() {
    return '<style>html .cc [data-lp]{touch-action:manipulation}html .cc .nt-like{display:inline-flex;align-items:center;gap:5px;margin:6px 0 0;padding:3px 10px;border-radius:999px;background:rgba(225,6,0,.12);font-size:15px;line-height:1.3}html .cc .nt-like[hidden]{display:none}html .cc .nt-like small{font-size:14px;color:#d0d6e0}'
        . 'html .cc .nt-pop{position:fixed;z-index:99999;font-size:64px;pointer-events:none;transform:translate(-50%,-50%) scale(.3);opacity:0;animation:ntPop .8s ease-out forwards}@keyframes ntPop{30%{transform:translate(-50%,-50%) scale(1.15);opacity:1}60%{transform:translate(-50%,-50%) scale(1)}100%{transform:translate(-50%,-70%) scale(1);opacity:0}}'
        . 'html .cc .nt-hint{margin:2px 0 10px;font-size:14px;color:#b8bec8}</style>'
        . '<script>(function(){if(window.ccNtLike)return;window.ccNtLike=1;var API=' . wp_json_encode(rest_url('cc/v1/note-like')) . ',NONCE=' . wp_json_encode(wp_create_nonce('wp_rest')) . ';'
        . 'function skip(t){return t.closest("button,a,audio,textarea,input,details summary,.nt-replyd,.nt-del");}'
        . 'function like(el,x,y){var cc=document.querySelector(".cc")||document.body,p=document.createElement("span");p.className="nt-pop";p.textContent="❤️";p.style.left=x+"px";p.style.top=y+"px";cc.appendChild(p);setTimeout(function(){p.remove();},900);'
        . 'fetch(API,{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json","X-WP-Nonce":NONCE},body:JSON.stringify({page:+el.dataset.lp,at:+el.dataset.la,ri:+el.dataset.lr})}).then(function(r){return r.ok?r.json():null;}).then(function(j){if(!j)return;'
        . 'var s=null;for(var i=0;i<el.children.length;i++)if(el.children[i].classList.contains("nt-like"))s=el.children[i];if(s)s.outerHTML=j.html;});}'
        . 'document.addEventListener("dblclick",function(e){var el=e.target.closest&&e.target.closest("[data-lp]");if(!el||skip(e.target))return;var r=e.target.closest(".nt-rep");if(r&&r!==el)return;e.preventDefault();like(el,e.clientX,e.clientY);});'
        . 'var last=0,lastEl=null;document.addEventListener("touchend",function(e){var el=e.target.closest&&e.target.closest("[data-lp]");if(!el||skip(e.target))return;var r=e.target.closest(".nt-rep");if(r)el=r;var now=Date.now();'
        . 'if(lastEl===el&&now-last<320){e.preventDefault();var t=e.changedTouches[0];like(el,t.clientX,t.clientY);last=0;lastEl=null;}else{last=now;lastEl=el;}},{passive:false});})();</script>';
}
add_action('rest_api_init', function () {
    register_rest_route('cc/v1', '/note-like', ['methods' => 'POST', 'permission_callback' => 'is_user_logged_in', 'callback' => function (WP_REST_Request $r) {
        $pid = (int) $r['page']; $at = (int) $r['at']; $ri = (int) $r['ri']; $coach = cc_ath_is_coach();
        if (!$coach && (int) get_post_meta($pid, 'cc_user', true) !== get_current_user_id()) return new WP_Error('cc_no', 'Not allowed', ['status' => 403]);
        $ns = cc_nt_get($pid); $role = $coach ? 'coach' : 'athlete'; $key = $ri < 0 ? 'n' : 'r' . $ri; $on = false; $author = '';
        foreach ($ns as &$n) {
            if ((int) $n['at'] !== $at) continue;
            if ($ri >= 0 && !isset(array_values((array) ($n['replies'] ?? []))[$ri])) return new WP_Error('cc_none', 'No such reply', ['status' => 404]);
            $author = $ri < 0 ? ((($n['from'] ?? '') === 'coach') ? 'coach' : 'athlete') : ((array_values($n['replies'])[$ri]['from'] ?? 'coach') === 'coach' ? 'coach' : 'athlete');
            $lk = (array) ($n['likes'][$key] ?? []); $on = empty($lk[$role]);
            if ($on) $lk[$role] = time(); else unset($lk[$role]);
            $n['likes'][$key] = $lk; $liked = $lk; break;
        }
        unset($n);
        if (!isset($liked)) return new WP_Error('cc_none', 'No such note', ['status' => 404]);
        cc_nt_put($pid, $ns);
        // Matteo liked the athlete's message: a quiet line in their bell (no phone buzz, no email)
        if ($on && $coach && $author === 'athlete' && function_exists('cc_inbox_add') && ($uid = (int) get_post_meta($pid, 'cc_user', true))) {
            $keep = $GLOBALS['cc_ath_lang'] ?? 'en'; $GLOBALS['cc_ath_lang'] = function_exists('cc_ath_user_lang') ? cc_ath_user_lang($uid) : 'en';
            cc_inbox_add($uid, '❤️ ' . cc_nt_w('liked_m'), '', home_url('/' . CC_ATH_SLUG . '/#notes'), 'cc-like');
            $GLOBALS['cc_ath_lang'] = $keep;
        }
        if (!$coach && function_exists('cc_ath_user_lang')) $GLOBALS['cc_ath_lang'] = cc_ath_user_lang(get_current_user_id());
        $html = cc_nt_likes($liked, $coach, get_the_title($pid));
        return ['ok' => true, 'on' => $on, 'html' => $html];
    }]);
});
function cc_nt_js() {
    static $done = false; if ($done) return ''; $done = true;
    return cc_nt_like_js() . <<<'JS'
<script>(function(){function ntInit(){document.querySelectorAll('.nt-box').forEach(function(A){var W=JSON.parse(A.dataset.w),L=A.dataset.lang,ta=A.querySelector('textarea'),
b=A.querySelector('.nt-rec'),st=A.querySelector('.nt-st'),go=A.querySelector('.nt-send'),m=A.querySelector('.nt-msg'),dy=A.querySelector('.nt-day input'),
rec=null,sr=null,chunks=[],blob=null,tr='',t0=0,tick=null;
function msg(t,e){m.textContent=t||'';m.classList.toggle('err',!!e);}
function lab(t){b.querySelector('span').textContent=t;}
/* Matteo 17 Nov: a voice note needs no text box: it hides while recording and while a recording waits to be sent */
function voice(on){if(!ta.value.trim())ta.hidden=on;}
b.addEventListener('click',function(){if(rec){rec.stop();return;}msg('');
 if(!navigator.mediaDevices||!window.MediaRecorder){msg(W.mic_no,true);return;}
 navigator.mediaDevices.getUserMedia({audio:true}).then(function(s){
  var type=['audio/webm;codecs=opus','audio/mp4','audio/webm'].filter(function(t){return MediaRecorder.isTypeSupported&&MediaRecorder.isTypeSupported(t);})[0];
  rec=new MediaRecorder(s,type?{mimeType:type,audioBitsPerSecond:32000}:undefined);chunks=[];rec.ondataavailable=function(e){if(e.data.size)chunks.push(e.data);};
  rec.onstop=function(){s.getTracks().forEach(function(t){t.stop();});blob=new Blob(chunks,{type:rec.mimeType||'audio/mp4'});rec=null;if(sr)try{sr.stop();}catch(x){}
   clearInterval(tick);b.classList.remove('on');b.setAttribute('aria-pressed','false');lab(W.rec);
   st.textContent=W.ready.replace('{s}',Math.round((Date.now()-t0)/1000));var x=document.createElement('button');x.type='button';x.textContent=W.del;x.onclick=function(){blob=null;tr='';st.textContent='';voice(false);};st.appendChild(x);};
  rec.start(1000);t0=Date.now();tr='';voice(true);b.classList.add('on');b.setAttribute('aria-pressed','true');lab(W.stop);
  tick=setInterval(function(){var n=Math.round((Date.now()-t0)/1000);st.textContent=W.listening.replace('{s}',n);if(n>=300&&rec)rec.stop();},500);
  /* the words are written out for Matteo only: nothing appears in the text box */
  /* Matteo 17 Nov: on iPhone the speech-to-text fights the recording for the microphone and kept stopping; restarting it at once
     looped and froze the phone. iPhone: no live writing-out (the recording is what counts); elsewhere: restarts spaced out and capped. */
  var SR=window.SpeechRecognition||window.webkitSpeechRecognition,done='',tries=0,ios=/iphone|ipad|ipod/i.test(navigator.userAgent)||(navigator.platform==='MacIntel'&&navigator.maxTouchPoints>1);
  if(SR&&!ios){sr=new SR();sr.lang=L;sr.continuous=true;sr.interimResults=true;
   sr.onresult=function(e){var t='';for(var i=0;i<e.results.length;i++)t+=e.results[i][0].transcript;tr=(done+' '+t).trim();};
   sr.onend=function(){done=tr;if(rec&&tries++<8)setTimeout(function(){if(rec)try{sr.start();}catch(x){}},700);};sr.onerror=function(){};try{sr.start();}catch(x){}}
 }).catch(function(){msg(W.mic_denied,true);});});
go.addEventListener('click',function(){if(rec){rec.stop();setTimeout(function(){go.click();},600);return;}var txt=ta.value.trim();if(!txt&&!blob){msg(W.empty,true);return;}
 go.disabled=true;msg(W.sending);var f=new FormData(),ex=JSON.parse(A.dataset.extra||'{}');Object.keys(ex).forEach(function(k){f.append(k,ex[k]);});
 f.append('text',txt);if(dy&&dy.value)f.append('day',dy.value);if(blob){f.append('audio',blob,'voice.'+(/mp4/.test(blob.type)?'m4a':'webm'));f.append('transcript',tr);}
 fetch(A.dataset.api,{method:'POST',body:f,credentials:'same-origin',headers:{'X-WP-Nonce':A.dataset.nonce}}).then(function(r){return r.json().then(function(j){return[r.ok,j];});})
 .then(function(x){if(!x[0])throw new Error();ta.value='';blob=null;tr='';st.textContent='';voice(false);if(dy)dy.value='';msg(W.sent);go.disabled=false;
  /* Matteo 17 Nov: show it straight away: reload and come back to the notes */
  setTimeout(function(){var u=location.href.split('#')[0];location.replace(u+(u.indexOf('?')>-1?'&':'?')+'nt='+Date.now()+(A.dataset.api.indexOf('result-reply')>-1?'#results':'#notes'));},900);})
 .catch(function(){go.disabled=false;msg(W.err,true);});});
});}
/* boxes further down the page (results) exist only once the page has loaded */
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',ntInit);else ntInit();
/* delete a note or a reply (asks first) */
document.addEventListener('click',function(e){var d=e.target.closest('.nt-del');if(!d||!confirm(d.dataset.q))return;var f=new FormData();f.append('page',d.dataset.page);f.append('at',d.dataset.at);f.append('ri',d.dataset.ri);
 fetch(d.dataset.api,{method:'POST',body:f,credentials:'same-origin',headers:{'X-WP-Nonce':d.dataset.nonce}}).then(function(r){if(!r.ok)throw 0;var el=d.dataset.ri==='-1'?d.closest('.nt-item'):d.closest('.nt-rep');if(el){if(d.dataset.ri==='-1'){var w=el.previousElementSibling;if(w&&w.classList.contains('nt-who'))w.remove();}el.remove();}}).catch(function(){alert('Not deleted. Please try again.');});});
/* the player: one sound at a time; recordings from phones can report no length at first, so it is worked out on load */
var cur=null;function fm(s){s=Math.max(0,Math.floor(s||0));return Math.floor(s/60)+':'+('0'+s%60).slice(-2);}
document.querySelectorAll('.nt-pl').forEach(function(P){var a=null,bar=P.querySelector('.nt-bar'),fill=bar.querySelector('i'),dot=bar.querySelector('b'),t=P.querySelector('.nt-t');
 function dur(){return a&&isFinite(a.duration)&&a.duration>0?a.duration:0;}
 function draw(){if(!a)return;var d=dur(),p=d?Math.min(1,a.currentTime/d):0;fill.style.width=(p*100)+'%';dot.style.left=(p*100)+'%';bar.setAttribute('aria-valuenow',Math.round(p*100));t.textContent=a.paused&&!a.currentTime&&d?fm(d):fm(a.currentTime);}
 function load(){if(a)return a;a=new Audio(P.dataset.src);a.preload='metadata';
  a.addEventListener('loadedmetadata',function(){if(!isFinite(a.duration)){a.currentTime=1e7;a.addEventListener('timeupdate',function f(){a.removeEventListener('timeupdate',f);a.currentTime=0;draw();});}draw();});
  a.addEventListener('timeupdate',draw);a.addEventListener('ended',function(){P.classList.remove('on');a.currentTime=0;draw();});return a;}
 P.querySelector('.nt-pb').addEventListener('click',function(){load();if(a.paused){if(cur&&cur!==P)cur.dispatchEvent(new Event('ntstop'));cur=P;a.play();P.classList.add('on');}else{a.pause();P.classList.remove('on');}});
 P.addEventListener('ntstop',function(){if(a){a.pause();P.classList.remove('on');}});
 function seek(e){load();var r=bar.getBoundingClientRect(),x=(e.touches?e.touches[0].clientX:e.clientX)-r.left,d=dur();if(d){a.currentTime=Math.max(0,Math.min(1,x/r.width))*d;draw();}}
 var drag=false;bar.addEventListener('pointerdown',function(e){drag=true;bar.setPointerCapture&&bar.setPointerCapture(e.pointerId);seek(e);});
 bar.addEventListener('pointermove',function(e){if(drag)seek(e);});bar.addEventListener('pointerup',function(){drag=false;});
 bar.addEventListener('keydown',function(e){load();var d=dur();if(!d)return;if(e.key==='ArrowRight')a.currentTime=Math.min(d,a.currentTime+5);if(e.key==='ArrowLeft')a.currentTime=Math.max(0,a.currentTime-5);draw();});
});
})();</script>
JS;
}

/* ---------- saving ---------- */
add_action('rest_api_init', function () {
    register_rest_route('cc/v1', '/note', ['methods' => 'POST', 'callback' => 'cc_nt_save', 'permission_callback' => function () { return is_user_logged_in() && (bool) cc_ath_page_of(get_current_user_id()) && !cc_ath_is_coach(); }]);
    // Matteo, or the athlete in a thread on their own page
    $own = function (WP_REST_Request $r) { return cc_ath_is_coach() || (is_user_logged_in() && (int) $r->get_param('page') === cc_ath_page_of(get_current_user_id())); };
    register_rest_route('cc/v1', '/note-reply', ['methods' => 'POST', 'callback' => 'cc_nt_reply', 'permission_callback' => $own]);
    // Matteo 18 Nov: a message he starts himself (text and/or voice); the athlete gets it in their notes, bell, phone and an email
    register_rest_route('cc/v1', '/coach-note', ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        $pid = (int) $r->get_param('page'); if (get_post_type($pid) !== 'cc_athlete') return new WP_Error('cc_none', 'No such athlete', ['status' => 404]);
        $text = cc_av_note((string) $r->get_param('text'), 3000); $aid = cc_nt_audio($r, $pid, ''); if (is_wp_error($aid)) return $aid;
        if ($text === '' && !$aid) return new WP_Error('cc_empty', 'Empty message', ['status' => 400]);
        $ns = cc_nt_get($pid); $ns[] = ['at' => time(), 'text' => $text, 'tr' => '', 'audio' => (int) $aid, 'day' => null, 'replies' => [], 'from' => 'coach']; cc_nt_put($pid, $ns);
        $uid = (int) get_post_meta($pid, 'cc_user', true); $u = $uid ? get_userdata($uid) : null;
        if ($u && is_email($u->user_email) && function_exists('cc_ath_mail_shell')) {
            $keep = $GLOBALS['cc_ath_lang'] ?? 'en'; $GLOBALS['cc_ath_lang'] = cc_ath_user_lang($uid);
            $to = strpos(home_url(), '//staging.') !== false ? (string) get_option('cc_staging_notify', '') : $u->user_email;   // staging: never an athlete
            $h = cc_ath_mail_shell(sprintf(cc_L('Hi %s,', 'Ciao %s,'), esc_html($u->first_name ?: $u->display_name)), esc_html(cc_nt_w('new_p')), esc_html(cc_nt_w('mail_btn')), home_url('/' . CC_ATH_SLUG . '/') . '#notes');
            if (is_email($to)) wp_mail($to, cc_nt_w('new_subj'), $h, ['Content-Type: text/html; charset=UTF-8', 'From: Matteo Cigala <coaching@cigalacycling.com>', 'Reply-To: Matteo Cigala <matteo@cigalacycling.com>']);
            if (function_exists('cc_push_user')) cc_push_user($uid, cc_nt_w('new_subj'), $text !== '' ? wp_trim_words($text, 18) : '🎙 ' . cc_nt_w('voice'), home_url('/' . CC_ATH_SLUG . '/') . '#nt-' . $pid . '-' . end($ns)['at'], 'cc-msg');
            $GLOBALS['cc_ath_lang'] = $keep;
        }
        return ['ok' => true];
    }]);
    register_rest_route('cc/v1', '/note-delete', ['methods' => 'POST', 'callback' => 'cc_nt_delete', 'permission_callback' => $own]);
    register_rest_route('cc/v1', '/notes', ['methods' => 'GET', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function () {   // the laptop (Vekta sync) and Matteo's tools
        $out = []; foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'meta_key' => 'cc_notes']) as $p) {
            $uid = (int) get_post_meta($p->ID, 'cc_user', true); $vid = $uid ? (string) get_user_meta($uid, 'cc_vekta_id', true) : '';
            foreach (cc_nt_get($p->ID) as $n) if (($n['from'] ?? '') !== 'coach') $out[] = ['page' => $p->ID,   // Matteo's own messages stay in the hub (not synced to Vekta) 'athlete' => $p->post_title, 'vekta_id' => $vid ?: null, 'at' => $n['at'], 'day' => $n['day'] ?? null,
                'text' => $n['text'] ?? '', 'transcript' => $n['tr'] ?? '', 'audio' => cc_nt_url($n['audio'] ?? 0) ?: null, 'replies' => count((array) ($n['replies'] ?? []))];
        }
        usort($out, function ($a, $b) { return $b['at'] <=> $a['at']; }); return $out;
    }]);
});
function cc_nt_audio($r, $pid, $tr) {
    $files = $r->get_file_params(); if (empty($files['audio']['tmp_name'])) return 0;
    return cc_av_store_audio($files['audio'], $pid, $tr);
}
function cc_nt_save(WP_REST_Request $r) {
    $uid = get_current_user_id(); $pid = cc_ath_page_of($uid);
    $ns = cc_nt_get($pid); $today = 0; foreach ($ns as $n) if ($n['at'] > time() - DAY_IN_SECONDS) $today++;
    if ($today >= 10) return new WP_Error('cc_many', 'Too many notes today.', ['status' => 429]);
    $text = cc_av_note((string) $r->get_param('text'), 3000); $tr = cc_av_str($r->get_param('transcript'), 3000);
    $aid = cc_nt_audio($r, $pid, $tr); if (is_wp_error($aid)) return $aid;
    if ($text === '' && !$aid) return new WP_Error('cc_empty', 'Empty note', ['status' => 400]);
    $day = cc_av_date((string) $r->get_param('day')); if ($day && $day > current_time('Y-m-d')) $day = '';
    $n = ['at' => time(), 'text' => $text, 'tr' => $aid ? $tr : '', 'audio' => (int) $aid, 'day' => $day ?: null, 'replies' => []]; $ns[] = $n;
    cc_nt_put($pid, $ns); update_post_meta($pid, 'cc_notes_updated', time());
    cc_nt_mail($pid, $uid, $n);
    if (function_exists('cc_push_coaches')) cc_push_coaches('Note from ' . get_the_title($pid), $text !== '' ? wp_trim_words($text, 18) : ($tr !== '' ? '🎙 ' . wp_trim_words($tr, 18) : '🎙 Voice note'), add_query_arg('board', 'notes', home_url('/' . CC_ATH_SLUG . '/')) . '#nt-' . $pid . '-' . $n['at'], 'cc-note', $pid);
    return ['ok' => true];
}
function cc_nt_delete(WP_REST_Request $r) {   // a note (ri -1) or one reply; athletes only their own, Matteo anything; the recordings go too
    $pid = (int) $r->get_param('page'); $at = (int) $r->get_param('at'); $ri = (int) $r->get_param('ri'); $coach = cc_ath_is_coach(); $ns = cc_nt_get($pid);
    foreach ($ns as $k => $n) {
        if ((int) $n['at'] !== $at) continue;
        if ($ri < 0) { foreach (array_merge([$n], (array) ($n['replies'] ?? [])) as $x) if (!empty($x['audio'])) wp_delete_attachment((int) $x['audio'], true); unset($ns[$k]); }
        else {
            $reps = array_values((array) ($n['replies'] ?? [])); if (!isset($reps[$ri])) return new WP_Error('cc_none', 'No such reply', ['status' => 404]);
            if (!$coach && ($reps[$ri]['from'] ?? 'coach') !== 'athlete') return new WP_Error('cc_no', 'Not yours', ['status' => 403]);
            if (!empty($reps[$ri]['audio'])) wp_delete_attachment((int) $reps[$ri]['audio'], true);
            array_splice($reps, $ri, 1); $ns[$k]['replies'] = $reps;
        }
        cc_nt_put($pid, $ns); return ['ok' => true];
    }
    return new WP_Error('cc_none', 'No such note', ['status' => 404]);
}
function cc_nt_reply(WP_REST_Request $r) {   // a reply in the thread: Matteo (shown in the athlete's hub + email/phone to them) or the athlete (email/phone to Matteo)
    $pid = (int) $r->get_param('page'); $at = (int) $r->get_param('at'); $ns = cc_nt_get($pid);
    $i = null; foreach ($ns as $k => $n) if ((int) $n['at'] === $at) $i = $k;
    if ($i === null) return new WP_Error('cc_none', 'No such note', ['status' => 404]);
    $text = cc_av_note((string) $r->get_param('text'), 3000);
    $aid = cc_nt_audio($r, $pid, cc_av_str($r->get_param('transcript'), 2000)); if (is_wp_error($aid)) return $aid;
    if ($text === '' && !$aid) return new WP_Error('cc_empty', 'Empty reply', ['status' => 400]);
    if (!cc_ath_is_coach()) {   // the athlete answering Matteo
        $tr = cc_av_str($r->get_param('transcript'), 2000);
        $ns[$i]['replies'][] = ['at' => time(), 'text' => $text, 'audio' => (int) $aid, 'from' => 'athlete', 'tr' => $aid ? $tr : '']; cc_nt_put($pid, $ns); update_post_meta($pid, 'cc_notes_updated', time());
        cc_nt_mail($pid, get_current_user_id(), ['text' => $text, 'tr' => $aid ? $tr : '', 'audio' => (int) $aid, 'day' => null], true);
        if (function_exists('cc_push_coaches')) cc_push_coaches('Reply from ' . get_the_title($pid), $text !== '' ? wp_trim_words($text, 18) : '🎙 Voice note', add_query_arg('board', 'notes', home_url('/' . CC_ATH_SLUG . '/')) . '#nt-' . $pid . '-' . $at, 'cc-note', $pid);
        return ['ok' => true];
    }
    $ns[$i]['replies'][] = ['at' => time(), 'text' => $text, 'audio' => (int) $aid, 'from' => 'coach']; cc_nt_put($pid, $ns);
    $uid = (int) get_post_meta($pid, 'cc_user', true); $u = $uid ? get_userdata($uid) : null;
    if ($u && is_email($u->user_email) && function_exists('cc_ath_mail_shell')) {
        $keep = $GLOBALS['cc_ath_lang'] ?? 'en'; $GLOBALS['cc_ath_lang'] = cc_ath_user_lang($uid);
        $to = strpos(home_url(), '//staging.') !== false ? (string) get_option('cc_staging_notify', '') : $u->user_email;   // staging: never an athlete
        $h = cc_ath_mail_shell(sprintf(cc_L('Hi %s,', 'Ciao %s,'), esc_html($u->first_name ?: $u->display_name)), esc_html(cc_nt_w('mail_p')), esc_html(cc_nt_w('mail_btn')), home_url('/' . CC_ATH_SLUG . '/') . '#notes');
        if (is_email($to)) wp_mail($to, cc_nt_w('mail_subj'), $h, ['Content-Type: text/html; charset=UTF-8', 'From: Matteo Cigala <coaching@cigalacycling.com>', 'Reply-To: Matteo Cigala <matteo@cigalacycling.com>']);
        // and on their phone, if they turned notifications on (push.php)
        if (function_exists('cc_push_user')) cc_push_user($uid, cc_nt_w('mail_subj'), $text !== '' ? wp_trim_words($text, 18) : '🎙 ' . cc_nt_w('voice'), home_url('/' . CC_ATH_SLUG . '/') . '#nt-' . $pid . '-' . $at, 'cc-reply');
        $GLOBALS['cc_ath_lang'] = $keep;
    }
    return ['ok' => true];
}
function cc_nt_mail($pid, $uid, $n, $isReply = false) {
    if (!function_exists('cc_av_notify_to') || !cc_av_notify_to()) return;
    $u = get_userdata($uid); $name = get_the_title($pid); $board = add_query_arg('board', 'notes', home_url('/' . CC_ATH_SLUG . '/'));
    $h = '<div style="font-family:Montserrat,Helvetica,Arial,sans-serif;font-size:16px;color:#222"><h2>' . ($isReply ? 'Reply from ' : 'Note from ') . esc_html($name) . '</h2>'
       . (!empty($n['day']) ? '<p style="margin:0 0 10px">About the session on <b>' . esc_html(date_i18n('j M Y', strtotime($n['day'] . ' 12:00'))) . '</b> (it goes into their Vekta calendar on that day).</p>' : '')
       . ($n['audio'] ? '<p style="margin:0 0 10px"><b>🎙 Voice note attached</b>: open the attachment to listen.</p>' : '')
       . ($n['text'] !== '' ? '<blockquote style="margin:0 0 16px;padding:10px 14px;background:#f2f4f3;border-left:3px solid #009a44;white-space:pre-line">' . esc_html($n['text']) . '</blockquote>' : '')
       . ($n['tr'] !== '' ? '<p style="margin:0 0 6px;color:#555">Written out from the voice note (automatic, may have mistakes):</p><blockquote style="margin:0 0 16px;padding:10px 14px;background:#f2f4f3;border-left:3px solid #9aa0a6;white-space:pre-line">' . esc_html($n['tr']) . '</blockquote>' : '')
       . '<p style="margin:20px 0 0"><a href="' . esc_url($board) . '" style="display:inline-block;padding:12px 20px;border-radius:8px;background:#009a44;color:#fff;font-weight:600;text-decoration:none">Reply in the hub</a></p></div>';
    $hd = ['Content-Type: text/html; charset=UTF-8']; if ($u && is_email($u->user_email)) $hd[] = 'Reply-To: ' . $name . ' <' . $u->user_email . '>';
    if (function_exists('cc_ath_coach_wrap')) $h = cc_ath_coach_wrap($h);
    wp_mail(cc_av_notify_to(), ($isReply ? 'Reply from ' : 'Note from ') . $name . ($n['audio'] ? ' (voice)' : ''), $h, $hd, array_filter($n['audio'] ? [get_attached_file((int) $n['audio'])] : []));
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
    $o = '<section class="ath-s nt"><h2>' . cc_ath_icon('mic', 'ath-hic') . 'Notes</h2><p class="av-lede">Notes and voice notes from your athletes, newest first. Tap Reply to answer by typing or with a voice note: they see it in their hub and get an email.</p>';
    if (!$all) return $o . '<p class="av-lede">No notes yet.</p></section>' . cc_nt_css();
    foreach (array_slice($all, 0, 80) as [$p, $n]) $o .= '<div class="nt-who">' . (function_exists('cc_ph_face') ? cc_ph_face($p->ID, 30) . ' ' : '') . '<b><a style="color:#fff" href="' . esc_url(add_query_arg('view', $p->ID, home_url('/' . CC_ATH_SLUG . '/'))) . '">' . esc_html($p->post_title) . '</a></b>' . '</div>' . cc_nt_item($n, true, $p->ID);
    return $o . '</section>' . cc_nt_css() . cc_nt_js();
}, 10, 2);
