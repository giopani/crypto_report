import sqlite3
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

def classificaNewArticle():
    # Connessione al database
    conn = sqlite3.connect('crypto_news.db')
    cursor = conn.cursor()

    # Estrarre i dati dalla tabella 'descrizione_articoli'
    query = """
        SELECT id_articolo, long_resume
        FROM descrizione_articoli
        WHERE long_resume IS NOT NULL AND category IS NULL;
    """
    cursor.execute(query)
    dati = cursor.fetchall()

    # Creare un DataFrame dai dati estratti
    columns = ['id', 'long_resume']
    df = pd.DataFrame(dati, columns=columns)

    # Caricare il modello e il vettorizzatore
    with open('Classificazione/modello_naive_bayes.pkl', 'rb') as model_file:
        model = pickle.load(model_file)

    with open('Classificazione/vectorizer_tfidf.pkl', 'rb') as vectorizer_file:
        vectorizer = pickle.load(vectorizer_file)

    # Trasformare i testi in TF-IDF
    X_tfidf = vectorizer.transform(df['long_resume'])

    # Predire le categorie
    predizioni = model.predict(X_tfidf)
    df['categoria'] = predizioni

    # Aggiornare il database con le categorie
    for index, row in df.iterrows():
        cursor.execute("""
            UPDATE descrizione_articoli
            SET category = ?
            WHERE id_articolo = ?;
        """, (row['categoria'], row['id']))

    # Salvare le modifiche
    conn.commit()

    # Chiudere la connessione
    conn.close()

    print("Categorizzazione completata e salvata nel database.")
