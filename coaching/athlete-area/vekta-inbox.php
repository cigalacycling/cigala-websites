<?php
/* ---------- Vekta inbox in the hub (Matteo, 18 Nov 2026) ----------
 * Vekta has no notification centre: athletes' comments on their sessions are easy to miss. Matteo's laptop
 * (vekta\hub\vekta_inbox.py, every 15 min; his Vekta key never leaves the laptop) sends here, for each athlete:
 * the latest sessions (one line each) and every comment still waiting for his answer. He answers here; the reply waits
 * in a queue until the laptop posts it on the session in Vekta, under his name (his Send click is the go-ahead, like the Desk).
 * Coach only. Nothing here is visible to athletes. */

function cc_vx_data() { $d = get_option('cc_vx_data', []); return is_array($d) ? $d : []; }
function cc_vx_outbox() { $o = get_option('cc_vx_outbox', []); return is_array($o) ? $o : []; }
function cc_vx_drafts() { $d = get_option('cc_vx_drafts', []); return is_array($d) ? $d : []; }
function cc_vx_dismissed() { $d = get_option('cc_vx_dismissed', []); return is_array($d) ? $d : []; }   // "No reply needed" (Matteo 18 Nov)
function cc_vx_open($u) { static $q = null, $d = null; if ($q === null) { $q = cc_vx_queued_ids(); $d = cc_vx_dismissed(); } return !isset($d[$u['key']]); }
function cc_vx_open_count() {
    $n = 0; $q = cc_vx_queued_ids();
    foreach (cc_vx_data() as $a) foreach ((array) ($a['unanswered'] ?? []) as $u) if (!isset($q[$u['key']]) && cc_vx_open($u)) $n++;
    return $n;
}
function cc_vx_queued_ids() { $q = []; foreach (cc_vx_outbox() as $o) if (in_array($o['status'], ['queued', 'sent'], true)) $q[$o['key']] = $o['status']; return $q; }
function cc_vx_dur($s) { $s = (int) $s; return $s >= 3600 ? floor($s / 3600) . 'h' . str_pad((string) floor(($s % 3600) / 60), 2, '0', STR_PAD_LEFT) : floor($s / 60) . ' min'; }
function cc_vx_when($iso) { $t = strtotime((string) $iso); return $t ? date_i18n('D j M', $t + (int) (get_option('gmt_offset') * HOUR_IN_SECONDS)) : ''; }
function cc_vx_clean_session($s) {
    $n = function ($k) use ($s) { return is_numeric($s[$k] ?? null) ? 0 + $s[$k] : null; };
    $o = ['id' => sanitize_text_field($s['id'] ?? ''), 'date' => sanitize_text_field($s['date'] ?? ''), 'name' => sanitize_text_field($s['name'] ?? ''), 'sport' => sanitize_key($s['sport'] ?? ''),
          'dur' => (int) ($s['dur'] ?? 0), 'avg_w' => (int) ($s['avg_w'] ?? 0), 'np' => (int) ($s['np'] ?? 0), 'stim' => sanitize_text_field($s['stim'] ?? ''),
          'rpe' => $n('rpe'), 'feeling' => $n('feeling'), 'km' => $n('km'), 'elev' => $n('elev'), 'hr' => $n('hr'), 'kj' => $n('kj')];
    if (!empty($s['plan']) && is_array($s['plan'])) { $p = $s['plan'];
        $o['plan'] = ['title' => sanitize_text_field($p['title'] ?? ''), 'dur' => (int) ($p['dur'] ?? 0), 'avg_w' => (int) ($p['avg_w'] ?? 0), 'kj' => (int) ($p['kj'] ?? 0),
                      'dur_pct' => is_numeric($p['dur_pct'] ?? null) ? (int) $p['dur_pct'] : null, 'kj_pct' => is_numeric($p['kj_pct'] ?? null) ? (int) $p['kj_pct'] : null]; }
    return $o;
}
// Matteo 18 Nov: under the session line, the plan vs what was done and a few facts (deep analysis stays in Vekta)
function cc_vx_session_more($s) {
    $f = array_filter([!empty($s['km']) ? $s['km'] . ' km' : '', !empty($s['elev']) ? number_format_i18n($s['elev']) . ' m' : '', !empty($s['hr']) ? 'HR ' . (int) $s['hr'] : '', !empty($s['kj']) ? number_format_i18n($s['kj']) . ' kJ' : '']);
    $o = $f ? '<span class="vx-f">' . esc_html(implode(' · ', $f)) . '</span>' : '';
    if (!empty($s['plan'])) { $p = $s['plan'];
        $pl = array_filter([$p['dur'] ? cc_vx_dur($p['dur']) : '', $p['avg_w'] ? $p['avg_w'] . ' W' : '', $p['kj'] ? number_format_i18n($p['kj']) . ' kJ' : '']);
        $done = array_filter([$p['dur_pct'] !== null ? $p['dur_pct'] . '% of the time' : '', $p['kj_pct'] !== null ? $p['kj_pct'] . '% of the work' : '']);
        $ok = ($p['dur_pct'] ?? 100) >= 90 && ($p['kj_pct'] ?? 100) >= 90;
        $o .= '<span class="vx-p"><b>Plan:</b> ' . esc_html(($p['title'] ?: 'planned session') . ($pl ? ' · ' . implode(' · ', $pl) : '')) . ($done ? ' <i class="' . ($ok ? 'ok' : 'lo') . '">→ done ' . esc_html(implode(', ', $done)) . '</i>' : '') . '</span>';
    } else $o .= '<span class="vx-p vx-np">Not a planned session</span>';
    return '<span class="vx-more">' . $o . '</span>';
}
function cc_vx_session_line($s) {
    $bits = [cc_vx_when($s['date'] ?? ''), cc_vx_dur($s['dur'] ?? 0)];
    if (!empty($s['avg_w'])) $bits[] = (int) $s['avg_w'] . ' W' . (!empty($s['np']) ? ' (NP ' . (int) $s['np'] . ')' : '');
    if (!empty($s['stim'])) $bits[] = ucfirst(str_replace('_', ' ', (string) $s['stim']));
    if (!empty($s['rpe'])) $bits[] = 'RPE ' . $s['rpe'];
    if (!empty($s['feeling'])) $bits[] = 'feel ' . $s['feeling'] . '/5';
    return '<b>' . esc_html($s['name'] ?: (!empty($s['plan']['title']) ? $s['plan']['title'] : ucfirst((string) ($s['sport'] ?? 'Session')))) . '</b> <span>' . esc_html(implode(' · ', array_filter($bits))) . '</span>';
}
function cc_vx_anchor($key) { return 'vx-' . preg_replace('/[^a-z0-9_-]+/i', '-', (string) $key); }   // Matteo 18 Nov: a notification jumps to its comment
function cc_vx_item($pid, $u, $queued) {
    $face = function_exists('cc_ph_widget') ? cc_ph_widget($pid, 30, false, 'nt-me-a') : '';
    $uid = (int) get_post_meta($pid, 'cc_user', true); $lang = $uid && function_exists('cc_ath_user_lang') ? cc_ath_user_lang($uid) : 'en';
    $speech = ['en' => 'en-IE', 'it' => 'it-IT', 'pt' => 'pt-PT', 'sl' => 'sl-SI', 'sk' => 'sk-SK'][$lang] ?? 'en-IE';   // Matteo 18 Nov: dictate in the athlete's language
    // Matteo 18 Nov: one tap to the session in Vekta (the link format he gave: workspace "cigala-cycling")
    // Matteo 18 Nov (later): the Vekta logo in the box's top-right corner instead of a text link ("looks more pro")
    $vk = !empty($u['activity']) ? '<a class="vx-open" href="' . esc_url('https://app.joinvekta.com/cigala-cycling/activity/' . rawurlencode($u['activity']) . '/overview') . '" target="_blank" rel="noopener" title="Open in Vekta" aria-label="Open this session in Vekta">' . (function_exists('cc_ath_icon') ? cc_ath_icon('logo-vekta', 'vx-vl') : 'Vekta') . '</a>' : '';
    $o = '<div class="vx-msg' . ($vk !== '' ? ' vx-has-open' : '') . '" id="' . esc_attr(cc_vx_anchor($u['key'])) . '" data-key="' . esc_attr($u['key']) . '" data-lang="' . esc_attr($speech) . '">' . $vk . '<p class="vx-ses">' . cc_vx_session_line($u['session'] ?? []) . cc_vx_session_more($u['session'] ?? []) . '</p>'
       . '<div class="vx-b"><span class="nt-rh">' . $face . '<b>' . esc_html(get_the_title($pid)) . '</b> <small>' . esc_html(cc_vx_when($u['at'] ?? '')) . ($u['kind'] === 'description' ? ' · ride description' : '') . '</small></span>'
       . '<p>' . nl2br(esc_html($u['text'])) . '</p></div>';
    if ($queued) $o .= '<p class="vx-st">' . ($queued === 'sent' ? '✅ Posted in Vekta' : '⏳ Your reply is queued: your laptop posts it in Vekta within about 15 minutes') . '</p>';
    else { $dr = cc_vx_drafts()[$u['key']] ?? '';   // Matteo 18 Nov: a draft in his style, ready to edit (Claude task 8:00 / 18:00)
        $o .= '<div class="vx-r">' . ($dr !== '' ? '<p class="vx-dl">✍️ Draft in your style: edit it, then send</p>' : '')
            . '<textarea rows="' . ($dr !== '' ? 3 : 2) . '" placeholder="Reply on this session in Vekta…" aria-label="Reply">' . esc_textarea($dr) . '</textarea><div class="vx-bt"><button type="button" class="btn btn-go vx-send">Send to Vekta</button><button type="button" class="btn btn-ghost vx-dict" aria-pressed="false">🎙 Dictate</button>'
            . '<button type="button" class="btn btn-ghost vx-skip">No reply needed</button></div><span class="vx-m" role="status"></span></div>'; }
    return $o . '</div>';
}
function cc_vx_assets() {
    static $done = false; if ($done) return ''; $done = true;
    return '<style>html .cc .vx-sync{color:#b8bec8;font-size:15px;margin:0 0 14px}html .cc .vx-who{display:flex;align-items:center;gap:10px;margin:22px 0 8px;font-size:17px}html .cc .vx-who a{color:#fff;font-weight:700;text-decoration:none}'
        . 'html .cc .vx-msg{padding:12px 14px;margin:0 0 10px;border-radius:12px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.03)}'
        . 'html .cc .vx-ses{margin:0 0 8px;font-size:15px;color:#d0d6e0}html .cc .vx-ses b{color:#fff;margin-right:6px}html .cc .vx-ses span{color:#b8bec8}'
        . 'html .cc .vx-b{padding:10px 12px;border-left:3px solid #b8bec8;background:rgba(255,255,255,.04);border-radius:0 10px 10px 0}html .cc .vx-b p{margin:4px 0 0;font-size:16px;color:#e6e9ee}html .cc .vx-b small{color:#b8bec8;font-size:14px}'
        . 'html .cc .vx-r{display:grid;gap:8px;margin-top:10px}html .cc .vx-r textarea{width:100%;box-sizing:border-box;font:16px var(--body);padding:10px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.18);background:#0b0d0f;color:#fff;line-height:1.5;min-height:96px;resize:vertical;overflow:hidden}'
        . 'html .cc .vx-more{display:block;margin-top:4px}html .cc .vx-f,html .cc .vx-p{display:block;font-size:14px;color:#b8bec8;line-height:1.45}html .cc .vx-p b{color:#d0d6e0;margin:0}'
        . 'html .cc .vx-p i{font-style:normal;font-weight:600}html .cc .vx-p i.ok{color:#2bd47a}html .cc .vx-p i.lo{color:#f0bf00}html .cc .vx-np{opacity:.8}'
        . 'html .cc .vx-msg{position:relative}html .cc .vx-has-open .vx-ses{padding-right:48px}'
        . 'html .cc .vx-open{position:absolute;top:10px;right:10px;width:38px;height:38px;border-radius:10px;background:#FFC20E;display:grid;place-items:center;text-decoration:none;box-shadow:0 2px 10px rgba(0,0,0,.35);transition:transform .15s}'
        . 'html .cc .vx-open:hover,html .cc .vx-open:focus-visible{transform:scale(1.08)}'
        . 'html .cc .vx-open .vx-vl{display:block;width:24px;height:24px;background-color:transparent!important;border:0!important;background-size:contain;background-position:center;background-repeat:no-repeat}'
        . 'html .cc .vx-dl{margin:0;font-size:14px;color:#b8bec8;font-weight:600}html .cc .vx-bt{display:flex;flex-wrap:wrap;gap:8px}html .cc .vx-r .btn{justify-self:start;width:auto;margin:0}html .cc .vx-m{font-size:15px;color:#2bd47a;font-weight:600}html .cc .vx-m.err{color:#ff7a73}html .cc .vx-st{margin:10px 0 0;font-size:15px;color:#2bd47a;font-weight:600}'
        . 'html .cc .vx-list{display:grid;gap:6px;margin:6px 0 14px}html .cc .vx-list p{margin:0;padding:8px 12px;border-radius:10px;background:rgba(255,255,255,.03);font-size:15px;color:#d0d6e0}html .cc .vx-list b{color:#fff;margin-right:6px}html .cc .vx-list span{color:#b8bec8}'
        . 'html .cc .vx-none{color:#2bd47a;font-weight:600;font-size:16px}'
        . 'html .cc .vx-msg.vx-hl{border-color:#2bd47a;box-shadow:0 0 0 3px rgba(43,212,122,.25);transition:box-shadow .4s}html .cc .vx-dict.on{background:#12a150;color:#fff;border-color:#12a150}</style>'
        // Matteo 18 Nov: tapping a notification lands on that comment (highlighted); "Dictate" types what he says, in the athlete's language
        . '<script>(function(){function go(){var h=location.hash;if(h.indexOf("#vx-")!==0)return;var el=document.getElementById(h.slice(1));if(!el)return;el.scrollIntoView({block:"center"});el.classList.add("vx-hl");setTimeout(function(){el.classList.remove("vx-hl");},4000);}'
        // Matteo 18 Nov: the reply box grows to show the whole draft (long drafts were hard to read on the phone)
        . 'function fit(t){t.style.height="auto";t.style.height=(t.scrollHeight+2)+"px";}function fitAll(){document.querySelectorAll(".vx-r textarea").forEach(fit);}'
        . 'document.addEventListener("input",function(e){if(e.target.matches&&e.target.matches(".vx-r textarea"))fit(e.target);});addEventListener("resize",fitAll);document.addEventListener("toggle",fitAll,true);'
        . 'if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",function(){fitAll();go();});else{fitAll();go();}addEventListener("load",fitAll);addEventListener("hashchange",go);'
        . 'var SR=window.SpeechRecognition||window.webkitSpeechRecognition,cur=null;'
        . 'document.addEventListener("click",function(e){var b=e.target.closest(".vx-dict");if(!b)return;var m=b.closest(".vx-msg"),t=m.querySelector("textarea"),s=m.querySelector(".vx-m");'
        . 'if(!SR){s.className="vx-m";s.textContent="Dictation is not available here: tap the box and use the microphone on your keyboard.";t.focus();return;}'
        . 'if(cur){cur.stop();return;}var r=new SR();cur=r;r.lang=m.dataset.lang||"en-IE";r.continuous=true;r.interimResults=false;'
        . 'b.classList.add("on");b.setAttribute("aria-pressed","true");b.textContent="■ Stop";s.className="vx-m";s.textContent="Listening…";'
        . 'r.onresult=function(ev){for(var i=ev.resultIndex;i<ev.results.length;i++)if(ev.results[i].isFinal){var x=ev.results[i][0].transcript.trim();if(x){t.value=(t.value.trim()?t.value.trim()+" ":"")+x;fit(t);}}};'
        . 'r.onerror=function(ev){s.className="vx-m err";s.textContent=ev.error==="not-allowed"?"Allow the microphone for this site, then try again.":"Dictation stopped. Try again.";};'
        . 'r.onend=function(){cur=null;b.classList.remove("on");b.setAttribute("aria-pressed","false");b.textContent="🎙 Dictate";if(s.textContent==="Listening…")s.textContent="";};'   // no automatic restart (iPhone)
        . 'try{r.start();}catch(x){cur=null;}});})();</script>'
        . '<script>(function(){document.addEventListener("click",function(e){var k=e.target.closest(".vx-skip");if(!k)return;var m=k.closest(".vx-msg");k.disabled=true;'
        . 'fetch(' . wp_json_encode(rest_url('cc/v1/vekta-dismiss')) . ',{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json","X-WP-Nonce":' . wp_json_encode(wp_create_nonce('wp_rest')) . '},body:JSON.stringify({key:m.dataset.key})})'
        . '.then(function(r){if(!r.ok)throw 0;m.style.transition="opacity .25s";m.style.opacity="0";setTimeout(function(){m.remove();},260);}).catch(function(){k.disabled=false;});});'
        . 'document.addEventListener("click",function(e){var b=e.target.closest(".vx-send");if(!b)return;var m=b.closest(".vx-msg"),t=m.querySelector("textarea"),s=m.querySelector(".vx-m"),v=t.value.trim();if(!v){t.focus();return;}'
        . 'b.disabled=true;s.className="vx-m";s.textContent="…";fetch(' . wp_json_encode(rest_url('cc/v1/vekta-reply')) . ',{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json","X-WP-Nonce":' . wp_json_encode(wp_create_nonce('wp_rest')) . '},body:JSON.stringify({key:m.dataset.key,text:v})})'
        . '.then(function(r){if(!r.ok)throw 0;m.querySelector(".vx-r").outerHTML="<p class=\"vx-st\">⏳ Your reply is queued: your laptop posts it in Vekta within about 15 minutes</p>";})'
        . '.catch(function(){b.disabled=false;s.className="vx-m err";s.textContent="Not saved. Please try again.";});});})();</script>';
}
function cc_vx_sync_line() {
    $at = (int) get_option('cc_vx_at', 0);
    return '<p class="vx-sync">' . ($at ? 'Updated ' . esc_html(human_time_diff($at, time())) . ' ago from your laptop (every 15 minutes while it is on).' : 'Waiting for the first update from your laptop.') . '</p>';
}

