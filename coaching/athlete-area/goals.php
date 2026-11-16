<?php
/* "My goals & events" (Matteo, 16 Nov 2026): the athlete keeps their goals and events here (never in Vekta); Matteo gets an email
 * on every change; his Claude-Vekta session reads them (GET /wp-json/cc/v1/goals) for planning, periodization and calendar notes.
 * Starts from the rider form's goals. Shown after "My availability". Pushed with --availability. Needs availability.php (helpers).
 */
if (!defined('ABSPATH')) return;

const CC_G_TYPES = ['race' => 'Race', 'sportive' => 'Sportive / Gran Fondo', 'camp' => 'Camp or trip', 'other' => 'Other'];
function cc_g_get($pid) { $g = json_decode((string) get_post_meta($pid, 'cc_goals', true), true); return is_array($g) ? $g : null; }
function cc_g_clean($in) {
    $in = is_array($in) ? $in : [];
    $out = ['short' => cc_av_note($in['short'] ?? '', 1500), 'long' => cc_av_note($in['long'] ?? '', 1500), 'events' => []];
    foreach (array_slice((array) ($in['events'] ?? []), 0, 40) as $e) {
        $name = cc_av_str($e['name'] ?? '', 120); $date = cc_av_date($e['date'] ?? '');
        if ($name === '' || !$date) continue;
        $out['events'][] = ['name' => $name, 'date' => $date, 'type' => isset(CC_G_TYPES[$e['type'] ?? '']) ? $e['type'] : 'race',
            'prio' => in_array($e['prio'] ?? '', ['A', 'B', 'C'], true) ? $e['prio'] : 'B',
            'dist' => is_numeric($e['dist'] ?? '') ? 0 + $e['dist'] : '', 'elev' => is_numeric($e['elev'] ?? '') ? 0 + $e['elev'] : '', 'note' => cc_av_str($e['note'] ?? '', 300)];
    }
    usort($out['events'], function ($a, $b) { return strcmp($a['date'], $b['date']); });
    return $out;
}
function cc_g_event_text($e) {
    return $e['name'] . ' · ' . date_i18n('D j M Y', strtotime($e['date'] . ' 12:00')) . ' · ' . $e['prio'] . ' ' . strtolower(CC_G_TYPES[$e['type']])
         . ($e['dist'] !== '' ? ' · ' . $e['dist'] . ' km' : '') . ($e['elev'] !== '' ? ' · ' . $e['elev'] . ' m' : '') . ($e['note'] !== '' ? ' · ' . $e['note'] : '');
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
    register_rest_route('cc/v1', '/goals', [
        ['methods' => 'POST', 'callback' => 'cc_g_save', 'permission_callback' => function () { return is_user_logged_in() && (bool) cc_ath_page_of(get_current_user_id()) && !cc_ath_is_coach(); }],
        ['methods' => 'GET', 'callback' => 'cc_g_list', 'permission_callback' => 'cc_ath_is_coach'],
    ]);
});
function cc_g_save(WP_REST_Request $r) {
    $uid = get_current_user_id(); $pid = cc_ath_page_of($uid);
    $old = cc_g_get($pid) ?: []; $new = cc_g_clean($r->get_json_params()['goals'] ?? null);
    $new['from_form'] = $old['from_form'] ?? '';
    $diff = cc_g_diff($old, $new);
    if (!$diff) return ['ok' => true, 'unchanged' => true];
    $new['updated'] = time();
    update_post_meta($pid, 'cc_goals', wp_slash(wp_json_encode($new)));
    $u = get_userdata($uid); $name = get_post_field('post_title', $pid);
    $h = '<div style="font:15px/1.5 Montserrat,Arial,sans-serif;color:#111;max-width:560px"><p style="margin:0 0 4px;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#E10600;font-weight:600">Goals &amp; events</p>'
       . '<h2 style="margin:0 0 14px;color:#111">' . esc_html($name) . ' updated their goals and events</h2><ul>' . implode('', array_map(function ($x) { return '<li>' . esc_html($x) . '</li>'; }, $diff)) . '</ul>'
       . ($new['events'] ? '<p style="margin:16px 0 6px"><b style="color:#111">All their events</b></p><ul>' . implode('', array_map(function ($e) { return '<li>' . esc_html(cc_g_event_text($e)) . '</li>'; }, $new['events'])) . '</ul>' : '')
       . '<p style="margin:20px 0 0"><a href="' . esc_url(add_query_arg('board', 'goals', home_url('/' . CC_ATH_SLUG . '/'))) . '" style="display:inline-block;padding:12px 20px;border-radius:8px;background:#009a44;color:#fff;font-weight:600;text-decoration:none">Open all athletes’ goals</a></p></div>';
    $hd = ['Content-Type: text/html; charset=UTF-8']; if ($u && is_email($u->user_email)) $hd[] = 'Reply-To: ' . $name . ' <' . $u->user_email . '>';
    if (cc_av_notify_to()) wp_mail(cc_av_notify_to(), 'Goals & events: ' . $name . ' – ' . $diff[0], $h, $hd);
    return ['ok' => true, 'updated' => $new['updated']];
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
add_filter('cc_ath_nav', function ($nav, $view, $coach) { if ($view) { cc_f_set_lang((int) get_post_meta($view, 'cc_user', true)); array_splice($nav, 2, 0, [['goals', cc_f('My goals & events')]]); } return $nav; }, 20, 3);
add_filter('cc_ath_after_reports', function ($html, $view, $coach) {
    if (!$view) return $html;
    $g = cc_g_get($view) ?: ['short' => '', 'long' => '', 'events' => [], 'from_form' => ''];
    $today = current_time('Y-m-d'); $g['events'] = array_values(array_filter($g['events'], function ($e) use ($today) { return $e['date'] >= $today; }));
    $ro = $coach && cc_ath_page_of(get_current_user_id()) !== $view;
    cc_f_set_lang((int) get_post_meta($view, 'cc_user', true));
    $W = []; foreach (['My goals & events', 'Short-term goal (1 year)', 'Long-term goal (more than 1 year)', 'Events coming up', 'No events yet. Add your races, sportives and camps: I plan your training around them.',
        'Event', 'Date', 'Type', 'Priority', 'A = your main goal, B = important, C = for training or fun', 'Distance (km)', 'Climbing (m)', 'Note', 'Remove', '+ Add an event', 'Save my goals & events', 'Saving…',
        'Saved. Thanks, I will plan around it.', 'Nothing new to save.', 'That did not save. Please try again.', 'days to go', 'Today!', 'Tomorrow', 'From your form', 'optional',
        'Where you want to get to, and the events on the way. Keep them up to date: your plan is built around them.'] as $s) $W[$s] = cc_f($s);
    $types = []; foreach (CC_G_TYPES as $k => $v) $types[$k] = cc_f($v);
    $speech = function_exists('cc_av_lang') ? (CC_AV_SPEECH[cc_av_lang($view)] ?? 'en-GB') : 'en-GB';
    return $html . '<section class="ath-s gl" id="goals" lang="' . esc_attr($speech) . '"><h2>' . cc_ath_icon('peaks', 'ath-hic') . esc_html($W['My goals & events']) . '</h2>'
        . '<p class="av-lede">' . esc_html($W['Where you want to get to, and the events on the way. Keep them up to date: your plan is built around them.']) . '</p>'
        . '<div id="gl-app" data-ro="' . ($ro ? 1 : 0) . '" data-today="' . esc_attr($today) . '" data-api="' . esc_url(rest_url('cc/v1/goals')) . '" data-nonce="' . esc_attr(wp_create_nonce('wp_rest')) . '"></div>'
        . '<script type="application/json" id="gl-data">' . wp_json_encode(['g' => $g, 'w' => $W, 'types' => $types, 'L' => $speech]) . '</script></section>' . cc_g_js();
}, 20, 3);

/* ---------- Matteo's board: /athletes/?board=goals ---------- */
add_filter('cc_ath_coach_links', function ($html) { return $html . '<a class="av-boardlink" href="' . esc_url(add_query_arg('board', 'goals', home_url('/' . CC_ATH_SLUG . '/'))) . '">Goals &amp; events</a>'; }, 15);
add_filter('cc_ath_board', function ($html, $board) {
    if ($board !== 'goals' || !cc_ath_is_coach()) return $html;
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
   +'<div class="gl-r"><label>'+esc(W['Distance (km)'])+' <small>('+esc(W.optional)+')</small><input type="number" inputmode="decimal" class="gl-km" value="'+esc(e.dist)+'"'+(ro?' readonly':'')+'></label>'
   +'<label>'+esc(W['Climbing (m)'])+' <small>('+esc(W.optional)+')</small><input type="number" inputmode="numeric" class="gl-m" value="'+esc(e.elev)+'"'+(ro?' readonly':'')+'></label></div>'
   +'<label>'+esc(W.Note)+' <small>('+esc(W.optional)+')</small><input type="text" class="gl-no" maxlength="300" value="'+esc(e.note)+'"'+(ro?' readonly':'')+'></label>'
   +(ro?'':'<button type="button" class="av-del gl-del">'+esc(W.Remove)+'</button>')+'</div>';});
 h+='</div><p class="gl-hint">'+esc(W['A = your main goal, B = important, C = for training or fun'])+'</p>';
 if(!ro)h+='<button type="button" class="btn btn-ghost gl-add">'+esc(W['+ Add an event'])+'</button><div class="av-save"><button type="button" class="btn btn-go gl-go" disabled>'+esc(W['Save my goals & events'])+'</button><span class="av-msg gl-msg" role="status"></span></div>';
 A.innerHTML=h;}
