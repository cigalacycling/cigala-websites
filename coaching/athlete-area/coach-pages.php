<?php
if (!defined('ABSPATH')) return;
/* ---------- Morning pages for the coach (Matteo, 20 Nov 2026) ----------
 * The Coach Command Centre and Early Warning pages are built on Matteo's laptop each morning (command-centre\morning.py,
 * early-warning\morning.py) and posted here by vekta\hub\post_coach_page.py, so he can read them on his phone without Claude.
 * They hold athlete names and physiology: COACH ONLY. Every request checks cc_ath_is_coach() (edit_pages); athletes and the
 * nutritionist never see the board, the link or the files.
 * - POST /wp-json/cc/v1/coach-page {key: command-centre|early-warning, html, date: YYYY-MM-DD}: stores one self-contained page
 *   (max 3 MB) in uploads/cc-private/coach-pages (closed to direct downloads); the same key and date replace it; last 14 kept per key.
 * - GET /wp-json/cc/v1/coach-page[?key=]: what is stored. GET /wp-json/cc/v1/coach-page/raw?key=&date=: the page itself
 *   (sandboxed, no caching, noindex, frame only from this site). The board shows it inside a sandboxed iframe.
 * - Board ?board=morning: tabs Command Centre / Early Warning, latest by default, earlier days from a list. */

function cc_cp_keys() { return ['command-centre' => 'Command Centre', 'early-warning' => 'Early Warning']; }
function cc_cp_max() { return 3 * 1024 * 1024; }
function cc_cp_keep() { return 14; }

function cc_cp_dir() {
    $u = wp_get_upload_dir(); $d = $u['basedir'] . '/cc-private/coach-pages';
    if (!file_exists($d . '/.htaccess')) {
        wp_mkdir_p($d);
        @file_put_contents($d . '/.htaccess', "Require all denied\n<IfModule !mod_authz_core.c>\nOrder allow,deny\nDeny from all\n</IfModule>\nOptions -Indexes\n");
        @file_put_contents($d . '/index.php', "<?php\n");
    }
    return $d;
}
function cc_cp_index() { $i = get_option('cc_cp_index', []); return is_array($i) ? $i : []; }
function cc_cp_list($key) {
    $i = cc_cp_index(); $l = (isset($i[$key]) && is_array($i[$key])) ? $i[$key] : [];
    krsort($l); return $l;
}
function cc_cp_latest($key) { $l = cc_cp_list($key); return $l ? (string) array_key_first($l) : ''; }
function cc_cp_html($key, $date) {
    $l = cc_cp_list($key);
    if (!isset($l[$date])) return null;
    $f = cc_cp_dir() . '/' . basename((string) $l[$date]['f']);
    return file_exists($f) ? file_get_contents($f) : null;
}
function cc_cp_raw_url($key, $date) {
    return add_query_arg(['key' => $key, 'date' => $date, '_wpnonce' => wp_create_nonce('wp_rest')], rest_url('cc/v1/coach-page/raw'));
}
function cc_cp_board_url($key = '', $date = '') {
    $a = ['board' => 'morning'];
    if ($key !== '') $a['pg'] = $key;
    if ($date !== '') $a['d'] = $date;
    return add_query_arg($a, home_url('/' . CC_ATH_SLUG . '/'));
}

/* the page itself: only for the coach, never cached, never indexed, framed only by this site, sandboxed (no access to the login) */
function cc_cp_serve($key, $date) {
    if ($date === '') $date = cc_cp_latest($key);
    $h = $date !== '' ? cc_cp_html($key, $date) : null;
    while (ob_get_level()) ob_end_clean();
    nocache_headers();
    do_action('litespeed_control_set_nocache', 'coach morning page');
    header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0, private');
    header('X-Robots-Tag: noindex, nofollow');
    header('X-Frame-Options: SAMEORIGIN');
    header('X-Content-Type-Options: nosniff');
    header('Referrer-Policy: same-origin');
    header("Content-Security-Policy: sandbox allow-scripts allow-popups allow-popups-to-escape-sandbox allow-modals allow-downloads; frame-ancestors 'self'");
    if ($h === null) { status_header(404); header('Content-Type: text/plain; charset=utf-8'); echo 'No page stored for that day.'; exit; }
    status_header(200);
    header('Content-Type: text/html; charset=utf-8');
    echo $h; exit;
}