/* Matteo 18 Nov: an icon beside every coach tool (the Vekta logo for Vekta messages), added last so it covers every module's link */
add_filter('cc_ath_coach_links', function ($html) {
    $map = ['vekta' => 'logo-vekta', 'notes' => 'mic', 'results' => 'trophy', 'reports' => 'reports', 'forms' => 'doc', 'availability' => 'calendar',
            'goals' => 'peaks', 'contracts' => 'people', 'news' => 'bolt', 'ideas' => 'idea', 'blood' => 'sweat'];
    $html = preg_replace_callback('~<a class="av-boardlink" href="([^"]*)">~', function ($m) use ($map) {
        $b = preg_match('~[?&](?:amp;)?board=([a-z]+)~', html_entity_decode($m[1]), $x) ? $x[1] : '';
        return $m[0] . (function_exists('cc_ath_icon') ? cc_ath_icon($map[$b] ?? 'link', 'ath-jic') : '');
    }, $html);
    return $html . '<style>html .cc .ath-coach-tools .av-boardlink .ath-jic{flex:none;width:24px;height:24px;border-radius:7px;display:inline-grid;place-items:center;background:rgba(18,161,80,.15);border:1px solid rgba(43,212,122,.35)}'
        . 'html .cc .ath-coach-tools .av-boardlink .ath-jic svg{width:14px;height:14px;fill:none;stroke:#2bd47a;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}'
        . 'html .cc .ath-coach-tools .av-boardlink .ath-jic.ath-logo{background-size:cover;background-position:center;border:0}'
        . 'html .cc .ath-coach-tools .av-boardlink .ath-jic.logo-vekta{background-color:#FFD400;background-size:68%;background-repeat:no-repeat}</style>';   // Matteo 18 Nov: Vekta yellow
}, 999);

