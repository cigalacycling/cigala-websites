<?php
if (!defined('ABSPATH')) return;
/* Profile photos (Matteo, 17 Nov 2026). Optional. The athlete adds it from the hub header (round photo, or their initials with
 * a camera badge until they do) or from the rider form's first step. The phone crops it to a square and shrinks it to 600 px
 * before upload. Stored like their other private files (uploads/cc-private, attached to their page, served only to them and
 * Matteo after the login check). Shown small next to their name on Matteo's athlete list, Notes board and Contracts.
 * Deleted when coaching ends. Page meta cc_photo = attachment id. */

function cc_ph_w($k) {
    static $W = [
        'add' => ['en' => 'Add your photo', 'it' => 'Aggiungi la tua foto', 'pt' => 'Adicionar a tua foto', 'sl' => 'Dodaj svojo fotografijo'],
        'change' => ['en' => 'Change your photo', 'it' => 'Cambia la tua foto', 'pt' => 'Mudar a tua foto', 'sl' => 'Zamenjaj fotografijo'],
        'form' => ['en' => 'A photo of you (optional)', 'it' => 'Una tua foto (facoltativa)', 'pt' => 'Uma foto tua (opcional)', 'sl' => 'Tvoja fotografija (neobvezno)'],
        'form_hint' => ['en' => 'It shows in your hub, and helps me put a face to your name.', 'it' => 'Compare nella tua area e mi aiuta ad associare un volto al tuo nome.', 'pt' => 'Aparece na tua área e ajuda-me a associar um rosto ao teu nome.', 'sl' => 'Prikaže se v tvojem središču in mi pomaga, da imenu dodam obraz.'],
        'up' => ['en' => 'Uploading…', 'it' => 'Caricamento…', 'pt' => 'A carregar…', 'sl' => 'Nalagam…'],
        'ok' => ['en' => 'Photo saved', 'it' => 'Foto salvata', 'pt' => 'Foto guardada', 'sl' => 'Fotografija shranjena'],
        'remove' => ['en' => 'Remove photo', 'it' => 'Rimuovi la foto', 'pt' => 'Remover a foto', 'sl' => 'Odstrani fotografijo'],
        'removed' => ['en' => 'Photo removed', 'it' => 'Foto rimossa', 'pt' => 'Foto removida', 'sl' => 'Fotografija odstranjena'],
        'bad' => ['en' => 'That photo did not upload. Please try another one.', 'it' => 'La foto non è stata caricata. Prova con un’altra.', 'pt' => 'A foto não foi carregada. Tenta outra.', 'sl' => 'Fotografija se ni naložila. Poskusi z drugo.'],
    ];
    $l = $GLOBALS['cc_ath_lang'] ?? 'en';
    return $W[$k][$l] ?? $W[$k]['en'];
}
function cc_ph_url($pid) { $id = (int) get_post_meta((int) $pid, 'cc_photo', true); return $id && get_post($id) ? wp_get_attachment_url($id) : ''; }
function cc_ph_initials($pid) {
    $parts = preg_split('/\s+/', trim(wp_strip_all_tags(get_the_title((int) $pid)))) ?: [];
    $i = ''; foreach ([reset($parts), count($parts) > 1 ? end($parts) : ''] as $p) if ($p !== '' && $p !== false) $i .= mb_strtoupper(mb_substr($p, 0, 1));
    return $i ?: '?';
}
// small round face for Matteo's lists (nothing when there is no photo)
function cc_ph_face($pid, $size = 24) {
    $u = cc_ph_url($pid); if (!$u) return '';
    return '<img class="cc-face" src="' . esc_url($u) . '" width="' . (int) $size . '" height="' . (int) $size . '" alt="" loading="lazy" style="width:' . (int) $size . 'px;height:' . (int) $size . 'px">';
}
// the tap-to-add / tap-to-change round photo (header and rider form); $edit: the viewer may change it
function cc_ph_widget($pid, $size, $edit, $cls = '') {
    $u = cc_ph_url($pid);
    $face = $u ? '<img src="' . esc_url($u) . '" alt="">' : '<span class="ph-ini">' . esc_html(cc_ph_initials($pid)) . '</span>';
    if (!$edit) return '<span class="ph-av ph-av-p' . (int) $pid . ' ' . esc_attr($cls) . '" style="--ph:' . (int) $size . 'px">' . $face . '</span>';
    $W = ['up' => cc_ph_w('up'), 'ok' => cc_ph_w('ok'), 'bad' => cc_ph_w('bad'), 'removed' => cc_ph_w('removed'), 'ini' => cc_ph_initials($pid)];
    return '<span class="ph-wrap ' . esc_attr($cls) . '"><button type="button" class="ph-av ph-edit" style="--ph:' . (int) $size . 'px" aria-label="' . esc_attr(cc_ph_w($u ? 'change' : 'add')) . '" title="' . esc_attr(cc_ph_w($u ? 'change' : 'add')) . '"'
         . ' data-api="' . esc_url(rest_url('cc/v1/photo')) . '" data-nonce="' . esc_attr(wp_create_nonce('wp_rest')) . '" data-page="' . (int) $pid . '" data-w="' . esc_attr(wp_json_encode($W)) . '">'
         . $face . '<span class="ph-cam" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M4 8h3l2-2.5h6L17 8h3v11H4z"/><circle cx="12" cy="13" r="3.5"/></svg></span></button>'
         . '<input type="file" accept="image/*" class="ph-file" hidden><button type="button" class="ph-rm"' . ($u ? '' : ' hidden') . '>' . esc_html(cc_ph_w('remove')) . '</button><span class="ph-msg" role="status"></span></span>';
}
function cc_ph_assets() {
    static $done = false; if ($done) return ''; $done = true;
    return '<style>html .cc .ph-av{position:relative;flex:none;width:var(--ph);height:var(--ph);border-radius:50%;display:grid;place-items:center;overflow:visible;padding:0;margin:0;min-height:0;'
        . 'background:linear-gradient(135deg,#12a150,#0b6b37);border:2px solid #2bd47a;box-shadow:0 6px 18px rgba(0,0,0,.45);color:#fff}'
        . 'html .cc .ph-av img{width:100%;height:100%;border-radius:50%;object-fit:cover;display:block}html .cc .ph-ini{font:400 calc(var(--ph)*.38)/1 var(--head,Anton,sans-serif);letter-spacing:.02em}'
        . 'html .cc .ph-edit{cursor:pointer;transition:transform .15s ease}html .cc .ph-edit:hover{transform:scale(1.04)}'
        . 'html .cc .ph-cam{position:absolute;right:-2px;bottom:-2px;width:calc(var(--ph)*.36);height:calc(var(--ph)*.36);min-width:22px;min-height:22px;border-radius:50%;background:#0b0d0f;border:2px solid #2bd47a;display:grid;place-items:center}'
        . 'html .cc .ph-cam svg{width:62%;height:62%;fill:none;stroke:#fff;stroke-width:2}html .cc .ph-wrap{display:inline-flex;flex-direction:column;align-items:center;gap:6px}html .cc .ph-msg{font-size:14px;color:#d0d6e0;min-height:0}html .cc .ph-msg:empty{display:none}'
        . 'html .cc .ph-rm{background:none;border:0;padding:0;margin:0;min-height:0;font:600 13px var(--body);color:#b8bec8;text-decoration:underline;cursor:pointer}html .cc .ph-rm[hidden]{display:none}'
        . 'html .cc .cc-face{border-radius:50%;object-fit:cover;vertical-align:middle;border:1.5px solid rgba(43,212,122,.6);flex:none}'
        . 'html .cc .ath-hero-txt .ath-hello{display:flex;align-items:center;gap:16px}html .cc .ath-hero-txt .ath-hello h1{margin:8px 0 12px}'
        . 'html .cc .rf-photo{display:flex;align-items:center;gap:16px;padding:12px 14px;border-radius:12px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.03)}'
        . 'html .cc .rf-photo-t{margin:0;font-weight:600;font-size:16px;color:#fff}html .cc .rf-photo-h{margin:4px 0 0;font-size:15px;color:#b8bec8}'
        . '@media (max-width:760px){html .cc .ath-hero-txt .ath-hello{gap:12px}}</style>'
        . <<<'JS'
<script>(function(){document.querySelectorAll('.ph-edit').forEach(function(b){var w=b.parentNode,f=w.querySelector('.ph-file'),m=w.querySelector('.ph-msg'),W=JSON.parse(b.dataset.w);
b.addEventListener('click',function(){f.click();});
f.addEventListener('change',function(){var file=f.files&&f.files[0];if(!file)return;m.textContent=W.up;
 var img=new Image(),url=URL.createObjectURL(file);img.onload=function(){var s=Math.min(img.naturalWidth,img.naturalHeight),c=document.createElement('canvas'),n=Math.min(600,s);c.width=c.height=n;
  c.getContext('2d').drawImage(img,(img.naturalWidth-s)/2,(img.naturalHeight-s)/2,s,s,0,0,n,n);URL.revokeObjectURL(url);var data=c.toDataURL('image/jpeg',.86);
  var fd=new FormData();fd.append('img',data);fd.append('page',b.dataset.page);
  fetch(b.dataset.api,{method:'POST',body:fd,credentials:'same-origin',headers:{'X-WP-Nonce':b.dataset.nonce}}).then(function(r){return r.json().then(function(j){return[r.ok,j];});})
  .then(function(x){if(!x[0])throw 0;document.querySelectorAll('.ph-av[data-page="'+b.dataset.page+'"], .ph-av-p'+b.dataset.page).forEach(function(a){var i=a.querySelector('img'),t=a.querySelector('.ph-ini');if(!i){i=document.createElement('img');i.alt='';a.insertBefore(i,a.firstChild);}if(t)t.remove();i.src=data;});var rm=w.querySelector('.ph-rm');if(rm)rm.hidden=false;m.textContent=W.ok;setTimeout(function(){m.textContent='';},2500);})
  .catch(function(){m.textContent=W.bad;});};
 img.onerror=function(){m.textContent=W.bad;};img.src=url;f.value='';});
var rm=w.querySelector('.ph-rm');if(rm)rm.addEventListener('click',function(){var fd=new FormData();fd.append('remove','1');fd.append('page',b.dataset.page);
 fetch(b.dataset.api,{method:'POST',body:fd,credentials:'same-origin',headers:{'X-WP-Nonce':b.dataset.nonce}}).then(function(r){if(!r.ok)throw 0;
  document.querySelectorAll('.ph-av[data-page="'+b.dataset.page+'"], .ph-av-p'+b.dataset.page).forEach(function(a){var i=a.querySelector('img');if(i)i.remove();if(!a.querySelector('.ph-ini')){var s=document.createElement('span');s.className='ph-ini';s.textContent=W.ini;a.insertBefore(s,a.firstChild);}});
  rm.hidden=true;m.textContent=W.removed;setTimeout(function(){m.textContent='';},2500);}).catch(function(){m.textContent=W.bad;});});});})();</script>
JS;
}

