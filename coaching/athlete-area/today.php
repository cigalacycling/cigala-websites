<?php
if (!defined('ABSPATH')) return;
/* "Today" card (round 2, 19 Nov 2026): at the top of the athlete's home, under the welcome header and above the jump links.
 * Shows only what the hub already has (it never calls Vekta):
 *  - today's planned session(s) and anything already done today: from the Vekta summary the laptop syncs for the food diary
 *    (cc_food_vx, POST /cc/v1/food-vekta from vekta\hub\vekta_inbox.py). That sync covers food-package athletes only, so other
 *    athletes have no planned sessions in the hub yet. Never for TrainingPeaks athletes (no Vekta content for them).
 *  - Marine's plan for today (food package on): her day note and the number of meals she planned (mealplan.php).
 *  - "Log today's food" (food package on).
 *  - the newest unread message from Matteo (last 14 days) from the athlete's notification centre (push.php).
 * Each line is left out when it has nothing; the whole card is left out when it is empty. */

function cc_td_w($k) {
    static $W = [
        'title' => ['en' => 'Today', 'it' => 'Oggi', 'pt' => 'Hoje', 'sl' => 'Danes', 'sk' => 'Dnes'],
        'session' => ['en' => 'Today’s session', 'it' => 'L’allenamento di oggi', 'pt' => 'O treino de hoje', 'sl' => 'Današnji trening', 'sk' => 'Dnešný tréning'],
        'sessions' => ['en' => 'Today’s sessions', 'it' => 'Gli allenamenti di oggi', 'pt' => 'Os treinos de hoje', 'sl' => 'Današnji treningi', 'sk' => 'Dnešné tréningy'],
        'done' => ['en' => 'Done', 'it' => 'Fatto', 'pt' => 'Feito', 'sl' => 'Opravljeno', 'sk' => 'Hotovo'],
        'carbs' => ['en' => '%d g/h carbs', 'it' => '%d g/h di carboidrati', 'pt' => '%d g/h de hidratos', 'sl' => '%d g/h ogljikovih hidratov', 'sk' => '%d g/h sacharidov'],
        'marine' => ['en' => 'Marine’s plan for today', 'it' => 'Il piano di Marine per oggi', 'pt' => 'O plano da Marine para hoje', 'sl' => 'Marinin načrt za danes', 'sk' => 'Plán od Marine na dnes'],
        'meals' => ['en' => 'Meals planned: %d', 'it' => 'Pasti in programma: %d', 'pt' => 'Refeições planeadas: %d', 'sl' => 'Načrtovani obroki: %d', 'sk' => 'Naplánované jedlá: %d'],
        'see' => ['en' => 'See it in your diary', 'it' => 'Vedilo nel diario', 'pt' => 'Ver no diário', 'sl' => 'Poglej v dnevniku', 'sk' => 'Pozri v denníku'],
        'msg' => ['en' => 'New message from Matteo', 'it' => 'Nuovo messaggio da Matteo', 'pt' => 'Nova mensagem do Matteo', 'sl' => 'Novo sporočilo od Mattea', 'sk' => 'Nová správa od Mattea'],
        'read' => ['en' => 'Read it', 'it' => 'Leggi', 'pt' => 'Ler', 'sl' => 'Preberi', 'sk' => 'Prečítať'],
    ];
    $l = $GLOBALS['cc_ath_lang'] ?? 'en'; return $W[$k][$l] ?? $W[$k]['en'];
}
function cc_td_hm($min) { $min = (int) $min; if ($min <= 0) return ''; $h = intdiv($min, 60); $m = $min % 60; return $h ? $h . 'h' . ($m ? sprintf('%02d', $m) : '') : $m . ' min'; }

