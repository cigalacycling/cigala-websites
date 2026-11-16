<?php
/* Rider Information Form online + "Update your details" + hub lock (Matteo, 16 Nov 2026). Part of the athlete area.
 * Pushed with athlete-area.php by `python3 -I tools/coaching_athlete_area.py --availability` (staging first; live only with Matteo).
 * Needs form-legal.php (the legal texts) loaded first.
 *
 * - New athletes: the hub stays closed until they complete and sign the full form (7 steps, saved as they go).
 * - Athletes with a paper form on file (Matteo marks them, or the import does): a short "Update your details" step, no signature.
 * - Under 18 (from the date of birth): the parent/guardian consent part and a guardian signature; Matteo countersigns.
 * - On submit: answers saved privately on the athlete page (meta cc_profile), a signed PDF in uploads/cc-private, emailed to
 *   Matteo and the athlete; the usual week fills "My availability" and the goals fill "My goals & events" if those are empty.
 * - Matteo: /athletes/?board=forms (status, view answers, unlock/lock, paper form on file, countersign). Never locked himself.
 * - PC tools: GET /wp-json/cc/v1/profile?email= (application password, editor or above).
 * Health answers: only the athlete (their PDF) and Matteo. Never shown in the hub.
 */
if (!defined('ABSPATH')) return;

/* ---------- the questions, defined once (page, checks, PDF, coach view, API) ---------- */
// the athlete's own language (their "Athlete language"), from onboarding-i18n.php; anything missing stays English
function cc_f($s) { $l = $GLOBALS['cc_f_lang'] ?? 'en'; if ($l === 'en' || !function_exists('cc_f_dict')) return $s; $d = cc_f_dict($l); return isset($d[$s]) && $d[$s] !== '' ? $d[$s] : $s; }
function cc_f_set_lang($uid) { $GLOBALS['cc_f_lang'] = $uid && function_exists('cc_ath_lang_code') ? cc_ath_lang_code($uid) : 'en'; }
const CC_F_YN = ['Frequent or severe headaches', 'Dizziness or fainting spells', 'Heart or vascular problems', 'High or low blood pressure', 'Asthma or lung disease',
    'Epilepsy or seizures', 'Diabetes', 'Stroke', 'Muscular disorders or complaints', 'Chest pains', 'Back pains', 'Lower limb or joint problems',
    '(Women only) Are you or have you been pregnant in the past year?'];
function cc_f_steps() {
    $yn = []; foreach (CC_F_YN as $i => $q) $yn[] = ['yn' . $i, 'yn', $q, 'if' => $i === 12 ? 'notmale' : null];
    $med = []; foreach (['cyc' => 'Cycling', 'run' => 'Running', 'swim' => 'Swimming', 'gym' => 'Gym', 'core' => 'Core & Stretching', 'hike' => 'Hiking'] as $k => $a) $med[] = ['med_' . $k, 'text', $a, 'ph' => 'N/A if nothing', 'half' => 1];
    return [
      ['about', 'About you', 'both', [
        ['p', 'About you', null, 'fields' => [
          ['first', 'text', 'First name', 'req' => 1, 'half' => 1, 'ac' => 'given-name'], ['last', 'text', 'Surname', 'req' => 1, 'half' => 1, 'ac' => 'family-name'],
          ['dob', 'date', 'Date of birth', 'req' => 'full', 'half' => 1, 'only' => 'full'], ['gender', 'radio', 'Gender', 'opts' => ['f' => 'Female', 'm' => 'Male'], 'half' => 1, 'only' => 'full'],
          ['phone', 'tel', 'Mobile', 'req' => 1, 'half' => 1, 'ac' => 'tel'], ['phone_home', 'tel', 'Home telephone', 'opt' => 1, 'half' => 1],
          ['email', 'email', 'Email', 'req' => 1, 'ac' => 'email'],
          ['address', 'text', 'Address', 'opt' => 'adult', 'req' => 'u18', 'ac' => 'street-address', 'only' => 'full'], ['postcode', 'text', 'Postcode / Eircode', 'opt' => 'adult', 'req' => 'u18', 'half' => 1, 'ac' => 'postal-code', 'only' => 'full'],
          ['team', 'text', 'Cycling club, group or team', 'ph' => 'or N/A', 'half' => 1],
          ['sport', 'radio', 'Category', 'opts' => ['cycling' => 'Cycling', 'triathlon' => 'Triathlon', 'running' => 'Running'], 'only' => 'full'],
        ]],
        ['p', 'Emergency contact', 'Someone I can call in an emergency.', 'fields' => [
          ['ec_first', 'text', 'First name', 'req' => 1, 'half' => 1], ['ec_last', 'text', 'Surname', 'req' => 1, 'half' => 1],
          ['ec_rel', 'text', 'Relationship to you', 'ph' => 'e.g. partner, parent', 'half' => 1], ['ec_mobile', 'tel', 'Mobile', 'req' => 1, 'half' => 1],
          ['ec_home', 'tel', 'Home telephone', 'opt' => 1, 'half' => 1], ['ec_work', 'tel', 'Work telephone', 'opt' => 1, 'half' => 1],
        ]]]],
      ['numbers', 'Your numbers', 'both', [
        ['p', 'Your numbers', 'Only what you know. Leave anything else empty: we will test it together.', 'fields' => [
          ['height', 'number', 'Height (cm)', 'half' => 1], ['weight', 'number', 'Weight (kg)', 'half' => 1], ['weight_goal', 'number', 'Ideal race weight (kg)', 'opt' => 1],
          ['ftp', 'number', 'Threshold power, FTP or CP (W)', 'half' => 1], ['ftp_date', 'date', 'Date of that test', 'half' => 1],
          ['thr', 'number', 'Threshold heart rate (bpm)', 'half' => 1], ['thr_date', 'date', 'Date of that test', 'half' => 1],
          ['pace', 'text', 'Running threshold pace (min/km)', 'ph' => 'e.g. 4:30', 'half' => 1, 'if' => 'run'], ['pace_date', 'date', 'Date of that test', 'half' => 1, 'if' => 'run'],
          ['kit', 'checks', 'Do you have a heart rate monitor, a power meter, a cadence sensor, a turbo trainer, a gym membership? Tap what you have.',
             'opts' => ['hr' => 'Heart rate monitor', 'power' => 'Power meter', 'cadence' => 'Cadence sensor', 'turbo' => 'Turbo trainer', 'gym' => 'Gym membership']],
          ['turbo_model', 'text', 'Which turbo trainer?', 'opt' => 1, 'ph' => 'e.g. Wahoo Kickr'],
        ]]]],
      ['week', 'Your week', 'both', [
        ['p', 'Your usual week', 'Day of the week and hours available. This fills in “My availability” in your hub, so you only do it once.', 'fields' => [
          ['week', 'week', ''],
          ['rest', 'checks', 'Day or days you would prefer to have as REST', 'opts' => 'days'],
          ['hours_now', 'textarea', 'How many hours a week, and a day, do you normally train?', 'only' => 'full'],
          ['week_could', 'textarea', 'What could your training week look like?', 'only' => 'full'],
          ['recent', 'textarea', 'Can you give me an example week of your training in the past months, up to now?', 'ph' => 'e.g. 1h turbo Tue and Thu, club spin Sunday 100 km'],
          ['with', 'checks', 'Do you train alone or with someone?', 'opts' => ['alone' => 'Alone', 'club' => 'Club spins', 'friends' => 'With friends', 'indoor' => 'Indoor (Zwift etc.)'], 'only' => 'full'],
          ['winter', 'checks', 'What other sports could you do in the winter?', 'opts' => ['gym' => 'Gym', 'running' => 'Running', 'swimming' => 'Swimming', 'hiking' => 'Hiking', 'mtb' => 'MTB', 'cx' => 'Cyclocross'], 'only' => 'full'],
          ['with_more', 'text', 'Anything else about training with others or winter sports?', 'opt' => 1, 'only' => 'full'],
        ]]]],
      ['goals', 'Your goals', 'both', [
        ['p', 'Your goals', null, 'fields' => [
          ['goal_short', 'textarea', 'Short-term goal (1 year)'], ['goal_long', 'textarea', 'Long-term goal (more than 1 year)'],
          ['races', 'textarea', 'If you are racing, what is your racing calendar for the next months? Please include league and club races too.'],
          ['race_a', 'text', 'Which of those races would you like to do particularly well?'],
        ]],
        ['p', 'You as a rider', null, 'only' => 'full', 'fields' => [
          ['since', 'text', 'When did you start cycling / triathlon?'],
          ['motiv', 'radio', 'Are you motivated?', 'opts' => ['4' => 'Highly', '3' => 'Quite', '2' => 'Not really', '1' => 'Not at all']],
          ['motiv_why', 'textarea', 'Tell me more', 'opt' => 1], ['strengths', 'textarea', 'What are your strengths?'], ['weak', 'textarea', 'What are your weaknesses?'],
        ]]]],
      ['health', 'Health', 'full', [
        ['note', 'Your health answers are private: only you and Matteo can see them.'],
        ['p', 'Medical history', 'CC_F_MED_INTRO', 'fields' => array_merge(
          [['med', 'group', 'Any medical history that may prevent or be affected by your participating in the following activities? Please state:']], $med, [
          ['injuries', 'textarea', 'Any previous or recent injuries or disabilities that may prevent or be affected by you participating in the coaching program? If yes, please state:'],
          ['disab', 'yn', 'Have you any disabilities that may prevent you taking part in sport activity?'],
          ['ops', 'yn', 'Have you had any operations or surgical procedures that would affect your ability to cycle at high intensity?'],
          ['allerg', 'yn', 'Do you have any allergies?'], ['docno', 'yn', 'Has your doctor ever advised you not to take part in exercise?'],
          ['yn2_details', 'textarea', 'Please give details', 'if' => 'yes:disab,ops,allerg,docno'],
          ['ynh', 'group', 'Do you have or have you ever had the following?']], $yn, [
          ['yn_details', 'textarea', 'If you have answered yes to any of the questions above, please give details:', 'if' => 'yes:yn0,yn1,yn2,yn3,yn4,yn5,yn6,yn7,yn8,yn9,yn10,yn11,yn12'],
        ])],
        ['p', 'Food and diet', null, 'fields' => [
          ['diet_plan', 'textarea', 'Do you currently follow a diet plan?'], ['diet_req', 'text', 'Have you any dietary requirements?'],
          ['diet_score', 'select', 'How would you rate your diet from 1 to 10?', 'opts' => array_combine(range(1, 10), range(1, 10))],
          ['lose', 'yn', 'Do you feel you need to lose weight to improve your cycling performance?'], ['lose_more', 'text', 'Tell me more', 'opt' => 1],
          ['supps', 'text', 'Are you currently taking tablets to aid immune function, such as a multivitamin?'],
        ]]]],
      ['healthupd', 'Health', 'update', [
        ['p', 'Anything new?', 'Since your last form: a new injury, illness, operation or medication? Your answers are private: only you and Matteo can see them.', 'fields' => [
          ['health_new', 'yn', 'Anything new since your form?', 'req' => 1], ['health_new_details', 'textarea', 'Please give details', 'if' => 'yes:health_new'],
        ]]]],
      ['agree', 'Agreements', 'full', [
        ['p', 'Agreements', 'Please read each part. Ticking and signing at the end counts as your signature.', 'fields' => [
          ['legal_h', 'legal', 'Health declaration', 'text' => 'CC_F_HEALTH'], ['ok_health', 'tick', 'I have read and agree to the health declaration', 'req' => 1],
          ['legal_w', 'legal', 'Acknowledgement of responsibility and liability', 'text' => 'CC_F_WAIVER'], ['ok_waiver', 'tick', 'I have read and agree to the acknowledgement of responsibility and liability', 'req' => 1],
          ['legal_t', 'legal', 'Coaching terms and conditions', 'text' => 'CC_F_TERMS'], ['ok_terms', 'tick', 'I have read and agree to the Coaching Terms & Conditions, including the Coaching & Training Plan Liability Waiver & Informed Consent', 'req' => 1],
          ['ok_doping', 'tick', 'Anti-doping: I take responsibility for the pharmaceutical and nutritional side (medicines, supplements, food), and I am aware of the World Anti-Doping Agency list of prohibited substances', 'req' => 1],
        ]],
        ['p', 'Rider information and coaching consent', 'CC_F_U18_INTRO', 'if' => 'u18', 'fields' => [
          ['u18c', 'group', 'Parental / guardian / carer consent for riders under the age of 18', 'text' => 'CC_F_U18_CONSENT'],
          ['g1', 'yn', 'Consent for participation in coaching activities on public roads.', 'yesno' => 1, 'req' => 'u18'],
          ['g2', 'yn', 'Consent for moving from one location to another on the public highway (riders must be aged 12 or older).', 'yesno' => 1, 'req' => 'u18'],
          ['g3', 'yn', 'Consent for participating in prescribed training (riders must be category U14 or older).', 'yesno' => 1, 'req' => 'u18'],
          ['g4', 'yn', 'Consent for appropriate photographs and videos for coaching purposes.', 'yesno' => 1, 'req' => 'u18'],
          ['g_name', 'text', 'Parent / guardian / carer name', 'half' => 1, 'req' => 'u18'], ['g_rel', 'text', 'Relationship to rider', 'half' => 1, 'req' => 'u18'],
          ['legal_a', 'legal', 'Appendix: notes for riders and parents', 'text' => 'CC_F_APPENDIX'], ['ok_u18', 'tick', 'I have read the appendix and give the consents above', 'req' => 'u18'],
        ]]]],
      ['sign', 'Sign', 'full', [
        ['p', 'Sign', 'Type your full name and sign with your finger (or mouse). The date is added for you. You and Matteo both get a PDF copy by email. Under 18: the parent or guardian signs.', 'fields' => [
          ['sig_name', 'text', 'Full name', 'req' => 1, 'ac' => 'name'], ['sig_g', 'text', 'Parent / guardian / carer full name', 'if' => 'u18', 'req' => 'u18'],
          ['sig', 'sig', ''],
        ]]]],
    ];
}
// every answer field with its definition, for one kind of form ('full' or 'update')
function cc_f_fields($kind) {
    $out = [];
    foreach (cc_f_steps() as $st) {
        if ($st[2] !== 'both' && $st[2] !== $kind) continue;
        foreach ($st[3] as $pn) {
            if (($pn[0] ?? '') !== 'p' || (isset($pn['only']) && $pn['only'] !== $kind)) continue;
            foreach ($pn['fields'] as $f) {
                if (isset($f['only']) && $f['only'] !== $kind) continue;
                if (in_array($f[1], ['group', 'legal', 'sig'], true)) continue;
                $f['_panel_if'] = $pn['if'] ?? null; $out[$f[0]] = $f;
            }
        }
    }
    return $out;
}
function cc_f_age($dob) { if (!cc_av_date($dob)) return null; $b = new DateTime($dob); return $b->diff(new DateTime(current_time('Y-m-d')))->y; }
// browser data -> clean answers (unknown keys dropped)
function cc_f_clean($in, $kind) {
    $in = is_array($in) ? $in : []; $out = [];
    $days = array_keys(CC_AV_DAYS);
    foreach (cc_f_fields($kind) as $k => $f) {
        $v = $in[$k] ?? null;
        switch ($f[1]) {
            case 'week': $out[$k] = cc_av_clean(['week' => is_array($v) ? $v : []], current_time('Y-m-d'))['week']; break;
            case 'checks': $opts = $f['opts'] === 'days' ? $days : array_map('strval', array_keys($f['opts'])); $out[$k] = array_values(array_intersect($opts, array_map('strval', (array) $v))); break;
            case 'radio': case 'select': $out[$k] = isset($f['opts'][(string) $v]) ? (string) $v : ''; break;
            case 'yn': $out[$k] = in_array($v, ['yes', 'no'], true) ? $v : ''; break;
            case 'tick': $out[$k] = !empty($v) ? 1 : 0; break;
            case 'date': $out[$k] = cc_av_date((string) $v); break;
            case 'number': $out[$k] = is_numeric($v) ? 0 + $v : ''; break;
            case 'email': $out[$k] = sanitize_email((string) $v); break;
            case 'textarea': $out[$k] = cc_av_note($v, 3000); break;
            default: $out[$k] = cc_av_str($v, 300);
        }
    }
    return $out;
}
// what is missing before the form can be submitted (labels), given the answers
function cc_f_missing($a, $kind, $sig_ok) {
    $u18 = $kind === 'full' && ($age = cc_f_age($a['dob'] ?? '')) !== null && $age < 18;
    $miss = [];
    foreach (cc_f_fields($kind) as $k => $f) {
        $r = $f['req'] ?? 0;
        $need = $r === 1 || ($r === 'full' && $kind === 'full') || ($r === 'u18' && $u18);
        if ($f['_panel_if'] === 'u18' && !$u18) $need = false;
        if ($need && ($a[$k] === '' || $a[$k] === 0 || $a[$k] === [] || $a[$k] === null)) $miss[] = $f[2];
    }
    if ($kind === 'full' && !$sig_ok) $miss[] = 'Signature';
    return $miss;
}

