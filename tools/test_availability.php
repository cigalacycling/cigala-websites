<?php
/* Local test of the availability logic (no WordPress needed): php tools/test_availability.php */
define('ABSPATH', '/');
function add_action() {} function add_filter() {}
require __DIR__ . '/../coaching/athlete-area/availability.php';
$fail = 0; function ok($c, $m) { global $fail; echo ($c ? "ok   " : "FAIL ") . $m . "\n"; if (!$c) $fail++; }
$today = '2026-11-18';   // a Wednesday
$in = ['week' => ['mon' => ['h' => '1', 'w' => ['pm', 'bogus']], 'tue' => ['h' => '0', 'w' => ['am']], 'sat' => ['h' => '4', 'w' => ['am']], 'sun' => ['h' => '9']],
       'changes' => [['from' => '2026-12-19', 'to' => '2026-12-12', 'type' => 'away', 'h' => '2', 'text' => '<b>Ski</b> trip'],
                     ['from' => '2026-11-01', 'to' => '2026-11-10', 'type' => 'less'],            // over: dropped
                     ['from' => '2026-11-20', 'type' => 'less', 'h' => '1'],                       // one day
                     ['from' => '2026-02-30', 'type' => 'more']],                                  // bad date: dropped
       'note' => "  Line one\n\n\n\nLine two <script>x</script> "];
$a = cc_av_clean($in, $today);
ok($a['week']['mon'] === ['h' => '1', 'w' => ['pm']], 'unknown "when" dropped');
ok($a['week']['tue'] === ['h' => '0', 'w' => []], 'rest day has no times');
ok($a['week']['sun']['h'] === '', 'unknown hours -> not set');
ok(count($a['changes']) === 2, 'past and invalid changes dropped');
ok($a['changes'][0]['from'] === '2026-11-20' && $a['changes'][0]['to'] === '2026-11-20', 'sorted; missing end = one day');
ok($a['changes'][1]['from'] === '2026-12-12' && $a['changes'][1]['to'] === '2026-12-19', 'swapped dates fixed');
ok($a['changes'][1]['h'] === '' && $a['changes'][1]['text'] === 'Ski trip', 'away has no hours; tags stripped');
ok($a['note'] === "Line one\n\nLine two x", 'note cleaned, line breaks kept');
ok(cc_av_day_text($a['week']['mon']) === '1h, evening', 'day text');
ok(cc_av_change_text($a['changes'][1]) === '12–19 Dec: Away, no riding · Ski trip', 'change text: ' . cc_av_change_text($a['changes'][1]));
ok(cc_av_change_text($a['changes'][0]) === 'Fri 20 Nov: Less time (1h a day)', 'one-day change: ' . cc_av_change_text($a['changes'][0]));
ok(cc_av_hours_week($a) == 5, 'weekly hours');
$d = cc_av_diff(null, $a);
ok(in_array('Monday: not set → 1h, evening', $d, true) && in_array('New: 12–19 Dec: Away, no riding · Ski trip', $d, true) && in_array('Note updated', $d, true), 'diff from nothing');
$b = $a; $b['week']['mon']['h'] = '2'; $b['changes'] = [$a['changes'][1]];
$d = cc_av_diff($a, $b);
ok($d === ['Monday: 1h, evening → 2h, evening', 'Removed: Fri 20 Nov: Less time (1h a day)'], 'diff: ' . json_encode($d, JSON_UNESCAPED_UNICODE));
ok(cc_av_diff($a, $a) === [], 'no change, no diff');
$n = cc_av_vekta_notes(null, $a, $today);
ok(isset($n['2026-11-20'], $n['2026-12-12'], $n['2026-12-19']) && !isset($n['2026-12-20']), 'a note on each day of each change');
ok(isset($n['2026-11-23']) && strpos($n['2026-11-23'], 'Usual week from now: Mon 1h, evening; Tue rest day') !== false, 'new usual week: note on next Monday');
ok(count($n) === 1 + 8 + 1, 'note count ' . count($n));
$n2 = cc_av_vekta_notes($a, $b, $today);
ok(isset($n2['2026-11-23']) && !isset($n2['2026-11-20']), 'removed change gets no note');
$long = cc_av_clean(['changes' => [['from' => '2026-11-18', 'to' => '2027-06-01', 'type' => 'away']]], $today);
ok(count(cc_av_vekta_notes($long, $long, $today)) === 31, 'long absence capped at 31 notes');
echo $fail ? "$fail failed\n" : "all passed\n"; exit($fail ? 1 : 0);