add_action('rest_api_init', function () {
    $keyok = function ($v) { return is_string($v) && isset(cc_cp_keys()[$v]); };
    register_rest_route('cc/v1', '/coach-page', [
        ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
            $key = (string) $r['key']; $html = $r['html']; $date = (string) ($r['date'] ?? '');
            if (!isset(cc_cp_keys()[$key])) return new WP_Error('cc_cp_key', 'Unknown key.', ['status' => 400]);
            if (!is_string($html) || trim($html) === '') return new WP_Error('cc_cp_empty', 'No html.', ['status' => 400]);
            if (strlen($html) > cc_cp_max()) return new WP_Error('cc_cp_big', 'Page larger than 3 MB.', ['status' => 413]);
            if (!preg_match('/^\d{4}-\d{2}-\d{2}$/', $date)) $date = current_time('Y-m-d');
            $dir = cc_cp_dir(); $i = cc_cp_index(); $l = (isset($i[$key]) && is_array($i[$key])) ? $i[$key] : [];
            $name = $key . '-' . $date . '-' . wp_generate_password(16, false) . '.html';
            if (file_put_contents($dir . '/' . $name, $html) === false) return new WP_Error('cc_cp_write', 'Could not save.', ['status' => 500]);
            if (isset($l[$date]['f'])) @unlink($dir . '/' . basename((string) $l[$date]['f']));
            $l[$date] = ['f' => $name, 'size' => strlen($html), 'at' => time()];
            krsort($l);
            foreach (array_slice($l, cc_cp_keep(), null, true) as $d => $old) { @unlink($dir . '/' . basename((string) $old['f'])); unset($l[$d]); }
            $i[$key] = $l; update_option('cc_cp_index', $i, false);
            return ['ok' => true, 'key' => $key, 'date' => $date, 'size' => strlen($html), 'kept' => count($l), 'board' => cc_cp_board_url($key, $date)];
        }],
        ['methods' => 'GET', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
            $out = [];
            foreach (cc_cp_keys() as $k => $label) {
                if (!empty($r['key']) && $r['key'] !== $k) continue;
                $out[$k] = [];
                foreach (cc_cp_list($k) as $d => $e) $out[$k][] = ['date' => (string) $d, 'size' => (int) $e['size'], 'at' => gmdate('c', (int) $e['at'])];
            }
            return $out;
        }],
    ]);
    register_rest_route('cc/v1', '/coach-page/raw', ['methods' => 'GET', 'permission_callback' => 'cc_ath_is_coach', 'args' => ['key' => ['required' => true, 'validate_callback' => $keyok]],
        'callback' => function (WP_REST_Request $r) {
            $date = (string) ($r['date'] ?? '');
            if ($date !== '' && !preg_match('/^\d{4}-\d{2}-\d{2}$/', $date)) $date = '';
            cc_cp_serve((string) $r['key'], $date);
        }]);
});

/* the link in "Your coach tools" */
add_filter('cc_ath_coach_links', function ($html) {
    if (!cc_ath_is_coach()) return $html;
    return $html . '<a class="av-boardlink" href="' . esc_url(cc_cp_board_url()) . '">Morning pages</a>';
}, 4);

/* the board */
add_filter('cc_ath_board', function ($html, $board) {
    if ($board !== 'morning' || !cc_ath_is_coach()) return $html;
    $keys = cc_cp_keys();
    $key = isset($_GET['pg']) ? sanitize_key($_GET['pg']) : '';
    if (!isset($keys[$key])) $key = 'command-centre';
    $list = cc_cp_list($key);
    $date = isset($_GET['d']) ? sanitize_text_field(wp_unslash($_GET['d'])) : '';
    if (!isset($list[$date])) $date = $list ? (string) array_key_first($list) : '';
    $o = '<section class="ath-s cp-wrap"><h2>Morning pages</h2>'
        . '<p class="av-lede">Built on your laptop each morning from Vekta and put here for your phone. Only you can see them.</p><div class="cp-tabs" role="tablist">';
    foreach ($keys as $k => $label) {
        $o .= '<a role="tab" class="cp-tab' . ($k === $key ? ' on' : '') . '" href="' . esc_url(cc_cp_board_url($k)) . '"' . ($k === $key ? ' aria-selected="true"' : '') . '>' . esc_html($label) . '</a>';
    }
    $o .= '</div>';
    if ($date === '') {
        $o .= '<p class="vx-none">Nothing here yet: the first page arrives after the next morning run on your laptop.</p>';
    } else {
        $e = $list[$date]; $t = strtotime($date);
        $o .= '<div class="cp-bar"><span class="cp-when">' . esc_html(date_i18n('l j F Y', $t)) . ' · put here ' . esc_html(date_i18n('H:i', (int) $e['at'] + (int) (get_option('gmt_offset') * HOUR_IN_SECONDS))) . '</span>'
            . '<label class="cp-pick">Earlier days <select onchange="if(this.value)location.href=this.value">';
        foreach ($list as $d => $x) $o .= '<option value="' . esc_url(cc_cp_board_url($key, (string) $d)) . '"' . ((string) $d === $date ? ' selected' : '') . '>' . esc_html(date_i18n('D j M', strtotime((string) $d))) . '</option>';
        $raw = cc_cp_raw_url($key, $date);
        $o .= '</select></label><a class="cp-full" href="' . esc_url($raw) . '" target="_blank" rel="noopener">Open full screen</a></div>'
            . '<div class="cp-frame"><iframe src="' . esc_url($raw) . '" title="' . esc_attr($keys[$key]) . '" sandbox="allow-scripts allow-popups allow-popups-to-escape-sandbox allow-modals allow-downloads" allow="clipboard-write" referrerpolicy="same-origin"></iframe></div>';
    }
    $o .= '</section><style>'
        . 'html .cc .cp-tabs{display:flex;gap:8px;flex-wrap:wrap;margin:14px 0 10px}'
        . 'html .cc .cp-tab{padding:9px 16px;border-radius:999px;border:1px solid rgba(255,255,255,.18);color:#d7dbe2;text-decoration:none;font-weight:600;font-size:15px}'
        . 'html .cc .cp-tab.on{background:rgba(18,161,80,.18);border-color:rgba(43,212,122,.55);color:#fff}'
        . 'html .cc .cp-bar{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:center;margin:0 0 10px;font-size:15px;color:#b8bec8}'
        . 'html .cc .cp-pick{display:flex;gap:8px;align-items:center;margin:0}'
        . 'html .cc .cp-pick select{font-size:16px;padding:6px 8px;border-radius:8px;background:#111317;color:#e6e8ec;border:1px solid rgba(255,255,255,.2)}'
        . 'html .cc .cp-full{color:#2bd47a;font-weight:600}'
        . 'html .cc .cp-frame{border:1px solid rgba(255,255,255,.12);border-radius:12px;overflow:hidden;background:#08090a}'
        . 'html .cc .cp-frame iframe{display:block;width:100%;height:calc(100vh - 120px);min-height:560px;border:0;background:#08090a}'
        . '</style>';
    return $o;
}, 10, 2);
