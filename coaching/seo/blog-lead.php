<?php
// Blog posts (Matteo 16 Nov 2026): the post template shows the excerpt as an opening line above the article. On many posts that
// excerpt is just the start of the article (automatic, or copied), so readers saw the same text twice. When it repeats the
// article's opening, the body gets the class cc-no-lead and the excerpt is hidden (CSS in the Coaching kit). A real, separate
// introduction (e.g. Strength Training) still shows, at the same size as the article text.
function cc_lead_norm($s) { return trim(preg_replace('/\s+/u', ' ', mb_strtolower(html_entity_decode(wp_strip_all_tags($s), ENT_QUOTES, 'UTF-8')))); }
function cc_lead_repeats($post) {
    if (!$post || !has_excerpt($post)) return true;                     // automatic excerpt = the article's first words
    $ex = cc_lead_norm($post->post_excerpt); $c = cc_lead_norm($post->post_content);
    $probe = mb_substr($ex, 2, 60);                                      // skip the first characters (some copies lost a letter)
    return $probe !== '' && mb_strpos(mb_substr($c, 0, 2000), $probe) !== false;
}
add_filter('body_class', function ($c) {
    if (is_singular('post') && cc_lead_repeats(get_queried_object())) $c[] = 'cc-no-lead';
    return $c;
});
