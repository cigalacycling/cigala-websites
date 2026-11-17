"""Matteo 17 Nov 2026: everything in the hub in the athlete's language. The English articles in "Worth reading" keep their
link (the article itself is English, the section heading already says so) but their titles are shown translated in the
Italian, Portuguese and Slovenian hubs. Edits the shared hub pages in place (backup first). Usage: reading_titles.py [--live]"""
import sys, json
live = '--live' in sys.argv
sys.argv = ['x'] + (['--live'] if live else []); sys.path.insert(0, r'C:\Users\matte\vekta\athlete-hub\cigala-websites\tools')
import coaching_athlete_area as c
T = {
 'The power of Zone 2 training': ('Il potere dell’allenamento in Zona 2', 'O poder do treino em Zona 2', 'Moč treninga v coni 2'),
 'Critical Power': ('Critical Power (potenza critica)', 'Critical Power (potência crítica)', 'Critical Power (kritična moč)'),
 'What is W Prime?': ('Cos’è il W′ (W prime)?', 'O que é o W′ (W prime)?', 'Kaj je W′ (W prime)?'),
 'Critical Power testing: how to get reliable data': ('Test di Critical Power: come ottenere dati affidabili', 'Testes de Critical Power: como obter dados fiáveis', 'Testiranje kritične moči: kako do zanesljivih podatkov'),
 'Strength training for cyclists': ('Allenamento di forza per ciclisti', 'Treino de força para ciclistas', 'Trening moči za kolesarje'),
 'How to calibrate a power meter': ('Come calibrare un misuratore di potenza', 'Como calibrar um medidor de potência', 'Kako umeriti merilnik moči'),
 'How many carbs per hour?': ('Quanti carboidrati all’ora?', 'Quantos hidratos por hora?', 'Koliko ogljikovih hidratov na uro?'),
 'What to eat and drink on the bike': ('Cosa mangiare e bere in bici', 'O que comer e beber na bicicleta', 'Kaj jesti in piti na kolesu'),
 'Hydration tips': ('Consigli sull’idratazione', 'Dicas de hidratação', 'Nasveti za hidracijo'),
 'Avoid bonking on the bike': ('Come evitare la crisi di fame in bici', 'Como evitar a quebra de energia na bicicleta', 'Kako se izogniti padcu energije na kolesu'),
 'How to maximise your recovery': ('Come massimizzare il recupero', 'Como maximizar a tua recuperação', 'Kako čim bolje regenerirati'),
 'Why am I so tired after exercise?': ('Perché sono così stanco dopo l’allenamento?', 'Porque fico tão cansado depois do treino?', 'Zakaj sem po treningu tako utrujen?'),
 'Heart rate variability (HRV)': ('Variabilità della frequenza cardiaca (HRV)', 'Variabilidade da frequência cardíaca (VFC)', 'Variabilnost srčnega utripa (HRV)'),
 'Tapering': ('Lo scarico prima della gara', 'O taper antes da prova', 'Zmanjšanje obremenitve pred tekmo'),
 'Potentiation in warm-ups': ('La potenziazione nel riscaldamento', 'Potenciação no aquecimento', 'Potenciacija pri ogrevanju'),
 'Tips for not getting dropped': ('Consigli per non staccarsi dal gruppo', 'Dicas para não ficar para trás no grupo', 'Nasveti, da ne odpadeš iz skupine'),
 'Tips for gravel racing': ('Consigli per le gare gravel', 'Dicas para provas de gravel', 'Nasveti za gravel tekme'),
}
IDX = {'it': 0, 'pt': 1, 'sl': 2}
bk = c.ROOT + ('live-coaching' if live else 'stg-coaching') + '/backup/'
for p in c.req(f'{c.B}/wp/v2/cc_athlete?status=private&per_page=100&context=edit&_fields=id,meta,content'):
    if not (p.get('meta') or {}).get('cc_shared'): continue
    L = p['meta'].get('cc_lang') or 'en'
    if L not in IDX: continue
    raw = p['content']['raw']; new = raw; n = 0
    for en, tr in T.items():
        a = f'">{en}</a></li>'
        if a in new: new = new.replace(a, f'">{tr[IDX[L]]}</a></li>'); n += 1
    if not n: print(p['id'], L, 'nothing to translate'); continue
    json.dump({'id': p['id'], 'raw': raw}, open(bk + f'shared-hub-{p["id"]}-before-reading-titles-2026-11-17.json', 'w', encoding='utf-8'), ensure_ascii=False)
    r = c.req(f'{c.B}/wp/v2/cc_athlete/{p["id"]}', {'content': new}, 'POST')
    print(p['id'], L, f'{n} titles translated' if isinstance(r, dict) and r.get('id') else 'FAILED ' + str(r)[:150])
