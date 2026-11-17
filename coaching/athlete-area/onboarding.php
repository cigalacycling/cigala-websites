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
// a legal text in the athlete's language when Matteo has one (form-legal-it.php: Italian), otherwise English
function cc_f_legal($name) { $l = strtoupper($GLOBALS['cc_f_lang'] ?? 'en'); return defined($name . '_' . $l) ? constant($name . '_' . $l) : constant($name); }
function cc_f_set_lang($uid) { $GLOBALS['cc_f_lang'] = $uid && function_exists('cc_ath_lang_code') ? cc_ath_lang_code($uid) : 'en'; }
const CC_F_COUNTRIES = ['af' => 'Afghanistan', 'ax' => 'Åland Islands', 'al' => 'Albania', 'dz' => 'Algeria', 'as' => 'American Samoa', 'ad' => 'Andorra', 'ao' => 'Angola', 'ai' => 'Anguilla', 'aq' => 'Antarctica', 'ag' => 'Antigua & Barbuda', 'ar' => 'Argentina', 'am' => 'Armenia', 'aw' => 'Aruba', 'au' => 'Australia', 'at' => 'Austria', 'az' => 'Azerbaijan', 'bs' => 'Bahamas', 'bh' => 'Bahrain', 'bd' => 'Bangladesh', 'bb' => 'Barbados', 'by' => 'Belarus', 'be' => 'Belgium', 'bz' => 'Belize', 'bj' => 'Benin', 'dy' => 'Benin', 'bm' => 'Bermuda', 'bt' => 'Bhutan', 'bo' => 'Bolivia', 'ba' => 'Bosnia & Herzegovina', 'bw' => 'Botswana', 'bv' => 'Bouvet Island', 'br' => 'Brazil', 'io' => 'British Indian Ocean Territory', 'vg' => 'British Virgin Islands', 'bn' => 'Brunei', 'bg' => 'Bulgaria', 'bf' => 'Burkina Faso', 'hv' => 'Burkina Faso', 'bi' => 'Burundi', 'kh' => 'Cambodia', 'cm' => 'Cameroon', 'ca' => 'Canada', 'cv' => 'Cape Verde', 'bq' => 'Caribbean Netherlands', 'ky' => 'Cayman Islands', 'cf' => 'Central African Republic', 'td' => 'Chad', 'cl' => 'Chile', 'cn' => 'China', 'cx' => 'Christmas Island', 'cc' => 'Cocos (Keeling) Islands', 'co' => 'Colombia', 'km' => 'Comoros', 'cg' => 'Congo - Brazzaville', 'cd' => 'Congo - Kinshasa', 'ck' => 'Cook Islands', 'cr' => 'Costa Rica', 'ci' => 'Côte d’Ivoire', 'hr' => 'Croatia', 'cu' => 'Cuba', 'cw' => 'Curaçao', 'cy' => 'Cyprus', 'cz' => 'Czechia', 'dk' => 'Denmark', 'dj' => 'Djibouti', 'dm' => 'Dominica', 'do' => 'Dominican Republic', 'ec' => 'Ecuador', 'eg' => 'Egypt', 'sv' => 'El Salvador', 'gq' => 'Equatorial Guinea', 'er' => 'Eritrea', 'ee' => 'Estonia', 'sz' => 'Eswatini', 'et' => 'Ethiopia', 'fk' => 'Falkland Islands', 'fo' => 'Faroe Islands', 'fj' => 'Fiji', 'fi' => 'Finland', 'fr' => 'France', 'gf' => 'French Guiana', 'pf' => 'French Polynesia', 'tf' => 'French Southern Territories', 'ga' => 'Gabon', 'gm' => 'Gambia', 'ge' => 'Georgia', 'de' => 'Germany', 'gh' => 'Ghana', 'gi' => 'Gibraltar', 'gr' => 'Greece', 'gl' => 'Greenland', 'gd' => 'Grenada', 'gp' => 'Guadeloupe', 'gu' => 'Guam', 'gt' => 'Guatemala', 'gg' => 'Guernsey', 'gn' => 'Guinea', 'gw' => 'Guinea-Bissau', 'gy' => 'Guyana', 'ht' => 'Haiti', 'hm' => 'Heard & McDonald Islands', 'hn' => 'Honduras', 'hk' => 'Hong Kong SAR China', 'hu' => 'Hungary', 'is' => 'Iceland', 'in' => 'India', 'id' => 'Indonesia', 'ir' => 'Iran', 'iq' => 'Iraq', 'ie' => 'Ireland', 'im' => 'Isle of Man', 'il' => 'Israel', 'it' => 'Italy', 'jm' => 'Jamaica', 'jp' => 'Japan', 'je' => 'Jersey', 'jo' => 'Jordan', 'kz' => 'Kazakhstan', 'ke' => 'Kenya', 'ki' => 'Kiribati', 'xk' => 'Kosovo', 'kw' => 'Kuwait', 'kg' => 'Kyrgyzstan', 'la' => 'Laos', 'lv' => 'Latvia', 'lb' => 'Lebanon', 'ls' => 'Lesotho', 'lr' => 'Liberia', 'ly' => 'Libya', 'li' => 'Liechtenstein', 'lt' => 'Lithuania', 'lu' => 'Luxembourg', 'mo' => 'Macao SAR China', 'mg' => 'Madagascar', 'mw' => 'Malawi', 'my' => 'Malaysia', 'mv' => 'Maldives', 'ml' => 'Mali', 'mt' => 'Malta', 'mh' => 'Marshall Islands', 'mq' => 'Martinique', 'mr' => 'Mauritania', 'mu' => 'Mauritius', 'yt' => 'Mayotte', 'mx' => 'Mexico', 'fm' => 'Micronesia', 'md' => 'Moldova', 'mc' => 'Monaco', 'mn' => 'Mongolia', 'me' => 'Montenegro', 'ms' => 'Montserrat', 'ma' => 'Morocco', 'mz' => 'Mozambique', 'mm' => 'Myanmar (Burma)', 'na' => 'Namibia', 'nr' => 'Nauru', 'np' => 'Nepal', 'nl' => 'Netherlands', 'nc' => 'New Caledonia', 'nz' => 'New Zealand', 'ni' => 'Nicaragua', 'ne' => 'Niger', 'ng' => 'Nigeria', 'nu' => 'Niue', 'nf' => 'Norfolk Island', 'kp' => 'North Korea', 'mk' => 'North Macedonia', 'mp' => 'Northern Mariana Islands', 'no' => 'Norway', 'om' => 'Oman', 'pk' => 'Pakistan', 'pw' => 'Palau', 'ps' => 'Palestinian Territories', 'pa' => 'Panama', 'pg' => 'Papua New Guinea', 'py' => 'Paraguay', 'pe' => 'Peru', 'ph' => 'Philippines', 'pn' => 'Pitcairn Islands', 'pl' => 'Poland', 'pt' => 'Portugal', 'pr' => 'Puerto Rico', 'qa' => 'Qatar', 're' => 'Réunion', 'ro' => 'Romania', 'ru' => 'Russia', 'rw' => 'Rwanda', 'ws' => 'Samoa', 'sm' => 'San Marino', 'st' => 'São Tomé & Príncipe', 'cq' => 'Sark', 'sa' => 'Saudi Arabia', 'sn' => 'Senegal', 'rs' => 'Serbia', 'sc' => 'Seychelles', 'sl' => 'Sierra Leone', 'sg' => 'Singapore', 'sx' => 'Sint Maarten', 'sk' => 'Slovakia', 'si' => 'Slovenia', 'sb' => 'Solomon Islands', 'so' => 'Somalia', 'za' => 'South Africa', 'gs' => 'South Georgia & South Sandwich Islands', 'kr' => 'South Korea', 'ss' => 'South Sudan', 'es' => 'Spain', 'lk' => 'Sri Lanka', 'bl' => 'St. Barthélemy', 'sh' => 'St. Helena', 'kn' => 'St. Kitts & Nevis', 'lc' => 'St. Lucia', 'mf' => 'St. Martin', 'pm' => 'St. Pierre & Miquelon', 'vc' => 'St. Vincent & Grenadines', 'sd' => 'Sudan', 'sr' => 'Suriname', 'sj' => 'Svalbard & Jan Mayen', 'se' => 'Sweden', 'ch' => 'Switzerland', 'sy' => 'Syria', 'tw' => 'Taiwan', 'tj' => 'Tajikistan', 'tz' => 'Tanzania', 'th' => 'Thailand', 'tl' => 'Timor-Leste', 'tg' => 'Togo', 'tk' => 'Tokelau', 'to' => 'Tonga', 'tt' => 'Trinidad & Tobago', 'tn' => 'Tunisia', 'tr' => 'Türkiye', 'tm' => 'Turkmenistan', 'tc' => 'Turks & Caicos Islands', 'tv' => 'Tuvalu', 'um' => 'U.S. Outlying Islands', 'vi' => 'U.S. Virgin Islands', 'ug' => 'Uganda', 'ua' => 'Ukraine', 'ae' => 'United Arab Emirates', 'gb' => 'United Kingdom', 'gb-eng' => 'England', 'gb-nir' => 'Northern Ireland', 'gb-sct' => 'Scotland', 'gb-wls' => 'Wales', 'us' => 'United States', 'uy' => 'Uruguay', 'uz' => 'Uzbekistan', 'nh' => 'Vanuatu', 'vu' => 'Vanuatu', 'va' => 'Vatican City', 've' => 'Venezuela', 'vd' => 'Vietnam', 'vn' => 'Vietnam', 'wf' => 'Wallis & Futuna', 'eh' => 'Western Sahara', 'ye' => 'Yemen', 'zm' => 'Zambia', 'rh' => 'Zimbabwe', 'zw' => 'Zimbabwe'];   // nationality (ISO codes); the form shows the names in the athlete's language (browser Intl)
const CC_F_YN = ['Frequent or severe headaches', 'Dizziness or fainting spells', 'Heart or vascular problems', 'High or low blood pressure', 'Asthma or lung disease',
    'Epilepsy or seizures', 'Diabetes', 'Stroke', 'Muscular disorders or complaints', 'Chest pains', 'Back pains', 'Lower limb or joint problems',
    '(Women only) Are you or have you been pregnant in the past year?'];
