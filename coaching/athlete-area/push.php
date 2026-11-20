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
// Matteo 18 Nov: a line in the bell only, no phone buzz (Vekta replies: Vekta's own app already buzzes the phone)
/* 20 Nov 2026 (smoothness): no piling up. An unread line with the same tag, link and athlete is replaced (moved to the top, new time)
 * and keeps a count ('n'), shown as "(3)". Returns the line's time ('at'), which push links carry as ?n=<at>. */
function cc_inbox_put($uid, $title, $body, $url, $tag = '', $from = 0) {
    $in = get_user_meta((int) $uid, 'cc_inbox', true); $in = is_array($in) ? $in : [];
    $url = esc_url_raw($url); $n = 1;
    if ((string) $tag !== '') foreach ($in as $k => $x) {
        if (empty($x['read']) && (string) ($x['tag'] ?? '') === (string) $tag && (string) ($x['url'] ?? '') === $url && (int) ($x['from'] ?? 0) === (int) $from) { $n += max(1, (int) ($x['n'] ?? 1)); unset($in[$k]); }
    }
    $at = time(); foreach ($in as $x) if ((int) ($x['at'] ?? 0) >= $at) $at = (int) $x['at'] + 1;   // each line its own time (the ?n= key)
    array_unshift($in, ['at' => $at, 'title' => wp_strip_all_tags($title), 'body' => wp_strip_all_tags($body), 'url' => $url, 'read' => 0, 'tag' => (string) $tag, 'from' => (int) $from, 'n' => $n]);
    update_user_meta((int) $uid, 'cc_inbox', array_slice(array_values($in), 0, 40));
    return $at;
}
/* Reading elsewhere clears the bell: marks this person's unread lines read when the tag matches (exact, or "tag-…" when $prefix)
 * and the link contains every piece in $has. Returns how many lines changed. */
