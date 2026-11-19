<?php
if (!defined('ABSPATH')) return;
/* ---------- Food diary (Matteo, 19 Nov 2026) ----------
 * For athletes with the "Nutrition package" (post meta cc_nutri_pkg, switched on by Matteo on the athlete's page or by Marine in her view).
 * Athletes log their food per day in fixed slots (search in an open food database copied into the hub: ANSES-CIQUAL + USDA FoodData Central,
 * plus their own foods and recipes), with a time, a note and a private photo per slot. Marine (role cc_nutritionist) and Matteo review
 * each day with the athlete's training and Marine's nutrition notes from Vekta (sent by Matteo's laptop: the Vekta key never comes here),
 * and reply under the day. Without the package the athlete sees a small card about it instead. Health data: deleted when coaching ends.
 * Storage: one post meta per day (cc_fd_YYYY-MM-DD), own foods in cc_food_mine, weight in cc_food_kg, Vekta summary in cc_food_vx.
 * The food database is one JSON in the option cc_food_db (gzip copy in cc_food_db_gz), served by GET /cc/v1/foods with a long cache. */

const CC_FD_SLOTS = ['breakfast', 'pre', 'bike', 'recovery', 'lunch', 'dinner', 'snacks'];
const CC_FD_MARINE_URL = 'https://www.vivifysports.com/nutritionalcoaching';

function cc_fd_w($k) {
    static $W = [
        'title' => ['Food diary', 'Diario alimentare', 'Diário alimentar', 'Prehranski dnevnik', 'Stravovací denník'],
        'lede' => ['Log what you eat and drink, meal by meal. Marine Lenehan, your sports nutritionist, reviews your diary and replies here.',
                   'Annota cosa mangi e bevi, pasto per pasto. Marine Lenehan, la tua nutrizionista sportiva, legge il tuo diario e ti risponde qui.',
                   'Regista o que comes e bebes, refeição a refeição. A Marine Lenehan, a tua nutricionista desportiva, revê o teu diário e responde-te aqui.',
                   'Zapisuj, kaj ješ in piješ, obrok za obrokom. Marine Lenehan, tvoja športna nutricionistka, pregleda tvoj dnevnik in ti odgovori tukaj.',
                   'Zapisuj si, čo ješ a piješ, jedlo po jedle. Marine Lenehan, tvoja športová nutričná poradkyňa, si tvoj denník prezrie a odpovie ti tu.'],
        'breakfast' => ['Breakfast', 'Colazione', 'Pequeno-almoço', 'Zajtrk', 'Raňajky'],
        'pre' => ['Pre-ride', 'Prima dell’uscita', 'Antes do treino', 'Pred vožnjo', 'Pred jazdou'],
        'bike' => ['On the bike', 'In bici', 'Na bicicleta', 'Na kolesu', 'Na bicykli'],
        'recovery' => ['Recovery', 'Recupero', 'Recuperação', 'Regeneracija', 'Regenerácia'],
        'lunch' => ['Lunch', 'Pranzo', 'Almoço', 'Kosilo', 'Obed'],
        'dinner' => ['Dinner', 'Cena', 'Jantar', 'Večerja', 'Večera'],
        'snacks' => ['Snacks', 'Spuntini', 'Snacks', 'Prigrizki', 'Snacky'],
        'time' => ['Time', 'Ora', 'Hora', 'Ura', 'Čas'],
        'add' => ['Add food', 'Aggiungi alimento', 'Adicionar alimento', 'Dodaj živilo', 'Pridať potravinu'],
        'search' => ['Search a food, e.g. oats, banana', 'Cerca un alimento (in inglese, es. oats, banana)', 'Procura um alimento (em inglês, p. ex. oats, banana)', 'Poišči živilo (v angleščini, npr. oats, banana)', 'Hľadaj potravinu (po anglicky, napr. oats, banana)'],
        'grams' => ['Amount (g)', 'Quantità (g)', 'Quantidade (g)', 'Količina (g)', 'Množstvo (g)'],
        'addit' => ['Add', 'Aggiungi', 'Adicionar', 'Dodaj', 'Pridať'],
        'remove' => ['Remove', 'Rimuovi', 'Remover', 'Odstrani', 'Odstrániť'],
        'cancel' => ['Cancel', 'Annulla', 'Cancelar', 'Prekliči', 'Zrušiť'],
        'noresults' => ['No food found. Try another word, or add your own food from a label below.', 'Nessun alimento trovato. Prova un’altra parola, o aggiungi un tuo alimento dall’etichetta qui sotto.', 'Nenhum alimento encontrado. Tenta outra palavra ou adiciona o teu próprio alimento a partir do rótulo, mais abaixo.', 'Živila ni bilo mogoče najti. Poskusi z drugo besedo ali spodaj dodaj svoje živilo z etikete.', 'Potravina sa nenašla. Skús iné slovo alebo nižšie pridaj vlastnú potravinu podľa etikety.'],
        'loading' => ['Loading foods…', 'Caricamento alimenti…', 'A carregar alimentos…', 'Nalagam živila…', 'Načítavam potraviny…'],
        'slot_total' => ['Total', 'Totale', 'Total', 'Skupaj', 'Spolu'],
        'day_total' => ['Day total', 'Totale del giorno', 'Total do dia', 'Skupaj za dan', 'Spolu za deň'],
        'carbs' => ['Carbs', 'Carboidrati', 'Hidratos', 'Ogljikovi hidrati', 'Sacharidy'],
        'protein' => ['Protein', 'Proteine', 'Proteína', 'Beljakovine', 'Bielkoviny'],
        'fat' => ['Fat', 'Grassi', 'Gordura', 'Maščobe', 'Tuky'],
        'fibre' => ['Fibre', 'Fibre', 'Fibra', 'Vlaknine', 'Vláknina'],
        'sugars' => ['Sugars', 'Zuccheri', 'Açúcares', 'Sladkorji', 'Cukry'],
        'c_ab' => ['C', 'C', 'H', 'OH', 'S'],
        'p_ab' => ['P', 'P', 'P', 'B', 'B'],
        'f_ab' => ['F', 'G', 'G', 'M', 'T'],
        'weight' => ['My weight (kg)', 'Il mio peso (kg)', 'O meu peso (kg)', 'Moja teža (kg)', 'Moja hmotnosť (kg)'],
        'weight_h' => ['Optional: with your weight, carbs and protein are also shown per kg.', 'Facoltativo: con il tuo peso, carboidrati e proteine compaiono anche per kg.', 'Opcional: com o teu peso, os hidratos e a proteína aparecem também por kg.', 'Neobvezno: s tvojo težo so ogljikovi hidrati in beljakovine prikazani tudi na kg.', 'Nepovinné: s tvojou hmotnosťou sa sacharidy a bielkoviny ukážu aj na kg.'],
        'note' => ['Note (optional)', 'Nota (facoltativa)', 'Nota (opcional)', 'Opomba (neobvezno)', 'Poznámka (nepovinné)'],
        'note_ph' => ['e.g. how you felt, where you ate', 'es. come ti sentivi, dove hai mangiato', 'p. ex. como te sentiste, onde comeste', 'npr. kako si se počutil, kje si jedel', 'napr. ako si sa cítil, kde si jedol'],
        'photo' => ['Add a photo', 'Aggiungi una foto', 'Adicionar foto', 'Dodaj fotografijo', 'Pridať fotku'],
        'photo_ch' => ['Change photo', 'Cambia foto', 'Mudar foto', 'Zamenjaj fotografijo', 'Zmeniť fotku'],
        'photo_del' => ['Remove photo', 'Rimuovi foto', 'Remover foto', 'Odstrani fotografijo', 'Odstrániť fotku'],
        'photo_bad' => ['Please choose a photo (up to 10 MB).', 'Scegli una foto (fino a 10 MB).', 'Escolhe uma foto (até 10 MB).', 'Izberi fotografijo (do 10 MB).', 'Vyber fotku (do 10 MB).'],
        'uploading' => ['Uploading…', 'Caricamento…', 'A carregar…', 'Nalaganje…', 'Nahrávam…'],
        'saving' => ['Saving…', 'Salvataggio…', 'A guardar…', 'Shranjujem…', 'Ukladám…'],
        'saved' => ['Saved', 'Salvato', 'Guardado', 'Shranjeno', 'Uložené'],
        'err' => ['Not saved. Check your connection and try again.', 'Non salvato. Controlla la connessione e riprova.', 'Não guardado. Verifica a ligação e tenta de novo.', 'Ni shranjeno. Preveri povezavo in poskusi znova.', 'Neuložené. Skontroluj pripojenie a skús to znova.'],
        'prev' => ['Previous day', 'Giorno precedente', 'Dia anterior', 'Prejšnji dan', 'Predchádzajúci deň'],
        'next' => ['Next day', 'Giorno successivo', 'Dia seguinte', 'Naslednji dan', 'Nasledujúci deň'],
        'today' => ['Today', 'Oggi', 'Hoje', 'Danes', 'Dnes'],
        'gotoday' => ['Back to today', 'Torna a oggi', 'Voltar a hoje', 'Nazaj na danes', 'Späť na dnes'],
        'mine' => ['My foods & recipes', 'I miei alimenti e ricette', 'Os meus alimentos e receitas', 'Moja živila in recepti', 'Moje potraviny a recepty'],
        'mine_lede' => ['Your own foods and recipes appear in the search like any other food.', 'I tuoi alimenti e le tue ricette compaiono nella ricerca come tutti gli altri.', 'Os teus alimentos e receitas aparecem na pesquisa como qualquer outro.', 'Tvoja živila in recepti se v iskanju pojavijo kot vsa druga.', 'Tvoje potraviny a recepty sa vo vyhľadávaní zobrazia ako všetky ostatné.'],
        'add_label' => ['Add a food from a label', 'Aggiungi un alimento dall’etichetta', 'Adicionar um alimento a partir do rótulo', 'Dodaj živilo z etikete', 'Pridať potravinu podľa etikety'],
        'add_recipe' => ['Add a recipe', 'Aggiungi una ricetta', 'Adicionar uma receita', 'Dodaj recept', 'Pridať recept'],
        'name' => ['Name', 'Nome', 'Nome', 'Ime', 'Názov'],
        'per100' => ['Per 100 g', 'Per 100 g', 'Por 100 g', 'Na 100 g', 'Na 100 g'],
        'optional' => ['optional', 'facoltativo', 'opcional', 'neobvezno', 'nepovinné'],
        'ingredients' => ['Ingredients', 'Ingredienti', 'Ingredientes', 'Sestavine', 'Ingrediencie'],
        'add_ing' => ['Add an ingredient', 'Aggiungi un ingrediente', 'Adicionar um ingrediente', 'Dodaj sestavino', 'Pridať ingredienciu'],
        'cooked' => ['Total weight when cooked (g)', 'Peso totale da cotto (g)', 'Peso total depois de cozinhado (g)', 'Skupna teža po kuhanju (g)', 'Celková hmotnosť po uvarení (g)'],
        'cooked_h' => ['Optional. Leave empty to use the sum of the ingredients.', 'Facoltativo. Lascia vuoto per usare la somma degli ingredienti.', 'Opcional. Deixa vazio para usar a soma dos ingredientes.', 'Neobvezno. Pusti prazno, da se uporabi vsota sestavin.', 'Nepovinné. Nechaj prázdne a použije sa súčet ingrediencií.'],
        'save' => ['Save', 'Salva', 'Guardar', 'Shrani', 'Uložiť'],
        'edit' => ['Edit', 'Modifica', 'Editar', 'Uredi', 'Upraviť'],
        'del' => ['Delete', 'Elimina', 'Apagar', 'Izbriši', 'Vymazať'],
        'delq' => ['Delete this?', 'Eliminare?', 'Apagar?', 'Izbrišem?', 'Vymazať?'],
        'myfood' => ['My food', 'Mio alimento', 'O meu alimento', 'Moje živilo', 'Moja potravina'],
        'myrecipe' => ['My recipe', 'Mia ricetta', 'A minha receita', 'Moj recept', 'Môj recept'],
        'need' => ['Please fill in the name and the kcal.', 'Inserisci il nome e le kcal.', 'Preenche o nome e as kcal.', 'Vpiši ime in kcal.', 'Vyplň názov a kcal.'],
        'need_r' => ['Please add a name and at least one ingredient.', 'Aggiungi un nome e almeno un ingrediente.', 'Adiciona um nome e pelo menos um ingrediente.', 'Dodaj ime in vsaj eno sestavino.', 'Pridaj názov a aspoň jednu ingredienciu.'],
        'none_mine' => ['No own foods or recipes yet.', 'Ancora nessun alimento o ricetta tua.', 'Ainda não tens alimentos nem receitas.', 'Še nimaš svojih živil ali receptov.', 'Zatiaľ nemáš vlastné potraviny ani recepty.'],
        'thread' => ['Messages with Marine', 'Messaggi con Marine', 'Mensagens com a Marine', 'Sporočila z Marine', 'Správy s Marine'],
        'ask' => ['Write to Marine about this day', 'Scrivi a Marine su questo giorno', 'Escreve à Marine sobre este dia', 'Piši Marine o tem dnevu', 'Napíš Marine o tomto dni'],
        'reply' => ['Reply', 'Rispondi', 'Responder', 'Odgovori', 'Odpovedať'],
        'send_r' => ['Send', 'Invia', 'Enviar', 'Pošlji', 'Odoslať'],
        'sent_err' => ['Not sent. Please try again.', 'Non inviato. Riprova.', 'Não enviado. Tenta de novo.', 'Ni poslano. Poskusi znova.', 'Neodoslané. Skús to znova.'],
        'you' => ['You', 'Tu', 'Tu', 'Ti', 'Ty'],
        'marine_rep' => ['Marine replied on your food diary', 'Marine ha risposto sul tuo diario alimentare', 'A Marine respondeu no teu diário alimentar', 'Marine je odgovorila v tvojem prehranskem dnevniku', 'Marine odpovedala v tvojom stravovacom denníku'],
        'matteo_rep' => ['Matteo replied on your food diary', 'Matteo ha risposto sul tuo diario alimentare', 'O Matteo respondeu no teu diário alimentar', 'Matteo je odgovoril v tvojem prehranskem dnevniku', 'Matteo odpovedal v tvojom stravovacom denníku'],
        'open' => ['Open my food diary', 'Apri il mio diario', 'Abrir o meu diário', 'Odpri moj dnevnik', 'Otvoriť môj denník'],
        'up_title' => ['Food diary with Marine', 'Diario alimentare con Marine', 'Diário alimentar com a Marine', 'Prehranski dnevnik z Marine', 'Stravovací denník s Marine'],
        'up_text' => ['With the Nutrition package, Marine Lenehan, our sports nutritionist, puts a daily nutrition plan in your training calendar and reviews a food diary you keep right here.',
                      'Con il pacchetto Nutrizione, Marine Lenehan, la nostra nutrizionista sportiva, inserisce ogni giorno un piano alimentare nel tuo calendario di allenamento e legge il diario alimentare che tieni proprio qui.',
                      'Com o pacote de Nutrição, a Marine Lenehan, a nossa nutricionista desportiva, coloca um plano alimentar diário no teu calendário de treino e revê o diário alimentar que manténs aqui mesmo.',
                      'S paketom Prehrana ti Marine Lenehan, naša športna nutricionistka, vsak dan v koledar treningov doda prehranski načrt in pregleda prehranski dnevnik, ki ga vodiš kar tukaj.',
                      'S balíkom Výživa ti Marine Lenehan, naša športová nutričná poradkyňa, dáva každý deň do tréningového kalendára plán stravovania a prezerá si stravovací denník, ktorý si vedieš priamo tu.'],
        'up_text2' => ['She works out your macros and gives you feedback on your fuelling for training and racing.', 'Calcola i tuoi macronutrienti e ti dà un riscontro su come ti alimenti per allenamenti e gare.', 'Ela calcula os teus macronutrientes e dá-te feedback sobre a tua alimentação para treinos e provas.', 'Izračuna tvoja makrohranila in ti svetuje glede prehrane za trening in tekme.', 'Vypočíta tvoje makroživiny a dá ti spätnú väzbu k tomu, ako sa stravuješ na tréningy a preteky.'],
        'up_more' => ['Find out more', 'Scopri di più', 'Saber mais', 'Več o tem', 'Zistiť viac'],
        'up_h' => ['How it works', 'Come funziona', 'Como funciona', 'Kako deluje', 'Ako to funguje'],
        'up_1' => ['Marine looks at your training and goals and sets your daily carbs, protein and fat.', 'Marine guarda i tuoi allenamenti e obiettivi e stabilisce carboidrati, proteine e grassi per ogni giorno.', 'A Marine analisa os teus treinos e objetivos e define os teus hidratos, proteína e gordura diários.', 'Marine pregleda tvoje treninge in cilje ter določi dnevne ogljikove hidrate, beljakovine in maščobe.', 'Marine sa pozrie na tvoje tréningy a ciele a určí ti denné sacharidy, bielkoviny a tuky.'],
        'up_2' => ['Each day’s nutrition plan appears in your training calendar, next to your sessions.', 'Il piano alimentare di ogni giorno compare nel tuo calendario di allenamento, accanto alle sedute.', 'O plano alimentar de cada dia aparece no teu calendário de treino, ao lado dos treinos.', 'Prehranski načrt za vsak dan se pojavi v tvojem koledarju treningov, ob treningih.', 'Plán stravovania na každý deň uvidíš v tréningovom kalendári, vedľa tréningov.'],
        'up_3' => ['You log your meals here in a few taps: a large food database, your own foods and recipes, and a photo if you like.', 'Registri i pasti qui in pochi tocchi: un grande database di alimenti, i tuoi alimenti e le tue ricette, e una foto se vuoi.', 'Registas as refeições aqui em poucos toques: uma grande base de dados de alimentos, os teus próprios alimentos e receitas, e uma foto se quiseres.', 'Obroke zapišeš tukaj v nekaj dotikih: velika baza živil, tvoja živila in recepti ter fotografija, če želiš.', 'Jedlá si tu zapíšeš na pár ťuknutí: veľká databáza potravín, tvoje vlastné potraviny a recepty a fotka, ak chceš.'],
        'up_4' => ['Marine reviews your diary and replies right here, with feedback on fuelling before, during and after your rides and races.', 'Marine legge il tuo diario e ti risponde qui, con consigli su cosa mangiare prima, durante e dopo uscite e gare.', 'A Marine revê o teu diário e responde aqui mesmo, com feedback sobre a alimentação antes, durante e depois dos treinos e provas.', 'Marine pregleda tvoj dnevnik in ti odgovori kar tukaj, z nasveti o prehrani pred, med in po vožnjah in tekmah.', 'Marine si prezrie tvoj denník a odpovie ti priamo tu, so spätnou väzbou k jedlu pred, počas a po jazdách a pretekoch.'],
        'up_ask' => ['Ask Matteo to add it to your coaching.', 'Chiedi a Matteo di aggiungerlo al tuo coaching.', 'Pede ao Matteo para o juntar ao teu coaching.', 'Prosi Mattea, naj ga doda tvojemu coachingu.', 'Požiadaj Mattea, aby ho pridal k tvojmu coachingu.'],
        'up_btn' => ['Marine’s nutrition coaching', 'Il coaching nutrizionale di Marine', 'O coaching de nutrição da Marine', 'Marinino prehransko svetovanje', 'Nutričný koučing s Marine'],
    ];
    static $I = ['en' => 0, 'it' => 1, 'pt' => 2, 'sl' => 3, 'sk' => 4];
    $l = $GLOBALS['cc_ath_lang'] ?? 'en';
    return $W[$k][$I[$l] ?? 0] ?? $W[$k][0];
}

