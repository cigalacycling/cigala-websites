<?php
if (!defined('ABSPATH')) return;
/* Matteo, 17 Nov 2026:
 * 1. "How to use your hub": a short guide at the top of every athlete's hub (Vekta or TrainingPeaks version), foldable.
 * 2. "News from Matteo": announcements (Q&A sessions, camps…) at the top of the hub, for everyone or a group, in each athlete's
 *    language (all four texts are required, so nobody ever reads it in the wrong language), optional button and phone notification.
 *    Posted on the News board, or by Claude with POST /wp-json/cc/v1/news. Athletes tap "Got it" to hide one.
 * 3. A new blog post: a phone notification to athletes who turned them on (Italian posts to Italian readers, the others to the rest). */

function cc_nw_w($k) {
    static $W = [
        'g_title' => ['en' => 'How to use your hub', 'it' => 'Come usare la tua area', 'pt' => 'Como usar a tua área', 'sl' => 'Kako uporabljati svoje središče', 'sk' => 'Ako používať svoju zónu'],
        'g_train_v' => ['en' => '🚴 <b>Your training</b> (plan, workouts, comments on a specific ride): in <a href="https://app.joinvekta.com/" target="_blank" rel="noopener">Vekta</a>', 'it' => '🚴 <b>Il tuo allenamento</b> (piano, allenamenti, commenti su un’uscita specifica): su <a href="https://app.joinvekta.com/" target="_blank" rel="noopener">Vekta</a>',
                        'pt' => '🚴 <b>O teu treino</b> (plano, treinos, comentários sobre um treino específico): no <a href="https://app.joinvekta.com/" target="_blank" rel="noopener">Vekta</a>', 'sl' => '🚴 <b>Tvoj trening</b> (načrt, treningi, komentarji k določeni vožnji): v <a href="https://app.joinvekta.com/" target="_blank" rel="noopener">Vekti</a>', 'sk' => '🚴 <b>Tvoj tréning</b> (plán, tréningy, komentáre ku konkrétnej jazde): vo <a href="https://app.joinvekta.com/" target="_blank" rel="noopener">Vekte</a>'],
        'g_train_t' => ['en' => '🚴 <b>Your training</b> (plan, workouts, comments on a specific ride): in <a href="https://app.trainingpeaks.com/" target="_blank" rel="noopener">TrainingPeaks</a>', 'it' => '🚴 <b>Il tuo allenamento</b> (piano, allenamenti, commenti su un’uscita specifica): su <a href="https://app.trainingpeaks.com/" target="_blank" rel="noopener">TrainingPeaks</a>',
                        'pt' => '🚴 <b>O teu treino</b> (plano, treinos, comentários sobre um treino específico): no <a href="https://app.trainingpeaks.com/" target="_blank" rel="noopener">TrainingPeaks</a>', 'sl' => '🚴 <b>Tvoj trening</b> (načrt, treningi, komentarji k določeni vožnji): v <a href="https://app.trainingpeaks.com/" target="_blank" rel="noopener">TrainingPeaks</a>', 'sk' => '🚴 <b>Tvoj tréning</b> (plán, tréningy, komentáre ku konkrétnej jazde): v <a href="https://app.trainingpeaks.com/" target="_blank" rel="noopener">TrainingPeaks</a>'],
        'g_note' => ['en' => '🎙 <b>How your week is going</b>: <a href="#notes">Leave me a note</a> (text or voice)', 'it' => '🎙 <b>Come va la tua settimana</b>: <a href="#notes">Lasciami un messaggio</a> (testo o vocale)',
                     'pt' => '🎙 <b>Como está a correr a tua semana</b>: <a href="#notes">Deixa-me uma mensagem</a> (texto ou voz)', 'sl' => '🎙 <b>Kako gre tvoj teden</b>: <a href="#notes">Pusti mi sporočilo</a> (besedilo ali glas)', 'sk' => '🎙 <b>Ako ti ide týždeň</b>: <a href="#notes">Nechaj mi správu</a> (text alebo hlas)'],
        'g_res' => ['en' => '🏆 <b>A result you are proud of</b>: <a href="#results">Share a result</a>', 'it' => '🏆 <b>Un risultato di cui sei fiero</b>: <a href="#results">Condividi un risultato</a>',
                    'pt' => '🏆 <b>Um resultado de que te orgulhas</b>: <a href="#results">Partilha um resultado</a>', 'sl' => '🏆 <b>Rezultat, na katerega si ponosen</b>: <a href="#results">Deli rezultat</a>', 'sk' => '🏆 <b>Výsledok, ktorý ťa teší</b>: <a href="#results">Pochváľ sa výsledkom</a>'],
        // Matteo 18 Nov: blood tests, private, kept as history
        'g_blood' => ['en' => '🩸 <b>Your blood tests</b>: <a href="#blood">upload them privately</a>, kept as your history', 'it' => '🩸 <b>Le tue analisi del sangue</b>: <a href="#blood">caricale in privato</a>, restano come tuo storico',
                      'pt' => '🩸 <b>As tuas análises ao sangue</b>: <a href="#blood">carrega-as em privado</a>, ficam como o teu histórico', 'sl' => '🩸 <b>Tvoji krvni izvidi</b>: <a href="#blood">naloži jih zasebno</a>, ostanejo kot tvoja zgodovina', 'sk' => '🩸 <b>Tvoje krvné testy</b>: <a href="#blood">nahraj ich súkromne</a>, zostanú ako tvoja história'],
        'g_av' => ['en' => '📅 <b>Your availability and races</b>: keep <a href="#availability">your availability</a> and <a href="#goals">your races</a> up to date here. They go into your Vekta calendar automatically.',
                   'it' => '📅 <b>La tua disponibilità e le gare</b>: tieni aggiornate qui <a href="#availability">la tua disponibilità</a> e <a href="#goals">le tue gare</a>. Finiscono automaticamente nel tuo calendario Vekta.',
                   'pt' => '📅 <b>A tua disponibilidade e as provas</b>: mantém aqui atualizadas <a href="#availability">a tua disponibilidade</a> e <a href="#goals">as tuas provas</a>. Passam automaticamente para o teu calendário Vekta.',
                   'sl' => '📅 <b>Tvoja razpoložljivost in tekme</b>: tu sproti posodabljaj <a href="#availability">svojo razpoložljivost</a> in <a href="#goals">svoje tekme</a>. Samodejno se prenesejo v tvoj koledar Vekta.', 'sk' => '📅 <b>Tvoja dostupnosť a preteky</b>: tu priebežne aktualizuj <a href="#availability">svoju dostupnosť</a> a <a href="#goals">svoje preteky</a>. Automaticky sa prenesú do tvojho kalendára Vekta.'],
        'g_rep' => ['en' => '📄 <b>Your reports and guides</b>: <a href="#reports">your reports</a> and the training guides, all here', 'it' => '📄 <b>I tuoi report e le guide</b>: <a href="#reports">i tuoi report</a> e le guide di allenamento, tutto qui',
                    'pt' => '📄 <b>Os teus relatórios e guias</b>: <a href="#reports">os teus relatórios</a> e os guias de treino, tudo aqui', 'sl' => '📄 <b>Tvoja poročila in vodiči</b>: <a href="#reports">tvoja poročila</a> in vodiči za trening, vse tukaj', 'sk' => '📄 <b>Tvoje reporty a návody</b>: <a href="#reports">tvoje reporty</a> a tréningové návody, všetko tu'],
        'g_wa' => ['en' => '💬 <b>Something urgent</b>: <a href="https://wa.me/353834777697" target="_blank" rel="noopener">WhatsApp me</a>', 'it' => '💬 <b>Qualcosa di urgente</b>: <a href="https://wa.me/353834777697" target="_blank" rel="noopener">scrivimi su WhatsApp</a>',
                   'pt' => '💬 <b>Algo urgente</b>: <a href="https://wa.me/353834777697" target="_blank" rel="noopener">envia-me WhatsApp</a>', 'sl' => '💬 <b>Nekaj nujnega</b>: <a href="https://wa.me/353834777697" target="_blank" rel="noopener">piši mi na WhatsApp</a>', 'sk' => '💬 <b>Niečo súrne</b>: <a href="https://wa.me/353834777697" target="_blank" rel="noopener">napíš mi na WhatsApp</a>'],
        'news' => ['en' => 'News from Matteo', 'it' => 'Novità da Matteo', 'pt' => 'Novidades do Matteo', 'sl' => 'Novice od Mattea', 'sk' => 'Novinky od Mattea'],
        'got' => ['en' => 'Got it', 'it' => 'Ok, letto', 'pt' => 'Entendido', 'sl' => 'Razumem', 'sk' => 'Rozumiem'],
        'more' => ['en' => 'Find out more', 'it' => 'Scopri di più', 'pt' => 'Saber mais', 'sl' => 'Več o tem', 'sk' => 'Zistiť viac'],
        'blog' => ['en' => 'New on the blog', 'it' => 'Nuovo sul blog', 'pt' => 'Novo no blog', 'sl' => 'Novo na blogu', 'sk' => 'Nové na blogu'],
    ];
    $l = $GLOBALS['cc_ath_lang'] ?? 'en'; return $W[$k][$l] ?? $W[$k]['en'];
}
const CC_NW_LANGS = ['en', 'it', 'pt', 'sl', 'sk'];
// Matteo 17 Nov: each athlete's time zone (sent by their browser when they open the hub), for event times in emails / notifications
add_action('rest_api_init', function () {
    register_rest_route('cc/v1', '/tz', ['methods' => 'POST', 'permission_callback' => 'is_user_logged_in', 'callback' => function (WP_REST_Request $r) {
        $tz = (string) $r->get_param('tz'); if (!in_array($tz, timezone_identifiers_list(), true)) return new WP_Error('cc_tz', 'Unknown time zone', ['status' => 400]);
        update_user_meta(get_current_user_id(), 'cc_tz', $tz); return ['ok' => true];
    }]);
});
// "Thu 20 Nov, 21:00" in the athlete's language and time zone (Irish time when unknown)
function cc_nw_when($utc, $uid, $l) {
    $tz = $uid ? (string) get_user_meta($uid, 'cc_tz', true) : ''; $known = $tz !== '';
    try { $d = new DateTime('@' . (int) $utc); $d->setTimezone(new DateTimeZone($known ? $tz : 'Europe/Dublin')); } catch (Exception $e) { return ''; }
    $loc = ['en' => 'en_GB', 'it' => 'it_IT', 'pt' => 'pt_PT', 'sl' => 'sl_SI', 'sk' => 'sk_SK'][$l] ?? 'en_GB';
    if (class_exists('IntlDateFormatter')) { $f = new IntlDateFormatter($loc, IntlDateFormatter::FULL, IntlDateFormatter::SHORT, $d->getTimezone()->getName(), null, 'EEEE d MMMM, HH:mm'); $s = $f->format($d); }
    else $s = $d->format('l j F, H:i');
    $suffix = $known ? ['en' => 'your time', 'it' => 'ora locale', 'pt' => 'hora local', 'sl' => 'tvoj čas', 'sk' => 'tvoj čas'][$l] ?? 'your time' : ['en' => 'Irish time', 'it' => 'ora irlandese', 'pt' => 'hora da Irlanda', 'sl' => 'irski čas', 'sk' => 'írsky čas'][$l] ?? 'Irish time';
    return '🕗 ' . $s . ' (' . $suffix . ')';
}
function cc_nw_all() { $a = get_option('cc_news', []); return is_array($a) ? $a : []; }
function cc_nw_for($pid) {   // the news this athlete should see (audience match), newest first
    $tp = function_exists('cc_ath_tp') && cc_ath_tp($pid); $uid = (int) get_post_meta($pid, 'cc_user', true); $l = $uid ? cc_ath_lang_code($uid) : 'en';
    $out = [];
    foreach (array_reverse(cc_nw_all()) as $n) {
        // Matteo 17 Nov: news ends by itself: 2 hours after its event time, or 14 days after posting when it has none
        if (!empty($n['when']) ? (int) $n['when'] < time() - 2 * HOUR_IN_SECONDS : (int) $n['at'] < time() - 14 * DAY_IN_SECONDS) continue;
        $aud = $n['aud'] ?? 'all';
        if ($aud === 'vekta' && $tp) continue; if ($aud === 'tp' && !$tp) continue; if (strpos($aud, 'lang:') === 0 && substr($aud, 5) !== $l) continue;
        if (strpos($aud, 'page:') === 0 && (int) substr($aud, 5) !== (int) $pid) continue;   // one athlete (e.g. a test)
        if (empty($n['t'][$l])) continue;   // never in the wrong language
        $out[] = $n;
    }
    return $out;
}

