<?php
if (!defined('ABSPATH')) return;
/* ---------- Food diary (Matteo, 19 Nov 2026) ----------
 * For athletes with the "Nutrition package" (post meta cc_nutri_pkg, switched on by Matteo on the athlete's page or by Marine in her view).
 * Athletes log their food per day in fixed slots (search in an open food database copied into the hub: ANSES-CIQUAL + USDA FoodData Central (SR Legacy, Foundation, FNDDS)
 * + McCance and Widdowson's CoFID (UK) + a few café drinks computed from those official values; UK/Irish search words have aliases in the JS,
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
        'closest' => ['No exact match. Closest foods:', 'Nessuna corrispondenza esatta. Alimenti più vicini:', 'Sem correspondência exata. Alimentos mais próximos:', 'Ni natančnega zadetka. Najbližja živila:', 'Žiadna presná zhoda. Najbližšie potraviny:'],
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
        'weight_n' => ['Your weight (kg) — helps Marine read your diary.', 'Il tuo peso (kg) — aiuta Marine a leggere il tuo diario.', 'O teu peso (kg) — ajuda a Marine a ler o teu diário.', 'Tvoja teža (kg) — Marine pomaga brati tvoj dnevnik.', 'Tvoja hmotnosť (kg) — pomáha Marine čítať tvoj denník.'],
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
        /* 19 Nov 2026: hydration, sodium, weight from Vekta, raw/cooked, micronutrients, trends */
        'drinks' => ['Drinks (ml)', 'Bevande (ml)', 'Bebidas (ml)', 'Pijača (ml)', 'Nápoje (ml)'],
        'drinks_h' => ['Water, electrolyte drink, juice…', 'Acqua, bevanda salina, succo…', 'Água, bebida isotónica, sumo…', 'Voda, elektrolitski napitek, sok…', 'Voda, iontový nápoj, džús…'],
        'fluids' => ['Fluids', 'Liquidi', 'Líquidos', 'Tekočina', 'Tekutiny'],
        'per_h' => ['per hour', 'all’ora', 'por hora', 'na uro', 'za hodinu'],
        'ride' => ['Your ride', 'La tua uscita', 'O teu treino', 'Tvoja vožnja', 'Tvoja jazda'],
        'sodium' => ['Sodium', 'Sodio', 'Sódio', 'Natrij', 'Sodík'],
        'na_inc' => ['sodium incomplete', 'sodio incompleto', 'sódio incompleto', 'natrij nepopoln', 'sodík neúplný'],
        'vk_weight' => ['Weight from Vekta: %1$s kg (%2$s)', 'Peso da Vekta: %1$s kg (%2$s)', 'Peso do Vekta: %1$s kg (%2$s)', 'Teža iz Vekte: %1$s kg (%2$s)', 'Hmotnosť z Vekty: %1$s kg (%2$s)'],
        'vk_weight_h' => ['Carbs and protein per kg use your latest weight.', 'Carboidrati e proteine per kg usano il tuo peso più recente.', 'Os hidratos e a proteína por kg usam o teu peso mais recente.', 'Ogljikovi hidrati in beljakovine na kg uporabljajo tvojo zadnjo težo.', 'Sacharidy a bielkoviny na kg používajú tvoju poslednú hmotnosť.'],
        'b_raw' => ['RAW / DRY', 'CRUDO / SECCO', 'CRU / SECO', 'SUROVO / SUHO', 'SUROVÉ / SUCHÉ'],
        'b_cooked' => ['COOKED', 'COTTO', 'COZINHADO', 'KUHANO', 'VARENÉ'],
        'ask_rc' => ['Did you weigh it raw or cooked?', 'L’hai pesato crudo o cotto?', 'Pesaste cru ou cozinhado?', 'Si ga stehtal surovega ali kuhanega?', 'Vážil si to surové alebo uvarené?'],
        'w_raw' => ['Raw / dry', 'Crudo / secco', 'Cru / seco', 'Surovo / suho', 'Surové / suché'],
        'w_cooked' => ['Cooked', 'Cotto', 'Cozinhado', 'Kuhano', 'Uvarené'],
        'weigh_h' => ['Weigh raw or cooked as you prefer, then pick the matching food.', 'Pesa crudo o cotto come preferisci, poi scegli l’alimento corrispondente.', 'Pesa cru ou cozinhado, como preferires, e escolhe o alimento correspondente.', 'Stehtaj surovo ali kuhano, kakor ti je ljubše, nato izberi ustrezno živilo.', 'Váž surové alebo uvarené, ako chceš, a potom vyber zodpovedajúcu potravinu.'],
        'micro' => ['Micronutrients & electrolytes (day total)', 'Micronutrienti ed elettroliti (totale del giorno)', 'Micronutrientes e eletrólitos (total do dia)', 'Mikrohranila in elektroliti (skupaj za dan)', 'Mikroživiny a elektrolyty (spolu za deň)'],
        'electro' => ['Electrolytes', 'Elettroliti', 'Eletrólitos', 'Elektroliti', 'Elektrolyty'],
        'microh' => ['Micronutrients', 'Micronutrienti', 'Micronutrientes', 'Mikrohranila', 'Mikroživiny'],
        'ri' => ['% of reference intake', '% dell’assunzione di riferimento', '% da dose de referência', '% referenčnega vnosa', '% referenčného príjmu'],
        'ri_note' => ['Reference intakes for an average adult (EU). Needs can be higher on long rides.', 'Assunzioni di riferimento per un adulto medio (UE). Il fabbisogno può essere più alto nelle uscite lunghe.', 'Doses de referência para um adulto médio (UE). As necessidades podem ser maiores em treinos longos.', 'Referenčni vnosi za povprečno odraslo osebo (EU). Na dolgih vožnjah so potrebe lahko višje.', 'Referenčné príjmy pre priemerného dospelého (EÚ). Pri dlhých jazdách môže byť potreba vyššia.'],
        'incomplete' => ['incomplete', 'incompleto', 'incompleto', 'nepopolno', 'neúplné'],
        'inc_h' => ['“incomplete”: some foods have no value for it, so the real total is higher.', '“incompleto”: alcuni alimenti non hanno questo valore, quindi il totale reale è più alto.', '“incompleto”: alguns alimentos não têm este valor, por isso o total real é maior.', '“nepopolno”: nekatera živila te vrednosti nimajo, zato je dejanski seštevek višji.', '“neúplné”: niektoré potraviny túto hodnotu nemajú, takže skutočný súčet je vyšší.'],
        'm_k' => ['Potassium', 'Potassio', 'Potássio', 'Kalij', 'Draslík'], 'm_mg' => ['Magnesium', 'Magnesio', 'Magnésio', 'Magnezij', 'Horčík'],
        'm_ca' => ['Calcium', 'Calcio', 'Cálcio', 'Kalcij', 'Vápnik'], 'm_cl' => ['Chloride', 'Cloruro', 'Cloreto', 'Klorid', 'Chlorid'],
        'm_fe' => ['Iron', 'Ferro', 'Ferro', 'Železo', 'Železo'], 'm_zn' => ['Zinc', 'Zinco', 'Zinco', 'Cink', 'Zinok'],
        'm_vc' => ['Vitamin C', 'Vitamina C', 'Vitamina C', 'Vitamin C', 'Vitamín C'], 'm_vd' => ['Vitamin D', 'Vitamina D', 'Vitamina D', 'Vitamin D', 'Vitamín D'],
        'm_b12' => ['Vitamin B12', 'Vitamina B12', 'Vitamina B12', 'Vitamin B12', 'Vitamín B12'], 'm_fol' => ['Folate', 'Folati', 'Folato', 'Folat', 'Folát'],
        'm_va' => ['Vitamin A', 'Vitamina A', 'Vitamina A', 'Vitamin A', 'Vitamín A'], 'm_ve' => ['Vitamin E', 'Vitamina E', 'Vitamina E', 'Vitamin E', 'Vitamín E'],
        'm_io' => ['Iodine', 'Iodio', 'Iodo', 'Jod', 'Jód'],
        'mytrends' => ['My trends', 'I miei andamenti', 'As minhas tendências', 'Moji trendi', 'Moje trendy'],
        'tr_lede' => ['The last 12 weeks. The dashed line is your own 28-day average.', 'Le ultime 12 settimane. La linea tratteggiata è la tua media degli ultimi 28 giorni.', 'As últimas 12 semanas. A linha tracejada é a tua média dos últimos 28 dias.', 'Zadnjih 12 tednov. Črtkana črta je tvoje povprečje zadnjih 28 dni.', 'Posledných 12 týždňov. Prerušovaná čiara je tvoj priemer za posledných 28 dní.'],
        'tr_w' => ['Weight (kg)', 'Peso (kg)', 'Peso (kg)', 'Teža (kg)', 'Hmotnosť (kg)'],
        'tr_hrv' => ['HRV (ms, overnight)', 'HRV (ms, notturna)', 'HRV (ms, noturna)', 'HRV (ms, ponoči)', 'HRV (ms, nočná)'],
        'tr_rhr' => ['Resting heart rate (bpm)', 'Frequenza cardiaca a riposo (bpm)', 'Frequência cardíaca em repouso (bpm)', 'Srčni utrip v mirovanju (bpm)', 'Pokojová tepová frekvencia (bpm)'],
        'tr_avg' => ['28-day average', 'media 28 giorni', 'média de 28 dias', 'povprečje 28 dni', 'priemer 28 dní'],
        'nodata' => ['No data yet', 'Ancora nessun dato', 'Ainda sem dados', 'Še ni podatkov', 'Zatiaľ žiadne údaje'],
        'recent' => ['Recent', 'Recenti', 'Recentes', 'Nedavno', 'Nedávne'],
        'favs' => ['Favourites', 'Preferiti', 'Favoritos', 'Priljubljeni', 'Obľúbené'],
        'star_add' => ['Add to favourites', 'Aggiungi ai preferiti', 'Adicionar aos favoritos', 'Dodaj med priljubljene', 'Pridať medzi obľúbené'],
        'star_rm' => ['Remove from favourites', 'Togli dai preferiti', 'Remover dos favoritos', 'Odstrani iz priljubljenih', 'Odstrániť z obľúbených'],
        'copy_y' => ['Copy from yesterday', 'Copia da ieri', 'Copiar de ontem', 'Kopiraj od včeraj', 'Kopírovať zo včera'],
        'copy_day' => ['Copy whole day from yesterday', 'Copia tutto il giorno da ieri', 'Copiar o dia inteiro de ontem', 'Kopiraj ves dan od včeraj', 'Kopírovať celý deň zo včera'],
        'copy_q' => ['Replace this day’s foods and drinks with yesterday’s? Notes and photos stay as they are.', 'Sostituire alimenti e bevande di questo giorno con quelli di ieri? Note e foto restano come sono.', 'Substituir os alimentos e bebidas deste dia pelos de ontem? As notas e fotos ficam como estão.', 'Zamenjam živila in pijačo tega dne z včerajšnjimi? Opombe in fotografije ostanejo.', 'Nahradiť jedlá a nápoje tohto dňa včerajšími? Poznámky a fotky zostanú.'],
        'copy_none' => ['Nothing logged the day before.', 'Niente registrato il giorno prima.', 'Nada registado no dia anterior.', 'Prejšnji dan ni nič zapisano.', 'Deň predtým nie je nič zapísané.'],
        'ride_t' => ['Ride time (h:mm)', 'Durata uscita (h:mm)', 'Duração do treino (h:mm)', 'Čas vožnje (h:mm)', 'Čas jazdy (h:mm)'],
        'ride_rec' => ['From your recorded ride: %s', 'Dalla tua uscita registrata: %s', 'Do teu treino registado: %s', 'Iz zapisane vožnje: %s', 'Zo zaznamenanej jazdy: %s'],
        'g_h' => ['Carbs per hour', 'Carboidrati all’ora', 'Hidratos por hora', 'Ogljikovi hidrati na uro', 'Sacharidy za hodinu'],
        'ml_h' => ['Fluids per hour', 'Liquidi all’ora', 'Líquidos por hora', 'Tekočina na uro', 'Tekutiny za hodinu'],
        'target' => ['target %s', 'obiettivo %s', 'objetivo %s', 'cilj %s', 'cieľ %s'],
        'streak' => ['%d days logged in a row', '%d giorni registrati di fila', '%d dias registados seguidos', '%d dni zapored zapisanih', '%d dní zapísaných po sebe'],
        'add_short' => ['+ Add', '+ Aggiungi', '+ Adicionar', '+ Dodaj', '+ Pridať'],
        'of_energy' => ['of energy', 'dell’energia', 'da energia', 'energije', 'energie'],
        'new_msg' => ['New message from %s', 'Nuovo messaggio da %s', 'Nova mensagem de %s', 'Novo sporočilo od %s', 'Nová správa od %s'],
        'log_today' => ['Log today’s food', 'Registra il cibo di oggi', 'Regista a comida de hoje', 'Zapiši današnjo hrano', 'Zapíš dnešné jedlo'],
        'cyc_title' => ['My cycle', 'Il mio ciclo', 'O meu ciclo', 'Moj cikel', 'Môj cyklus'],
        'cyc_consent' => ['Optional. Track your cycle so Marine can adapt your fuelling. Only you, Marine and Matteo can see it. You can turn it off and delete it any time.',
                          'Facoltativo. Registra il tuo ciclo così Marine può adattare la tua alimentazione. Lo vedete solo tu, Marine e Matteo. Puoi disattivarlo e cancellarlo in qualsiasi momento.',
                          'Opcional. Regista o teu ciclo para que a Marine possa adaptar a tua alimentação. Só tu, a Marine e o Matteo o podem ver. Podes desativá-lo e apagá-lo a qualquer momento.',
                          'Neobvezno. Beleži svoj cikel, da lahko Marine prilagodi tvojo prehrano. Vidite ga samo ti, Marine in Matteo. Kadar koli ga lahko izklopiš in izbrišeš.',
                          'Nepovinné. Zaznamenávaj si cyklus, aby ti Marine mohla prispôsobiť stravovanie. Vidíš ho len ty, Marine a Matteo. Kedykoľvek ho môžeš vypnúť a vymazať.'],
        'cyc_on' => ['Turn on', 'Attiva', 'Ativar', 'Vklopi', 'Zapnúť'],
        'cyc_start' => ['My period started this day', 'Il ciclo è iniziato questo giorno', 'O período começou neste dia', 'Menstruacija se je začela ta dan', 'Menštruácia začala v tento deň'],
        'cyc_end' => ['My period ended this day', 'Il ciclo è finito questo giorno', 'O período terminou neste dia', 'Menstruacija se je končala ta dan', 'Menštruácia skončila v tento deň'],
        'cyc_unset' => ['Undo for this day', 'Annulla per questo giorno', 'Anular neste dia', 'Razveljavi za ta dan', 'Zrušiť pre tento deň'],
        'cyc_off' => ['Turn off and delete my cycle data', 'Disattiva e cancella i dati del mio ciclo', 'Desativar e apagar os dados do meu ciclo', 'Izklopi in izbriši podatke o mojem ciklu', 'Vypnúť a vymazať údaje o mojom cykle'],
        'cyc_offq' => ['Turn off and delete all your cycle data? This cannot be undone.', 'Disattivare e cancellare tutti i dati del ciclo? Non si può annullare.', 'Desativar e apagar todos os dados do ciclo? Não é possível anular.', 'Izklopim in izbrišem vse podatke o ciklu? Tega ni mogoče razveljaviti.', 'Vypnúť a vymazať všetky údaje o cykle? Nedá sa to vrátiť späť.'],
        'cyc_day' => ['Day %d', 'Giorno %d', 'Dia %d', 'Dan %d', 'Deň %d'],
        'ph_m' => ['Menstrual', 'Mestruale', 'Menstrual', 'Menstruacija', 'Menštruácia'],
        'ph_f' => ['Follicular', 'Follicolare', 'Folicular', 'Folikularna', 'Folikulárna'],
        'ph_o' => ['Ovulation (estimate)', 'Ovulazione (stima)', 'Ovulação (estimativa)', 'Ovulacija (ocena)', 'Ovulácia (odhad)'],
        'ph_l' => ['Luteal', 'Luteale', 'Lútea', 'Lutealna', 'Luteálna'],
        'cyc_len' => ['Average cycle: %d days', 'Ciclo medio: %d giorni', 'Ciclo médio: %d dias', 'Povprečen cikel: %d dni', 'Priemerný cyklus: %d dní'],
        'cyc_def' => ['Average cycle: 28 days (used until 2 cycles are logged)', 'Ciclo medio: 28 giorni (finché non registri 2 cicli)', 'Ciclo médio: 28 dias (até registares 2 ciclos)', 'Povprečen cikel: 28 dni (dokler ne zabeležiš 2 ciklov)', 'Priemerný cyklus: 28 dní (kým nezaznamenáš 2 cykly)'],
        'cyc_starts' => ['Period starts logged', 'Inizi del ciclo registrati', 'Inícios do período registados', 'Zabeleženi začetki menstruacije', 'Zaznamenané začiatky menštruácie'],
        'iron_line' => ['Iron: %s mg of 14 mg', 'Ferro: %s mg su 14 mg', 'Ferro: %s mg de 14 mg', 'Železo: %s mg od 14 mg', 'Železo: %s mg zo 14 mg'],
        'iron_note' => ['Iron today: %s mg of 14 mg. Iron-rich ideas: red meat, lentils and beans, spinach or kale with vitamin C (e.g. orange juice), fortified breakfast cereals.',
                        'Ferro oggi: %s mg su 14 mg. Idee ricche di ferro: carne rossa, lenticchie e fagioli, spinaci o cavolo riccio con vitamina C (ad es. succo d’arancia), cereali per la colazione fortificati.',
                        'Ferro hoje: %s mg de 14 mg. Ideias ricas em ferro: carne vermelha, lentilhas e feijão, espinafres ou couve kale com vitamina C (p. ex. sumo de laranja), cereais de pequeno-almoço fortificados.',
                        'Železo danes: %s mg od 14 mg. Ideje, bogate z železom: rdeče meso, leča in fižol, špinača ali ohrovt z vitaminom C (npr. pomarančni sok), obogateni kosmiči za zajtrk.',
                        'Železo dnes: %s mg zo 14 mg. Nápady bohaté na železo: červené mäso, šošovica a fazuľa, špenát alebo kel s vitamínom C (napr. pomarančový džús), obohatené raňajkové cereálie.'],
        /* 19 Nov 2026 (nutrition backlog 1-4): water vs other drinks, portions, voice logging, Marine's day targets */
        'water' => ['Water (ml)', 'Acqua (ml)', 'Água (ml)', 'Voda (ml)', 'Voda (ml)'],
        'water_h' => ['Other drinks (coffee, juice, milk, sports drink…): add them as foods above.', 'Altre bevande (caffè, succo, latte, bevanda sportiva…): aggiungile come alimenti qui sopra.', 'Outras bebidas (café, sumo, leite, bebida desportiva…): adiciona-as como alimentos acima.', 'Druge pijače (kava, sok, mleko, športni napitek…): dodaj jih zgoraj kot živila.', 'Iné nápoje (káva, džús, mlieko, športový nápoj…): pridaj ich vyššie ako potraviny.'],
        'w_tile' => ['Water', 'Acqua', 'Água', 'Voda', 'Voda'],
        'od_tile' => ['Other drinks', 'Altre bevande', 'Outras bebidas', 'Druge pijače', 'Iné nápoje'],
        'tf_tile' => ['Total fluids', 'Liquidi totali', 'Líquidos totais', 'Tekočina skupaj', 'Tekutiny spolu'],
        'amount' => ['Amount', 'Quantità', 'Quantidade', 'Količina', 'Množstvo'],
        'unit' => ['Unit', 'Unità di misura', 'Unidade', 'Enota', 'Jednotka'],
        'un_g' => ['g', 'g', 'g', 'g', 'g'], 'un_u' => ['unit', 'unità', 'unidade', 'kos', 'kus'], 'un_s' => ['small', 'piccolo', 'pequeno', 'majhen', 'malý'],
        'un_m' => ['medium', 'medio', 'médio', 'srednji', 'stredný'], 'un_l' => ['large', 'grande', 'grande', 'velik', 'veľký'], 'un_sl' => ['slice', 'fetta', 'fatia', 'rezina', 'plátok'],
        'un_pot' => ['pot', 'vasetto', 'copo', 'lonček', 'téglik'], 'un_tsp' => ['tsp', 'cucchiaino', 'colher de chá', 'čajna žlička', 'čajová lyžička'],
        'un_tbsp' => ['tbsp', 'cucchiaio', 'colher de sopa', 'jedilna žlica', 'polievková lyžica'], 'un_cup' => ['cup', 'tazza', 'chávena', 'skodelica', 'šálka'],
        'un_can' => ['can', 'lattina', 'lata', 'pločevinka', 'plechovka'], 'un_btl' => ['bottle', 'bottiglia', 'garrafa', 'steklenica', 'fľaša'],
        'v_btn' => ['Say what you ate', 'Di’ cosa hai mangiato', 'Diz o que comeste', 'Povej, kaj si jedel', 'Povedz, čo si jedol'],
        'v_listen' => ['Listening… say e.g. “two slices of toast with jam and a banana”', 'Ti ascolto… di’ per es. “due fette di pane con marmellata e una banana”', 'A ouvir… diz p. ex. “duas fatias de pão com doce e uma banana”', 'Poslušam… reci npr. “dve rezini kruha z marmelado in banana”', 'Počúvam… povedz napr. „dva plátky chleba s džemom a banán“'],
        'v_text' => ['What you ate (you can edit it or type it)', 'Cosa hai mangiato (puoi modificarlo o scriverlo)', 'O que comeste (podes editar ou escrever)', 'Kaj si jedel (lahko popraviš ali napišeš)', 'Čo si jedol (môžeš to upraviť alebo napísať)'],
        'v_read' => ['Find these foods', 'Trova questi alimenti', 'Encontrar estes alimentos', 'Poišči ta živila', 'Nájsť tieto potraviny'],
        'v_again' => ['Speak again', 'Parla di nuovo', 'Falar de novo', 'Govori znova', 'Hovoriť znova'],
        'v_right' => ['Is this right?', 'È giusto?', 'Está certo?', 'Je to prav?', 'Je to správne?'],
        'v_logall' => ['Log all', 'Registra tutto', 'Registar tudo', 'Zapiši vse', 'Zapísať všetko'],
        'v_none' => ['No food found for “%s”. Try another word.', 'Nessun alimento trovato per “%s”. Prova un’altra parola.', 'Nenhum alimento encontrado para “%s”. Tenta outra palavra.', 'Za “%s” ni živila. Poskusi z drugo besedo.', 'Pre „%s“ sa nenašla potravina. Skús iné slovo.'],
        'v_nosup' => ['Voice input isn’t available in this browser. Tip: tap the box below and use the microphone on your keyboard, then tap “Find these foods”.', 'L’input vocale non è disponibile in questo browser. Consiglio: tocca il riquadro qui sotto e usa il microfono della tastiera, poi tocca “Trova questi alimenti”.', 'A entrada por voz não está disponível neste navegador. Dica: toca na caixa abaixo e usa o microfone do teclado; depois toca em “Encontrar estes alimentos”.', 'Glasovni vnos v tem brskalniku ni na voljo. Namig: tapni polje spodaj in uporabi mikrofon na tipkovnici, nato tapni “Poišči ta živila”.', 'Hlasový vstup v tomto prehliadači nie je dostupný. Tip: ťukni do poľa nižšie a použi mikrofón na klávesnici, potom ťukni na „Nájsť tieto potraviny“.'],
        'v_err' => ['I didn’t catch that. Try again or type it below.', 'Non ho capito. Riprova o scrivilo qui sotto.', 'Não percebi. Tenta de novo ou escreve abaixo.', 'Nisem razumel. Poskusi znova ali napiši spodaj.', 'Nerozumel som. Skús znova alebo to napíš nižšie.'],
        'v_food' => ['Food', 'Alimento', 'Alimento', 'Živilo', 'Potravina'],
        'tg_of' => ['%1$s of %2$s kcal', '%1$s di %2$s kcal', '%1$s de %2$s kcal', '%1$s od %2$s kcal', '%1$s z %2$s kcal'],
        'tg_eat' => ['You’ve eaten', 'Hai mangiato', 'Já comeste', 'Pojedel si', 'Zjedol si'],
        'tg_your' => ['of your', 'delle tue', 'das tuas', 'od svojih', 'z tvojich'],
        'tg_go' => ['%s to go', 'ancora %s', 'faltam %s', 'še %s', 'ešte %s'],
        'tg_done' => ['%s kcal reached ✓', '%s kcal raggiunte ✓', '%s kcal alcançadas ✓', '%s kcal doseženih ✓', '%s kcal splnených ✓'],
        'tg_mac' => ['%1$s of %2$s g', '%1$s di %2$s g', '%1$s de %2$s g', '%1$s od %2$s g', '%1$s z %2$s g'],
        'tg_ml' => ['%1$s of %2$s ml', '%1$s di %2$s ml', '%1$s de %2$s ml', '%1$s od %2$s ml', '%1$s z %2$s ml'],
        'tg_meal' => ['Your target', 'Il tuo obiettivo', 'O teu objetivo', 'Tvoj cilj', 'Tvoj cieľ'],
        'tg_title' => ['Today’s targets from Marine', 'Obiettivi di oggi da Marine', 'Objetivos de hoje da Marine', 'Današnji cilji od Marine', 'Dnešné ciele od Marine'],
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
function cc_fd_get($pid, $date) { $a = json_decode((string) get_post_meta((int) $pid, 'cc_fd_' . $date, true), true); return is_array($a) ? cc_fd_fresh_day($pid, $a) : ['s' => [], 'r' => []]; }
/* Marine 19 Nov: a diary line keeps a copy of the food's values from the day it was added, so lines from before the sodium column had no sodium.
   Every read now takes the values from the CURRENT food table (database foods, by id) or from the athlete's current own foods and recipes;
   the stored copy is only the fallback when the id is gone. The state (raw / cooked) and the grams stay as logged. */