/* ---------- data ---------- */
function cc_fd_on($pid) { return $pid && (bool) get_post_meta((int) $pid, 'cc_nutri_pkg', true); }
function cc_fd_is_nutri() { return is_user_logged_in() && current_user_can('cc_nutrition') && !cc_ath_is_coach(); }
function cc_fd_staff() { return cc_ath_is_coach() || cc_fd_is_nutri(); }
function cc_fd_date($d) { return function_exists('cc_av_date') ? cc_av_date((string) $d) : (preg_match('/^\d{4}-\d{2}-\d{2}$/', (string) $d) ? (string) $d : ''); }
function cc_fd_get($pid, $date) { $a = json_decode((string) get_post_meta((int) $pid, 'cc_fd_' . $date, true), true); return is_array($a) ? $a : ['s' => [], 'r' => []]; }
function cc_fd_put($pid, $date, $a) { update_post_meta((int) $pid, 'cc_fd_' . $date, wp_slash(wp_json_encode($a))); }
function cc_fd_mine($pid) { $a = json_decode((string) get_post_meta((int) $pid, 'cc_food_mine', true), true); return is_array($a) ? $a : []; }
function cc_fd_kg($pid) { $k = (float) get_post_meta((int) $pid, 'cc_food_kg', true); return $k > 0 ? $k : 0; }
function cc_fd_vx($pid) { $a = json_decode((string) get_post_meta((int) $pid, 'cc_food_vx', true), true); return is_array($a) ? $a : []; }
function cc_fd_num($v, $max) { $v = (float) str_replace(',', '.', (string) $v); return $v > 0 ? round(min($v, $max), 1) : 0; }
function cc_fd_txt($v, $n) { return mb_substr(trim(sanitize_text_field((string) $v)), 0, $n); }
function cc_fd_item($it) {
    if (!is_array($it)) return null;
    $o = ['id' => mb_substr(preg_replace('/[^A-Za-z0-9_-]/', '', (string) ($it['id'] ?? '')), 0, 40), 'n' => cc_fd_txt($it['n'] ?? '', 200), 'g' => cc_fd_num($it['g'] ?? 0, 5000)];
    foreach (['k' => 950, 'c' => 100, 'p' => 100, 'f' => 100, 'fi' => 100, 'su' => 100] as $f => $mx) $o[$f] = cc_fd_num($it[$f] ?? 0, $mx);
    if (in_array($it['m'] ?? '', ['f', 'r'], true)) $o['m'] = $it['m'];
    return $o['n'] === '' ? null : $o;
}
/* what the client sends for a day: the slots only (photos are set by their own route, replies by theirs) */
function cc_fd_clean_slots($in, $old) {
    $out = [];
    foreach (CC_FD_SLOTS as $k) {
        $s = is_array($in[$k] ?? null) ? $in[$k] : [];
        $t = preg_match('/^([01]\d|2[0-3]):[0-5]\d$/', (string) ($s['t'] ?? '')) ? $s['t'] : '';
        $items = [];
        foreach (array_slice((array) ($s['i'] ?? []), 0, 60) as $it) { $c = cc_fd_item($it); if ($c) $items[] = $c; }
        $o = ['t' => $t, 'n' => mb_substr(trim(sanitize_textarea_field((string) ($s['n'] ?? ''))), 0, 1000), 'i' => $items];
        if (!empty($old[$k]['ph'])) $o['ph'] = (int) $old[$k]['ph'];
        if ($o['t'] !== '' || $o['n'] !== '' || $o['i'] || !empty($o['ph'])) $out[$k] = $o;
    }
    return $out;
}
function cc_fd_tot($items) {
    $t = ['k' => 0, 'c' => 0, 'p' => 0, 'f' => 0, 'fi' => 0, 'su' => 0];
    foreach ((array) $items as $it) { $m = ((float) ($it['g'] ?? 0)) / 100; foreach ($t as $f => $_) $t[$f] += ((float) ($it[$f] ?? 0)) * $m; }
    return $t;
}
function cc_fd_daytot($day) { $all = []; foreach ((array) ($day['s'] ?? []) as $s) foreach ((array) ($s['i'] ?? []) as $it) $all[] = $it; return cc_fd_tot($all); }
/* the day as the browser gets it: photo URLs added */
function cc_fd_out($pid, $date) {
    $d = cc_fd_get($pid, $date); $s = [];
    foreach ((array) ($d['s'] ?? []) as $k => $v) { if (!empty($v['ph'])) { $u = wp_get_attachment_url((int) $v['ph']); if ($u) $v['phu'] = $u; else unset($v['ph']); } $s[$k] = $v; }
    return ['date' => $date, 's' => (object) $s, 'r' => array_values((array) ($d['r'] ?? []))];
}
function cc_fd_days($pid) {   // the dates with an entry, newest first
    $o = []; foreach (array_keys((array) get_post_meta((int) $pid)) as $k) if (preg_match('/^cc_fd_(\d{4}-\d{2}-\d{2})$/', $k, $m)) $o[] = $m[1];
    rsort($o); return $o;
}
function cc_fd_to($email) { return strpos(home_url(), '//staging.') !== false ? (string) get_option('cc_staging_notify', '') : (string) $email; }   // staging: never a real person
function cc_fd_mail($to, $subject, $html) {
    if (!is_email($to)) return false;
    return wp_mail($to, $subject, $html, ['Content-Type: text/html; charset=UTF-8', 'From: Matteo Cigala <coaching@cigalacycling.com>', 'Reply-To: Matteo Cigala <matteo@cigalacycling.com>']);
}
function cc_fd_hub() { return home_url('/' . CC_ATH_SLUG . '/'); }

/* Marine may open a food photo of a package athlete (blood.php lets her open shared blood tests) */
add_filter('cc_ath_file_ok', function ($ok, $id) {
    if ($ok || !cc_fd_is_nutri() || !get_post_meta($id, 'cc_food_photo', true)) return $ok;
    return cc_fd_on(wp_get_post_parent_id($id));
}, 11, 2);