/* ---------- state ---------- */
function cc_f_kind($uid) { return get_user_meta($uid, 'cc_form_kind', true) === 'update' ? 'update' : 'full'; }
function cc_f_open($uid) { return (bool) (get_user_meta($uid, 'cc_form_done', true) || get_user_meta($uid, 'cc_form_unlock', true)); }
// the hub is closed for athletes until the form is done (or Matteo unlocked it)
add_filter('cc_ath_gate', function ($html, $me, $mine) {
    if ($html !== '' || !$mine || cc_ath_is_coach() || cc_f_open($me->ID)) return $html;
    return cc_f_page($me->ID, $mine, false);
}, 10, 3);
add_filter('cc_ath_can_see', function ($ok, $pid, $uid) { return ($ok && !cc_ath_is_coach() && !cc_f_open($uid)) ? false : $ok; }, 10, 3);

/* ---------- the page ---------- */
function cc_f_page($uid, $pid, $preview, $kind = null) {
    $u = get_userdata($uid); $kind = $kind ?: cc_f_kind($uid);
    cc_f_set_lang($preview ? 0 : $uid);
    if ($preview && isset($_GET['flang']) && preg_match('/^[a-z]{2}$/', $_GET['flang'])) $GLOBALS['cc_f_lang'] = $_GET['flang'];   // Matteo previews a language
    $draft = $preview ? [] : (json_decode((string) get_user_meta($uid, 'cc_form_draft', true), true) ?: []);
    $pre = $preview ? [] : (json_decode((string) get_post_meta($pid, 'cc_profile_prefill', true), true) ?: []);
    $prof = $preview ? [] : (json_decode((string) get_post_meta($pid, 'cc_profile', true), true) ?: []);   // earlier answers, when asked again
    $vals = array_merge(['first' => $u ? $u->first_name : '', 'last' => $u ? $u->last_name : '', 'email' => $u ? $u->user_email : ''], $prof, $pre, $draft);
    if (!$preview && ($av = cc_av_get($pid)) && empty($draft['week'])) $vals['week'] = $av['week'];
    $steps = array_values(array_filter(cc_f_steps(), function ($s) use ($kind) { return $s[2] === 'both' || $s[2] === $kind; }));
    $n = count($steps);
    $first = $u ? ($u->first_name ?: $u->display_name) : '';
    $o = '<div class="rf" id="rf" data-kind="' . $kind . '" data-preview="' . ($preview ? 1 : 0) . '" data-api="' . esc_url(rest_url('cc/v1/form')) . '" data-nonce="' . esc_attr(wp_create_nonce('wp_rest')) . '">'
       . '<div class="rf-hero"><p class="eyebrow">' . esc_html(cc_f($kind === 'full' ? 'Welcome to Cigala Cycling Coaching' : 'Athlete hub')) . '</p>'
       . ($preview ? '<h2 class="rf-h1">' : '<h1>') . esc_html(cc_f($kind === 'full' ? 'Tell me about you' : 'Update your details')) . ($preview ? '</h2>' : '</h1>') . '<div class="bar"></div>'
       . '<p class="ath-lede">' . esc_html($kind === 'full'
            ? cc_f('This helps me build your plan around your life and your goals. It takes about 15 minutes, and you can stop and come back: your answers are saved as you go.')
            : sprintf(cc_f('Hi %s, your hub has a new home. Before it opens, take 3 minutes to update your details, so your plan starts from where you are now. Your answers are saved as you go.'), $first)) . '</p>'
       . '<a class="ath-out" href="' . esc_url(wp_logout_url(home_url('/' . CC_ATH_SLUG . '/'))) . '">' . esc_html(cc_t('Log out')) . '</a></div>'
       . '<div class="rf-steps"><ol aria-hidden="true">' . str_repeat('<li></li>', $n) . '</ol><p>' . esc_html(cc_f('Step')) . ' <b class="rf-sn">1</b> / ' . $n . ' · <b class="rf-st"></b></p></div><form novalidate>';
    foreach ($steps as $i => $st) {
        $o .= '<section class="rf-step' . ($i ? '' : ' on') . '" data-t="' . esc_attr(cc_f($st[1])) . '" data-k="' . $st[0] . '">';
        if ($st[0] === 'agree' && ($GLOBALS['cc_f_lang'] ?? 'en') !== 'en') $o .= '<div class="rf-note">' . esc_html(cc_f('The agreements are in English: that is the version you sign. Message me if anything is unclear.')) . '</div>';
        foreach ($st[3] as $pn) {
            if ($pn[0] === 'note') { $o .= '<div class="rf-note">' . esc_html(cc_f($pn[1])) . '</div>'; continue; }
            if (isset($pn['only']) && $pn['only'] !== $kind) continue;
            $sub = $pn[2] ?? null; $sub = $sub && defined($sub) ? constant($sub) : ($sub ? esc_html(cc_f($sub)) : '');
            $o .= '<div class="rf-panel"' . (isset($pn['if']) ? ' data-if="' . $pn['if'] . '" hidden' : '') . '><h2>' . esc_html(cc_f($pn[1])) . '</h2><div class="bar"></div>'
                . ($sub ? '<p class="rf-sub">' . $sub . '</p>' : '') . '<div class="rf-grid">';
            foreach ($pn['fields'] as $f) { if (isset($f['only']) && $f['only'] !== $kind) continue; $o .= cc_f_field($f, $vals[$f[0]] ?? null, $kind); }
            $o .= '</div></div>';
        }
        $o .= '</section>';
    }
    $o .= '<p class="ath-err rf-err" role="alert" hidden></p><div class="rf-nav"><button type="button" class="btn btn-ghost rf-back">' . esc_html(cc_f('Back')) . '</button>'
        . '<button type="button" class="btn btn-go rf-next">' . esc_html(cc_f('Next')) . '</button></div>'
        . '<p class="rf-saved" aria-live="polite">' . esc_html(cc_f('Your answers are saved as you go.')) . '</p></form>'
        . '<p class="ath-help">' . esc_html(cc_f('Any trouble?')) . ' <a href="https://wa.me/353834777697" target="_blank" rel="noopener">WhatsApp</a> · <a href="mailto:matteo@cigalacycling.com">matteo@cigalacycling.com</a></p></div>'
        . '<script type="application/json" id="rf-words">' . wp_json_encode(['next' => cc_f('Next'), 'submit' => cc_f($kind === 'full' ? 'Submit and sign' : 'Save and open my hub'),
            'saving' => cc_f('Saving…'), 'saved' => cc_f('Saved'), 'almost' => cc_f('Almost there: please fill in'), 'err' => cc_f('That did not save. Please check your connection and try again.'),
            'age' => cc_f('Age'), 'preview' => cc_f('Preview: nothing is saved.')]) . '</script>' . cc_f_js();
    return $o;
}
function cc_f_field($f, $v, $kind) {
    [$k, $t, $label] = $f; $label = $label !== '' ? esc_html(cc_f($label)) : '';
    $opt = ($f['opt'] ?? 0) === 1 ? ' <small>' . esc_html(cc_f('(optional)')) . '</small>' : (($f['opt'] ?? 0) === 'adult' ? ' <small class="rf-opt">' . esc_html(cc_f('(optional)')) . '</small>' : '');
    $wrap = function ($inner, $cls = '') use ($f) { return '<div class="rf-f' . (!empty($f['half']) ? ' half' : '') . $cls . '"' . (!empty($f['if']) ? ' data-if="' . esc_attr($f['if']) . '" hidden' : '') . '>' . $inner . '</div>'; };
    $ph = isset($f['ph']) ? ' placeholder="' . esc_attr(cc_f($f['ph'])) . '"' : ''; $ac = isset($f['ac']) ? ' autocomplete="' . $f['ac'] . '"' : '';
    $id = 'rf-' . $k; $name = ' name="' . $k . '" id="' . $id . '"';
    switch ($t) {
        case 'text': case 'tel': case 'email': case 'date':
            $extra = $t === 'date' && $k === 'dob' ? '<small class="rf-age"></small>' : '';
            return $wrap('<label for="' . $id . '">' . $label . $opt . '</label><input type="' . $t . '"' . $name . $ph . $ac . ' value="' . esc_attr((string) $v) . '">' . $extra);
        case 'number': return $wrap('<label for="' . $id . '">' . $label . $opt . '</label><input type="number" inputmode="decimal" step="any"' . $name . ' value="' . esc_attr((string) $v) . '">');
        case 'textarea': return $wrap('<label for="' . $id . '">' . $label . $opt . '</label><textarea rows="3"' . $name . $ph . '>' . esc_textarea((string) $v) . '</textarea>');
        case 'select': $s = '<option value=""></option>'; foreach ($f['opts'] as $ov => $ol) $s .= '<option value="' . $ov . '"' . ((string) $v === (string) $ov ? ' selected' : '') . '>' . esc_html($ol) . '</option>';
            return $wrap('<label for="' . $id . '">' . $label . '</label><select' . $name . '>' . $s . '</select>');
        case 'radio': case 'checks':
            $opts = $f['opts'] === 'days' ? array_map(function ($d) { return cc_f(substr($d, 0, 3)); }, CC_AV_DAYS) : $f['opts']; $c = '';
            foreach ($opts as $ov => $ol) $c .= '<label class="rf-chip"><input type="' . ($t === 'radio' ? 'radio' : 'checkbox') . '" name="' . $k . '" value="' . esc_attr($ov) . '"'
                . (($t === 'radio' ? (string) $v === (string) $ov : in_array((string) $ov, array_map('strval', (array) $v), true)) ? ' checked' : '') . '><span>' . esc_html(cc_f($ol)) . '</span></label>';
            return $wrap('<fieldset><legend>' . $label . '</legend><div class="rf-chips">' . $c . '</div></fieldset>', ' full');
        case 'yn': $o = $f['yesno'] ?? 0;
            $c = '<label><input type="radio" name="' . $k . '" value="' . ($o ? 'yes' : 'no') . '"' . ($v === ($o ? 'yes' : 'no') ? ' checked' : '') . '><span>' . esc_html(cc_f($o ? 'Yes' : 'No')) . '</span></label>'
               . '<label><input type="radio" name="' . $k . '" value="' . ($o ? 'no' : 'yes') . '"' . ($v === ($o ? 'no' : 'yes') ? ' checked' : '') . '><span>' . esc_html(cc_f($o ? 'No' : 'Yes')) . '</span></label>';
            return $wrap('<fieldset class="rf-yn"><legend>' . $label . '</legend><div class="rf-seg">' . $c . '</div></fieldset>', ' full');
        case 'tick': return $wrap('<label class="rf-tick"><input type="checkbox" name="' . $k . '" value="1"' . ($v ? ' checked' : '') . '><span>' . $label . '</span></label>', ' full');
        case 'group': return $wrap('<p class="rf-group">' . $label . '</p>' . (isset($f['text']) ? '<div class="rf-group-t">' . constant($f['text']) . '</div>' : ''), ' full');
        case 'legal': return $wrap('<div class="rf-legal" tabindex="0" role="region" aria-label="' . esc_attr($label) . '"><h3>' . $label . '</h3>' . constant($f['text']) . '</div>', ' full');
        case 'week':
            $w = is_array($v) ? $v : []; $g = '<div class="av-week rf-week">';
            foreach (CC_AV_DAYS as $dk => $dn) { $d = $w[$dk] ?? ['h' => '', 'w' => []]; $s = '';
                foreach (CC_AV_HOURS as $hv => $hl) $s .= '<option value="' . $hv . '"' . ((string) $d['h'] === (string) $hv ? ' selected' : '') . '>' . esc_html(cc_f($hl)) . '</option>';
                $g .= '<div class="av-day" data-k="' . $dk . '"><label class="av-dn" for="rf-h-' . $dk . '">' . esc_html(cc_f($dn)) . '</label><select id="rf-h-' . $dk . '" data-day="' . $dk . '">' . $s . '</select><div class="av-when">';
                foreach (CC_AV_WHEN as $wk => $wl) $g .= '<button type="button" class="av-w" data-day="' . $dk . '" data-w="' . $wk . '" aria-pressed="' . (in_array($wk, $d['w'] ?? [], true) ? 'true' : 'false') . '"' . ($d['h'] === '0' ? ' disabled' : '') . '>' . esc_html(cc_f($wl)) . '</button>';
                $g .= '</div></div>'; }
            return $wrap($g . '</div>', ' full');
        case 'sig': return $wrap('<div class="rf-sig"><canvas aria-label="' . esc_attr(cc_f('Signature pad: sign with your finger')) . '"></canvas><span class="rf-sig-ph">' . esc_html(cc_f('Sign here')) . '</span>'
            . '<button type="button" class="btn btn-ghost rf-clr">' . esc_html(cc_f('Clear')) . '</button></div><p class="rf-date">' . esc_html(cc_f('Date')) . ': <b>' . esc_html(date_i18n('j F Y')) . '</b></p>', ' full');
    }
    return '';
}