// the app question: only for an athlete not linked to Vekta and not on TrainingPeaks (set before the form is shown or checked)
function cc_f_askapp($uid, $pid) { $GLOBALS['cc_f_askapp'] = $uid && $pid && !get_user_meta($uid, 'cc_vekta_id', true) && !(function_exists('cc_ath_tp') && cc_ath_tp($pid)); }
function cc_f_steps() {
    $s = cc_f_steps_all();
    // not set (coach view, PDF): every field, so an answer given is shown
    if (isset($GLOBALS['cc_f_askapp']) && !$GLOBALS['cc_f_askapp']) foreach ($s as &$st) foreach ($st[3] as &$pn) if (isset($pn['fields'])) $pn['fields'] = array_values(array_filter($pn['fields'], function ($f) { return empty($f['askapp']); }));
    return $s;
}
function cc_f_steps_all() {
    $yn = []; foreach (CC_F_YN as $i => $q) $yn[] = ['yn' . $i, 'yn', $q, 'if' => $i === 12 ? 'notmale' : null, 'req' => $i === 12 ? 'shown' : 1];
    $med = []; foreach (['cyc' => 'Cycling', 'run' => 'Running', 'swim' => 'Swimming', 'gym' => 'Gym', 'core' => 'Core & Stretching', 'hike' => 'Hiking'] as $k => $a) $med[] = ['med_' . $k, 'text', $a, 'ph' => 'N/A if nothing', 'half' => 1, 'if' => 'yes:med_any', 'req' => 'shown'];
    return [
      ['about', 'About you', 'both', [
        ['p', 'About you', null, 'fields' => [
          ['first', 'text', 'First name', 'req' => 1, 'half' => 1, 'ac' => 'given-name'], ['last', 'text', 'Surname', 'req' => 1, 'half' => 1, 'ac' => 'family-name'],
          ['dob', 'date', 'Date of birth', 'req' => 'full', 'half' => 1, 'only' => 'full'], ['gender', 'radio', 'Gender', 'opts' => ['f' => 'Female', 'm' => 'Male'], 'half' => 1, 'only' => 'full', 'req' => 1],
          ['nat', 'select', 'Nationality', 'opts' => CC_F_COUNTRIES, 'req' => 1, 'half' => 1, 'ac' => 'country'],   // Matteo 17 Nov: the flag in his coach list
          ['phone', 'tel', 'Mobile', 'req' => 1, 'half' => 1, 'ac' => 'tel'], ['phone_home', 'tel', 'Home telephone', 'opt' => 1, 'half' => 1],
          ['email', 'email', 'Email', 'req' => 1, 'ac' => 'email'],
          ['photo', 'photo', 'A photo of you', 'only' => 'full'],   // optional, photo.php
          ['address', 'text', 'Address', 'opt' => 'adult', 'req' => 'u18', 'ac' => 'street-address', 'only' => 'full'], ['postcode', 'text', 'Postcode / Eircode', 'opt' => 'adult', 'req' => 'u18', 'half' => 1, 'ac' => 'postal-code', 'only' => 'full'],
          ['team', 'text', 'Cycling club, group or team', 'ph' => 'or N/A', 'half' => 1, 'req' => 1],
          ['sport', 'checks', 'Sport', 'opts' => ['cycling' => 'Cycling', 'triathlon' => 'Triathlon', 'running' => 'Running', 'swimming' => 'Swimming', 'other' => 'Other'], 'only' => 'full', 'req' => 1],
          ['sport_other', 'text', 'Which other sport?', 'if' => 'has:sport=other', 'only' => 'full'],
          // Matteo 17 Nov: new athletes choose their training app (only asked when they are not on Vekta or TrainingPeaks yet)
          ['app', 'radio', 'Which app will you train with?', 'opts' => ['vekta' => 'Vekta (recommended)', 'trainingpeaks' => 'TrainingPeaks'], 'only' => 'full', 'req' => 1, 'askapp' => 1],
        ]],
        ['p', 'Emergency contact', 'Someone I can call in an emergency.', 'fields' => [
          ['ec_first', 'text', 'First name', 'req' => 1, 'half' => 1], ['ec_last', 'text', 'Surname', 'req' => 1, 'half' => 1],
          ['ec_rel', 'text', 'Relationship to you', 'ph' => 'e.g. partner, parent', 'half' => 1, 'req' => 1], ['ec_mobile', 'tel', 'Mobile', 'req' => 1, 'half' => 1],
          ['ec_home', 'tel', 'Home telephone', 'opt' => 1, 'half' => 1], ['ec_work', 'tel', 'Work telephone', 'opt' => 1, 'half' => 1],
        ]]]],
      ['numbers', 'Your numbers', 'both', [
        ['p', 'Your numbers', 'Only what you know. Leave anything else empty: we will test it together.', 'fields' => [
          ['height', 'number', 'Height (cm)', 'half' => 1, 'req' => 1], ['weight', 'number', 'Weight (kg)', 'half' => 1, 'req' => 1], ['weight_goal', 'number', 'Ideal race weight (kg)', 'opt' => 1],
          ['ftp', 'number', 'Threshold power, FTP or CP (W)', 'opt' => 1, 'half' => 1], ['ftp_date', 'date', 'Date of that test', 'opt' => 1, 'half' => 1],
          ['thr', 'number', 'Threshold heart rate (bpm)', 'opt' => 1, 'half' => 1], ['thr_date', 'date', 'Date of that test', 'opt' => 1, 'half' => 1],
          ['pace', 'text', 'Running threshold pace (min/km)', 'opt' => 1, 'ph' => 'e.g. 4:30', 'half' => 1, 'if' => 'run'], ['pace_date', 'date', 'Date of that test', 'opt' => 1, 'half' => 1, 'if' => 'run'],
          ['kit', 'checks', 'Do you have a heart rate monitor, a power meter, a cadence sensor, a turbo trainer, a gym membership? Tap what you have.',
             'opts' => ['hr' => 'Heart rate monitor', 'power' => 'Power meter', 'cadence' => 'Cadence sensor', 'turbo' => 'Turbo trainer', 'gym' => 'Gym membership']],
          ['setup_notes', 'textarea', 'Any notes about your setup?', 'opt' => 1, 'ph' => 'e.g. which turbo trainer, power meter on which bike, a gym at home'],
        ]]]],
      ['week', 'Your week', 'both', [
        ['p', 'Your usual week', 'Day of the week and hours available. This fills in “My availability” in your hub, so you only do it once.', 'fields' => [
          ['weekhint', 'group', 'If any time of day suits you, leave morning, lunch and evening off. Two slots on the same day? Tap both.'],
          ['week', 'week', '', 'req' => 1],
          ['rest', 'checks', 'Day or days you would prefer to have as REST', 'opts' => 'days'],
          ['hours_week', 'text', 'How many hours a week do you normally train?', 'ph' => 'e.g. 6h', 'half' => 1, 'req' => 1],
          ['hours_day', 'text', 'How many hours a day do you normally train?', 'ph' => 'e.g. 1h, 1h 30', 'half' => 1, 'req' => 1],
          ['recent', 'textarea', 'Any notes about your normal training week?', 'opt' => 1, 'ph' => 'e.g. 1h turbo Tue and Thu, club spin Sunday 100 km'],
          ['with', 'checks', 'Do you train alone or with someone?', 'opts' => ['alone' => 'Alone', 'club' => 'Club spins', 'friends' => 'With friends', 'indoor' => 'Indoor (Zwift etc.)'], 'only' => 'full', 'req' => 1],
          ['winter', 'checks', 'What other sports could you do in the winter?', 'opts' => ['gym' => 'Gym', 'running' => 'Running', 'swimming' => 'Swimming', 'hiking' => 'Hiking', 'mtb' => 'MTB', 'cx' => 'Cyclocross'], 'only' => 'full', 'req' => 1],
          ['with_more', 'text', 'Anything else about training with others or winter sports?', 'opt' => 1, 'only' => 'full'],
        ]]]],
      ['goals', 'Your goals', 'both', [
        ['p', 'Your goals', null, 'fields' => [
          ['goal_short', 'textarea', 'Short-term goal (1 year)', 'req' => 1], ['goal_long', 'textarea', 'Long-term goal (more than 1 year)', 'req' => 1],
          ['events', 'events', 'If you race or do any events, list them here with their priority: A = your main goal, B = important, C = for training or fun. League and club races too.'],
        ]],
        ['p', 'You as a rider', null, 'only' => 'full', 'fields' => [
          ['since', 'text', 'When did you start your discipline or sport?', 'req' => 'full'],
          ['motiv', 'radio', 'Are you motivated?', 'opts' => ['4' => 'Highly', '3' => 'Quite', '2' => 'Not really', '1' => 'Not at all'], 'req' => 'full'],
          ['motiv_why', 'textarea', 'Tell me more', 'opt' => 1],
          ['swot', 'group', 'Your SWOT: a quick look at you as an athlete. A few words for each is enough.'],
          ['strengths', 'textarea', 'Strengths: what you are good at', 'ph' => 'e.g. climbing, consistency, early mornings, a supportive family', 'req' => 'full'],
          ['weak', 'textarea', 'Weaknesses: what holds you back or you would like to improve', 'ph' => 'e.g. sprinting, never stretching, fuelling on long rides', 'req' => 'full'],
          ['opps', 'textarea', 'Opportunities: what could help you improve', 'ph' => 'e.g. more time in winter, a turbo at home, a training camp, riding with a faster group', 'req' => 'full'],
          ['threats', 'textarea', 'Threats: what could stop you or get in the way', 'ph' => 'e.g. work travel, family commitments, a recurring injury, bad weather', 'req' => 'full'],
        ]]]],
      ['health', 'Health', 'full', [
        ['note', 'Your health answers are private: only you and Matteo can see them.'],
        ['p', 'Medical history', 'CC_F_MED_INTRO', 'fields' => array_merge(
          [['med_any', 'yn', 'Any medical history that may prevent or be affected by your participating in cycling, running, swimming, gym, core & stretching or hiking?', 'req' => 1],
           ['med', 'group', 'Please state, for each activity:', 'if' => 'yes:med_any']], $med, [
          ['inj_any', 'yn', 'Any previous or recent injuries or disabilities that may prevent or be affected by you participating in the coaching program?', 'req' => 1],
          ['injuries', 'textarea', 'Please state:', 'if' => 'yes:inj_any', 'req' => 'shown'],
          ['disab', 'yn', 'Have you any disabilities that may prevent you taking part in sport activity?', 'req' => 1],
          ['ops', 'yn', 'Have you had any operations or surgical procedures that would affect your ability to cycle at high intensity?', 'req' => 1],
          ['allerg', 'yn', 'Do you have any allergies?', 'req' => 1], ['docno', 'yn', 'Has your doctor ever advised you not to take part in exercise?', 'req' => 1],
          ['yn2_details', 'textarea', 'Please give details', 'if' => 'yes:disab,ops,allerg,docno', 'req' => 'shown'],
          ['ynh', 'group', 'Do you have or have you ever had the following?']], $yn, [
          ['yn_details', 'textarea', 'If you have answered yes to any of the questions above, please give details:', 'if' => 'yes:yn0,yn1,yn2,yn3,yn4,yn5,yn6,yn7,yn8,yn9,yn10,yn11,yn12', 'req' => 'shown'],
        ])],
        ['p', 'Food and diet', null, 'fields' => [
          ['diet_plan', 'textarea', 'Do you currently follow a diet plan?', 'req' => 1], ['diet_req', 'text', 'Have you any dietary requirements?', 'req' => 1],
          ['diet_score', 'select', 'How would you rate your diet from 1 to 10?', 'opts' => array_combine(range(1, 10), range(1, 10)), 'req' => 1],
          ['lose', 'yn', 'Do you feel you need to lose weight to improve your cycling performance?', 'req' => 1], ['lose_more', 'text', 'Tell me more', 'opt' => 1],
          ['supps_any', 'yn', 'Are you currently taking tablets to aid immune function, such as multivitamins or supplements?', 'req' => 1],
          ['supps', 'textarea', 'Please list them:', 'if' => 'yes:supps_any', 'req' => 'shown'],
        ]]]],
      ['healthupd', 'Health', 'update', [
        ['p', 'Anything new?', 'Since your last form: a new injury, illness, operation or medication? Your answers are private: only you and Matteo can see them.', 'fields' => [
          ['health_new', 'yn', 'Anything new since your form?', 'req' => 1], ['health_new_details', 'textarea', 'Please give details', 'if' => 'yes:health_new', 'req' => 'shown'],
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
                if (in_array($f[1], ['group', 'legal', 'sig', 'photo'], true)) continue;
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
            case 'events': $out[$k] = function_exists('cc_g_clean') ? cc_g_clean(['events' => is_array($v) ? $v : []])['events'] : []; break;
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
// a field's condition (same rules as the browser script): u18, run, notmale, yes:a,b (any is yes), has:key=value
function cc_f_cond($c, $a, $u18) {
    if (!$c) return true;
    if ($c === 'u18') return $u18;
    if ($c === 'run') return (bool) array_intersect((array) ($a['sport'] ?? []), ['running', 'triathlon']);
    if ($c === 'notmale') return ($a['gender'] ?? '') !== 'm';
    if (strpos($c, 'yes:') === 0) { foreach (explode(',', substr($c, 4)) as $k) if (($a[$k] ?? '') === 'yes') return true; return false; }
    if (strpos($c, 'has:') === 0) { [$k, $v] = explode('=', substr($c, 4)); return in_array($v, (array) ($a[$k] ?? []), true); }
    return true;
}
// what is missing before the form can be submitted (labels), given the answers
function cc_f_missing($a, $kind, $sig_ok) {
    $u18 = $kind === 'full' && ($age = cc_f_age($a['dob'] ?? '')) !== null && $age < 18;
    $miss = [];
    foreach (cc_f_fields($kind) as $k => $f) {
        $r = $f['req'] ?? 0;
        if (!cc_f_cond($f['if'] ?? null, $a, $u18)) continue;   // hidden questions are never required
        $need = $r === 1 || $r === 'shown' || ($r === 'full' && $kind === 'full') || ($r === 'u18' && $u18);
        if ($f['_panel_if'] === 'u18' && !$u18) $need = false;
        $empty = $f[1] === 'week' ? in_array('', array_map(function ($d) { return (string) ($d['h'] ?? ''); }, (array) $a[$k]), true) : ($a[$k] === '' || $a[$k] === 0 || $a[$k] === [] || $a[$k] === null);
        if ($need && $empty) $miss[] = $f[2] !== '' ? $f[2] : 'Your usual week';
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
    if ($preview) $GLOBALS['cc_f_askapp'] = true; else cc_f_askapp($uid, $pid);
    $GLOBALS['cc_f_pid'] = $preview ? 0 : (int) $pid;   // the photo field saves to this page
    if ($preview && isset($_GET['flang']) && preg_match('/^[a-z]{2}$/', $_GET['flang'])) $GLOBALS['cc_f_lang'] = $_GET['flang'];   // Matteo previews a language
    $draft = $preview ? [] : (json_decode((string) get_user_meta($uid, 'cc_form_draft', true), true) ?: []);
    $pre = $preview ? [] : (json_decode((string) get_post_meta($pid, 'cc_profile_prefill', true), true) ?: []);
    $prof = $preview ? [] : (json_decode((string) get_post_meta($pid, 'cc_profile', true), true) ?: []);   // earlier answers, when asked again
    $vals = array_merge(['first' => $u ? $u->first_name : '', 'last' => $u ? $u->last_name : '', 'email' => $u ? $u->user_email : ''], $prof, $pre, $draft);
    if (!$preview && ($av = cc_av_get($pid)) && empty($draft['week'])) $vals['week'] = $av['week'];
    if (!$preview && empty($vals['nat']) && ($cn = (string) get_post_meta($pid, 'cc_nat', true)) !== '') $vals['nat'] = $cn;   // set by Matteo or the laptop (pc-api.php): the athlete just confirms it
    $steps = array_values(array_filter(cc_f_steps(), function ($s) use ($kind) { return $s[2] === 'both' || $s[2] === $kind; }));
    $n = count($steps);
    $first = $u ? ($u->first_name ?: $u->display_name) : '';
    $o = '<div class="rf" id="rf" data-lang="' . esc_attr($GLOBALS['cc_f_lang'] ?? 'en') . '" data-kind="' . $kind . '" data-preview="' . ($preview ? 1 : 0) . '" data-api="' . esc_url(rest_url('cc/v1/form')) . '" data-nonce="' . esc_attr(wp_create_nonce('wp_rest')) . '">'
       . '<div class="rf-hero"><p class="eyebrow">' . esc_html(cc_f($kind === 'full' ? 'Welcome to Cigala Cycling Coaching' : 'Athlete hub')) . '</p>'
       . ($preview ? '<h2 class="rf-h1">' : '<h1>') . esc_html(cc_f($kind === 'full' ? 'Tell me about you' : 'Update your details')) . ($preview ? '</h2>' : '</h1>') . '<div class="bar"></div>'
       . '<p class="ath-lede">' . esc_html($kind === 'full'
            ? cc_f('This helps me build your plan around your life and your goals. It takes about 15 minutes, and you can stop and come back: your answers are saved as you go.')
            : sprintf(cc_f('Hi %s, your hub has a new home. Before it opens, take 3 minutes to update your details, so your plan starts from where you are now. Your answers are saved as you go.'), $first)) . '</p>'
       . '<a class="ath-out" href="' . esc_url(wp_logout_url(home_url('/' . CC_ATH_SLUG . '/'))) . '">' . esc_html(cc_t('Log out')) . '</a>' . (!$preview && function_exists('cc_ath_lang_switch') ? cc_ath_lang_switch() : '') . '</div>'
       . ($preview ? '<div class="rf-note rf-pv"><b>' . esc_html(cc_f('Coach preview.')) . '</b> ' . esc_html(cc_f('This is only to look at the form: answers are not saved and it cannot be submitted. To try it for real, log in as a test athlete.')) . '</div>' : '')
       . '<div class="rf-steps"><ol aria-hidden="true">' . str_repeat('<li></li>', $n) . '</ol><p>' . esc_html(cc_f('Step')) . ' <b class="rf-sn">1</b> / ' . $n . ' · <b class="rf-st"></b></p></div><form novalidate>';
    foreach ($steps as $i => $st) {
        $o .= '<section class="rf-step' . ($i ? '' : ' on') . '" data-t="' . esc_attr(cc_f($st[1])) . '" data-k="' . $st[0] . '">';
        if ($st[0] === 'agree' && ($GLOBALS['cc_f_lang'] ?? 'en') !== 'en' && !defined('CC_F_WAIVER_' . strtoupper($GLOBALS['cc_f_lang']))) $o .= '<div class="rf-note">' . esc_html(cc_f('The agreements are in English: that is the version you sign. Message me if anything is unclear.')) . '</div>';
        foreach ($st[3] as $pn) {
            if ($pn[0] === 'note') { $o .= '<div class="rf-note">' . esc_html(cc_f($pn[1])) . '</div>'; continue; }
            if (isset($pn['only']) && $pn['only'] !== $kind) continue;
            $sub = $pn[2] ?? null; $sub = $sub && defined($sub) ? cc_f_legal($sub) : ($sub ? esc_html(cc_f($sub)) : '');
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
            'age' => cc_f('Age'), 'preview' => cc_f('This is the coach preview, so nothing is saved or sent. Everything else is ready: an athlete would now sign and submit.'),
            'step' => cc_f('Please answer the questions marked in red:')]) . '</script>' . cc_f_js();
    return $o;
}
function cc_f_field($f, $v, $kind) {
    [$k, $t, $label] = $f; $label = $label !== '' ? esc_html(cc_f($label)) : '';
    $opt = ($f['opt'] ?? 0) === 1 ? ' <small>' . esc_html(cc_f('(optional)')) . '</small>' : (($f['opt'] ?? 0) === 'adult' ? ' <small class="rf-opt">' . esc_html(cc_f('(optional)')) . '</small>' : '');
    if ($t === 'week' && $label === '') $f[2] = 'Your usual week: a time or “Rest day” for every day';
    $rq = $f['req'] ?? 0; $rq = ($rq === 1 || $rq === 'shown' || ($rq === 'full' && $kind === 'full')) ? '1' : ($rq === 'u18' ? 'u18' : '');
    $wrap = function ($inner, $cls = '') use ($f, $rq) { return '<div class="rf-f' . (!empty($f['half']) ? ' half' : '') . $cls . '"' . ($rq ? ' data-req="' . $rq . '" data-label="' . esc_attr(cc_f($f[2])) . '"' : '')
        . (!empty($f['if']) ? ' data-if="' . esc_attr($f['if']) . '" hidden' : '') . '>' . $inner . '</div>'; };
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
            // Matteo 17 Nov: plain elements (a fieldset/legend was drawn on the box's edge on some phones)
            return $wrap('<div class="rf-yn" role="radiogroup" aria-labelledby="q-' . esc_attr($k) . '"><span class="rf-ynq" id="q-' . esc_attr($k) . '">' . $label . '</span><div class="rf-seg">' . $c . '</div></div>', ' full');
        case 'tick': return $wrap('<label class="rf-tick"><input type="checkbox" name="' . $k . '" value="1"' . ($v ? ' checked' : '') . '><span>' . $label . '</span></label>', ' full');
        case 'group': return $wrap('<p class="rf-group">' . $label . '</p>' . (isset($f['text']) ? '<div class="rf-group-t">' . cc_f_legal($f['text']) . '</div>' : ''), ' full');
        case 'legal': return $wrap('<div class="rf-legal" tabindex="0" role="region" aria-label="' . esc_attr($label) . '">' . cc_f_legal($f['text']) . '</div><p class="rf-scrollhint">' . esc_html(cc_f('Scroll to the end to agree.')) . '</p>', ' full');
        case 'week':
            $w = is_array($v) ? $v : []; $g = '<div class="av-week rf-week">';
            foreach (CC_AV_DAYS as $dk => $dn) { $d = $w[$dk] ?? ['h' => '', 'w' => []]; $s = '';
                foreach (CC_AV_HOURS as $hv => $hl) $s .= '<option value="' . $hv . '"' . ((string) $d['h'] === (string) $hv ? ' selected' : '') . '>' . esc_html(cc_f($hl)) . '</option>';
                $g .= '<div class="av-day" data-k="' . $dk . '"><label class="av-dn" for="rf-h-' . $dk . '">' . esc_html(cc_f($dn)) . '</label><select id="rf-h-' . $dk . '" data-day="' . $dk . '">' . $s . '</select><div class="av-when">';
                foreach (CC_AV_WHEN as $wk => $wl) $g .= '<button type="button" class="av-w" data-day="' . $dk . '" data-w="' . $wk . '" aria-pressed="' . (in_array($wk, $d['w'] ?? [], true) ? 'true' : 'false') . '"' . ($d['h'] === '0' ? ' disabled' : '') . '>' . esc_html(cc_f($wl)) . '</button>';
                $g .= '</div></div>'; }
            return $wrap($g . '</div>', ' full');
        case 'events':
            $ev = is_array($v) ? array_values($v) : [];
            return $wrap('<fieldset><legend>' . $label . '</legend><div class="rf-evs" data-words="' . esc_attr(wp_json_encode(['ev' => cc_f('Event'), 'date' => cc_f('Date'), 'prio' => cc_f('Priority'), 'rm' => cc_f('Remove')])) . '">'
                . '<script type="application/json" class="rf-ev-data">' . wp_json_encode($ev) . '</script></div><button type="button" class="btn btn-ghost rf-ev-add">' . esc_html(cc_f('+ Add an event')) . '</button></fieldset>', ' full');
        case 'photo':   // Matteo 17 Nov: optional photo, saved straight away (photo.php), not part of the form answers
            if (!function_exists('cc_ph_widget')) return '';
            $pp = (int) ($GLOBALS['cc_f_pid'] ?? 0);
            return $wrap('<div class="rf-photo">' . ($pp ? cc_ph_widget($pp, 96, true) : '') . '<div><p class="rf-photo-t">' . esc_html(cc_ph_w('form')) . '</p><p class="rf-photo-h">' . esc_html(cc_ph_w('form_hint')) . '</p></div></div>' . cc_ph_assets(), ' full');
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
    cc_f_askapp($uid, $pid);
    $a = cc_f_clean($r->get_param('data'), $kind);
    if ($r->get_param('action') !== 'submit') { update_user_meta($uid, 'cc_form_draft', wp_slash(wp_json_encode($a))); return ['ok' => true, 'saved' => time()]; }
    $sig = ''; $raw = (string) $r->get_param('sig');
    if ($kind === 'full' && preg_match('#^data:image/jpeg;base64,([A-Za-z0-9+/=]+)$#', $raw, $m)) { $sig = base64_decode($m[1]); if (strlen($sig) < 800 || strlen($sig) > 600000 || !@getimagesizefromstring($sig)) $sig = ''; }
    cc_f_set_lang($uid);   // the message below in the athlete's language
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
    // Matteo 17 Nov: their training app. TrainingPeaks: the hub switches to that view; Vekta: the laptop sends Vekta's invitation (vekta-pending)
    if (($a['app'] ?? '') === 'trainingpeaks') {
        update_post_meta($pid, 'cc_tp', 1);
        $nm = get_the_title($pid); $u = get_userdata($uid);
        if (function_exists('cc_av_notify_to') && cc_av_notify_to()) wp_mail(cc_av_notify_to(), $nm . ' chose TrainingPeaks', '<p><b>' . esc_html($nm) . '</b> chose <b>TrainingPeaks</b> in the rider form. Their hub now shows the TrainingPeaks view.</p><p>To do: invite them in TrainingPeaks (' . esc_html($u ? $u->user_email : '') . ').</p>',
            ['Content-Type: text/html; charset=UTF-8'] + ($u && is_email($u->user_email) ? [1 => 'Reply-To: ' . $nm . ' <' . $u->user_email . '>'] : []));
    }
    elseif (($a['app'] ?? '') === 'vekta' && !get_user_meta($uid, 'cc_vekta_id', true)) update_post_meta($pid, 'cc_vekta_pending', $now);
    cc_f_mail($uid, $pid, $profile, $meta, $pdf);
    if (function_exists('cc_push_coaches')) cc_push_coaches(($kind === 'full' ? 'Rider form signed: ' : 'Details updated: ') . get_the_title($pid), ($a['app'] ?? '') === 'trainingpeaks' ? 'Chose TrainingPeaks' : '', add_query_arg(['board' => 'forms', 'a' => $pid], home_url('/' . CC_ATH_SLUG . '/')), 'cc-form');
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
       . ($full ? '<p style="font-size:13px;color:#555">The signed PDF is attached and saved in their private area.</p>' : '')
       . '<p style="margin:20px 0 0"><a href="' . esc_url($board) . '" style="display:inline-block;padding:12px 20px;border-radius:8px;background:#009a44;color:#fff;font-weight:600;text-decoration:none">Open their answers</a></p></div>';
    $hd = ['Content-Type: text/html; charset=UTF-8'];
    if ($u && is_email($u->user_email)) $hd[] = 'Reply-To: ' . $name . ' <' . $u->user_email . '>';
    if (function_exists('cc_ath_coach_wrap')) $h = cc_ath_coach_wrap($h);
    if (cc_av_notify_to()) wp_mail(cc_av_notify_to(), ($full ? 'Rider form signed: ' : 'Details updated: ') . $name, $h, $hd, $tmp ? [$tmp] : []);
    if ($full && $u && is_email($u->user_email)) {   // the athlete's own copy
        cc_f_set_lang($uid);
        $first = esc_html($u->first_name ?: $name);
        $GLOBALS['cc_ath_lang'] = cc_ath_user_lang($uid);   // the branded athlete email (same design as the welcome email)
        $h = cc_ath_mail_shell(sprintf(esc_html(cc_f('Hi %s,')), $first), esc_html(cc_f('Thank you! Your Rider Information Form is in, and your signed copy is attached. Your athlete hub is now open.')),
                               esc_html(cc_f('Open my athlete hub')), home_url('/' . CC_ATH_SLUG . '/'), '', esc_html(cc_f('See you on the road,')));
        $to = strpos(home_url(), '//staging.') !== false ? (string) get_option('cc_staging_notify', '') : $u->user_email;   // staging: never a real inbox
        if (is_email($to)) wp_mail($to, cc_f('Your signed Rider Information Form'), $h,
            ['Content-Type: text/html; charset=UTF-8', 'From: Matteo Cigala <coaching@cigalacycling.com>', 'Reply-To: Matteo Cigala <matteo@cigalacycling.com>'], $tmp ? [$tmp] : []);
    }
    if ($tmp) @unlink($tmp);
}
function cc_f_line($a) {   // one line for Matteo: sport, age, numbers, goal
    $p = [];
    if (!empty($a['dob'])) $p[] = cc_f_age($a['dob']) . ' years';
    if (!empty($a['sport'])) $p[] = implode('/', (array) $a['sport']) . (!empty($a['sport_other']) ? ' (' . $a['sport_other'] . ')' : '');
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
    if ($act === 'purge') return cc_f_purge($pid) ? ['ok' => true, 'status' => 'deleted'] : new WP_Error('cc_purge', 'Only a former athlete can be deleted', ['status' => 400]);   // no login any more, so before the check below
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
        case 'end': if (!cc_f_end($pid)) return new WP_Error('cc_end', 'Could not end coaching', ['status' => 400]); return ['ok' => true, 'status' => 'former'];
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
    wp_safe_redirect(add_query_arg(array_merge(['board' => 'forms', 'done' => $act], $act === 'purge' ? [] : ['a' => $pid]), home_url('/' . CC_ATH_SLUG . '/'))); exit;
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
       . '<b>Paper form on file</b> means they get the short “Update your details” step instead of the full form.</p>'
       . (isset($_GET['done'], $_GET['n']) ? '<p class="av-msg">' . (int) $_GET['n'] . ($_GET['done'] === 'end' ? ' athlete(s) moved to Former athletes.' : ' former athlete(s) deleted for good.') . '</p>' : '')
       . (($_GET['done'] ?? '') === 'purge' && !isset($_GET['n']) ? '<p class="av-msg">Deleted for good.</p>' : '')
       . cc_f_bulkbar('rf-bulk-cur', 'end', 'End coaching for selected', 'End coaching for %n athlete(s)? Their login stops working now and their health answers are deleted (privacy policy). The signed form and other answers stay under Former athletes for two years.') . '<div class="rf-list">';
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'orderby' => 'title', 'order' => 'ASC', 'meta_key' => 'cc_user']) as $p) {
        $uid = (int) get_post_meta($p->ID, 'cc_user', true); if (!$uid) continue;
        $st = cc_f_status($uid); $m = json_decode((string) get_post_meta($p->ID, 'cc_form_signed', true), true) ?: [];
        $when = $st === 'signed' || $st === 'updated' ? ' ' . date_i18n('j M Y', (int) get_user_meta($uid, 'cc_form_done', true)) : ($st === 'unlocked' ? ' ' . date_i18n('j M', (int) get_user_meta($uid, 'cc_form_unlock', true)) : '');
        $o .= cc_f_pickrow($p->ID, 'rf-bulk-cur', '<a class="rf-row rf-' . $st . '" href="' . esc_url(add_query_arg('a', $p->ID, $base)) . '"><b>' . esc_html($p->post_title) . '</b><span>' . $label[$st] . esc_html($when)
            . (cc_f_kind($uid) === 'update' ? ' · paper form on file' : '') . (!empty($m['u18']) && empty($m['coach']) ? ' · <em>under 18: countersign</em>' : '') . '</span></a>');
    }
    $o .= '</div>';
    // former athletes (login deleted when coaching ended): their signed form and answers stay here, read only
    $former = [];
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'orderby' => 'title', 'order' => 'ASC']) as $p)
        if (!get_post_meta($p->ID, 'cc_user', true) && !get_post_meta($p->ID, 'cc_shared', true) && (get_post_meta($p->ID, 'cc_ended', true) || get_post_meta($p->ID, 'cc_form_signed', true) || get_post_meta($p->ID, 'cc_profile', true) || get_post_meta($p->ID, 'cc_profile_prefill', true))) $former[] = $p;
    if ($former) {
        $o .= '<h3 class="av-sub" style="margin-top:24px">Former athletes</h3><p class="av-lede">Login removed when coaching ended. Their signed form and answers are kept here (read only), without the health answers, which go when coaching ends. Each record is deleted automatically two years after coaching ended (as your privacy policy says), or now with “Delete”.</p>'
            . cc_f_bulkbar('rf-bulk-old', 'purge', 'Delete selected for good', 'Delete everything for %n former athlete(s): signed form, answers, availability, goals, voice notes and reports? This cannot be undone.') . '<div class="rf-list">';
        foreach ($former as $p) { $m = json_decode((string) get_post_meta($p->ID, 'cc_form_signed', true), true) ?: [];
            $end = (int) get_post_meta($p->ID, 'cc_ended', true);
            $o .= cc_f_pickrow($p->ID, 'rf-bulk-old', '<a class="rf-row rf-former" href="' . esc_url(add_query_arg('a', $p->ID, $base)) . '"><b>' . esc_html(preg_replace('/^Former athlete: /', '', $p->post_title)) . '</b><span>'
                . ($end ? 'Ended ' . esc_html(date_i18n('j M Y', $end)) . ' · ' : '') . ($m ? 'Signed ' . esc_html(date_i18n('j M Y', $m['at'])) : (get_post_meta($p->ID, 'cc_profile_prefill', true) ? 'Paper form on file' : 'No form')) . '</span></a>'); }
        $o .= '</div>';
    }
    $o .= '<script>(function(){document.querySelectorAll("form.rf-bulk").forEach(function(f){var ps=function(){return document.querySelectorAll("input.rf-pick[form="+f.id+"]")};'
        . 'f.querySelector(".rf-all").addEventListener("change",function(e){ps().forEach(function(c){c.checked=e.target.checked})});'
        . 'f.addEventListener("submit",function(e){var n=[].filter.call(ps(),function(c){return c.checked}).length;if(!n){e.preventDefault();alert("Tick the athletes first.");return}'
        . 'if(!confirm(f.dataset.confirm.replace("%n",n)))e.preventDefault();});});})();</script>';
    return $o . '</section>';
}, 10, 2);
/* Matteo 17 Nov: end coaching (login removed, the record stays under Former athletes) and delete a former athlete's data for good, one or many at once */
function cc_f_end($pid) {   // removes the login; the record stays read only under Former athletes, without the health answers (cc_f_ended below)
    $uid = (int) get_post_meta($pid, 'cc_user', true); $u = $uid ? get_userdata($uid) : null;
    if (!$u || user_can($u, 'edit_posts')) return false;   // never a coach, editor or admin
    require_once ABSPATH . 'wp-admin/includes/user.php';
    return wp_delete_user($uid, get_current_user_id());   // anything they uploaded is kept, under Matteo's name
}
/* The privacy policy (live, "How long we keep it"): health information is deleted when coaching ends; coaching records are kept no longer
 * than two years after it ends. So: whenever an athlete's login is deleted (here or in Users), their health answers go and the signed PDF
 * is made again without them; two years later a daily job deletes the whole record. */