/* ---------- the athlete's hub ---------- */
function cc_fd_upgrade() {
    $li = ''; foreach (['up_1', 'up_2', 'up_3', 'up_4'] as $k) $li .= '<li>' . esc_html(cc_fd_w($k)) . '</li>';
    return '<section class="ath-s fd-up" id="food-info"><h2>' . cc_ath_icon('food', 'ath-hic') . esc_html(cc_fd_w('up_title')) . '</h2>'
        . '<p class="fd-lede">' . esc_html(cc_fd_w('up_text')) . ' ' . esc_html(cc_fd_w('up_text2')) . '</p>'
        . '<details class="fd-more"><summary class="btn btn-ghost">' . esc_html(cc_fd_w('up_more')) . '</summary><div class="fd-morep"><h3>' . esc_html(cc_fd_w('up_h')) . '</h3><ol>' . $li . '</ol>'
        . '<p>' . esc_html(cc_fd_w('up_ask')) . '</p><a class="btn btn-go" href="' . esc_url(CC_FD_MARINE_URL) . '" target="_blank" rel="noopener">' . esc_html(cc_fd_w('up_btn')) . '</a></div></details></section>' . cc_fd_css();
}
function cc_fd_athlete($pid) {
    $date = cc_fd_date($_GET['fd'] ?? '') ?: current_time('Y-m-d');
    $W = []; foreach (['time', 'add', 'search', 'grams', 'addit', 'remove', 'cancel', 'noresults', 'loading', 'slot_total', 'day_total', 'carbs', 'protein', 'fat', 'fibre', 'sugars', 'c_ab', 'p_ab', 'f_ab',
                       'weight', 'weight_h', 'note', 'note_ph', 'photo', 'photo_ch', 'photo_del', 'photo_bad', 'uploading', 'saving', 'saved', 'err', 'prev', 'next', 'today', 'gotoday', 'mine', 'mine_lede',
                       'add_label', 'add_recipe', 'name', 'per100', 'optional', 'ingredients', 'add_ing', 'cooked', 'cooked_h', 'save', 'edit', 'del', 'delq', 'myfood', 'myrecipe', 'need', 'need_r',
                       'none_mine', 'thread', 'ask', 'reply', 'send_r', 'sent_err', 'you'] as $k) $W[$k] = cc_fd_w($k);
    $slots = []; foreach (CC_FD_SLOTS as $k) $slots[] = [$k, cc_fd_w($k)];
    $u = function ($p) { return esc_url_raw(rest_url('cc/v1/' . $p)); };
    $cfg = ['page' => (int) $pid, 'date' => $date, 'fixed' => isset($_GET['fd']) ? 1 : 0, 'lang' => $GLOBALS['cc_ath_lang'] ?? 'en', 'nonce' => wp_create_nonce('wp_rest'), 'w' => $W, 'slots' => $slots,
            'day' => cc_fd_out($pid, $date), 'mine' => cc_fd_mine($pid), 'kg' => cc_fd_kg($pid) ?: '', 'credit' => 'Food data: ANSES-CIQUAL · USDA FoodData Central',
            'foods' => esc_url_raw(add_query_arg('v', get_option('cc_food_db_v', '0'), rest_url('cc/v1/foods'))),
            'u' => ['day' => $u('food-day'), 'save' => $u('food-day'), 'photo' => $u('food-photo'), 'photodel' => $u('food-photo-del'), 'mine' => $u('food-mine'), 'kg' => $u('food-kg'), 'reply' => $u('food-reply')]];
    return '<section class="ath-s fd" id="food"><h2>' . cc_ath_icon('food', 'ath-hic') . esc_html(cc_fd_w('title')) . '</h2><p class="fd-lede">' . esc_html(cc_fd_w('lede')) . '</p>'
        . '<div class="fd-app" data-cfg="' . esc_attr(wp_json_encode($cfg)) . '"><div class="fd-day"></div><div class="fd-minebox"></div></div></section>' . cc_fd_css() . cc_fd_js();
}
function cc_fd_coach_card($pid) {
    $on = cc_fd_on($pid); $days = $on ? cc_fd_days($pid) : [];
    return '<section class="ath-s fd" id="food"><h2>' . cc_ath_icon('food', 'ath-hic') . 'Food diary</h2>'
        . '<p class="fd-lede">Nutrition package: with it on, the athlete gets the food diary and Marine Lenehan can review it (and her Vekta nutrition notes are matched to each day). Without it, the athlete sees a short card about the package.</p>'
        . cc_fd_switch($pid)
        . ($on ? '<p class="fd-lede">' . ($days ? 'Last entry: <b>' . esc_html(date_i18n('D j M', strtotime($days[0] . ' 12:00'))) . '</b> · ' . count($days) . ' day' . (count($days) === 1 ? '' : 's') . ' logged.' : 'Nothing logged yet.') . '</p>'
              . '<p><a class="btn btn-go" href="' . esc_url(add_query_arg(['board' => 'food', 'ath' => (int) $pid], cc_fd_hub())) . '">Open the food diary</a></p>' : '')
        . '</section>' . cc_fd_css() . cc_fd_rjs();
}
function cc_fd_switch($pid) {
    $on = cc_fd_on($pid);
    return '<p class="fd-sw"><button type="button" class="fd-pkg' . ($on ? ' on' : '') . '" role="switch" aria-checked="' . ($on ? 'true' : 'false') . '" data-page="' . (int) $pid . '"><span class="fd-knob"></span></button>'
         . '<span>Nutrition package: <b>' . ($on ? 'on' : 'off') . '</b></span></p>';
}
add_filter('cc_ath_after_reports', function ($html, $view, $coach) {
    if (!$view || get_post_meta($view, 'cc_shared', true)) return $html;
    // Matteo 19 Nov: on his demo page (no login) he sees the athlete's own diary too, so he can try it as an athlete would
    if ($coach) return $html . cc_fd_coach_card($view) . (get_post_meta($view, 'cc_demo', true) && cc_fd_on($view) ? cc_fd_athlete($view) : '');
    // the upgrade card only once Matteo launches the diary (option cc_fd_launched); until then athletes without the package see nothing
    return $html . (cc_fd_on($view) ? cc_fd_athlete($view) : (get_option('cc_fd_launched') ? cc_fd_upgrade() : ''));
}, 18, 3);
add_filter('cc_ath_nav', function ($nav, $view, $coach) { if ($view && !$coach && cc_fd_on($view)) $nav[] = ['food', cc_fd_w('title')]; return $nav; }, 32, 3);

/* ---------- Marine's and Matteo's review ---------- */
function cc_fd_hm($sec) { $sec = (int) $sec; if ($sec <= 0) return ''; $h = intdiv($sec, 3600); $m = intdiv($sec % 3600, 60); return $h ? $h . 'h' . sprintf('%02d', $m) : $m . ' min'; }
function cc_fd_f1($x) { return rtrim(rtrim(number_format((float) $x, 1, '.', ''), '0'), '.'); }
function cc_fd_vx_day($vx, $d, $what) {
    $o = [];
    foreach ((array) ($vx[$what] ?? []) as $x) if (($x['d'] ?? '') === $d) $o[] = $x;
    return $o;
}
function cc_fd_plan_line($p) {
    return esc_html($p['n'] ?: 'Session') . ($p['min'] ? ' · ' . esc_html(cc_fd_hm($p['min'] * 60)) : '') . (!empty($p['carb']) ? ' · ' . (int) $p['carb'] . ' g/h carbs planned' : '');
}
function cc_fd_training_html($vx, $d, $label) {
    $done = cc_fd_vx_day($vx, $d, 'done'); $plan = cc_fd_vx_day($vx, $d, 'plan'); $o = '';
    foreach ($done as $a) $o .= '<li>✓ ' . esc_html($a['n'] ?: 'Session') . ($a['min'] ? ' · ' . esc_html(cc_fd_hm($a['min'] * 60)) : '') . ($a['kj'] ? ' · ' . (int) $a['kj'] . ' kJ' : '') . '</li>';
    if (!$done) foreach ($plan as $p) $o .= '<li>Planned: ' . cc_fd_plan_line($p) . '</li>';
    return '<div class="fd-vxb"><h4>' . esc_html($label) . '</h4>' . ($o ? '<ul>' . $o . '</ul>' : '<p class="fd-muted">Rest day (nothing planned)</p>') . '</div>';
}
function cc_fd_notes_html($vx, $d, $label) {
    $o = '';
    foreach (cc_fd_vx_day($vx, $d, 'notes') as $n) {
        $c = (string) ($n['c'] ?? '');
        $o .= '<div class="fd-vnote"><b>' . esc_html($n['t'] ?: 'Nutrition') . '</b>' . ($c !== '' ? (mb_strlen($c) > 260 ? '<details><summary>' . esc_html(mb_substr($c, 0, 220)) . '… <span class="fd-link">more</span></summary><p>' . nl2br(esc_html($c)) . '</p></details>' : '<p>' . nl2br(esc_html($c)) . '</p>') : '') . '</div>';
    }
    return '<div class="fd-vxb"><h4>' . esc_html($label) . '</h4>' . ($o ?: '<p class="fd-muted">No nutrition note</p>') . '</div>';
}
function cc_fd_thread_html($pid, $date, $replies, $viewer) {
    $o = '';
    foreach ((array) $replies as $r) {
        $who = $r['from'] ?? 'coach';
        $face = $who === 'athlete' ? (function_exists('cc_ph_widget') ? cc_ph_widget($pid, 30, false, 'nt-me-a') : '')
              : '<img class="nt-me" src="' . esc_url($who === 'nutri' ? 'https://coaching.cigalacycling.com/wp-content/uploads/2026/11/vivify-tile.png' : 'https://coaching.cigalacycling.com/wp-content/uploads/2026/11/cigala-email-matteo-photo.jpg') . '" width="30" height="30" alt="">';
        $label = $who === 'athlete' ? get_the_title($pid) : ($who === 'nutri' ? 'Marine' : 'Matteo');
        $o .= '<div class="nt-rep' . ($who === 'athlete' ? ' nt-rep-a' : '') . '"><span class="nt-rh">' . $face . '<b>' . esc_html($label) . '</b> <small>' . esc_html(date_i18n('j M, H:i', (int) $r['at'])) . '</small></span><p>' . nl2br(esc_html($r['text'])) . '</p></div>';
    }
    return $o . '<details class="nt-replyd"><summary>Reply to ' . esc_html(get_the_title($pid)) . ' about this day</summary><div class="fd-r" data-page="' . (int) $pid . '" data-date="' . esc_attr($date) . '"><textarea rows="3"></textarea>'
        . '<button type="button" class="btn btn-go fd-send">Send</button></div></details>';
}
function cc_fd_day_html($pid, $date, $vx, $tp, $kg, $viewer) {
    $d = cc_fd_get($pid, $date); $t = cc_fd_daytot($d); $has = false;
    $ts = strtotime($date . ' 12:00'); $next = gmdate('Y-m-d', $ts + DAY_IN_SECONDS);
    $o = '<article class="fd-rd" id="fd-' . esc_attr($date) . '"><h3>' . esc_html(date_i18n('l j F', $ts)) . ($date === current_time('Y-m-d') ? ' <small>today</small>' : '') . '</h3>';
    $sl = '';
    foreach (CC_FD_SLOTS as $k) {
        $s = $d['s'][$k] ?? null; if (!$s) continue;
        $has = true; $st = cc_fd_tot($s['i'] ?? []);
        $sl .= '<div class="fd-rs"><div class="fd-rsh"><b>' . esc_html(cc_fd_w($k)) . '</b>' . (!empty($s['t']) ? ' <span class="fd-time-b">' . esc_html($s['t']) . '</span>' : '')
             . (!empty($s['i']) ? '<span class="fd-rst">' . round($st['k']) . ' kcal · C ' . cc_fd_f1($st['c']) . ' · P ' . cc_fd_f1($st['p']) . ' · F ' . cc_fd_f1($st['f']) . '</span>' : '') . '</div>';
        if (!empty($s['i'])) {
            $sl .= '<ul class="fd-ri">';
            foreach ($s['i'] as $it) { $m = ((float) $it['g']) / 100;
                $sl .= '<li><span>' . esc_html($it['n']) . (!empty($it['m']) ? ' <span class="fd-tag">' . ($it['m'] === 'r' ? 'own recipe' : 'own food') . '</span>' : '') . '</span><small>' . cc_fd_f1($it['g']) . ' g · ' . round($it['k'] * $m) . ' kcal · C ' . cc_fd_f1($it['c'] * $m) . ' · P ' . cc_fd_f1($it['p'] * $m) . ' · F ' . cc_fd_f1($it['f'] * $m) . '</small></li>'; }
            $sl .= '</ul>';
        }
        if (!empty($s['n'])) $sl .= '<p class="fd-rn">“' . nl2br(esc_html($s['n'])) . '”</p>';
        if (!empty($s['ph']) && ($u = wp_get_attachment_url((int) $s['ph']))) $sl .= '<a class="fd-rph" href="' . esc_url($u) . '" target="_blank" rel="noopener"><img src="' . esc_url($u) . '" alt="Photo of ' . esc_attr(cc_fd_w($k)) . '" loading="lazy"></a>';
        $sl .= '</div>';
    }
    if ($has) {
        $o .= $sl . '<div class="fd-rtot"><b>Day total</b><span>' . round($t['k']) . ' kcal</span><span>Carbs ' . round($t['c']) . ' g' . ($kg ? ' (' . cc_fd_f1($t['c'] / $kg) . ' g/kg)' : '') . '</span>'
            . '<span>Protein ' . round($t['p']) . ' g' . ($kg ? ' (' . cc_fd_f1($t['p'] / $kg) . ' g/kg)' : '') . '</span><span>Fat ' . round($t['f']) . ' g</span><span>Fibre ' . round($t['fi']) . ' g</span><span>Sugars ' . round($t['su']) . ' g</span></div>';
    } else $o .= '<p class="fd-muted">Nothing logged.</p>';
    if (!$tp && $vx) $o .= '<div class="fd-vx">' . cc_fd_training_html($vx, $date, 'Training this day') . cc_fd_training_html($vx, $next, 'Training next day')
        . cc_fd_notes_html($vx, $date, 'Your nutrition note this day') . cc_fd_notes_html($vx, $next, 'Your nutrition note next day') . '</div>';
    return $o . '<div class="fd-th">' . cc_fd_thread_html($pid, $date, $d['r'] ?? [], $viewer) . '</div></article>';
}
function cc_fd_week_ahead($vx) {
    $o = ''; $t0 = strtotime(current_time('Y-m-d') . ' 12:00');
    for ($i = 0; $i < 7; $i++) {
        $d = gmdate('Y-m-d', $t0 + $i * DAY_IN_SECONDS); $p = cc_fd_vx_day($vx, $d, 'plan'); $n = cc_fd_vx_day($vx, $d, 'notes');
        $o .= '<div class="fd-wk"><b>' . esc_html(date_i18n('D j M', $t0 + $i * DAY_IN_SECONDS)) . '</b>'
            . ($p ? implode('', array_map(function ($x) { return '<span>' . cc_fd_plan_line($x) . '</span>'; }, $p)) : '<span class="fd-muted">Rest / nothing planned</span>')
            . ($n ? implode('', array_map(function ($x) { return '<details class="fd-wkn"><summary>🥗 ' . esc_html($x['t'] ?: 'Nutrition note') . '</summary>' . (!empty($x['c']) ? '<p>' . nl2br(esc_html($x['c'])) . '</p>' : '') . '</details>'; }, $n)) : '<span class="fd-warn-n">No nutrition note yet</span>')
            . '</div>';
    }
    return '<div class="fd-week"><h3>Week ahead</h3><div class="fd-wkg">' . $o . '</div></div>';
}
function cc_fd_review($pid, $viewer) {
    $GLOBALS['cc_ath_lang'] = 'en';
    $off = max(0, (int) ($_GET['fo'] ?? 0)); $tp = cc_ath_tp($pid); $vx = $tp ? [] : cc_fd_vx($pid); $kg = cc_fd_kg($pid);
    $back = $viewer === 'nutri' ? cc_fd_hub() : add_query_arg('board', 'food', cc_fd_hub());
    $o = '<section class="ath-s fd-rv"><p class="fd-back"><a href="' . esc_url($back) . '">← All food diaries</a></p>'
       . '<h2>' . (function_exists('cc_ph_face') ? cc_ph_face($pid, 36) . ' ' : '') . esc_html(get_the_title($pid)) . '</h2>'
       . '<p class="fd-lede">Food diary, newest day first' . ($kg ? ' · weight ' . cc_fd_f1($kg) . ' kg (from the athlete)' : ' · no weight entered by the athlete') . '.'
       . (!$tp && !empty($vx['at']) ? ' Training and nutrition notes updated ' . esc_html(human_time_diff((int) $vx['at'])) . ' ago.' : '') . '</p>' . cc_fd_switch($pid);
    if (!$tp && $vx) $o .= cc_fd_week_ahead($vx);
    $t0 = strtotime(current_time('Y-m-d') . ' 12:00') - $off * 14 * DAY_IN_SECONDS;
    for ($i = 0; $i < 14; $i++) $o .= cc_fd_day_html($pid, gmdate('Y-m-d', $t0 - $i * DAY_IN_SECONDS), $vx, $tp, $kg, $viewer);
    $o .= '<p class="fd-pager">' . ($off ? '<a class="btn btn-ghost" href="' . esc_url(add_query_arg('fo', $off - 1)) . '">Newer days</a> ' : '') . '<a class="btn btn-ghost" href="' . esc_url(add_query_arg('fo', $off + 1)) . '">Older days</a></p>';
    return $o . '</section>' . cc_fd_css() . cc_fd_rjs() . (function_exists('cc_nt_css') ? cc_nt_css() : '') . (function_exists('cc_ph_assets') ? cc_ph_assets() : '');
}
function cc_fd_pkg_pages() { return get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'numberposts' => -1, 'orderby' => 'title', 'order' => 'ASC', 'meta_key' => 'cc_nutri_pkg', 'meta_value' => '1']); }
function cc_fd_list($viewer) {
    $o = '<section class="ath-s fd-rv" id="food-diaries"><h2>' . cc_ath_icon('food', 'ath-hic') . 'Food diaries</h2><p class="fd-lede">Athletes with the Nutrition package. Open one to see each day with the training and your nutrition notes, and reply under any day: the athlete gets an email and a notification.</p>';
    $ps = cc_fd_pkg_pages();
    if (!$ps) $o .= '<p class="fd-muted">No athlete has the Nutrition package yet.</p>';
    foreach ($ps as $p) {
        $days = cc_fd_days($p->ID); $last = $days ? $days[0] : ''; $wait = 0;
        foreach (array_slice($days, 0, 14) as $d) { $r = (array) (cc_fd_get($p->ID, $d)['r'] ?? []); if ($r && (end($r)['from'] ?? '') === 'athlete') $wait++; }
        $o .= '<a class="fd-al" href="' . esc_url($viewer === 'nutri' ? add_query_arg('food', $p->ID, cc_fd_hub()) : add_query_arg(['board' => 'food', 'ath' => $p->ID], cc_fd_hub())) . '">'
            . (function_exists('cc_ph_face') ? cc_ph_face($p->ID, 32) : '') . '<span><b>' . esc_html($p->post_title) . '</b><small>' . ($last ? 'Last entry ' . esc_html(date_i18n('D j M', strtotime($last . ' 12:00'))) : 'Nothing logged yet') . '</small></span>'
            . ($wait ? '<span class="av-badge fd-badge">' . $wait . ' to answer</span>' : '') . '</a>';
    }
    if ($viewer === 'nutri') $o .= '<details class="fd-addath"><summary>Add an athlete to the Nutrition package</summary><div class="fd-addf"><label>Athlete’s email (the one they log in with)<input type="email" class="fd-addmail" autocomplete="off"></label><button type="button" class="btn btn-go fd-addgo">Add</button><p class="fd-msg" role="status"></p></div></details>';
    return $o . '</section>' . cc_fd_css() . cc_fd_rjs() . (function_exists('cc_ph_assets') ? cc_ph_assets() : '');
}
/* Marine's view: her food diaries after the blood tests; ?food=<page> opens one athlete */
add_filter('cc_ath_nutritionist', function ($html, $me) {
    if (!user_can($me, 'cc_nutrition')) return $html;
    $pid = (int) ($_GET['food'] ?? 0);
    if ($pid && get_post_type($pid) === 'cc_athlete' && cc_fd_on($pid)) return cc_fd_review($pid, 'nutri');
    return $html . cc_fd_list('nutri');
}, 20, 2);
/* Matteo's board */
add_filter('cc_ath_coach_links', function ($html) {
    return $html . '<a class="av-boardlink" href="' . esc_url(add_query_arg('board', 'food', cc_fd_hub())) . '">Food diaries</a>';
}, 21);
add_filter('cc_ath_board', function ($html, $board) {
    if ($board !== 'food' || !cc_ath_is_coach()) return $html;
    $pid = (int) ($_GET['ath'] ?? 0);
    if ($pid && get_post_type($pid) === 'cc_athlete') return cc_fd_review($pid, 'coach');
    return cc_fd_list('coach');
}, 10, 2);