function cc_inbox_mark($uid, $tags, $has = [], $prefix = false) {
    $uid = (int) $uid; if (!$uid) return 0;
    $in = get_user_meta($uid, 'cc_inbox', true); if (!is_array($in) || !$in) return 0;
    $c = 0;
    foreach ($in as &$x) {
        if (!empty($x['read'])) continue; $t = (string) ($x['tag'] ?? ''); $ok = false;
        foreach ((array) $tags as $w) if ($t === $w || ($prefix && strpos($t, $w . '-') === 0)) $ok = true;
        if (!$ok) continue;
        foreach ((array) $has as $h) if ($h !== '' && strpos((string) ($x['url'] ?? ''), (string) $h) === false) $ok = false;
        if ($ok) { $x['read'] = 1; $c++; }
    }
    unset($x);
    if ($c) update_user_meta($uid, 'cc_inbox', $in);
    return $c;
}
function cc_inbox_mark_at($uid, $at) {   // the line a phone notification was about (?n=<at>)
    $uid = (int) $uid; $at = (int) $at; if (!$uid || !$at) return 0;
    $in = get_user_meta($uid, 'cc_inbox', true); if (!is_array($in)) return 0; $c = 0;
    foreach ($in as &$x) if ((int) ($x['at'] ?? 0) === $at && empty($x['read'])) { $x['read'] = 1; $c++; }
    unset($x); if ($c) update_user_meta($uid, 'cc_inbox', $in); return $c;
}
// opening a page marks what it shows: ?n=<at> from a phone notification; Matteo's boards (notes, results, blood tests, forms, ideas)
add_action('template_redirect', function () {
    if (!is_user_logged_in() || !function_exists('cc_ath_is_area') || !cc_ath_is_area() || (function_exists('cc_ath_demo_as') && cc_ath_demo_as())) return;
    $uid = get_current_user_id();
    if (!empty($_GET['n']) && !isset($_GET['done'])) cc_inbox_mark_at($uid, (int) $_GET['n']);
    $bd = isset($_GET['board']) ? sanitize_key($_GET['board']) : '';
    $by = ['notes' => 'cc-note', 'results' => 'cc-result', 'blood' => 'cc-blood', 'forms' => 'cc-form', 'ideas' => 'cc-idea'];
    if ($bd !== '' && isset($by[$bd]) && current_user_can('edit_pages')) cc_inbox_mark($uid, [$by[$bd]]);
    if ($bd === 'blood' && !current_user_can('edit_pages')) cc_inbox_mark($uid, ['cc-blood']);   // the nutritionist's blood-test board
}, 5);
function cc_inbox_add($uid, $title, $body, $url, $tag = '', $from = 0) { return cc_inbox_put($uid, $title, $body, $url, $tag, $from); }
function cc_push_user($uid, $title, $body, $url, $tag = '', $from = 0) {
    // Matteo 17 Nov: every notification also goes to their notification centre (the bell in the hub), phone or not
    // $from: the athlete page it is about (their face shows in Matteo's bell; athletes always see Matteo's face)
    $at = cc_inbox_put($uid, $title, $body, $url, $tag, $from);
    $subs = get_user_meta((int) $uid, 'cc_push', true); if (!is_array($subs) || !$subs) return 0;
    $sent = 0; $msg = ['title' => $title, 'body' => wp_strip_all_tags($body), 'url' => add_query_arg('n', $at, $url), 'tag' => $tag ?: 'cc-' . time()];
    foreach ($subs as $k => $s) { $st = cc_push_one($s, $msg); if ($st >= 200 && $st < 300) $sent++; elseif (in_array($st, [404, 410], true)) unset($subs[$k]); }
    update_user_meta((int) $uid, 'cc_push', $subs); return $sent;
}
function cc_push_coaches($title, $body, $url, $tag = '', $from = 0) {   // Matteo (any coach account with a phone turned on)
    foreach (get_users(['capability' => 'edit_pages', 'fields' => 'ID']) as $uid) cc_push_user((int) $uid, $title, $body, $url, $tag, $from);   // every coach account: bell always, phone if turned on
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
       // Matteo 17 Nov: tapping a notification always opens the hub (focus an open hub window and go to the page, else open a new one)
       . "self.addEventListener('notificationclick',function(e){e.notification.close();var u=new URL((e.notification.data&&e.notification.data.url)||'/" . CC_ATH_SLUG . "/',self.location.origin).href;"
       . "e.waitUntil(self.clients.matchAll({type:'window',includeUncontrolled:true}).then(function(cs){var c=cs.filter(function(x){return x.url.indexOf('/" . CC_ATH_SLUG . "/')>-1;})[0];"
       . "if(c&&'focus' in c){return c.focus().then(function(f){f=f||c;if(f.url!==u&&'navigate' in f)return f.navigate(u).catch(function(){return self.clients.openWindow(u);});});}"
       . "return self.clients.openWindow(u);}).catch(function(){return self.clients.openWindow(u);}));});\n";
    exit;
}, 1);
function cc_push_w($k) {
    static $W = [
        'title' => ['en' => 'Get notifications on this device', 'it' => 'Ricevi le notifiche su questo dispositivo', 'pt' => 'Recebe notificações neste dispositivo', 'sl' => 'Prejemaj obvestila na tej napravi', 'sk' => 'Dostávaj upozornenia na tomto zariadení'],
        'text' => ['en' => 'This device tells you when I reply to your note or something new is in your hub.', 'it' => 'Questo dispositivo ti avvisa quando rispondo al tuo messaggio o c’è qualcosa di nuovo nella tua area.',
                   'pt' => 'Este dispositivo avisa-te quando respondo à tua mensagem ou há algo novo na tua área.', 'sl' => 'Ta naprava te obvesti, ko odgovorim na tvoje sporočilo ali je v tvojem središču kaj novega.', 'sk' => 'Toto zariadenie ti dá vedieť, keď odpoviem na tvoju správu alebo keď bude v tvojej zóne niečo nové.'],
        'coach' => ['en' => 'This device tells you about new notes, results, signups, signed forms and ideas.', 'it' => 'This device tells you about new notes, results, signups, signed forms and ideas.', 'pt' => 'This device tells you about new notes, results, signups, signed forms and ideas.', 'sl' => 'This device tells you about new notes, results, signups, signed forms and ideas.', 'sk' => 'This device tells you about new notes, results, signups, signed forms and ideas.'],
        'ask' => ['en' => 'Your browser did not ask. Click the lock or bell icon next to the web address, allow notifications for this site, then tap the button again.',
                  'it' => 'Il browser non ha chiesto. Clicca sull’icona del lucchetto o della campanella accanto all’indirizzo, consenti le notifiche per questo sito, poi tocca di nuovo il pulsante.',
                  'pt' => 'O navegador não perguntou. Clica no ícone do cadeado ou do sino junto ao endereço, permite as notificações deste site e toca de novo no botão.',
                  'sl' => 'Brskalnik ni vprašal. Klikni ikono ključavnice ali zvonca ob naslovu, dovoli obvestila za to stran in znova tapni gumb.', 'sk' => 'Prehliadač sa neopýtal. Klikni na ikonu zámku alebo zvončeka vedľa adresy, povoľ upozornenia pre túto stránku a potom znova ťukni na tlačidlo.'],
        // Android: the phone could not reach Google's notification service (Chrome needs it)
        'android' => ['en' => 'This phone could not connect to Google’s notification service. Update Google Play services and Chrome, turn off any VPN or ad blocker (also “Private DNS” in Settings), allow Chrome to run in the background (Battery settings; on Xiaomi/Redmi also turn on Autostart for Chrome and Google Play services), then tap the button again. Everything still shows in the bell in your hub.',
                      'it' => 'Questo telefono non riesce a collegarsi al servizio di notifiche di Google. Aggiorna Google Play Services e Chrome, disattiva VPN o blocco pubblicità (anche “DNS privato” nelle Impostazioni), consenti a Chrome di funzionare in background (impostazioni Batteria; su Xiaomi/Redmi attiva anche l’Avvio automatico per Chrome e Google Play Services), poi tocca di nuovo il pulsante. Trovi comunque tutto nella campanella della tua area.',
                      'pt' => 'Este telemóvel não conseguiu ligar-se ao serviço de notificações da Google. Atualiza os Serviços do Google Play e o Chrome, desliga qualquer VPN ou bloqueador de anúncios (também “DNS privado” nas Definições), permite que o Chrome funcione em segundo plano (definições de Bateria; num Xiaomi/Redmi ativa também o Início automático para o Chrome e os Serviços do Google Play) e toca de novo no botão. Tudo continua a aparecer no sino da tua área.',
                      'sl' => 'Ta telefon se ni mogel povezati z Googlovo storitvijo za obvestila. Posodobi storitve Google Play in Chrome, izklopi VPN ali blokator oglasov (tudi »Zasebni DNS« v nastavitvah), dovoli Chromu delovanje v ozadju (nastavitve baterije; na Xiaomi/Redmi vklopi tudi Samodejni zagon za Chrome in storitve Google Play) in znova tapni gumb. Vse je še vedno v zvoncu v tvojem središču.', 'sk' => 'Tento telefón sa nevedel pripojiť k službe upozornení od Googlu. Aktualizuj Služby Google Play a Chrome, vypni VPN alebo blokovanie reklám (aj „Súkromný DNS“ v Nastaveniach), povoľ Chromu bežať na pozadí (nastavenia batérie; na Xiaomi/Redmi zapni aj Automatické spustenie pre Chrome a Služby Google Play) a potom znova ťukni na tlačidlo. Všetko sa ti aj tak zobrazuje pod zvončekom v tvojej zóne.'],
        'on' => ['en' => 'Turn on notifications', 'it' => 'Attiva le notifiche', 'pt' => 'Ativar notificações', 'sl' => 'Vklopi obvestila', 'sk' => 'Zapnúť upozornenia'],
        'no' => ['en' => 'Not now', 'it' => 'Non ora', 'pt' => 'Agora não', 'sl' => 'Ne zdaj', 'sk' => 'Teraz nie'],
        'done' => ['en' => 'Notifications are on for this device.', 'it' => 'Notifiche attive su questo dispositivo.', 'pt' => 'Notificações ativas neste dispositivo.', 'sl' => 'Obvestila so vklopljena na tej napravi.', 'sk' => 'Upozornenia sú na tomto zariadení zapnuté.'],
        'ios' => ['en' => 'On iPhone, add the hub to your Home Screen first, then open it from there to turn notifications on.', 'it' => 'Su iPhone aggiungi prima l’area alla schermata Home, poi aprila da lì per attivare le notifiche.',
                  'pt' => 'No iPhone, adiciona primeiro a área ao ecrã principal e abre-a a partir daí para ativar as notificações.', 'sl' => 'Na iPhonu najprej dodaj središče na začetni zaslon in ga odpri od tam, da vklopiš obvestila.', 'sk' => 'Na iPhone si najprv pridaj zónu na plochu a otvor ju odtiaľ: až potom sa dajú zapnúť upozornenia.'],
        'denied' => ['en' => 'Notifications are blocked for this site in your phone settings.', 'it' => 'Le notifiche per questo sito sono bloccate nelle impostazioni del telefono.', 'pt' => 'As notificações deste site estão bloqueadas nas definições do telemóvel.', 'sl' => 'Obvestila za to stran so blokirana v nastavitvah telefona.', 'sk' => 'Upozornenia pre túto stránku sú zablokované v nastaveniach telefónu.'],
    ];
    $l = $GLOBALS['cc_ath_lang'] ?? 'en'; return $W[$k][$l] ?? $W[$k]['en'];
}
// the card: on the hub, until notifications are on for this phone (or "Not now"); for athletes and for Matteo
add_filter('cc_ath_before_reports', function ($html, $view, $coach) {
    $v = cc_push_vapid(); if (!$v) return $html;
    $W = ['done' => cc_push_w('done'), 'ios' => cc_push_w('ios'), 'denied' => cc_push_w('denied'), 'ask' => cc_push_w('ask'), 'android' => cc_push_w('android')];
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
        . 'Promise.resolve(pr).then(function(p){p=p||Notification.permission;if(p!=="granted"){rep("permission "+p);if(p==="default")m.textContent=W.ask;return;}m.textContent="… 1/3";'
        . 'return Promise.race([navigator.serviceWorker.ready,new Promise(function(_,no){setTimeout(function(){no(new Error("service worker not ready"));},10000);})]).then(function(r){m.textContent="… 2/3";'
        // Matteo 17 Nov (Android: "Registration failed - push service error"): try up to 3 times, clearing any half-made subscription in between
        . 'function sub(n){return r.pushManager.subscribe({userVisibleOnly:true,applicationServerKey:key(c.dataset.key)}).catch(function(e){if(n>=2)throw e;m.textContent="… 2/3 ("+(n+2)+")";'
        . 'return r.pushManager.getSubscription().then(function(s){return s&&s.unsubscribe();}).catch(function(){}).then(function(){return new Promise(function(ok){setTimeout(ok,1500);});}).then(function(){return sub(n+1);});});}return sub(0);})'
        . '.catch(function(e){rep("subscribe",e);if(/android/i.test(navigator.userAgent))m.textContent=W.android+" ("+(e&&e.message||e)+")";throw e;}).then(function(s){m.textContent="… 3/3";'
        . 'return fetch(c.dataset.api,{method:"POST",credentials:"same-origin",headers:{"Content-Type":"application/json","X-WP-Nonce":c.dataset.nonce},body:JSON.stringify(s)});}).then(function(r){if(!r.ok){rep("save "+r.status);return;}m.textContent=W.done;c.querySelector(".push-on").hidden=true;c.querySelector(".push-no").hidden=true;setTimeout(function(){c.hidden=true;},4000);});'
        . '}).catch(function(e){if(m.textContent.indexOf("(")<0)rep("other",e);});});'
        . 'c.querySelector(".push-no").addEventListener("click",function(){try{localStorage.setItem(k,"1");}catch(e){}c.hidden=true;});})();</script>';
}, 2, 3);
/* ---------- the notification centre: a bell next to "Log out", with the last 40 notifications ---------- */
function cc_inbox_w($k) {
    static $W = ['title' => ['en' => 'Notifications', 'it' => 'Notifiche', 'pt' => 'Notificações', 'sl' => 'Obvestila', 'sk' => 'Upozornenia'],
                 'empty' => ['en' => 'Nothing yet. My replies, your new reports and news show up here.', 'it' => 'Ancora niente. Qui compaiono le mie risposte, i tuoi nuovi report e le novità.',
                             'pt' => 'Ainda nada. Aqui aparecem as minhas respostas, os teus novos relatórios e as novidades.', 'sl' => 'Še nič. Tu se pojavijo moji odgovori, tvoja nova poročila in novice.', 'sk' => 'Zatiaľ nič. Tu sa objavia moje odpovede, tvoje nové reporty a novinky.'],
                 'fresh' => ['en' => 'New: tap to see', 'it' => 'Novità: tocca per vedere', 'pt' => 'Novidade: toca para ver', 'sl' => 'Novo: tapni za ogled', 'sk' => 'Novinka: ťukni a pozri'],
                 'all' => ['en' => 'Mark all as read', 'it' => 'Segna tutte come lette', 'pt' => 'Marcar todas como lidas', 'sl' => 'Označi vse kot prebrano', 'sk' => 'Označiť všetko ako prečítané']];
    $l = $GLOBALS['cc_ath_lang'] ?? 'en'; return $W[$k][$l] ?? $W[$k]['en'];
}
function cc_inbox_get($uid) { $in = get_user_meta((int) $uid, 'cc_inbox', true); return is_array($in) ? $in : []; }
function cc_inbox_unread($uid) { $n = 0; foreach (cc_inbox_get($uid) as $x) if (empty($x['read'])) $n += max(1, (int) ($x['n'] ?? 1)); return $n; }
// Matteo 17 Nov: each line shows who it is from, like the notes: athletes see Matteo's photo, Matteo sees the athlete's (else the Cigala icon)
function cc_inbox_guess_from($title) {   // "🏆 Result from Laura X", "Note from …", "Rider form signed: …", "Hub idea: …" → that athlete's page
    static $by = null;
    if ($by === null) { $by = []; foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'fields' => 'ids']) as $id) $by[mb_strtolower(trim(get_the_title($id)))] = (int) $id; }
    $title = preg_replace('/\b(?:Private|Privato|Privado|Zasebno):\s*/u', '', $title);   // older lines carried WordPress's "Private: " prefix
    if (!preg_match('/(?:\bfrom|:)\s+(.+)$/u', $title, $m)) return 0;
    return $by[mb_strtolower(trim($m[1]))] ?? 0;
}
function cc_inbox_items($uid) {
    $coach = user_can((int) $uid, 'edit_pages'); $items = '';
    $matteo = '<img class="bell-f" src="https://coaching.cigalacycling.com/wp-content/uploads/2026/11/cigala-email-matteo-photo.jpg" alt="">';
    $logo = '<img class="bell-f" src="https://coaching.cigalacycling.com/wp-content/uploads/2026/11/cigala-hub-app-192.png" alt="">';
    $vivify = '<img class="bell-f" src="https://coaching.cigalacycling.com/wp-content/uploads/2026/11/vivify-tile.png" alt="">';
    foreach (cc_inbox_get($uid) as $x) {
        $from = (int) ($x['from'] ?? 0);
        if (!$from && $coach) $from = cc_inbox_guess_from((string) $x['title']);   // older lines: the athlete's name is in the title
        // 19 Nov: athletes see the sender's face: Marine (nutritionist) gets her Vivify logo, as in blood.php; anything else is from Matteo.
        // Her lines are recognised by 'who' => 'nutri' or by her name in the title ("Marine replied…", "A Marine respondeu…").
        $nutri = ($x['who'] ?? '') === 'nutri' || preg_match('/\bMarine\b/u', (string) $x['title']);
        $face = !$coach ? ($nutri ? $vivify : $matteo) : ($from && function_exists('cc_ph_widget') && get_post_type($from) === 'cc_athlete' ? cc_ph_widget($from, 40, false, 'bell-f') : $logo);
        $items .= '<a class="bell-it' . (empty($x['read']) ? ' new" data-c="' . max(1, (int) ($x['n'] ?? 1)) . '" data-at="' . (int) $x['at'] . '" data-tag="' . esc_attr((string) ($x['tag'] ?? '')) : '') . '" href="' . esc_url($x['url'] ?: home_url('/' . CC_ATH_SLUG . '/')) . '">' . $face . '<span class="bell-t"><b>' . esc_html(preg_replace('/\b(?:Private|Privato|Privado|Zasebno):\s*/u', '', (string) $x['title']) . ((int) ($x['n'] ?? 1) > 1 ? ' (' . (int) $x['n'] . ')' : '')) . '</b>'
            . ($x['body'] !== '' ? '<span>' . esc_html($x['body']) . '</span>' : '') . '<small>' . esc_html(cc_r_ago((int) $x['at'])) . '</small></span></a>';
    }
    return $items ?: '<p class="bell-e">' . esc_html(cc_inbox_w('empty')) . '</p>';
}
add_filter('cc_ath_hero_links', function ($html, $coach) {
    $uid = get_current_user_id(); if (!$uid) return $html;
    // Matteo 19 Nov: on his demo page (athlete view) the bell is the demo athlete's: empty, and it never reads or marks his own coach inbox
    $demo = function_exists('cc_ath_demo_as') && cc_ath_demo_as(); if ($demo) $uid = 0;
    $unread = cc_inbox_unread($uid);
    return $html . ' <span class="bell-w"><button type="button" class="ath-bell" aria-label="' . esc_attr(cc_inbox_w('title')) . '" aria-expanded="false" data-api="' . esc_url(rest_url('cc/v1/inbox-read')) . '" data-nonce="' . esc_attr(wp_create_nonce('wp_rest')) . '" data-n="' . $unread . '" data-fresh="' . esc_attr(cc_inbox_w('fresh')) . '"' . ($demo ? ' data-demo="1"' : '') . '>'
        . '<svg viewBox="0 0 24 24"><path d="M6 16V11a6 6 0 0 1 12 0v5l2 2H4zM10 20a2 2 0 0 0 4 0"/></svg>' . ($unread ? '<i>' . min(99, $unread) . '</i>' : '') . '</button>'
        . '<div class="bell-p" hidden><p class="bell-h">' . esc_html(cc_inbox_w('title')) . '<button type="button" class="bell-all"' . ($unread ? '' : ' hidden') . '>' . esc_html(cc_inbox_w('all')) . '</button></p><div class="bell-l">' . cc_inbox_items($uid) . '</div></div></span>' . (function_exists('cc_ph_assets') ? cc_ph_assets() : '')
        // Matteo 17 Nov: top-right corner of the header (like apps); the list opens on top of the page (the header clips what sticks out)
        . '<style>html .cc .bell-w{position:absolute;top:14px;right:14px;z-index:5}html .cc .ath-bell{box-shadow:0 4px 14px rgba(0,0,0,.5);position:relative;width:44px;height:44px;min-height:0;padding:0;margin:0;border-radius:50%;border:1px solid rgba(255,255,255,.2);background:rgba(12,14,16,.85);display:grid;place-items:center;cursor:pointer}'
        . 'html .cc .ath-bell svg{width:22px;height:22px;fill:none;stroke:#fff;stroke-width:2;stroke-linejoin:round}html .cc .ath-bell i{position:absolute;top:-4px;right:-4px;min-width:20px;height:20px;padding:0 5px;border-radius:999px;background:#E10600;color:#fff;font:700 12px/20px var(--body);font-style:normal;text-align:center}'
        . 'html body .bell-p{font-family:Montserrat,system-ui,sans-serif;position:fixed;z-index:99990;width:min(360px,calc(100vw - 32px));max-height:65vh;overflow:auto;padding:8px;border-radius:14px;border:1px solid rgba(255,255,255,.15);background:#0b0d0f;box-shadow:0 18px 40px rgba(0,0,0,.6)}html body .bell-p[hidden]{display:none}'
        . 'html body .bell-h{margin:4px 8px 8px;font-weight:700;color:#fff;font-size:16px;display:flex;align-items:center;justify-content:space-between;gap:8px}html body .bell-all{min-height:44px;padding:0 10px;border:0;background:none;color:#2bd47a;font:600 14px/1.2 Montserrat,system-ui,sans-serif;cursor:pointer;text-decoration:underline}html body .bell-all[hidden]{display:none}html body .bell-it{display:flex;align-items:flex-start;gap:12px;padding:10px;border-radius:10px;text-decoration:none;color:#d0d6e0}html body .bell-it:hover{background:rgba(255,255,255,.06)}'
        . 'html body .bell-it .bell-f{flex:none;width:40px;height:40px;border-radius:50%;object-fit:cover;border:2px solid #2bd47a;--ph:40px}html body .bell-it .bell-f .ph-ini{font-size:14px}'
        . 'html body span.bell-f{display:grid;place-items:center;overflow:hidden;background:linear-gradient(135deg,#12a150,#0b6b37);color:#fff;font-weight:700}html body span.bell-f img{width:100%;height:100%;object-fit:cover;border-radius:50%;display:block}'
        . 'html body .bell-t{display:grid;gap:2px;min-width:0}html body .bell-it.new{background:rgba(18,161,80,.14)}html body .bell-it b{color:#fff;font-size:15px;line-height:1.3}html body .bell-t span{font-size:15px;line-height:1.4;color:#d0d6e0}'
        . 'html body .bell-it small{font-size:14px;color:#b8bec8}html body .bell-e{margin:6px 8px 10px;font-size:15px;color:#d0d6e0}'
        // the pill floats at the bottom of the screen (under the bell it covered the greeting on phones, and the bell scrolls away)
        . 'html body .bell-new{position:fixed;left:50%;bottom:max(18px,env(safe-area-inset-bottom));transform:translateX(-50%);z-index:99980;white-space:nowrap;min-height:44px;padding:0 18px;border-radius:999px;border:1px solid rgba(255,255,255,.25);background:#12a150;color:#fff;font:600 15px/1 Montserrat,system-ui,sans-serif;box-shadow:0 8px 24px rgba(0,0,0,.6);cursor:pointer}</style>'
        . '<script>(function(){var b=document.querySelector(".ath-bell");if(!b||b.dataset.on)return;b.dataset.on=1;var p=b.parentNode.querySelector(".bell-p");'
        . 'document.body.appendChild(p);'   // out of the header, so nothing clips it
        . 'var hero=b.closest(".ath-hero");if(hero&&b.parentNode.parentNode!==hero)hero.appendChild(b.parentNode);'   // the bell sits in the header's own top-right corner (not the text column's)
        . 'function place(){var r=b.getBoundingClientRect(),w=p.offsetWidth||340;p.style.top=Math.round(r.bottom+8)+"px";p.style.left=Math.max(16,Math.min(window.innerWidth-w-16,Math.round(r.right-w)))+"px";}'
        . 'addEventListener("resize",function(){if(!p.hidden)place();});addEventListener("scroll",function(){if(!p.hidden)place();},{passive:true});'
        . 'b.addEventListener("click",function(e){e.stopPropagation();if(!p.hidden){shut();return;}p.hidden=false;place();b.setAttribute("aria-expanded","true");});'
        // Matteo 20 Nov: opening the bell no longer clears everything; each line is marked read when tapped and the number goes down one by one
        . 'function setn(n){var i=b.querySelector("i");if(n>0){if(!i){i=document.createElement("i");b.appendChild(i);}i.textContent=Math.min(99,n);}else if(i)i.remove();var a=p.querySelector(".bell-all");if(a)a.hidden=n<=0;shown=n;try{if(n>0&&navigator.setAppBadge)navigator.setAppBadge(n);else if(navigator.clearAppBadge)navigator.clearAppBadge();}catch(x){}}'
        . 'function mark(body){if(b.dataset.demo)return;try{fetch(b.dataset.api,{method:"POST",keepalive:true,credentials:"same-origin",headers:{"X-WP-Nonce":b.dataset.nonce,"Content-Type":"application/json"},body:JSON.stringify(body||{})});}catch(x){}}'
        . 'p.addEventListener("click",function(e){var a=e.target.closest(".bell-all");if(a){e.preventDefault();[].forEach.call(p.querySelectorAll(".bell-it.new"),function(x){x.classList.remove("new");});setn(0);mark({});return;}'
        . 'var it=e.target.closest(".bell-it.new");if(!it)return;it.classList.remove("new");mark({at:+it.dataset.at,tag:it.dataset.tag||""});setn(cnt());});'
        . 'function cnt(){var n=0;[].forEach.call(p.querySelectorAll(".bell-it.new"),function(x){n+=(+x.dataset.c||1);});return n;}'
        . 'var later=null;function shut(){p.hidden=true;b.setAttribute("aria-expanded","false");if(later!==null){p.querySelector(".bell-l").innerHTML=later;later=null;}}'
        . 'document.addEventListener("click",function(e){if(!p.hidden&&!p.contains(e.target))shut();});'
        // 20 Nov (smoothness): a phone notification's ?n=<at> was marked on the server; take it off the address so a reload stays clean
        . 'try{var U=new URL(location.href);if(U.searchParams.has("n")&&!U.searchParams.has("done")){U.searchParams.delete("n");history.replaceState(history.state,"",U.pathname+U.search+U.hash);}}catch(x){}'
        // Matteo 17 Nov: opening the app from a notification brought back the old page. Each time the hub comes back on screen it asks for the
        // latest notifications. 20 Nov: the page never reloads by itself any more: a small "New: tap to see" pill appears under the bell
        // and reloads only when tapped; the open list is not redrawn under the finger (it is refreshed when it closes)
        . 'var shown=+b.dataset.n||0,pill=null;'
        . 'function fresh(){if(b.dataset.demo)return;fetch(b.dataset.api.replace("inbox-read","inbox"),{credentials:"same-origin",cache:"no-store",headers:{"X-WP-Nonce":b.dataset.nonce}}).then(function(r){return r.ok?r.json():null;}).then(function(j){if(!j)return;'
        . 'if(p.hidden)p.querySelector(".bell-l").innerHTML=j.html;else later=j.html;var was=shown;setn(j.unread);'
        . 'if(j.unread>was&&!pill){pill=document.createElement("button");pill.type="button";pill.className="bell-new";pill.textContent=b.dataset.fresh;pill.addEventListener("click",function(){location.reload();});document.body.appendChild(pill);}}).catch(function(){});}'
        . 'window.ccBell={fresh:fresh,set:function(n){setn(n);}};'
        . 'document.addEventListener("visibilitychange",function(){if(document.visibilityState==="visible")fresh();});addEventListener("pageshow",function(e){if(e.persisted)fresh();});addEventListener("focus",fresh);'
        . '})();</script>' . cc_ui_lib();
}, 30, 2);
/* 20 Nov 2026 (smoothness): small shared helpers for every hub page that has the bell.
 * ccAsk(question, "del"|"yes") -> Promise<bool>: an in-page confirm sheet (translated Delete / Yes / Cancel) instead of the phone's confirm().
 * ccErr(el, text?): a short red line under el when something did not go through (text optional, translated default).
 * ccGo(param, hash): reload with one fresh ?param=<time> (old nt/rs/bt/fd/n removed) and come back to hash.
 * After a page opened with ?nt/rs/bt/fd/n (or #nt-/#fd-/#vx-) has used them, they are taken off the address, so a later reload opens today. */
