import sqlite3
import requests
import re
import database

# URL dell'API su ngrok
API_URL = "https://a20f-34-90-148-36.ngrok-free.app/generate_summaries/"    #da aggiornare a ogni avvio del server

# Funzione per rimuovere l'ultima frase incompleta
def clean_incomplete_sentence(text):
    sentences = re.split(r'([.!?]\s+)', text)  # Divide il testo mantenendo i segni di punteggiatura e gli spazi
    if len(sentences) > 2:
        return "".join(sentences[:-2]) + "."  # Rimuove l'ultima frase se è incompleta
    return text


#funzione principale per riassumere gli articoli
def summarize_articles():
    articles = database.get_articles_to_summarize()

    for article in articles:
        id_articolo, full_article_html = article
        
        # Creazione del payload per l'API
        payload = {"article_text": full_article_html}
        
        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) == 2:
                    short_summary = clean_incomplete_sentence(data[0])
                    long_summary = clean_incomplete_sentence(data[1])
                    
                    # Aggiornamento del database con i riassunti generati
                    database.save_article_summary(id_articolo,short_summary,long_summary)
                    
                    print(f"Riassunto generato e salvato per l'articolo ID {id_articolo}")
                else:
                    print(f"Formato della risposta non valido per l'articolo ID {id_articolo}: {data}")
            else:
                print(f"Errore nella richiesta per l'articolo ID {id_articolo}: {response.status_code} {response.text}")
        except Exception as e:
            database.mark_article_as_processed(id_articolo)
            print(f"Errore durante l'elaborazione dell'articolo ID {id_articolo}: {str(e)}")

    print("Elaborazione completata.")

#summarize_articles()