/* ---------- REST ---------- */
add_action('rest_api_init', function () {
    $mine = function (WP_REST_Request $r) {   // the athlete's own page with the package on (Matteo may act on any page)
        if (cc_ath_is_coach()) return true;
        $p = cc_ath_page_of(get_current_user_id());
        return $p && (int) ($r->get_param('page') ?: $p) === $p && cc_fd_on($p);
    };
    $page = function (WP_REST_Request $r) { return cc_ath_is_coach() ? (int) $r->get_param('page') : cc_ath_page_of(get_current_user_id()); };
    // the food database: open data, the same for everyone, cached by the browser for a year (the URL carries the version)
    register_rest_route('cc/v1', '/foods', ['methods' => 'GET', 'permission_callback' => '__return_true', 'callback' => function () {
        $gz = (string) get_option('cc_food_db_gz', ''); $raw = $gz === '' ? (string) get_option('cc_food_db', '') : '';
        if ($gz === '' && $raw === '') return new WP_Error('cc_none', 'No food data yet', ['status' => 404]);
        while (ob_get_level()) ob_end_clean();
        header_remove('Expires'); header_remove('Pragma'); header_remove('Set-Cookie');
        header('Content-Type: application/json; charset=utf-8'); header('Cache-Control: public, max-age=31536000, immutable'); header('Vary: Accept-Encoding');
        if ($gz !== '') {
            $b = base64_decode($gz);
            if (strpos((string) ($_SERVER['HTTP_ACCEPT_ENCODING'] ?? ''), 'gzip') !== false) { header('Content-Encoding: gzip'); header('Content-Length: ' . strlen($b)); echo $b; exit; }
            $raw = (string) gzdecode($b);
        }
        header('Content-Length: ' . strlen($raw)); echo $raw; exit;
    }]);
    register_rest_route('cc/v1', '/food-db', ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        $d = (string) $r->get_param('data'); $j = json_decode($d, true);
        if (!is_array($j) || empty($j['foods']) || !is_array($j['foods'])) return new WP_Error('cc_bad', 'Not a food table', ['status' => 400]);
        update_option('cc_food_db', $d, false);
        update_option('cc_food_db_gz', function_exists('gzencode') ? base64_encode(gzencode($d, 9)) : '', false);
        update_option('cc_food_db_v', substr(md5($d), 0, 10), false);
        return ['ok' => true, 'foods' => count($j['foods']), 'bytes' => strlen($d), 'v' => get_option('cc_food_db_v')];
    }]);
    register_rest_route('cc/v1', '/food-day', ['methods' => 'GET', 'permission_callback' => function (WP_REST_Request $r) use ($mine) { return cc_fd_is_nutri() ? cc_fd_on((int) $r->get_param('page')) : $mine($r); }, 'callback' => function (WP_REST_Request $r) use ($page) {
        $pid = cc_fd_is_nutri() ? (int) $r->get_param('page') : $page($r); $d = cc_fd_date($r->get_param('date'));
        if (!$pid || !$d) return new WP_Error('cc_bad', 'Page and date needed', ['status' => 400]);
        return cc_fd_out($pid, $d);
    }]);
    register_rest_route('cc/v1', '/food-day', ['methods' => 'POST', 'permission_callback' => $mine, 'callback' => function (WP_REST_Request $r) use ($page) {
        $pid = $page($r); $d = cc_fd_date($r->get_param('date')); $in = json_decode((string) $r->get_param('data'), true);
        if (!$pid || !$d || !is_array($in)) return new WP_Error('cc_bad', 'Page, date and data needed', ['status' => 400]);
        $cur = cc_fd_get($pid, $d); $cur['s'] = cc_fd_clean_slots($in, (array) ($cur['s'] ?? [])); $cur['u'] = time();
        if (!$cur['s'] && empty($cur['r'])) delete_post_meta($pid, 'cc_fd_' . $d); else cc_fd_put($pid, $d, $cur);
        return ['ok' => true];
    }]);
    register_rest_route('cc/v1', '/food-photo', ['methods' => 'POST', 'permission_callback' => $mine, 'callback' => function (WP_REST_Request $r) use ($page) {
        $pid = $page($r); $d = cc_fd_date($r->get_param('date')); $k = (string) $r->get_param('slot'); $f = $r->get_file_params()['file'] ?? null;
        if (!$pid || !$d || !in_array($k, CC_FD_SLOTS, true)) return new WP_Error('cc_bad', 'Date and slot needed', ['status' => 400]);
        if (!$f || empty($f['tmp_name']) || $f['error'] || $f['size'] > 10485760) return new WP_Error('cc_bad', 'No file or too big', ['status' => 400]);
        $bytes = file_get_contents($f['tmp_name']); $ft = wp_check_filetype_and_ext($f['tmp_name'], $f['name']);
        $ext = strtolower((string) ($ft['ext'] ?: pathinfo($f['name'], PATHINFO_EXTENSION)));
        $ok = ['jpg' => 'image/jpeg', 'jpeg' => 'image/jpeg', 'png' => 'image/png', 'webp' => 'image/webp', 'heic' => 'image/heic', 'heif' => 'image/heif'];
        if (!isset($ok[$ext]) || (in_array($ext, ['jpg', 'jpeg', 'png', 'webp'], true) && !@getimagesizefromstring($bytes))) return new WP_Error('cc_bad', 'Photo only', ['status' => 400]);
        $id = cc_f_store($pid, $bytes, 'food', $ext, $ok[$ext], 'Food photo'); if (!$id) return new WP_Error('cc_fail', 'Could not save', ['status' => 500]);
        update_post_meta($id, 'cc_food_photo', 1);
        $cur = cc_fd_get($pid, $d); $s = (array) ($cur['s'][$k] ?? ['t' => '', 'n' => '', 'i' => []]);
        if (!empty($s['ph'])) wp_delete_attachment((int) $s['ph'], true);
        $s['ph'] = $id; $cur['s'][$k] = $s; $cur['u'] = time(); cc_fd_put($pid, $d, $cur);
        return ['ok' => true, 'id' => $id, 'url' => wp_get_attachment_url($id)];
    }]);
    register_rest_route('cc/v1', '/food-photo-del', ['methods' => 'POST', 'permission_callback' => $mine, 'callback' => function (WP_REST_Request $r) use ($page) {
        $pid = $page($r); $d = cc_fd_date($r->get_param('date')); $k = (string) $r->get_param('slot');
        $cur = cc_fd_get($pid, $d);
        if (!empty($cur['s'][$k]['ph'])) { wp_delete_attachment((int) $cur['s'][$k]['ph'], true); unset($cur['s'][$k]['ph']); cc_fd_put($pid, $d, $cur); }
        return ['ok' => true];
    }]);
    register_rest_route('cc/v1', '/food-mine', ['methods' => 'POST', 'permission_callback' => $mine, 'callback' => function (WP_REST_Request $r) use ($page) {
        $pid = $page($r); $in = json_decode((string) $r->get_param('data'), true); if (!$pid || !is_array($in)) return new WP_Error('cc_bad', 'Data needed', ['status' => 400]);
        $out = [];
        foreach (array_slice($in, 0, 300) as $m) {
            $c = cc_fd_item(array_merge((array) $m, ['g' => 100])); if (!$c) continue;
            unset($c['g'], $c['m']); $c['t'] = ($m['t'] ?? '') === 'r' ? 'r' : 'f'; $c['id'] = preg_match('/^M[a-z0-9]{1,20}$/', (string) ($m['id'] ?? '')) ? $m['id'] : 'M' . base_convert((string) (time() . wp_rand(10, 99)), 10, 36);
            if ($c['t'] === 'r') { $c['ing'] = []; foreach (array_slice((array) ($m['ing'] ?? []), 0, 40) as $i) { $ci = cc_fd_item($i); if ($ci) $c['ing'][] = $ci; } $c['cw'] = cc_fd_num($m['cw'] ?? 0, 20000); }
            $out[] = $c;
        }
        update_post_meta($pid, 'cc_food_mine', wp_slash(wp_json_encode($out)));
        return ['ok' => true, 'mine' => $out];
    }]);
    register_rest_route('cc/v1', '/food-kg', ['methods' => 'POST', 'permission_callback' => $mine, 'callback' => function (WP_REST_Request $r) use ($page) {
        $pid = $page($r); $k = cc_fd_num($r->get_param('kg'), 250);
        if ($k >= 25) update_post_meta($pid, 'cc_food_kg', $k); else delete_post_meta($pid, 'cc_food_kg');
        return ['ok' => true, 'kg' => $k >= 25 ? $k : 0];
    }]);
    // the package switch: Matteo on any athlete; Marine on a package athlete (off), or by the athlete's login email (on)
    register_rest_route('cc/v1', '/food-pkg', ['methods' => 'POST', 'permission_callback' => 'cc_fd_staff', 'callback' => function (WP_REST_Request $r) {
        $pid = (int) $r->get_param('page');
        if (!$pid && ($e = sanitize_email((string) $r->get_param('email')))) { $u = get_user_by('email', $e); $pid = $u ? cc_ath_page_of($u->ID) : 0; if (!$pid) return new WP_Error('cc_none', 'No athlete with that email', ['status' => 404]); }
        if (!$pid || get_post_type($pid) !== 'cc_athlete' || get_post_meta($pid, 'cc_shared', true)) return new WP_Error('cc_bad', 'Unknown athlete', ['status' => 400]);
        if (cc_fd_is_nutri() && !cc_fd_on($pid) && !$r->get_param('email')) return new WP_Error('cc_no', 'Not allowed', ['status' => 403]);
        $on = (bool) $r->get_param('on');
        if ($on) update_post_meta($pid, 'cc_nutri_pkg', 1); else delete_post_meta($pid, 'cc_nutri_pkg');
        return ['ok' => true, 'page' => $pid, 'name' => get_the_title($pid), 'on' => $on];
    }]);
    // a reply under a day: Matteo, the nutritionist (package athletes) or the athlete (own diary)
    register_rest_route('cc/v1', '/food-reply', ['methods' => 'POST', 'permission_callback' => 'is_user_logged_in', 'callback' => function (WP_REST_Request $r) {
        $pid = (int) $r->get_param('page'); $d = cc_fd_date($r->get_param('date')); $text = trim(sanitize_textarea_field((string) $r->get_param('text')));
        if (!$d || $text === '' || mb_strlen($text) > 3000) return new WP_Error('cc_bad', 'Empty or too long', ['status' => 400]);
        $from = cc_ath_is_coach() ? 'coach' : (cc_fd_is_nutri() ? 'nutri' : ((int) cc_ath_page_of(get_current_user_id()) === $pid ? 'athlete' : ''));
        if ($from === '' || !cc_fd_on($pid)) return new WP_Error('cc_no', 'Not allowed', ['status' => 403]);
        $cur = cc_fd_get($pid, $d); $cur['r'][] = ['at' => time(), 'from' => $from, 'text' => $text]; cc_fd_put($pid, $d, $cur);
        $name = get_the_title($pid); $nice = date_i18n('j M', strtotime($d . ' 12:00'));
        if ($from !== 'athlete') {   // the athlete: bell + phone + email, in their language
            $uid = (int) get_post_meta($pid, 'cc_user', true);
            if ($uid) { $keep = $GLOBALS['cc_ath_lang'] ?? 'en'; $GLOBALS['cc_ath_lang'] = cc_ath_user_lang($uid);
                $url = add_query_arg('fd', $d, cc_fd_hub()) . '#food'; $title = cc_fd_w($from === 'nutri' ? 'marine_rep' : 'matteo_rep');
                if (function_exists('cc_push_user')) cc_push_user($uid, $title, wp_trim_words($text, 18), $url, 'cc-food-' . $d);
                $au = get_userdata($uid);
                if ($au && function_exists('cc_ath_mail_shell')) cc_fd_mail(cc_fd_to($au->user_email), $title, cc_ath_mail_shell(sprintf(cc_L('Hi %s,', 'Ciao %s,'), esc_html($au->first_name ?: $au->display_name)), nl2br(esc_html($text)), cc_fd_w('open'), $url));
                $GLOBALS['cc_ath_lang'] = $keep; }
        } else {   // the athlete wrote: Marine gets an email and her phone/bell
            foreach (get_users(['role' => 'cc_nutritionist']) as $nu) {
                $u = add_query_arg('food', $pid, cc_fd_hub()) . '#fd-' . $d;
                if (function_exists('cc_push_user')) cc_push_user($nu->ID, $name . ' wrote on their food diary (' . $nice . ')', wp_trim_words($text, 18), $u, 'cc-food');
                $GLOBALS['cc_ath_lang'] = 'en';
                if (function_exists('cc_ath_mail_shell')) cc_fd_mail(cc_fd_to($nu->user_email), $name . ' wrote on their food diary', cc_ath_mail_shell('Hi ' . esc_html($nu->first_name ?: $nu->display_name) . ',', '<b>' . esc_html($name) . '</b> wrote about ' . esc_html($nice) . ': ' . nl2br(esc_html($text)), 'Open the food diary', $u, '', 'Thank you,', 'Nutrition'));
            }
        }
        if ($from !== 'coach' && function_exists('cc_push_coaches')) cc_push_coaches(($from === 'nutri' ? 'Marine' : $name) . ' on the food diary (' . $name . ', ' . $nice . ')', wp_trim_words($text, 18), add_query_arg(['board' => 'food', 'ath' => $pid], cc_fd_hub()) . '#fd-' . $d, 'cc-food', $pid);
        return ['ok' => true, 'r' => array_values($cur['r'])];
    }]);
    // Matteo's laptop: which athletes have the package (with their Vekta id), and their Vekta summary (sessions + Marine's nutrition notes)
    // link Matteo's demo page to a Vekta test athlete (coach only; demo pages only)
    register_rest_route('cc/v1', '/demo-vekta', ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        $pid = (int) $r['page']; if (!get_post_meta($pid, 'cc_demo', true)) return new WP_Error('cc_no', 'Not a demo page', ['status' => 400]);
        $vid = sanitize_text_field((string) $r['vekta_id']); if ($vid === '') delete_post_meta($pid, 'cc_demo_vid'); else update_post_meta($pid, 'cc_demo_vid', $vid);
        return ['ok' => true, 'page' => $pid, 'vekta_id' => $vid ?: null];
    }]);
    // Matteo's launch switch: shows the "Food diary with Marine" upgrade card to athletes without the package
    register_rest_route('cc/v1', '/food-launch', ['methods' => 'GET,POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        if ($r->get_method() === 'POST') update_option('cc_fd_launched', $r['on'] ? 1 : 0, false);
        return ['launched' => (bool) get_option('cc_fd_launched')];
    }]);
    register_rest_route('cc/v1', '/food-athletes', ['methods' => 'GET', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function () {
        $o = [];
        // Matteo 19 Nov: his demo page has no login, so it can carry a Vekta athlete id of its own (a Vekta test athlete) for testing
        foreach (cc_fd_pkg_pages() as $p) { $uid = (int) get_post_meta($p->ID, 'cc_user', true); $vid = $uid ? (string) get_user_meta($uid, 'cc_vekta_id', true) : (string) get_post_meta($p->ID, 'cc_demo_vid', true);
            $o[] = ['page' => $p->ID, 'name' => $p->post_title, 'vekta_id' => ($vid !== '' && !cc_ath_tp($p->ID)) ? $vid : null, 'tp' => cc_ath_tp($p->ID)]; }
        return $o;
    }]);
    register_rest_route('cc/v1', '/food-vekta', ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        $n = 0; $d = function ($x) { return cc_fd_date(substr((string) $x, 0, 10)); };
        foreach ((array) $r->get_param('athletes') as $a) {
            $pid = (int) ($a['page'] ?? 0); if (!$pid || !cc_fd_on($pid) || cc_ath_tp($pid)) continue;
            $o = ['at' => time(), 'plan' => [], 'done' => [], 'notes' => []];
            foreach (array_slice((array) ($a['plan'] ?? []), 0, 80) as $x) if ($dd = $d($x['date'] ?? '')) $o['plan'][] = ['d' => $dd, 'n' => cc_fd_txt($x['name'] ?? '', 160), 'min' => (int) round(((float) ($x['dur'] ?? 0)) / 60), 'carb' => (int) ($x['carbs'] ?? 0)];
            foreach (array_slice((array) ($a['done'] ?? []), 0, 80) as $x) if ($dd = $d($x['date'] ?? '')) $o['done'][] = ['d' => $dd, 'n' => cc_fd_txt($x['name'] ?? '', 160), 'min' => (int) round(((float) ($x['dur'] ?? 0)) / 60), 'kj' => (int) ($x['kj'] ?? 0)];
            foreach (array_slice((array) ($a['notes'] ?? []), 0, 80) as $x) if ($dd = $d($x['date'] ?? '')) $o['notes'][] = ['d' => $dd, 't' => cc_fd_txt($x['title'] ?? '', 200), 'c' => mb_substr(trim(sanitize_textarea_field((string) ($x['content'] ?? ''))), 0, 4000)];
            update_post_meta($pid, 'cc_food_vx', wp_slash(wp_json_encode($o))); $n++;
        }
        return ['ok' => true, 'stored' => $n];
    }]);
});
// health data: gone when coaching ends (login removed), unless the athlete stays coached
add_action('delete_user', function ($uid) {
    if (!empty($GLOBALS['cc_keep_record'])) return;
    foreach (get_posts(['post_type' => 'cc_athlete', 'post_status' => 'any', 'meta_key' => 'cc_user', 'meta_value' => (int) $uid, 'numberposts' => -1, 'fields' => 'ids']) as $pid) {
        foreach (cc_fd_days($pid) as $d) { foreach ((array) (cc_fd_get($pid, $d)['s'] ?? []) as $s) if (!empty($s['ph'])) wp_delete_attachment((int) $s['ph'], true); delete_post_meta($pid, 'cc_fd_' . $d); }
        foreach (['cc_food_mine', 'cc_food_kg', 'cc_food_vx'] as $k) delete_post_meta($pid, $k);
    }
}, 4);

