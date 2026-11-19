<?php
if (!defined('ABSPATH')) return;
/* "Ideas for your hub" (Matteo, 17 Nov 2026): a short box at the bottom of every athlete's hub, in their language, with the mic.
 * Each idea goes to Matteo only: a list on /athletes/?board=ideas (with a count on his coach tools) and one email per idea.
 * Never shown to other athletes, no automatic reply. Stored in the option cc_ideas (newest first, at most 500). */

function cc_idea_w($k) {
    static $W = [
        'title' => ['en' => 'Ideas for your hub', 'it' => 'Idee per il tuo hub', 'pt' => 'Ideias para o teu hub', 'sl' => 'Ideje za tvoj hub', 'sk' => 'Nápady pre tvoju zónu'],
        'lede' => ['en' => 'Is there a report, a feature or anything else you would like to see here? Tell me, I read every idea.',
                   'it' => 'C’è un report, una funzione o altro che vorresti vedere qui? Dimmelo, leggo ogni idea.',
                   'pt' => 'Há algum relatório, funcionalidade ou outra coisa que gostarias de ver aqui? Diz-me, leio todas as ideias.',
                   'sl' => 'Bi tukaj rad videl kakšno poročilo, funkcijo ali kaj drugega? Povej mi, preberem vsako idejo.', 'sk' => 'Chýba ti tu nejaký report, funkcia alebo niečo iné? Povedz mi, čítam každý nápad.'],
        'ph' => ['en' => 'Your idea…', 'it' => 'La tua idea…', 'pt' => 'A tua ideia…', 'sl' => 'Tvoja ideja…', 'sk' => 'Tvoj nápad…'],
        'send' => ['en' => 'Send my idea', 'it' => 'Invia la mia idea', 'pt' => 'Enviar a minha ideia', 'sl' => 'Pošlji mojo idejo', 'sk' => 'Poslať môj nápad'],
        'thanks' => ['en' => 'Thank you! Your idea reached me.', 'it' => 'Grazie! La tua idea mi è arrivata.', 'pt' => 'Obrigado! A tua ideia chegou até mim.', 'sl' => 'Hvala! Tvoja ideja je prišla do mene.', 'sk' => 'Ďakujem! Tvoj nápad ku mne dorazil.'],
    ];
    $l = $GLOBALS['cc_ath_lang'] ?? 'en';
    return $W[$k][$l] ?? $W[$k]['en'];
}
function cc_ideas() { $a = get_option('cc_ideas', []); return is_array($a) ? $a : []; }

// the box, last thing on the athlete's own hub (not on the coach's view of it)
add_filter('cc_ath_end', function ($html, $view, $coach) {
    if ($coach || !$view) return $html;
    $ok = isset($_GET['idea']);
    return $html . '<section class="ath-s cc-idea" id="cc-idea"><h2>' . cc_ath_icon('idea', 'ath-hic') . esc_html(cc_idea_w('title')) . '</h2>'
        . '<p class="av-lede">' . esc_html(cc_idea_w('lede')) . '</p>'
        . ($ok ? '<p class="cc-idea-ok" role="status">' . esc_html(cc_idea_w('thanks')) . '</p>' : '')
        . '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="cc_idea">' . wp_nonce_field('cc_idea', '_wpnonce', false, false)
        . '<textarea name="idea" rows="3" maxlength="2000" required placeholder="' . esc_attr(cc_idea_w('ph')) . '" aria-label="' . esc_attr(cc_idea_w('title')) . '"></textarea>'
        . '<button class="btn btn-go" type="submit">' . esc_html(cc_idea_w('send')) . '</button></form></section>'
        . '<style>html .cc .cc-idea form{display:grid;gap:12px;justify-items:stretch}html .cc .cc-idea form .btn{justify-self:start}html .cc .cc-idea .cc-micw{display:block;width:100%}html .cc .cc-idea textarea{width:100%;min-height:110px;font:16px var(--body);padding:12px 14px;border-radius:12px;border:1px solid rgba(255,255,255,.2);background:#0b0d0f;color:#fff;box-sizing:border-box}'
        . 'html .cc .cc-idea-ok{color:#34c46a;font-weight:600;font-size:16px;margin:0 0 12px}</style>';
}, 10, 3);

