<?php
/* Passwords without Matteo (16 Nov 2026): "Forgot your password?" on the login page emails a reset link, and "Change password"
 * inside the hub. The reset link opens the same "choose your password" page as the welcome email (athlete-area.php, ?cc_set=).
 * English or Italian, like the rest of the hub interface. Pushed with --availability.
 */
if (!defined('ABSPATH')) return;

function cc_pw_t($en, $it) { return cc_L($en, $it); }
add_filter('cc_ath_forgot_link', function () {
    return '<p class="ath-help"><a href="' . esc_url(add_query_arg('cc_forgot', 1, home_url('/' . CC_ATH_SLUG . '/'))) . '">' . esc_html(cc_pw_t('Forgot your password?', 'Password dimenticata?')) . '</a> '
         . esc_html(cc_pw_t('Get a link to choose a new one by email.', 'Ricevi via email un link per sceglierne una nuova.')) . '</p>';
});
add_filter('cc_ath_forgot_page', function () {
    $sent = isset($_GET['sent']);
    $o = '<div class="ath-login"><p class="eyebrow">' . cc_t('Coached athletes') . '</p><h1>' . esc_html(cc_pw_t('New password', 'Nuova password')) . '</h1>';
    if ($sent) return $o . '<p class="ath-lede">' . esc_html(cc_pw_t('If that email has an athlete login, a link to choose a new password is on its way. Check your inbox (and spam) in a few minutes. The link works for 7 days.',
        'Se quell’email ha un accesso atleta, ti sta arrivando un link per scegliere una nuova password. Controlla la posta (anche lo spam) tra qualche minuto. Il link vale 7 giorni.')) . '</p>'
        . '<p><a class="btn btn-go" href="' . esc_url(home_url('/' . CC_ATH_SLUG . '/')) . '">' . cc_t('Log in') . '</a></p></div>';
    return $o . '<p class="ath-lede">' . esc_html(cc_pw_t('Type the email you log in with and I will send you a link to choose a new password.', 'Scrivi l’email con cui accedi e ti mando un link per scegliere una nuova password.')) . '</p>'
        . '<form method="post"><input type="hidden" name="cc_forgot_go" value="1">' . wp_nonce_field('cc_forgot', '_ccn', false, false)
        . '<label for="ath-fe">' . esc_html(cc_pw_t('Email', 'Email')) . '</label><input id="ath-fe" name="cc_email" type="text" inputmode="email" autocomplete="email" autocapitalize="none" required>'
        . '<button type="submit" class="btn btn-go">' . esc_html(cc_pw_t('Send me the link', 'Mandami il link')) . '</button></form>'
        . '<p class="ath-help"><a href="' . esc_url(home_url('/' . CC_ATH_SLUG . '/')) . '">' . esc_html(cc_pw_t('Back to log in', 'Torna all’accesso')) . '</a></p></div>';
});
add_action('template_redirect', function () {
    if (!is_page(CC_ATH_SLUG) || empty($_POST['cc_forgot_go'])) return;
    $back = add_query_arg(['cc_forgot' => 1, 'sent' => 1], home_url('/' . CC_ATH_SLUG . '/'));
    if (!wp_verify_nonce($_POST['_ccn'] ?? '', 'cc_forgot')) { wp_safe_redirect($back); exit; }
    $em = sanitize_email(wp_unslash($_POST['cc_email'] ?? ''));
    $u = $em ? get_user_by('email', $em) : null;
    // only athlete logins, at most one email every 2 minutes; the answer is the same either way (nobody can test which emails exist)
    if ($u && !user_can($u, 'edit_posts') && cc_ath_page_of($u->ID) && !get_transient('cc_forgot_' . $u->ID)) {
        set_transient('cc_forgot_' . $u->ID, 1, 2 * MINUTE_IN_SECONDS);
        cc_pw_mail($u);
    }
    wp_safe_redirect($back); exit;
}, 3);
function cc_pw_mail($u) {
    $key = get_password_reset_key($u); if (is_wp_error($key)) return;
    $link = add_query_arg(['cc_set' => $key, 'u' => rawurlencode($u->user_login)], home_url('/' . CC_ATH_SLUG . '/'));
    $GLOBALS['cc_ath_lang'] = cc_ath_user_lang($u->ID); $it = $GLOBALS['cc_ath_lang'] === 'it'; $first = esc_html($u->first_name ?: $u->display_name);
    $h = cc_ath_mail_shell(sprintf(cc_L('Hi %s,', 'Ciao %s,'), $first),
        cc_L('Here is your link to choose a new password for your athlete hub. It works once and lasts 7 days.', 'ecco il link per scegliere una nuova password per la tua area atleta. Vale 7 giorni e si usa una volta sola.'),
        cc_L('Choose a new password', 'Scegli una nuova password'), $link,
        cc_ath_mail_small(cc_L('Didn’t ask for this? Just ignore this email: your password stays the same.', 'Non l’hai chiesto tu? Ignora questa email: la tua password non cambia.')));
    wp_mail($u->user_email, cc_L('Your new Cigala Coaching password', 'La tua nuova password Cigala Coaching'), $h,
        ['Content-Type: text/html; charset=UTF-8', 'From: Matteo Cigala <coaching@cigalacycling.com>', 'Reply-To: Matteo Cigala <matteo@cigalacycling.com>']);
}