function cc_fd_dbidx() {
    static $ix = null; if ($ix !== null) return $ix; $ix = [];
    $j = json_decode((string) get_option('cc_food_db', ''), true);
    foreach ((array) ($j['foods'] ?? []) as $r) if (is_array($r) && isset($r[0], $r[4])) $ix[(string) $r[0]] = [(float) $r[4], (float) ($r[5] ?? 0), (float) ($r[6] ?? 0), (float) ($r[7] ?? 0), (float) ($r[8] ?? 0), (float) ($r[9] ?? 0), isset($r[10]) ? (float) $r[10] : null];
    return $ix;
}
function cc_fd_fresh_item($it, $own) {
    if (!is_array($it) || empty($it['id'])) return $it;
    $id = (string) $it['id'];
    if (!empty($it['m'])) { $m = $own[$id] ?? null; if (!$m) return $it; $v = [$m['k'] ?? 0, $m['c'] ?? 0, $m['p'] ?? 0, $m['f'] ?? 0, $m['fi'] ?? 0, $m['su'] ?? 0, (isset($m['na']) && $m['na'] !== '') ? $m['na'] : null]; }
    else { $ix = cc_fd_dbidx(); if (!isset($ix[$id])) return $it; $v = $ix[$id]; }
    foreach (['k', 'c', 'p', 'f', 'fi', 'su'] as $i => $f) $it[$f] = round((float) $v[$i], 1);
    if ($v[6] === null) unset($it['na']); else $it['na'] = round((float) $v[6], 1);
    return $it;
}
function cc_fd_own_idx($mine) { $o = []; foreach ((array) $mine as $m) if (!empty($m['id'])) $o[(string) $m['id']] = $m; return $o; }
function cc_fd_fresh_day($pid, $a) {
    $own = cc_fd_own_idx(cc_fd_mine($pid));
    foreach ((array) ($a['s'] ?? []) as $k => $s) if (!empty($s['i']) && is_array($s['i'])) foreach ($s['i'] as $x => $it) $a['s'][$k]['i'][$x] = cc_fd_fresh_item($it, $own);
    return $a;
}
function cc_fd_put($pid, $date, $a) { update_post_meta((int) $pid, 'cc_fd_' . $date, wp_slash(wp_json_encode($a))); }
function cc_fd_mine_raw($pid) { $a = json_decode((string) get_post_meta((int) $pid, 'cc_food_mine', true), true); return is_array($a) ? $a : []; }
/* own foods and recipes; a recipe's values per 100 g are worked out again from its ingredients' current values (same rule as the diary lines) */
function cc_fd_mine($pid) {
    static $c = []; $pid = (int) $pid; if (isset($c[$pid])) return $c[$pid];
    $mine = cc_fd_mine_raw($pid); $own = [];
    foreach ($mine as $m) if (is_array($m) && !empty($m['id']) && ($m['t'] ?? 'f') !== 'r') $own[(string) $m['id']] = $m;
    foreach ($mine as $x => $m) {
        if (!is_array($m) || ($m['t'] ?? '') !== 'r' || empty($m['ing'])) continue;
        $sum = 0; $tot = ['k' => 0, 'c' => 0, 'p' => 0, 'f' => 0, 'fi' => 0, 'su' => 0]; $na = 0; $nam = 0;
        foreach ($m['ing'] as $y => $i) { $i = cc_fd_fresh_item($i, $own); $m['ing'][$y] = $i; $g = (float) ($i['g'] ?? 0); if ($g <= 0) continue; $sum += $g;
            foreach ($tot as $f => $_) $tot[$f] += (float) ($i[$f] ?? 0) * $g / 100; if (isset($i['na'])) $na += (float) $i['na'] * $g / 100; else $nam++; }
        $w = (float) ($m['cw'] ?? 0); if ($w <= 0) $w = $sum;
        if ($w > 0) { foreach ($tot as $f => $v) $m[$f] = round($v * 100 / $w, 1); $m['na'] = $nam ? null : round($na * 100 / $w, 1); }
        $mine[$x] = $m;
    }
    return $c[$pid] = $mine;
}
function cc_fd_kg($pid) { $k = (float) get_post_meta((int) $pid, 'cc_food_kg', true); return $k > 0 ? $k : 0; }
function cc_fd_vx($pid) { $a = json_decode((string) get_post_meta((int) $pid, 'cc_food_vx', true), true); return is_array($a) ? $a : []; }
function cc_fd_num($v, $max) { $v = (float) str_replace(',', '.', (string) $v); return $v > 0 ? round(min($v, $max), 1) : 0; }
function cc_fd_txt($v, $n) { return mb_substr(trim(sanitize_text_field((string) $v)), 0, $n); }
function cc_fd_item($it) {
    if (!is_array($it)) return null;
    $o = ['id' => mb_substr(preg_replace('/[^A-Za-z0-9_-]/', '', (string) ($it['id'] ?? '')), 0, 40), 'n' => cc_fd_txt($it['n'] ?? '', 200), 'g' => cc_fd_num($it['g'] ?? 0, 5000)];
    foreach (['k' => 950, 'c' => 100, 'p' => 100, 'f' => 100, 'fi' => 100, 'su' => 100] as $f => $mx) $o[$f] = cc_fd_num($it[$f] ?? 0, $mx);
    if (in_array($it['m'] ?? '', ['f', 'r'], true)) $o['m'] = $it['m'];
    // sodium mg per 100 g: only when known (missing stays missing, never 0); state of the food as weighed: r = raw / dry, c = cooked
    $na = str_replace(',', '.', (string) ($it['na'] ?? ''));
    if ($na !== '' && is_numeric($na) && (float) $na >= 0) $o['na'] = round(min((float) $na, 50000), 1);
    if (in_array($it['st'] ?? '', ['r', 'c'], true)) $o['st'] = $it['st'];
    if (preg_match('/^[a-z0-9]{4,20}$/', (string) ($it['pl'] ?? ''))) $o['pl'] = $it['pl'];   // mealplan.php: logged from Marine's planned item
    if (in_array($it['u'] ?? '', ['u', 's', 'm', 'l', 'sl', 'pot', 'tsp', 'tbsp', 'cup', 'can', 'btl'], true) && ($q = cc_fd_num($it['q'] ?? 0, 100)) > 0) { $o['u'] = $it['u']; $o['q'] = $q; }   // portion as logged, e.g. 1 medium (the grams stay in g)
    if (!empty($it['dr'])) $o['dr'] = 1;   // a drink (counted as ml of other drinks)
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
        $ml = (int) round(cc_fd_num($s['d'] ?? 0, 10000)); if ($ml > 0) $o['d'] = $ml;   // water in ml (named "drinks" before 19 Nov 2026; those values count as water)
        if ($k === 'bike') { $rt = (int) round(cc_fd_num($s['r'] ?? 0, 1440)); if ($rt > 0) $o['r'] = $rt; }   // ride time in minutes (typed by the athlete)
        if (!empty($old[$k]['ph'])) $o['ph'] = (int) $old[$k]['ph'];
        if ($o['t'] !== '' || $o['n'] !== '' || $o['i'] || !empty($o['ph']) || $ml > 0) $out[$k] = $o;
    }
    return $out;
}
function cc_fd_tot($items) {
    $t = ['k' => 0, 'c' => 0, 'p' => 0, 'f' => 0, 'fi' => 0, 'su' => 0];
    foreach ((array) $items as $it) { $m = ((float) ($it['g'] ?? 0)) / 100; foreach ($t as $f => $_) $t[$f] += ((float) ($it[$f] ?? 0)) * $m; }
    $t['na'] = 0; $t['nam'] = 0;   // sodium mg and the number of lines without a sodium value
    foreach ((array) $items as $it) { $g = (float) ($it['g'] ?? 0); if ($g <= 0) continue; if (isset($it['na'])) $t['na'] += ((float) $it['na']) * $g / 100; else $t['nam']++; }
    return $t;
}
function cc_fd_daytot($day) { $all = []; foreach ((array) ($day['s'] ?? []) as $s) foreach ((array) ($s['i'] ?? []) as $it) $all[] = $it; return cc_fd_tot($all); }
function cc_fd_dayml($day) { $f = cc_fd_fluids($day); return $f[0] + $f[1]; }
/* 19 Nov 2026: [water ml, other drinks ml]. Water = the slot's "Water (ml)" field (before 19 Nov it was "Drinks (ml)": those values count as water)
   + foods of the Water family; other drinks = grams of drink foods (juice, coffee, milk, sports drinks...; 1 g taken as 1 ml) */
function cc_fd_fluids($day) {
    $w = 0; $o = 0;
    foreach ((array) ($day['s'] ?? []) as $s) { $w += (int) ($s['d'] ?? 0);
        foreach ((array) ($s['i'] ?? []) as $it) { $k = function_exists('cc_np_drink') ? cc_np_drink($it) : (!empty($it['dr']) ? 'd' : ''); if ($k === 'w') $w += (float) ($it['g'] ?? 0); elseif ($k) $o += (float) ($it['g'] ?? 0); } }
    return [(int) round($w), (int) round($o)];
}
/* "1 medium (118 g)" when the athlete logged a portion, else "118 g" */
function cc_fd_amount($it) {
    $g = cc_fd_f1($it['g'] ?? 0) . ' g'; if (empty($it['u']) || empty($it['q'])) return $g;
    return cc_fd_f1($it['q']) . ((float) $it['q'] == 1 ? ' ' : ' × ') . cc_fd_w('un_' . $it['u']) . ' (' . $g . ')';
}
/* weight used for g/kg: the latest Vekta weight (last 60 days, sent by Matteo's laptop) when there is one, else the athlete's own entry.
   TrainingPeaks athletes never get a Vekta weight. */
function cc_fd_kgv($pid) {
    if (!cc_ath_tp($pid)) { $vx = cc_fd_vx($pid); $w = $vx['kg'] ?? null;
        if (is_array($w) && ($w['v'] ?? 0) > 0 && !empty($w['d']) && strtotime($w['d'] . ' 12:00') >= time() - 60 * DAY_IN_SECONDS) return ['kg' => (float) $w['v'], 'src' => 'vekta', 'd' => (string) $w['d']]; }
    $k = cc_fd_kg($pid); return $k ? ['kg' => $k, 'src' => 'athlete', 'd' => ''] : ['kg' => 0, 'src' => '', 'd' => ''];
}
/* minutes ridden per day (done sessions from Vekta) for the "per hour" line of On the bike */
function cc_fd_rides($vx) { $o = []; foreach ((array) ($vx['done'] ?? []) as $a) if (!empty($a['d']) && ($a['min'] ?? 0) > 0) $o[$a['d']] = ($o[$a['d']] ?? 0) + (int) $a['min']; return $o; }
/* the carbs (g/h) and fluids (ml/h) targets Marine wrote in that day's nutrition note, e.g. "70 g/h", "80 g carbs per hour", "500 ml per hour" */
function cc_fd_targets($vx) {
    $o = [];
    foreach ((array) ($vx['notes'] ?? []) as $n) {
        $txt = ($n['t'] ?? '') . ' ' . ($n['c'] ?? ''); $d = $n['d'] ?? ''; if (!$d) continue;
        if (preg_match('/(\d{2,3})\s*(?:-\s*\d{2,3}\s*)?g(?:rams?)?\s*(?:of\s+)?(?:carbs?|carbohydrates?|cho)?\s*(?:\/\s*h(?:r|our)?\b|per\s+hour|an\s+hour|each\s+hour|every\s+hour)/i', $txt, $m)) $o[$d]['c'] = (int) $m[1];
        if (preg_match('/(\d{3,4})\s*ml\s*(?:(?:of\s+)?\w+\s+)?(?:\/\s*h(?:r|our)?\b|per\s+hour|an\s+hour|each\s+hour|every\s+hour)/i', $txt, $m)) $o[$d]['ml'] = (int) $m[1];
    }
    return $o;
}
/* the last 8 different foods this athlete logged (newest first) and their favourites, for one-tap adding */
function cc_fd_recent($pid) {
    $o = []; $seen = [];
    foreach (array_slice(cc_fd_days($pid), 0, 21) as $d) {
        $day = cc_fd_get($pid, $d); $its = [];
        foreach (array_reverse(CC_FD_SLOTS) as $k) foreach (array_reverse((array) ($day['s'][$k]['i'] ?? [])) as $it) $its[] = $it;
        foreach ($its as $it) { $id = $it['id'] ?? ''; if ($id === '' || isset($seen[$id])) continue; $seen[$id] = 1; $o[] = $it; if (count($o) >= 8) return $o; }
    }
    return $o;
}
function cc_fd_fav($pid) { $a = json_decode((string) get_post_meta((int) $pid, 'cc_food_fav', true), true); return is_array($a) ? $a : []; }
/* days logged in a row, counted up to yesterday; the page adds today once something is logged */
function cc_fd_streak($pid) {
    $set = array_flip(array_slice(cc_fd_days($pid), 0, 400)); $n = 0; $t = strtotime(current_time('Y-m-d') . ' 12:00');
    for ($i = 1; $i < 400; $i++) { $d = gmdate('Y-m-d', $t - $i * DAY_IN_SECONDS); if (!isset($set[$d]) || empty(cc_fd_get($pid, $d)['s'])) break; $n++; }
    return $n;
}
function cc_fd_seen($pid) { $a = json_decode((string) get_post_meta((int) $pid, 'cc_fd_seen', true), true); return is_array($a) ? $a : []; }   // per day: when the athlete last saw that day's messages
function cc_fd_trends_on($pid) { return !get_post_meta((int) $pid, 'cc_fd_trends_off', true); }
/* the 12-week trends (weight, HRV, resting HR per day) as the charts get them; null when no series has 3 points */
function cc_fd_trend_data($vx) {
    $rows = array_values(array_filter((array) ($vx['tr'] ?? []), 'is_array')); if (!$rows) return null;
    $n = [0, 0, 0]; foreach ($rows as $r) for ($i = 0; $i < 3; $i++) if (!empty($r[$i + 1])) $n[$i]++;
    if (max($n) < 3) return null;
    $to = current_time('Y-m-d');
    return ['from' => gmdate('Y-m-d', strtotime($to . ' 12:00') - 83 * DAY_IN_SECONDS), 'to' => $to, 'days' => $rows, 'w' => cc_fd_tw()];
}
function cc_fd_tw() { $o = []; foreach (['tr_w', 'tr_hrv', 'tr_rhr', 'tr_avg', 'nodata'] as $k) $o[$k] = cc_fd_w($k); $o['lang'] = $GLOBALS['cc_ath_lang'] ?? 'en'; return $o; }
function cc_fd_mw($fem = false) {
    $o = ['loading' => cc_fd_w('loading')]; if ($fem) $o['fe14'] = cc_fd_w('iron_line'); foreach (['electro', 'microh', 'ri', 'ri_note', 'incomplete', 'inc_h', 'sodium', 'fibre', 'm_k', 'm_mg', 'm_ca', 'm_cl', 'm_fe', 'm_zn', 'm_vc', 'm_vd', 'm_b12', 'm_fol', 'm_va', 'm_ve', 'm_io'] as $k) $o[$k] = cc_fd_w($k);
    $o['lang'] = $GLOBALS['cc_ath_lang'] ?? 'en'; return $o;
}
/* iron screening (female athletes, gender from Vekta; never for TrainingPeaks athletes or unknown gender) */
/* Matteo 19 Nov: no Vekta gender (TrainingPeaks athletes, or not sent yet) -> the rider form's Gender answer (post meta cc_profile) */
function cc_fd_female($pid, $vx = null) {
    $vx = cc_ath_tp($pid) ? [] : ($vx ?? cc_fd_vx($pid)); $s = (string) ($vx['sex'] ?? '');
    if ($s === '') { $a = json_decode((string) get_post_meta((int) $pid, 'cc_profile', true), true); $s = is_array($a) ? (string) ($a['gender'] ?? '') : ''; }
    return $s === 'f';
}
/* "My cycle" (opt-in, female athletes only; Matteo 19 Nov 2026): post meta cc_fd_cycle = {on, p: [[start, end|null], ...]}.
   Never in emails or notifications; deleted with the diary when coaching ends, or by the athlete at any time. */
