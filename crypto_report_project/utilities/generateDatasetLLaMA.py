import sqlite3
import csv

# Nome del database e del file CSV di output
db_path = "crypto_news.db"
csv_filename = "summaryDataset.csv"

# Connessione al database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Query per estrarre i dati richiesti
query = """
SELECT full_article_html, short_resume, long_resume 
FROM descrizione_articoli
WHERE full_article_html IS NOT NULL AND full_article_html != "" AND id_articolo < 525
"""
cursor.execute(query)

# Recupera i dati
rows = cursor.fetchall()

# Creazione del file dataset CSV per addestramento LLama 3.2
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["User", "Summary"])  # Intestazione colonne

    for full_article, short_resume, long_resume in rows:
        # Prompt per il riassunto breve (30-40 parole)
        short_summary_prompt = f"""Genera un riassunto conciso di 30-40 parole per il seguente articolo, offrendo una panoramica chiara e immediata della notizia. Se l'articolo ha scarso contenuto informativo, restituisci invece la frase: "L'articolo non contiene contenuti rilevanti.". Articolo: {full_article}"""
        
        # Prompt per il riassunto lungo (150-200 parole)
        long_summary_prompt = f"""Genera un riassunto dettagliato di 150-200 parole del seguente articolo. Il riassunto deve includere i punti chiave, il contesto e le implicazioni della notizia. Se l'articolo ha scarso contenuto informativo, restituisci invece la frase: "L'articolo non contiene contenuti rilevanti.". Articolo: {full_article}"""

        # Scrive due righe nel CSV: una per short_resume e una per long_resume
        writer.writerow([short_summary_prompt, short_resume])  # Riga per short resume
        writer.writerow([long_summary_prompt, long_resume])   # Riga per long resume

# Chiudi la connessione al database
conn.close()

print(f"File CSV '{csv_filename}' creato con successo.")