function cc_td_card($view) {
    if (!$view || cc_ath_is_coach() || get_post_meta($view, 'cc_shared', true)) return '';
    $today = current_time('Y-m-d'); $tp = function_exists('cc_ath_tp') && cc_ath_tp($view);
    $food = function_exists('cc_fd_on') && cc_fd_on($view); $hub = home_url('/' . CC_ATH_SLUG . '/');
    $rows = '';
    // 1. today's sessions (Vekta, synced by the laptop; food-package athletes only for now)
    if (!$tp && function_exists('cc_fd_vx')) {
        $vx = cc_fd_vx($view);
        if (!empty($vx['at']) && (time() - (int) $vx['at']) < 3 * DAY_IN_SECONDS) {
            $li = ''; $n = 0;
            foreach ((array) ($vx['done'] ?? []) as $a) if (($a['d'] ?? '') === $today) { $n++;
                $li .= '<li><span class="td-ok" aria-hidden="true">✓</span> <b>' . esc_html(cc_td_w('done')) . ':</b> ' . esc_html(trim(($a['n'] ?? '') . ' · ' . cc_td_hm($a['min'] ?? 0), ' ·')) . '</li>'; }
            if (!$n) foreach ((array) ($vx['plan'] ?? []) as $p) if (($p['d'] ?? '') === $today) { $n++;
                $bits = array_filter([(string) ($p['n'] ?? ''), cc_td_hm($p['min'] ?? 0), !empty($p['carb']) ? sprintf(cc_td_w('carbs'), (int) $p['carb']) : '']);
                $li .= '<li>' . esc_html(implode(' · ', $bits)) . '</li>'; }
            if ($li !== '') $rows .= '<div class="td-row">' . cc_ath_icon('bike', 'td-ic') . '<div class="td-tx"><h3>' . esc_html(cc_td_w($n > 1 ? 'sessions' : 'session')) . '</h3><ul>' . $li . '</ul></div></div>';
        }
    }
    // 2. Marine's plan for today
    if ($food && function_exists('cc_mp_get')) {
        $pl = cc_mp_get($view, $today); $txt = trim((string) $pl['n']); $nm = count((array) $pl['i']);
        if ($txt !== '' || $nm) {
            $short = mb_strlen($txt) > 220 ? rtrim(mb_substr($txt, 0, 200)) . '…' : $txt;
            $rows .= '<div class="td-row">' . cc_ath_icon('food', 'td-ic') . '<div class="td-tx"><h3>' . esc_html(cc_td_w('marine')) . '</h3>'
                . ($short !== '' ? '<p>' . nl2br(esc_html($short)) . '</p>' : '') . ($nm ? '<p class="td-sub">' . esc_html(sprintf(cc_td_w('meals'), $nm)) . '</p>' : '')
                . '<a class="td-link" data-fd-load href="' . esc_url(add_query_arg('fd', 'today', $hub)) . '#food">' . esc_html(cc_td_w('see')) . ' →</a></div></div>';
        }
    }
    // 3. the newest unread message from Matteo (his replies, his own messages, his answers on results and Vekta sessions)
    if (function_exists('cc_inbox_get')) {
        foreach (cc_inbox_get(function_exists('cc_ath_viewer_uid') ? cc_ath_viewer_uid() : get_current_user_id()) as $x) {   // demo page: no inbox (never Matteo's own)
            if (!empty($x['read']) || (time() - (int) ($x['at'] ?? 0)) > 14 * DAY_IN_SECONDS) continue;
            $tag = (string) ($x['tag'] ?? '');
            if (!($tag === 'cc-msg' || $tag === 'cc-reply' || strpos($tag, 'cc-result-') === 0 || (!$tp && strpos($tag, 'cc-vx-') === 0))) continue;
            $body = trim((string) ($x['body'] ?? '')); $url = (string) ($x['url'] ?? '') ?: $hub;
            $rows .= '<div class="td-row td-msg"><img class="td-face" src="https://coaching.cigalacycling.com/wp-content/uploads/2026/11/cigala-email-matteo-photo.jpg" alt="" width="44" height="44">'
                . '<div class="td-tx"><h3>' . esc_html(cc_td_w('msg')) . '</h3>' . ($body !== '' ? '<p>' . esc_html(mb_strlen($body) > 160 ? mb_substr($body, 0, 150) . '…' : $body) . '</p>' : '')
                . '<a class="td-link" href="' . esc_url($url) . '">' . esc_html(cc_td_w('read')) . ' →</a></div></div>';
            break;
        }
    }
    $btn = $food ? '<a class="btn btn-go td-log" data-fd-load href="' . esc_url(add_query_arg('fd', 'today', $hub)) . '#food">🍽 ' . esc_html(cc_fd_w('log_today')) . '</a>' : '';
    if ($rows === '' && $btn === '') return '';
    return '<section class="ath-s ath-today" id="today" aria-labelledby="td-h"><h2 id="td-h">' . cc_ath_icon('calendar', 'ath-hic') . esc_html(cc_td_w('title')) . '</h2>'
        . $rows . $btn . '</section>' . cc_td_css();
}
function cc_td_css() {
    return '<style>html .cc .ath-today{display:grid;gap:12px}html .cc .ath-today>h2{margin-bottom:2px}'
        . 'html .cc .td-row{display:flex;align-items:flex-start;gap:12px;padding:12px 0 0;border-top:1px solid rgba(255,255,255,.08)}html .cc .ath-today>h2+.td-row{border-top:0;padding-top:0}'
        . 'html .cc .td-ic{flex:none;width:44px;height:44px;border-radius:12px;display:grid;place-items:center;background:rgba(18,161,80,.15);border:1px solid rgba(43,212,122,.35)}'
        . 'html .cc .td-ic svg{width:22px;height:22px;fill:none;stroke:#2bd47a;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}'
        . 'html .cc .td-face{flex:none;width:44px;height:44px;border-radius:50%;object-fit:cover}'
        . 'html .cc .td-tx{flex:1;min-width:0}html .cc .td-tx h3{margin:0 0 4px;font:700 16px var(--body);color:#fff;text-transform:none;letter-spacing:0}'
        . 'html .cc .td-tx p,html .cc .td-tx li{margin:0 0 4px;color:#d0d6e0;font-size:16px;line-height:1.5;overflow-wrap:anywhere}html .cc .td-tx ul{list-style:none;margin:0;padding:0}'
        . 'html .cc .td-tx .td-sub{color:#b8bec8;font-size:15px}html .cc .td-ok{color:#2bd47a;font-weight:700}html .cc .td-tx li b{color:#fff}'
        . 'html .cc .td-link{display:inline-flex;align-items:center;min-height:44px;color:#2bd47a;font-weight:600;font-size:15px;text-decoration:underline}'
        . 'html .cc .td-log{justify-self:start;width:auto;min-height:44px;margin:4px 0 0}@media (max-width:600px){html .cc .td-log{justify-self:stretch;text-align:center}}</style>';
}
add_filter('cc_ath_after_hero', function ($html, $view) { return $html . cc_td_card($view); }, 10, 2);
