import sqlite3
import re
import datetime  # Per lavorare con le date
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
import KnowledgeGraph_and_Prolog.entities_and_relations

# Scarica le stopwords se non lo hai già fatto
#nltk.download('punkt')
#nltk.download('stopwords')



# Rimozione delle stopwords
stop_words = set(stopwords.words('italian'))

def preprocess_text(text):
    """Rimuove le stopwords dal testo"""
    text = text.lower()  # Converti tutto in minuscolo
    words = word_tokenize(text)
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]
    return " ".join(filtered_words)  # Restituisce il testo filtrato come stringa



def extract_entities(text):
    """Estrae le entità riconosciute nel testo confrontandole con i dizionari definiti"""
    recognized_entities = set()
    text = text.lower()  # Converte tutto in minuscolo per il confronto

    all_entities = {**KnowledgeGraph_and_Prolog.entities_and_relations.people, **KnowledgeGraph_and_Prolog.entities_and_relations.crypto, **KnowledgeGraph_and_Prolog.entities_and_relations.financial_institutions, **KnowledgeGraph_and_Prolog.entities_and_relations.companies}

    for entity_name, aliases in all_entities.items():
        for alias in aliases:
            if re.search(r'\b' + re.escape(alias.lower()) + r'\b', text):
                recognized_entities.add(entity_name)
                break  # Passa alla prossima entità se è trovata

    return recognized_entities



def genera_kb_settimanale():

    # Connessione al database SQLite
    conn = sqlite3.connect('crypto_news.db')
    cursor = conn.cursor()

    # Calcoliamo la data di oggi e quella di una settimana fa
    oggi = datetime.date.today()
    una_settimana_fa = oggi - datetime.timedelta(days=7)

    # Convertiamo le date nel formato richiesto dal database: YYYY/MM/DD
    oggi_str = oggi.strftime('%Y/%m/%d')
    una_settimana_fa_str = una_settimana_fa.strftime('%Y/%m/%d')

    # Estrazione degli articoli dal database per l'ultima settimana
    query = """SELECT da.id_articolo, da.long_resume, ma.data 
            FROM meta_articoli as ma
            JOIN descrizione_articoli as da ON ma.id = da.id_articolo
            WHERE da.long_resume IS NOT NULL 
            AND ma.data BETWEEN ? AND ?"""
    cursor.execute(query, (una_settimana_fa_str, oggi_str))
    articoli = cursor.fetchall()
    conn.close()


    with open("knowledgeBaseSettimanale.pl", "w") as file:
        
        # Carichiamo il contenuto di knowledgeBaseStandard.pl e lo scriviamo all'inizio del file
        try:
            with open("KnowledgeGraph_and_Prolog/knowledgeBaseStandard.pl", "r") as kb_file:
                kb_content = kb_file.read()
                file.write(kb_content)
                file.write("\n\n")  # Separatore per chiarezza
        except FileNotFoundError:
            print("Attenzione: Il file 'kb.pl' non è stato trovato. Procedo senza includerlo.")
        
        # Aggiunta delle direttive discontiguous per evitare errori
        file.write(":- discontiguous article/2.\n")
        file.write(":- discontiguous mention/2.\n\n")
        
        file.write(f"% Knowledge Graph Settimanale generato il {oggi_str}\n\n")
        
        # Aggiungiamo le regole di inferenza
        file.write(r"""
                   
% --- Regola per identificare i documenti rilevanti ---
relevant_document(Document) :-
    findall(Entity, mention(Document, Entity), Entities),
    length(Entities, Count),
    Count > 3.
                        
% --- Articoli Correlati Direttamente ---
articolo_correlato(Articolo1, Articolo2) :-
    mention(Articolo1, Entita),
    mention(Articolo2, Entita),
    Articolo1 \= Articolo2.

% --- Articoli Correlati Indirettamente tramite Founder ---
articolo_correlato(Articolo1, Articolo2) :-
    mention(Articolo1, Entita1),
    mention(Articolo2, Entita2),
    (founder(Entita1, Entita2); founder(Entita2, Entita1)),
    Articolo1 \= Articolo2.

% --- Articoli Correlati Indirettamente tramite President ---
articolo_correlato(Articolo1, Articolo2) :-
    mention(Articolo1, Entita1),
    mention(Articolo2, Entita2),
    (president(Entita1, Entita2); president(Entita2, Entita1)),
    Articolo1 \= Articolo2.

% --- Articoli Correlati Indirettamente tramite CEO ---
articolo_correlato(Articolo1, Articolo2) :-
    mention(Articolo1, Entita1),
    mention(Articolo2, Entita2),
    (ceo(Entita1, Entita2); ceo(Entita2, Entita1)),
    Articolo1 \= Articolo2.

% --- Articoli Correlati Estesi ---
articolo_correlato(Articolo1, Articolo2) :-
    mention(Articolo1, Entita1),
    mention(Articolo2, Entita2),
    (   Entita1 = Entita2 ; 
        founder(Entita1, Entita2) ; 
        founder(Entita2, Entita1) ;
        ceo(Entita1, Entita2) ; 
        ceo(Entita2, Entita1) ;
        president(Entita1, Entita2) ; 
        president(Entita2, Entita1)
    ),
    Articolo1 \= Articolo2.

% --- Regole per Scoprire Tendenze Emergenti ---
frequenza_entita(Entita, Count) :-
    setof(ArticoloID, mention(ArticoloID, Entita), ArticoliUnici),
    length(ArticoliUnici, Count).
                   
% --- Query per estrarre tutte le entità con i conteggi ---
all_entities_query(ListaEntita) :-
    findall([Count, Entita], (frequenza_entita(Entita, Count)), ListaEntita).

""")
        
        # Processamento degli articoli
        file.write("\n% --- Articoli e Menzioni ---\n")
        for articolo in articoli:
            id_articolo, long_resume, data_articolo = articolo
            file.write(f"article({id_articolo}, '{data_articolo}').\n")
            
            # Estrazione delle entità citate PRIMA del pre-processing
            entities_found = extract_entities(long_resume)
            
            # Aggiunta delle entità riconosciute nel file Prolog
            for entity in entities_found:
                file.write(f"mention({id_articolo}, '{entity}').\n")
        
        print(f"Knowledge Graph Settimanale generato correttamente")