function cc_f_health_keys() {
    $k = [];
    foreach (cc_f_steps() as $st) foreach ($st[3] as $pn) if (($pn[0] ?? '') === 'p' && ($st[0] === 'healthupd' || ($pn[1] ?? '') === 'Medical history')) foreach ($pn['fields'] as $f) $k[] = $f[0];
    return $k;
}
function cc_f_strip_health($pid) {
    $hk = array_flip(cc_f_health_keys());
    foreach (['cc_profile', 'cc_profile_prefill'] as $mk) { $a = json_decode((string) get_post_meta($pid, $mk, true), true);
        if (is_array($a)) update_post_meta($pid, $mk, wp_slash(wp_json_encode(array_diff_key($a, $hk)))); }
    $m = json_decode((string) get_post_meta($pid, 'cc_form_signed', true), true) ?: [];
    if (!empty($m['pdf_id']) && ($m['kind'] ?? '') === 'full') {
        $a = json_decode((string) get_post_meta($pid, 'cc_profile', true), true) ?: [];
        $sigf = !empty($m['sig_id']) ? get_attached_file($m['sig_id']) : '';
        $old = (int) $m['pdf_id'];
        $m['pdf_id'] = cc_f_store($pid, cc_f_pdf($pid, $a, $m, $sigf && file_exists($sigf) ? file_get_contents($sigf) : ''), 'rider-form', 'pdf', 'application/pdf', 'Rider Information Form (signed, health answers removed when coaching ended)');
        if ($m['pdf_id']) { wp_delete_attachment($old, true); $m['health_removed'] = time(); update_post_meta($pid, 'cc_form_signed', wp_slash(wp_json_encode($m))); }
    }
    update_post_meta($pid, 'cc_health_removed', time());
}
add_action('delete_user', function ($uid) {   // before athlete-area.php turns the page into "Former athlete: …"
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'meta_key' => 'cc_user', 'meta_value' => (int) $uid, 'numberposts' => -1, 'fields' => 'ids']) as $pid) {
        update_post_meta($pid, 'cc_ended', time()); cc_f_strip_health($pid);
    }
}, 5);
add_action('init', function () { if (!wp_next_scheduled('cc_f_retention')) wp_schedule_event(time() + HOUR_IN_SECONDS, 'daily', 'cc_f_retention'); });
add_action('cc_f_retention', function () {   // two years after coaching ended: the whole record goes
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'fields' => 'ids', 'meta_key' => 'cc_ended']) as $pid)
        if (!get_post_meta($pid, 'cc_user', true) && (int) get_post_meta($pid, 'cc_ended', true) < time() - 2 * YEAR_IN_SECONDS) cc_f_purge($pid);
});
function cc_f_purge($pid) {   // a former athlete only: the page, its private files (signed PDF, signature, voice notes), their reports
    if (get_post_type($pid) !== 'cc_athlete' || get_post_meta($pid, 'cc_user', true) || get_post_meta($pid, 'cc_shared', true)) return false;
    $kids = get_posts(['post_parent' => $pid, 'post_type' => ['attachment', 'cc_report'], 'post_status' => 'any', 'numberposts' => -1]);   // 'any' would skip cc_report (excluded from search)
    foreach ($kids as $k) {
        if ($k->post_type === 'attachment') { wp_delete_attachment($k->ID, true); continue; }
        foreach (get_posts(['post_parent' => $k->ID, 'post_type' => 'attachment', 'post_status' => 'any', 'numberposts' => -1, 'fields' => 'ids']) as $a) wp_delete_attachment($a, true);
        wp_delete_post($k->ID, true);
    }
    foreach (['cc_form_signed'] as $mk) { $m = json_decode((string) get_post_meta($pid, $mk, true), true) ?: []; foreach (['pdf_id', 'sig_id'] as $f) if (!empty($m[$f])) wp_delete_attachment((int) $m[$f], true); }
    return (bool) wp_delete_post($pid, true);
}
function cc_f_bulkbar($id, $act, $text, $confirm) {
    return '<form id="' . $id . '" class="rp-bulk rf-bulk" method="post" action="' . esc_url(admin_url('admin-post.php')) . '" data-confirm="' . esc_attr($confirm) . '"><input type="hidden" name="action" value="cc_form_bulk">'
         . '<input type="hidden" name="act" value="' . $act . '">' . wp_nonce_field('cc_form_bulk', '_wpnonce', false, false)
         . '<label class="rp-mail"><input type="checkbox" class="rf-all"> Select all</label><button class="btn btn-ghost rp-del">' . esc_html($text) . '</button></form>';
}
function cc_f_pickrow($pid, $form, $row) { return '<div class="rf-pickrow"><input type="checkbox" class="rf-pick" name="pids[]" value="' . $pid . '" form="' . $form . '" aria-label="Select ' . esc_attr(get_post_field('post_title', $pid)) . '">' . $row . '</div>'; }
add_action('admin_post_cc_form_bulk', function () {
    if (!cc_ath_is_coach() || !wp_verify_nonce($_POST['_wpnonce'] ?? '', 'cc_form_bulk')) wp_die('Not allowed');
    $act = sanitize_key($_POST['act'] ?? ''); $n = 0;
    foreach (array_map('intval', (array) ($_POST['pids'] ?? [])) as $pid) {
        if (get_post_type($pid) !== 'cc_athlete') continue;
        if ($act === 'end' && cc_f_end($pid)) $n++; elseif ($act === 'purge' && cc_f_purge($pid)) $n++;
    }
    wp_safe_redirect(add_query_arg(['board' => 'forms', 'done' => $act, 'n' => $n], home_url('/' . CC_ATH_SLUG . '/'))); exit;
});
function cc_f_btn($pid, $act, $text, $ghost = true) {
    return '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" class="rf-act"><input type="hidden" name="action" value="cc_form_admin"><input type="hidden" name="page" value="' . $pid . '">'
         . '<input type="hidden" name="act" value="' . $act . '">' . wp_nonce_field('cc_form_admin_' . $pid, '_wpnonce', false, false) . '<button class="btn ' . ($ghost ? 'btn-ghost' : 'btn-go') . ($act === 'end' || $act === 'purge' ? ' rp-del' : '') . '"'
         . ($act === 'end' ? ' onclick="return confirm(\'End coaching? Their login stops working now and their health answers are deleted (privacy policy). The signed form and other answers stay under Former athletes for two years.\')"' : '')
         . ($act === 'purge' ? ' onclick="return confirm(\'Delete everything for good: signed form, answers, availability, goals, voice notes and reports? This cannot be undone.\')"' : '') . '>' . esc_html($text) . '</button></form>';
}
function cc_f_one($pid, $base) {
    $uid = (int) get_post_meta($pid, 'cc_user', true); $st = cc_f_status($uid); $kind = cc_f_kind($uid);
    $m = json_decode((string) get_post_meta($pid, 'cc_form_signed', true), true) ?: [];
    $a = json_decode((string) get_post_meta($pid, 'cc_profile', true), true) ?: []; $pre = json_decode((string) get_post_meta($pid, 'cc_profile_prefill', true), true) ?: [];
    $o = '<p><a href="' . esc_url($base) . '">← All rider forms</a></p><section class="ath-s"><h2>' . cc_ath_icon('doc', 'ath-hic') . esc_html(get_post_field('post_title', $pid)) . '</h2><div class="rf-acts">';
    if (!$uid) {   // former athlete: no login any more, nothing to unlock or ask; just the record
        if (!empty($m['pdf_id'])) $o .= '<a class="btn btn-go" href="' . esc_url(wp_get_attachment_url($m['pdf_id'])) . '" target="_blank" rel="noopener">Signed PDF</a>';
        $o .= cc_f_btn($pid, 'purge', 'Delete all their data for good') . '</div><p class="av-lede">Former athlete: login removed' . (($e = (int) get_post_meta($pid, 'cc_ended', true)) ? ' on ' . esc_html(date_i18n('j M Y', $e)) : '') . '. ' . ($m ? 'Signed ' . esc_html(date_i18n('j M Y, H:i', $m['at'])) . ($m['name'] ? ' by ' . esc_html($m['name']) : '') . '.' : '') . '</p>';
        $show = $a ?: $pre;
        return $o . ($show ? cc_f_answers_html($show, $a ? ($m['kind'] ?? 'full') : 'full') : '<p>No answers on file.</p>') . '</section>';
    }
    if (!empty($m['pdf_id'])) $o .= '<a class="btn btn-go" href="' . esc_url(wp_get_attachment_url($m['pdf_id'])) . '" target="_blank" rel="noopener">Signed PDF</a>';
    if (!empty($m['u18']) && empty($m['coach'])) $o .= cc_f_btn($pid, 'countersign', 'Countersign as coach (under 18)', false);
    $o .= $st === 'unlocked' ? cc_f_btn($pid, 'lock', 'Lock the hub again') : (!cc_f_open($uid) ? cc_f_btn($pid, 'unlock', 'Unlock hub') : '');
    if (!get_user_meta($uid, 'cc_form_done', true)) $o .= $kind === 'full' ? cc_f_btn($pid, 'paper', 'Paper form on file (short update instead)') : cc_f_btn($pid, 'full', 'Ask for the full form instead');
    else $o .= cc_f_btn($pid, 'reopen', 'Ask them to fill it in again');
    $o .= cc_f_btn($pid, 'end', 'End coaching (remove login)');
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
        case 'events': return implode("\n", array_map(function ($e) { return function_exists('cc_g_event_text') ? cc_g_event_text($e) : $e['name']; }, (array) $v));
        case 'checks': $o = $f['opts'] === 'days' ? CC_AV_DAYS : $f['opts']; return implode(', ', array_map(function ($x) use ($o) { return $o[$x] ?? $x; }, (array) $v));
        case 'radio': case 'select': return (string) ($f['opts'][$v] ?? $v);
        case 'yn': return $v === 'yes' ? 'Yes' : ($v === 'no' ? 'No' : '');
        case 'tick': return $v ? 'Agreed' : '';
        case 'date': return $v ? date_i18n('j M Y', strtotime($v . ' 12:00')) : '';
        default: return (string) $v;
    }
}