/* the board: every comment waiting for an answer, newest first, by athlete */
add_filter('cc_ath_coach_links', function ($html) {
    $n = cc_vx_open_count();
    return $html . '<a class="av-boardlink" href="' . esc_url(add_query_arg('board', 'vekta', home_url('/' . CC_ATH_SLUG . '/'))) . '">Vekta messages' . ($n ? ' <span class="av-badge">' . $n . '</span>' : '') . '</a>';
}, 5);
add_filter('cc_ath_board', function ($html, $board) {
    if ($board !== 'vekta' || !cc_ath_is_coach()) return $html;
    $q = cc_vx_queued_ids(); $rows = [];
    foreach (cc_vx_data() as $pid => $a) foreach ((array) ($a['unanswered'] ?? []) as $u) if (cc_vx_open($u)) $rows[] = [(int) $pid, $u];
    usort($rows, function ($x, $y) { return strcmp($y[1]['at'] ?? '', $x[1]['at'] ?? ''); });
    $o = '<section class="ath-s"><h2>Vekta messages</h2><p class="av-lede">Comments your athletes wrote on their sessions in Vekta that are still waiting for your answer (last 21 days). Your reply is posted on that session in Vekta, under your name.</p>' . cc_vx_sync_line();
    if (!$rows) $o .= '<p class="vx-none">✓ All caught up: no Vekta comment is waiting for you.</p>';
    $last = 0;
    foreach ($rows as [$pid, $u]) {
        if ($pid !== $last) { $o .= '<div class="vx-who">' . (function_exists('cc_ph_face') ? cc_ph_face($pid, 30) : '') . '<a href="' . esc_url(add_query_arg('view', $pid, home_url('/' . CC_ATH_SLUG . '/'))) . '">' . esc_html(get_the_title($pid)) . '</a>' . (function_exists('cc_ath_flag_for') ? cc_ath_flag_for($pid) : '') . '</div>'; $last = $pid; }
        $o .= cc_vx_item($pid, $u, $q[$u['key']] ?? '');
    }
    return $o . '</section>' . cc_vx_assets() . (function_exists('cc_nt_css') ? cc_nt_css() : '') . (function_exists('cc_ph_assets') ? cc_ph_assets() : '');
}, 10, 2);

