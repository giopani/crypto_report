import sqlite3
import csv

def fetch_and_save_to_csv():
    # Connessione al database
    conn = sqlite3.connect("crypto_news.db")
    cursor = conn.cursor()

    # Query per selezionare id_articolo, long_resume e caetgory
    query = """
    SELECT long_resume, category 
    FROM descrizione_articoli
    WHERE (long_resume IS NOT NULL OR long_resume<>"") AND id_articolo <=1265 AND category is not null
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    # Salvataggio dei risultati in un file CSV
    with open("summary_categorized.csv", "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        # Scrittura dell'intestazione
        writer.writerow(["long_resume", "category"])
        # Scrittura dei dati
        writer.writerows(rows)
    
    # Chiusura della connessione
    conn.close()

if __name__ == '__main__':
    fetch_and_save_to_csv()
