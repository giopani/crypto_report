import sqlite3
import pandas as pd

# Percorso del database SQLite
db_path = "crypto_news.db"  # Modifica con il percorso corretto

# Percorso del dataset riclassificato
dataset_path = "Dataset/dataset_long_classificato.csv"

# Caricare il dataset riclassificato
df_riclassificato = pd.read_csv(dataset_path)

# Connessione al database SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Iterare su ogni riga del dataset e aggiornare il database
for index, row in df_riclassificato.iterrows():
    id_articolo = row["id_articolo"]
    categoria_riclassificata = row["categoria"]

    # Query SQL per aggiornare il campo "category"
    query = """
    UPDATE descrizione_articoli
    SET category = ?
    WHERE id_articolo = ?
    """
    cursor.execute(query, (categoria_riclassificata, id_articolo))

# Salvare le modifiche e chiudere la connessione
conn.commit()
conn.close()

print("Database aggiornato con le categorie riclassificate!")

