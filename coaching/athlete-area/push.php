<?php
if (!defined('ABSPATH')) return;
/* Phone notifications for the hub on the home screen (Matteo, 17 Nov 2026). Standard Web Push: works on Android, and on iPhone
 * (iOS 16.4+) for the hub added to the Home Screen. Nothing is sent to anyone who did not tap "Turn on notifications" themselves
 * on their own phone, so athletes who have not been told about the hub can never get one. Never triggers an email.
 * - Keys (VAPID) made once on the server (option cc_push_vapid); messages encrypted per phone (RFC 8291, aes128gcm).
 * - Service worker at /athletes/?cc_sw=1 (scope /athletes/). Subscriptions in user meta cc_push (max 5 phones each).
 * - Athletes: Matteo replied to your note, a new report / race plan is in your hub. Matteo: new note, new athlete, rider form signed, new idea. */

function cc_push_b64u($s) { return rtrim(strtr(base64_encode($s), '+/', '-_'), '='); }
function cc_push_ub64($s) { return base64_decode(strtr($s, '-_', '+/') . str_repeat('=', (4 - strlen($s) % 4) % 4)); }
function cc_push_raw_pub($key) { $d = openssl_pkey_get_details($key); return "\x04" . str_pad($d['ec']['x'], 32, "\0", STR_PAD_LEFT) . str_pad($d['ec']['y'], 32, "\0", STR_PAD_LEFT); }
function cc_push_pem_from_raw($raw) {   // a P-256 public key (65 bytes, uncompressed) as PEM, for ECDH
    $der = hex2bin('3059301306072a8648ce3d020106082a8648ce3d030107034200') . $raw;
    return "-----BEGIN PUBLIC KEY-----\n" . chunk_split(base64_encode($der), 64, "\n") . "-----END PUBLIC KEY-----\n";
}
function cc_push_vapid() {
    $v = get_option('cc_push_vapid');
    if (!is_array($v) || empty($v['pem'])) {
        $k = openssl_pkey_new(['curve_name' => 'prime256v1', 'private_key_type' => OPENSSL_KEYTYPE_EC]); if (!$k) return null;
        openssl_pkey_export($k, $pem); $v = ['pem' => $pem, 'pub' => cc_push_b64u(cc_push_raw_pub($k))];
        update_option('cc_push_vapid', $v, false);
    }
    return $v;
}
function cc_push_der2raw($der) {   // ECDSA signature DER -> 64-byte r||s (JWT ES256)
    $o = 3; $lr = ord($der[$o]); $r = substr($der, $o + 1, $lr); $o += 1 + $lr + 1; $ls = ord($der[$o]); $s = substr($der, $o + 1, $ls);
    $f = function ($x) { $x = ltrim($x, "\0"); return str_pad($x, 32, "\0", STR_PAD_LEFT); };
    return $f($r) . $f($s);
}
function cc_push_encrypt($payload, $p256dh, $auth) {   // RFC 8291 aes128gcm
    $ua = cc_push_ub64($p256dh); $authk = cc_push_ub64($auth); if (strlen($ua) !== 65 || strlen($authk) < 16) return null;
    $eph = openssl_pkey_new(['curve_name' => 'prime256v1', 'private_key_type' => OPENSSL_KEYTYPE_EC]); $as = cc_push_raw_pub($eph);
    $shared = openssl_pkey_derive(openssl_pkey_get_public(cc_push_pem_from_raw($ua)), $eph, 32); if (!$shared) return null;
    $ikm = hash_hkdf('sha256', $shared, 32, "WebPush: info\0" . $ua . $as, $authk);
    $salt = random_bytes(16);
    $cek = hash_hkdf('sha256', $ikm, 16, "Content-Encoding: aes128gcm\0", $salt);
    $nonce = hash_hkdf('sha256', $ikm, 12, "Content-Encoding: nonce\0", $salt);
    $ct = openssl_encrypt($payload . "\x02", 'aes-128-gcm', $cek, OPENSSL_RAW_DATA, $nonce, $tag); if ($ct === false) return null;
    return $salt . pack('N', 4096) . chr(65) . $as . $ct . $tag;
}
function cc_push_one($sub, $msg) {   // returns HTTP status (0 on local failure)
    $v = cc_push_vapid(); if (!$v || empty($sub['endpoint'])) return 0;
    $body = cc_push_encrypt(wp_json_encode($msg), $sub['keys']['p256dh'] ?? '', $sub['keys']['auth'] ?? ''); if ($body === null) return 0;
    $p = wp_parse_url($sub['endpoint']); $aud = $p['scheme'] . '://' . $p['host'];
    $hdr = cc_push_b64u(wp_json_encode(['typ' => 'JWT', 'alg' => 'ES256'])); $cl = cc_push_b64u(wp_json_encode(['aud' => $aud, 'exp' => time() + 12 * 3600, 'sub' => 'mailto:info@cigalacycling.com']));
    if (!openssl_sign("$hdr.$cl", $sig, openssl_pkey_get_private($v['pem']), OPENSSL_ALGO_SHA256)) return 0;
    $jwt = "$hdr.$cl." . cc_push_b64u(cc_push_der2raw($sig));
    $r = wp_remote_post($sub['endpoint'], ['timeout' => 10, 'body' => $body, 'headers' => ['TTL' => '86400', 'Urgency' => 'normal', 'Content-Type' => 'application/octet-stream',
        'Content-Encoding' => 'aes128gcm', 'Authorization' => 'vapid t=' . $jwt . ', k=' . $v['pub']]]);
    return is_wp_error($r) ? 0 : (int) wp_remote_retrieve_response_code($r);
}
// one person's phones; gone phones (404/410) are forgotten
function cc_push_user($uid, $title, $body, $url, $tag = '') {
    $subs = get_user_meta((int) $uid, 'cc_push', true); if (!is_array($subs) || !$subs) return 0;
    $sent = 0; $msg = ['title' => $title, 'body' => wp_strip_all_tags($body), 'url' => $url, 'tag' => $tag ?: 'cc-' . time()];
    foreach ($subs as $k => $s) { $st = cc_push_one($s, $msg); if ($st >= 200 && $st < 300) $sent++; elseif (in_array($st, [404, 410], true)) unset($subs[$k]); }
    update_user_meta((int) $uid, 'cc_push', $subs); return $sent;
}
function cc_push_coaches($title, $body, $url, $tag = '') {   // Matteo (any coach account with a phone turned on)
    foreach (get_users(['meta_key' => 'cc_push', 'fields' => 'ID']) as $uid) if (user_can((int) $uid, 'edit_pages')) cc_push_user((int) $uid, $title, $body, $url, $tag);
}
function cc_push_athlete_page($pid, $title, $body, $url, $tag = '') { $uid = (int) get_post_meta((int) $pid, 'cc_user', true); return $uid ? cc_push_user($uid, $title, $body, $url, $tag) : 0; }