/* ---------- look ---------- */
function cc_fd_css() {
    static $done = false; if ($done) return ''; $done = true;
    return '<style>'
        . 'html .cc .fd-lede{font-size:16px;color:#d0d6e0;line-height:1.55;margin:0 0 14px}html .cc .fd-muted{color:#b8bec8;font-size:15px;margin:6px 0}'
        . 'html .cc .fd-link{background:none;border:0;padding:4px 2px;color:#2bd47a;text-decoration:underline;font:600 15px var(--body);cursor:pointer}'
        . 'html .cc .fd-tag{display:inline-block;margin-left:6px;padding:1px 8px;border-radius:999px;background:rgba(18,161,80,.15);border:1px solid rgba(43,212,122,.35);color:#c9f3da;font-size:14px;font-weight:600;white-space:nowrap}'
        . 'html .cc .fd-nav{display:flex;align-items:center;gap:10px;margin:4px 0 6px}html .cc .fd-date{flex:1;min-width:0;text-align:center;display:grid;gap:2px}html .cc .fd-date b{color:#fff;font-size:18px;text-transform:capitalize}html .cc .fd-date small{color:#b8bec8;font-size:14px}'
        . 'html .cc .fd-arrow{flex:none;width:46px;height:46px;border-radius:12px;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.04);color:#fff;font-size:26px;line-height:1;cursor:pointer}html .cc .fd-arrow:disabled{opacity:.35;cursor:default}'
        . 'html .cc .fd-status{min-height:20px;margin:0 0 6px;text-align:center;font-size:14px;color:#b8bec8}html .cc .fd-status.err{color:#ff7a73;font-weight:600}'
        . 'html .cc .fd-slot{border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.03);border-radius:14px;margin:0 0 10px}'
        . 'html .cc .fd-slot>summary{list-style:none;display:flex;align-items:center;justify-content:space-between;gap:10px;padding:14px 16px;cursor:pointer}html .cc .fd-slot>summary::-webkit-details-marker{display:none}'
        . 'html .cc .fd-slot>summary::after{content:"▾";color:#b8bec8;font-size:16px;flex:none}html .cc .fd-slot[open]>summary::after{content:"▴"}'
        . 'html .cc .fd-sl{color:#fff;font-weight:700;font-size:17px}html .cc .fd-st{margin-left:auto;color:#b8bec8;font-size:15px;text-align:right}'
        . 'html .cc .fd-sb{padding:0 16px 16px;display:grid;gap:12px}'
        . 'html .cc .fd-time{display:flex;align-items:center;gap:10px;font-size:15px;color:#d0d6e0;font-weight:600}'
        . 'html .cc .fd input[type=time],html .cc .fd input[type=number],html .cc .fd input[type=search],html .cc .fd input[type=text],html .cc .fd textarea,html .cc .fd-rv input[type=email],html .cc .fd-rv textarea{font:16px var(--body);padding:9px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.2);background:#0b0d0f;color:#fff;box-sizing:border-box}'
        . 'html .cc .fd input[type=time]{width:130px;max-width:100%}html .cc .fd textarea,html .cc .fd input[type=search],html .cc .fd input[type=text]{width:100%}'
        . 'html .cc .fd-items{list-style:none;margin:0;padding:0;display:grid;gap:8px}html .cc .fd-items li{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:12px;background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.08)}'
        . 'html .cc .fd-in{flex:1;min-width:0;display:grid;gap:3px}html .cc .fd-in b{color:#fff;font-size:16px;font-weight:600;overflow-wrap:anywhere}html .cc .fd-in small{color:#b8bec8;font-size:14px}'
        . 'html .cc .fd-g{display:flex;align-items:center;gap:4px;color:#d0d6e0;font-size:15px;flex:none}html .cc .fd .fd-g input{width:78px;padding:8px}'
        . 'html .cc .fd-x{flex:none;width:36px;height:36px;border-radius:10px;border:1px solid rgba(255,255,255,.15);background:none;color:#d0d6e0;font-size:20px;cursor:pointer}'
        . 'html .cc .fd-stot{margin:0;font-size:15px;color:#d0d6e0;font-weight:600}'
        . 'html .cc .fd .btn{width:auto;margin:0;justify-self:start}html .cc .fd-note{display:grid;gap:6px;font-size:15px;color:#d0d6e0;font-weight:600}'
        . 'html .cc .fd-ph{display:flex;flex-wrap:wrap;align-items:center;gap:10px}html .cc .fd-ph img{width:96px;height:96px;object-fit:cover;border-radius:10px;display:block}html .cc .fd-phb{cursor:pointer}'
        . 'html .cc .fd-search{display:grid;gap:8px;padding:12px;border-radius:12px;border:1px solid rgba(43,212,122,.35);background:rgba(18,161,80,.06)}html .cc .fd-credit{margin:0;color:#b8bec8;font-size:14px}'
        . 'html .cc .fd-rl{list-style:none;margin:0;padding:0;max-height:340px;overflow:auto;display:grid;gap:4px}'
        . 'html .cc .fd-rl button{width:100%;text-align:left;display:grid;gap:2px;padding:10px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.03);color:#fff;font:500 16px var(--body);cursor:pointer}'
        . 'html .cc .fd-rl button:hover,html .cc .fd-rl button:focus{border-color:rgba(43,212,122,.6)}html .cc .fd-rl small{color:#b8bec8;font-size:14px}html .cc .fd-rl i{color:#b8bec8;font-size:14px;font-style:normal}'
        . 'html .cc .fd-pick{display:grid;gap:10px}html .cc .fd-pick b{color:#fff;font-size:16px}html .cc .fd-pick label{display:flex;align-items:center;gap:10px;color:#d0d6e0;font-size:15px;font-weight:600}html .cc .fd .fd-pick input{width:110px}html .cc .fd-pp{color:#d0d6e0;font-size:15px}html .cc .fd-row{display:flex;flex-wrap:wrap;align-items:center;gap:10px 16px}'
        . 'html .cc .fd-tot{margin:16px 0 6px;padding:16px;border-radius:14px;border:1px solid rgba(43,212,122,.3);background:rgba(18,161,80,.07)}html .cc .fd-tot h3{margin:0 0 10px;font-size:18px}'
        . 'html .cc .fd-tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:8px}html .cc .fd-tiles div{padding:10px 12px;border-radius:12px;background:rgba(0,0,0,.25);display:grid;gap:2px}'
        . 'html .cc .fd-tiles b{color:#fff;font-size:20px}html .cc .fd-tiles span{color:#b8bec8;font-size:14px}html .cc .fd-tiles em{color:#c9f3da;font-style:normal;font-size:15px;font-weight:600}'
        . 'html .cc .fd-kg{display:flex;flex-wrap:wrap;align-items:center;gap:10px;margin:14px 0 4px;color:#d0d6e0;font-size:15px;font-weight:600}html .cc .fd .fd-kg input{width:100px}'
        . 'html .cc .fd-thread{margin:16px 0 0}html .cc .fd-thread h3{font-size:18px;margin:0 0 6px}html .cc .fd-rbox{display:grid;gap:8px;margin-top:8px}'
        . 'html .cc .fd-mine{margin:18px 0 0;border:1px solid rgba(255,255,255,.1);border-radius:14px;background:rgba(255,255,255,.03)}html .cc .fd-mine>summary{padding:14px 16px;cursor:pointer;color:#fff;font-weight:700;font-size:17px}'
        . 'html .cc .fd-mb{padding:0 16px 16px;display:grid;gap:10px}html .cc .fd-mrow{display:flex;flex-wrap:wrap;align-items:center;gap:6px 12px;padding:10px 0;border-top:1px solid rgba(255,255,255,.08)}html .cc .fd-mrow>div{flex:1;min-width:200px;display:grid;gap:3px}html .cc .fd-mrow b{color:#fff;font-size:16px}html .cc .fd-mrow small{color:#b8bec8;font-size:14px}'
        . 'html .cc .fd-form{display:grid;gap:12px;padding:14px;border-radius:12px;border:1px solid rgba(255,255,255,.14);background:rgba(0,0,0,.2)}html .cc .fd-form>label,html .cc .fd-nums label{display:grid;gap:6px;color:#d0d6e0;font-size:15px;font-weight:600}'
        . 'html .cc .fd-nums{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:10px}html .cc .fd-nums input{width:100%}html .cc .fd-form h4{margin:4px 0 0;font-size:16px;color:#fff}html .cc .fd-hint{color:#b8bec8;font-size:14px;font-weight:500}'
        . 'html .cc .fd-msg{margin:0;font-size:15px;font-weight:600;color:#2bd47a}html .cc .fd-msg.err{color:#ff7a73}html .cc .fd-msg:empty{display:none}'
        . 'html .cc .fd-more{margin-top:4px}html .cc .fd-more>summary{list-style:none;display:inline-block;width:auto;cursor:pointer}html .cc .fd-more>summary::-webkit-details-marker{display:none}'
        . 'html .cc .fd-morep{margin-top:14px;padding:16px;border-radius:14px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.03)}html .cc .fd-morep h3{margin:0 0 8px;font-size:18px}html .cc .fd-morep ol{margin:0 0 12px;padding-left:22px;color:#d0d6e0;font-size:16px;line-height:1.55}html .cc .fd-morep li{margin:4px 0}html .cc .fd-morep p{color:#d0d6e0;font-size:16px}html .cc .fd-up .btn{width:auto}'
        . 'html .cc .fd-sw{display:flex;align-items:center;gap:12px;font-size:16px;color:#d0d6e0;margin:4px 0 12px}html .cc .fd-pkg{position:relative;flex:none;width:54px;height:30px;border-radius:999px;border:1px solid rgba(255,255,255,.25);background:#2a2e34;cursor:pointer;padding:0}'
        . 'html .cc .fd-pkg .fd-knob{position:absolute;top:3px;left:3px;width:22px;height:22px;border-radius:50%;background:#d0d6e0;transition:left .15s}html .cc .fd-pkg.on{background:#12a150;border-color:#12a150}html .cc .fd-pkg.on .fd-knob{left:27px;background:#fff}'
        . 'html .cc .fd-back a{color:#2bd47a;font-weight:600;font-size:15px}html .cc .fd-rv h2 .ph-face,html .cc .fd-rv h2 img{vertical-align:middle}'
        . 'html .cc .fd-al{display:flex;align-items:center;gap:12px;padding:12px;margin:8px 0 0;border-radius:12px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.03);color:#fff;text-decoration:none}html .cc .fd-al>span{display:grid;flex:1;min-width:0}html .cc .fd-al b{font-size:16px}html .cc .fd-al small{color:#b8bec8;font-size:14px}'
        . 'html .cc .fd-badge{background:#ca212a;color:#fff;border-radius:999px;padding:2px 10px;font-size:14px;font-weight:700;white-space:nowrap}'
        . 'html .cc .fd-addath{margin-top:16px}html .cc .fd-addath summary{cursor:pointer;color:#2bd47a;font-weight:600;font-size:15px}html .cc .fd-addf{display:grid;gap:10px;margin-top:10px;max-width:420px}html .cc .fd-addf label{display:grid;gap:6px;color:#d0d6e0;font-size:15px;font-weight:600}html .cc .fd-addf .btn{justify-self:start;width:auto;margin:0}'
        . 'html .cc .fd-week{margin:6px 0 18px}html .cc .fd-week h3{font-size:18px;margin:0 0 8px}html .cc .fd-wkg{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}'
        . 'html .cc .fd-wk{display:grid;align-content:start;gap:4px;padding:10px 12px;border-radius:12px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.03);font-size:15px;color:#d0d6e0}html .cc .fd-wk b{color:#fff}html .cc .fd-wk summary{cursor:pointer;color:#c9f3da}html .cc .fd-wk p{margin:4px 0 0;font-size:14px}html .cc .fd-warn-n{color:#b8bec8;font-size:14px}'
        . 'html .cc .fd-rd{padding:16px 0;border-top:1px solid rgba(255,255,255,.12)}html .cc .fd-rd h3{margin:0 0 10px;font-size:19px}html .cc .fd-rd h3 small{font-size:14px;color:#2bd47a;font-weight:600}'
        . 'html .cc .fd-rs{padding:10px 12px;margin:0 0 8px;border-radius:12px;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.08)}html .cc .fd-rsh{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 10px}html .cc .fd-rsh b{color:#fff;font-size:16px}'
        . 'html .cc .fd-time-b{color:#c9f3da;font-size:15px;font-weight:600}html .cc .fd-rst{margin-left:auto;color:#d0d6e0;font-size:15px}html .cc .fd-ri{list-style:none;margin:6px 0 0;padding:0;display:grid;gap:4px}html .cc .fd-ri li{display:grid;gap:1px;font-size:15px;color:#e6e9ee}html .cc .fd-ri small{color:#b8bec8;font-size:14px}'
        . 'html .cc .fd-rn{margin:6px 0 0;color:#d0d6e0;font-size:15px;font-style:italic}html .cc .fd-rph img{display:block;margin-top:8px;width:140px;height:140px;object-fit:cover;border-radius:10px}'
        . 'html .cc .fd-rtot{display:flex;flex-wrap:wrap;gap:6px 14px;padding:10px 12px;border-radius:12px;background:rgba(18,161,80,.08);border:1px solid rgba(43,212,122,.3);font-size:15px;color:#d0d6e0}html .cc .fd-rtot b{color:#fff;width:100%}'
        . 'html .cc .fd-vx{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px;margin:10px 0 0}html .cc .fd-vxb{padding:10px 12px;border-radius:12px;border:1px solid rgba(255,255,255,.08)}html .cc .fd-vxb h4{margin:0 0 4px;font-size:14px;color:#b8bec8;text-transform:uppercase;letter-spacing:.06em}'
        . 'html .cc .fd-vxb ul{margin:0;padding:0;list-style:none;font-size:15px;color:#e6e9ee;display:grid;gap:3px}html .cc .fd-vnote b{color:#fff;font-size:15px}html .cc .fd-vnote p,html .cc .fd-vnote summary{margin:4px 0 0;font-size:15px;color:#d0d6e0}html .cc .fd-vnote summary{cursor:pointer}'
        . 'html .cc .ath .fd-tot h3,html .cc .ath .fd-thread h3,html .cc .ath .fd-morep h3,html .cc .ath .fd-week h3,html .cc .ath .fd-rd h3{font-size:20px!important}'
        . 'html .cc .fd-vxb h4,html .cc .fd-form h4,html .cc .fd-rd h3 small{font-family:var(--body);letter-spacing:.02em}html .cc .fd-vxb h4{font-size:14px;font-weight:700}'
        . 'html .cc .ath .fd label,html .cc .ath .fd-rv label{font-size:15px;margin-top:0}html .cc .ath .fd .fd-g{font-size:15px;font-weight:500}'
        . 'html .cc .fd-th{margin-top:6px}html .cc .fd-r{display:grid;gap:8px}html .cc .fd-r textarea{width:100%}html .cc .fd-r .btn{justify-self:start;width:auto;margin:0}html .cc .fd-pager{margin-top:16px}'
        . '</style>';
}
/* review pages (Matteo / Marine): replies, the package switch, adding an athlete by email */
function cc_fd_rjs() {
    static $done = false; if ($done) return ''; $done = true;
    $n = esc_js(wp_create_nonce('wp_rest'));
    $js = <<<'JS'
(function(){
function post(u,data){var f=new FormData();for(var k in data){f.append(k,data[k]);}return fetch(u,{method:"POST",body:f,credentials:"same-origin",headers:{"X-WP-Nonce":"%NONCE%"}}).then(function(r){return r.json().then(function(j){if(!r.ok){throw j;}return j;});});}
document.addEventListener("click",function(e){
var s=e.target.closest(".fd-send");
if(s){var r=s.closest(".fd-r"),t=r.querySelector("textarea");if(!t.value.trim()){return;}s.disabled=true;
post("%REPLY%",{page:r.dataset.page,date:r.dataset.date,text:t.value}).then(function(){var u=location.href.split("#")[0];location.replace(u+"#fd-"+r.dataset.date);location.reload();}).catch(function(){s.disabled=false;alert("Not sent. Please try again.");});return;}
var p=e.target.closest(".fd-pkg");
if(p){var on=!p.classList.contains("on");if(!on&&!confirm("Turn the Nutrition package off for this athlete? Their diary stays saved, but they and Marine will no longer see it.")){return;}p.disabled=true;
post("%PKG%",{page:p.dataset.page,on:on?1:0}).then(function(){location.reload();}).catch(function(){p.disabled=false;alert("Not changed. Please try again.");});return;}
var a=e.target.closest(".fd-addgo");
if(a){var box=a.closest(".fd-addf"),m=box.querySelector(".fd-msg"),em=box.querySelector(".fd-addmail").value.trim();if(!em){return;}a.disabled=true;
post("%PKG%",{email:em,on:1}).then(function(j){m.className="fd-msg";m.textContent=j.name+" now has the Nutrition package.";setTimeout(function(){location.reload();},900);}).catch(function(){a.disabled=false;m.className="fd-msg err";m.textContent="No athlete found with that email.";});}
});
})();
JS;
    return '<script>' . str_replace(["\r", "\n", '%NONCE%', '%REPLY%', '%PKG%'], ['', '', $n, esc_url_raw(rest_url('cc/v1/food-reply')), esc_url_raw(rest_url('cc/v1/food-pkg'))], $js) . '</script>';
}
/* the athlete's diary (all drawn in the browser from data-cfg; every change is saved through the REST routes) */
function cc_fd_js() {
    static $done = false; if ($done) return ''; $done = true;
    $js = <<<'JS'
(function(){
var root=document.querySelector(".fd-app");if(!root){return;}
var C=JSON.parse(root.getAttribute("data-cfg")),W=C.w;
var S={date:C.date,day:C.day,mine:C.mine||[],kg:C.kg||"",open:{},srch:null,edit:null,timer:null,dirty:false,mineOpen:false,res:[]};
var DB=null,DBP=null;
function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c];});}
function fmt(x){x=Math.round((+x||0)*10)/10;return x.toLocaleString(C.lang,{maximumFractionDigits:1});}
function fmt0(x){return Math.round(+x||0).toLocaleString(C.lang);}
function norm(s){return String(s||"").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"");}
function ymd(d){return d.getFullYear()+"-"+String(d.getMonth()+1).padStart(2,"0")+"-"+String(d.getDate()).padStart(2,"0");}
function today(){return ymd(new Date());}
function shift(ds,n){var d=new Date(ds+"T12:00:00");d.setDate(d.getDate()+n);return ymd(d);}
function send(url,data,method){var o={method:method||"POST",credentials:"same-origin",headers:{"X-WP-Nonce":C.nonce}};
if(o.method==="GET"){url+=(url.indexOf("?")>-1?"&":"?")+new URLSearchParams(data).toString();}
else if(data instanceof FormData){o.body=data;}else{var f=new FormData();for(var k in data){f.append(k,data[k]);}o.body=f;}
return fetch(url,o).then(function(r){if(!r.ok){throw r;}return r.json();});}
function status(t,bad){var el=root.querySelector(".fd-status");if(el){el.textContent=t||"";el.className="fd-status"+(bad?" err":"");}}
function slot(k){if(!S.day.s||Array.isArray(S.day.s)){S.day.s={};}var s=S.day.s[k];if(!s){s=S.day.s[k]={t:"",n:"",i:[]};}if(!s.i){s.i=[];}return s;}
var F=["k","c","p","f","fi","su"];
function tot(items){var t={k:0,c:0,p:0,f:0,fi:0,su:0};(items||[]).forEach(function(it){var m=(+it.g||0)/100;F.forEach(function(x){t[x]+=(+it[x]||0)*m;});});return t;}
function dayTot(){var a=[];C.slots.forEach(function(s){a=a.concat(slot(s[0]).i);});return tot(a);}
function macro(it){var m=(+it.g||0)/100;return fmt0(it.k*m)+" kcal · "+W.c_ab+" "+fmt(it.c*m)+" · "+W.p_ab+" "+fmt(it.p*m)+" · "+W.f_ab+" "+fmt(it.f*m);}
function macro100(f){return fmt0(f.k)+" kcal · "+W.c_ab+" "+fmt(f.c)+" · "+W.p_ab+" "+fmt(f.p)+" · "+W.f_ab+" "+fmt(f.f)+" / 100 g";}
function macroT(t){return fmt0(t.k)+" kcal · "+W.carbs+" "+fmt(t.c)+" g · "+W.protein+" "+fmt(t.p)+" g · "+W.fat+" "+fmt(t.f)+" g";}
function tag(m){return m?' <span class="fd-tag">'+esc(m==="r"?W.myrecipe:W.myfood)+'</span>':"";}
function loadDB(){if(DBP){return DBP;}DBP=fetch(C.foods,{credentials:"omit"}).then(function(r){if(!r.ok){throw r;}return r.json();}).then(function(d){
DB=d.foods.map(function(r){return {id:r[0],n:r[2],fr:r[3]||"",k:r[4],c:r[5],p:r[6],f:r[7],fi:r[8]==null?0:r[8],su:r[9]==null?0:r[9],q:norm(r[2]+" | "+(r[3]||"")),qn:norm(r[2])};});return DB;}).catch(function(){DBP=null;DB=null;});return DBP;}
function mineFoods(){return S.mine.map(function(m){return {id:m.id,n:m.n,fr:"",k:m.k,c:m.c,p:m.p,f:m.f,fi:m.fi||0,su:m.su||0,q:norm(m.n),qn:norm(m.n),mine:m.t};});}
function search(q){var ws=norm(q).split(/[\s,]+/).filter(Boolean);if(!ws.length){return [];}var whole=ws.join(" "),out=[];
var pool=mineFoods().concat(DB||[]);
for(var i=0;i<pool.length;i++){var f=pool[i],ok=true;for(var j=0;j<ws.length;j++){if(f.q.indexOf(ws[j])<0){ok=false;break;}}if(!ok){continue;}
var sc=f.qn.indexOf(whole)===0?0:(f.qn.indexOf(ws[0])===0?1:(ws.every(function(w){return new RegExp("(^|[^a-z0-9])"+w.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")).test(f.qn);})?2:3));
if(f.mine){sc-=2;}out.push([sc,f.n.length,f]);}
out.sort(function(a,b){return a[0]-b[0]||a[1]-b[1];});return out.slice(0,40).map(function(x){return x[2];});}
function resultsHtml(){if(!DB&&!S.mine.length){return '<p class="fd-muted">'+esc(W.loading)+'</p>';}if(!S.srch.q.trim()){return DB?"":'<p class="fd-muted">'+esc(W.loading)+'</p>';}
S.res=search(S.srch.q);if(!S.res.length){return DB?'<p class="fd-muted">'+esc(W.noresults)+'</p>':'<p class="fd-muted">'+esc(W.loading)+'</p>';}
var ws=norm(S.srch.q).split(/[\s,]+/).filter(Boolean);
return '<ul class="fd-rl">'+S.res.map(function(f,ix){var viaFr=f.fr&&!ws.every(function(w){return f.qn.indexOf(w)>-1;});
return '<li><button type="button" data-act="pick" data-rx="'+ix+'"><span>'+esc(f.n)+tag(f.mine)+'</span>'+(viaFr?'<i>'+esc(f.fr)+'</i>':'')+'<small>'+esc(macro100(f))+'</small></button></li>';}).join("")+'</ul>';}
function searchHtml(){var s=S.srch;
if(s.pick){var p=s.pick,it={k:p.k,c:p.c,p:p.p,f:p.f,g:s.g};
return '<div class="fd-search"><div class="fd-pick"><b>'+esc(p.n)+tag(p.mine)+'</b><label>'+esc(W.grams)+' <input type="number" class="fd-pg" inputmode="decimal" min="1" max="5000" step="1" value="'+esc(s.g)+'"></label><span class="fd-pp">'+esc(macro(it))+'</span><div class="fd-row"><button type="button" class="btn btn-go" data-act="pickadd">'+esc(W.addit)+'</button><button type="button" class="fd-link" data-act="unpick">'+esc(W.cancel)+'</button></div></div></div>';}
return '<div class="fd-search"><input type="search" class="fd-q" placeholder="'+esc(W.search)+'" value="'+esc(s.q)+'" autocomplete="off" enterkeyhint="search"><div class="fd-res">'+resultsHtml()+'</div><p class="fd-credit">'+esc(C.credit)+'</p><button type="button" class="fd-link" data-act="cancel" style="justify-self:start">'+esc(W.cancel)+'</button></div>';}
function slotHtml(k,label){var s=slot(k),t=tot(s.i),open=S.open[k]!==undefined?S.open[k]:(s.i.length>0||!!s.n||!!s.phu);
var h='<details class="fd-slot" data-slot="'+k+'"'+(open?" open":"")+'><summary><span class="fd-sl">'+esc(label)+'</span><span class="fd-st" data-tt="'+k+'">'+sumTxt(s,t)+'</span></summary><div class="fd-sb">';
h+='<label class="fd-time">'+esc(W.time)+' <input type="time" data-f="t" value="'+esc(s.t||"")+'"></label>';
if(s.i.length){h+='<ul class="fd-items">'+s.i.map(function(it,ix){return '<li><div class="fd-in"><b>'+esc(it.n)+tag(it.m)+'</b><small data-it="'+ix+'">'+esc(macro(it))+'</small></div><label class="fd-g"><input type="number" inputmode="decimal" min="0" max="5000" step="1" data-f="g" data-ix="'+ix+'" value="'+esc(it.g)+'" aria-label="'+esc(W.grams)+'"> g</label><button type="button" class="fd-x" data-act="rm" data-ix="'+ix+'" aria-label="'+esc(W.remove)+'">×</button></li>';}).join("")+'</ul>';
h+='<p class="fd-stot" data-stot="'+k+'">'+esc(W.slot_total+": "+macroT(t))+'</p>';}
h+=(S.srch&&S.srch.ctx==="slot"&&S.srch.slot===k)?searchHtml():'<button type="button" class="btn btn-go" data-act="add">'+esc(W.add)+'</button>';
h+='<label class="fd-note">'+esc(W.note)+'<textarea rows="2" data-f="n" placeholder="'+esc(W.note_ph)+'">'+esc(s.n||"")+'</textarea></label>';
h+='<div class="fd-ph">'+(s.phu?'<a href="'+esc(s.phu)+'" target="_blank" rel="noopener"><img src="'+esc(s.phu)+'" alt=""></a>':"")+'<label class="btn btn-ghost fd-phb">'+esc(s.phu?W.photo_ch:W.photo)+'<input type="file" accept="image/*" hidden data-f="ph"></label>'+(s.phu?'<button type="button" class="fd-link" data-act="phdel">'+esc(W.photo_del)+'</button>':"")+'</div>';
return h+'</div></details>';}
function sumTxt(s,t){var a=[];if(s.t){a.push(s.t);}if(s.i.length){a.push(fmt0(t.k)+" kcal");}return esc(a.join(" · "));}
function totV(){var t=dayTot(),kg=parseFloat(String(S.kg).replace(",","."))||0;
function tile(v,l,x){return '<div><b>'+v+'</b><span>'+esc(l)+'</span>'+(x?'<em>'+x+'</em>':"")+'</div>';}
return '<div class="fd-tiles">'+tile(fmt0(t.k),"kcal")+tile(fmt0(t.c)+" g",W.carbs,kg?fmt(t.c/kg)+" g/kg":"")+tile(fmt0(t.p)+" g",W.protein,kg?fmt(t.p/kg)+" g/kg":"")+tile(fmt0(t.f)+" g",W.fat)+tile(fmt0(t.fi)+" g",W.fibre)+tile(fmt0(t.su)+" g",W.sugars)+'</div>';}
function threadHtml(){var r=S.day.r||[];
var h=r.map(function(x){var who=x.from==="athlete"?W.you:(x.from==="nutri"?"Marine":"Matteo");var d=new Date(x.at*1000);
return '<div class="nt-rep'+(x.from==="athlete"?" nt-rep-a":"")+'"><span class="nt-rh"><b>'+esc(who)+'</b> <small>'+esc(d.toLocaleString(C.lang,{day:"numeric",month:"short",hour:"2-digit",minute:"2-digit"}))+'</small></span><p>'+esc(x.text).replace(/\n/g,"<br>")+'</p></div>';}).join("");
return '<div class="fd-thread">'+(r.length?'<h3>'+esc(W.thread)+'</h3>'+h:"")+'<details class="nt-replyd"><summary>'+esc(r.length?W.reply:W.ask)+'</summary><div class="fd-rbox"><textarea rows="3"></textarea><button type="button" class="btn btn-go" data-act="send">'+esc(W.send_r)+'</button></div></details></div>';}
function render(){var d=new Date(S.date+"T12:00:00"),lbl=d.toLocaleDateString(C.lang,{weekday:"long",day:"numeric",month:"long"}),isT=S.date===today();
var h='<div class="fd-nav"><button type="button" class="fd-arrow" data-act="prev" aria-label="'+esc(W.prev)+'">‹</button><div class="fd-date"><b>'+esc(lbl)+'</b>'+(isT?'<small>'+esc(W.today)+'</small>':'<button type="button" class="fd-link" data-act="today">'+esc(W.gotoday)+'</button>')+'</div><button type="button" class="fd-arrow" data-act="next" aria-label="'+esc(W.next)+'"'+(S.date>=today()?" disabled":"")+'>›</button></div><p class="fd-status" role="status"></p>';
C.slots.forEach(function(sv){h+=slotHtml(sv[0],sv[1]);});
h+='<div class="fd-tot"><h3>'+esc(W.day_total)+'</h3><div class="fd-totv">'+totV()+'</div><label class="fd-kg">'+esc(W.weight)+' <input type="number" class="fd-kgi" inputmode="decimal" min="25" max="250" step="0.1" value="'+esc(S.kg)+'"></label><p class="fd-muted">'+esc(W.weight_h)+'</p></div>';
h+=threadHtml();
root.querySelector(".fd-day").innerHTML=h;renderMine();}
function refreshNums(){C.slots.forEach(function(sv){var k=sv[0],s=slot(k),t=tot(s.i),el=root.querySelector('[data-tt="'+k+'"]');if(el){el.innerHTML=sumTxt(s,t);}
var st=root.querySelector('[data-stot="'+k+'"]');if(st){st.textContent=W.slot_total+": "+macroT(t);}
var sl=root.querySelector('.fd-slot[data-slot="'+k+'"]');if(sl){s.i.forEach(function(it,ix){var sm=sl.querySelector('[data-it="'+ix+'"]');if(sm){sm.textContent=macro(it);}});}});
var tv=root.querySelector(".fd-totv");if(tv){tv.innerHTML=totV();}}
function save(){S.dirty=true;status(W.saving);clearTimeout(S.timer);S.timer=setTimeout(flush,700);}
function payload(){return {page:C.page,date:S.date,data:JSON.stringify(S.day.s||{})};}
function flush(){clearTimeout(S.timer);if(!S.dirty){return Promise.resolve();}S.dirty=false;return send(C.u.save,payload()).then(function(){status(W.saved);}).catch(function(){S.dirty=true;status(W.err,true);});}
addEventListener("pagehide",function(){if(!S.dirty){return;}var f=new FormData(),p=payload();for(var k in p){f.append(k,p[k]);}f.append("_wpnonce",C.nonce);try{navigator.sendBeacon(C.u.save,f);S.dirty=false;}catch(x){}});
function go(ds){flush().then(function(){return send(C.u.day,{page:C.page,date:ds},"GET");}).then(function(d){S.date=ds;S.day=d;S.open={};S.srch=null;render();}).catch(function(){status(W.err,true);});}
function mineHtml(){var h='<details class="fd-mine"'+(S.mineOpen?" open":"")+'><summary>'+esc(W.mine)+'</summary><div class="fd-mb"><p class="fd-muted">'+esc(W.mine_lede)+'</p>';
if(!S.mine.length&&!S.edit){h+='<p class="fd-muted">'+esc(W.none_mine)+'</p>';}
S.mine.forEach(function(m){h+='<div class="fd-mrow"><div><b>'+esc(m.n)+tag(m.t)+'</b><small>'+esc(macro100(m))+'</small></div><button type="button" class="fd-link" data-act="medit" data-id="'+esc(m.id)+'">'+esc(W.edit)+'</button><button type="button" class="fd-link" data-act="mdel" data-id="'+esc(m.id)+'">'+esc(W.del)+'</button></div>';});
h+=S.edit?formHtml():'<div class="fd-row"><button type="button" class="btn btn-ghost" data-act="newfood">'+esc(W.add_label)+'</button><button type="button" class="btn btn-ghost" data-act="newrecipe">'+esc(W.add_recipe)+'</button></div>';
return h+'</div></details>';}
function recipeCalc(e){var t=tot(e.ing),w=parseFloat(e.cw)||0,sum=e.ing.reduce(function(a,i){return a+(+i.g||0);},0);if(!(w>0)){w=sum;}var o={};F.forEach(function(x){o[x]=w>0?Math.round(t[x]*1000/w)/10:0;});o.w=w;o.sum=sum;return o;}
function formHtml(){var e=S.edit,h='<div class="fd-form"><h4>'+esc(e.id?W.edit:(e.t==="r"?W.add_recipe:W.add_label))+'</h4><label>'+esc(W.name)+'<input type="text" data-e="n" value="'+esc(e.n)+'" maxlength="120"></label>';
if(e.t==="f"){h+='<h4>'+esc(W.per100)+'</h4><div class="fd-nums">'+[["k","kcal"],["c",W.carbs+" (g)"],["p",W.protein+" (g)"],["f",W.fat+" (g)"],["fi",W.fibre+" (g), "+W.optional],["su",W.sugars+" (g), "+W.optional]].map(function(x){return '<label>'+esc(x[1])+'<input type="number" inputmode="decimal" min="0" step="0.1" data-e="'+x[0]+'" value="'+esc(e[x[0]])+'"></label>';}).join("")+'</div>';}
else{h+='<h4>'+esc(W.ingredients)+'</h4>';
if(e.ing.length){h+='<ul class="fd-items">'+e.ing.map(function(it,ix){return '<li><div class="fd-in"><b>'+esc(it.n)+tag(it.m)+'</b><small data-ing="'+ix+'">'+esc(macro(it))+'</small></div><label class="fd-g"><input type="number" inputmode="decimal" min="0" max="5000" step="1" data-e="ig" data-ix="'+ix+'" value="'+esc(it.g)+'" aria-label="'+esc(W.grams)+'"> g</label><button type="button" class="fd-x" data-act="ingrm" data-ix="'+ix+'" aria-label="'+esc(W.remove)+'">×</button></li>';}).join("")+'</ul>';}
h+=(S.srch&&S.srch.ctx==="ing")?searchHtml():'<button type="button" class="btn btn-ghost" data-act="adding" style="justify-self:start">'+esc(W.add_ing)+'</button>';
var rc=recipeCalc(e);h+='<label>'+esc(W.cooked)+'<input type="number" inputmode="decimal" min="0" step="1" data-e="cw" value="'+esc(e.cw||"")+'" placeholder="'+esc(fmt0(rc.sum))+'" style="max-width:160px"><span class="fd-hint">'+esc(W.cooked_h)+'</span></label>';
h+='<p class="fd-stot fd-rcp">'+esc(W.per100+": "+macro100(rc))+'</p>';}
return h+'<p class="fd-msg err fd-emsg" role="alert"></p><div class="fd-row"><button type="button" class="btn btn-go" data-act="msave">'+esc(W.save)+'</button><button type="button" class="fd-link" data-act="mcancel">'+esc(W.cancel)+'</button></div></div>';}
function renderMine(){root.querySelector(".fd-minebox").innerHTML=mineHtml();}
function saveMine(){return send(C.u.mine,{page:C.page,data:JSON.stringify(S.mine)}).then(function(j){S.mine=j.mine||S.mine;}).catch(function(){status(W.err,true);});}
function focusQ(){var q=root.querySelector(".fd-q");if(q){q.focus();}}
function refreshRes(){var r=root.querySelector(".fd-res");if(r&&S.srch){r.innerHTML=resultsHtml();}}
function redraw(){if(S.srch&&S.srch.ctx==="ing"){renderMine();}else{render();}}
root.addEventListener("toggle",function(e){var t=e.target;if(t.classList&&t.classList.contains("fd-slot")){S.open[t.dataset.slot]=t.open;}else if(t.classList&&t.classList.contains("fd-mine")){S.mineOpen=t.open;}},true);
root.addEventListener("click",function(e){var b=e.target.closest("[data-act]");if(!b||!root.contains(b)){return;}var a=b.dataset.act,sl=b.closest(".fd-slot"),k=sl?sl.dataset.slot:null;
if(a==="prev"){go(shift(S.date,-1));}
else if(a==="next"){go(shift(S.date,1));}
else if(a==="today"){go(today());}
else if(a==="add"||a==="adding"){S.srch={ctx:a==="add"?"slot":"ing",slot:k,q:"",pick:null,g:100};if(a==="add"){S.open[k]=true;}redraw();focusQ();loadDB().then(refreshRes);}
else if(a==="cancel"){S.srch=null;redraw();}
else if(a==="pick"){S.srch.pick=S.res[+b.dataset.rx];redraw();var g=root.querySelector(".fd-pg");if(g){g.focus();g.select();}}
else if(a==="unpick"){S.srch.pick=null;redraw();focusQ();}
else if(a==="pickadd"){var p=S.srch.pick,g2=parseFloat(String(S.srch.g).replace(",","."))||0;if(!(g2>0)){return;}
var it={id:p.id,n:p.n,g:Math.round(g2*10)/10,k:p.k,c:p.c,p:p.p,f:p.f,fi:p.fi||0,su:p.su||0};if(p.mine){it.m=p.mine;}
if(S.srch.ctx==="slot"){slot(S.srch.slot).i.push(it);S.open[S.srch.slot]=true;S.srch=null;render();save();}else{S.edit.ing.push(it);S.srch=null;renderMine();}}
else if(a==="rm"){slot(k).i.splice(+b.dataset.ix,1);render();save();}
else if(a==="phdel"){flush().then(function(){return send(C.u.photodel,{page:C.page,date:S.date,slot:k});}).then(function(){var s=slot(k);delete s.ph;delete s.phu;render();}).catch(function(){status(W.err,true);});}
else if(a==="send"){var box=b.closest(".fd-rbox"),t=box.querySelector("textarea");if(!t.value.trim()){return;}b.disabled=true;
send(C.u.reply,{page:C.page,date:S.date,text:t.value}).then(function(j){S.day.r=j.r||[];render();}).catch(function(){b.disabled=false;status(W.sent_err,true);});}
else if(a==="newfood"||a==="newrecipe"){S.edit={t:a==="newfood"?"f":"r",id:"",n:"",k:"",c:"",p:"",f:"",fi:"",su:"",ing:[],cw:""};S.srch=null;S.mineOpen=true;renderMine();var n=root.querySelector('[data-e="n"]');if(n){n.focus();}}
else if(a==="medit"){var m=S.mine.filter(function(x){return x.id===b.dataset.id;})[0];if(!m){return;}S.edit=JSON.parse(JSON.stringify(m));if(!S.edit.ing){S.edit.ing=[];}S.srch=null;S.mineOpen=true;renderMine();}
else if(a==="mdel"){if(!confirm(W.delq)){return;}S.mine=S.mine.filter(function(x){return x.id!==b.dataset.id;});renderMine();saveMine();}
else if(a==="mcancel"){S.edit=null;S.srch=null;renderMine();}
else if(a==="ingrm"){S.edit.ing.splice(+b.dataset.ix,1);renderMine();}
else if(a==="msave"){var e2=S.edit,msg=root.querySelector(".fd-emsg"),o={id:e2.id||("M"+Date.now().toString(36)),t:e2.t,n:String(e2.n||"").trim()};
if(e2.t==="f"){if(!o.n||!(parseFloat(e2.k)>=0&&String(e2.k).trim()!=="")){msg.textContent=W.need;return;}F.forEach(function(x){o[x]=Math.max(0,parseFloat(String(e2[x]).replace(",","."))||0);});}
else{if(!o.n||!e2.ing.length){msg.textContent=W.need_r;return;}var rc=recipeCalc(e2);F.forEach(function(x){o[x]=rc[x];});o.ing=e2.ing;o.cw=parseFloat(e2.cw)||0;}
var ix=-1;S.mine.forEach(function(x,i){if(x.id===o.id){ix=i;}});if(ix>-1){S.mine[ix]=o;}else{S.mine.push(o);}S.edit=null;S.srch=null;renderMine();saveMine().then(renderMine);}
});
var qt=null,kt=null;
root.addEventListener("input",function(e){var el=e.target,sl=el.closest(".fd-slot"),k=sl?sl.dataset.slot:null,f=el.dataset.f,ef=el.dataset.e;
if(el.classList.contains("fd-q")){S.srch.q=el.value;clearTimeout(qt);qt=setTimeout(refreshRes,120);return;}
if(el.classList.contains("fd-pg")){S.srch.g=el.value;var p=S.srch.pick,pp=root.querySelector(".fd-pp");if(pp){pp.textContent=macro({k:p.k,c:p.c,p:p.p,f:p.f,g:parseFloat(el.value)||0});}return;}
if(el.classList.contains("fd-kgi")){S.kg=el.value;refreshNums();clearTimeout(kt);kt=setTimeout(function(){send(C.u.kg,{page:C.page,kg:S.kg}).then(function(){status(W.saved);}).catch(function(){status(W.err,true);});},800);return;}
if(f==="g"&&k){slot(k).i[+el.dataset.ix].g=parseFloat(el.value)||0;refreshNums();save();return;}
if(f==="t"&&k){slot(k).t=el.value;refreshNums();save();return;}
if(f==="n"&&k){slot(k).n=el.value;save();return;}
if(ef&&S.edit){if(ef==="ig"){S.edit.ing[+el.dataset.ix].g=parseFloat(el.value)||0;var sm=root.querySelector('[data-ing="'+el.dataset.ix+'"]');if(sm){sm.textContent=macro(S.edit.ing[+el.dataset.ix]);}}else{S.edit[ef]=el.value;}
var rp=root.querySelector(".fd-rcp");if(rp&&S.edit.t==="r"){rp.textContent=W.per100+": "+macro100(recipeCalc(S.edit));}}
});
root.addEventListener("keydown",function(e){if(e.key==="Enter"&&e.target.classList.contains("fd-pg")){e.preventDefault();var b=root.querySelector('[data-act="pickadd"]');if(b){b.click();}}
if(e.key==="Enter"&&e.target.classList.contains("fd-q")){e.preventDefault();var first=root.querySelector('.fd-rl [data-act="pick"]');if(first){first.click();}}});
root.addEventListener("change",function(e){var el=e.target;if(el.dataset.f!=="ph"){return;}var sl=el.closest(".fd-slot"),k=sl.dataset.slot,fi=el.files[0];if(!fi){return;}
if(fi.size>10485760||!/^image\//.test(fi.type||"")&&!/\.(heic|heif|jpe?g|png|webp)$/i.test(fi.name)){status(W.photo_bad,true);return;}
status(W.uploading);flush().then(function(){var fd=new FormData();fd.append("file",fi);fd.append("date",S.date);fd.append("slot",k);fd.append("page",C.page);return send(C.u.photo,fd);})
.then(function(j){var s=slot(k);s.ph=j.id;s.phu=j.url;S.open[k]=true;render();status(W.saved);}).catch(function(){status(W.err,true);});});
render();
if(!C.fixed&&today()!==S.date){go(today());}
if(C.fixed){var fe=document.getElementById("food");if(fe){setTimeout(function(){fe.scrollIntoView();},300);}}
})();
JS;
    return '<script>' . str_replace(["\r", "\n"], ['', ' '], $js) . '</script>';
}