add_action('admin_post_cc_idea', function () {
    $uid = get_current_user_id(); $url = home_url('/' . CC_ATH_SLUG . '/');
    if (!$uid || !wp_verify_nonce($_POST['_wpnonce'] ?? '', 'cc_idea') || !($pid = cc_ath_page_of($uid))) { wp_safe_redirect($url); exit; }
    $txt = trim(sanitize_textarea_field(wp_unslash((string) ($_POST['idea'] ?? '')))); $txt = mb_substr($txt, 0, 2000);
    $all = cc_ideas(); $today = 0;
    foreach ($all as $i) if ((int) $i['uid'] === $uid && $i['at'] > time() - DAY_IN_SECONDS) $today++;
    if ($txt !== '' && $today < 5) {   // at most five a day per athlete
        $u = wp_get_current_user(); $name = trim($u->first_name . ' ' . $u->last_name) ?: $u->display_name;
        array_unshift($all, ['id' => wp_generate_password(10, false), 'at' => time(), 'uid' => $uid, 'page' => (int) $pid, 'name' => $name, 'lang' => cc_ath_lang_code($uid), 'text' => $txt, 'done' => 0]);
        update_option('cc_ideas', array_slice($all, 0, 500), false);
        $board = add_query_arg('board', 'ideas', $url);
        $h = '<div style="font-family:Montserrat,Helvetica,Arial,sans-serif;font-size:16px;color:#222"><p style="margin:0 0 10px"><b style="color:#111">' . esc_html($name) . '</b> has an idea for the hub:</p>'
           . '<blockquote style="margin:0 0 16px;padding:10px 14px;background:#f2f4f3;border-left:3px solid #009a44;white-space:pre-line">' . esc_html($txt) . '</blockquote>'
           . '<p style="margin:20px 0 0"><a href="' . esc_url($board) . '" style="display:inline-block;padding:12px 20px;border-radius:8px;background:#009a44;color:#fff;font-weight:600;text-decoration:none">Open all ideas</a></p></div>';
        $hd = ['Content-Type: text/html; charset=UTF-8']; if (is_email($u->user_email)) $hd[] = 'Reply-To: ' . $name . ' <' . $u->user_email . '>';
        if (function_exists('cc_ath_coach_wrap')) $h = cc_ath_coach_wrap($h);
        if (function_exists('cc_av_notify_to') && cc_av_notify_to()) wp_mail(cc_av_notify_to(), 'Hub idea: ' . $name, $h, $hd);
        if (function_exists('cc_push_coaches')) cc_push_coaches('Hub idea: ' . $name, wp_trim_words($txt, 18), $board, 'cc-idea', $pid);
    }
    wp_safe_redirect(add_query_arg('idea', 1, $url) . '#cc-idea'); exit;
});

// Matteo's board: /athletes/?board=ideas
add_filter('cc_ath_coach_links', function ($html) {
    $n = 0; foreach (cc_ideas() as $i) if (empty($i['done'])) $n++;
    return $html . '<a class="av-boardlink" href="' . esc_url(add_query_arg('board', 'ideas', home_url('/' . CC_ATH_SLUG . '/'))) . '">Hub ideas' . ($n ? ' <span class="av-badge">' . $n . ' new</span>' : '') . '</a>';
}, 40);
add_filter('cc_ath_board', function ($html, $board) {
    if ($board !== 'ideas' || !cc_ath_is_coach()) return $html;
    $o = '<section class="ath-s"><h2>Hub ideas</h2><p class="av-lede">What athletes would like to see in their hub, newest first. Only you see these. Each one also came to you by email.</p>';
    $all = cc_ideas();
    if (!$all) return $o . '<p class="av-lede">No ideas yet.</p></section>';
    $f = function ($id, $act, $label, $cls = 'btn-ghost') { return '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:inline"><input type="hidden" name="action" value="cc_idea_act"><input type="hidden" name="id" value="' . esc_attr($id) . '"><input type="hidden" name="act" value="' . $act . '">' . wp_nonce_field('cc_idea_act', '_wpnonce', false, false) . '<button class="btn ' . $cls . '" type="submit"' . ($act === 'delete' ? ' onclick="return confirm(\'Delete this idea?\')"' : '') . '>' . $label . '</button></form>'; };
    foreach ($all as $i) {
        $o .= '<div class="cc-idea-row' . (empty($i['done']) ? '' : ' is-done') . '"><div class="cc-idea-h"><b><a href="' . esc_url(add_query_arg('view', (int) $i['page'], home_url('/' . CC_ATH_SLUG . '/'))) . '">' . esc_html($i['name']) . '</a></b>'
            . (function_exists('cc_ath_flag_for') ? cc_ath_flag_for((int) $i['page']) : '') . ' <small>' . esc_html(date_i18n('j M Y, H:i', (int) $i['at'])) . (empty($i['done']) ? '' : ' · done') . '</small></div>'
            . '<p>' . nl2br(esc_html($i['text'])) . '</p><div class="cc-idea-a">' . (empty($i['done']) ? $f($i['id'], 'done', 'Mark as done', 'btn-go') : $f($i['id'], 'undo', 'Not done')) . $f($i['id'], 'delete', 'Delete') . '</div></div>';
    }
    return $o . '</section><style>html .cc .cc-idea-row{padding:14px 0;border-top:1px solid rgba(255,255,255,.1)}html .cc .cc-idea-row p{margin:8px 0 10px;font-size:16px;color:#e6e9ee}'
        . 'html .cc .cc-idea-row small{color:#b8bec8;font-size:15px}html .cc .cc-idea-row.is-done{opacity:.6}html .cc .cc-idea-a{display:flex;gap:10px;flex-wrap:wrap}html .cc .cc-idea-h a{color:#fff}</style>';
}, 10, 2);
add_action('admin_post_cc_idea_act', function () {
    if (!cc_ath_is_coach() || !wp_verify_nonce($_POST['_wpnonce'] ?? '', 'cc_idea_act')) wp_die('Not allowed');
    $id = sanitize_key($_POST['id'] ?? ''); $act = sanitize_key($_POST['act'] ?? ''); $all = cc_ideas();
    foreach ($all as $k => $i) {
        if (strtolower($i['id']) !== $id) continue;
        if ($act === 'delete') unset($all[$k]); elseif ($act === 'done') $all[$k]['done'] = time(); elseif ($act === 'undo') $all[$k]['done'] = 0;
    }
    update_option('cc_ideas', array_values($all), false);
    wp_safe_redirect(add_query_arg('board', 'ideas', home_url('/' . CC_ATH_SLUG . '/'))); exit;
});