/* ---------- saving and submitting: POST /wp-json/cc/v1/form {action: save|submit, data, sig (jpeg data URL)} ---------- */
add_action('rest_api_init', function () {
    register_rest_route('cc/v1', '/form', ['methods' => 'POST', 'callback' => 'cc_f_rest',
        'permission_callback' => function () { return is_user_logged_in() && (bool) cc_ath_page_of(get_current_user_id()) && !cc_ath_is_coach(); }]);
    register_rest_route('cc/v1', '/profile', ['methods' => 'GET', 'callback' => 'cc_f_profiles', 'permission_callback' => 'cc_ath_is_coach']);
    // Matteo / Claude: prefill from an old form, paper form on file, unlock, lock (application password)
    register_rest_route('cc/v1', '/form-admin', ['methods' => 'POST', 'callback' => 'cc_f_admin_rest', 'permission_callback' => 'cc_ath_is_coach']);
});
function cc_f_rest(WP_REST_Request $r) {
    $uid = get_current_user_id(); $pid = cc_ath_page_of($uid); $kind = cc_f_kind($uid);
    if (cc_f_open($uid) && get_user_meta($uid, 'cc_form_done', true)) return new WP_Error('cc_done', 'Already submitted.', ['status' => 409]);
    $a = cc_f_clean($r->get_param('data'), $kind);
    if ($r->get_param('action') !== 'submit') { update_user_meta($uid, 'cc_form_draft', wp_slash(wp_json_encode($a))); return ['ok' => true, 'saved' => time()]; }
    $sig = ''; $raw = (string) $r->get_param('sig');
    if ($kind === 'full' && preg_match('#^data:image/jpeg;base64,([A-Za-z0-9+/=]+)$#', $raw, $m)) { $sig = base64_decode($m[1]); if (strlen($sig) < 800 || strlen($sig) > 600000 || !@getimagesizefromstring($sig)) $sig = ''; }
    if ($miss = cc_f_missing($a, $kind, $sig !== '')) return new WP_Error('cc_missing', implode(', ', array_map('cc_f', $miss)), ['status' => 400, 'missing' => $miss]);
    $now = time(); $meta = ['kind' => $kind, 'at' => $now, 'ip' => $_SERVER['REMOTE_ADDR'] ?? '', 'ua' => substr($_SERVER['HTTP_USER_AGENT'] ?? '', 0, 200),
        'name' => $a['sig_name'] ?? '', 'guardian' => $a['sig_g'] ?? '', 'u18' => $kind === 'full' && ($age = cc_f_age($a['dob'])) !== null && $age < 18, 'lang' => cc_ath_lang_code($uid)];
    $old = json_decode((string) get_post_meta($pid, 'cc_profile', true), true) ?: [];
    $profile = $kind === 'full' ? $a : array_merge($old, json_decode((string) get_post_meta($pid, 'cc_profile_prefill', true), true) ?: [], $a);
    update_post_meta($pid, 'cc_profile', wp_slash(wp_json_encode($profile)));
    if ($sig !== '') $meta['sig_id'] = cc_f_store($pid, $sig, 'signature', 'jpg', 'image/jpeg', 'Signature');
    $pdf = '';
    if ($kind === 'full') { $pdf = cc_f_pdf($pid, $profile, $meta, $sig); $meta['pdf_id'] = cc_f_store($pid, $pdf, 'rider-form', 'pdf', 'application/pdf', 'Rider Information Form (signed ' . date_i18n('j M Y') . ')'); }
    update_post_meta($pid, 'cc_form_signed', wp_slash(wp_json_encode($meta)));
    update_user_meta($uid, 'cc_form_done', $now); delete_user_meta($uid, 'cc_form_draft');
    // the usual week and the goals start their boxes, when those are still empty
    if (!cc_av_get($pid) && !empty(array_filter(array_column($profile['week'] ?? [], 'h'), 'strlen'))) {
        update_post_meta($pid, 'cc_avail', wp_slash(wp_json_encode(['week' => $profile['week'], 'changes' => [], 'note' => '', 'voice' => [], 'updated' => $now])));
        update_post_meta($pid, 'cc_avail_updated', $now);
    }
    if (function_exists('cc_g_from_form')) cc_g_from_form($pid, $profile);
    cc_f_mail($uid, $pid, $profile, $meta, $pdf);
    return ['ok' => true, 'done' => true];
}
function cc_f_store($pid, $bytes, $base, $ext, $mime, $title) {   // private file, attached to the athlete page (served only through the login check)
    $u = wp_get_upload_dir(); $dir = $u['basedir'] . '/cc-private'; wp_mkdir_p($dir);
    $name = $base . '-' . $pid . '-' . gmdate('Ymd-His') . '-' . wp_generate_password(8, false) . '.' . $ext;
    file_put_contents($dir . '/' . $name, $bytes);
    $id = wp_insert_attachment(['post_title' => $title, 'post_mime_type' => $mime, 'post_status' => 'inherit'], $dir . '/' . $name, $pid);
    return is_wp_error($id) ? 0 : (int) $id;
}
function cc_f_mail($uid, $pid, $a, $meta, $pdf) {
    $u = get_userdata($uid); $name = get_post_field('post_title', $pid); $full = $meta['kind'] === 'full';
    $board = add_query_arg(['board' => 'forms', 'a' => $pid], home_url('/' . CC_ATH_SLUG . '/'));
    $tmp = ''; if ($pdf !== '') { $tmp = trailingslashit(get_temp_dir()) . 'Rider-Information-Form-' . sanitize_file_name($name) . '.pdf'; file_put_contents($tmp, $pdf); }
    $flags = []; foreach (CC_F_YN as $i => $q) if (($a['yn' . $i] ?? '') === 'yes') $flags[] = $q;
    foreach (['disab' => 'Disability', 'ops' => 'Operations', 'allerg' => 'Allergies', 'docno' => 'Doctor advised not to exercise', 'health_new' => 'Something new since the last form'] as $k => $l) if (($a[$k] ?? '') === 'yes') $flags[] = $l;
    $h = '<div style="font:15px/1.5 Montserrat,Arial,sans-serif;color:#111;max-width:560px"><p style="margin:0 0 4px;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#E10600;font-weight:600">Athlete hub</p>'
       . '<h2 style="margin:0 0 14px;color:#111">' . esc_html($name) . ($full ? ' signed the Rider Information Form' : ' updated their details') . '</h2>'
       . ($meta['u18'] ? '<p style="padding:10px 12px;background:#fff4e5;border-left:3px solid #E10600"><b style="color:#111">Under 18.</b> Guardian: ' . esc_html($meta['guardian']) . '. Please countersign on your coach page.</p>' : '')
       . ($flags ? '<p style="margin:0 0 6px"><b style="color:#111">Health answers marked yes</b></p><ul>' . implode('', array_map(function ($x) { return '<li>' . esc_html($x) . '</li>'; }, $flags)) . '</ul>' : '<p>No health flags marked yes.</p>')
       . '<p>' . esc_html(cc_f_line($a)) . '</p>'
       . '<p style="margin:20px 0 0"><a href="' . esc_url($board) . '" style="display:inline-block;padding:12px 20px;border-radius:8px;background:#009a44;color:#fff;font-weight:600;text-decoration:none">Open their answers</a></p>'
       . ($full ? '<p style="font-size:13px;color:#555">The signed PDF is attached and saved in their private area.</p>' : '') . '</div>';
    $hd = ['Content-Type: text/html; charset=UTF-8'];
    if ($u && is_email($u->user_email)) $hd[] = 'Reply-To: ' . $name . ' <' . $u->user_email . '>';
    if (cc_av_notify_to()) wp_mail(cc_av_notify_to(), ($full ? 'Rider form signed: ' : 'Details updated: ') . $name, $h, $hd, $tmp ? [$tmp] : []);
    if ($full && $u && is_email($u->user_email)) {   // the athlete's own copy
        cc_f_set_lang($uid);
        $first = esc_html($u->first_name ?: $name);
        wp_mail($u->user_email, cc_f('Your signed Rider Information Form'), '<div style="font:15px/1.6 Montserrat,Arial,sans-serif;color:#111;max-width:560px"><p>' . sprintf(esc_html(cc_f('Hi %s,')), $first) . '</p><p>'
            . esc_html(cc_f('Thank you! Your Rider Information Form is in, and your signed copy is attached. Your athlete hub is now open.')) . '</p><p><a href="' . esc_url(home_url('/' . CC_ATH_SLUG . '/')) . '" style="color:#009a44;font-weight:600">'
            . esc_html(cc_f('Open my athlete hub')) . '</a></p><p>' . esc_html(cc_f('See you on the road,')) . '<br><b style="color:#111">Matteo</b></p></div>',
            ['Content-Type: text/html; charset=UTF-8', 'From: Matteo Cigala <noreply@cigalacycling.com>', 'Reply-To: Matteo Cigala <matteo@cigalacycling.com>'], $tmp ? [$tmp] : []);
    }
    if ($tmp) @unlink($tmp);
}
function cc_f_line($a) {   // one line for Matteo: sport, age, numbers, goal
    $p = [];
    if (!empty($a['dob'])) $p[] = cc_f_age($a['dob']) . ' years';
    if (!empty($a['sport'])) $p[] = $a['sport'];
    if ($a['ftp'] ?? '') $p[] = 'FTP/CP ' . $a['ftp'] . ' W'; if ($a['weight'] ?? '') $p[] = $a['weight'] . ' kg';
    if ($a['goal_short'] ?? '') $p[] = 'Goal: ' . wp_trim_words($a['goal_short'], 20);
    return implode(' · ', $p);
}
function cc_f_profiles(WP_REST_Request $r) {   // for Matteo's PC tools
    $out = [];
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'meta_key' => 'cc_user']) as $p) {
        $u = get_userdata((int) get_post_meta($p->ID, 'cc_user', true)); if (!$u) continue;
        if ($r->get_param('email') && strcasecmp($u->user_email, $r->get_param('email'))) continue;
        $m = json_decode((string) get_post_meta($p->ID, 'cc_form_signed', true), true) ?: [];
        $out[] = ['athlete' => $p->post_title, 'email' => $u->user_email, 'language' => cc_ath_lang_code($u->ID), 'form' => cc_f_status($u->ID),
                  'signed' => $m ? ['kind' => $m['kind'], 'at' => $m['at'], 'pdf' => !empty($m['pdf_id']) ? wp_get_attachment_url($m['pdf_id']) : null] : null,
                  'profile' => json_decode((string) get_post_meta($p->ID, 'cc_profile', true), true) ?: (json_decode((string) get_post_meta($p->ID, 'cc_profile_prefill', true), true) ?: null)];
    }
    return $out;
}
function cc_f_status($uid) {
    if (get_user_meta($uid, 'cc_form_done', true)) return cc_f_kind($uid) === 'full' ? 'signed' : 'updated';
    if (get_user_meta($uid, 'cc_form_unlock', true)) return 'unlocked';
    return get_user_meta($uid, 'cc_form_draft', true) ? 'started' : 'waiting';
}
function cc_f_admin($pid, $act, $data = null) {
    $uid = (int) get_post_meta($pid, 'cc_user', true); if (!$uid) return new WP_Error('cc_nouser', 'No login for that athlete', ['status' => 404]);
    switch ($act) {
        case 'unlock': update_user_meta($uid, 'cc_form_unlock', time()); break;
        case 'lock': delete_user_meta($uid, 'cc_form_unlock'); break;
        case 'paper': update_user_meta($uid, 'cc_form_kind', 'update'); delete_user_meta($uid, 'cc_form_draft'); break;   // paper form on file: short update instead
        case 'full': delete_user_meta($uid, 'cc_form_kind'); delete_user_meta($uid, 'cc_form_draft'); break;
        case 'reopen': delete_user_meta($uid, 'cc_form_done'); delete_user_meta($uid, 'cc_form_draft'); break;   // ask them to fill it in again (earlier answers pre-filled)
        case 'prefill': update_post_meta($pid, 'cc_profile_prefill', wp_slash(wp_json_encode(is_array($data) ? $data : []))); break;
        case 'countersign':
            $m = json_decode((string) get_post_meta($pid, 'cc_form_signed', true), true) ?: [];
            if (empty($m['u18'])) return new WP_Error('cc_no', 'Only for under-18 forms', ['status' => 400]);
            $m['coach'] = ['name' => 'Matteo Cigala', 'at' => time()];
            $a = json_decode((string) get_post_meta($pid, 'cc_profile', true), true) ?: [];
            $sigf = !empty($m['sig_id']) ? get_attached_file($m['sig_id']) : '';
            $m['pdf_id'] = cc_f_store($pid, cc_f_pdf($pid, $a, $m, $sigf && file_exists($sigf) ? file_get_contents($sigf) : ''), 'rider-form', 'pdf', 'application/pdf', 'Rider Information Form (countersigned ' . date_i18n('j M Y') . ')');
            update_post_meta($pid, 'cc_form_signed', wp_slash(wp_json_encode($m))); break;
        default: return new WP_Error('cc_act', 'Unknown action', ['status' => 400]);
    }
    return ['ok' => true, 'status' => cc_f_status($uid)];
}
function cc_f_admin_rest(WP_REST_Request $r) {
    $pid = (int) $r->get_param('page');
    if (!$pid && $r->get_param('email')) { $u = get_user_by('email', $r->get_param('email')); $pid = $u ? cc_ath_page_of($u->ID) : 0; }
    if (!$pid || get_post_type($pid) !== 'cc_athlete') return new WP_Error('cc_none', 'No such athlete', ['status' => 404]);
    return cc_f_admin($pid, (string) $r->get_param('action'), $r->get_param('data'));
}
add_action('admin_post_cc_form_admin', function () {   // the buttons on Matteo's coach page
    $pid = (int) ($_POST['page'] ?? 0); $act = sanitize_key($_POST['act'] ?? '');
    if (!cc_ath_is_coach() || !wp_verify_nonce($_POST['_wpnonce'] ?? '', 'cc_form_admin_' . $pid)) wp_die('Not allowed');
    cc_f_admin($pid, $act);
    wp_safe_redirect(add_query_arg(['board' => 'forms', 'a' => $pid, 'done' => $act], home_url('/' . CC_ATH_SLUG . '/'))); exit;
});