/* ---------- change password, inside the hub ---------- */
add_filter('cc_ath_hero_links', function ($html, $coach) {
    if ($coach) return $html;
    return $html . ' <a class="ath-out" href="' . esc_url(add_query_arg('cc_pw', 'change', home_url('/' . CC_ATH_SLUG . '/'))) . '#pw">' . esc_html(cc_pw_t('Change password', 'Cambia password')) . '</a>';
}, 10, 2);
add_filter('cc_ath_after_reports', function ($html, $view, $coach) {
    if ($coach || !isset($_GET['cc_pw'])) return $html;
    $err = ['wrong' => cc_pw_t('Your current password is not right.', 'La password attuale non è corretta.'), 'short' => cc_pw_t('Use at least 8 characters.', 'Usa almeno 8 caratteri.'),
            'match' => cc_pw_t('The two new passwords are not the same.', 'Le due nuove password non coincidono.')][$_GET['err'] ?? ''] ?? '';
    $o = '<section class="ath-s" id="pw"><h2>' . cc_ath_icon('gear', 'ath-hic') . esc_html(cc_pw_t('Change password', 'Cambia password')) . '</h2>';
    if ($_GET['cc_pw'] === 'ok') return $o . '<p class="av-msg">' . esc_html(cc_pw_t('Done: your new password is saved.', 'Fatto: la nuova password è salvata.')) . '</p></section>' . $html;
    return $o . ($err ? '<p class="ath-err" role="alert">' . esc_html($err) . '</p>' : '')
        . '<form method="post" class="pw-form"><input type="hidden" name="cc_pw_go" value="1">' . wp_nonce_field('cc_pw_change', '_ccn', false, false)
        . '<input type="text" name="log" value="' . esc_attr(wp_get_current_user()->user_email) . '" autocomplete="username" hidden>'
        . '<label for="pw0">' . esc_html(cc_pw_t('Current password', 'Password attuale')) . '</label><input id="pw0" name="pw0" type="password" autocomplete="current-password" required>'
        . '<label for="pw1">' . esc_html(cc_pw_t('New password (at least 8 characters)', 'Nuova password (almeno 8 caratteri)')) . '</label><input id="pw1" name="pw1" type="password" autocomplete="new-password" minlength="8" required>'
        . '<label for="pw2">' . esc_html(cc_pw_t('Repeat the new password', 'Ripeti la nuova password')) . '</label><input id="pw2" name="pw2" type="password" autocomplete="new-password" minlength="8" required>'
        . '<button type="submit" class="btn btn-go">' . esc_html(cc_pw_t('Save the new password', 'Salva la nuova password')) . '</button></form></section>' . $html;
}, 1, 3);
add_action('template_redirect', function () {
    if (!is_page(CC_ATH_SLUG) || empty($_POST['cc_pw_go']) || !is_user_logged_in()) return;
    $u = wp_get_current_user(); $base = add_query_arg('cc_pw', 'change', home_url('/' . CC_ATH_SLUG . '/'));
    $go = function ($q) use ($base) { wp_safe_redirect(add_query_arg($q, $base) . '#pw'); exit; };
    if (!wp_verify_nonce($_POST['_ccn'] ?? '', 'cc_pw_change') || user_can($u, 'edit_posts')) $go(['err' => 'wrong']);
    $p0 = (string) wp_unslash($_POST['pw0'] ?? ''); $p1 = (string) wp_unslash($_POST['pw1'] ?? ''); $p2 = (string) wp_unslash($_POST['pw2'] ?? '');
    if (!wp_check_password($p0, $u->user_pass, $u->ID)) $go(['err' => 'wrong']);
    if (strlen($p1) < 8) $go(['err' => 'short']);
    if ($p1 !== $p2) $go(['err' => 'match']);
    wp_set_password($p1, $u->ID); wp_set_current_user($u->ID); wp_set_auth_cookie($u->ID, true);   // stay logged in on this phone
    update_user_meta($u->ID, 'cc_pw_set', current_time('mysql'));
    wp_safe_redirect(add_query_arg('cc_pw', 'ok', home_url('/' . CC_ATH_SLUG . '/')) . '#pw'); exit;
}, 3);
add_action('wp_head', function () {
    if (!is_page(CC_ATH_SLUG)) return;
    echo "<style id=\"cc-pw\">html .cc .pw-form{display:grid;gap:8px;max-width:420px}html .cc .pw-form label{font-size:13px;font-weight:600;color:var(--text);margin-top:6px}"
       . "html .cc .pw-form input[type=password]{width:100%;box-sizing:border-box;font-size:16px;padding:13px 14px;border-radius:10px;border:1px solid rgba(255,255,255,.18);background:#0b0d0f;color:#fff}"
       . "html .cc .pw-form .btn{margin-top:8px;justify-self:start}html .cc .ath-hero-txt .ath-out+.ath-out{margin-left:14px}</style>\n";
});