function cc_fd_cycle($pid) {
    $a = json_decode((string) get_post_meta((int) $pid, 'cc_fd_cycle', true), true);
    if (!is_array($a) || empty($a['on'])) return ['on' => 0, 'p' => []];
    $p = array_values(array_filter((array) ($a['p'] ?? []), function ($x) { return is_array($x) && cc_fd_date($x[0] ?? ''); }));
    usort($p, function ($x, $y) { return strcmp($x[0], $y[0]); });
    return ['on' => 1, 'p' => $p];
}
function cc_fd_cyc_len($p) {   // average of the gaps between starts (18-45 days); 28 until two cycles are logged
    $g = []; for ($i = 1; $i < count($p); $i++) { $d = (int) round((strtotime($p[$i][0] . ' 12:00') - strtotime($p[$i - 1][0] . ' 12:00')) / DAY_IN_SECONDS); if ($d >= 18 && $d <= 45) $g[] = $d; }
    return count($g) >= 2 ? (int) round(array_sum($g) / count($g)) : 28;
}
function cc_fd_phase($cy, $date) {   // ['day' => n, 'ph' => m|f|o|l] or null
    if (empty($cy['on']) || !$cy['p']) return null; $L = cc_fd_cyc_len($cy['p']); $last = null;
    foreach ($cy['p'] as $x) if ($x[0] <= $date) $last = $x;
    if (!$last) return null;
    $day = (int) round((strtotime($date . ' 12:00') - strtotime($last[0] . ' 12:00')) / DAY_IN_SECONDS) + 1; if ($day > $L + 10) return null;
    $plen = !empty($last[1]) ? (int) round((strtotime($last[1] . ' 12:00') - strtotime($last[0] . ' 12:00')) / DAY_IN_SECONDS) + 1 : 5; $ov = $L - 14;
    return ['day' => $day, 'ph' => $day <= $plen ? 'm' : (abs($day - $ov) <= 1 ? 'o' : ($day < $ov ? 'f' : 'l'))];
}
function cc_fd_phase_chip($cy, $date) { $p = cc_fd_phase($cy, $date); return $p ? ' <span class="fd-cchip">' . esc_html(sprintf(cc_fd_w('cyc_day'), $p['day']) . ' · ' . cc_fd_w('ph_' . $p['ph'])) . '</span>' : ''; }
function cc_fd_micro_db() {
    static $M = null; if ($M !== null) return $M;
    $gz = (string) get_option('cc_food_micro_gz', ''); $raw = $gz !== '' ? (string) gzdecode(base64_decode($gz)) : (string) get_option('cc_food_micro', '');
    $j = json_decode($raw, true); $M = is_array($j) && !empty($j['m']) ? $j : ['cols' => [], 'm' => []]; return $M;
}
/* iron of one food per 100 g: the table, or an own recipe computed from its ingredients; null when unknown */
function cc_fd_fe100($id, $rec, $depth = 0) {
    $M = cc_fd_micro_db(); $j = array_search('fe', $M['cols'], true); if ($j === false) return null;
    if (isset($M['m'][$id])) { $v = $M['m'][$id][$j] ?? null; return $v === null ? null : (float) $v; }
    $r = $rec[$id] ?? null; if (!$r || $depth > 2) return null;
    $w = (float) ($r['cw'] ?? 0); $sum = 0; $fe = 0;
    foreach ((array) ($r['ing'] ?? []) as $i) { $g = (float) ($i[1] ?? 0); $sum += $g; if ($g <= 0) continue; $v = cc_fd_fe100($i[0] ?? '', $rec, $depth + 1); if ($v === null) return null; $fe += $v * $g / 100; }
    if ($w <= 0) $w = $sum; return $w > 0 ? $fe * 100 / $w : null;
}
/* a day's iron: total of the foods with a value; incomplete when more than 30 % of the grams have none; low = 3+ meals with food and under 14 mg */
function cc_fd_iron($day, $mine) {
    $rec = (array) cc_fd_recipes($mine); $fe = 0; $g = 0; $miss = 0; $slots = 0;
    foreach ((array) ($day['s'] ?? []) as $s) {
        if (!empty($s['i'])) $slots++;
        foreach ((array) ($s['i'] ?? []) as $it) { $gr = (float) ($it['g'] ?? 0); if ($gr <= 0) continue; $g += $gr; $v = cc_fd_fe100($it['id'] ?? '', $rec); if ($v === null) $miss += $gr; else $fe += $v * $gr / 100; }
    }
    $inc = $g > 0 && $miss / $g > 0.3;
    return ['fe' => $fe, 'inc' => $inc, 'slots' => $slots, 'low' => !$inc && $slots >= 3 && $fe < 14];
}
function cc_fd_micro_url() { return esc_url_raw(add_query_arg('v', get_option('cc_food_micro_v', '0'), rest_url('cc/v1/foods-micro'))); }
/* own recipes for the micronutrient sums: {id: {ing: [[id, g, m]], cw}} */
function cc_fd_recipes($mine) {
    $o = []; foreach ((array) $mine as $m) if (($m['t'] ?? '') === 'r') $o[$m['id']] = ['ing' => array_map(function ($i) { return [$i['id'] ?? '', (float) ($i['g'] ?? 0), $i['m'] ?? '']; }, (array) ($m['ing'] ?? [])), 'cw' => (float) ($m['cw'] ?? 0)];
    return (object) $o;
}
/* the folded "Micronutrients & electrolytes" line under a day (filled in the browser from the micronutrient table) */
function cc_fd_micro_box($day, $mine, $fem = false) {
    $items = []; foreach ((array) ($day['s'] ?? []) as $s) foreach ((array) ($s['i'] ?? []) as $it) $items[] = [$it['id'] ?? '', (float) ($it['g'] ?? 0), $it['m'] ?? ''];
    $t = cc_fd_daytot($day);
    return '<details class="fd-micro" data-url="' . esc_attr(cc_fd_micro_url()) . '" data-w="' . esc_attr(wp_json_encode(cc_fd_mw($fem))) . '" data-items="' . esc_attr(wp_json_encode($items)) . '" data-mine="' . esc_attr(wp_json_encode(cc_fd_recipes($mine)))
        . '" data-na="' . esc_attr(wp_json_encode(['v' => round($t['na']), 'inc' => $t['nam'], 'fi' => round($t['fi'], 1)])) . '"><summary>' . esc_html(cc_fd_w('micro')) . '</summary><div class="fd-mt"></div></details>';
}
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
    $W = []; foreach (['time', 'add', 'search', 'grams', 'addit', 'remove', 'cancel', 'noresults', 'closest', 'loading', 'slot_total', 'day_total', 'carbs', 'protein', 'fat', 'fibre', 'sugars', 'c_ab', 'p_ab', 'f_ab',
                       'weight', 'weight_n', 'note', 'note_ph', 'photo', 'photo_ch', 'photo_del', 'photo_bad', 'uploading', 'saving', 'saved', 'err', 'prev', 'next', 'today', 'gotoday', 'mine', 'mine_lede',
                       'add_label', 'add_recipe', 'name', 'per100', 'optional', 'ingredients', 'add_ing', 'cooked', 'cooked_h', 'save', 'edit', 'del', 'delq', 'myfood', 'myrecipe', 'need', 'need_r',
                       'none_mine', 'thread', 'ask', 'reply', 'send_r', 'sent_err', 'you', 'drinks', 'drinks_h', 'fluids', 'per_h', 'ride', 'sodium', 'na_inc', 'vk_weight', 'vk_weight_h',
                       'b_raw', 'b_cooked', 'ask_rc', 'w_raw', 'w_cooked', 'weigh_h', 'micro', 'mytrends', 'tr_lede',
                       'iron_line', 'iron_note', 'incomplete', 'cyc_title', 'cyc_consent', 'cyc_on', 'cyc_start', 'cyc_end', 'cyc_unset', 'cyc_off', 'cyc_offq', 'cyc_day', 'ph_m', 'ph_f', 'ph_o', 'ph_l', 'cyc_len', 'cyc_def', 'cyc_starts',
                       'recent', 'favs', 'star_add', 'star_rm', 'copy_y', 'copy_day', 'copy_q', 'copy_none', 'ride_t', 'ride_rec', 'g_h', 'ml_h', 'target', 'streak', 'add_short', 'new_msg', 'of_energy',
                       'water', 'water_h', 'w_tile', 'od_tile', 'tf_tile', 'amount', 'unit', 'un_g', 'un_u', 'un_s', 'un_m', 'un_l', 'un_sl', 'un_pot', 'un_tsp', 'un_tbsp', 'un_cup', 'un_can', 'un_btl',
                       'v_btn', 'v_listen', 'v_text', 'v_read', 'v_again', 'v_right', 'v_logall', 'v_none', 'v_nosup', 'v_err', 'v_food', 'tg_of', 'tg_go', 'tg_done', 'tg_mac', 'tg_title', 'tg_eat', 'tg_your', 'tg_ml', 'tg_meal'] as $k) $W[$k] = cc_fd_w($k);
    // ?fd=today (the header chip): the diary on the athlete's own today, scrolled into view
    $go = ($_GET['fd'] ?? '') === 'today';
    $slots = []; foreach (CC_FD_SLOTS as $k) $slots[] = [$k, cc_fd_w($k)];
    $u = function ($p) { return esc_url_raw(rest_url('cc/v1/' . $p)); };
    $tp = cc_ath_tp($pid); $vx = $tp ? [] : cc_fd_vx($pid); $kv = cc_fd_kgv($pid); $fem = cc_fd_female($pid, $vx);
    $cfg = ['page' => (int) $pid, 'date' => $date, 'fixed' => (isset($_GET['fd']) && !$go) ? 1 : 0, 'scroll' => $go ? 1 : 0, 'seen' => (object) cc_fd_seen($pid),'lang' => $GLOBALS['cc_ath_lang'] ?? 'en', 'nonce' => wp_create_nonce('wp_rest'), 'w' => $W, 'slots' => $slots,
            'day' => cc_fd_out($pid, $date), 'mine' => cc_fd_mine($pid), 'kg' => cc_fd_kg($pid) ?: '', 'credit' => "Food data: ANSES-CIQUAL · USDA FoodData Central · McCance and Widdowson's CoFID (© Crown copyright, OGL)",
            /* TrainingPeaks athletes: no Vekta weight, rides or trends (and never the word Vekta) */
            'vkg' => $kv['src'] === 'vekta' ? ['v' => $kv['kg'], 'd' => $kv['d']] : null, 'rides' => (object) ($tp ? [] : cc_fd_rides($vx)),
            'trends' => (!$tp && cc_fd_trends_on($pid)) ? cc_fd_trend_data($vx) : null, 'micro' => cc_fd_micro_url(), 'mw' => cc_fd_mw($fem), 'female' => $fem ? 1 : 0, 'cycle' => $fem ? cc_fd_cycle($pid) : null,
            'recent' => cc_fd_recent($pid), 'fav' => array_map(function ($it) use ($pid) { return cc_fd_fresh_item($it, cc_fd_own_idx(cc_fd_mine($pid))); }, cc_fd_fav($pid)), 'streak' => cc_fd_streak($pid), 'targets' => (object) ($tp ? [] : cc_fd_targets($vx)), 'today' => current_time('Y-m-d'),
            'foods' => esc_url_raw(add_query_arg('v', get_option('cc_food_db_v', '0'), rest_url('cc/v1/foods'))),
            'u' => ['day' => $u('food-day'), 'save' => $u('food-day'), 'photo' => $u('food-photo'), 'photodel' => $u('food-photo-del'), 'mine' => $u('food-mine'), 'kg' => $u('food-kg'), 'reply' => $u('food-reply'), 'fav' => $u('food-fav'), 'cycle' => $u('food-cycle'), 'seen' => $u('food-seen')]];
    $cfg = apply_filters('cc_fd_athlete_cfg', $cfg, (int) $pid, $date);   // nutrition-plus.php: Marine's day targets
    return '<section class="ath-s fd" id="food"><h2>' . cc_ath_icon('food', 'ath-hic') . esc_html(cc_fd_w('title')) . '</h2><p class="fd-lede">' . esc_html(cc_fd_w('lede')) . '</p>'
        . '<div class="fd-app" data-cfg="' . esc_attr(wp_json_encode($cfg)) . '"><div class="fd-day"></div><div class="fd-trbox"></div><div class="fd-cycbox"></div><div class="fd-minebox"></div><div class="fd-thbox"></div></div></section>' . cc_fd_css() . cc_fd_sjs() . (function_exists('cc_np_pjs') ? cc_np_pjs() : '') . cc_fd_js()
        . apply_filters('cc_fd_after_app', '', (int) $pid, $date);   // mealplan.php: Marine's planned meals in the diary

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
// header chip for package athletes (not Matteo, not athletes without the package): straight to today's diary
add_filter('cc_ath_live_chips_athlete', function ($html, $view) {
    if (!$view || cc_ath_is_coach() || !cc_fd_on($view)) return $html;
    return $html . '<a class="ath-chip ath-chip-go ath-chip-food" href="' . esc_url(add_query_arg('fd', 'today', cc_fd_hub())) . '#food">🍽 ' . esc_html(cc_fd_w('log_today')) . '</a>';
}, 10, 2);
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
    // Matteo 19 Nov: one comment box per day, always open (Marine could not find the folded "Reply" link); the reply shows at once, no reload
    $first = strtok(trim((string) get_the_title($pid)), ' ') ?: 'the athlete';
    return '<div class="fd-thl">' . $o . '</div><div class="fd-r" data-page="' . (int) $pid . '" data-date="' . esc_attr($date) . '" data-who="' . ($viewer === 'nutri' ? 'Marine' : 'Matteo') . '">'
        . '<textarea rows="2" aria-label="' . esc_attr('Comment to ' . $first . ' about this day') . '" placeholder="' . esc_attr('Write a comment to ' . $first . '…') . '"></textarea>'
        . '<div class="fd-row"><button type="button" class="btn btn-go fd-send">Send</button><span class="fd-msg" role="status"></span></div></div>';
}
/* the small carbs / protein / fat ring (share of kcal) at the top of a day in the review */
function cc_fd_ring($t) {
    $v = [$t['c'] * 4, $t['p'] * 4, $t['f'] * 9]; $tt = array_sum($v); if ($tt <= 0) return '';
    $L = 2 * M_PI * 42; $off = 0; $col = ['#7fb2ff', '#c99bff', '#f0b45a']; $nm = ['Carbs', 'Protein', 'Fat']; $g = [$t['c'], $t['p'], $t['f']];
    $s = '<div class="fd-ringw sm"><svg class="fd-ring" viewBox="0 0 110 110" width="76" height="76" aria-hidden="true"><circle cx="55" cy="55" r="42" fill="none" stroke="rgba(255,255,255,.08)" stroke-width="12"/>'; $leg = '';
    foreach ($v as $i => $x) {
        $len = $x / $tt * $L;
        $s .= '<circle cx="55" cy="55" r="42" fill="none" stroke="' . $col[$i] . '" stroke-width="12" stroke-dasharray="' . round($len, 1) . ' ' . round($L, 1) . '" stroke-dashoffset="' . round(-$off, 1) . '" transform="rotate(-90 55 55)"/>';
        $off += $len;
        $leg .= '<li><i style="background:' . $col[$i] . '"></i><span>' . $nm[$i] . '</span><b>' . round($x / $tt * 100) . ' % · ' . round($g[$i]) . ' g</b></li>';
    }
    return $s . '<text x="55" y="62" text-anchor="middle" font-size="26" font-weight="700" fill="#fff">' . number_format(round($t['k'])) . '</text></svg><ul class="fd-leg">' . $leg . '</ul></div>';
}
function cc_fd_rc_badge($st) { return in_array($st, ['r', 'c'], true) ? ' <span class="fd-rc fd-rc-' . $st . '">' . esc_html(cc_fd_w($st === 'r' ? 'b_raw' : 'b_cooked')) . '</span>' : ''; }
function cc_fd_day_html($pid, $date, $vx, $tp, $kg, $viewer, $mine = [], $fem = false, $cy = null) {
    $d = cc_fd_get($pid, $date); $t = cc_fd_daytot($d); $fl = cc_fd_fluids($d); $ml = $fl[0] + $fl[1]; $has = false; $ir = $fem ? cc_fd_iron($d, $mine) : null;
    $ts = strtotime($date . ' 12:00'); $next = gmdate('Y-m-d', $ts + DAY_IN_SECONDS);
    $ride = $tp ? 0 : (cc_fd_rides($vx)[$date] ?? 0); $tg = $tp ? [] : (cc_fd_targets($vx)[$date] ?? []);
    $o = '<article class="fd-rd" id="fd-' . esc_attr($date) . '"><h3>' . esc_html(date_i18n('l j F', $ts)) . ($date === current_time('Y-m-d') ? ' <small>today</small>' : '') . ($cy ? cc_fd_phase_chip($cy, $date) : '') . '%IRONTAG%</h3>';
    $sl = '';
    foreach (CC_FD_SLOTS as $k) {
        $s = $d['s'][$k] ?? null; if (!$s) continue;
        $has = true; $st = cc_fd_tot($s['i'] ?? []); $sfl = cc_fd_fluids(['s' => [$s]]); $sml = $sfl[0] + $sfl[1];
        $sl .= '<div class="fd-rs"><div class="fd-rsh"><b>' . esc_html(cc_fd_w($k)) . '</b>' . (!empty($s['t']) ? ' <span class="fd-time-b">' . esc_html($s['t']) . '</span>' : '')
             . (!empty($s['i']) ? '<span class="fd-rst">' . round($st['k']) . ' kcal · C ' . cc_fd_f1($st['c']) . ' · P ' . cc_fd_f1($st['p']) . ' · F ' . cc_fd_f1($st['f']) . '</span>' : '') . '</div>';
        $ex = [];
        if ($sml) $ex[] = 'Water ' . number_format($sfl[0]) . ' ml' . ($sfl[1] ? ' · other drinks ' . number_format($sfl[1]) . ' ml' : '');
        $rmin = $ride > 0 ? $ride : (int) ($s['r'] ?? 0);
        if ($k === 'bike' && !empty($s['i'])) $ex[] = 'Sodium: ' . number_format(round($st['na'])) . ' mg' . ($rmin > 0 ? ' · ≈ ' . number_format(round($st['na'] / ($rmin / 60))) . ' mg/h' : '');   // Marine 19 Nov: sodium only for training
        if ($k === 'bike' && $rmin > 0 && ($sml || $st['c'] > 0)) $ex[] = '<b>≈ ' . round($st['c'] / ($rmin / 60)) . ' g carbs/h</b>' . (!empty($tg['c']) ? ' (target ' . (int) $tg['c'] . ')' : '') . ' · <b>≈ ' . round($sml / ($rmin / 60)) . ' ml/h</b>' . (!empty($tg['ml']) ? ' (target ' . (int) $tg['ml'] . ')' : '') . ' · ride ' . esc_html(cc_fd_hm($rmin * 60)) . ($ride > 0 ? '' : ' (typed by the athlete)');
        if ($ex) $sl .= '<p class="fd-rex">' . implode(' · ', $ex) . '</p>';
        if (!empty($s['i'])) {
            $sl .= '<ul class="fd-ri">';
            foreach ($s['i'] as $it) { $m = ((float) $it['g']) / 100;
                $sl .= '<li><span>' . esc_html($it['n']) . cc_fd_rc_badge($it['st'] ?? '') . (!empty($it['m']) ? ' <span class="fd-tag">' . ($it['m'] === 'r' ? 'own recipe' : 'own food') . '</span>' : '') . '</span><small>' . cc_fd_amount($it) . ' · ' . round($it['k'] * $m) . ' kcal · C ' . cc_fd_f1($it['c'] * $m) . ' · P ' . cc_fd_f1($it['p'] * $m) . ' · F ' . cc_fd_f1($it['f'] * $m) . '</small></li>'; }
            $sl .= '</ul>';
        }
        if (!empty($s['n'])) $sl .= '<p class="fd-rn">“' . nl2br(esc_html($s['n'])) . '”</p>';
        if (!empty($s['ph']) && ($u = wp_get_attachment_url((int) $s['ph']))) $sl .= '<a class="fd-rph" href="' . esc_url($u) . '" target="_blank" rel="noopener"><img src="' . esc_url($u) . '" alt="Photo of ' . esc_attr(cc_fd_w($k)) . '" loading="lazy"></a>';
        $sl .= '</div>';
    }
    if ($has) {
        $o .= cc_fd_ring($t) . $sl . '<div class="fd-rtot"><b>Day total</b>' . (function_exists('cc_np_macro_spans') ? cc_np_macro_spans($t, $kg, cc_np_alc($d, $mine)) : '<span>' . round($t['k']) . ' kcal</span>')
            . '<span>Fibre ' . round($t['fi']) . ' g</span><span>Sugars ' . round($t['su']) . ' g</span>'
            . '<span>Water ' . number_format($fl[0]) . ' ml</span><span>Other drinks ' . number_format($fl[1]) . ' ml</span><span>Total fluids ' . number_format($ml) . ' ml (' . cc_fd_f1($ml / 1000) . ' L)</span></div>'
            . ($fem ? '<p class="fd-ironl">' . esc_html(sprintf(cc_fd_w('iron_line'), cc_fd_f1($ir['fe']))) . ($ir['inc'] ? ' <small class="fd-inc">incomplete</small>' : '') . '</p>' : '')
            . cc_fd_micro_box($d, $mine, $fem);
    } else $o .= '<p class="fd-muted">Nothing logged.</p>';
    $o = str_replace('%IRONTAG%', ($fem && $has && $ir['low']) ? ' <span class="fd-lowfe">Low iron</span>' : '', $o);
    if (!$tp && $vx) $o .= '<div class="fd-vx">' . cc_fd_training_html($vx, $date, 'Training this day') . cc_fd_training_html($vx, $next, 'Training next day')
        . cc_fd_notes_html($vx, $date, 'Your nutrition note this day') . cc_fd_notes_html($vx, $next, 'Your nutrition note next day') . '</div>';
    $o .= apply_filters('cc_fd_review_day_extra', '', (int) $pid, $date, $viewer);   // mealplan.php: planned vs eaten
    return $o . '<div class="fd-th">' . cc_fd_thread_html($pid, $date, $d['r'] ?? [], $viewer) . '</div></article>';
}
function cc_fd_week_ahead($vx, $pid = 0, $viewer = '') {
    $o = ''; $t0 = strtotime(current_time('Y-m-d') . ' 12:00');
    // Matteo 19 Nov: Marine can comment on the coming days too (one box per day; today has its own day below)
    for ($i = 0; $i < 7; $i++) {
        $d = gmdate('Y-m-d', $t0 + $i * DAY_IN_SECONDS); $p = cc_fd_vx_day($vx, $d, 'plan'); $n = cc_fd_vx_day($vx, $d, 'notes');
        $o .= '<div class="fd-wk"><b>' . esc_html(date_i18n('D j M', $t0 + $i * DAY_IN_SECONDS)) . '</b>'
            . ($p ? implode('', array_map(function ($x) { return '<span>' . cc_fd_plan_line($x) . '</span>'; }, $p)) : '<span class="fd-muted">Rest / nothing planned</span>')
            . ($n ? implode('', array_map(function ($x) { return '<details class="fd-wkn"><summary>🥗 ' . esc_html($x['t'] ?: 'Nutrition note') . '</summary>' . (!empty($x['c']) ? '<p>' . nl2br(esc_html($x['c'])) . '</p>' : '') . '</details>'; }, $n)) : '<span class="fd-warn-n">No nutrition note yet</span>')
            . ($pid && $i > 0 ? '<div class="fd-wkc">' . cc_fd_thread_html($pid, $d, cc_fd_get($pid, $d)['r'] ?? [], $viewer) . '</div>' : '')
            . '</div>';
    }
    return '<div class="fd-week"><h3>Week ahead</h3><div class="fd-wkg">' . $o . '</div></div>';
}
function cc_fd_review($pid, $viewer) {
    $GLOBALS['cc_ath_lang'] = 'en';
    $off = max(0, (int) ($_GET['fo'] ?? 0)); $tp = cc_ath_tp($pid); $vx = $tp ? [] : cc_fd_vx($pid); $kv = cc_fd_kgv($pid); $kg = $kv['kg']; $mine = cc_fd_mine($pid); $fem = cc_fd_female($pid, $vx); $cy = $fem ? cc_fd_cycle($pid) : null; if ($cy && empty($cy['on'])) $cy = null;
    $back = $viewer === 'nutri' ? cc_fd_hub() : add_query_arg('board', 'food', cc_fd_hub());
    $wtxt = $kv['src'] === 'vekta' ? ' · weight used for g/kg: <b>' . cc_fd_f1($kg) . ' kg</b> (from Vekta, ' . esc_html(date_i18n('j M', strtotime($kv['d'] . ' 12:00'))) . ')'
          : ($kv['src'] === 'athlete' ? ' · weight used for g/kg: <b>' . cc_fd_f1($kg) . ' kg</b> (entered by the athlete)' : ' · no weight' . ($tp ? ' entered by the athlete' : ' in Vekta (last 60 days) or entered by the athlete'));
    $o = '<section class="ath-s fd-rv"><p class="fd-back"><a href="' . esc_url($back) . '">← All food diaries</a></p>'
       . '<h2>' . (function_exists('cc_ph_face') ? cc_ph_face($pid, 36) . ' ' : '') . esc_html(get_the_title($pid)) . '</h2>'
       . '<p class="fd-lede">Food diary, newest day first' . $wtxt . '.'
       . (!$tp && !empty($vx['at']) ? ' Training and nutrition notes updated ' . esc_html(human_time_diff((int) $vx['at'])) . ' ago.' : '') . '</p>' . cc_fd_switch($pid);
    if ($fem) {   // iron below 14 mg on N of the last 7 logged days
        $n = 0; $k = 0; foreach (cc_fd_days($pid) as $dd) { $day = cc_fd_get($pid, $dd); if (empty($day['s'])) continue; $k++; $ir = cc_fd_iron($day, $mine); if ($ir['low']) $n++; if ($k >= 7) break; }
        if ($n >= 1) $o .= '<p class="fd-ironsum">Iron below 14 mg on <b>' . $n . '</b> of the last ' . $k . ' logged day' . ($k === 1 ? '' : 's') . ' (days with 3+ meals logged and enough iron data).</p>';
    }
    $o .= '<div class="fd-top">' . cc_fd_blood_box($pid, $viewer) . ($tp ? '' : cc_fd_trends_box($pid, $vx, $cy)) . '</div>';
    $o .= apply_filters('cc_fd_review_top', '', (int) $pid, $viewer);   // nutrition-plus.php: carbs per hour and energy charts, omega-3 week
    $o .= apply_filters('cc_fd_review_plan', '', (int) $pid, $viewer);   // mealplan.php: plan the coming days
    if (!$tp && $vx) $o .= cc_fd_week_ahead($vx, $pid, $viewer);
    $t0 = strtotime(current_time('Y-m-d') . ' 12:00') - $off * 14 * DAY_IN_SECONDS;
    for ($i = 0; $i < 14; $i++) $o .= cc_fd_day_html($pid, gmdate('Y-m-d', $t0 - $i * DAY_IN_SECONDS), $vx, $tp, $kg, $viewer, $mine, $fem, $cy);
    $o .= '<p class="fd-pager">' . ($off ? '<a class="btn btn-ghost" href="' . esc_url(add_query_arg('fo', $off - 1)) . '">Newer days</a> ' : '') . '<a class="btn btn-ghost" href="' . esc_url(add_query_arg('fo', $off + 1)) . '">Older days</a></p>';
    return $o . '</section>' . cc_fd_css() . cc_fd_rjs() . cc_fd_sjs() . (function_exists('cc_nt_css') ? cc_nt_css() : '') . (function_exists('cc_ph_assets') ? cc_ph_assets() : '')
        . (function_exists('cc_bt_assets') ? cc_bt_assets($viewer === 'nutri') : '');
}
/* blood tests next to the diary: Marine sees only the tests the athlete shared with her; Matteo sees all of them */
function cc_fd_blood_box($pid, $viewer) {
    if (!function_exists('cc_bt_get') || !function_exists('cc_bt_row')) return '';
    $rows = '';
    foreach (array_reverse(cc_bt_get($pid)) as $b) {
        if ($viewer === 'nutri') { if (!empty($b['share'])) $rows .= cc_bt_row($pid, $b, false, 'nutri'); }
        else $rows .= cc_bt_row($pid, $b, true);
    }
    return '<div class="fd-box fd-blood"><h3>Blood tests</h3>' . ($rows ?: '<p class="fd-muted">' . ($viewer === 'nutri' ? 'No blood tests shared yet.' : 'No blood tests uploaded yet.') . '</p>') . '</div>';
}
/* the 12-week trends (weight, HRV, resting HR) from Vekta, and the switch that shows them to the athlete */
function cc_fd_trends_box($pid, $vx, $cy = null) {
    $td = cc_fd_trend_data($vx); $on = cc_fd_trends_on($pid);
    if ($td && $cy) $td['cyc'] = ['p' => $cy['p'], 'L' => cc_fd_cyc_len($cy['p']), 'label' => 'Cycle (shaded: period days)'];
    return '<div class="fd-box fd-trw"><h3>Trends · last 12 weeks</h3>'
        . ($td ? '<div class="fd-trends" data-tr="' . esc_attr(wp_json_encode($td)) . '"></div><p class="fd-muted">Dashed line: the athlete’s own 28-day average (HRV and resting HR). Updated ' . esc_html(human_time_diff((int) ($vx['at'] ?? time()))) . ' ago.</p>'
               : '<p class="fd-muted">No data yet.</p>')
        . '<p class="fd-sw"><button type="button" class="fd-pkg fd-trsw' . ($on ? ' on' : '') . '" role="switch" aria-checked="' . ($on ? 'true' : 'false') . '" data-page="' . (int) $pid . '"><span class="fd-knob"></span></button>'
        . '<span>Show trends to the athlete: <b>' . ($on ? 'on' : 'off') . '</b></span></p></div>';
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
/* one stored JSON table (option + gzip copy), open data, cached by the browser for a year (the URL carries the version) */
function cc_fd_serve($opt) {
    $gz = (string) get_option($opt . '_gz', ''); $raw = $gz === '' ? (string) get_option($opt, '') : '';
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
}
add_action('rest_api_init', function () {
    $mine = function (WP_REST_Request $r) {   // the athlete's own page with the package on (Matteo may act on any page)
        if (cc_ath_is_coach()) return true;
        $p = cc_ath_page_of(get_current_user_id());
        return $p && (int) ($r->get_param('page') ?: $p) === $p && cc_fd_on($p);
    };
    $page = function (WP_REST_Request $r) { return cc_ath_is_coach() ? (int) $r->get_param('page') : cc_ath_page_of(get_current_user_id()); };
    // the food database: open data, the same for everyone, cached by the browser for a year (the URL carries the version)
    register_rest_route('cc/v1', '/foods', ['methods' => 'GET', 'permission_callback' => '__return_true', 'callback' => function () { return cc_fd_serve('cc_food_db'); }]);
    // micronutrients and electrolytes per food (a separate table, fetched only when someone opens the micronutrient line)
    register_rest_route('cc/v1', '/foods-micro', ['methods' => 'GET', 'permission_callback' => '__return_true', 'callback' => function () { return cc_fd_serve('cc_food_micro'); }]);
    register_rest_route('cc/v1', '/food-db', ['methods' => 'POST', 'permission_callback' => 'cc_ath_is_coach', 'callback' => function (WP_REST_Request $r) {
        $o = ['ok' => true];
        foreach (['data' => 'cc_food_db', 'micro' => 'cc_food_micro'] as $p => $opt) {
            $d = (string) $r->get_param($p); if ($d === '') continue; $j = json_decode($d, true);
            if (!is_array($j) || ($p === 'data' ? (empty($j['foods']) || !is_array($j['foods'])) : (empty($j['m']) || !is_array($j['m'])))) return new WP_Error('cc_bad', 'Not a food table: ' . $p, ['status' => 400]);
            if ($p === 'data') update_option('cc_food_db', $d, false);
            update_option($opt . '_gz', function_exists('gzencode') ? base64_encode(gzencode($d, 9)) : '', false);
            if ($p === 'micro' && !function_exists('gzencode')) update_option('cc_food_micro', $d, false);
            update_option($opt . '_v', substr(md5($d), 0, 10), false);
            $o[$p] = ['rows' => count($p === 'data' ? $j['foods'] : $j['m']), 'bytes' => strlen($d), 'v' => get_option($opt . '_v')];
        }
        return $o;
    }]);
    register_rest_route('cc/v1', '/food-trends', ['methods' => 'POST', 'permission_callback' => 'cc_fd_staff', 'callback' => function (WP_REST_Request $r) {
        $pid = (int) $r->get_param('page');
        if (!$pid || get_post_type($pid) !== 'cc_athlete' || (cc_fd_is_nutri() && !cc_fd_on($pid))) return new WP_Error('cc_no', 'Not allowed', ['status' => 403]);
        if ($r->get_param('on')) delete_post_meta($pid, 'cc_fd_trends_off'); else update_post_meta($pid, 'cc_fd_trends_off', 1);
        return ['ok' => true, 'on' => cc_fd_trends_on($pid)];
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
    // "My cycle": opt-in by the athlete herself (female athletes only); off deletes everything
    register_rest_route('cc/v1', '/food-cycle', ['methods' => 'POST', 'permission_callback' => $mine, 'callback' => function (WP_REST_Request $r) use ($page) {
        $pid = $page($r); if (!$pid || !cc_fd_female($pid)) return new WP_Error('cc_no', 'Not available', ['status' => 403]);
        $act = (string) $r->get_param('act'); $d = cc_fd_date($r->get_param('date')); $cy = cc_fd_cycle($pid);
        if ($act === 'off') { delete_post_meta($pid, 'cc_fd_cycle'); return ['ok' => true, 'cycle' => ['on' => 0, 'p' => []]]; }
        if ($act === 'on') $cy['on'] = 1;
        elseif (!$cy['on'] || !$d) return new WP_Error('cc_bad', 'Turn it on first', ['status' => 400]);
        elseif ($act === 'start') { $cy['p'] = array_values(array_filter($cy['p'], function ($x) use ($d) { return abs(strtotime($x[0]) - strtotime($d)) > 3 * DAY_IN_SECONDS; })); $cy['p'][] = [$d, null]; }
        elseif ($act === 'end') { $ix = -1; foreach ($cy['p'] as $i => $x) if ($x[0] <= $d) $ix = $i; if ($ix < 0 || strtotime($d) - strtotime($cy['p'][$ix][0]) > 14 * DAY_IN_SECONDS) return new WP_Error('cc_bad', 'No start before', ['status' => 400]); $cy['p'][$ix][1] = $d; }
        elseif ($act === 'unset') { $o2 = []; foreach ($cy['p'] as $x) { if ($x[0] === $d) continue; if (($x[1] ?? null) === $d) $x[1] = null; $o2[] = $x; } $cy['p'] = $o2; }
        usort($cy['p'], function ($x, $y) { return strcmp($x[0], $y[0]); }); $cy['p'] = array_slice($cy['p'], -60);
        update_post_meta($pid, 'cc_fd_cycle', wp_slash(wp_json_encode(['on' => 1, 'p' => $cy['p']])));
        return ['ok' => true, 'cycle' => cc_fd_cycle($pid)];
    }]);
    // the athlete saw the messages under a day (thread scrolled into view): hides "New message from Marine" for that day
    register_rest_route('cc/v1', '/food-seen', ['methods' => 'POST', 'permission_callback' => $mine, 'callback' => function (WP_REST_Request $r) use ($page) {
        $pid = $page($r); $d = cc_fd_date($r->get_param('date')); if (!$pid || !$d) return new WP_Error('cc_bad', 'Date needed', ['status' => 400]);
        $s = cc_fd_seen($pid); $s[$d] = time(); ksort($s); $s = array_slice($s, -120, null, true);
        update_post_meta($pid, 'cc_fd_seen', wp_slash(wp_json_encode($s)));
        return ['ok' => true, 'at' => $s[$d]];
    }]);
    // favourite foods (starred on a diary line): the athlete's own list, up to 40
    register_rest_route('cc/v1', '/food-fav', ['methods' => 'POST', 'permission_callback' => $mine, 'callback' => function (WP_REST_Request $r) use ($page) {
        $pid = $page($r); $in = json_decode((string) $r->get_param('data'), true); if (!$pid || !is_array($in)) return new WP_Error('cc_bad', 'Data needed', ['status' => 400]);
        $out = []; foreach (array_slice($in, 0, 40) as $m) { $c = cc_fd_item($m); if ($c) $out[] = $c; }
        update_post_meta($pid, 'cc_food_fav', wp_slash(wp_json_encode($out)));
        return ['ok' => true, 'fav' => $out];
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
            foreach (array_slice((array) ($a['notes'] ?? []), 0, 80) as $x) if ($dd = $d($x['date'] ?? '')) $o['notes'][] = ['d' => $dd, 't' => cc_fd_txt($x['title'] ?? '', 200), 'c' => mb_substr(trim(sanitize_textarea_field((string) ($x['content'] ?? ''))), 0, 4000), 'tg' => function_exists('cc_np_clean_ntg') ? cc_np_clean_ntg($x['tg'] ?? null) : null];
            // latest body weight (last 60 days) and 84 days of weight / overnight HRV / resting HR for the trends
            $o['sex'] = ['female' => 'f', 'male' => 'm'][strtolower((string) ($a['gender'] ?? ''))] ?? '';   // for the iron screening and the cycle tracker
            $w = (array) ($a['weight'] ?? []); $wv = (float) ($w['value'] ?? 0);
            if ($wv >= 25 && $wv <= 250 && ($wd = $d($w['date'] ?? ''))) $o['kg'] = ['v' => round($wv, 1), 'd' => $wd];
            $o['tr'] = [];
            foreach (array_slice((array) ($a['days'] ?? []), 0, 100) as $x) {
                if (!($dd = $d($x['date'] ?? ''))) continue;
                $kg = (float) ($x['weight'] ?? 0); $hv = (float) ($x['hrv'] ?? 0); $hr = (float) ($x['rhr'] ?? 0);
                $row = [$dd, ($kg >= 25 && $kg <= 250) ? round($kg, 1) : null, ($hv > 0 && $hv < 400) ? round($hv) : null, ($hr > 20 && $hr < 150) ? round($hr) : null];
                if ($row[1] || $row[2] || $row[3]) $o['tr'][] = $row;
            }
            // 12 weeks of sessions for Marine's charts (carbs per hour and energy vs duration and intensity)
            $o['acts'] = [];
            foreach (array_slice((array) ($a['acts'] ?? []), 0, 400) as $x) if ($dd = $d($x['date'] ?? '')) $o['acts'][] = ['d' => $dd, 'sp' => cc_fd_txt($x['sport'] ?? '', 40), 'n' => cc_fd_txt($x['name'] ?? '', 120), 's' => (int) ($x['dur'] ?? 0),
                'i' => is_numeric($x['intensity'] ?? null) ? round((float) $x['intensity'], 3) : null, 'kc' => is_numeric($x['calories'] ?? null) ? (int) round((float) $x['calories']) : null, 'kj' => (int) round((float) ($x['kj'] ?? 0))];
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
        foreach (['cc_food_mine', 'cc_food_kg', 'cc_food_vx', 'cc_fd_trends_off', 'cc_food_fav', 'cc_fd_cycle', 'cc_fd_seen', 'cc_np_tg'] as $k) delete_post_meta($pid, $k);
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
        /* 19 Nov 2026: drinks, sodium, raw/cooked, micronutrients, trends */
        . 'html .cc .fd-drk{display:flex;flex-wrap:wrap;align-items:center;gap:6px 10px;font-size:15px;color:#d0d6e0;font-weight:600}html .cc .fd .fd-drk input{width:110px}html .cc .fd-drk .fd-hint{flex-basis:100%}'
        . 'html .cc .fd-sx{margin:0;font-size:15px;color:#d0d6e0}html .cc .fd-sx b{color:#fff}html .cc .fd-inc{color:#b8bec8;font-size:14px;font-weight:500;font-style:normal}'
        . 'html .cc .fd-rc{display:inline-block;margin-left:6px;padding:1px 7px;border-radius:6px;border:1px solid rgba(255,255,255,.28);color:#e6e9ee;font-size:14px;font-weight:700;letter-spacing:.03em;white-space:nowrap;vertical-align:1px}'
        . 'html .cc .fd-rc-c{background:rgba(255,255,255,.1)}html .cc .fd-rc-r{background:transparent;border-style:dashed}'
        . 'html .cc .fd-ask{display:grid;gap:10px}html .cc .fd-ask b{color:#fff;font-size:16px}html .cc .fd-ask p{margin:0;color:#fff;font-size:16px;font-weight:600}'
        . 'html .cc .fd-wh{margin:0;color:#b8bec8;font-size:14px}'
        . 'html .cc .fd-vkg{margin:14px 0 4px;color:#e6e9ee;font-size:16px;font-weight:600}'
        . 'html .cc .fd-micro{margin:10px 0 0;border-radius:12px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.02)}html .cc .fd-micro>summary{cursor:pointer;padding:10px 12px;color:#d0d6e0;font-size:15px;font-weight:600}'
        . 'html .cc .fd-mt{padding:0 12px 12px}html .cc .fd-mtab{width:100%;border-collapse:collapse;border:0;margin:0;font-size:15px;color:#e6e9ee;background:none}html .cc .fd-mtab tr,html .cc .fd-mtab th,html .cc .fd-mtab td{border:0;background:none}html .cc .fd-mtab th{text-align:left;color:#b8bec8;font-size:14px;font-weight:700;padding:10px 0 4px;letter-spacing:.02em}html .cc .fd-mtab th+th{text-align:right}'
        . 'html .cc .fd-mtab td{padding:5px 0;border-top:1px solid rgba(255,255,255,.07)}html .cc .fd-mtab td+td{text-align:right;white-space:nowrap;padding-left:10px}html .cc .fd-mtab small{color:#b8bec8;font-size:14px}'
        . 'html .cc .fd-top{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:12px;margin:8px 0 18px}html .cc .fd-box{padding:12px 14px;border-radius:14px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.03);min-width:0}'
        . 'html .cc .fd-box h3{margin:0 0 6px;font-size:18px}html .cc .ath .fd-box h3{font-size:20px!important}html .cc .fd-box .fd-sw{margin:10px 0 0;font-size:15px}'
        . 'html .cc .fd-trends{display:grid;gap:12px}html .cc .fd-tc h4{margin:0 0 2px;font:700 15px var(--body);color:#e6e9ee;letter-spacing:.01em}html .cc .fd-tc svg{display:block;width:100%;height:auto;touch-action:pan-y}'
        . 'html .cc .fd-tc .fd-muted{margin:2px 0 6px}html .cc .fd-trd{margin:14px 0 0;border:1px solid rgba(255,255,255,.1);border-radius:14px;background:rgba(255,255,255,.03)}html .cc .fd-trd>summary{padding:12px 16px;cursor:pointer;color:#d0d6e0;font-weight:600;font-size:16px}html .cc .fd-trd>div{padding:0 16px 14px}'
        . 'html .cc .fd-rex{margin:4px 0 0;font-size:15px;color:#d0d6e0}html .cc .fd-rex b{color:#fff}html .cc .ath .fd-tc h4,html .cc .fd-tc h4{text-transform:none}'
        . 'html .cc .fd-status.ok{color:#2bd47a;font-weight:600;transition:opacity .6s}html .cc .fd-status.ok.fade{opacity:0}'
        /* 19 Nov 2026: open -> log. Sticky date bar + one slim summary line; day summary, folded sections and messages after the meals */
        . 'html .cc .fd-stick{position:sticky;top:70px;z-index:6;background:rgba(10,12,14,.94);backdrop-filter:blur(6px);margin:4px -6px 8px;padding:6px 6px 8px;border-radius:12px}html .cc .fd-stick .fd-nav{margin:0 0 4px}'
        . 'html .cc .fd-slim{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:4px 10px;margin:0;font-size:15px;color:#d0d6e0;text-align:center}html .cc .fd-sm{color:#e6e9ee;font-weight:600;white-space:nowrap}'
        . 'html .cc .fd-sk{color:#f3e2c4;font-weight:700;white-space:nowrap}html .cc .fd-slim .fd-cchip{vertical-align:0}html .cc .fd-newm{padding:2px 4px;font-size:15px;text-decoration:none;color:#2bd47a;white-space:nowrap}html .cc .fd-newm:hover{text-decoration:underline}'
        . 'html .cc .fd-tot .fd-ringw{margin:0 0 12px;background:rgba(0,0,0,.2)}html .cc .fd-tot .fd-copyday{display:block;margin:12px 0 0;padding:4px 0}html .cc .fd-thbox .fd-thread{margin:22px 0 0}'
        . 'html .cc .fd .fd-x,html .cc .fd .fd-star{flex:none;box-sizing:border-box;width:40px;height:40px;min-width:40px;min-height:40px;display:grid;place-items:center;padding:0;line-height:1;font-size:20px;border-radius:10px;border:1px solid rgba(255,255,255,.15);background:none;cursor:pointer}'
        . 'html .cc .fd-r{margin-top:10px}html .cc .fd-r textarea{min-height:64px}html .cc .fd-r .fd-row .btn{margin:0}html .cc .fd-wkc{margin-top:8px;display:grid;gap:4px}html .cc .fd-wkc .nt-rep{margin-left:0}html .cc .fd-wkc .fd-r{margin-top:4px}html .cc .fd-wkc textarea{font-size:16px}'
        . 'html .cc .fd-nw{white-space:nowrap}html .cc .fd .fd-x{color:#d0d6e0}html .cc .fd .fd-x svg,html .cc .fd .fd-star svg{display:block;pointer-events:none}'
        . 'html .cc .fd-streak{margin:0;font-size:16px;font-weight:600;color:#e6e9ee}'
        . 'html .cc .fd-ringw{display:flex;align-items:center;gap:16px;padding:10px 12px;border-radius:14px;border:1px solid rgba(255,255,255,.1);background:rgba(255,255,255,.03)}html .cc .fd-ring{flex:none;width:110px;height:110px}'
        . 'html .cc .fd-ring circle{transition:stroke-dasharray .5s ease,stroke-dashoffset .5s ease}html .cc .fd-leg{list-style:none;margin:0;padding:0;display:grid;gap:6px;min-width:0;flex:1}'
        . 'html .cc .fd-leg li{display:flex;flex-wrap:wrap;align-items:center;gap:4px 8px;font-size:15px;color:#d0d6e0}html .cc .fd-leg i{flex:none;width:12px;height:12px;border-radius:50%}html .cc .fd-leg b{margin-left:auto;color:#fff;font-weight:600;white-space:nowrap}'
        . 'html .cc .fd-ringw.sm{padding:6px 10px;gap:12px;margin:0 0 8px}html .cc .fd-ringw.sm .fd-ring{width:76px;height:76px}html .cc .fd-ringw.sm .fd-leg li{font-size:14px}'
        . 'html .cc .fd-gg{display:grid;gap:10px}html .cc .fd-gg:empty{display:none}html .cc .fd-gauge{display:grid;gap:5px}html .cc .fd-gh{display:flex;justify-content:space-between;gap:10px;font-size:15px;color:#d0d6e0}html .cc .fd-gh b{color:#fff}'
        . 'html .cc .fd-gbar{position:relative;height:12px;border-radius:999px;background:rgba(255,255,255,.08);overflow:visible}html .cc .fd-gbar i{position:absolute;left:0;top:0;bottom:0;border-radius:999px;background:#8a9099;transition:width .5s ease}html .cc .fd-gbar i.ok{background:#12a150}'
        . 'html .cc .fd-gbar u{position:absolute;top:-4px;bottom:-4px;width:2px;margin-left:-1px;background:#e6e9ee;border-radius:2px}html .cc .fd-gauge small{color:#b8bec8;font-size:14px}'
        . 'html .cc .fd-chipbox{display:grid;gap:6px}html .cc .fd-chipbox[hidden]{display:none}html .cc .fd-chl{margin:2px 0 0;color:#b8bec8;font-size:14px;font-weight:700}html .cc .fd-chips{display:flex;flex-wrap:wrap;gap:6px}'
        . 'html .cc .fd-chip{max-width:100%;padding:7px 12px;border-radius:999px;border:1px solid rgba(255,255,255,.18);background:rgba(255,255,255,.05);color:#fff;font:500 15px var(--body);cursor:pointer;text-align:left;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}html .cc .fd-chip:hover{border-color:rgba(43,212,122,.6)}'
        . 'html .cc .fd-star{flex:none;width:36px;height:36px;border-radius:10px;border:1px solid rgba(255,255,255,.15);background:none;color:#b8bec8;font-size:19px;line-height:1;cursor:pointer;padding:0}html .cc .fd-star.on{color:#f0c75a;border-color:rgba(240,199,90,.45)}'
        . 'html .cc .fd-items li.fd-new{animation:fdIn .35s ease-out}html .cc .fd-items li.fd-out{transition:opacity .2s,transform .2s;opacity:0;transform:translateX(12px)}@keyframes fdIn{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}'
        . 'html .cc .fd-addh{color:#2bd47a;font-weight:600}html .cc .fd .fd-slot .fd-row .btn{margin:0}'
        . '@media (max-width:420px){html .cc .fd-items li{flex-wrap:wrap}html .cc .fd-in{flex-basis:100%}}'
        . 'html .cc .fd-ironl{margin:10px 0 0;font-size:15px;color:#e6e9ee;font-weight:600}html .cc .fd-ironnote{margin:10px 0 0;padding:10px 12px;border-radius:12px;border:1px solid rgba(240,180,90,.35);background:rgba(240,180,90,.08);color:#f3e2c4;font-size:15px;line-height:1.5}'
        . 'html .cc .fd-lowfe{display:inline-block;margin-left:8px;padding:1px 8px;border-radius:999px;border:1px solid rgba(240,180,90,.45);background:rgba(240,180,90,.1);color:#f3e2c4;font:600 14px var(--body);letter-spacing:0;vertical-align:3px;text-transform:none}'
        . 'html .cc .fd-ironsum{margin:0 0 12px;padding:8px 12px;border-radius:12px;border:1px solid rgba(240,180,90,.3);background:rgba(240,180,90,.06);color:#f3e2c4;font-size:15px}'
        . 'html .cc .fd-cchip{display:inline-block;padding:2px 10px;border-radius:999px;border:1px solid rgba(201,155,255,.4);background:rgba(201,155,255,.1);color:#eadcff;font:600 14px var(--body);letter-spacing:0;text-transform:none;vertical-align:3px;white-space:nowrap}'
        . 'html .cc .fd-rd h3 .fd-cchip{margin-left:8px}html .cc .fd-cyc{margin:14px 0 0;border:1px solid rgba(255,255,255,.1);border-radius:14px;background:rgba(255,255,255,.03)}html .cc .fd-cyc>summary{padding:12px 16px;cursor:pointer;color:#d0d6e0;font-weight:600;font-size:16px}'
        . 'html .cc .fd-cyc>div{padding:0 16px 14px;display:grid;gap:10px}html .cc .fd-cyc .btn{width:auto;margin:0;justify-self:start}html .cc .fd-cyc p{margin:0;color:#d0d6e0;font-size:15px}html .cc .fd-cyc small{color:#b8bec8;font-size:14px}'
        . 'html .cc .fd-cycs svg{display:block;width:100%;height:auto}'
        /* 19 Nov 2026: portions, voice logging, day targets, fluids */
        . 'html .cc .fd select{font:16px var(--body);min-height:44px;padding:8px 34px 8px 12px;border-radius:10px;border:1px solid rgba(255,255,255,.2);background:#0b0d0f url("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 width=%2712%27 height=%278%27%3E%3Cpath d=%27M1 1l5 5 5-5%27 stroke=%27%23d0d6e0%27 stroke-width=%272%27 fill=%27none%27/%3E%3C/svg%3E") no-repeat right 12px center;color:#fff;-webkit-appearance:none;appearance:none;max-width:100%;box-sizing:border-box}'
        . 'html .cc .fd-amt{display:flex;flex-wrap:wrap;align-items:center;gap:8px 10px}html .cc .fd .fd-amt input{width:96px;min-height:44px}html .cc .fd-amt label{display:flex;align-items:center;gap:8px;color:#d0d6e0;font-size:15px;font-weight:600}'
        . 'html .cc .fd-ul select{min-width:0;max-width:230px}html .cc .fd-pgv{color:#c9f3da;font-size:15px;font-weight:600}html .cc .fd-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}'
        . 'html .cc .fd-mic{white-space:nowrap}html .cc .fd-voice{display:grid;gap:10px;padding:12px;border-radius:12px;border:1px solid rgba(43,212,122,.35);background:rgba(18,161,80,.06);min-width:0}'
        . 'html .cc .fd-vtl{display:grid;gap:6px;color:#d0d6e0;font-size:15px;font-weight:600}html .cc .fd .fd-vtl textarea{width:100%;min-height:64px}'
        . 'html .cc .fd-vmsg{margin:0;color:#e6e9ee;font-size:16px;line-height:1.45;display:flex;gap:10px;align-items:flex-start}html .cc .fd-dot{flex:none;width:12px;height:12px;margin-top:6px;border-radius:50%;background:#2bd47a;animation:fdpulse 1s ease-in-out infinite}'
        . '@keyframes fdpulse{50%{opacity:.25;transform:scale(.7)}}'
        . 'html .cc .fd-vh{margin:4px 0 0;font-size:18px;color:#fff}html .cc .fd-vl{list-style:none;margin:0;padding:0;display:grid;gap:10px}'
        . 'html .cc .fd-vl li{display:grid;gap:8px;padding:10px;border-radius:12px;background:rgba(0,0,0,.25);min-width:0}html .cc .fd-vrow{display:flex;gap:8px;align-items:center;min-width:0}'
        . 'html .cc .fd-vfl{flex:1;min-width:0}html .cc .fd-vfl select{width:100%}html .cc .fd-vnf{display:flex!important;grid-template-columns:none;align-items:center;justify-content:space-between;gap:10px;color:#e6e9ee;font-size:15px}'
        . 'html .cc .fd-tgbox:empty{display:none}html .cc .fd-tgt{margin:2px 0 12px;padding:14px 14px 12px;border-radius:12px;background:rgba(18,161,80,.07);border:1px solid rgba(43,212,122,.25)}'
        . 'html .cc .fd-tge{margin:0;color:#d0d6e0;font-size:15px;text-align:center}html .cc .fd-tgk{margin:0 0 10px;color:#e6e9ee;font-size:18px;text-align:center;line-height:1.2}html .cc .fd-tgk b{color:#fff;font-size:34px;font-weight:800;letter-spacing:-.5px}html .cc .fd-tgk span{color:#e6e9ee;font-weight:600}'
        . 'html .cc .fd-tgk.ok b{color:#2bd47a;font-size:24px}html .cc .fd-tggo{margin:8px 0 0;text-align:center;color:#c9f3da;font-size:16px;font-weight:600}html .cc .fd .fd-tgb.big{height:16px}'
        . 'html .cc .fd-tgb{height:8px;border-radius:99px;background:rgba(255,255,255,.08);overflow:hidden}html .cc .fd-tgb i{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,#12a150,#2bd47a)}'
        . 'html .cc .fd-tgm{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px 12px;margin-top:10px}html .cc .fd-tgm div{display:grid;gap:4px;min-width:0}'
        . 'html .cc .fd-tgm span{color:#b8bec8;font-size:14px}html .cc .fd-tgm small{color:#d0d6e0;font-size:14px;white-space:nowrap}html .cc .fd-tgm .fd-tgb{height:6px}'
        . 'html .cc .fd-fl{margin-top:8px}html .cc .fd-stg{margin:0 0 10px;padding:8px 10px;border-radius:10px;background:rgba(18,161,80,.08);border:1px solid rgba(43,212,122,.2);color:#e6e9ee;font-size:15px;line-height:1.5}html .cc .fd-stg b{color:#c9f3da}'
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
var msg=r.querySelector(".fd-msg");if(msg){msg.className="fd-msg";msg.textContent="Sending…";}
post("%REPLY%",{page:r.dataset.page,date:r.dataset.date,text:t.value}).then(function(){var th=r.parentNode.querySelector(".fd-thl"),d=document.createElement("div"),now=new Date();
d.className="nt-rep fd-just";d.innerHTML='<span class="nt-rh"><b></b> <small></small></span><p></p>';d.querySelector("b").textContent=r.dataset.who||"";d.querySelector("small").textContent=now.toLocaleString(undefined,{day:"numeric",month:"short",hour:"2-digit",minute:"2-digit"});
d.querySelector("p").textContent=t.value;if(th){th.appendChild(d);}t.value="";s.disabled=false;if(msg){msg.className="fd-msg";msg.textContent="✓ Sent";}}).catch(function(e){s.disabled=false;if(msg){msg.className="fd-msg err";msg.textContent="Not sent"+(e&&e.message?" ("+e.message+")":"")+". Please try again.";}else{alert("Not sent. Please try again.");}});return;}
var ts=e.target.closest(".fd-trsw");
if(ts){var on2=!ts.classList.contains("on");ts.disabled=true;
post("%TRENDS%",{page:ts.dataset.page,on:on2?1:0}).then(function(){location.reload();}).catch(function(){ts.disabled=false;alert("Not changed. Please try again.");});return;}
var p=e.target.closest(".fd-pkg");
if(p){var on=!p.classList.contains("on");if(!on&&!confirm("Turn the Nutrition package off for this athlete? Their diary stays saved, but they and Marine will no longer see it.")){return;}p.disabled=true;
post("%PKG%",{page:p.dataset.page,on:on?1:0}).then(function(){location.reload();}).catch(function(){p.disabled=false;alert("Not changed. Please try again.");});return;}
var a=e.target.closest(".fd-addgo");
if(a){var box=a.closest(".fd-addf"),m=box.querySelector(".fd-msg"),em=box.querySelector(".fd-addmail").value.trim();if(!em){return;}a.disabled=true;
post("%PKG%",{email:em,on:1}).then(function(j){m.className="fd-msg";m.textContent=j.name+" now has the Nutrition package.";setTimeout(function(){location.reload();},900);}).catch(function(){a.disabled=false;m.className="fd-msg err";m.textContent="No athlete found with that email.";});}
});
})();
JS;
    return '<script>' . str_replace(["\r", "\n", '%NONCE%', '%REPLY%', '%PKG%', '%TRENDS%'], ['', '', $n, esc_url_raw(rest_url('cc/v1/food-reply')), esc_url_raw(rest_url('cc/v1/food-pkg')), esc_url_raw(rest_url('cc/v1/food-trends'))], $js) . '</script>';
}
/* shared by the diary and the review pages: the micronutrient table (lazy) and the 12-week trend charts (inline SVG) */
function cc_fd_sjs() {
    static $done = false; if ($done) return ''; $done = true;
    $js = <<<'JS'
(function(){
if(window.ccFdMicro){return;}
function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return {"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c];});}
var MP=null;
function loadM(u){if(!MP){MP=fetch(u,{credentials:"omit"}).then(function(r){if(!r.ok){throw r;}return r.json();}).catch(function(e){MP=null;throw e;});}return MP;}
function per100(M,id,mine,depth){var row=M.m[id];if(row){return M.cols.map(function(c,j){return row[j]==null?null:row[j];});}
var r=mine&&mine[id];if(!r||depth>2){return null;}var w=+r.cw||0,sum=0;(r.ing||[]).forEach(function(i){sum+=+i[1]||0;});if(!(w>0)){w=sum;}if(!(w>0)){return null;}
var out=M.cols.map(function(){return 0;});(r.ing||[]).forEach(function(i){var g=+i[1]||0;if(!(g>0)){return;}var v=per100(M,i[0],mine,depth+1);out.forEach(function(x,j){if(x===null){return;}if(!v||v[j]==null){out[j]=null;}else{out[j]=x+v[j]*g/100;}});});
return out.map(function(x){return x===null?null:x*100/w;});}
function fm(v){v=+v||0;return v>=100?Math.round(v).toLocaleString():(v>=10?(Math.round(v*10)/10).toLocaleString():(Math.round(v*100)/100).toLocaleString());}
function micro(el){var W=JSON.parse(el.dataset.w),items=JSON.parse(el.dataset.items||"[]"),mine=JSON.parse(el.dataset.mine||"{}"),na=JSON.parse(el.dataset.na||"{}"),box=el.querySelector(".fd-mt");
if(!box.innerHTML){box.innerHTML='<p class="fd-muted">'+esc(W.loading)+'</p>';}
loadM(el.dataset.url).then(function(M){var tot=M.cols.map(function(){return 0;}),miss=M.cols.map(function(){return 0;}),any=M.cols.map(function(){return 0;});
items.forEach(function(it){var g=+it[1]||0;if(!(g>0)){return;}var v=per100(M,it[0],mine,0);M.cols.forEach(function(c,j){if(!v||v[j]==null){miss[j]++;}else{tot[j]+=v[j]*g/100;any[j]++;}});});
function row(name,val,unit,ri,inc){return '<tr><td>'+esc(name)+(inc?' <small>· '+esc(W.incomplete)+'</small>':'')+'</td><td>'+val+(unit?' '+esc(unit):'')+'</td><td>'+(ri==null?'<small>–</small>':esc(ri)+' %')+'</td></tr>';}
function nut(c){var j=M.cols.indexOf(c);if(j<0){return "";}if(!any[j]){return row(W["m_"+c],'–',"",null,false);}
if(c==="fe"&&W.fe14){return row(W.m_fe,esc(W.fe14.replace(/^[^:]*:\s*/,"").replace("%s",fm(tot[j]))),"",Math.round(tot[j]*100/M.ri[j]),miss[j]>0);}
return row(W["m_"+c],fm(tot[j]),M.units[j],Math.round(tot[j]*100/M.ri[j]),miss[j]>0);}
var h='<table class="fd-mtab"><tr><th>'+esc(W.electro)+'</th><th></th><th>'+esc(W.ri)+'</th></tr>'+row(W.sodium,fm(na.v||0),"mg",null,(na.inc||0)>0)+["k","mg","ca","cl"].map(nut).join("");
h+='<tr><th>'+esc(W.microh)+'</th><th></th><th></th></tr>'+["fe","zn","vc","vd","b12","fol","va","ve","io"].map(nut).join("")+row(W.fibre,fm(na.fi||0),"g",null,false)+'</table>';
h+='<p class="fd-muted">'+esc(W.ri_note)+(miss.some(function(x){return x>0;})||(na.inc||0)>0?' '+esc(W.inc_h):'')+'</p>';box.innerHTML=h;}).catch(function(){box.innerHTML="";el.open=false;});}
window.ccFdMicro=micro;window.ccFdM={load:loadM,per100:per100};
function dn(s){return Math.round(Date.parse(s+"T12:00:00Z")/864e5);}
function dl(s,lang){return new Date(s+"T12:00:00").toLocaleDateString(lang||undefined,{day:"numeric",month:"short"});}
function draw(c){var o=JSON.parse(c.dataset.tc),w=Math.max(240,Math.round(c.clientWidth||300)),h=160,pl=8,pr=58,pt=30,pb=28,P=o.p;
var vs=P.map(function(p){return p[1];});if(o.avg!=null){vs.push(o.avg);}var dmn=Math.min.apply(0,P.map(function(p){return p[1];})),dmx=Math.max.apply(0,P.map(function(p){return p[1];}));
var mn=Math.min.apply(0,vs),mx=Math.max.apply(0,vs),pad=Math.max((mx-mn)*0.18,o.pad);mn-=pad;mx+=pad;
function X(d){return pl+(d-o.x0)/((o.x1-o.x0)||1)*(w-pl-pr);}function Y(v){return pt+(mx-v)/(mx-mn)*(h-pt-pb);}
var q=P.map(function(p){return [X(p[0]),Y(p[1])];}),d="M"+q[0][0].toFixed(1)+" "+q[0][1].toFixed(1);
for(var i=0;i<q.length-1;i++){var p0=q[i-1]||q[i],p1=q[i],p2=q[i+1],p3=q[i+2]||p2;d+=" C"+(p1[0]+(p2[0]-p0[0])/6).toFixed(1)+" "+(p1[1]+(p2[1]-p0[1])/6).toFixed(1)+" "+(p2[0]-(p3[0]-p1[0])/6).toFixed(1)+" "+(p2[1]-(p3[1]-p1[1])/6).toFixed(1)+" "+p2[0].toFixed(1)+" "+p2[1].toFixed(1);}
var last=q[q.length-1],lp=P[P.length-1],gid="fdg"+Math.random().toString(36).slice(2);
var s='<svg viewBox="0 0 '+w+' '+h+'" width="'+w+'" height="'+h+'" role="img" aria-label="'+esc(o.label)+'"><defs><linearGradient id="'+gid+'" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e6e9ee" stop-opacity=".16"/><stop offset="1" stop-color="#e6e9ee" stop-opacity="0"/></linearGradient></defs>';
s+='<line x1="'+pl+'" x2="'+(w-pr)+'" y1="'+(h-pb)+'" y2="'+(h-pb)+'" stroke="rgba(255,255,255,.12)"/>';
s+='<path d="'+d+' L'+last[0].toFixed(1)+' '+(h-pb)+' L'+q[0][0].toFixed(1)+' '+(h-pb)+' Z" fill="url(#'+gid+')"/>';
if(o.avg!=null){var ya=Y(o.avg).toFixed(1);s+='<line x1="'+pl+'" x2="'+(w-pr)+'" y1="'+ya+'" y2="'+ya+'" stroke="#b8bec8" stroke-width="1.5" stroke-dasharray="5 5"/><text x="'+(w-pr+6)+'" y="'+(+ya+5)+'" font-size="14" fill="#b8bec8">'+esc(fm2(o.avg,o.dec))+'</text>';}
s+='<path d="'+d+'" fill="none" stroke="#e6e9ee" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"/>';
s+='<circle cx="'+last[0].toFixed(1)+'" cy="'+last[1].toFixed(1)+'" r="4" fill="#fff"/><text x="'+(last[0]+8).toFixed(1)+'" y="'+(o.avg!=null&&Math.abs(Y(o.avg)-last[1])<16?(last[1]+(last[1]<Y(o.avg)?-6:20)):(last[1]+5)).toFixed(1)+'" font-size="15" font-weight="700" fill="#fff">'+esc(fm2(lp[1],o.dec))+'</text>';
s+='<text x="'+pl+'" y="'+(h-6)+'" font-size="14" fill="#b8bec8">'+esc(dl(o.from,o.lang))+'</text><text x="'+(w-pr)+'" y="'+(h-6)+'" font-size="14" fill="#b8bec8" text-anchor="end">'+esc(dl(o.to,o.lang))+'</text>';
s+='<text x="'+pl+'" y="16" font-size="14" fill="#b8bec8">'+esc(fm2(dmn,o.dec)+" – "+fm2(dmx,o.dec))+'</text>';
s+='<g class="fd-tip" style="display:none"><line y1="'+pt+'" y2="'+(h-pb)+'" stroke="rgba(255,255,255,.35)"/><circle r="4.5" fill="#fff"/><text y="16" font-size="14" font-weight="700" fill="#fff"></text></g><rect x="0" y="0" width="'+w+'" height="'+h+'" fill="transparent"/></svg>';
c.innerHTML=s;var svg=c.querySelector("svg"),tip=svg.querySelector(".fd-tip");
function show(ev){var r=svg.getBoundingClientRect(),mx2=(ev.clientX-r.left)*w/r.width,b=0;q.forEach(function(p,ix){if(Math.abs(p[0]-mx2)<Math.abs(q[b][0]-mx2)){b=ix;}});
tip.style.display="";var ln=tip.querySelector("line"),ci=tip.querySelector("circle"),tx=tip.querySelector("text");ln.setAttribute("x1",q[b][0]);ln.setAttribute("x2",q[b][0]);ci.setAttribute("cx",q[b][0]);ci.setAttribute("cy",q[b][1]);
tx.textContent=dl(P[b][2],o.lang)+" · "+fm2(P[b][1],o.dec)+" "+o.unit;var right=q[b][0]>w/2;tx.setAttribute("x",right?q[b][0]-6:q[b][0]+6);tx.setAttribute("text-anchor",right?"end":"start");}
svg.style.touchAction="pan-y";svg.style.cursor="crosshair";
svg.addEventListener("pointermove",show);svg.addEventListener("pointerdown",show);svg.addEventListener("pointerleave",function(ev){if(ev.pointerType==="mouse"){tip.style.display="none";}});
svg.addEventListener("touchmove",function(ev){var t=ev.touches[0];if(t){show({clientX:t.clientX});}},{passive:true});svg.addEventListener("touchstart",function(ev){var t=ev.touches[0];if(t){show({clientX:t.clientX});}},{passive:true});}
function fm2(v,dec){return (+v).toLocaleString(undefined,{minimumFractionDigits:dec,maximumFractionDigits:dec});}
function trends(el){if(el.dataset.done){return;}var T=JSON.parse(el.dataset.tr),W=T.w,x0=dn(T.from),x1=dn(T.to),h="";
[[1,W.tr_w,"kg",1,false,0.5],[2,W.tr_hrv,"ms",0,true,3],[3,W.tr_rhr,"bpm",0,true,2]].forEach(function(sr){var P=[];T.days.forEach(function(r){var v=r[sr[0]];if(v!=null&&+v>0){P.push([dn(r[0]),+v,r[0]]);}});
P.sort(function(a,b){return a[0]-b[0];});
if(P.length<3){h+='<div class="fd-tc"><h4>'+esc(sr[1])+'</h4><p class="fd-muted">'+esc(W.nodata)+'</p></div>';return;}
var avg=null;if(sr[4]){var r28=P.filter(function(p){return p[0]>x1-28;});if(r28.length>=3){avg=r28.reduce(function(a,p){return a+p[1];},0)/r28.length;}}
var o={p:P,x0:x0,x1:x1,from:T.from,to:T.to,lang:W.lang,unit:sr[2],dec:sr[3],avg:avg,pad:sr[5],label:sr[1]};
h+='<div class="fd-tc"><h4>'+esc(sr[1])+'</h4>'+(avg!=null?'<p class="fd-muted">- - '+esc(W.tr_avg)+': '+esc(fm2(avg,sr[3]))+' '+esc(sr[2])+'</p>':'')+'<div class="fd-tcv" data-tc="'+esc(JSON.stringify(o))+'"></div></div>';});
if(T.cyc&&T.cyc.p&&T.cyc.p.length){h+='<div class="fd-tc"><h4>'+esc(T.cyc.label||"")+'</h4><div class="fd-cycs" data-cy="'+esc(JSON.stringify({p:T.cyc.p,x0:x0,x1:x1,from:T.from,to:T.to,lang:W.lang}))+'"></div></div>';}
el.innerHTML=h;el.dataset.done=1;el.querySelectorAll(".fd-tcv").forEach(draw);el.querySelectorAll(".fd-cycs").forEach(cstrip);}
function cstrip(c){var o=JSON.parse(c.dataset.cy),w=Math.max(240,Math.round(c.clientWidth||300)),h=46,pl=8,pr=58,s='<svg viewBox="0 0 '+w+' '+h+'" width="'+w+'" height="'+h+'" aria-hidden="true"><rect x="'+pl+'" y="6" width="'+(w-pl-pr)+'" height="16" rx="4" fill="rgba(255,255,255,.05)"/>';
function X(d){return pl+(d-o.x0)/((o.x1-o.x0)||1)*(w-pl-pr);}o.p.forEach(function(p){var a=dn(p[0]),b=p[1]?dn(p[1]):a+4;if(b<o.x0||a>o.x1){return;}a=Math.max(a,o.x0);b=Math.min(b,o.x1);s+='<rect x="'+X(a).toFixed(1)+'" y="6" width="'+Math.max(3,X(b+1)-X(a)).toFixed(1)+'" height="16" rx="3" fill="#c99bff" fill-opacity=".55"/>';});
s+='<text x="'+pl+'" y="42" font-size="14" fill="#b8bec8">'+esc(dl(o.from,o.lang))+'</text><text x="'+(w-pr)+'" y="42" font-size="14" fill="#b8bec8" text-anchor="end">'+esc(dl(o.to,o.lang))+'</text></svg>';c.innerHTML=s;}
window.ccFdTrends=trends;
function visible(){document.querySelectorAll(".fd-trends[data-tr]").forEach(function(el){if(el.offsetParent!==null){trends(el);}});}
document.addEventListener("toggle",function(e){var t=e.target;if(!t.classList||!t.open){return;}if(t.classList.contains("fd-micro")){micro(t);}if(t.classList.contains("fd-trd")){visible();}},true);
var rt=null;addEventListener("resize",function(){clearTimeout(rt);rt=setTimeout(function(){document.querySelectorAll(".fd-tcv").forEach(function(c){if(c.offsetParent!==null){draw(c);}});document.querySelectorAll(".fd-cycs").forEach(function(c){if(c.offsetParent!==null){cstrip(c);}});},200);});
if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",visible);}else{visible();}
})();
JS;
    return '<script>' . str_replace(["\r", "\n"], ['', ' '], $js) . '</script>';
}
/* the athlete's diary (all drawn in the browser from data-cfg; every change is saved through the REST routes) */
function cc_fd_js() {
    static $done = false; if ($done) return ''; $done = true;
    $js = <<<'JS'
(function(){
var root=document.querySelector(".fd-app");if(!root){return;}
var C=JSON.parse(root.getAttribute("data-cfg")),W=C.w;
var OPEN=(function(){try{return JSON.parse(localStorage.getItem("ccFdOpen")||"{}")||{};}catch(x){return {};}})();
function keepOpen(k,v){OPEN[k]=v?1:0;try{localStorage.setItem("ccFdOpen",JSON.stringify(OPEN));}catch(x){}}
var S={date:C.date,day:C.day,mine:C.mine||[],kg:C.kg||"",open:{},srch:null,edit:null,timer:null,dirty:false,mineOpen:!!OPEN.mine,microOpen:!!OPEN.micro,cycOpen:!!OPEN.cyc,res:[],fav:C.fav||[],recent:C.recent||[],just:null,cyc:C.cycle||null,M:null,seen:C.seen||{}};
var XI='<svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true" focusable="false"><path d="M2.5 2.5l9 9M11.5 2.5l-9 9" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>';
function starI(on){return '<svg width="18" height="18" viewBox="0 0 16 16" aria-hidden="true" focusable="false"><path d="M8 1.4l1.98 4.1 4.52.6-3.3 3.13.83 4.47L8 11.55 3.97 13.7l.83-4.47L1.5 6.1l4.52-.6z" fill="'+(on?"currentColor":"none")+'" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/></svg>';}
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
var stT=null;function status(t,bad){var el=root.querySelector(".fd-status");if(el){var ok=t===W.saved;el.textContent=ok?"✓ "+t:(t||"");el.className="fd-status"+(bad?" err":"")+(ok?" ok":"");clearTimeout(stT);if(ok){stT=setTimeout(function(){el.classList.add("fade");},1600);}}}
function slot(k){if(!S.day.s||Array.isArray(S.day.s)){S.day.s={};}var s=S.day.s[k];if(!s){s=S.day.s[k]={t:"",n:"",i:[]};}if(!s.i){s.i=[];}return s;}
var F=["k","c","p","f","fi","su"];
function tot(items){var t={k:0,c:0,p:0,f:0,fi:0,su:0,na:0,nam:0};(items||[]).forEach(function(it){var m=(+it.g||0)/100;F.forEach(function(x){t[x]+=(+it[x]||0)*m;});if(m>0){if(it.na==null||it.na===""){t.nam++;}else{t.na+=(+it.na)*m;}}});return t;}
function dayTot(){var a=[];C.slots.forEach(function(s){a=a.concat(slot(s[0]).i);});return tot(a);}
function dayMl(){var f=dayFl();return f[0]+f[1];}
function macro(it){var m=(+it.g||0)/100;return fmt0(it.k*m)+" kcal · "+W.c_ab+" "+fmt(it.c*m)+" · "+W.p_ab+" "+fmt(it.p*m)+" · "+W.f_ab+" "+fmt(it.f*m);}
function kgUsed(){return C.vkg?+C.vkg.v:(parseFloat(String(S.kg).replace(",","."))||0);}
function sxTxt(k,s,t){var a=[],rm=rideMin(s);if(k==="bike"&&s.i.length){a.push(W.sodium+": "+fmt0(t.na)+" mg"+(rm>0?" · ≈ "+fmt0(t.na/(rm/60))+" mg/h":""));}
return a.map(function(x){return x.charAt(0)==="<"?x:esc(x);}).join(" · ");}
function hm(m){m=Math.round(+m||0);return m>0?Math.floor(m/60)+":"+String(m%60).padStart(2,"0"):"";}
function pmin(v){v=String(v||"").trim().replace(",",".");if(!v){return 0;}var m=v.match(/^(\d{1,2})[:h.](\d{1,2})$/);if(m&&v.indexOf(".")<0){return (+m[1])*60+(+m[2]);}var x=parseFloat(v);return x>0?(x<=24?Math.round(x*60):Math.round(x)):0;}
function rideMin(s){var r=C.rides&&C.rides[S.date];return r>0?r:(+s.r||0);}
function gauge(label,val,unit,tg){var max=Math.max(tg?tg*1.3:0,val*1.1,unit==="ml"?800:100),pct=Math.min(100,val/max*100),ok=tg&&val>=tg;
return '<div class="fd-gauge"><div class="fd-gh"><span>'+esc(label)+'</span><b>'+fmt0(val)+' '+unit+'/h</b></div><div class="fd-gbar"><i class="'+(ok?"ok":"")+'" style="width:'+pct.toFixed(1)+'%"></i>'+(tg?'<u style="left:'+(tg/max*100).toFixed(1)+'%"></u>':"")+'</div>'+(tg?'<small>'+esc(W.target.replace("%s",tg+" "+unit+"/h"))+(ok?" ✓":"")+'</small>':"")+'</div>';}
function gaugesHtml(k,s,t){if(k!=="bike"){return "";}var rm=rideMin(s);if(!(rm>0)||(!s.i.length&&!(+s.d>0))){return "";}var h=rm/60,tg=(C.targets&&C.targets[S.date])||{};
return gauge(W.g_h,t.c/h,"g",tg.c||0)+gauge(W.ml_h,(slotFl(s)[0]+slotFl(s)[1])/h,"ml",tg.ml||0);}
function isFav(id){return S.fav.some(function(f){return f.id===id;});}
function ringParts(t){var kc=t.c*4,kp=t.p*4,kf=t.f*9,tt=kc+kp+kf,L=2*Math.PI*42,off=0;return [kc,kp,kf].map(function(v){var len=tt?v/tt*L:0,o={len:len,off:off,pct:tt?Math.round(v/tt*100):0};off+=len;return o;});}
function ringHtml(t){var P=ringParts(t),L=2*Math.PI*42,col=["#7fb2ff","#c99bff","#f0b45a"],g=[t.c,t.p,t.f],nm=[W.carbs,W.protein,W.fat];
var h='<div class="fd-ringw"><svg class="fd-ring" viewBox="0 0 110 110" width="110" height="110" aria-hidden="true"><circle cx="55" cy="55" r="42" fill="none" stroke="rgba(255,255,255,.08)" stroke-width="12"/>';
P.forEach(function(p,i){h+='<circle data-rg="'+i+'" cx="55" cy="55" r="42" fill="none" stroke="'+col[i]+'" stroke-width="12" stroke-dasharray="'+p.len.toFixed(1)+' '+L.toFixed(1)+'" stroke-dashoffset="'+(-p.off).toFixed(1)+'" transform="rotate(-90 55 55)"/>';});
h+='<text data-rk x="55" y="58" text-anchor="middle" font-size="22" font-weight="700" fill="#fff">'+fmt0(t.k)+'</text><text x="55" y="76" text-anchor="middle" font-size="14" fill="#b8bec8">kcal</text></svg><ul class="fd-leg">';
P.forEach(function(p,i){h+='<li><i style="background:'+col[i]+'"></i><span>'+esc(nm[i])+'</span><b data-rl="'+i+'">'+fmt0(g[i])+' g</b></li>';});return h+'</ul></div>';}
function ringUpd(){var w=root.querySelector(".fd-ringw");if(!w){return;}var t=dayTot(),P=ringParts(t),L=2*Math.PI*42,g=[t.c,t.p,t.f];
P.forEach(function(p,i){var c=w.querySelector('[data-rg="'+i+'"]');if(c){c.setAttribute("stroke-dasharray",p.len.toFixed(1)+" "+L.toFixed(1));c.setAttribute("stroke-dashoffset",(-p.off).toFixed(1));}var l=w.querySelector('[data-rl="'+i+'"]');if(l){l.textContent=fmt0(g[i])+" g";}});
var k=w.querySelector("[data-rk]");if(k){k.textContent=fmt0(t.k);}}
function ironDay(){if(!C.female||!S.M){return null;}var j=S.M.cols.indexOf("fe"),rc=recipes(),fe=0,g=0,miss=0,sl=0;
C.slots.forEach(function(sv){var s=slot(sv[0]);if(s.i.length){sl++;}s.i.forEach(function(it){var gr=+it.g||0;if(!(gr>0)){return;}g+=gr;var v=window.ccFdM.per100(S.M,it.id,rc,0);if(!v||v[j]==null){miss+=gr;}else{fe+=v[j]*gr/100;}});});
var inc=g>0&&miss/g>0.3;return {fe:fe,inc:inc,low:!inc&&sl>=3&&fe<14};}
function ironHtml(){var r=ironDay();if(!r||!hasAny()){return "";}var v=fmt(r.fe);
return '<p class="fd-ironl">'+esc(W.iron_line.replace("%s",v))+(r.inc?' <small class="fd-inc">('+esc(W.incomplete)+')</small>':'')+'</p>'+(r.low?'<p class="fd-ironnote">'+esc(W.iron_note.replace("%s",v))+'</p>':'');}
function cycLen(p){var g=[];for(var i=1;i<p.length;i++){var d=dn2(p[i][0])-dn2(p[i-1][0]);if(d>=18&&d<=45){g.push(d);}}return g.length>=2?Math.round(g.reduce(function(a,b){return a+b;},0)/g.length):28;}
function cycN(p){var n=0;for(var i=1;i<p.length;i++){var d=dn2(p[i][0])-dn2(p[i-1][0]);if(d>=18&&d<=45){n++;}}return n;}
function dn2(s){return Math.round(Date.parse(s+"T12:00:00Z")/864e5);}
function phase(ds){var cy=S.cyc;if(!cy||!cy.on||!cy.p.length){return null;}var L=cycLen(cy.p),last=null;cy.p.forEach(function(x){if(x[0]<=ds){last=x;}});if(!last){return null;}
var day=dn2(ds)-dn2(last[0])+1;if(day>L+10){return null;}var pl=last[1]?dn2(last[1])-dn2(last[0])+1:5,ov=L-14;return {day:day,ph:day<=pl?"m":(Math.abs(day-ov)<=1?"o":(day<ov?"f":"l"))};}
function cycChip(){var p=phase(S.date);return p?'<span class="fd-cchip">'+esc(W.cyc_day.replace("%d",p.day)+" · "+W["ph_"+p.ph])+'</span>':"";}
function cycHtml(){if(!C.female){return "";}var cy=S.cyc||{on:0,p:[]},h='<details class="fd-cyc"'+(S.cycOpen?" open":"")+'><summary>'+esc(W.cyc_title)+'</summary><div><p>'+esc(W.cyc_consent)+'</p>';
if(!cy.on){return h+'<button type="button" class="btn btn-ghost" data-act="cyc" data-v="on">'+esc(W.cyc_on)+'</button></div></details>';}
var isS=cy.p.some(function(x){return x[0]===S.date;}),isE=cy.p.some(function(x){return x[1]===S.date;}),L=cycLen(cy.p);
h+='<div class="fd-row">'+(isS||isE?'<button type="button" class="btn btn-ghost" data-act="cyc" data-v="unset">'+esc(W.cyc_unset)+'</button>':'<button type="button" class="btn btn-ghost" data-act="cyc" data-v="start">'+esc(W.cyc_start)+'</button><button type="button" class="btn btn-ghost" data-act="cyc" data-v="end">'+esc(W.cyc_end)+'</button>')+'</div>';
h+='<p><small>'+esc(cycN(cy.p)>=2?W.cyc_len.replace("%d",L):W.cyc_def)+'</small></p>';
if(cy.p.length){h+='<p><small>'+esc(W.cyc_starts)+': '+esc(cy.p.slice(-6).map(function(x){return new Date(x[0]+"T12:00:00").toLocaleDateString(C.lang,{day:"numeric",month:"short"});}).join(", "))+'</small></p>';}
return h+'<button type="button" class="fd-link" data-act="cyc" data-v="off" style="justify-self:start">'+esc(W.cyc_off)+'</button></div></details>';}
function renderCyc(){var b=root.querySelector(".fd-cycbox");if(b){b.innerHTML=cycHtml();}}
function hasAny(){return C.slots.some(function(sv){return slot(sv[0]).i.length>0;});}
function streakHtml(){if(S.date!==C.today){return "";}var n=(+C.streak||0)+(hasAny()?1:0);return n>=2?'<span class="fd-sk" title="'+esc(W.streak.replace("%d",n))+'" aria-label="'+esc(W.streak.replace("%d",n))+'">🔥 '+n+'</span>':"";}
function newMsg(){var r=S.day.r||[],seen=+(S.seen[S.date]||0),who="";r.forEach(function(x){if(x.from==="athlete"&&+x.at>seen){seen=+x.at;}});r.forEach(function(x){if(x.from!=="athlete"&&+x.at>seen){who=x.from==="nutri"?"Marine":"Matteo";}});return who;}
function slimHtml(){var t=dayTot(),nm=newMsg();
return '<span class="fd-sm">'+esc([fmt0(t.k)+" kcal",W.c_ab+" "+fmt0(t.c)+" g",W.p_ab+" "+fmt0(t.p)+" g",W.f_ab+" "+fmt0(t.f)+" g"].join(" · "))+'</span>'+streakHtml()+cycChip()+(nm?'<button type="button" class="fd-link fd-newm" data-act="tothread">💬 '+esc(W.new_msg.replace("%s",nm))+'</button>':"");}
function slimUpd(){var el=root.querySelector(".fd-slim");if(el){el.innerHTML=slimHtml();}}
function markSeen(){if(!newMsg()){return;}var mx=0;(S.day.r||[]).forEach(function(x){mx=Math.max(mx,+x.at||0);});S.seen[S.date]=mx;slimUpd();send(C.u.seen,{page:C.page,date:S.date}).catch(function(){});}
var IO=null;function watchThread(){if(IO){IO.disconnect();IO=null;}var th=root.querySelector(".fd-thread");if(!th||!newMsg()||!window.IntersectionObserver){return;}
IO=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){markSeen();if(IO){IO.disconnect();IO=null;}}});},{threshold:0.3});IO.observe(th);}
function chipsHtml(){var h="";function row(lbl,src,arr){if(!arr.length){return "";}return '<p class="fd-chl">'+esc(lbl)+'</p><div class="fd-chips">'+arr.map(function(f,i){return '<button type="button" class="fd-chip" data-act="chip" data-src="'+src+'" data-i="'+i+'">'+(src==="fav"?"★ ":"")+esc(f.n)+'</button>';}).join("")+'</div>';}
h+=row(W.favs,"fav",S.fav)+row(W.recent,"recent",S.recent);return h?'<div class="fd-chipbox">'+h+'</div>':"";}
function macro100(f){return fmt0(f.k)+" kcal · "+W.c_ab+" "+fmt(f.c)+" · "+W.p_ab+" "+fmt(f.p)+" · "+W.f_ab+" "+fmt(f.f)+" / 100 g";}
function macroT(t){return fmt0(t.k)+" kcal · "+W.carbs+" "+fmt(t.c)+" g · "+W.protein+" "+fmt(t.p)+" g · "+W.fat+" "+fmt(t.f)+" g";}
function tag(m){return m?' <span class="fd-tag">'+esc(m==="r"?W.myrecipe:W.myfood)+'</span>':"";}
function loadDB(){if(DBP){return DBP;}DBP=fetch(C.foods,{credentials:"omit"}).then(function(r){if(!r.ok){throw r;}return r.json();}).then(function(d){
DB=d.foods.map(function(r){return {id:r[0],n:r[2],fr:r[3]||"",k:r[4],c:r[5],p:r[6],f:r[7],fi:r[8]==null?0:r[8],su:r[9]==null?0:r[9],na:r[10]==null?null:r[10],st:r[11]||"",fm:r[12]==null?null:r[12],po:r[13]||null,q:norm(r[2]+" | "+(r[3]||"")),qn:norm(r[2])};});FAM=d.families||null;
BYID={};DB.forEach(function(f){BYID[f.id]=f;});STAP=(d.staples||[]).map(function(s){return {re:new RegExp(s.rx),raw:s.raw,cooked:s.cooked};});return DB;}).catch(function(){DBP=null;DB=null;});return DBP;}
var BYID={},STAP=[];
function staple(f){if(!f||f.mine||(f.st!=="r"&&f.st!=="c")){return null;}for(var i=0;i<STAP.length;i++){if(STAP[i].re.test(f.qn)){return STAP[i];}}return null;}
function rcb(st){return st==="r"||st==="c"?' <span class="fd-rc fd-rc-'+st+'">'+esc(st==="r"?W.b_raw:W.b_cooked)+'</span>':"";}
function mineFoods(){return S.mine.map(function(m){return {id:m.id,n:m.n,fr:"",k:m.k,c:m.c,p:m.p,f:m.f,fi:m.fi||0,su:m.su||0,na:m.na==null?null:m.na,st:"",q:norm(m.n),qn:norm(m.n),mine:m.t};});}
var ALIAS={rasher:"bacon",rashers:"bacon",crisps:"potato chips",crisp:"potato chips",porridge:"oats",courgette:"zucchini",courgettes:"zucchini",aubergine:"eggplant",aubergines:"eggplant",biscuit:"cookie",biscuits:"cookies",chips:"french fries",coriander:"cilantro",rocket:"arugula",prawn:"shrimp",prawns:"shrimp",sweets:"candy",treacle:"molasses",swede:"rutabaga",cornflour:"cornstarch",yoghurt:"yogurt",isotonic:"sports drink",krispies:"rice crisp",nutella:"hazelnut spread",preserve:"jam",conserve:"jam",brack:"barmbrack"};
function scoreOf(f,ws){for(var j=0;j<ws.length;j++){if(f.q.indexOf(ws[j])<0){return -1;}}var whole=ws.join(" ");
return f.qn.indexOf(whole)===0?0:(f.qn.indexOf(ws[0])===0?1:(ws.every(function(w){return new RegExp("(^|[^a-z0-9])"+w.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")).test(f.qn);})?2:3));}
function search(q){var ws=norm(q).split(/[\s,]+/).filter(Boolean);if(!ws.length){return [];}var out=[];
var wa=[];ws.forEach(function(w){wa=wa.concat((ALIAS[w]||w).split(" "));});var alt=wa.join(" ")!==ws.join(" ");
var pool=mineFoods().concat(DB||[]);
for(var i=0;i<pool.length;i++){var f=pool[i],sc=scoreOf(f,ws);
if(sc<0&&alt){sc=scoreOf(f,wa);if(sc>-1){sc+=4;}}if(sc<0){continue;}
if(f.mine){sc-=2;}out.push([sc,f.n.length,f]);}
S.near=false;
if(!out.length&&ws.length>1){var any=[];ws.concat(wa).forEach(function(w){if(w.length>2&&any.indexOf(w)<0){any.push(w);}});
for(var i2=0;i2<pool.length;i2++){var f2=pool[i2],n2=0,st=1;for(var j2=0;j2<any.length;j2++){if(f2.q.indexOf(any[j2])>-1){n2++;if(f2.qn.indexOf(any[j2])===0){st=0;}}}
if(n2>0){out.push([-n2*10+st-(f2.mine?2:0),f2.n.length,f2]);}}
S.near=out.length>0;}
out.sort(function(a,b){return a[0]-b[0]||a[1]-b[1];});return out.slice(0,40).map(function(x){return x[2];});}
function resultsHtml(){if(!DB&&!S.mine.length){return '<p class="fd-muted">'+esc(W.loading)+'</p>';}if(!S.srch.q.trim()){return DB?"":'<p class="fd-muted">'+esc(W.loading)+'</p>';}
S.res=search(S.srch.q);if(!S.res.length){return DB?'<p class="fd-muted">'+esc(W.noresults)+'</p>':'<p class="fd-muted">'+esc(W.loading)+'</p>';}
var ws=norm(S.srch.q).split(/[\s,]+/).filter(Boolean);
return (S.near?'<p class="fd-muted">'+esc(W.closest)+'</p>':'')+'<ul class="fd-rl">'+S.res.map(function(f,ix){var viaFr=f.fr&&!ws.every(function(w){return f.qn.indexOf(w)>-1;});
return '<li><button type="button" data-act="pick" data-rx="'+ix+'"><span>'+esc(f.n)+rcb(f.st)+tag(f.mine)+'</span>'+(viaFr?'<i>'+esc(f.fr)+'</i>':'')+'<small>'+esc(macro100(f))+'</small></button></li>';}).join("")+'</ul>';}
function searchHtml(){var s=S.srch;
if(s.ask){var af=s.ask.f;return '<div class="fd-search"><div class="fd-ask"><b>'+esc(af.n)+rcb(af.st)+'</b><p>'+esc(W.ask_rc)+'</p><div class="fd-row"><button type="button" class="btn btn-go" data-act="rc" data-v="r">'+esc(W.w_raw)+'</button><button type="button" class="btn btn-go" data-act="rc" data-v="c">'+esc(W.w_cooked)+'</button><button type="button" class="fd-link" data-act="unpick">'+esc(W.cancel)+'</button></div></div></div>';}
if(s.pick){return pickHtml();}
return '<div class="fd-search"><p class="fd-wh">'+esc(W.weigh_h)+'</p><input type="search" class="fd-q" placeholder="'+esc(W.search)+'" value="'+esc(s.q)+'" autocomplete="off" enterkeyhint="search">'+(s.q.trim()?"":chipsHtml())+'<div class="fd-res">'+resultsHtml()+'</div><p class="fd-credit">'+esc(C.credit)+'</p><button type="button" class="fd-link" data-act="cancel" style="justify-self:start">'+esc(W.cancel)+'</button></div>';}
function slotHtml(k,label){var s=slot(k),t=tot(s.i),open=S.open[k]!==undefined?S.open[k]:(s.i.length>0||!!s.n||!!s.phu||+s.d>0||!!(window.ccMpHas&&window.ccMpHas(S.date,k)));
var h='<details class="fd-slot" data-slot="'+k+'"'+(open?" open":"")+'><summary><span class="fd-sl">'+esc(label)+'</span><span class="fd-st" data-tt="'+k+'">'+sumTxt(s,t)+'</span></summary><div class="fd-sb">'+stgHtml(k)+(window.ccMpSlot?window.ccMpSlot(S.date,k):"");
if(k==="bike"){var rv=C.rides&&C.rides[S.date];h+=rv>0?'<p class="fd-hint">'+esc(W.ride_rec.replace("%s",hm(rv).replace(":","h")))+'</p>':'<label class="fd-drk">'+esc(W.ride_t)+' <input type="text" inputmode="decimal" data-f="r" placeholder="2:30" value="'+esc(hm(s.r))+'" maxlength="5"></label>';}
h+='<label class="fd-time">'+esc(W.time)+' <input type="time" data-f="t" value="'+esc(s.t||"")+'"></label>';
if(s.i.length){h+='<ul class="fd-items">'+s.i.map(function(it,ix){return '<li'+(S.just===k+":"+ix?' class="fd-new"':'')+'><div class="fd-in"><b>'+esc(it.n)+rcb(it.st)+tag(it.m)+(window.ccMpTag?window.ccMpTag(it):"")+'</b><small data-it="'+ix+'">'+esc(itemSub(it))+'</small></div><label class="fd-g"><input type="number" inputmode="decimal" min="0" max="5000" step="1" data-f="g" data-ix="'+ix+'" value="'+esc(it.g)+'" aria-label="'+esc(W.grams)+'"> g</label><button type="button" class="fd-star'+(isFav(it.id)?' on':'')+'" data-act="star" data-ix="'+ix+'" aria-label="'+esc(isFav(it.id)?W.star_rm:W.star_add)+'" title="'+esc(isFav(it.id)?W.star_rm:W.star_add)+'">'+starI(isFav(it.id))+'</button><button type="button" class="fd-x" data-act="rm" data-ix="'+ix+'" aria-label="'+esc(W.remove)+'">'+XI+'</button></li>';}).join("")+'</ul>';
h+='<p class="fd-stot" data-stot="'+k+'">'+esc(W.slot_total+": "+macroT(t))+'</p>';}
h+='<p class="fd-sx" data-sx="'+k+'">'+sxTxt(k,s,t)+'</p><div class="fd-gg" data-gg="'+k+'">'+gaugesHtml(k,s,t)+'</div>';
h+=(S.srch&&S.srch.ctx==="slot"&&S.srch.slot===k)?searchHtml():((S.voice&&S.voice.slot===k)?voiceHtml():'<div class="fd-row"><button type="button" class="btn btn-go" data-act="add">'+esc(W.add)+'</button><button type="button" class="btn btn-ghost fd-mic" data-act="voice">🎙 '+esc(W.v_btn)+'</button><button type="button" class="fd-link" data-act="copyslot">'+esc(W.copy_y)+'</button></div>');
h+='<label class="fd-drk">'+esc(W.water)+' <input type="number" inputmode="numeric" min="0" max="10000" step="50" data-f="d" value="'+esc(s.d||"")+'"><span class="fd-hint">'+esc(W.water_h)+'</span></label>';
h+='<label class="fd-note">'+esc(W.note)+'<textarea rows="2" data-f="n" placeholder="'+esc(W.note_ph)+'">'+esc(s.n||"")+'</textarea></label>';
h+='<div class="fd-ph">'+(s.phu?'<a href="'+esc(s.phu)+'" target="_blank" rel="noopener"><img src="'+esc(s.phu)+'" alt=""></a>':"")+'<label class="btn btn-ghost fd-phb">'+esc(s.phu?W.photo_ch:W.photo)+'<input type="file" accept="image/*" hidden data-f="ph"></label>'+(s.phu?'<button type="button" class="fd-link" data-act="phdel">'+esc(W.photo_del)+'</button>':"")+'</div>';
return h+'</div></details>';}
function sumTxt(s,t){var a=[];if(s.t){a.push(s.t);}if(s.i.length){a.push(fmt0(t.k)+" kcal");}var fl=slotFl(s);if(fl[0]+fl[1]>0){a.push(fmt0(fl[0]+fl[1])+" ml");}if(!a.length&&!s.n&&!s.phu){return '<span class="fd-addh">'+esc(W.add_short)+'</span>';}return esc(a.join(" · "));}
function totV(){var t=dayTot(),ml=dayMl();
function tile(v,l,x,cl){return '<div><b>'+v+'</b><span>'+esc(l)+'</span>'+(x?'<em'+(cl?' class="fd-inc"':"")+'>'+x+'</em>':"")+'</div>';}
return '<div class="fd-tiles">'+tile(fmt0(t.k),"kcal")+tile(fmt0(t.c)+" g",W.carbs)+tile(fmt0(t.p)+" g",W.protein)+tile(fmt0(t.f)+" g",W.fat)+tile(fmt0(t.fi)+" g",W.fibre)+tile(fmt0(t.su)+" g",W.sugars)
+'</div><div class="fd-tiles fd-fl">'+tile(fmt0(dayFl()[0])+" ml",W.w_tile)+tile(fmt0(dayFl()[1])+" ml",W.od_tile)+tile(fmt0(ml)+" ml",W.tf_tile,ml?(Math.round(ml/100)/10).toLocaleString(C.lang,{minimumFractionDigits:1,maximumFractionDigits:1})+" L":"")+'</div>'+ironHtml();}
function microItems(){var a=[];C.slots.forEach(function(sv){slot(sv[0]).i.forEach(function(it){a.push([it.id,+it.g||0,it.m||""]);});});return a;}
function recipes(){var o={};S.mine.forEach(function(m){if(m.t==="r"){o[m.id]={ing:(m.ing||[]).map(function(i){return [i.id,+i.g||0,i.m||""];}),cw:+m.cw||0};}});return o;}
function microSet(el){var t=dayTot();el.setAttribute("data-items",JSON.stringify(microItems()));el.setAttribute("data-mine",JSON.stringify(recipes()));el.setAttribute("data-na",JSON.stringify({v:Math.round(t.na),inc:t.nam,fi:Math.round(t.fi*10)/10}));}
function microHtml(){if(!microItems().length){return "";}return '<details class="fd-micro"'+(S.microOpen?" open":"")+' data-url="'+esc(C.micro)+'" data-w="'+esc(JSON.stringify(C.mw))+'"><summary>'+esc(W.micro)+'</summary><div class="fd-mt"></div></details>';}
function microRefresh(){var el=root.querySelector(".fd-micro");if(!el){return;}microSet(el);if(el.open&&window.ccFdMicro){window.ccFdMicro(el);}}
function threadHtml(){var r=S.day.r||[];
var h=r.map(function(x){var who=x.from==="athlete"?W.you:(x.from==="nutri"?"Marine":"Matteo");var d=new Date(x.at*1000);
return '<div class="nt-rep'+(x.from==="athlete"?" nt-rep-a":"")+'"><span class="nt-rh"><b>'+esc(who)+'</b> <small>'+esc(d.toLocaleString(C.lang,{day:"numeric",month:"short",hour:"2-digit",minute:"2-digit"}))+'</small></span><p>'+esc(x.text).replace(/\n/g,"<br>")+'</p></div>';}).join("");
return '<div class="fd-thread">'+(r.length?'<h3>'+esc(W.thread)+'</h3>'+h:"")+'<details class="nt-replyd"><summary>'+esc(r.length?W.reply:W.ask)+'</summary><div class="fd-rbox"><textarea rows="3"></textarea><button type="button" class="btn btn-go" data-act="send">'+esc(W.send_r)+'</button></div></details></div>';}
var FAM=null,PK=["u","s","m","l","sl","pot","tsp","tbsp","cup","can","btl"];
function drinkOf(it){if(!it||it.m){return "";}var f=BYID[it.id];if(f&&FAM&&f.fm!=null){var fa=FAM[f.fm];if(!fa||!fa[1]){return "";}return fa[0]==="Water"?"w":"d";}return it.dr?"d":"";}
function slotFl(s){var w=+s.d||0,o=0;(s.i||[]).forEach(function(it){var k=drinkOf(it),g=+it.g||0;if(k==="w"){w+=g;}else if(k==="d"){o+=g;}});return [w,o];}
function dayFl(){var a=[0,0];C.slots.forEach(function(sv){var f=slotFl(slot(sv[0]));a[0]+=f[0];a[1]+=f[1];});return a;}
function porOf(f){if(!f){return null;}var b=BYID[f.id];return (b&&b.po)||f.po||null;}
function porG(po,u){if(!po){return 0;}for(var i=0;i<po.length;i++){if(po[i][0]===u){return +po[i][1];}}return 0;}
function unitLbl(u){return W["un_"+u]||u;}
function amtTxt(it){var g=fmt(it.g)+" g";return it.u&&+it.q>0?fmt(it.q)+(+it.q===1?" ":" × ")+unitLbl(it.u)+" ("+g+")":"";}
function itemSub(it){var a=amtTxt(it);return (a?a+" · ":"")+macro(it);}
function unitOpts(po,u,gen){var h='<option value="g"'+(u==="g"?" selected":"")+'>'+esc(W.un_g)+'</option>';(po||[]).forEach(function(p){h+='<option value="'+p[0]+'"'+(u===p[0]?" selected":"")+'>'+esc(unitLbl(p[0])+" ("+fmt(p[1])+" g)")+'</option>';});return h;}
function pickG(s){var q=parseFloat(String(s.q).replace(",","."))||0;return s.u==="g"?q:q*porG(porOf(s.pick),s.u);}
function setPick(f,g,u,q){var s=S.srch;s.pick=f;var po=porOf(f);if(u&&u!=="g"&&porG(po,u)>0){s.u=u;s.q=q||1;}else if(g){s.u="g";s.q=g;}else if(po&&po.length){var pref=["m","u","sl","pot"],k=po[0][0];for(var i=0;i<pref.length;i++){if(porG(po,pref[i])>0){k=pref[i];break;}}s.u=k;s.q=1;}else{s.u="g";s.q=100;}s.g=pickG(s);}
function pickHtml(){var s=S.srch,p=s.pick,po=porOf(p),g=pickG(s),it={k:p.k,c:p.c,p:p.p,f:p.f,g:g};
return '<div class="fd-search"><div class="fd-pick"><b>'+esc(p.n)+rcb(p.st)+tag(p.mine)+'</b><div class="fd-amt"><label>'+esc(W.amount)+' <input type="number" class="fd-pq" inputmode="decimal" min="0" max="5000" step="any" value="'+esc(s.q)+'"></label><label class="fd-ul"><span class="fd-sr">'+esc(W.unit)+'</span><select class="fd-pu" aria-label="'+esc(W.unit)+'">'+unitOpts(po,s.u)+'</select></label>'+(s.u!=="g"?'<span class="fd-pgv">= '+esc(fmt(g))+' g</span>':'')+'</div><span class="fd-pp">'+esc(macro(it))+'</span><div class="fd-row"><button type="button" class="btn btn-go" data-act="pickadd">'+esc(W.addit)+'</button><button type="button" class="fd-link" data-act="unpick">'+esc(W.cancel)+'</button></div></div></div>';}
function pickUpd(){var s=S.srch;s.g=pickG(s);var p=s.pick,pp=root.querySelector(".fd-pp"),gv=root.querySelector(".fd-pgv");if(pp){pp.textContent=macro({k:p.k,c:p.c,p:p.p,f:p.f,g:s.g});}if(gv){gv.textContent="= "+fmt(s.g)+" g";}}
/* Marine's day targets (athlete-visible, positive wording only) */
function tgHtml(){var tg=C.tg&&C.tg[S.date];if(!tg||!(+tg.k>0||+tg.c>0||+tg.p>0||+tg.f>0)){return "";}var t=dayTot(),h='<div class="fd-tgt" role="group" aria-label="'+esc(W.tg_title)+'">';
function bar(v,max,cl){var pc=max>0?Math.min(100,v/max*100):0;return '<div class="fd-tgb'+(cl?" "+cl:"")+'"><i'+(v>=max?' class="ok"':'')+' style="width:'+pc.toFixed(1)+'%"></i></div>';}
if(+tg.k>0){var k=Math.round(t.k),K=Math.round(+tg.k);
if(k>=K){h+='<p class="fd-tgk ok"><b>'+esc(W.tg_done.replace("%s",fmt0(K)))+'</b></p>';}
else{h+='<p class="fd-tge">'+esc(W.tg_eat)+'</p><p class="fd-tgk"><b>'+esc(fmt0(k))+'</b> <span>'+esc(W.tg_your)+' '+esc(fmt0(K))+' kcal</span></p>';}
h+=bar(k,K,"big");if(k<K){h+='<p class="fd-tggo">'+esc(W.tg_go.replace("%s",fmt0(K-k)+" kcal"))+'</p>';}}
var m=[["c",W.carbs],["p",W.protein],["f",W.fat]].filter(function(x){return (+tg[x[0]])>0;});
if(m.length){h+='<div class="fd-tgm">'+m.map(function(x){var v=Math.round(t[x[0]]),T=Math.round(+tg[x[0]]);return '<div><span>'+esc(x[1])+'</span>'+bar(v,T)+'<small>'+esc(W.tg_mac.replace("%1$s",fmt0(v)).replace("%2$s",fmt0(T)))+(v>=T?" ✓":"")+'</small></div>';}).join("")+'</div>';}
return h+'</div>';}
function stgHtml(k){var tg=C.tg&&C.tg[S.date],st=tg&&tg.sl&&tg.sl[k];if(!st){return "";}var s=slot(k),t=tot(s.i),fl=slotFl(s),a=[];
[["c",W.carbs],["p",W.protein],["f",W.fat]].forEach(function(x){var T=+st[x[0]]||0;if(T>0){var v=Math.round(t[x[0]]);a.push(x[1]+" "+W.tg_mac.replace("%1$s",fmt0(v)).replace("%2$s",fmt0(T))+(v>=T?" ✓":""));}});
if(+st.w>0){var w=Math.round(fl[0]+fl[1]);a.push(W.w_tile+" "+W.tg_ml.replace("%1$s",fmt0(w)).replace("%2$s",fmt0(st.w))+(w>=st.w?" ✓":""));}
return a.length?'<p class="fd-stg" data-stg="'+k+'"><b>'+esc(W.tg_meal)+':</b> '+esc(a.join(" · "))+'</p>':"";}
function tgUpd(){C.slots.forEach(function(sv){var el=root.querySelector('[data-stg="'+sv[0]+'"]');if(el){el.outerHTML=stgHtml(sv[0])||'<p class="fd-stg" data-stg="'+sv[0]+'" hidden></p>';}});var el=root.querySelector(".fd-tgbox");if(el){el.innerHTML=tgHtml();}}
/* voice logging: the browser's own speech recognition (no paid service); the text is parsed here and matched with the normal search */
var SRC=window.SpeechRecognition||window.webkitSpeechRecognition,REC=null,VL={en:"en-IE",it:"it-IT",pt:"pt-PT",sl:"sl-SI",sk:"sk-SK"};
function vParse(text){var P=window.ccNpParse;if(!P){return [];}return P.chunks(text,C.lang).map(function(c){return vRow(c.word,c.query,c.q,c.unit);});}
function vRow(word,query,q,unit){var P=window.ccNpParse,res=search(query);if(!res.length&&query!==word){res=search(word);}res=P.best(res,unit,porOf).slice(0,5);var r={word:word,opts:res,fi:0,q:1,u:"g"};if(!res.length){return r;}vUnit(r,q,unit);return r;}
function vUnit(r,q,unit){var x=window.ccNpParse.unitFor(porOf(r.opts[r.fi]),q,unit);r.u=x.u;r.q=x.q;}
function vG(r){var f=r.opts[r.fi];return r.u==="g"?(+r.q||0):(+r.q||0)*porG(porOf(f),r.u);}
function voiceHtml(){var v=S.voice,h='<div class="fd-voice">';
if(v.msg){h+='<p class="fd-vmsg'+(v.listening?" on":"")+'" role="status">'+(v.listening?'<span class="fd-dot" aria-hidden="true"></span>':'')+esc(v.msg)+'</p>';}
h+='<label class="fd-vtl">'+esc(W.v_text)+'<textarea class="fd-vt" rows="2">'+esc(v.text)+'</textarea></label><div class="fd-row">'+(SRC?'<button type="button" class="btn btn-ghost fd-mic" data-act="vlisten">🎙 '+esc(v.rows?W.v_again:W.v_btn)+'</button>':'')+'<button type="button" class="btn btn-ghost" data-act="vparse">'+esc(W.v_read)+'</button></div>';
if(v.rows){var ok=v.rows.filter(function(r){return r.opts.length;});h+='<h4 class="fd-vh">'+esc(W.v_right)+'</h4><ul class="fd-vl">';
v.rows.forEach(function(r,ix){if(!r.opts.length){h+='<li class="fd-vnf">'+esc(W.v_none.replace("%s",r.word))+'<button type="button" class="fd-x" data-act="vrm" data-vx="'+ix+'" aria-label="'+esc(W.remove)+'">'+XI+'</button></li>';return;}
var f=r.opts[r.fi],po=porOf(f),g=vG(r);
h+='<li><div class="fd-vrow"><label class="fd-vfl"><span class="fd-sr">'+esc(W.v_food)+'</span><select class="fd-vf" data-vx="'+ix+'" aria-label="'+esc(W.v_food+": "+r.word)+'">'+r.opts.map(function(o,j){return '<option value="'+j+'"'+(j===r.fi?" selected":"")+'>'+esc(o.n)+'</option>';}).join("")+'</select></label><button type="button" class="fd-x" data-act="vrm" data-vx="'+ix+'" aria-label="'+esc(W.remove)+'">'+XI+'</button></div>'
+'<div class="fd-amt"><label>'+esc(W.amount)+' <input type="number" class="fd-vq" data-vx="'+ix+'" inputmode="decimal" min="0" max="5000" step="any" value="'+esc(r.q)+'"></label><label class="fd-ul"><span class="fd-sr">'+esc(W.unit)+'</span><select class="fd-vu" data-vx="'+ix+'" aria-label="'+esc(W.unit)+'">'+unitOpts(po,r.u)+'</select></label><span class="fd-pgv" data-vg="'+ix+'">'+(r.u!=="g"?"= "+esc(fmt(g))+" g · ":"")+esc(fmt0(f.k*g/100))+' kcal</span></div></li>';});
h+='</ul><div class="fd-row">'+(ok.length?'<button type="button" class="btn btn-go" data-act="vlog">'+esc(W.v_logall)+' ('+ok.length+')</button>':'')+'<button type="button" class="fd-link" data-act="vcancel">'+esc(W.cancel)+'</button></div>';}
else{h+='<div class="fd-row"><button type="button" class="fd-link" data-act="vcancel">'+esc(W.cancel)+'</button></div>';}
return h+'</div>';}
function vRedraw(){var sl=root.querySelector('.fd-slot[data-slot="'+(S.voice&&S.voice.slot)+'"] .fd-voice');if(sl){var w=document.createElement("div");w.innerHTML=voiceHtml();sl.replaceWith(w.firstChild);}else{render();}}
function vDo(){var v=S.voice;if(!v){return;}var tx=root.querySelector(".fd-vt");if(tx){v.text=tx.value;}if(!v.text.trim()){return;}v.msg="";loadDB().then(function(){if(S.voice!==v){return;}v.rows=vParse(v.text);vRedraw();});}
function vListen(){var v=S.voice;if(!SRC){v.msg=W.v_nosup;vRedraw();var t0=root.querySelector(".fd-vt");if(t0){t0.focus();}return;}
try{if(REC){REC.abort();}}catch(x){}REC=new SRC();REC.lang=VL[C.lang]||"en-IE";REC.interimResults=true;REC.maxAlternatives=1;REC.continuous=false;
var fin="";v.listening=true;v.msg=W.v_listen;v.rows=null;v.text="";vRedraw();loadDB();
REC.onresult=function(e){var it="";fin="";for(var i=0;i<e.results.length;i++){if(e.results[i].isFinal){fin+=e.results[i][0].transcript+" ";}else{it+=e.results[i][0].transcript;}}var tx=root.querySelector(".fd-vt");v.text=(fin+it).trim();if(tx){tx.value=v.text;}};
REC.onerror=function(e){v.listening=false;v.msg=(e&&(e.error==="not-allowed"||e.error==="service-not-allowed"))?W.v_nosup:W.v_err;vRedraw();};
REC.onend=function(){if(S.voice!==v){return;}var was=v.listening;v.listening=false;if(v.text.trim()){vDo();}else if(was){v.msg=W.v_err;vRedraw();}};
try{REC.start();}catch(x){v.listening=false;v.msg=W.v_nosup;vRedraw();}}
function render(){var d=new Date(S.date+"T12:00:00"),lbl=d.toLocaleDateString(C.lang,{weekday:"long",day:"numeric",month:"long"}),isT=S.date===today();
var h='<div class="fd-nav"><button type="button" class="fd-arrow" data-act="prev" aria-label="'+esc(W.prev)+'">‹</button><div class="fd-date"><b>'+esc(lbl)+'</b>'+(isT?'<small>'+esc(W.today)+'</small>':'<button type="button" class="fd-link" data-act="today">'+esc(W.gotoday)+'</button>')+'</div><button type="button" class="fd-arrow" data-act="next" aria-label="'+esc(W.next)+'"'+(S.date>=shift(today(),7)?" disabled":"")+'>›</button></div>';
h='<div class="fd-stick">'+h+'<p class="fd-slim">'+slimHtml()+'</p></div><div class="fd-tgbox">'+tgHtml()+'</div><p class="fd-status" role="status"></p>'+(window.ccMpTop?window.ccMpTop(S.date):"");
C.slots.forEach(function(sv){h+=slotHtml(sv[0],sv[1]);});
/* Matteo 19 Nov: per-kg numbers are for Marine and the coach only; the weight box shows only when there is no Vekta weight (last 60 days) */
var wb=C.vkg?"":'<label class="fd-kg">'+esc(W.weight_n)+' <input type="number" class="fd-kgi" inputmode="decimal" min="25" max="250" step="0.1" value="'+esc(S.kg)+'"></label>';
h+='<div class="fd-tot"><h3>'+esc(W.day_total)+'</h3>'+(hasAny()?ringHtml(dayTot()):'')+'<div class="fd-totv">'+totV()+'</div>'+wb+'<button type="button" class="fd-link fd-copyday" data-act="copyday">'+esc(W.copy_day)+'</button></div>'+microHtml();
root.querySelector(".fd-day").innerHTML=h;root.querySelector(".fd-thbox").innerHTML=threadHtml();S.just=null;renderMine();renderCyc();microRefresh();watchThread();if(window.ccMpAfter){window.ccMpAfter(S.date);}}
function refreshNums(){C.slots.forEach(function(sv){var k=sv[0],s=slot(k),t=tot(s.i),el=root.querySelector('[data-tt="'+k+'"]');if(el){el.innerHTML=sumTxt(s,t);}
var st=root.querySelector('[data-stot="'+k+'"]');if(st){st.textContent=W.slot_total+": "+macroT(t);}
var sl=root.querySelector('.fd-slot[data-slot="'+k+'"]');if(sl){s.i.forEach(function(it,ix){var sm=sl.querySelector('[data-it="'+ix+'"]');if(sm){sm.textContent=itemSub(it);}});}});
C.slots.forEach(function(sv){var sx=root.querySelector('[data-sx="'+sv[0]+'"]');if(sx){var s2=slot(sv[0]);sx.innerHTML=sxTxt(sv[0],s2,tot(s2.i));}});
C.slots.forEach(function(sv){var gg=root.querySelector('[data-gg="'+sv[0]+'"]');if(gg){var s3=slot(sv[0]);gg.innerHTML=gaugesHtml(sv[0],s3,tot(s3.i));}});
var tv=root.querySelector(".fd-totv");if(tv){tv.innerHTML=totV();}ringUpd();slimUpd();tgUpd();microRefresh();}
function save(){S.dirty=true;status(W.saving);clearTimeout(S.timer);S.timer=setTimeout(flush,700);}
function payload(){return {page:C.page,date:S.date,data:JSON.stringify(S.day.s||{})};}
function flush(){clearTimeout(S.timer);if(!S.dirty){return Promise.resolve();}S.dirty=false;return send(C.u.save,payload()).then(function(){status(W.saved);}).catch(function(){S.dirty=true;status(W.err,true);});}
addEventListener("pagehide",function(){if(!S.dirty){return;}var f=new FormData(),p=payload();for(var k in p){f.append(k,p[k]);}f.append("_wpnonce",C.nonce);try{navigator.sendBeacon(C.u.save,f);S.dirty=false;}catch(x){}});
function go(ds){flush().then(function(){return send(C.u.day,{page:C.page,date:ds},"GET");}).then(function(d){S.date=ds;S.day=d;S.open={};S.srch=null;S.voice=null;render();}).catch(function(){status(W.err,true);});}
function mineHtml(){var h='<details class="fd-mine"'+(S.mineOpen?" open":"")+'><summary>'+esc(W.mine)+'</summary><div class="fd-mb"><p class="fd-muted">'+esc(W.mine_lede)+'</p>';
if(!S.mine.length&&!S.edit){h+='<p class="fd-muted">'+esc(W.none_mine)+'</p>';}
S.mine.forEach(function(m){h+='<div class="fd-mrow"><div><b>'+esc(m.n)+tag(m.t)+'</b><small>'+esc(macro100(m))+'</small></div><button type="button" class="fd-link" data-act="medit" data-id="'+esc(m.id)+'">'+esc(W.edit)+'</button><button type="button" class="fd-link" data-act="mdel" data-id="'+esc(m.id)+'">'+esc(W.del)+'</button></div>';});
h+=S.edit?formHtml():'<div class="fd-row"><button type="button" class="btn btn-ghost" data-act="newfood">'+esc(W.add_label)+'</button><button type="button" class="btn btn-ghost" data-act="newrecipe">'+esc(W.add_recipe)+'</button></div>';
return h+'</div></details>';}
function recipeCalc(e){var t=tot(e.ing),w=parseFloat(e.cw)||0,sum=e.ing.reduce(function(a,i){return a+(+i.g||0);},0);if(!(w>0)){w=sum;}var o={};F.forEach(function(x){o[x]=w>0?Math.round(t[x]*1000/w)/10:0;});o.na=(w>0&&!t.nam)?Math.round(t.na*1000/w)/10:null;o.w=w;o.sum=sum;return o;}
function formHtml(){var e=S.edit,h='<div class="fd-form"><h4>'+esc(e.id?W.edit:(e.t==="r"?W.add_recipe:W.add_label))+'</h4><label>'+esc(W.name)+'<input type="text" data-e="n" value="'+esc(e.n)+'" maxlength="120"></label>';
if(e.t==="f"){h+='<h4>'+esc(W.per100)+'</h4><div class="fd-nums">'+[["k","kcal"],["c",W.carbs+" (g)"],["p",W.protein+" (g)"],["f",W.fat+" (g)"],["fi",W.fibre+" (g), "+W.optional],["su",W.sugars+" (g), "+W.optional],["na",W.sodium+" (mg), "+W.optional]].map(function(x){return '<label>'+esc(x[1])+'<input type="number" inputmode="decimal" min="0" step="0.1" data-e="'+x[0]+'" value="'+esc(e[x[0]])+'"></label>';}).join("")+'</div>';}
else{h+='<h4>'+esc(W.ingredients)+'</h4>';
if(e.ing.length){h+='<ul class="fd-items">'+e.ing.map(function(it,ix){return '<li><div class="fd-in"><b>'+esc(it.n)+rcb(it.st)+tag(it.m)+'</b><small data-ing="'+ix+'">'+esc(macro(it))+'</small></div><label class="fd-g"><input type="number" inputmode="decimal" min="0" max="5000" step="1" data-e="ig" data-ix="'+ix+'" value="'+esc(it.g)+'" aria-label="'+esc(W.grams)+'"> g</label><button type="button" class="fd-x" data-act="ingrm" data-ix="'+ix+'" aria-label="'+esc(W.remove)+'">'+XI+'</button></li>';}).join("")+'</ul>';}
h+=(S.srch&&S.srch.ctx==="ing")?searchHtml():'<button type="button" class="btn btn-ghost" data-act="adding" style="justify-self:start">'+esc(W.add_ing)+'</button>';
var rc=recipeCalc(e);h+='<label>'+esc(W.cooked)+'<input type="number" inputmode="decimal" min="0" step="1" data-e="cw" value="'+esc(e.cw||"")+'" placeholder="'+esc(fmt0(rc.sum))+'" style="max-width:160px"><span class="fd-hint">'+esc(W.cooked_h)+'</span></label>';
h+='<p class="fd-stot fd-rcp">'+esc(W.per100+": "+macro100(rc))+'</p>';}
return h+'<p class="fd-msg err fd-emsg" role="alert"></p><div class="fd-row"><button type="button" class="btn btn-go" data-act="msave">'+esc(W.save)+'</button><button type="button" class="fd-link" data-act="mcancel">'+esc(W.cancel)+'</button></div></div>';}
function renderMine(){root.querySelector(".fd-minebox").innerHTML=mineHtml();}
function saveMine(){return send(C.u.mine,{page:C.page,data:JSON.stringify(S.mine)}).then(function(j){S.mine=j.mine||S.mine;}).catch(function(){status(W.err,true);});}
function focusQ(){var q=root.querySelector(".fd-q");if(q){q.focus();}}
function refreshRes(){var r=root.querySelector(".fd-res");if(r&&S.srch){r.innerHTML=resultsHtml();}}
function redraw(){if(S.srch&&S.srch.ctx==="ing"){renderMine();}else{render();}}
root.addEventListener("toggle",function(e){var t=e.target;if(t.classList&&t.classList.contains("fd-slot")){S.open[t.dataset.slot]=t.open;}else if(t.classList&&t.classList.contains("fd-mine")){S.mineOpen=t.open;keepOpen("mine",t.open);}else if(t.classList&&t.classList.contains("fd-micro")){S.microOpen=t.open;keepOpen("micro",t.open);}else if(t.classList&&t.classList.contains("fd-cyc")){S.cycOpen=t.open;keepOpen("cyc",t.open);}else if(t.classList&&t.classList.contains("fd-trd")){keepOpen("tr",t.open);}},true);
root.addEventListener("click",function(e){var b=e.target.closest("[data-act]");if(!b||!root.contains(b)){return;}var a=b.dataset.act,sl=b.closest(".fd-slot"),k=sl?sl.dataset.slot:null;
if(a==="prev"){go(shift(S.date,-1));}
else if(a==="next"){go(shift(S.date,1));}
else if(a==="today"){go(today());}
else if(a==="tothread"){var th=root.querySelector(".fd-thread");if(th){th.scrollIntoView({behavior:"smooth",block:"start"});}markSeen();}
else if(a==="add"||a==="adding"){S.voice=null;S.srch={ctx:a==="add"?"slot":"ing",slot:k,q:"",pick:null,g:100};if(a==="add"){S.open[k]=true;}redraw();focusQ();loadDB().then(refreshRes);}
else if(a==="cancel"){S.srch=null;redraw();}
else if(a==="voice"){S.srch=null;S.voice={slot:k,text:"",rows:null,msg:SRC?"":W.v_nosup,listening:false};S.open[k]=true;render();if(SRC){vListen();}else{var vt=root.querySelector(".fd-vt");if(vt){vt.focus();}}}
else if(a==="vlisten"){vListen();}
else if(a==="vparse"){vDo();}
else if(a==="vcancel"){try{if(REC){REC.abort();}}catch(x){}S.voice=null;render();}
else if(a==="vrm"){S.voice.rows.splice(+b.dataset.vx,1);vRedraw();}
else if(a==="vlog"){var vk=S.voice.slot,va=slot(vk).i,n0=va.length;S.voice.rows.forEach(function(r){if(!r.opts.length){return;}var f=r.opts[r.fi],g=Math.round(vG(r)*10)/10;if(!(g>0)){return;}
var it={id:f.id,n:f.n,g:g,k:f.k,c:f.c,p:f.p,f:f.f,fi:f.fi||0,su:f.su||0};if(f.mine){it.m=f.mine;}if(f.na!=null&&f.na!==""){it.na=f.na;}if(f.st){it.st=f.st;}if(r.u!=="g"){it.u=r.u;it.q=+r.q||1;}if(drinkOf(it)==="d"){it.dr=1;}
va.push(it);S.recent=[it].concat(S.recent.filter(function(x){return x.id!==it.id;})).slice(0,8);});
try{if(REC){REC.abort();}}catch(x){}S.voice=null;if(va.length>n0){S.just=vk+":"+(va.length-1);}S.open[vk]=true;render();save();}
else if(a==="pick"){var pf=S.res[+b.dataset.rx];if(staple(pf)){S.srch.ask={f:pf};redraw();}else{setPick(pf);redraw();var g=root.querySelector(".fd-pq");if(g){g.focus();g.select();}}}
else if(a==="rc"){var af=S.srch.ask.f,sp=staple(af),want=b.dataset.v,tg=(af.st===want||!sp)?af:(BYID[want==="r"?sp.raw:sp.cooked]||af);S.srch.ask=null;setPick(tg);redraw();var g3=root.querySelector(".fd-pq");if(g3){g3.focus();g3.select();}}
else if(a==="unpick"){S.srch.pick=null;S.srch.ask=null;redraw();focusQ();}
else if(a==="pickadd"){var p=S.srch.pick,g2=pickG(S.srch);if(!(g2>0)){return;}
var it={id:p.id,n:p.n,g:Math.round(g2*10)/10,k:p.k,c:p.c,p:p.p,f:p.f,fi:p.fi||0,su:p.su||0};if(p.mine){it.m=p.mine;}if(p.na!=null&&p.na!==""){it.na=p.na;}if(p.st){it.st=p.st;}if(S.srch.u&&S.srch.u!=="g"){it.u=S.srch.u;it.q=parseFloat(String(S.srch.q).replace(",","."))||1;}if(drinkOf(it)==="d"){it.dr=1;}
S.recent=[it].concat(S.recent.filter(function(x){return x.id!==it.id;})).slice(0,8);
if(S.srch.ctx==="slot"){var sk2=S.srch.slot,ar=slot(sk2).i;ar.push(it);S.just=sk2+":"+(ar.length-1);S.open[sk2]=true;S.srch=null;render();save();}else{S.edit.ing.push(it);S.srch=null;renderMine();}}
else if(a==="rm"){var li=b.closest("li");if(li){li.classList.add("fd-out");}setTimeout(function(){slot(k).i.splice(+b.dataset.ix,1);render();save();},200);}
else if(a==="star"){var si=slot(k).i[+b.dataset.ix];if(!si){return;}if(isFav(si.id)){S.fav=S.fav.filter(function(f){return f.id!==si.id;});}else{S.fav=S.fav.concat([JSON.parse(JSON.stringify(si))]).slice(-40);}render();
send(C.u.fav,{page:C.page,data:JSON.stringify(S.fav)}).then(function(j){S.fav=j.fav||S.fav;status(W.saved);}).catch(function(){status(W.err,true);});}
else if(a==="cyc"){var cv=b.dataset.v;if(cv==="off"&&!confirm(W.cyc_offq)){return;}b.disabled=true;
send(C.u.cycle,{page:C.page,act:cv,date:S.date}).then(function(j){S.cyc=j.cycle;S.cycOpen=true;render();status(W.saved);}).catch(function(){b.disabled=false;status(W.err,true);});}
else if(a==="chip"){var arr=b.dataset.src==="fav"?S.fav:S.recent,cf=arr[+b.dataset.i];if(!cf){return;}
setPick({id:cf.id,n:cf.n,k:cf.k,c:cf.c,p:cf.p,f:cf.f,fi:cf.fi||0,su:cf.su||0,na:cf.na==null?null:cf.na,st:cf.st||"",mine:cf.m||""},cf.u?0:(cf.g||100),cf.u,cf.q);redraw();var g4=root.querySelector(".fd-pq");if(g4){g4.focus();g4.select();}}
else if(a==="copyslot"||a==="copyday"){if(a==="copyday"&&hasAny()&&!confirm(W.copy_q)){return;}b.disabled=true;
flush().then(function(){return send(C.u.day,{page:C.page,date:shift(S.date,-1)},"GET");}).then(function(y){var ys=(y&&y.s&&!Array.isArray(y.s))?y.s:{},n=0;
(a==="copyday"?C.slots.map(function(sv){return sv[0];}):[k]).forEach(function(sk3){var src=ys[sk3];if(!src||(!(src.i||[]).length&&!(+src.d>0))){return;}n++;var dst=slot(sk3),cp=JSON.parse(JSON.stringify(src.i||[]));
if(a==="copyday"){dst.i=cp;dst.d=+src.d||0;if(src.r){dst.r=src.r;}}else{dst.i=dst.i.concat(cp);if(!(+dst.d>0)&&+src.d>0){dst.d=+src.d;}}S.open[sk3]=true;});
if(!n){b.disabled=false;status(W.copy_none);return;}render();save();}).catch(function(){b.disabled=false;status(W.err,true);});}
else if(a==="phdel"){flush().then(function(){return send(C.u.photodel,{page:C.page,date:S.date,slot:k});}).then(function(){var s=slot(k);delete s.ph;delete s.phu;render();}).catch(function(){status(W.err,true);});}
else if(a==="send"){var box=b.closest(".fd-rbox"),t=box.querySelector("textarea");if(!t.value.trim()){return;}b.disabled=true;
send(C.u.reply,{page:C.page,date:S.date,text:t.value}).then(function(j){S.day.r=j.r||[];render();markSeen();}).catch(function(){b.disabled=false;status(W.sent_err,true);});}
else if(a==="newfood"||a==="newrecipe"){S.edit={t:a==="newfood"?"f":"r",id:"",n:"",k:"",c:"",p:"",f:"",fi:"",su:"",na:"",ing:[],cw:""};S.srch=null;S.mineOpen=true;renderMine();var n=root.querySelector('[data-e="n"]');if(n){n.focus();}}
else if(a==="medit"){var m=S.mine.filter(function(x){return x.id===b.dataset.id;})[0];if(!m){return;}S.edit=JSON.parse(JSON.stringify(m));if(!S.edit.ing){S.edit.ing=[];}S.srch=null;S.mineOpen=true;renderMine();}
else if(a==="mdel"){if(!confirm(W.delq)){return;}S.mine=S.mine.filter(function(x){return x.id!==b.dataset.id;});renderMine();saveMine();}
else if(a==="mcancel"){S.edit=null;S.srch=null;renderMine();}
else if(a==="ingrm"){S.edit.ing.splice(+b.dataset.ix,1);renderMine();}
else if(a==="msave"){var e2=S.edit,msg=root.querySelector(".fd-emsg"),o={id:e2.id||("M"+Date.now().toString(36)),t:e2.t,n:String(e2.n||"").trim()};
if(e2.t==="f"){if(!o.n||!(parseFloat(e2.k)>=0&&String(e2.k).trim()!=="")){msg.textContent=W.need;return;}F.forEach(function(x){o[x]=Math.max(0,parseFloat(String(e2[x]).replace(",","."))||0);});var nv=String(e2.na==null?"":e2.na).replace(",",".").trim();o.na=nv!==""&&!isNaN(parseFloat(nv))?Math.max(0,parseFloat(nv)):null;}
else{if(!o.n||!e2.ing.length){msg.textContent=W.need_r;return;}var rc=recipeCalc(e2);F.forEach(function(x){o[x]=rc[x];});o.na=rc.na;o.ing=e2.ing;o.cw=parseFloat(e2.cw)||0;}
var ix=-1;S.mine.forEach(function(x,i){if(x.id===o.id){ix=i;}});if(ix>-1){S.mine[ix]=o;}else{S.mine.push(o);}S.edit=null;S.srch=null;renderMine();saveMine().then(renderMine);}
});
var qt=null,kt=null;
root.addEventListener("input",function(e){var el=e.target,sl=el.closest(".fd-slot"),k=sl?sl.dataset.slot:null,f=el.dataset.f,ef=el.dataset.e;
if(el.classList.contains("fd-q")){S.srch.q=el.value;var cb=el.parentNode.querySelector(".fd-chipbox");if(cb){cb.hidden=!!el.value.trim();}clearTimeout(qt);qt=setTimeout(refreshRes,120);return;}
if(el.classList.contains("fd-pq")){S.srch.q=el.value;pickUpd();return;}
if(el.classList.contains("fd-vt")&&S.voice){S.voice.text=el.value;return;}
if(el.classList.contains("fd-vq")&&S.voice){var vr=S.voice.rows[+el.dataset.vx];vr.q=el.value;var vf=vr.opts[vr.fi],vgg=vG(vr),vs=root.querySelector('[data-vg="'+el.dataset.vx+'"]');if(vs){vs.textContent=(vr.u!=="g"?"= "+fmt(vgg)+" g · ":"")+fmt0(vf.k*vgg/100)+" kcal";}return;}
if(el.classList.contains("fd-kgi")){S.kg=el.value;refreshNums();clearTimeout(kt);kt=setTimeout(function(){send(C.u.kg,{page:C.page,kg:S.kg}).then(function(){status(W.saved);}).catch(function(){status(W.err,true);});},800);return;}
if(f==="g"&&k){var gi=slot(k).i[+el.dataset.ix];gi.g=parseFloat(el.value)||0;delete gi.u;delete gi.q;refreshNums();save();return;}
if(f==="t"&&k){slot(k).t=el.value;refreshNums();save();return;}
if(f==="d"&&k){slot(k).d=Math.max(0,Math.round(parseFloat(el.value)||0));refreshNums();save();return;}
if(f==="r"&&k){slot(k).r=Math.min(1440,pmin(el.value));refreshNums();save();return;}
if(f==="n"&&k){slot(k).n=el.value;save();return;}
if(ef&&S.edit){if(ef==="ig"){S.edit.ing[+el.dataset.ix].g=parseFloat(el.value)||0;var sm=root.querySelector('[data-ing="'+el.dataset.ix+'"]');if(sm){sm.textContent=macro(S.edit.ing[+el.dataset.ix]);}}else{S.edit[ef]=el.value;}
var rp=root.querySelector(".fd-rcp");if(rp&&S.edit.t==="r"){rp.textContent=W.per100+": "+macro100(recipeCalc(S.edit));}}
});
root.addEventListener("keydown",function(e){if(e.key==="Enter"&&e.target.classList.contains("fd-pq")){e.preventDefault();var b=root.querySelector('[data-act="pickadd"]');if(b){b.click();}}
if(e.key==="Enter"&&e.target.classList.contains("fd-q")){e.preventDefault();var first=root.querySelector('.fd-rl [data-act="pick"]');if(first){first.click();}}});
root.addEventListener("change",function(e){var el=e.target;
if(el.classList.contains("fd-pu")&&S.srch&&S.srch.pick){var og=pickG(S.srch);S.srch.u=el.value;S.srch.q=el.value==="g"?Math.round(og||100):1;S.srch.g=pickG(S.srch);redraw();var pq=root.querySelector(".fd-pq");if(pq){pq.focus();pq.select();}return;}
if((el.classList.contains("fd-vf")||el.classList.contains("fd-vu"))&&S.voice){var r=S.voice.rows[+el.dataset.vx];if(!r){return;}
if(el.classList.contains("fd-vf")){r.fi=+el.value;if(r.u!=="g"&&!(porG(porOf(r.opts[r.fi]),r.u)>0)){vUnit(r,null,null);}}else{var og2=vG(r);r.u=el.value;r.q=r.u==="g"?Math.round(og2||100):1;}vRedraw();return;}
if(el.dataset.f!=="ph"){return;}var sl=el.closest(".fd-slot"),k=sl.dataset.slot,fi=el.files[0];if(!fi){return;}
if(fi.size>10485760||!/^image\//.test(fi.type||"")&&!/\.(heic|heif|jpe?g|png|webp)$/i.test(fi.name)){status(W.photo_bad,true);return;}
status(W.uploading);flush().then(function(){var fd=new FormData();fd.append("file",fi);fd.append("date",S.date);fd.append("slot",k);fd.append("page",C.page);return send(C.u.photo,fd);})
.then(function(j){var s=slot(k);s.ph=j.id;s.phu=j.url;S.open[k]=true;render();status(W.saved);}).catch(function(){status(W.err,true);});});
if(C.trends){root.querySelector(".fd-trbox").innerHTML='<details class="fd-trd"'+(OPEN.tr?" open":"")+'><summary>'+esc(W.mytrends)+'</summary><div><p class="fd-muted">'+esc(W.tr_lede)+'</p><div class="fd-trends" data-tr="'+esc(JSON.stringify(C.trends))+'"></div></div></details>';}
window.ccFd={root:root,render:render,flush:flush,status:status,date:function(){return S.date;},setDay:function(d){S.day=d;render();},add:function(k){S.srch={ctx:"slot",slot:k,q:"",pick:null,g:100};S.open[k]=true;render();focusQ();loadDB().then(refreshRes);var sl=root.querySelector('.fd-slot[data-slot="'+k+'"]');if(sl){sl.scrollIntoView({block:"start"});}}};
render();
loadDB().then(function(){if(DB){refreshNums();}});
if(OPEN.tr&&window.ccFdTrends){var tre=root.querySelector(".fd-trends[data-tr]");if(tre){setTimeout(function(){window.ccFdTrends(tre);},0);}}
if(C.female&&window.ccFdM){window.ccFdM.load(C.micro).then(function(M){S.M=M;var tv=root.querySelector(".fd-totv");if(tv){tv.innerHTML=totV();}}).catch(function(){});}
if(!C.fixed&&today()!==S.date){go(today());}
if(C.fixed||C.scroll){var fe=document.getElementById("food");if(fe){setTimeout(function(){fe.scrollIntoView();},300);}}
})();
JS;
    return '<script>' . str_replace(["\r", "\n"], ['', ' '], $js) . '</script>';
}