function cc_ui_w($k) {
    static $W = [
        'del' => ['en' => 'Delete', 'it' => 'Elimina', 'pt' => 'Apagar', 'sl' => 'Izbriši', 'sk' => 'Vymazať'],
        'yes' => ['en' => 'Yes', 'it' => 'Sì', 'pt' => 'Sim', 'sl' => 'Da', 'sk' => 'Áno'],
        'no' => ['en' => 'Cancel', 'it' => 'Annulla', 'pt' => 'Cancelar', 'sl' => 'Prekliči', 'sk' => 'Zrušiť'],
        'q' => ['en' => 'Delete?', 'it' => 'Eliminare?', 'pt' => 'Apagar?', 'sl' => 'Izbrišem?', 'sk' => 'Vymazať?'],
        'err' => ['en' => 'That did not go through. Please try again.', 'it' => 'Non è andato a buon fine. Riprova.', 'pt' => 'Não foi possível. Tenta de novo.', 'sl' => 'Ni uspelo. Poskusi znova.', 'sk' => 'Nepodarilo sa. Skús to znova.'],
    ];
    $l = $GLOBALS['cc_ath_lang'] ?? 'en'; return $W[$k][$l] ?? $W[$k]['en'];
}
function cc_ui_lib() {
    static $done = false; if ($done) return ''; $done = true;
    $T = []; foreach (['del', 'yes', 'no', 'q', 'err'] as $k) $T[$k] = cc_ui_w($k);
    return '<style>html body .cc-ask{position:fixed;inset:0;z-index:99995;background:rgba(0,0,0,.6);display:flex;align-items:flex-end;justify-content:center;padding:16px;font-family:Montserrat,system-ui,sans-serif}'
        . 'html body .cc-ask-b{width:min(420px,100%);background:#0b0d0f;border:1px solid rgba(255,255,255,.18);border-radius:16px;padding:18px 16px 16px;box-shadow:0 18px 40px rgba(0,0,0,.6);margin-bottom:max(8px,env(safe-area-inset-bottom))}'
        . 'html body .cc-ask-b p{margin:0 0 14px;font-size:16px;line-height:1.45;color:#fff;font-weight:600}html body .cc-ask-b div{display:flex;gap:10px;justify-content:flex-end;flex-wrap:wrap}'
        . 'html body .cc-ask-b button{min-height:44px;padding:0 18px;border-radius:12px;font:600 16px/1 Montserrat,system-ui,sans-serif;cursor:pointer;border:1px solid rgba(255,255,255,.25);background:transparent;color:#fff}'
        . 'html body .cc-ask-b .cc-ask-ok{border:0;background:#12a150;color:#fff}html body .cc-ask-b .cc-ask-ok.del{background:#E10600}'
        . 'html body .cc-err{margin:8px 0 0;font-size:15px;font-weight:600;color:#ff7a73}@media (min-width:700px){html body .cc-ask{align-items:center}}</style>'
        . '<script>(function(){if(window.ccAsk)return;var T=' . wp_json_encode($T) . ';'
        . 'window.ccAsk=function(q,kind){return new Promise(function(res){var o=document.createElement("div");o.className="cc-ask";o.innerHTML="<div class=\"cc-ask-b\" role=\"dialog\" aria-modal=\"true\"><p></p><div><button type=\"button\" class=\"cc-ask-no\"></button><button type=\"button\" class=\"cc-ask-ok\"></button></div></div>";'
        . 'o.querySelector("p").textContent=q||T.q;var ok=o.querySelector(".cc-ask-ok");ok.textContent=kind==="yes"?T.yes:T.del;if(kind!=="yes")ok.classList.add("del");o.querySelector(".cc-ask-no").textContent=T.no;'
        . 'var last=document.activeElement;function end(v){document.removeEventListener("keydown",key);o.remove();try{if(last&&last.focus)last.focus();}catch(x){}res(v);}function key(e){if(e.key==="Escape")end(false);}'
        . 'o.addEventListener("click",function(e){if(e.target===o)end(false);});ok.addEventListener("click",function(){end(true);});o.querySelector(".cc-ask-no").addEventListener("click",function(){end(false);});document.addEventListener("keydown",key);document.body.appendChild(o);ok.focus();});};'
        . 'window.ccErr=function(el,t){if(!el)return;var p=el.parentNode&&el.parentNode.querySelector(":scope>.cc-err");if(!p){p=document.createElement("p");p.className="cc-err";p.setAttribute("role","alert");el.insertAdjacentElement("afterend",p);}p.textContent=t||T.err;setTimeout(function(){if(p.parentNode)p.remove();},8000);};'
        . 'window.ccDec=function(bd,n){n=n||1;[].forEach.call(document.querySelectorAll("a[href*=\"board="+bd+"\"] .av-badge,a[href*=\"board="+bd+"\"] .ath-n"),function(x){var v=(parseInt(x.textContent,10)||0)-n;if(v>0){x.textContent=x.textContent.replace(/^\s*\d+/,String(v));if(x.dataset.n)x.dataset.n=v;}else{var c=x.closest(".ath-chip");if(c)c.remove();else x.remove();}});};'
        . 'window.ccGo=function(k,h){var U=new URL(location.href);["nt","rs","bt","fd","n"].forEach(function(x){U.searchParams.delete(x);});if(k)U.searchParams.set(k,Date.now());U.hash=h||"";location.replace(U.toString());};'
        . 'setTimeout(function(){try{var U=new URL(location.href),ch=false;["nt","rs","bt","fd"].forEach(function(x){if(U.searchParams.has(x)){U.searchParams.delete(x);ch=true;}});'
        . 'if(ch||/^#(nt-|fd-|vx-|rs-|bt-)/.test(U.hash)){history.replaceState(history.state,"",U.pathname+U.search);}}catch(x){}},4000);'
        . '})();</script>';
}
/* ---------- Settings (Matteo 18 Nov 2026): a gear next to the bell, like in an app ----------
 * Language, notifications (phone + "email me when Matteo replies on Vekta"), change password, log out. They used to sit in
 * the header as a row of links; now the header shows only the bell and the gear. */