/* ---------- the service worker and the phone side ---------- */
add_action('init', function () {
    if (!isset($_GET['cc_sw'])) return;
    nocache_headers(); header('Content-Type: application/javascript; charset=utf-8'); header('Service-Worker-Allowed: /' . CC_ATH_SLUG . '/');
    $icon = 'https://coaching.cigalacycling.com/wp-content/uploads/2026/11/cigala-hub-app-192.png';
    echo "self.addEventListener('install',function(){self.skipWaiting();});self.addEventListener('activate',function(e){e.waitUntil(self.clients.claim());});\n"
       . "self.addEventListener('push',function(e){var d={};try{d=e.data?e.data.json():{};}catch(x){}var w=[self.registration.showNotification(d.title||'Cigala Cycling',{body:d.body||'',icon:'$icon',badge:'$icon',tag:d.tag,data:{url:d.url||'/" . CC_ATH_SLUG . "/'}})];"
       . "if(self.navigator&&self.navigator.setAppBadge)w.push(self.navigator.setAppBadge(1).catch(function(){}));e.waitUntil(Promise.all(w));});\n"
       . "self.addEventListener('notificationclick',function(e){e.notification.close();var u=(e.notification.data&&e.notification.data.url)||'/" . CC_ATH_SLUG . "/';"
       . "e.waitUntil(self.clients.matchAll({type:'window',includeUncontrolled:true}).then(function(cs){for(var i=0;i<cs.length;i++){if('focus' in cs[i]){cs[i].navigate(u);return cs[i].focus();}}return self.clients.openWindow(u);}));});\n";
    exit;
}, 1);
function cc_push_w($k) {
    static $W = [
        'title' => ['en' => 'Get notifications on this phone', 'it' => 'Ricevi le notifiche su questo telefono', 'pt' => 'Recebe notificações neste telemóvel', 'sl' => 'Prejemaj obvestila na ta telefon'],
        'text' => ['en' => 'Your phone tells you when I reply to your note or something new is in your hub.', 'it' => 'Il telefono ti avvisa quando rispondo al tuo messaggio o c’è qualcosa di nuovo nella tua area.',
                   'pt' => 'O telemóvel avisa-te quando respondo à tua mensagem ou há algo novo na tua área.', 'sl' => 'Telefon te obvesti, ko odgovorim na tvoje sporočilo ali je v tvojem središču kaj novega.'],
        'coach' => ['en' => 'Your phone tells you about new notes, signups, signed forms and ideas.', 'it' => 'Your phone tells you about new notes, signups, signed forms and ideas.', 'pt' => 'Your phone tells you about new notes, signups, signed forms and ideas.', 'sl' => 'Your phone tells you about new notes, signups, signed forms and ideas.'],
        'on' => ['en' => 'Turn on notifications', 'it' => 'Attiva le notifiche', 'pt' => 'Ativar notificações', 'sl' => 'Vklopi obvestila'],
        'no' => ['en' => 'Not now', 'it' => 'Non ora', 'pt' => 'Agora não', 'sl' => 'Ne zdaj'],
        'done' => ['en' => 'Notifications are on for this phone.', 'it' => 'Notifiche attive su questo telefono.', 'pt' => 'Notificações ativas neste telemóvel.', 'sl' => 'Obvestila so vklopljena na tem telefonu.'],
        'ios' => ['en' => 'On iPhone, add the hub to your Home Screen first, then open it from there to turn notifications on.', 'it' => 'Su iPhone aggiungi prima l’area alla schermata Home, poi aprila da lì per attivare le notifiche.',
                  'pt' => 'No iPhone, adiciona primeiro a área ao ecrã principal e abre-a a partir daí para ativar as notificações.', 'sl' => 'Na iPhonu najprej dodaj središče na začetni zaslon in ga odpri od tam, da vklopiš obvestila.'],
        'denied' => ['en' => 'Notifications are blocked for this site in your phone settings.', 'it' => 'Le notifiche per questo sito sono bloccate nelle impostazioni del telefono.', 'pt' => 'As notificações deste site estão bloqueadas nas definições do telemóvel.', 'sl' => 'Obvestila za to stran so blokirana v nastavitvah telefona.'],
    ];
    $l = $GLOBALS['cc_ath_lang'] ?? 'en'; return $W[$k][$l] ?? $W[$k]['en'];
}
// the card: on the hub, until notifications are on for this phone (or "Not now"); for athletes and for Matteo
add_filter('cc_ath_before_reports', function ($html, $view, $coach) {
    $v = cc_push_vapid(); if (!$v) return $html;
    $W = ['done' => cc_push_w('done'), 'ios' => cc_push_w('ios'), 'denied' => cc_push_w('denied')];
    return $html . '<div class="ath-push" hidden data-key="' . esc_attr($v['pub']) . '" data-sw="' . esc_url(add_query_arg('cc_sw', 1, home_url('/' . CC_ATH_SLUG . '/'))) . '" data-api="' . esc_url(rest_url('cc/v1/push-sub')) . '" data-nonce="' . esc_attr(wp_create_nonce('wp_rest')) . '" data-w="' . esc_attr(wp_json_encode($W)) . '">'
        . '<p><b>' . esc_html(cc_push_w('title')) . '</b><span>' . esc_html(cc_push_w($coach ? 'coach' : 'text')) . '</span></p>'
        . '<button type="button" class="btn btn-go push-on">' . esc_html(cc_push_w('on')) . '</button><button type="button" class="btn btn-ghost push-no">' . esc_html(cc_push_w('no')) . '</button><span class="push-msg" role="status"></span></div>'
        . '<style>html .cc .ath-push{display:flex;flex-wrap:wrap;align-items:center;gap:10px 14px;margin:0 0 14px;padding:12px 16px;border-radius:12px;border:1px solid rgba(43,212,122,.35);background:rgba(18,161,80,.08)}html .cc .ath-push[hidden]{display:none!important}'
        . 'html .cc .ath-push p{margin:0;flex:1 1 220px;font-size:15px;color:var(--text-2)}html .cc .ath-push b{display:block;color:#fff;font-size:16px}html .cc .ath-push .btn{width:auto;margin:0}html .cc .push-msg{flex-basis:100%;font-size:15px;color:#d0d6e0}html .cc .push-msg:empty{display:none}</style>'
        . '<script>(function(){var c=document.querySelector(".ath-push");if(!c)return;var W=JSON.parse(c.dataset.w),m=c.querySelector(".push-msg"),k="cc_push_no";'
        . 'try{if(navigator.clearAppBadge)navigator.clearAppBadge();}catch(e){}'
        . 'if(!("serviceWorker" in navigator))return;navigator.serviceWorker.register(c.dataset.sw,{scope:"' . '/' . CC_ATH_SLUG . '/' . '"}).catch(function(){});'
        . 'var ios=/iphone|ipad|ipod/i.test(navigator.userAgent),standalone=window.matchMedia("(display-mode: standalone)").matches||navigator.standalone;'
        . 'try{if(localStorage.getItem(k))return;}catch(e){}if(!("Notification" in window)){if(ios&&!standalone){c.hidden=false;c.querySelector(".push-on").hidden=true;m.textContent=W.ios;}return;}'
        . 'if(Notification.permission==="denied")return;'
        . 'navigator.serviceWorker.ready.then(function(r){return r.pushManager&&r.pushManager.getSubscription();}).then(function(s){if(!s||Notification.permission!=="granted")c.hidden=false;});'
        . 'function key(b){var p="=".repeat((4-b.length%4)%4),s=atob((b+p).replace(/-/g,"+").replace(/_/g,"/")),a=new Uint8Array(s.length);for(var i=0;i<s.length;i++)a[i]=s.charCodeAt(i);return a;}'
        // Matteo 17 Nov: each step shows on screen and any error is reported to the hub (GET /cc/v1/push-status shows the last ones)
        . 'function rep(step,e){m.textContent=W.denied+" ("+step+(e?": "+(e.message||e):"")+")";try{fetch(c.dataset.api.replace("push-sub","push-log"),{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json","X-WP-Nonce":c.dataset.nonce},body:JSON.stringify({step:step,err:String(e&&(e.message||e)||""),ua:navigator.userAgent,sa:!!(window.matchMedia("(display-mode: standalone)").matches||navigator.standalone),perm:Notification.permission})});}catch(x){}}'
        . 'c.querySelector(".push-on").addEventListener("click",function(){m.textContent="…";var pr;try{pr=Notification.requestPermission();}catch(e){rep("permission",e);return;}'
        . 'Promise.resolve(pr).then(function(p){p=p||Notification.permission;if(p!=="granted"){rep("permission "+p);return;}m.textContent="… 1/3";'
        . 'return Promise.race([navigator.serviceWorker.ready,new Promise(function(_,no){setTimeout(function(){no(new Error("service worker not ready"));},10000);})]).then(function(r){m.textContent="… 2/3";return r.pushManager.subscribe({userVisibleOnly:true,applicationServerKey:key(c.dataset.key)});}).catch(function(e){rep("subscribe",e);throw e;}).then(function(s){m.textContent="… 3/3";'
        . 'return fetch(c.dataset.api,{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json","X-WP-Nonce":c.dataset.nonce},body:JSON.stringify(s)});}).then(function(r){if(!r.ok){rep("save "+r.status);return;}m.textContent=W.done;c.querySelector(".push-on").hidden=true;c.querySelector(".push-no").hidden=true;setTimeout(function(){c.hidden=true;},4000);});'
        . '}).catch(function(e){if(m.textContent.indexOf("(")<0)rep("other",e);});});'
        . 'c.querySelector(".push-no").addEventListener("click",function(){try{localStorage.setItem(k,"1");}catch(e){}c.hidden=true;});})();</script>';
}, 2, 3);
add_action('rest_api_init', function () {
    register_rest_route('cc/v1', '/push-sub', ['methods' => 'POST', 'permission_callback' => 'is_user_logged_in', 'callback' => function (WP_REST_Request $r) {
        $s = $r->get_json_params(); $ep = esc_url_raw((string) ($s['endpoint'] ?? ''), ['https']);
        if ($ep === '' || empty($s['keys']['p256dh']) || empty($s['keys']['auth'])) return new WP_Error('cc_bad', 'Bad subscription', ['status' => 400]);
        $uid = get_current_user_id(); $subs = get_user_meta($uid, 'cc_push', true); $subs = is_array($subs) ? $subs : [];
        $subs[md5($ep)] = ['endpoint' => $ep, 'keys' => ['p256dh' => sanitize_text_field($s['keys']['p256dh']), 'auth' => sanitize_text_field($s['keys']['auth'])], 'at' => time()];
        update_user_meta($uid, 'cc_push', array_slice($subs, -5, null, true)); return ['ok' => true];
    }]);
    register_rest_route('cc/v1', '/push-log', ['methods' => 'POST', 'permission_callback' => 'is_user_logged_in', 'callback' => function (WP_REST_Request $r) {   // what went wrong on a phone
        $l = get_option('cc_push_log', []); $l = is_array($l) ? $l : [];
        array_unshift($l, ['at' => time(), 'user' => wp_get_current_user()->display_name] + array_map(function ($x) { return substr(sanitize_text_field((string) $x), 0, 300); }, (array) $r->get_json_params()));
        update_option('cc_push_log', array_slice($l, 0, 20), false); return ['ok' => true];
    }]);
    register_rest_route('cc/v1', '/push-test', ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function () {   // Matteo: a test to his own phones
        return ['sent' => cc_push_user(get_current_user_id(), 'Cigala Cycling', 'Test: notifications work on this phone.', home_url('/' . CC_ATH_SLUG . '/'), 'cc-test')];
    }]);
    register_rest_route('cc/v1', '/push-status', ['methods' => 'GET', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function () {
        $n = 0; $who = []; foreach (get_users(['meta_key' => 'cc_push', 'fields' => ['ID', 'display_name']]) as $u) { $c = count((array) get_user_meta($u->ID, 'cc_push', true)); if ($c) { $n += $c; $who[] = $u->display_name; } }
        return ['openssl' => function_exists('openssl_pkey_derive'), 'key' => (bool) cc_push_vapid(), 'phones' => $n, 'people' => $who, 'log' => array_slice((array) get_option('cc_push_log', []), 0, 5)];
    }]);
    register_rest_route('cc/v1', '/push-selftest', ['methods' => 'GET', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function () {   // encryption round trip check (no sending)
        $ua = openssl_pkey_new(['curve_name' => 'prime256v1', 'private_key_type' => OPENSSL_KEYTYPE_EC]); $auth = random_bytes(16);
        $body = cc_push_encrypt('{"t":"hello"}', cc_push_b64u(cc_push_raw_pub($ua)), cc_push_b64u($auth)); if (!$body) return ['ok' => false, 'step' => 'encrypt'];
        $salt = substr($body, 0, 16); $as = substr($body, 21, 65); $ct = substr($body, 86, -16); $tag = substr($body, -16);
        $shared = openssl_pkey_derive(openssl_pkey_get_public(cc_push_pem_from_raw($as)), $ua, 32);
        $ikm = hash_hkdf('sha256', $shared, 32, "WebPush: info\0" . cc_push_raw_pub($ua) . $as, $auth);
        $pt = openssl_decrypt($ct, 'aes-128-gcm', hash_hkdf('sha256', $ikm, 16, "Content-Encoding: aes128gcm\0", $salt), OPENSSL_RAW_DATA, hash_hkdf('sha256', $ikm, 12, "Content-Encoding: nonce\0", $salt), $tag);
        $v = cc_push_vapid(); $ok_sig = openssl_sign('x', $sig, openssl_pkey_get_private($v['pem']), OPENSSL_ALGO_SHA256) && strlen(cc_push_der2raw($sig)) === 64;
        return ['ok' => $pt === "{\"t\":\"hello\"}\x02", 'jwt_sig' => $ok_sig];
    }]);
});