/* ---------- Matteo's coach page: /athletes/?board=forms (list) and &a=PAGE (one athlete's answers) ---------- */
add_filter('cc_ath_coach_links', function ($html) {
    $w = 0; foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'fields' => 'ids', 'meta_key' => 'cc_user']) as $p)
        if (($uid = (int) get_post_meta($p, 'cc_user', true)) && !cc_f_open($uid)) $w++;
    $base = home_url('/' . CC_ATH_SLUG . '/');
    return $html . '<a class="av-boardlink" href="' . esc_url(add_query_arg('board', 'forms', $base)) . '">Rider forms' . ($w ? ' <span class="av-badge rf-wait">' . $w . ' waiting</span>' : '') . '</a>';
}, 5);
add_filter('cc_ath_coach_links', function ($html) {
    return $html . '<a class="av-boardlink" href="' . esc_url(add_query_arg(['board' => 'form-preview', 'kind' => 'full'], home_url('/' . CC_ATH_SLUG . '/'))) . '">Preview the athlete form</a>';
}, 30);
add_filter('cc_ath_board', function ($html, $board) {
    if (!cc_ath_is_coach()) return $html;
    if ($board === 'form-preview') return '<div class="ath-coach"><p><b>Preview.</b> This is what a new athlete sees: <a href="' . esc_url(add_query_arg(['board' => 'form-preview', 'kind' => 'full'])) . '">full form</a> · '
        . '<a href="' . esc_url(add_query_arg(['board' => 'form-preview', 'kind' => 'update'])) . '">update (paper form on file)</a>. Nothing is saved. Language: '
        . implode(' · ', array_map(function ($l) { return '<a href="' . esc_url(add_query_arg('flang', $l)) . '">' . strtoupper($l) . '</a>'; }, ['en', 'it', 'pt', 'sl'])) . '</p></div>'
        . cc_f_page(get_current_user_id(), 0, true, ($_GET['kind'] ?? '') === 'update' ? 'update' : 'full');
    if ($board !== 'forms') return $html;
    $base = add_query_arg('board', 'forms', home_url('/' . CC_ATH_SLUG . '/'));
    if (!empty($_GET['a']) && get_post_type((int) $_GET['a']) === 'cc_athlete') return cc_f_one((int) $_GET['a'], $base);
    $label = ['signed' => 'Signed', 'updated' => 'Details updated', 'unlocked' => 'Unlocked by you', 'started' => 'Started, not finished', 'waiting' => 'Not started'];
    $o = '<section class="ath-s"><h2>' . cc_ath_icon('doc', 'ath-hic') . 'Rider forms</h2><p class="av-lede">Who has completed the form. Athletes see their hub only after that, or once you unlock it. '
       . '<b>Paper form on file</b> means they get the short “Update your details” step instead of the full form.</p><div class="rf-list">';
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'orderby' => 'title', 'order' => 'ASC', 'meta_key' => 'cc_user']) as $p) {
        $uid = (int) get_post_meta($p->ID, 'cc_user', true); if (!$uid) continue;
        $st = cc_f_status($uid); $m = json_decode((string) get_post_meta($p->ID, 'cc_form_signed', true), true) ?: [];
        $when = $st === 'signed' || $st === 'updated' ? ' ' . date_i18n('j M Y', (int) get_user_meta($uid, 'cc_form_done', true)) : ($st === 'unlocked' ? ' ' . date_i18n('j M', (int) get_user_meta($uid, 'cc_form_unlock', true)) : '');
        $o .= '<a class="rf-row rf-' . $st . '" href="' . esc_url(add_query_arg('a', $p->ID, $base)) . '"><b>' . esc_html($p->post_title) . '</b><span>' . $label[$st] . esc_html($when)
            . (cc_f_kind($uid) === 'update' ? ' · paper form on file' : '') . (!empty($m['u18']) && empty($m['coach']) ? ' · <em>under 18: countersign</em>' : '') . '</span></a>';
    }
    return $o . '</div></section>';
}, 10, 2);
function cc_f_btn($pid, $act, $text, $ghost = true) {
    return '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" class="rf-act"><input type="hidden" name="action" value="cc_form_admin"><input type="hidden" name="page" value="' . $pid . '">'
         . '<input type="hidden" name="act" value="' . $act . '">' . wp_nonce_field('cc_form_admin_' . $pid, '_wpnonce', false, false) . '<button class="btn ' . ($ghost ? 'btn-ghost' : 'btn-go') . '">' . esc_html($text) . '</button></form>';
}
function cc_f_one($pid, $base) {
    $uid = (int) get_post_meta($pid, 'cc_user', true); $st = cc_f_status($uid); $kind = cc_f_kind($uid);
    $m = json_decode((string) get_post_meta($pid, 'cc_form_signed', true), true) ?: [];
    $a = json_decode((string) get_post_meta($pid, 'cc_profile', true), true) ?: []; $pre = json_decode((string) get_post_meta($pid, 'cc_profile_prefill', true), true) ?: [];
    $o = '<p><a href="' . esc_url($base) . '">← All rider forms</a></p><section class="ath-s"><h2>' . cc_ath_icon('doc', 'ath-hic') . esc_html(get_post_field('post_title', $pid)) . '</h2><div class="rf-acts">';
    if (!empty($m['pdf_id'])) $o .= '<a class="btn btn-go" href="' . esc_url(wp_get_attachment_url($m['pdf_id'])) . '" target="_blank" rel="noopener">Signed PDF</a>';
    if (!empty($m['u18']) && empty($m['coach'])) $o .= cc_f_btn($pid, 'countersign', 'Countersign as coach (under 18)', false);
    $o .= $st === 'unlocked' ? cc_f_btn($pid, 'lock', 'Lock the hub again') : (!cc_f_open($uid) ? cc_f_btn($pid, 'unlock', 'Unlock hub') : '');
    if (!get_user_meta($uid, 'cc_form_done', true)) $o .= $kind === 'full' ? cc_f_btn($pid, 'paper', 'Paper form on file (short update instead)') : cc_f_btn($pid, 'full', 'Ask for the full form instead');
    else $o .= cc_f_btn($pid, 'reopen', 'Ask them to fill it in again');
    $o .= '</div><p class="av-lede">Status: <b>' . esc_html($st) . '</b>' . ($m ? ' · ' . esc_html(date_i18n('j M Y, H:i', $m['at'])) . ($m['name'] ? ' · signed by ' . esc_html($m['name']) : '') . ($m['guardian'] ? ' (guardian: ' . esc_html($m['guardian']) . ')' : '')
       . (!empty($m['coach']) ? ' · countersigned ' . esc_html(date_i18n('j M Y', $m['coach']['at'])) : '') : '') . '</p>';
    $show = $a ?: $pre;
    if (!$show) return $o . '<p>No answers yet.</p></section>';
    if (!$a) $o .= '<p class="rf-note">From their earlier paper form (imported). The athlete checks and updates these.</p>';
    return $o . cc_f_answers_html($show, $a ? ($m['kind'] ?? $kind) : 'full') . '</section>';
}
function cc_f_answers_html($a, $kind) {   // Matteo's view of the answers, grouped like the form, legal texts left out
    $o = '';
    foreach (cc_f_steps() as $st) {
        if ($st[2] !== 'both' && $st[2] !== $kind) continue;
        foreach ($st[3] as $pn) {
            if (($pn[0] ?? '') !== 'p' || (isset($pn['only']) && $pn['only'] !== $kind)) continue;
            $rows = '';
            foreach ($pn['fields'] as $f) {
                if (!array_key_exists($f[0], $a)) continue; $v = cc_f_val($f, $a[$f[0]]); if ($v === '') continue;
                $rows .= '<div class="rf-qa"><span>' . esc_html($f[2] ?: 'Usual week') . '</span><b>' . nl2br(esc_html($v)) . '</b></div>';
            }
            if ($rows) $o .= '<h3 class="av-sub">' . esc_html($pn[1]) . '</h3>' . $rows;
        }
    }
    return $o;
}
function cc_f_val($f, $v) {   // an answer in words (also used by the PDF)
    switch ($f[1]) {
        case 'week': $l = []; foreach (CC_AV_DAYS as $k => $n) $l[] = $n . ': ' . cc_av_day_text($v[$k] ?? ['h' => '', 'w' => []]); return implode("\n", $l);
        case 'checks': $o = $f['opts'] === 'days' ? CC_AV_DAYS : $f['opts']; return implode(', ', array_map(function ($x) use ($o) { return $o[$x] ?? $x; }, (array) $v));
        case 'radio': case 'select': return (string) ($f['opts'][$v] ?? $v);
        case 'yn': return $v === 'yes' ? 'Yes' : ($v === 'no' ? 'No' : '');
        case 'tick': return $v ? 'Agreed' : '';
        case 'date': return $v ? date_i18n('j M Y', strtotime($v . ' 12:00')) : '';
        default: return (string) $v;
    }
}

