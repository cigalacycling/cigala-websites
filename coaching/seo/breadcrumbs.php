<?php
/* Breadcrumb structured data (BreadcrumbList JSON-LD), Matteo 16 Nov 2026 "go ahead on all sites".
 * The site has no Yoast schema graph (its JSON-LD is Organization / Service / WebSite only), so this adds one
 * BreadcrumbList per page: Home > (Blog for posts | parent pages) > page. Nothing visible changes.
 * Not on the homepage, on noindex pages (athlete area), on archives or on 404s.
 * Pushed as a Code Snippets snippet by tools/coaching_breadcrumbs.py. */
add_action('wp_head', function () {
    if (is_front_page() || !is_singular() || is_404()) return;
    $id = get_queried_object_id();
    if (!$id || get_post_status($id) !== 'publish' || in_array(get_post_type($id), array('cc_athlete'), true)) return;
    if (class_exists('WPSEO_Meta') && WPSEO_Meta::get_value('meta-robots-noindex', $id) === '1') return;
    if (strpos((string) get_page_template_slug($id), 'athlete') !== false || get_post_field('post_name', $id) === 'athletes') return;
    $name = function ($pid) { return trim(wp_strip_all_tags(html_entity_decode(get_the_title($pid), ENT_QUOTES, 'UTF-8'))); };
    $items = array(array('Home', home_url('/')));
    if (get_post_type($id) === 'post') {
        $blog = get_page_by_path('blog');
        if ($blog) $items[] = array($name($blog->ID), get_permalink($blog->ID));
    } else {
        foreach (array_reverse(get_post_ancestors($id)) as $a) $items[] = array($name($a), get_permalink($a));
    }
    $items[] = array($name($id), get_permalink($id));
    $list = array();
    foreach ($items as $i => $it) $list[] = array('@type' => 'ListItem', 'position' => $i + 1, 'name' => $it[0], 'item' => $it[1]);
    echo '<script type="application/ld+json">' . wp_json_encode(array('@context' => 'https://schema.org', '@type' => 'BreadcrumbList', 'itemListElement' => $list), JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE) . "</script>\n";
}, 30);