// top of the hub (after the phone / home-screen cards): the guide, then the news
add_filter('cc_ath_before_reports', function ($html, $view, $coach) {
    if (!$view) return $html;
    $tp = function_exists('cc_ath_tp') && cc_ath_tp($view);
    $lines = [cc_nw_w($tp ? 'g_train_t' : 'g_train_v'), cc_nw_w('g_note'), cc_nw_w('g_res'), cc_nw_w('g_blood')];
    if (!$tp) $lines[] = cc_nw_w('g_av');
    $lines[] = cc_nw_w('g_rep'); $lines[] = cc_nw_w('g_wa');
    $o = '<details class="nw-guide" id="nw-guide" open><summary>' . esc_html(cc_nw_w('g_title')) . '</summary><ul>' . implode('', array_map(function ($x) { return '<li>' . wp_kses($x, ['b' => [], 'a' => ['href' => [], 'target' => [], 'rel' => []]]) . '</li>'; }, $lines)) . '</ul></details>';
    foreach (array_slice(cc_nw_for($view), 0, 3) as $n) {
        $l = $GLOBALS['cc_ath_lang'] ?? 'en'; $t = $n['t'][$l] ?? ($n['t']['en'] ?? []);
        $o .= '<div class="nw-card" data-id="' . esc_attr($n['id']) . '" hidden>' . (!empty($n['img']) ? '<img src="' . esc_url($n['img']) . '" alt="">' : '')
            . '<div><p class="nw-eb">📣 ' . esc_html(cc_nw_w('news')) . ' · ' . esc_html(date_i18n('j M', (int) $n['at'])) . '</p><b>' . esc_html($t['title'] ?? '') . '</b>'
            // the event time: Irish time from the server, then the browser rewrites it in the viewer's own time zone
            . (!empty($n['when']) ? '<p class="nw-when" data-utc="' . (int) $n['when'] . '" data-loc="' . esc_attr(['en' => 'en-GB', 'it' => 'it-IT', 'pt' => 'pt-PT', 'sl' => 'sl-SI', 'sk' => 'sk-SK'][$l] ?? 'en-GB') . '" data-mine="' . esc_attr(['en' => 'your time', 'it' => 'ora locale', 'pt' => 'hora local', 'sl' => 'tvoj čas', 'sk' => 'tvoj čas'][$l] ?? 'your time') . '">'
                . esc_html(cc_nw_when($n['when'], 0, $l)) . '</p>' : '')
            . (($t['body'] ?? '') !== '' ? '<p>' . nl2br(esc_html($t['body'])) . '</p>' : '')
            . '<span class="nw-acts">' . (!empty($n['url']) ? '<a class="btn btn-go" href="' . esc_url($n['url']) . '" target="_blank" rel="noopener">' . esc_html(($t['btn'] ?? '') !== '' ? $t['btn'] : cc_nw_w('more')) . '</a>' : '')
            . '<button type="button" class="btn btn-ghost nw-got">' . esc_html(cc_nw_w('got')) . '</button></span></div></div>'
            // after "Got it": a slim one-line reminder that opens it again (Matteo 17 Nov: keep reminding until it is over)
            . '<button type="button" class="nw-mini" data-id="' . esc_attr($n['id']) . '" hidden>📣 <b>' . esc_html($t['title'] ?? '') . '</b>' . (!empty($n['when']) ? ' <span class="nw-when nw-when-mini" data-utc="' . (int) $n['when'] . '" data-loc="' . esc_attr(['en' => 'en-GB', 'it' => 'it-IT', 'pt' => 'pt-PT', 'sl' => 'sl-SI', 'sk' => 'sk-SK'][$l] ?? 'en-GB') . '" data-mine="' . esc_attr(['en' => 'your time', 'it' => 'ora locale', 'pt' => 'hora local', 'sl' => 'tvoj čas', 'sk' => 'tvoj čas'][$l] ?? 'your time') . '"></span>' : '') . '<i aria-hidden="true">›</i></button>';
    }
    return $html . $o
        . '<style>html .cc .nw-guide{margin:0 0 14px;padding:12px 16px;border-radius:12px;border:1px solid rgba(255,255,255,.12);background:rgba(255,255,255,.04)}html .cc .nw-guide summary{cursor:pointer;font-weight:700;font-size:16px;color:#fff;list-style:none;display:flex;align-items:center;justify-content:space-between;gap:12px}'
        . 'html .cc .nw-guide summary::-webkit-details-marker{display:none}html .cc .nw-guide summary::after{content:"";width:9px;height:9px;border-right:2.5px solid #2bd47a;border-bottom:2.5px solid #2bd47a;transform:rotate(45deg);margin:-4px 4px 0 0;transition:transform .2s}'
        . 'html .cc .nw-guide[open] summary::after{transform:rotate(-135deg);margin-top:4px}'
        . 'html .cc .nw-guide ul{margin:10px 0 2px;padding:0;list-style:none;display:grid;gap:8px}html .cc .nw-guide li{font-size:16px;color:var(--text-2);line-height:1.45}html .cc .nw-guide b{color:#fff}html .cc .nw-guide a{color:#2bd47a;text-decoration:underline;text-underline-offset:3px;font-weight:600}'
        . 'html .cc .nw-card{display:flex;gap:14px;align-items:flex-start;margin:0 0 14px;padding:14px 16px;border-radius:14px;border:1px solid rgba(43,212,122,.45);background:linear-gradient(135deg,rgba(18,161,80,.16),rgba(18,161,80,.04))}html .cc .nw-card[hidden]{display:none!important}'
        . 'html .cc .nw-card img{width:84px;height:84px;border-radius:12px;object-fit:cover;flex:none}html .cc .nw-eb{margin:0 0 4px;font-size:14px;color:#2bd47a;font-weight:700;letter-spacing:.04em;text-transform:uppercase}'
        . 'html .cc .nw-card b{display:block;font-size:18px;color:#fff}html .cc .nw-card p{margin:6px 0 0;font-size:16px;color:var(--text-2)}html .cc .nw-acts{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}html .cc .nw-acts .btn{width:auto;margin:0}'
        . 'html .cc .nw-mini{display:flex;align-items:center;gap:8px;width:100%;margin:0 0 14px;padding:10px 14px;min-height:0;border-radius:12px;border:1px solid rgba(43,212,122,.45);background:rgba(18,161,80,.10);color:var(--text-2);font:500 15px var(--body);text-align:left;cursor:pointer}'
        . 'html .cc .nw-mini[hidden]{display:none!important}html .cc .nw-mini b{color:#fff;font-weight:700}html .cc .nw-mini i{margin-left:auto;font-style:normal;color:#2bd47a;font-size:22px;line-height:1}'
        . '@media (max-width:560px){html .cc .nw-card{flex-direction:column}html .cc .nw-card img{width:100%;height:160px}}</style>'
        . '<script>(function(){function g(k){try{return localStorage.getItem(k);}catch(e){return null;}}function s(k,v){try{localStorage.setItem(k,v);}catch(e){}}'
        // Matteo 17 Nov: open on the first visit only; afterwards folded (tap the title to open it again)
        . 'var d=document.getElementById("nw-guide");if(d){if(g("cc_guide_seen"))d.open=false;else s("cc_guide_seen","1");}'
        . 'document.querySelectorAll(".nw-card").forEach(function(c){var mini=document.querySelector(".nw-mini[data-id=\'"+c.dataset.id+"\']");'
        . 'function fold(){c.hidden=true;if(mini)mini.hidden=false;}if(g("cc_news_"+c.dataset.id))fold();else c.hidden=false;'
        . 'c.querySelector(".nw-got").addEventListener("click",function(){s("cc_news_"+c.dataset.id,"1");fold();});'
        . 'if(mini)mini.addEventListener("click",function(){mini.hidden=true;c.hidden=false;});});'
        // event times in the viewer's own time zone; and the hub remembers that zone for emails / notifications
        . 'document.querySelectorAll(".nw-when").forEach(function(p){try{var d=new Date(1000*p.dataset.utc);if(p.classList.contains("nw-when-mini")){p.textContent="· "+d.toLocaleString(p.dataset.loc,{weekday:"short",hour:"2-digit",minute:"2-digit"});return;}p.textContent="🕗 "+d.toLocaleString(p.dataset.loc,{weekday:"long",day:"numeric",month:"long",hour:"2-digit",minute:"2-digit"})+" ("+p.dataset.mine+")";}catch(e){}});'
        . 'try{var tz=Intl.DateTimeFormat().resolvedOptions().timeZone;if(tz&&g("cc_tz")!==tz){fetch("' . esc_url(rest_url('cc/v1/tz')) . '",{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json","X-WP-Nonce":"' . esc_attr(wp_create_nonce('wp_rest')) . '"},body:JSON.stringify({tz:tz})}).then(function(r){if(r.ok)s("cc_tz",tz);});}}catch(e){}'
        . '})();</script>';
}, 3, 3);