/* on an athlete's page in Matteo's coach view: latest sessions + what is waiting */
add_filter('cc_ath_before_reports', function ($html, $view, $coach) {
    if (!$coach || !$view || !cc_ath_is_coach()) return $html;
    $a = cc_vx_data()[$view] ?? null; if (!$a) return $html;
    $q = cc_vx_queued_ids();
    $o = '<section class="ath-s" id="vekta"><h2>Vekta · latest sessions</h2>' . cc_vx_sync_line();
    $ses = array_slice((array) ($a['sessions'] ?? []), 0, 10);
    $o .= $ses ? '<div class="vx-list">' . implode('', array_map(function ($s) { return '<p>' . cc_vx_session_line($s) . cc_vx_session_more($s) . '</p>'; }, $ses)) . '</div>' : '<p class="av-lede">No sessions in the last 21 days.</p>';
    $un = array_filter((array) ($a['unanswered'] ?? []), 'cc_vx_open');
    if ($un) { $o .= '<h3 class="av-sub">Waiting for your answer</h3>'; foreach ($un as $u) $o .= cc_vx_item($view, $u, $q[$u['key']] ?? ''); }
    return $html . $o . '</section>' . cc_vx_assets() . (function_exists('cc_nt_css') ? cc_nt_css() : '');
}, 3, 3);

