<?php
/* Live Coaching, 16 Nov 2026 (coaching/SEO-DECISIONS.md): the two approved 301 redirects and /llms.txt.
 * The 301 Redirects plugin has no REST API and there is no FTP access, so both are done here.
 * The two old pages are set to draft, so they leave the sitemap. Pushed by tools/coaching_live_snippets.py. */
add_action('init', function () {
    $path = strtok($_SERVER['REQUEST_URI'] ?? '', '?');
    $map = array('/dummy-page/' => '/', '/dummy-page' => '/', '/group-club-packages2/' => '/group-club-packages/', '/group-club-packages2' => '/group-club-packages/');
    if (isset($map[$path])) { wp_redirect(home_url($map[$path]), 301, 'Cigala'); exit; }
    if ($path === '/llms.txt') {
        header('Content-Type: text/plain; charset=utf-8'); header('X-Robots-Tag: noindex');
        echo get_option('cc_llms_txt', ''); exit;
    }
}, 1);