/* Coach-only preview of an athlete's signed-form PDF, rebuilt from their saved answers (Matteo 17 Nov; also used to check the design). Nothing is stored or sent. */
add_action('rest_api_init', function () {
    register_rest_route('cc/v1', '/form-pdf', ['methods' => 'GET', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        $pid = (int) $r->get_param('page'); $m = json_decode((string) get_post_meta($pid, 'cc_form_signed', true), true) ?: [];
        $a = json_decode((string) get_post_meta($pid, 'cc_profile', true), true) ?: [];
        if ((!$m || !$a) && $r->get_param('sample')) {   // design check with made-up answers
            $a = ['first_name' => 'Sample', 'last_name' => 'Rider', 'goal_short' => 'Ride the Etape du Tour strongly and enjoy the climbs.', 'goal_long' => 'Keep getting fitter for years to come.',
                  'hours_week' => '7h', 'hours_day' => '1h30', 'recent' => 'Two turbo sessions midweek and a long club ride on Sunday.'];
            $m = ['lang' => 'en', 'at' => time(), 'u18' => false, 'name' => 'Sample Rider', 'ip' => '-', 'kind' => 'full'];
        }
        if (!$m || !$a) return new WP_Error('cc_none', 'No signed form for this athlete', ['status' => 404]);
        $sigf = !empty($m['sig_id']) ? get_attached_file((int) $m['sig_id'], true) : '';
        return ['base64' => base64_encode(cc_f_pdf($pid, $a, $m + ['u18' => false, 'ip' => '', 'name' => '', 'at' => time()], $sigf && file_exists($sigf) ? file_get_contents($sigf) : ''))];
    }]);
});
/* ---------- the signed PDF (A4, built-in fonts, signature picture). No library needed. ---------- */
const CC_F_PDF_LOGO = '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';   // round coaching logo on the dark band, 180 px JPEG
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
    private function reg($data) { $sz = @getimagesizefromstring($data); if (!$sz) return -1; $this->imgs[] = [$data, $sz[0], $sz[1]]; return count($this->imgs) - 1; }
    /* Matteo 17 Nov: branded like the rest (dark band, round logo, "Cigala Cycling Coaching / by Matteo Cigala", green accent) */
    function band($logo) {
        $h = 92; $this->s .= sprintf("q 0.031 0.035 0.039 rg 0 %.2F %.2F %.2F re f Q\n", self::H - $h, self::W, $h);
        $n = $logo !== '' ? $this->reg($logo) : -1;
        if ($n >= 0) $this->s .= sprintf("q 56 0 0 56 %.2F %.2F cm /Im%d Do Q\n", self::M, self::H - $h + 18, $n);
        $x = self::M + 70;
        $this->s .= sprintf("BT 1 1 1 rg /F2 17 Tf %.2F %.2F Td (Cigala Cycling Coaching) Tj ET\n", $x, self::H - $h + 50);
        $this->s .= sprintf("BT 0.75 0.78 0.82 rg /F1 10 Tf %.2F %.2F Td (by Matteo Cigala) Tj ET\n", $x, self::H - $h + 32);
        $this->s .= sprintf("q 0.004 0.541 0.267 rg 0 %.2F %.2F 4 re f Q\n", self::H - $h - 4, self::W);
        $this->y = self::H - $h - 4 - 26;
    }
    function accent() { $this->s .= sprintf("q 0.004 0.541 0.267 rg %.2F %.2F 44 3 re f Q\n", self::M, $this->y - 2); $this->y -= 12; }
    function jpeg($data, $w) { $sz = @getimagesizefromstring($data); if (!$sz) return; $h = $w * $sz[1] / $sz[0]; $this->need($h + 4);
        $n = count($this->imgs); $this->imgs[] = [$data, $sz[0], $sz[1]]; $this->y -= $h; $this->s .= sprintf("q %.2F 0 0 %.2F %.2F %.2F cm /Im%d Do Q\n", $w, $h, self::M, $this->y, $n); $this->y -= 4; }
    function output() {
        $this->pages[] = $this->s; $np = count($this->pages);
        foreach ($this->pages as $i => $c) $this->pages[$i] = $c . sprintf("BT 0.45 0.45 0.45 rg /F1 8 Tf %.2F 24 Td (Cigala Cycling Coaching  |  coaching.cigalacycling.com) Tj ET\nBT 0.45 0.45 0.45 rg /F1 8 Tf %.2F 24 Td (%d / %d) Tj ET\nq 0.004 0.541 0.267 rg %.2F 36 %.2F 1 re f Q\n", self::M, self::W - self::M - 24, $i + 1, $np, self::M, self::W - 2 * self::M);
        $o = []; $ni = count($this->imgs);
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
    $GLOBALS['cc_f_lang'] = $m['lang'] ?? 'en';   // the legal texts as signed (Italian for Italian athletes)
    $p = new CC_Pdf();
    $p->band(base64_decode(CC_F_PDF_LOGO));
    $p->text('Rider Information Form', 22, true, 0, 2);
    $p->accent();
    $p->text(get_post_field('post_title', $pid) . ' · signed ' . date_i18n('j F Y, H:i', $m['at']) . ($m['u18'] ? ' · under 18' : ''), 10, false, 0, 6, '0.35 0.35 0.35');
    $p->rule();
    foreach (cc_f_steps() as $st) {
        if ($st[2] !== 'both' && $st[2] !== 'full') continue;
        foreach ($st[3] as $pn) {
            if (($pn[0] ?? '') !== 'p' || $st[0] === 'sign' || (($pn['if'] ?? '') === 'u18' && !$m['u18'])) continue;
            $has = false; foreach ($pn['fields'] as $f) if (in_array($f[1], ['legal', 'group'], true) || (array_key_exists($f[0], $a) && cc_f_val($f, $a[$f[0]]) !== '')) $has = true;
            if (!$has) continue;   // no empty headings
            $p->space(6); $p->text($pn[1], 13, true, 0, 4);
            if (($pn[2] ?? '') === 'CC_F_MED_INTRO') $p->text(cc_f_html2text(cc_f_legal('CC_F_MED_INTRO')), 9.5, false, 0, 4, '0.25 0.25 0.25');
            foreach ($pn['fields'] as $f) {
                if ($f[1] === 'legal') { $p->space(4); foreach (explode("\n", cc_f_html2text(cc_f_legal($f['text']))) as $ln) { $b = strpos($ln, '[[B]]') === 0; $p->text($b ? substr($ln, 5) : $ln, $b ? 10.5 : 9.5, $b, 0, 1, $b ? '0 0 0' : '0.2 0.2 0.2'); } $p->space(4); continue; }
                if ($f[1] === 'group') { $p->text($f[2], 10.5, true, 0, 2); if (isset($f['text'])) $p->text(cc_f_html2text(cc_f_legal($f['text'])), 9.5, false, 0, 3, '0.2 0.2 0.2'); continue; }
                if (in_array($f[1], ['sig'], true) || !array_key_exists($f[0], $a)) continue;
                $v = cc_f_val($f, $a[$f[0]]); if ($v === '' && $f[1] !== 'tick') continue;
                $p->text($f[2] ?: 'Usual week', 9.5, false, 0, 0, '0.3 0.3 0.3'); $p->text($v === '' ? '-' : $v, 11, true, 0, 6);
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
var R=document.getElementById('rf');if(!R)return;var F=R.querySelector('form:not(.ath-lang)'),/* Matteo 17 Nov: the language switch is a form too; it came first, so taps and autosave went to the wrong form */W=JSON.parse(document.getElementById('rf-words').textContent),pv=R.dataset.preview==='1',kind=R.dataset.kind;
var steps=[].slice.call(R.querySelectorAll('.rf-step')),dots=[].slice.call(R.querySelectorAll('.rf-steps li')),i=0,timer=null,drawn=false;
function data(){var d={week:{},events:[]};R.querySelectorAll('input,select,textarea').forEach(function(e){if(!e.name||e.closest('.rf-ev'))return;
  if(e.type==='checkbox'){if(e.closest('.rf-tick')){d[e.name]=e.checked?1:0;}else{d[e.name]=d[e.name]||[];if(e.checked)d[e.name].push(e.value);}}
  else if(e.type==='radio'){if(e.checked)d[e.name]=e.value;else if(!(e.name in d))d[e.name]='';}else d[e.name]=e.value;});
 R.querySelectorAll('.rf-ev').forEach(function(x){var n=x.querySelector('.rf-ev-n').value,dt=x.querySelector('.rf-ev-d').value;if(n||dt)d.events.push({name:n,date:dt,prio:(x.querySelector('.gl-pb[aria-pressed=true]')||{dataset:{p:'B'}}).dataset.p,type:'race'});});
 R.querySelectorAll('.rf-week .av-day').forEach(function(x){var k=x.dataset.k;d.week[k]={h:x.querySelector('select').value,w:[].slice.call(x.querySelectorAll('.av-w[aria-pressed=true]')).map(function(b){return b.dataset.w;})};});return d;}
function age(){var v=(R.querySelector('[name=dob]')||{}).value;if(!v)return null;var b=new Date(v),n=new Date();return n.getFullYear()-b.getFullYear()-((n.getMonth()<b.getMonth()||(n.getMonth()===b.getMonth()&&n.getDate()<b.getDate()))?1:0);}
function cond(){var d=data(),a=age(),u18=a!==null&&a<18;var A=R.querySelector('.rf-age');if(A)A.textContent=a!==null?W.age+': '+a:'';
 R.querySelectorAll('.rf-opt').forEach(function(o){o.hidden=u18;});
 R.querySelectorAll('[data-if]').forEach(function(e){var c=e.dataset.if,s=true;
  if(c==='u18')s=u18;else if(c==='run')s=[].concat(d.sport||[]).some(function(x){return x==='running'||x==='triathlon';});else if(c==='notmale')s=d.gender!=='m';
  else if(c.indexOf('has:')===0){var kv=c.slice(4).split('=');s=[].concat(d[kv[0]]||[]).indexOf(kv[1])>-1;}
  else if(c.indexOf('yes:')===0)s=c.slice(4).split(',').some(function(k){return d[k]==='yes';});e.hidden=!s;});}
function show(n){steps[i].classList.remove('on');i=n;steps[i].classList.add('on');dots.forEach(function(x,k){x.className=k<i?'done':(k===i?'now':'');});
 R.querySelector('.rf-sn').textContent=i+1;R.querySelector('.rf-st').textContent=steps[i].dataset.t;R.querySelector('.rf-back').style.visibility=i?'visible':'hidden';
 R.querySelector('.rf-next').textContent=i===steps.length-1?(pv?W.preview.split('.')[0]:W.submit):W.next;R.querySelector('.rf-err').hidden=true;if(steps[i].dataset.k==='sign')pad();
 var t=R.getBoundingClientRect().top+scrollY-90;scrollTo({top:t,behavior:'smooth'});}
function post(action,extra){var b={action:action,data:data()};for(var k in extra)b[k]=extra[k];
 return fetch(R.dataset.api,{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/json','X-WP-Nonce':R.dataset.nonce},body:JSON.stringify(b)}).then(function(r){return r.json().then(function(j){if(!r.ok)throw j;return j;});});}
function autosave(){if(pv)return;clearTimeout(timer);timer=setTimeout(function(){var s=R.querySelector('.rf-saved');s.textContent=W.saving;post('save').then(function(){s.textContent=W.saved+' ✓';}).catch(function(){s.textContent=W.err;});},1200);}
window.ccRfSaveNow=function(){if(pv)return Promise.resolve();clearTimeout(timer);return post('save');};
(function(){var n=R.querySelector('select[name=nat]');if(!n||!window.Intl||!Intl.DisplayNames)return;try{var dn=new Intl.DisplayNames([R.dataset.lang||'en'],{type:'region'}),v=n.value,o=[].slice.call(n.options,1);
 var G={it:{'gb-eng':'Inghilterra','gb-sct':'Scozia','gb-wls':'Galles','gb-nir':'Irlanda del Nord'},pt:{'gb-eng':'Inglaterra','gb-sct':'Escócia','gb-wls':'País de Gales','gb-nir':'Irlanda do Norte'},sl:{'gb-eng':'Anglija','gb-sct':'Škotska','gb-wls':'Wales','gb-nir':'Severna Irska'}}[R.dataset.lang]||{};o.forEach(function(x){if(G[x.value]){x.textContent=G[x.value];return;}if(x.value.indexOf('-')>0)return;try{var t=dn.of(x.value.toUpperCase());if(t&&t.toUpperCase()!==x.value.toUpperCase())x.textContent=t;}catch(e){}});o.sort(function(a,b){return a.textContent.localeCompare(b.textContent,R.dataset.lang||'en');}).forEach(function(x){n.appendChild(x);});n.value=v;}catch(e){}})();
F.addEventListener('input',function(){cond();autosave();});F.addEventListener('change',function(e){
 if(e.target.dataset.day){var r=e.target.value==='0';e.target.closest('.av-day').querySelectorAll('.av-w').forEach(function(b){b.disabled=r;if(r)b.setAttribute('aria-pressed','false');});}cond();autosave();});
F.addEventListener('click',function(e){var b=e.target.closest('.av-w');if(!b)return;b.setAttribute('aria-pressed',b.getAttribute('aria-pressed')!=='true');autosave();});
/* events: name, date, priority A/B/C (they go to "My goals & events") */
var EV=R.querySelector('.rf-evs');if(EV){var EW=JSON.parse(EV.dataset.words),esc=function(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});};
 var row=function(e){var r=document.createElement('div');r.className='rf-ev';r.innerHTML='<div class="gl-r"><label>'+esc(EW.ev)+'<input type="text" class="rf-ev-n" maxlength="120" value="'+esc(e.name)+'"></label><label>'+esc(EW.date)+'<input type="date" class="rf-ev-d" value="'+esc(e.date)+'"></label></div>'
  +'<div class="rf-ev-b"><span class="rf-ev-pl">'+esc(EW.prio)+'</span><div class="gl-p">'+['A','B','C'].map(function(p){return '<button type="button" class="gl-pb" data-p="'+p+'" aria-pressed="'+((e.prio||'B')===p)+'">'+p+'</button>';}).join('')+'</div><button type="button" class="av-del rf-ev-x">'+esc(EW.rm)+'</button></div>';EV.appendChild(r);};
 JSON.parse(EV.querySelector('.rf-ev-data').textContent).forEach(row);
 R.querySelector('.rf-ev-add').onclick=function(){row({});EV.lastChild.querySelector('.rf-ev-n').focus();};
 EV.addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;if(b.classList.contains('gl-pb')){b.parentNode.querySelectorAll('.gl-pb').forEach(function(y){y.setAttribute('aria-pressed',y===b);});autosave();}
  if(b.classList.contains('rf-ev-x')){b.closest('.rf-ev').remove();autosave();}});}
// signature
var c=R.querySelector('.rf-sig canvas'),x=c&&c.getContext('2d'),down=false,last=null;
function pad(){if(!c)return;var r=c.getBoundingClientRect(),d=window.devicePixelRatio||1;if(!r.width)return;c.width=r.width*d;c.height=r.height*d;x.setTransform(d,0,0,d,0,0);
 x.fillStyle='#fff';x.fillRect(0,0,r.width,r.height);x.lineWidth=2.4;x.lineCap='round';x.lineJoin='round';x.strokeStyle='#111';drawn=false;R.querySelector('.rf-sig-ph').hidden=false;}
if(c){var pt=function(e){var r=c.getBoundingClientRect();return[e.clientX-r.left,e.clientY-r.top];};
 c.addEventListener('pointerdown',function(e){down=true;last=pt(e);c.setPointerCapture(e.pointerId);});
 c.addEventListener('pointermove',function(e){if(!down)return;var p=pt(e);x.beginPath();x.moveTo(last[0],last[1]);x.lineTo(p[0],p[1]);x.stroke();last=p;if(!drawn){drawn=true;R.querySelector('.rf-sig-ph').hidden=true;}});
 ['pointerup','pointercancel'].forEach(function(t){c.addEventListener(t,function(){down=false;});});R.querySelector('.rf-clr').onclick=pad;}
/* every required question on this step must be answered before "Next" (hidden ones never count) */
function check(st){var miss=[],a=age(),u18=a!==null&&a<18;st.querySelectorAll('.rf-f[data-req]').forEach(function(w){w.classList.remove('rf-miss');if(w.closest('[hidden]')||(w.dataset.req==='u18'&&!u18))return;var ok;
  var tk=w.querySelector('.rf-tick input'),wk=w.querySelector('.rf-week');if(wk){ok=true;wk.querySelectorAll('select').forEach(function(x){var d=x.closest('.av-day');d.classList.toggle('rf-dmiss',x.value==='');if(x.value==='')ok=false;});}else if(tk)ok=tk.checked;else{var rs=w.querySelectorAll('input[type=radio],input[type=checkbox]');
   if(rs.length)ok=[].some.call(rs,function(x){return x.checked;});else{var f=w.querySelector('input,select,textarea');ok=!f||f.value.trim()!=='';}}
  if(!ok){w.classList.add('rf-miss');miss.push(w.dataset.label);}});return miss;}
F.addEventListener('change',function(e){var w=e.target.closest('.rf-miss');if(w)w.classList.remove('rf-miss');var d=e.target.closest('.rf-dmiss');if(d&&e.target.value!=='')d.classList.remove('rf-dmiss');});
F.addEventListener('input',function(e){var w=e.target.closest('.rf-miss');if(w)w.classList.remove('rf-miss');});
/* agreements: each tick opens once its text has been scrolled to the end */
R.querySelectorAll('.rf-legal').forEach(function(L){var w=L.closest('.rf-f'),n=w.nextElementSibling,t=n&&n.querySelector('.rf-tick input');if(!t)return;
 var open=function(){t.disabled=false;var h=w.querySelector('.rf-scrollhint');if(h)h.hidden=true;};
 var test=function(){if(L.scrollHeight-L.scrollTop-L.clientHeight<24)open();};if(!t.checked)t.disabled=true;else open();
 L.addEventListener('scroll',test);new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting)test();});}).observe(L);});