/* ---------- "More from Cigala Cycling": bike tours and the shop (Matteo 19 Nov 2026) ----------
 * A quiet section near the end of every athlete's hub (TrainingPeaks riders too: nothing Vekta here), just before the ideas box. */
function cc_more_w($k) {
    static $W = [
        'h' => ['en' => 'More from Cigala Cycling', 'it' => 'Di più da Cigala Cycling', 'pt' => 'Mais da Cigala Cycling', 'sl' => 'Več od Cigala Cycling', 'sk' => 'Viac od Cigala Cycling'],
        'lede' => ['en' => 'Ride with me in person, and gear up for your season.', 'it' => 'Pedala con me dal vivo e preparati al meglio per la tua stagione.', 'pt' => 'Pedala comigo ao vivo e prepara-te para a tua época.', 'sl' => 'Kolesari z mano v živo in se opremi za svojo sezono.', 'sk' => 'Jazdi so mnou naživo a priprav sa na svoju sezónu.'],
        'tours' => ['en' => 'Bike tours', 'it' => 'Tour in bici', 'pt' => 'Tours de bicicleta', 'sl' => 'Kolesarske ture', 'sk' => 'Cyklistické túry'],
        'tours_s' => ['en' => 'Cycling holidays with me, from the Dolomites to the Alps', 'it' => 'Vacanze in bici con me, dalle Dolomiti alle Alpi', 'pt' => 'Férias de bicicleta comigo, das Dolomitas aos Alpes', 'sl' => 'Kolesarske počitnice z mano, od Dolomitov do Alp', 'sk' => 'Cyklistické dovolenky so mnou, od Dolomitov po Alpy'],
        'shop' => ['en' => 'Shop', 'it' => 'Negozio', 'pt' => 'Loja', 'sl' => 'Trgovina', 'sk' => 'Obchod'],
        'shop_s' => ['en' => 'Premium cycling brands and sports nutrition', 'it' => 'Marchi di ciclismo di qualità e nutrizione sportiva', 'pt' => 'Marcas de ciclismo premium e nutrição desportiva', 'sl' => 'Vrhunske kolesarske znamke in športna prehrana', 'sk' => 'Prémiové cyklistické značky a športová výživa'],
    ];
    $l = $GLOBALS['cc_ath_lang'] ?? 'en'; return $W[$k][$l] ?? $W[$k]['en'];
}
function cc_more_tile($href, $icon, $title, $sub) {
    return '<a class="ath-tile" href="' . esc_url($href) . '" target="_blank" rel="noopener">' . cc_ath_icon($icon)
         . '<span class="ath-tt"><b>' . esc_html($title) . '</b><small>' . esc_html($sub) . '</small></span><span class="ath-go" aria-hidden="true">→</span></a>';
}
add_filter('cc_ath_end', function ($html, $view, $coach) {
    if (!$view) return $html;
    return $html . '<section class="ath-s" id="more"><h2>' . cc_ath_icon('bike', 'ath-hic') . esc_html(cc_more_w('h')) . '</h2><div class="ath-body"><p>' . esc_html(cc_more_w('lede')) . '</p>'
        . '<div class="wp-block-buttons">' . cc_more_tile('https://tours.cigalacycling.com/', 'bike', cc_more_w('tours'), cc_more_w('tours_s'))
        . cc_more_tile('https://retail.cigalacycling.com/', 'bag', cc_more_w('shop'), cc_more_w('shop_s')) . '</div></div></section>';
}, 5, 3);
add_filter('cc_ath_nav', function ($nav, $view, $coach) { if ($view) $nav[] = ['more', cc_more_w('h')]; return $nav; }, 90, 3);
