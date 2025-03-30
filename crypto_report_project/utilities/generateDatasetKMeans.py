import sqlite3
import pandas as pd

# Nome del database SQLite
DB_NAME = "crypto_news.db"
# Nome del file CSV di output
CSV_FILENAME = "Dataset/dataset_KMeans.csv"

# Connessione al database
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# Query per selezionare i dati richiesti
query = """
SELECT id_articolo, long_resume 
FROM descrizione_articoli 
WHERE full_article_html IS NOT NULL AND full_article_html != "" AND long_resume IS NOT NULL OR long_resume<>""
"""

# Esecuzione della query e caricamento dei risultati in un DataFrame
cursor.execute(query)
rows = cursor.fetchall()

df = pd.DataFrame(rows, columns=["id_articolo", "long_resume"])
# Aggiunta della colonna 'categoria' inizialmente vuota
df["categoria"] = ""

# Salvataggio in un file CSV
df.to_csv(CSV_FILENAME, index=False, encoding='utf-8')

# Chiusura della connessione al database
conn.close()

print(f"File '{CSV_FILENAME}' generato con successo!")