/* ---------- saving: POST /wp-json/cc/v1/photo {img: JPEG data URL, page} (the athlete for themself, or Matteo) ---------- */
add_action('rest_api_init', function () {
    register_rest_route('cc/v1', '/photo', ['methods' => 'POST', 'permission_callback' => 'is_user_logged_in', 'callback' => function (WP_REST_Request $r) {
        $pid = (int) $r->get_param('page'); $me = get_current_user_id();
        if (!cc_ath_is_coach() && $pid !== cc_ath_page_of($me)) return new WP_Error('cc_no', 'Not your page', ['status' => 403]);
        if (get_post_type($pid) !== 'cc_athlete') return new WP_Error('cc_no', 'No such athlete', ['status' => 404]);
        if ($r->get_param('remove')) {   // Matteo 17 Nov: remove the photo (back to the initials)
            $old = (int) get_post_meta($pid, 'cc_photo', true); if ($old) wp_delete_attachment($old, true); delete_post_meta($pid, 'cc_photo'); return ['ok' => true, 'removed' => true];
        }
        if (!preg_match('#^data:image/jpeg;base64,([A-Za-z0-9+/=]+)$#', (string) $r->get_param('img'), $m)) return new WP_Error('cc_bad', 'Not a JPEG', ['status' => 400]);
        $bytes = base64_decode($m[1], true); $sz = $bytes ? @getimagesizefromstring($bytes) : false;
        if (!$bytes || strlen($bytes) > 600000 || !$sz || $sz[2] !== IMAGETYPE_JPEG || $sz[0] > 1200 || $sz[1] > 1200) return new WP_Error('cc_bad', 'Photo not accepted', ['status' => 400]);
        $old = (int) get_post_meta($pid, 'cc_photo', true);
        $id = cc_f_store($pid, $bytes, 'photo', 'jpg', 'image/jpeg', 'Profile photo');
        if (!$id) return new WP_Error('cc_fail', 'Could not save', ['status' => 500]);
        update_post_meta($pid, 'cc_photo', (int) $id); if ($old && $old !== (int) $id) wp_delete_attachment($old, true);
        return ['ok' => true, 'url' => wp_get_attachment_url($id)];
    }]);
});
// Matteo 17 Nov: logged in, the person icon in the site header (next to Book Consultation) becomes their round photo; Matteo's for him
add_action('wp_footer', function () {
    if (!is_user_logged_in()) return;
    $u = cc_ath_is_coach() ? 'https://coaching.cigalacycling.com/wp-content/uploads/2026/11/cigala-email-matteo-photo.jpg' : cc_ph_url(cc_ath_page_of(get_current_user_id()));
    if (!$u) return;
    echo '<style>a.nav-login.has-me{padding:0!important;width:36px;height:36px;border-radius:50%;overflow:hidden;border:2px solid #2bd47a;display:inline-flex!important;box-shadow:0 2px 10px rgba(0,0,0,.4)}a.nav-login.has-me img{width:100%;height:100%;object-fit:cover;display:block}</style>'
       . '<script>document.querySelectorAll("a.nav-login").forEach(function(a){a.classList.add("has-me");a.innerHTML=\'<img src="' . esc_url($u) . '" alt="">\';a.setAttribute("aria-label","My athlete hub");});</script>';
}, 50);
// coaching ended (login removed): the photo goes too
add_action('delete_user', function ($uid) {
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'meta_key' => 'cc_user', 'meta_value' => (int) $uid, 'numberposts' => -1, 'fields' => 'ids']) as $pid) {
        $old = (int) get_post_meta($pid, 'cc_photo', true); if ($old) wp_delete_attachment($old, true); delete_post_meta($pid, 'cc_photo');
    }
}, 6);