add_action('rest_api_init', function () {
    // the laptop: the latest picture (replaces the previous one)
    register_rest_route('cc/v1', '/vekta-inbox', ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        $in = (array) $r->get_param('athletes'); $out = [];
        foreach ($in as $a) {
            $pid = (int) ($a['page'] ?? 0); if (get_post_type($pid) !== 'cc_athlete') continue;
            $ses = array_map('cc_vx_clean_session', array_slice((array) ($a['sessions'] ?? []), 0, 15));
            $un = array_map(function ($u) { return ['key' => sanitize_text_field($u['key'] ?? ''), 'activity' => sanitize_text_field($u['activity'] ?? ''), 'kind' => ($u['kind'] ?? '') === 'description' ? 'description' : 'comment',
                'text' => sanitize_textarea_field($u['text'] ?? ''), 'at' => sanitize_text_field($u['at'] ?? ''),
                'thread' => array_map(function ($t) { return ['who' => sanitize_text_field($t['who'] ?? ''), 'text' => sanitize_textarea_field($t['text'] ?? '')]; }, array_slice((array) ($u['thread'] ?? []), 0, 6)),
                'detail' => mb_substr(sanitize_textarea_field((string) ($u['detail'] ?? '')), 0, 2500),   // the ride analysis for the drafts (plan, laps, peaks)
                'session' => cc_vx_clean_session((array) ($u['session'] ?? []))]; }, array_slice((array) ($a['unanswered'] ?? []), 0, 30));
            $out[$pid] = ['vekta_id' => sanitize_text_field($a['vekta_id'] ?? ''), 'sessions' => $ses, 'unanswered' => array_values(array_filter($un, function ($u) { return $u['key'] !== '' && $u['text'] !== ''; }))];
        }
        // Matteo 18 Nov: each NEW waiting message also goes to his notification centre (bell + phone), like notes and results
        $before = []; foreach (cc_vx_data() as $a) foreach ((array) $a['unanswered'] as $u) $before[$u['key']] = 1;
        $fresh = [];
        if ($before) foreach ($out as $pid => $a) foreach ($a['unanswered'] as $u) if (!isset($before[$u['key']])) $fresh[] = [$pid, $u];
        update_option('cc_vx_data', $out, false); update_option('cc_vx_at', time(), false);
        if ($fresh && function_exists('cc_push_coaches')) {
            $board = add_query_arg('board', 'vekta', home_url('/' . CC_ATH_SLUG . '/'));
            if (count($fresh) > 6) cc_push_coaches(count($fresh) . ' new Vekta messages', 'From ' . implode(', ', array_unique(array_map(function ($f) { return get_the_title($f[0]); }, array_slice($fresh, 0, 4)))) . '…', $board, 'cc-vekta');
            else foreach ($fresh as [$pid, $u]) cc_push_coaches('Vekta: ' . get_the_title($pid) . ($u['session']['name'] ? ' · ' . $u['session']['name'] : ''), wp_trim_words($u['text'], 18), $board . '#' . cc_vx_anchor($u['key']), 'cc-vekta', $pid);
        }
        // forget sent replies once the laptop no longer lists their comment as waiting
        $still = []; foreach ($out as $a) foreach ($a['unanswered'] as $u) $still[$u['key']] = 1;
        update_option('cc_vx_outbox', array_values(array_filter(cc_vx_outbox(), function ($o) use ($still) { return $o['status'] === 'queued' || ($o['status'] === 'failed') || isset($still[$o['key']]); })), false);
        update_option('cc_vx_dismissed', array_intersect_key(cc_vx_dismissed(), $still), false);   // forget dismissals the laptop no longer lists
        update_option('cc_vx_drafts', array_intersect_key(cc_vx_drafts(), $still), false);
        return ['ok' => true, 'athletes' => count($out), 'waiting' => cc_vx_open_count()];
    }]);
    // Matteo's reply from the hub: queued for the laptop
    register_rest_route('cc/v1', '/vekta-reply', ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        $key = sanitize_text_field((string) $r['key']); $text = trim(sanitize_textarea_field((string) $r['text']));
        if ($text === '' || mb_strlen($text) > 2000) return new WP_Error('cc_bad', 'Empty or too long', ['status' => 400]);
        foreach (cc_vx_data() as $pid => $a) foreach ((array) $a['unanswered'] as $u) if ($u['key'] === $key) {
            $ob = cc_vx_outbox();
            foreach ($ob as $o) if ($o['key'] === $key && $o['status'] === 'queued') return new WP_Error('cc_dup', 'Already queued', ['status' => 409]);
            $ob[] = ['id' => wp_generate_password(10, false), 'key' => $key, 'page' => (int) $pid, 'vekta_id' => $a['vekta_id'], 'activity' => $u['activity'], 'text' => $text, 'at' => time(), 'status' => 'queued', 'by' => get_current_user_id(),
                     'draft' => cc_vx_drafts()[$key] ?? '', 'message' => $u['text'], 'session' => $u['session']['name'] ?? ''];   // Matteo 18 Nov: the drafts learn from how he edits them
            update_option('cc_vx_outbox', $ob, false);
            return ['ok' => true, 'queued' => true];
        }
        return new WP_Error('cc_none', 'That comment is no longer waiting', ['status' => 404]);
    }]);
    // for the drafting task: what is waiting (with the conversation, athlete's language) and which already has a draft
    register_rest_route('cc/v1', '/vekta-waiting', ['methods' => 'GET', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function () {
        $q = cc_vx_queued_ids(); $dr = cc_vx_drafts(); $out = [];
        foreach (cc_vx_data() as $pid => $a) foreach ((array) $a['unanswered'] as $u) {
            if (isset($q[$u['key']]) || !cc_vx_open($u)) continue;
            $uid = (int) get_post_meta($pid, 'cc_user', true);
            $out[] = ['key' => $u['key'], 'page' => (int) $pid, 'athlete' => get_the_title($pid), 'first_name' => $uid ? get_userdata($uid)->first_name : '', 'language' => $uid ? cc_ath_lang_code($uid) : 'en',
                      'kind' => $u['kind'], 'text' => $u['text'], 'at' => $u['at'], 'thread' => $u['thread'] ?? [], 'session' => $u['session'], 'detail' => $u['detail'] ?? '', 'draft' => $dr[$u['key']] ?? null];
        }
        return $out;
    }]);
    register_rest_route('cc/v1', '/vekta-drafts', ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        $d = cc_vx_drafts(); $n = 0;
        foreach ((array) $r->get_param('drafts') as $k => $t) { $k = sanitize_text_field((string) $k); $t = trim(sanitize_textarea_field((string) $t)); if ($k !== '' && $t !== '' && mb_strlen($t) <= 1500) { $d[$k] = $t; $n++; } }
        update_option('cc_vx_drafts', $d, false); return ['ok' => true, 'saved' => $n];
    }]);
    register_rest_route('cc/v1', '/vekta-dismiss', ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        $key = sanitize_text_field((string) $r['key']); if ($key === '') return new WP_Error('cc_bad', 'No key', ['status' => 400]);
        $d = cc_vx_dismissed(); $d[$key] = time(); update_option('cc_vx_dismissed', $d, false); return ['ok' => true];
    }]);
    // coach-only check of what the board and an athlete's panel render (used to test without a browser login)
    register_rest_route('cc/v1', '/vekta-preview', ['methods' => 'GET', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        $pid = (int) $r['page'];
        // ?board=reports etc. for the laptop's checks
        return ['board' => apply_filters('cc_ath_board', '', sanitize_key((string) ($r['board'] ?? '')) ?: 'vekta'), 'athlete' => $pid ? apply_filters('cc_ath_before_reports', '', $pid, true) : '', 'chips' => function_exists('cc_ath_live_chips') ? cc_ath_live_chips(0, true, 0) : '', 'tools' => apply_filters('cc_ath_coach_links', '')];
    }]);
    register_rest_route('cc/v1', '/vekta-outbox', ['methods' => 'GET', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function () {
        return array_values(array_filter(cc_vx_outbox(), function ($o) { return $o['status'] === 'queued'; }));
    }]);
    register_rest_route('cc/v1', '/vekta-outbox-done', ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        $id = sanitize_text_field((string) $r['id']); $ob = cc_vx_outbox(); $hit = false;
        $notify = null;
        foreach ($ob as &$o) if ($o['id'] === $id) { $o['status'] = $r['ok'] ? 'sent' : 'failed'; $o['done_at'] = time(); $o['vekta_comment'] = sanitize_text_field((string) $r['vekta_comment']); $o['error'] = sanitize_text_field((string) $r['error']); $hit = true; if ($r['ok']) $notify = $o; }
        unset($o); update_option('cc_vx_outbox', $ob, false);
        // Matteo 18 Nov: Vekta's own alert is easy to miss, so the athlete also gets a hub notification (bell + phone), in their language.
        // "workout", not "ride": they also run, swim or do gym sessions. Tapping it opens their Vekta calendar.
        if ($notify && function_exists('cc_push_user') && ($uid = (int) get_post_meta((int) $notify['page'], 'cc_user', true))) {
            $T = ['en' => 'Matteo replied to your workout', 'it' => 'Matteo ha risposto al tuo allenamento', 'pt' => 'O Matteo respondeu ao teu treino', 'sl' => 'Matteo je odgovoril na tvoj trening'];
            $l = function_exists('cc_ath_user_lang') ? cc_ath_user_lang($uid) : 'en';
            // Matteo 18 Nov: open that exact session (athlete link format he gave: /me/activity/<id>/overview); calendar only if the id is missing
            $go = !empty($notify['activity']) ? 'https://app.joinvekta.com/me/activity/' . rawurlencode($notify['activity']) . '/overview' : 'https://app.joinvekta.com/me/calendar';
            cc_push_user($uid, $T[$l] ?? $T['en'], wp_trim_words($notify['text'], 20), $go, 'cc-vx-' . $notify['activity']);
        }
        return ['ok' => $hit];
    }]);
});