function cc_set_w($k) {
    static $W = [
        'set' => ['en' => 'Settings', 'it' => 'Impostazioni', 'pt' => 'Definições', 'sl' => 'Nastavitve', 'sk' => 'Nastavenia'],
        'phone' => ['en' => 'Phone notifications', 'it' => 'Notifiche sul telefono', 'pt' => 'Notificações no telemóvel', 'sl' => 'Obvestila na telefonu', 'sk' => 'Upozornenia v telefóne'],
        'phone_on' => ['en' => 'On for this phone', 'it' => 'Attive su questo telefono', 'pt' => 'Ativas neste telemóvel', 'sl' => 'Vklopljena na tem telefonu', 'sk' => 'Zapnuté v tomto telefóne'],
        'acc' => ['en' => 'Account', 'it' => 'Account', 'pt' => 'Conta', 'sl' => 'Račun', 'sk' => 'Účet'],
    ];
    $l = $GLOBALS['cc_ath_lang'] ?? 'en'; return $W[$k][$l] ?? $W[$k]['en'];
}
add_filter('cc_ath_hero_links', function ($html, $coach) {
    $uid = get_current_user_id(); if (!$uid) return $html;
    $logout = wp_logout_url(home_url('/' . CC_ATH_SLUG . '/'));
    $lang = (!$coach && function_exists('cc_ath_lang_switch')) ? '<div class="set-sec">' . cc_ath_lang_switch() . '</div>' : '';
    $notify = '<div class="set-sec"><p class="set-h">' . esc_html(cc_inbox_w('title')) . '</p>'
        . '<div class="set-row set-push"><span>' . esc_html(cc_set_w('phone')) . '</span><span class="set-pst" hidden>✓ ' . esc_html(cc_set_w('phone_on')) . '</span><button type="button" class="btn btn-go set-pon">' . esc_html(cc_push_w('on')) . '</button></div>'
        . apply_filters('cc_settings_notify', '', $uid, $coach) . '</div>';
    $acc = '<div class="set-sec"><p class="set-h">' . esc_html(cc_set_w('acc')) . '</p>'
        . (function_exists('cc_pw_change_url') ? '<a class="set-a" href="' . esc_url(cc_pw_change_url()) . '">' . esc_html(cc_L('Change password', 'Cambia password')) . '</a>' : '')
        . '<a class="set-a" href="' . esc_url($logout) . '">' . esc_html(cc_t('Log out')) . '</a></div>';
    return $html . '<span class="set-w"><button type="button" class="ath-gear" aria-label="' . esc_attr(cc_set_w('set')) . '" aria-expanded="false">'
        . '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3.2"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/></svg></button>'
        . '<div class="set-p" hidden><p class="bell-h">' . esc_html(cc_set_w('set')) . '</p>' . $lang . $notify . apply_filters('cc_settings_extra', '', $uid, $coach) . $acc . '</div></span>'
        . '<style>html .cc .set-w{position:absolute;top:14px;right:68px;z-index:5}html .cc .ath-gear{box-shadow:0 4px 14px rgba(0,0,0,.5);width:44px;height:44px;min-height:0;padding:0;margin:0;border-radius:50%;border:1px solid rgba(255,255,255,.2);background:rgba(12,14,16,.85);display:grid;place-items:center;cursor:pointer}'
        . 'html .cc .ath-gear svg{width:22px;height:22px;fill:none;stroke:#fff;stroke-width:1.8;stroke-linejoin:round}'
        . 'html body .set-p{font-family:Montserrat,system-ui,sans-serif;position:fixed;z-index:99990;width:min(360px,calc(100vw - 32px));max-height:75vh;overflow:auto;padding:8px 14px 12px;border-radius:14px;border:1px solid rgba(255,255,255,.15);background:#0b0d0f;box-shadow:0 18px 40px rgba(0,0,0,.6);color:#d0d6e0}html body .set-p[hidden]{display:none}'
        . 'html body .set-p .bell-h{margin:4px 0 6px}html body .set-sec{padding:10px 0;border-top:1px solid rgba(255,255,255,.1)}html body .set-h{margin:0 0 6px;font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:#b8bec8;font-weight:700}'
        . 'html body .set-row{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:6px 0;font-size:15px;color:#fff;font-weight:600}html body .set-row .btn{width:auto;margin:0;padding:9px 14px;font:600 15px Montserrat,system-ui,sans-serif;min-height:0;background:#12a150!important;color:#fff!important;border:0!important;border-radius:10px;cursor:pointer;white-space:nowrap}html body .set-row .btn[hidden]{display:none}html body .set-pst{color:#2bd47a;font-size:14px;font-weight:600}'
        . 'html body .set-a{display:block;padding:9px 0;font-size:16px;color:#fff;text-decoration:none;font-weight:600}html body .set-a:hover{color:#2bd47a}'
        . 'html body .set-p form.ath-lang{display:flex!important;align-items:center;justify-content:space-between;gap:10px;margin:0!important}html body .set-p form.ath-lang label{font-size:15px!important;color:#fff;font-weight:600;margin:0}html body .set-p form.ath-lang select{font-size:16px;min-height:38px;padding:5px 28px 5px 10px;border-radius:8px;background:#15181c;color:#fff;border:1px solid rgba(255,255,255,.18)}</style>'
        . '<script>(function(){var g=document.querySelector(".ath-gear");if(!g||g.dataset.on)return;g.dataset.on=1;var w=g.parentNode,p=w.querySelector(".set-p");document.body.appendChild(p);'
        . 'var hero=g.closest(".ath-hero");if(hero&&w.parentNode!==hero)hero.appendChild(w);'
        . 'function place(){var r=g.getBoundingClientRect(),pw=p.offsetWidth||340;p.style.top=Math.round(r.bottom+8)+"px";p.style.left=Math.max(16,Math.min(window.innerWidth-pw-16,Math.round(r.right-pw+56)))+"px";}'
        . 'addEventListener("resize",function(){if(!p.hidden)place();});addEventListener("scroll",function(){if(!p.hidden)place();},{passive:true});'
        . 'g.addEventListener("click",function(e){e.stopPropagation();var bp=document.querySelector(".bell-p");if(bp)bp.hidden=true;p.hidden=!p.hidden;g.setAttribute("aria-expanded",!p.hidden);if(!p.hidden){place();phone();}});'
        . 'document.addEventListener("click",function(e){if(!p.hidden&&!p.contains(e.target)&&e.target!==g){p.hidden=true;g.setAttribute("aria-expanded","false");}});'
        . 'var bl=document.querySelector(".ath-bell");if(bl)bl.addEventListener("click",function(){p.hidden=true;g.setAttribute("aria-expanded","false");});'
        // phone notifications: shows "On for this phone", or a button that brings back the "Turn on notifications" card
        . 'function phone(){var st=p.querySelector(".set-pst"),b=p.querySelector(".set-pon");if(!("serviceWorker" in navigator)||!("Notification" in window)){st.hidden=true;return;}'
        . 'navigator.serviceWorker.getRegistration().then(function(r){return r&&r.pushManager?r.pushManager.getSubscription():null;}).then(function(s){var on=!!s&&Notification.permission==="granted";st.hidden=!on;b.hidden=on;}).catch(function(){});}'
        . 'p.querySelector(".set-pon").addEventListener("click",function(){try{localStorage.removeItem("cc_push_no");}catch(x){}var c=document.querySelector(".ath-push");p.hidden=true;if(c){c.hidden=false;c.scrollIntoView({block:"center",behavior:"smooth"});}else location.reload();});'
        . '})();</script>';
}, 31, 2);
/* 20 Nov (smoothness): "Got it" on news and "add to home screen" dismissals are kept per person (user meta cc_dismiss), not only in
 * this browser's localStorage, so a second phone or a cleared browser does not ask again. */
