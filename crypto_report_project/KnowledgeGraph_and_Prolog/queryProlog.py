import sqlite3
import datetime
from pyswip import Prolog

def execute_queryProlog():
    # Connessione al database SQLite
    conn = sqlite3.connect('crypto_news.db')
    cursor = conn.cursor()

    # Date fisse per coerenza nei test
    oggi_str = "2025/03/24"
    una_settimana_fa_str = "2025/03/18"

    # Estrazione degli articoli dal database per l'ultima settimana
    query = """
    SELECT da.id_articolo, da.long_resume, ma.data
    FROM meta_articoli as ma
    JOIN descrizione_articoli as da ON ma.id = da.id_articolo
    WHERE da.long_resume IS NOT NULL
    AND ma.data BETWEEN ? AND ?
    """
    cursor.execute(query, (una_settimana_fa_str, oggi_str))
    articoli = cursor.fetchall()

    # Inizializza Prolog e carica la knowledge base generata
    prolog = Prolog()
    prolog.consult(r"knowledgeBaseSettimanale.pl")


    # 1. Identificazione articoli rilevanti
    articoli_rilevanti = {}

    for articolo in articoli:
        id_articolo = articolo[0]
        query = f"relevant_document({id_articolo})."
        if list(prolog.query(query)):
            articoli_rilevanti[id_articolo] = {'correlati': set()}

    # 2. Ricerca articoli correlati
    for id_articolo_rilevante in articoli_rilevanti.keys():
        query = f"articolo_correlato({id_articolo_rilevante}, Correlato)."
        risultati = list(prolog.query(query))
        for risultato in risultati:
            articolo_correlato = risultato['Correlato']
            articoli_rilevanti[id_articolo_rilevante]['correlati'].add(articolo_correlato)

    # 3. Stampa risultati articoli rilevanti e correlati
    for articolo_id, dati in articoli_rilevanti.items():
        print(f"Articolo Rilevante: {articolo_id}")
        print(f"Articoli Correlati: {sorted(list(dati['correlati']))}\n")

    # 4. Estrazione e stampa delle entità più menzionate
    query_all_entities = "all_entities_query(ListaEntita)."
    all_entities_result = list(prolog.query(query_all_entities))

    if all_entities_result:
        all_entities = all_entities_result[0]['ListaEntita']
        top_entities = sorted(all_entities, key=lambda x: x[0], reverse=True)[:6]

        print("\nLe entita' piu' citate sono:")
        for count, entity in top_entities:
            print(f"- {entity}: {count}")

    # Chiusura della connessione al database
    conn.close()