/* ---------- the signed PDF (A4, built-in fonts, signature picture). No library needed. ---------- */
class CC_Pdf {
    private $pages = []; private $s = ''; private $y = 0; private $img = null; private $imgs = [];
    const W = 595.28, H = 841.89, M = 48;
    private static $cw = [278,278,355,556,556,889,667,191,333,333,389,584,278,333,278,278,556,556,556,556,556,556,556,556,556,556,278,278,584,584,584,556,1015,667,667,722,722,667,611,778,722,278,500,667,556,833,722,778,667,778,722,667,611,722,667,944,667,667,611,278,278,278,469,556,333,556,556,500,556,556,278,556,556,222,222,500,222,833,556,556,556,556,333,500,278,556,500,722,500,500,500,334,260,334,584];
    function __construct() { $this->page(); }
    private function page() { if ($this->s !== '') $this->pages[] = $this->s; $this->s = ''; $this->y = self::H - self::M; }
    private static function enc($t) { $t = str_replace(['’', '‘', '“', '”', '–', '—', '…', '→'], ["'", "'", '"', '"', '-', '-', '...', '->'], $t);
        $c = function_exists('iconv') ? @iconv('UTF-8', 'Windows-1252//TRANSLIT', $t) : utf8_decode($t); return $c === false ? preg_replace('/[^\x20-\x7E]/', '?', $t) : $c; }
    private static function width($t, $size, $bold) { $w = 0; $n = strlen($t); for ($i = 0; $i < $n; $i++) { $o = ord($t[$i]); $w += ($o >= 32 && $o <= 126) ? self::$cw[$o - 32] : 556; } return $w * $size / 1000 * ($bold ? 1.07 : 1); }
    private function need($h) { if ($this->y - $h < self::M) $this->page(); }
    function text($t, $size = 10, $bold = false, $indent = 0, $gap = 3, $color = '0 0 0') {
        $max = self::W - 2 * self::M - $indent; $lh = $size * 1.32;
        foreach (preg_split("/\r?\n/", (string) $t) as $para) {
            $words = preg_split('/ +/', self::enc($para)); $line = '';
            foreach ($words as $w) { $try = $line === '' ? $w : "$line $w"; if (self::width($try, $size, $bold) > $max && $line !== '') { $this->line($line, $size, $bold, $indent, $lh, $color); $line = $w; } else $line = $try; }
            $this->line($line, $size, $bold, $indent, $lh, $color);
        }
        $this->y -= $gap;
    }
    private function line($t, $size, $bold, $indent, $lh, $color) { $this->need($lh); $this->y -= $lh;
        $this->s .= sprintf("BT %s rg /F%d %.1F Tf %.2F %.2F Td (%s) Tj ET\n", $color, $bold ? 2 : 1, $size, self::M + $indent, $this->y + $size * .25, str_replace(['\\', '(', ')', "\r"], ['\\\\', '\\(', '\\)', ''], $t)); }
    function rule() { $this->need(10); $this->y -= 6; $this->s .= sprintf("0.85 G 0.6 w %.2F %.2F m %.2F %.2F l S 0 G\n", self::M, $this->y, self::W - self::M, $this->y); $this->y -= 8; }
    function space($h) { $this->y -= $h; }
    function jpeg($data, $w) { $sz = @getimagesizefromstring($data); if (!$sz) return; $h = $w * $sz[1] / $sz[0]; $this->need($h + 4);
        $n = count($this->imgs); $this->imgs[] = [$data, $sz[0], $sz[1]]; $this->y -= $h; $this->s .= sprintf("q %.2F 0 0 %.2F %.2F %.2F cm /Im%d Do Q\n", $w, $h, self::M, $this->y, $n); $this->y -= 4; }
    function output() {
        $this->pages[] = $this->s; $o = []; $np = count($this->pages); $ni = count($this->imgs);
        // 1 catalog, 2 pages, 3 F1, 4 F2, then images, then page+content pairs
        $first = 5 + $ni; $kids = []; for ($i = 0; $i < $np; $i++) $kids[] = ($first + 2 * $i) . ' 0 R';
        $o[1] = '<< /Type /Catalog /Pages 2 0 R >>'; $o[2] = '<< /Type /Pages /Kids [' . implode(' ', $kids) . '] /Count ' . $np . ' >>';
        $o[3] = '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>'; $o[4] = '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>';
        $xo = ''; foreach ($this->imgs as $i => $im) { $o[5 + $i] = "<< /Type /XObject /Subtype /Image /Width {$im[1]} /Height {$im[2]} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length " . strlen($im[0]) . " >>\nstream\n" . $im[0] . "\nendstream"; $xo .= "/Im$i " . (5 + $i) . ' 0 R '; }
        foreach ($this->pages as $i => $c) { $pn = $first + 2 * $i; $z = gzcompress($c);
            $o[$pn] = '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 ' . self::W . ' ' . self::H . '] /Resources << /Font << /F1 3 0 R /F2 4 0 R >> /XObject << ' . $xo . '>> >> /Contents ' . ($pn + 1) . ' 0 R >>';
            $o[$pn + 1] = '<< /Length ' . strlen($z) . " /Filter /FlateDecode >>\nstream\n" . $z . "\nendstream"; }
        ksort($o); $pdf = "%PDF-1.4\n%\xE2\xE3\xCF\xD3\n"; $off = [];
        foreach ($o as $n => $body) { $off[$n] = strlen($pdf); $pdf .= "$n 0 obj\n$body\nendobj\n"; }
        $x = strlen($pdf); $pdf .= "xref\n0 " . (count($o) + 1) . "\n0000000000 65535 f \n"; foreach ($off as $v) $pdf .= sprintf("%010d 00000 n \n", $v);
        return $pdf . "trailer\n<< /Size " . (count($o) + 1) . " /Root 1 0 R >>\nstartxref\n$x\n%%EOF\n";
    }
}
function cc_f_html2text($h) {   // legal HTML -> plain text for the PDF (numbered lists kept)
    $n = 0;
    $h = preg_replace_callback('#<li[^>]*>#', function () use (&$n) { $n++; return "\n" . $n . '. '; }, preg_replace('#<(ol|ul)[^>]*>#', '', $h));
    $h = preg_replace('#<h3[^>]*>(.*?)</h3>#s', "\n\n[[B]]$1\n", $h);
    $h = preg_replace('#</p>|<br\s*/?>#', "\n", $h);
    $t = html_entity_decode(wp_strip_all_tags($h), ENT_QUOTES, 'UTF-8');
    return trim(preg_replace("/\n{3,}/", "\n\n", preg_replace('/[ \t]+/', ' ', $t)));
}
function cc_f_pdf($pid, $a, $m, $sig) {
    $p = new CC_Pdf();
    $p->text('Cigala Cycling Coaching', 9, true, 0, 0, '0.88 0.02 0');
    $p->text('Rider Information Form', 20, true, 0, 4);
    $p->text(get_post_field('post_title', $pid) . ' · signed ' . date_i18n('j F Y, H:i', $m['at']) . ($m['u18'] ? ' · under 18' : ''), 10, false, 0, 6, '0.35 0.35 0.35');
    $p->rule();
    foreach (cc_f_steps() as $st) {
        if ($st[2] !== 'both' && $st[2] !== 'full') continue;
        foreach ($st[3] as $pn) {
            if (($pn[0] ?? '') !== 'p' || $st[0] === 'sign' || (($pn['if'] ?? '') === 'u18' && !$m['u18'])) continue;
            $has = false; foreach ($pn['fields'] as $f) if (in_array($f[1], ['legal', 'group'], true) || (array_key_exists($f[0], $a) && cc_f_val($f, $a[$f[0]]) !== '')) $has = true;
            if (!$has) continue;   // no empty headings
            $p->space(6); $p->text($pn[1], 13, true, 0, 4);
            if (($pn[2] ?? '') === 'CC_F_MED_INTRO') $p->text(cc_f_html2text(CC_F_MED_INTRO), 8.5, false, 0, 4, '0.3 0.3 0.3');
            foreach ($pn['fields'] as $f) {
                if ($f[1] === 'legal') { $p->space(4); foreach (explode("\n", cc_f_html2text(constant($f['text']))) as $ln) { $b = strpos($ln, '[[B]]') === 0; $p->text($b ? substr($ln, 5) : $ln, $b ? 9.5 : 8.5, $b, 0, 1, $b ? '0 0 0' : '0.2 0.2 0.2'); } $p->space(4); continue; }
                if ($f[1] === 'group') { $p->text($f[2], 9.5, true, 0, 2); if (isset($f['text'])) $p->text(cc_f_html2text(constant($f['text'])), 8.5, false, 0, 3, '0.2 0.2 0.2'); continue; }
                if (in_array($f[1], ['sig'], true) || !array_key_exists($f[0], $a)) continue;
                $v = cc_f_val($f, $a[$f[0]]); if ($v === '' && $f[1] !== 'tick') continue;
                $p->text($f[2] ?: 'Usual week', 8.5, false, 0, 0, '0.35 0.35 0.35'); $p->text($v === '' ? '-' : $v, 10, true, 0, 5);
            }
        }
    }
    $p->space(10); $p->rule(); $p->text('Signed', 13, true, 0, 4);
    $p->text(($m['u18'] ? 'Parent / guardian / carer: ' . $m['guardian'] . ' (for the rider ' . $m['name'] . ')' : 'Name: ' . strtoupper($m['name'])), 10, true, 0, 3);
    if ($sig !== '') $p->jpeg($sig, 200);
    $p->text('Date: ' . date_i18n('j F Y, H:i', $m['at']) . ' · signed online in the Cigala Cycling athlete hub, logged in as ' . (get_userdata((int) get_post_meta($pid, 'cc_user', true))->user_email ?? '') . ' · IP ' . $m['ip'], 8, false, 0, 4, '0.35 0.35 0.35');
    if (!empty($m['coach'])) $p->text('Coach: ' . $m['coach']['name'] . ', countersigned ' . date_i18n('j F Y', $m['coach']['at']), 10, true, 0, 3);
    $p->text('Cigala Cycling Ltd · coaching.cigalacycling.com', 8, false, 0, 0, '0.5 0.5 0.5');
    return $p->output();
}