function cc_dismissed($k) { $uid = get_current_user_id(); if (!$uid) return false; $d = get_user_meta($uid, 'cc_dismiss', true); return is_array($d) && isset($d[$k]); }
function cc_dismiss_attr() { return ' data-dapi="' . esc_url(rest_url('cc/v1/dismiss')) . '" data-dn="' . esc_attr(wp_create_nonce('wp_rest')) . '"'; }
function cc_dismiss_js($el, $key) {   // JS: remember "dismissed" for this person (element with cc_dismiss_attr(), key expression)
    return 'try{if(' . $el . '.dataset.dapi)fetch(' . $el . '.dataset.dapi,{method:"POST",keepalive:true,credentials:"same-origin",headers:{"Content-Type":"application/json","X-WP-Nonce":' . $el . '.dataset.dn},body:JSON.stringify({k:' . $key . '})}).catch(function(){});}catch(x){}';
}
add_action('rest_api_init', function () {
    register_rest_route('cc/v1', '/dismiss', ['methods' => 'POST', 'permission_callback' => 'is_user_logged_in', 'callback' => function (WP_REST_Request $r) {
        $k = preg_replace('/[^A-Za-z0-9_-]/', '', (string) $r->get_param('k')); if ($k === '' || strlen($k) > 40) return new WP_Error('cc_bad', 'Bad key', ['status' => 400]);
        if (function_exists('cc_ath_demo_as') && cc_ath_demo_as()) return ['ok' => true];
        $uid = get_current_user_id(); $d = get_user_meta($uid, 'cc_dismiss', true); $d = is_array($d) ? $d : [];
        $d[$k] = time(); if (count($d) > 60) { asort($d); $d = array_slice($d, -60, null, true); }
        update_user_meta($uid, 'cc_dismiss', $d); return ['ok' => true];
    }]);
    register_rest_route('cc/v1', '/inbox-read', ['methods' => 'POST', 'permission_callback' => 'is_user_logged_in', 'callback' => function (WP_REST_Request $r) {
        $uid = get_current_user_id();
        // 20 Nov: {mark: [tags], has: [link pieces], prefix: bool} marks what was read elsewhere (a Today card, a food day…)
        if ($r->get_param('mark') !== null) {
            $tags = array_slice(array_map('sanitize_text_field', (array) $r->get_param('mark')), 0, 10); $has = array_slice(array_map('sanitize_text_field', (array) ($r->get_param('has') ?? [])), 0, 5);
            if ($tags) cc_inbox_mark($uid, $tags, $has, (bool) $r->get_param('prefix'));
            return ['ok' => true, 'unread' => cc_inbox_unread($uid)];
        }
        $in = get_user_meta($uid, 'cc_inbox', true); $in = is_array($in) ? $in : [];
        $at = (int) $r->get_param('at'); $tag = (string) $r->get_param('tag');
        foreach ($in as &$x) { if (!$at || ((int) $x['at'] === $at && (string) ($x['tag'] ?? '') === $tag)) $x['read'] = 1; } unset($x);
        update_user_meta($uid, 'cc_inbox', $in); return ['ok' => true, 'unread' => cc_inbox_unread($uid)];
    }]);
    register_rest_route('cc/v1', '/inbox', ['methods' => 'GET', 'permission_callback' => 'is_user_logged_in', 'callback' => function () {   // the bell, fresh
        $uid = get_current_user_id(); $GLOBALS['cc_ath_lang'] = function_exists('cc_ath_user_lang') ? cc_ath_user_lang($uid) : 'en';
        nocache_headers(); return ['unread' => cc_inbox_unread($uid), 'html' => cc_inbox_items($uid)];
    }]);
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
    register_rest_route('cc/v1', '/push-test', ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {   // Matteo: a test to his own phones, or to an athlete page's phones (page=)
        $uid = $r->get_param('page') ? (int) get_post_meta((int) $r->get_param('page'), 'cc_user', true) : get_current_user_id();
        return ['sent' => cc_push_user($uid, 'Cigala Cycling', 'Test: notifications work on this phone 🎉', home_url('/' . CC_ATH_SLUG . '/'), 'cc-test')];
    }]);
    register_rest_route('cc/v1', '/push-status', ['methods' => 'GET', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function () {
        $n = 0; $who = []; $hosts = [];
        foreach (get_users(['meta_key' => 'cc_push', 'fields' => ['ID', 'display_name']]) as $u) { $s = (array) get_user_meta($u->ID, 'cc_push', true); if ($s) { $n += count($s); $who[] = $u->display_name;
            foreach ($s as $x) $hosts[] = $u->display_name . ': ' . wp_parse_url((string) ($x['endpoint'] ?? ''), PHP_URL_HOST); } }   // which push service each phone uses (Apple, Google, Mozilla…), no keys
        return ['hosts' => $hosts, 'openssl' => function_exists('openssl_pkey_derive'), 'key' => (bool) cc_push_vapid(), 'phones' => $n, 'people' => $who, 'log' => array_slice((array) get_option('cc_push_log', []), 0, 5)];
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