R.querySelector('.rf-back').onclick=function(){if(i)show(i-1);};
R.querySelector('.rf-next').onclick=function(){var m=check(steps[i]),er=R.querySelector('.rf-err');
 if(m.length){er.hidden=false;er.textContent=W.step+' '+m.join(' · ');var f=steps[i].querySelector('.rf-miss');if(f)f.scrollIntoView({behavior:'smooth',block:'center'});return;}
 if(i<steps.length-1){show(i+1);autosave();return;}
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
html .cc .rf .rf-yn { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 12px 14px; border-radius: 10px; background: rgba(255,255,255,.03); border: 1px solid rgba(255,255,255,.07); }
html .cc .rf .rf-ynq { display: block; font-weight: 500; font-size: 14px; line-height: 1.4; margin: 0; color: var(--text); flex: 1 1 auto; min-width: 0; } html .cc .rf-seg { display: inline-flex; flex: none; margin-left: auto; border: 1px solid rgba(255,255,255,.16); border-radius: 999px; overflow: hidden; }
html .cc .rf-seg label { position: relative; margin: 0 !important; } html .cc .rf-seg input { position: absolute; opacity: 0; inset: 0; margin: 0; cursor: pointer; }
html .cc .rf-seg span { display: block; padding: 7px 14px; font: 600 13px var(--body); color: var(--text-3); } html .cc .rf-seg input:checked + span { background: #009a44; color: #fff; }
html .cc .rf-seg input[value=yes]:checked + span { background: #E10600; } html .cc .rf-seg input:focus-visible + span { outline: 2px solid #34c46a; outline-offset: -2px; }
html .cc .rf-legal { max-height: 300px; overflow: auto; padding: 14px 16px; border-radius: 12px; background: #0b0d0f; border: 1px solid rgba(255,255,255,.12); font-size: 13.5px; line-height: 1.55; color: var(--text-2); }
html .cc .rf-legal h3 { font: 700 12.5px var(--body); letter-spacing: .1em; text-transform: uppercase; color: var(--text); margin: 14px 0 6px; } html .cc .rf-legal h3:first-child { margin-top: 0; }
html .cc .rf-legal :is(p, li) { margin: 0 0 8px; } html .cc .rf-legal ol { padding-left: 20px; margin: 0; } html .cc .rf-legal a { color: #34c46a; word-break: break-all; }
html .cc .rf-tick { display: flex !important; gap: 12px; align-items: flex-start; font-weight: 500 !important; font-size: 14px !important; cursor: pointer; }
html .cc .rf-tick input { flex: none; appearance: none; -webkit-appearance: none; width: 28px; height: 28px; margin: 0; border: 2.5px solid rgba(255,255,255,.7); border-radius: 7px; background: #0b0d0f center / 18px no-repeat; cursor: pointer; }
html .cc .rf-tick input:checked { background-color: #009a44; border-color: #009a44; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23fff' stroke-width='3.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M5 12.5l4.5 4.5L19 7.5'/%3E%3C/svg%3E"); }
html .cc .rf-tick input:disabled { opacity: .35; cursor: not-allowed; } html .cc .rf-tick input:focus-visible { outline: 2px solid #34c46a; outline-offset: 2px; }
html .cc .rf-tick span { padding-top: 3px; } html .cc .rf-scrollhint { margin: 8px 0 0; font-size: 12.5px; color: #ff3d33; font-weight: 600; } html .cc .rf-scrollhint[hidden] { display: none; }
html .cc .rf-miss :is(input:not([type=radio]):not([type=checkbox]), select, textarea, .rf-seg, .rf-tick input) { border-color: #ff3d33 !important; box-shadow: 0 0 0 1px #ff3d33; }
html .cc .rf-miss :is(label, legend, .rf-tick span, .rf-ynq) { color: #ff3d33 !important; } html .cc .rf-miss .rf-chips { outline: 2px solid #ff3d33; outline-offset: 4px; border-radius: 8px; }
html .cc .rf-dmiss select { border-color: #ff3d33 !important; box-shadow: 0 0 0 1px #ff3d33; } html .cc .rf-dmiss .av-dn { color: #ff3d33; }
html .cc .rf-pv { border-color: rgba(240,191,0,.5); background: rgba(240,191,0,.08); }
html .cc .rf-group { margin: 6px 0 0; font-weight: 600; color: var(--text); font-size: 14px; } html .cc .rf-group-t p { margin: 8px 0 0; font-size: 14px; }
html .cc .rf-week { display: grid; gap: 8px; }
html .cc .rf-evs { display: grid; gap: 10px; margin: 4px 0 10px; } html .cc .rf-ev { display: grid; gap: 8px; padding: 12px; border-radius: 12px; border: 1px solid rgba(255,255,255,.1); background: rgba(255,255,255,.03); }
html .cc .rf-ev label { font-size: 12.5px !important; color: var(--text-3) !important; display: grid !important; gap: 5px; margin: 0 !important; min-width: 0; }
html .cc .rf .rf-ev input { min-width: 0; width: 100%; } html .cc .rf-ev .gl-r { grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr); }
html .cc .rf-ev-b { display: flex; flex-wrap: wrap; align-items: center; gap: 10px; } html .cc .rf-ev-pl { font-size: 12.5px; font-weight: 600; color: var(--text-3); } html .cc .rf-ev-b .gl-p { flex: 1; max-width: 220px; }
/* Race priority colours (Matteo 17 Nov, everywhere in Cigala + Vekta): A gold, B silver, C bronze */
html .cc .gl-ev.gl-A { border-left-color: #D4AF37 !important; background: linear-gradient(90deg, rgba(212,175,55,.14), rgba(255,255,255,.03) 50%) !important; }
html .cc .gl-ev.gl-B { border-left-color: #C0C4CC !important; background: linear-gradient(90deg, rgba(192,196,204,.10), rgba(255,255,255,.03) 50%) !important; }
html .cc .gl-ev.gl-C { border-left-color: #CD7F32 !important; background: linear-gradient(90deg, rgba(205,127,50,.12), rgba(255,255,255,.03) 50%) !important; }
html .cc .gl-pb[data-p=A][aria-pressed=true] { background: linear-gradient(135deg, #F3D774, #D4AF37 55%, #A8841F); border-color: #D4AF37; color: #1a1406; }
html .cc .gl-pb[data-p=B][aria-pressed=true] { background: linear-gradient(135deg, #F2F3F5, #C0C4CC 55%, #8E939C); border-color: #C0C4CC; color: #15171a; }
html .cc .gl-pb[data-p=C][aria-pressed=true] { background: linear-gradient(135deg, #E9A86B, #CD7F32 55%, #9A5A1F); border-color: #CD7F32; color: #1c1006; }
html .cc .gl-prio.A { background: linear-gradient(135deg, #F3D774, #D4AF37 55%, #A8841F) !important; color: #1a1406 !important; }
html .cc .gl-prio.B { background: linear-gradient(135deg, #F2F3F5, #C0C4CC 55%, #8E939C) !important; color: #15171a !important; }
html .cc .gl-prio.C { background: linear-gradient(135deg, #E9A86B, #CD7F32 55%, #9A5A1F) !important; color: #1c1006 !important; }
html .cc .ath form .rf-ev-add { width: auto; justify-self: start; margin: 0; }
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
html .cc .rf-pickrow { display: flex; align-items: center; gap: 10px; } html .cc .rf-pickrow > .rf-row { flex: 1 1 auto; min-width: 0; } html .cc .rf-pick { width: 20px; height: 20px; accent-color: #009a44; flex: none; margin: 0; }
html .cc .ath form.rf-bulk { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px; margin: 0 0 12px; padding: 10px 14px; border-radius: 12px; border: 1px dashed rgba(255,255,255,.14); } html .cc .ath form.rf-bulk .btn { width: auto; margin: 0; white-space: normal; }
html .cc .rp-del { border-color: rgba(225,6,0,.5) !important; }
html .cc .rf-row.rf-former { opacity: .75; } html .cc .rf-row em { color: #ff3d33; font-style: normal; } html .cc .rf-acts { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 14px; } html .cc .rf-act { margin: 0; }
html .cc .rf-qa { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.2fr); gap: 4px 14px; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,.06); font-size: 14px; }
html .cc .rf-qa span { color: var(--text-3); } html .cc .rf-qa b { color: #fff; font-weight: 500; }
@media (max-width: 640px) { html .cc .rf-grid { grid-template-columns: 1fr; } html .cc .rf-qa { grid-template-columns: 1fr; } html .cc .rf-steps { top: 60px; }
  html .cc .rf .rf-yn { flex-wrap: wrap; } html .cc .rf .rf-ynq { flex-basis: 100%; } }
</style>
CSS;
});