/* ---------- the form's script and look ---------- */
function cc_f_js() {
    return <<<'JS'
<script>(function(){
var R=document.getElementById('rf');if(!R)return;var F=R.querySelector('form'),W=JSON.parse(document.getElementById('rf-words').textContent),pv=R.dataset.preview==='1',kind=R.dataset.kind;
var steps=[].slice.call(R.querySelectorAll('.rf-step')),dots=[].slice.call(R.querySelectorAll('.rf-steps li')),i=0,timer=null,drawn=false;
function data(){var d={week:{}};R.querySelectorAll('input,select,textarea').forEach(function(e){if(!e.name)return;
  if(e.type==='checkbox'){if(e.closest('.rf-tick')){d[e.name]=e.checked?1:0;}else{d[e.name]=d[e.name]||[];if(e.checked)d[e.name].push(e.value);}}
  else if(e.type==='radio'){if(e.checked)d[e.name]=e.value;else if(!(e.name in d))d[e.name]='';}else d[e.name]=e.value;});
 R.querySelectorAll('.rf-week .av-day').forEach(function(x){var k=x.dataset.k;d.week[k]={h:x.querySelector('select').value,w:[].slice.call(x.querySelectorAll('.av-w[aria-pressed=true]')).map(function(b){return b.dataset.w;})};});return d;}
function age(){var v=(R.querySelector('[name=dob]')||{}).value;if(!v)return null;var b=new Date(v),n=new Date();return n.getFullYear()-b.getFullYear()-((n.getMonth()<b.getMonth()||(n.getMonth()===b.getMonth()&&n.getDate()<b.getDate()))?1:0);}
function cond(){var d=data(),a=age(),u18=a!==null&&a<18;var A=R.querySelector('.rf-age');if(A)A.textContent=a!==null?W.age+': '+a:'';
 R.querySelectorAll('.rf-opt').forEach(function(o){o.hidden=u18;});
 R.querySelectorAll('[data-if]').forEach(function(e){var c=e.dataset.if,s=true;
  if(c==='u18')s=u18;else if(c==='run')s=d.sport&&d.sport!=='cycling';else if(c==='notmale')s=d.gender!=='m';
  else if(c.indexOf('yes:')===0)s=c.slice(4).split(',').some(function(k){return d[k]==='yes';});e.hidden=!s;});}
function show(n){steps[i].classList.remove('on');i=n;steps[i].classList.add('on');dots.forEach(function(x,k){x.className=k<i?'done':(k===i?'now':'');});
 R.querySelector('.rf-sn').textContent=i+1;R.querySelector('.rf-st').textContent=steps[i].dataset.t;R.querySelector('.rf-back').style.visibility=i?'visible':'hidden';
 R.querySelector('.rf-next').textContent=i===steps.length-1?W.submit:W.next;R.querySelector('.rf-err').hidden=true;if(steps[i].dataset.k==='sign')pad();
 var t=R.getBoundingClientRect().top+scrollY-90;scrollTo({top:t,behavior:'smooth'});}
function post(action,extra){var b={action:action,data:data()};for(var k in extra)b[k]=extra[k];
 return fetch(R.dataset.api,{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-WP-Nonce':R.dataset.nonce},body:JSON.stringify(b)}).then(function(r){return r.json().then(function(j){if(!r.ok)throw j;return j;});});}
function autosave(){if(pv)return;clearTimeout(timer);timer=setTimeout(function(){var s=R.querySelector('.rf-saved');s.textContent=W.saving;post('save').then(function(){s.textContent=W.saved+' ✓';}).catch(function(){s.textContent=W.err;});},1200);}
F.addEventListener('input',function(){cond();autosave();});F.addEventListener('change',function(e){
 if(e.target.dataset.day){var r=e.target.value==='0';e.target.closest('.av-day').querySelectorAll('.av-w').forEach(function(b){b.disabled=r;if(r)b.setAttribute('aria-pressed','false');});}cond();autosave();});
F.addEventListener('click',function(e){var b=e.target.closest('.av-w');if(!b)return;b.setAttribute('aria-pressed',b.getAttribute('aria-pressed')!=='true');autosave();});
// signature
var c=R.querySelector('.rf-sig canvas'),x=c&&c.getContext('2d'),down=false,last=null;
function pad(){if(!c)return;var r=c.getBoundingClientRect(),d=window.devicePixelRatio||1;if(!r.width)return;c.width=r.width*d;c.height=r.height*d;x.setTransform(d,0,0,d,0,0);
 x.fillStyle='#fff';x.fillRect(0,0,r.width,r.height);x.lineWidth=2.4;x.lineCap='round';x.lineJoin='round';x.strokeStyle='#111';drawn=false;R.querySelector('.rf-sig-ph').hidden=false;}
if(c){var pt=function(e){var r=c.getBoundingClientRect();return[e.clientX-r.left,e.clientY-r.top];};
 c.addEventListener('pointerdown',function(e){down=true;last=pt(e);c.setPointerCapture(e.pointerId);});
 c.addEventListener('pointermove',function(e){if(!down)return;var p=pt(e);x.beginPath();x.moveTo(last[0],last[1]);x.lineTo(p[0],p[1]);x.stroke();last=p;if(!drawn){drawn=true;R.querySelector('.rf-sig-ph').hidden=true;}});
 ['pointerup','pointercancel'].forEach(function(t){c.addEventListener(t,function(){down=false;});});R.querySelector('.rf-clr').onclick=pad;}
R.querySelector('.rf-back').onclick=function(){if(i)show(i-1);};
R.querySelector('.rf-next').onclick=function(){if(i<steps.length-1){show(i+1);autosave();return;}
 clearTimeout(timer);var er=R.querySelector('.rf-err'),btn=this;if(pv){er.hidden=false;er.textContent=W.preview;return;}btn.disabled=true;
 post('submit',{sig:drawn?c.toDataURL('image/jpeg',.85):''}).then(function(){location.reload();}).catch(function(j){btn.disabled=false;er.hidden=false;er.textContent=j&&j.code==='cc_missing'?W.almost+': '+j.message+'.':W.err;});};
cond();show(0);scrollTo(0,0);
})();</script>
JS;
}
add_action('wp_head', function () {
    if (!is_page(CC_ATH_SLUG)) return;
    echo <<<'CSS'
<style id="cc-rider-form">
html .cc .rf { max-width: 760px; margin: 0 auto; }
html .cc .rf-hero { margin: 0 0 18px; } html .cc .rf-hero :is(h1, .rf-h1) { font-size: clamp(34px, 8vw, 54px); margin: 6px 0 0; }
html .cc .rf .bar { width: 40px; height: 3px; border-radius: 2px; background: #009a44; margin: 14px 0 16px; }
html .cc .rf-steps { position: sticky; top: 70px; z-index: 5; background: rgba(8,9,10,.94); backdrop-filter: blur(6px); padding: 10px 0; margin: 0 0 14px; border-bottom: 1px solid rgba(255,255,255,.08); }
html .cc .rf-steps ol { list-style: none; display: flex; gap: 4px; margin: 0 0 6px; padding: 0; } html .cc .rf-steps li { flex: 1; height: 5px; border-radius: 3px; background: rgba(255,255,255,.12); }
html .cc .rf-steps li.done { background: #009a44; } html .cc .rf-steps li.now { background: #34c46a; } html .cc .rf-steps p { margin: 0; font-size: 13px; color: var(--text-3); }
html .cc .rf-step { display: none; } html .cc .rf-step.on { display: block; }
html .cc .rf-panel { padding: 22px 18px 24px; border-radius: 16px; background: rgba(13,15,17,.92); border: 1px solid rgba(255,255,255,.09); margin: 0 0 16px; }
html .cc .rf-panel[hidden], html .cc .rf-f[hidden] { display: none; }
html .cc .rf-panel h2 { font-size: clamp(24px, 5vw, 32px); margin: 0; } html .cc .rf-sub { margin: -6px 0 18px; color: var(--text-3); font-size: 14px; }
html .cc .rf-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px 14px; } html .cc .rf-f { grid-column: 1 / -1; min-width: 0; } html .cc .rf-f.half { grid-column: auto; }
html .cc .rf label, html .cc .rf legend { display: block; font-size: 13.5px; font-weight: 600; color: var(--text); margin: 0 0 6px; padding: 0; } html .cc .rf fieldset { border: 0; margin: 0; padding: 0; min-width: 0; }
html .cc .rf small { font-weight: 500; color: var(--text-3); } html .cc .rf-age { display: block; margin-top: 4px; }
html .cc .rf :is(input[type=text], input[type=tel], input[type=email], input[type=date], input[type=number], select, textarea) { width: 100%; box-sizing: border-box; font: 16px var(--body); padding: 11px 13px; border-radius: 10px; border: 1px solid rgba(255,255,255,.18); background: #0b0d0f; color: #fff; color-scheme: dark; }
html .cc .rf textarea { resize: vertical; min-height: 88px; line-height: 1.5; } html .cc .rf :is(input, select, textarea):focus-visible { outline: 2px solid #009a44; outline-offset: 1px; }
html .cc .rf-chips { display: flex; flex-wrap: wrap; gap: 8px; } html .cc .rf-chip { position: relative; margin: 0 !important; } html .cc .rf-chip input { position: absolute; opacity: 0; inset: 0; margin: 0; cursor: pointer; }
html .cc .rf-chip span { display: inline-block; font: 600 13.5px var(--body); padding: 10px 15px; border-radius: 999px; border: 1px solid rgba(255,255,255,.16); color: var(--text-2); }
html .cc .rf-chip input:checked + span { background: #009a44; border-color: #009a44; color: #fff; } html .cc .rf-chip input:focus-visible + span { outline: 2px solid #34c46a; outline-offset: 2px; }
html .cc .rf-yn { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 10px 12px; border-radius: 10px; background: rgba(255,255,255,.03); border: 1px solid rgba(255,255,255,.07); }
html .cc .rf-yn legend { float: left; font-weight: 500; font-size: 14px; margin: 0; max-width: 70%; } html .cc .rf-seg { display: inline-flex; flex: none; margin-left: auto; border: 1px solid rgba(255,255,255,.16); border-radius: 999px; overflow: hidden; }
html .cc .rf-seg label { position: relative; margin: 0 !important; } html .cc .rf-seg input { position: absolute; opacity: 0; inset: 0; margin: 0; cursor: pointer; }
html .cc .rf-seg span { display: block; padding: 7px 14px; font: 600 13px var(--body); color: var(--text-3); } html .cc .rf-seg input:checked + span { background: #009a44; color: #fff; }
html .cc .rf-seg input[value=yes]:checked + span { background: #E10600; } html .cc .rf-seg input:focus-visible + span { outline: 2px solid #34c46a; outline-offset: -2px; }
html .cc .rf-legal { max-height: 300px; overflow: auto; padding: 14px 16px; border-radius: 12px; background: #0b0d0f; border: 1px solid rgba(255,255,255,.12); font-size: 13.5px; line-height: 1.55; color: var(--text-2); }
html .cc .rf-legal h3 { font: 700 12.5px var(--body); letter-spacing: .1em; text-transform: uppercase; color: var(--text); margin: 14px 0 6px; } html .cc .rf-legal h3:first-child { margin-top: 0; }
html .cc .rf-legal :is(p, li) { margin: 0 0 8px; } html .cc .rf-legal ol { padding-left: 20px; margin: 0; } html .cc .rf-legal a { color: #34c46a; word-break: break-all; }
html .cc .rf-tick { display: flex !important; gap: 12px; align-items: flex-start; font-weight: 500 !important; font-size: 14px !important; cursor: pointer; }
html .cc .rf-tick input { flex: none; width: 22px; height: 22px; margin: 1px 0 0; accent-color: #009a44; }
html .cc .rf-group { margin: 6px 0 0; font-weight: 600; color: var(--text); font-size: 14px; } html .cc .rf-group-t p { margin: 8px 0 0; font-size: 14px; }
html .cc .rf-week { display: grid; gap: 8px; }
html .cc .rf-sig { position: relative; border-radius: 12px; border: 1px dashed rgba(255,255,255,.3); overflow: hidden; } html .cc .rf-sig canvas { display: block; width: 100%; height: 160px; touch-action: none; cursor: crosshair; background: #fff; }
html .cc .rf-sig-ph { position: absolute; inset: auto 0 12px; text-align: center; font-size: 12.5px; color: #8a8f98; pointer-events: none; } html .cc .ath form .rf-clr { position: absolute; top: 8px; right: 8px; width: auto; margin: 0; padding: 6px 12px !important; font-size: 12.5px !important; background: rgba(8,9,10,.75); color: #fff; }
html .cc .rf-step[data-k=sign] .rf-panel { margin-bottom: 70px; }   /* room for the chat bubble */
html .cc .rf-date { font-size: 13px; color: var(--text-3); margin: 10px 0 0; } html .cc .rf-date b { color: var(--text); }
html .cc .rf-note { padding: 12px 14px; border-radius: 10px; background: rgba(0,154,68,.1); border: 1px solid rgba(52,196,106,.3); font-size: 13.5px; color: var(--text-2); margin: 0 0 16px; }
html .cc .rf-nav { display: flex; justify-content: space-between; gap: 12px; margin-top: 8px; } html .cc .ath form .rf-nav .btn { width: auto; flex: 1; margin: 0; } html .cc .rf-saved { font-size: 12.5px; color: var(--text-3); text-align: center; margin: 14px 0 0; }
html .cc .rf-err { margin: 0 0 12px; }
/* coach page */
html .cc .rf-list { display: grid; gap: 6px; } html .cc .rf-row { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 4px 14px; padding: 11px 14px; border-radius: 10px; background: rgba(255,255,255,.035); border: 1px solid rgba(255,255,255,.08); color: #fff; text-decoration: none; }
html .cc .rf-row span { color: var(--text-3); font-size: 13.5px; } html .cc .rf-row.rf-signed span, html .cc .rf-row.rf-updated span { color: #34c46a; } html .cc .rf-row.rf-waiting { border-color: rgba(225,6,0,.4); }
html .cc .rf-row em { color: #ff3d33; font-style: normal; } html .cc .rf-acts { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 14px; } html .cc .rf-act { margin: 0; }
html .cc .rf-qa { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr); gap: 4px 14px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,.06); font-size: 14px; }
html .cc .rf-qa span { color: var(--text-3); } html .cc .rf-qa b { color: #fff; font-weight: 500; }
@media (max-width: 640px) { html .cc .rf-grid { grid-template-columns: 1fr; } html .cc .rf-qa { grid-template-columns: 1fr; } html .cc .rf-steps { top: 60px; }
  html .cc .rf-yn { flex-wrap: wrap; } html .cc .rf-yn legend { max-width: 100%; } }
</style>
CSS;
});