function touch(){dirty=true;var b=A.querySelector('.gl-go');if(b)b.disabled=false;var m=A.querySelector('.gl-msg');if(m)m.textContent='';}
function ev(t){return G.events[+t.closest('.gl-ev').dataset.i];}
A.addEventListener('input',function(e){var t=e.target;if(t.id==='gl-s')G.short=t.value;else if(t.id==='gl-l')G.long=t.value;else if(t.closest('.gl-ev')){var x=ev(t);
 if(t.classList.contains('gl-n'))x.name=t.value;if(t.classList.contains('gl-km'))x.dist=t.value;if(t.classList.contains('gl-m'))x.elev=t.value;if(t.classList.contains('gl-no'))x.note=t.value;}touch();});
A.addEventListener('change',function(e){var t=e.target;if(!t.closest('.gl-ev'))return;var x=ev(t);if(t.classList.contains('gl-d')){x.date=t.value;var c=t.closest('.gl-ev').querySelector('.gl-top');c.innerHTML=x.date?'<span class="gl-cd">'+cd(x.date)+'</span>':'';}
 if(t.classList.contains('gl-t'))x.type=t.value;touch();});
A.addEventListener('click',function(e){var b=e.target.closest('button');if(!b||ro)return;
 if(b.classList.contains('gl-pb')){var x=ev(b);x.prio=b.dataset.p;var r=b.closest('.gl-ev');r.className='gl-ev gl-'+x.prio;r.querySelectorAll('.gl-pb').forEach(function(y){y.setAttribute('aria-pressed',y===b);});touch();}
 if(b.classList.contains('gl-add')){G.events.push({name:'',date:'',type:'race',prio:'B',dist:'',elev:'',note:''});draw();touch();var l=A.querySelectorAll('.gl-n');l[l.length-1].focus();}
 if(b.classList.contains('gl-del')){G.events.splice(+b.closest('.gl-ev').dataset.i,1);draw();touch();}
 if(b.classList.contains('gl-go')){b.disabled=true;var m=A.querySelector('.gl-msg');m.textContent=W['Saving…'];m.classList.remove('bad');
  fetch(A.dataset.api,{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-WP-Nonce':A.dataset.nonce},body:JSON.stringify({goals:G})})
  .then(function(r){if(!r.ok)throw 0;return r.json();}).then(function(j){dirty=false;m.textContent=j.unchanged?W['Nothing new to save.']:W['Saved. Thanks, I will plan around it.'];})
  .catch(function(){b.disabled=false;m.textContent=W['That did not save. Please try again.'];m.classList.add('bad');});}});
addEventListener('beforeunload',function(e){if(dirty&&!ro){e.preventDefault();e.returnValue='';}});
draw();})();</script>
JS;
}
add_action('wp_head', function () {
    if (!is_page(CC_ATH_SLUG)) return;
    echo <<<'CSS'
<style id="cc-goals">
html .cc .gl .av-sub { margin-top: 24px; } html .cc .gl-goals2 { display: grid; gap: 6px; } html .cc .gl-goals2 label, html .cc .gl-ev label, html .cc .gl-ev legend { display: grid; gap: 5px; margin: 8px 0 0; font-size: 12.5px; color: var(--text-3); font-weight: 600; padding: 0; }
html .cc .gl-goals2 label { color: var(--text); font-size: 13.5px; } html .cc .gl-ev fieldset { border: 0; margin: 0; padding: 0; min-width: 0; }
html .cc .ath :is(.gl-goals2 textarea, .gl-ev input, .gl-ev select) { width: 100%; box-sizing: border-box; font: 16px var(--body); padding: 10px 12px; border-radius: 10px; border: 1px solid rgba(255,255,255,.18); background: #0b0d0f; color: #fff; color-scheme: dark; min-width: 0; }
html .cc .gl-ff { margin: 12px 0 0; font-size: 14px; color: var(--text-2); } html .cc .gl-ff small { display: block; color: var(--text-3); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }
html .cc .gl-evs { display: grid; gap: 10px; margin: 0 0 10px; }
html .cc .gl-ev { display: grid; gap: 4px; padding: 14px; border-radius: 12px; border: 1px solid rgba(255,255,255,.1); border-left: 3px solid #8a8f98; background: rgba(255,255,255,.03); }
html .cc .gl-ev.gl-A { border-left-color: #009a44; background: linear-gradient(90deg, rgba(0,154,68,.12), rgba(255,255,255,.03) 50%); } html .cc .gl-ev.gl-B { border-left-color: #d0d6e0; }
html .cc .gl-top:empty { display: none; } html .cc .gl-cd { font-size: 14px; color: var(--text-2); } html .cc .gl-cd b { font: 400 26px/1 var(--head); color: #34c46a; margin-right: 4px; }
html .cc .gl-r { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 10px; }
html .cc .gl-p { display: flex; gap: 6px; } html .cc .gl-pb { flex: 1; font: 700 14px var(--body); min-height: 42px; border-radius: 10px; border: 1px solid rgba(255,255,255,.16); background: transparent; color: var(--text-2); cursor: pointer; }
html .cc .gl-pb[aria-pressed=true] { background: #009a44; border-color: #009a44; color: #fff; } html .cc .gl-hint { font-size: 12.5px; color: var(--text-3); margin: 0 0 12px; }
html .cc .gl-del { justify-self: start; }
html .cc .gl-board { display: grid; gap: 8px; } html .cc .gl-row { display: grid; grid-template-columns: 170px minmax(0, 1fr); gap: 6px 16px; padding: 12px 14px; border-radius: 12px; background: rgba(255,255,255,.03); border: 1px solid rgba(255,255,255,.08); font-size: 14px; }
html .cc .gl-who { display: grid; gap: 2px; align-content: start; } html .cc .gl-who b { color: #fff; } html .cc .gl-who small { color: var(--text-3); font-size: 12px; }
html .cc .gl-a { color: #fff; } html .cc .gl-a b { color: #34c46a; } html .cc .gl-none { color: var(--text-3); }
html .cc .gl-goals { grid-column: 2; color: var(--text-2); } html .cc .gl-goals p { margin: 4px 0; } html .cc .gl-goals small { color: var(--text-3); margin-right: 6px; } html .cc .gl-goals ul { margin: 6px 0 0; padding: 0; list-style: none; display: grid; gap: 3px; }
html .cc .gl-prio { display: inline-grid; place-items: center; width: 20px; height: 20px; border-radius: 6px; background: rgba(255,255,255,.12); font: 700 11px var(--body); color: #fff; } html .cc .gl-prio.A { background: #009a44; }
@media (max-width: 640px) { html .cc .gl-row { grid-template-columns: 1fr; } html .cc .gl-goals { grid-column: 1; } }
</style>
CSS;
});