/* ---------- posting: News board and POST /wp-json/cc/v1/news ---------- */
function cc_nw_post($in) {   // ['aud', 'url', 'img', 'push', 't' => [lang => [title, body, btn]]] -> the item, or WP_Error
    $aud = (string) ($in['aud'] ?? 'all'); if (!in_array($aud, ['all', 'vekta', 'tp'], true) && !preg_match('/^(lang:(en|it|pt|sl|sk)|page:\d+)$/', $aud)) $aud = 'all';
    if (strpos($aud, 'page:') === 0) { $pu = (int) get_post_meta((int) substr($aud, 5), 'cc_user', true); $need = [$pu ? cc_ath_lang_code($pu) : 'en']; }
    else $need = strpos($aud, 'lang:') === 0 ? [substr($aud, 5)] : CC_NW_LANGS;
    $t = [];
    foreach (CC_NW_LANGS as $l) { $x = (array) ($in['t'][$l] ?? []); $title = cc_av_str($x['title'] ?? '', 140); if ($title === '') continue;
        $t[$l] = ['title' => $title, 'body' => cc_av_note($x['body'] ?? '', 1500), 'btn' => cc_av_str($x['btn'] ?? '', 40)]; }
    foreach ($need as $l) if (empty($t[$l])) return new WP_Error('cc_lang', 'Missing the ' . strtoupper($l) . ' text: every athlete reads news in their own language', ['status' => 400]);
    $when = 0;   // optional event time, entered in Irish time ("YYYY-MM-DDTHH:MM"), stored as UTC
    if (preg_match('/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/', (string) ($in['when'] ?? ''))) { try { $when = (new DateTime(substr($in['when'], 0, 16), new DateTimeZone('Europe/Dublin')))->getTimestamp(); } catch (Exception $e) { $when = 0; } }
    $n = ['id' => wp_generate_password(8, false, false), 'at' => time(), 'aud' => $aud, 'url' => esc_url_raw((string) ($in['url'] ?? '')), 'img' => esc_url_raw((string) ($in['img'] ?? '')), 'when' => $when, 't' => $t];
    $all = cc_nw_all(); $all[] = $n; update_option('cc_news', array_slice($all, -30), false);
    // everyone in the audience: the notification centre (and their phone if they turned it on); an email only to athletes who
    // already set their hub password (Matteo 17 Nov: athletes not invited to the hub yet never get an email)
    $sent = 0;
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'meta_key' => 'cc_user', 'fields' => 'ids']) as $pid) {
        $uid = (int) get_post_meta($pid, 'cc_user', true); $u = $uid ? get_userdata($uid) : null; if (!$u || user_can($uid, 'edit_pages')) continue;
        $mine = false; foreach (cc_nw_for($pid) as $x) if ($x['id'] === $n['id']) $mine = true; if (!$mine) continue;
        $l = cc_ath_lang_code($uid); $keep = $GLOBALS['cc_ath_lang'] ?? 'en'; $GLOBALS['cc_ath_lang'] = $l; $tt = $t[$l];
        $wh = $when ? cc_nw_when($when, $uid, $l) : '';   // the event time in their own time zone
        if (!empty($in['push']) && function_exists('cc_push_user')) cc_push_user($uid, '📣 ' . $tt['title'], $wh !== '' ? $wh : wp_trim_words($tt['body'], 18), home_url('/' . CC_ATH_SLUG . '/'), 'cc-news-' . $n['id']);
        if (!empty($in['email']) && get_user_meta($uid, 'cc_pw_set', true) && is_email($u->user_email) && function_exists('cc_ath_mail_shell')) {
            $to = strpos(home_url(), '//staging.') !== false ? (string) get_option('cc_staging_notify', '') : $u->user_email;
            $h = cc_ath_mail_shell(sprintf(cc_L('Hi %s,', 'Ciao %s,'), esc_html($u->first_name ?: $u->display_name)), '<b>' . esc_html($tt['title']) . '</b>' . ($wh !== '' ? '<br><b style="color:#12a150">' . esc_html($wh) . '</b>' : '') . '<br>' . nl2br(esc_html($tt['body'])),
                esc_html($tt['btn'] !== '' ? $tt['btn'] : cc_nw_w('more')), $n['url'] ?: home_url('/' . CC_ATH_SLUG . '/'));
            if (is_email($to) && wp_mail($to, '📣 ' . $tt['title'], $h, ['Content-Type: text/html; charset=UTF-8', 'From: Matteo Cigala <coaching@cigalacycling.com>', 'Reply-To: Matteo Cigala <matteo@cigalacycling.com>'])) $sent++;
        }
        $GLOBALS['cc_ath_lang'] = $keep;
    }
    $n['emailed'] = $sent;
    return $n;
}
add_action('rest_api_init', function () {
    register_rest_route('cc/v1', '/news', [
        ['methods' => 'GET', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function () { return array_reverse(cc_nw_all()); }],
        ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) { $n = cc_nw_post($r->get_json_params() ?: $r->get_params()); return is_wp_error($n) ? $n : ['ok' => true, 'id' => $n['id'], 'emailed' => $n['emailed']]; }],
    ]);
    register_rest_route('cc/v1', '/news/(?P<id>[A-Za-z0-9]+)', ['methods' => 'DELETE', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        update_option('cc_news', array_values(array_filter(cc_nw_all(), function ($n) use ($r) { return $n['id'] !== $r['id']; })), false); return ['ok' => true];
    }]);
});
add_filter('cc_ath_coach_links', function ($html) { return $html . '<a class="av-boardlink" href="' . esc_url(add_query_arg('board', 'news', home_url('/' . CC_ATH_SLUG . '/'))) . '">News</a>'; }, 14);
add_filter('cc_ath_board', function ($html, $board) {
    if ($board !== 'news' || !cc_ath_is_coach()) return $html;
    $r = sanitize_key($_GET['nw'] ?? ''); $err = (string) get_transient('cc_nw_err');
    $o = '<section class="ath-s"><h2>📣 News for your athletes</h2><p class="av-lede">An announcement at the top of their hub (a Q&amp;A, a camp, a change…), with an optional button and phone notification. '
       . 'Every athlete reads it in their own language, so fill in all four (or tell Claude in chat “Announce: …” and it is translated and posted for you).</p>'
       . ($r === 'ok' ? '<p class="rp-smtp-m">Posted.</p>' : '') . ($r === 'bad' ? '<p class="rp-smtp-m" style="color:#ff4a3d">' . esc_html($err) . '</p>' : '')
       . '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" class="nw-form"><input type="hidden" name="action" value="cc_news">' . wp_nonce_field('cc_news', '_wpnonce', false, false)
       . '<label>Who sees it <select name="aud"><option value="all">Everyone</option><option value="vekta">Vekta athletes</option><option value="tp">TrainingPeaks athletes</option>'
       . '<option value="lang:en">English readers</option><option value="lang:it">Italian readers</option><option value="lang:pt">Portuguese readers</option><option value="lang:sl">Slovenian readers</option><option value="lang:sk">Slovak readers</option></select></label>';
    foreach (['en' => 'English', 'it' => 'Italiano', 'pt' => 'Português', 'sl' => 'Slovenščina', 'sk' => 'Slovenčina'] as $l => $nm)
        $o .= '<fieldset><legend>' . $nm . '</legend><input name="t[' . $l . '][title]" maxlength="140" placeholder="Title"><textarea name="t[' . $l . '][body]" rows="3" placeholder="Message"></textarea><input name="t[' . $l . '][btn]" maxlength="40" placeholder="Button text (optional)"></fieldset>';
    $o .= '<label>Event date &amp; time, Irish time (optional): each athlete sees it in their own time zone <input name="when" type="datetime-local"></label>'
       . '<label>Button link (optional) <input name="url" type="url" placeholder="https://"></label><label class="nw-tick"><input type="checkbox" name="push" value="1" checked> Also send a phone notification</label>'
       . '<label class="nw-tick"><input type="checkbox" name="email" value="1" checked> Also email it (only to athletes who already use the hub, i.e. set their password)</label>'
       . '<button class="btn btn-go" type="submit">Post the news</button></form>';
    $all = array_reverse(cc_nw_all());
    if ($all) { $o .= '<h3 class="av-sub">Posted</h3>'; foreach ($all as $n) $o .= '<div class="nt-item"><small>' . esc_html(date_i18n('j M Y, H:i', (int) $n['at']) . ' · ' . $n['aud']) . '</small><p><b>' . esc_html($n['t']['en']['title'] ?? reset($n['t'])['title']) . '</b></p>'
        . '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="cc_news_del"><input type="hidden" name="id" value="' . esc_attr($n['id']) . '">' . wp_nonce_field('cc_news', '_wpnonce', false, false) . '<button class="btn btn-ghost" type="submit" onclick="return confirm(\'Remove this news from every hub?\')">Remove</button></form></div>'; }
    return $o . '</section><style>html .cc .nw-form{display:grid;gap:12px;max-width:640px}html .cc .nw-form label{display:grid;gap:6px;font-size:15px;color:#d0d6e0;font-weight:600}html .cc .nw-form fieldset{border:1px solid rgba(255,255,255,.12);border-radius:12px;padding:10px 12px;display:grid;gap:8px}'
        . 'html .cc .nw-form legend{font-weight:700;color:#fff;padding:0 6px}html .cc .nw-form :is(input,textarea,select){font:16px var(--body);padding:10px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.2);background:#0b0d0f;color:#fff;width:100%;box-sizing:border-box}'
        . 'html .cc .nw-form .nw-tick{display:flex!important;gap:10px;align-items:center}html .cc .nw-form .nw-tick input{width:22px;height:22px}html .cc .nw-form .btn{justify-self:start}</style>';
}, 10, 2);
add_action('admin_post_cc_news', function () {
    if (!cc_ath_is_coach() || !wp_verify_nonce($_POST['_wpnonce'] ?? '', 'cc_news')) wp_die('Not allowed');
    $n = cc_nw_post(['aud' => $_POST['aud'] ?? 'all', 'url' => $_POST['url'] ?? '', 'when' => sanitize_text_field($_POST['when'] ?? ''), 'push' => !empty($_POST['push']), 'email' => !empty($_POST['email']), 't' => wp_unslash((array) ($_POST['t'] ?? []))]);
    if (is_wp_error($n)) set_transient('cc_nw_err', $n->get_error_message(), 120);
    wp_safe_redirect(add_query_arg(['board' => 'news', 'nw' => is_wp_error($n) ? 'bad' : 'ok'], home_url('/' . CC_ATH_SLUG . '/'))); exit;
});
add_action('admin_post_cc_news_del', function () {
    if (!cc_ath_is_coach() || !wp_verify_nonce($_POST['_wpnonce'] ?? '', 'cc_news')) wp_die('Not allowed');
    $id = sanitize_text_field($_POST['id'] ?? ''); update_option('cc_news', array_values(array_filter(cc_nw_all(), function ($n) use ($id) { return $n['id'] !== $id; })), false);
    wp_safe_redirect(add_query_arg('board', 'news', home_url('/' . CC_ATH_SLUG . '/'))); exit;
});

/* ---------- a new blog post: a buzz on the phones that are turned on (Italian posts to Italian readers, the others to the rest) ---------- */
add_action('transition_post_status', function ($new, $old, $post) {
    if ($new !== 'publish' || $old === 'publish' || $post->post_type !== 'post' || !function_exists('cc_push_user')) return;
    if (get_post_meta($post->ID, 'cc_blog_pushed', true)) return; update_post_meta($post->ID, 'cc_blog_pushed', time());
    $it = has_category('Italiano', $post);
    foreach (get_users(['meta_key' => 'cc_push', 'fields' => 'ID']) as $uid) {
        if (user_can((int) $uid, 'edit_pages')) continue;
        $l = cc_ath_lang_code((int) $uid); if (($l === 'it') !== $it) continue;
        $keep = $GLOBALS['cc_ath_lang'] ?? 'en'; $GLOBALS['cc_ath_lang'] = $l;
        cc_push_user((int) $uid, '📰 ' . cc_nw_w('blog'), wp_strip_all_tags(get_the_title($post)), get_permalink($post), 'cc-blog-' . $post->ID);
        $GLOBALS['cc_ath_lang'] = $keep;
    }
}, 10, 3);
