import config
from datetime import datetime
import requests
import html
import database


# Recupera le news da start_page a end_page, serve solo per inizializzare il db
def fetch_news_in_range(start_page, end_page):
    """
    Recupera le notizie da un range di pagine, effettua il parsing e restituisce una lista
    con gli articoli invertiti, in modo che gli elementi meno recenti siano all'inizio
    e quelli più recenti alla fine.

    Args:
        start_page (int): Numero della prima pagina da recuperare.
        end_page (int): Numero dell'ultima pagina da recuperare.

    Returns:
        list: Lista di notizie con gli articoli più recenti in cima.
    """
    if start_page > end_page:
        raise ValueError("start_page deve essere minore o uguale a end_page.")

    all_news = []

    for page in range(start_page, end_page + 1):  # Itera dalla prima pagina all'ultima
        raw_news = fetch_page(page)  # Recupera gli articoli grezzi della pagina

        if not raw_news:
            print(f"Pagina {page}: nessuna notizia trovata.")
            continue

        all_news.extend(raw_news)  # Aggiunge gli articoli alla lista totale
        print(f"Pagina {page} recuperata e processata con successo.")

    # Inverte la lista per inserire prima le notizie più recenti
    all_news.reverse()
    
    saved_count = database.save_news_to_db(all_news)
    print(f"{saved_count} nuove notizie salvate nel database.")
    
    return None


# Recupera una singola pagina di notizie
def fetch_page(page):
    """
    Recupera una singola pagina di notizie dall'API di CryptoPanic e formatta le notizie.
    """
    params = {
        "auth_token": config.API_TOKEN,
        "metadata": "true",
        "regions": "it",
        "page": page
    }

    response = requests.get(config.API_URL, params=params)

    if response.status_code != 200:
        print(f"Errore API: {response.status_code}")
        return []

    raw_news = response.json().get("results", [])
    formatted_news = []

    for item in raw_news:
        try:
            formatted_news.append(parse_news_item(item))  # parse_news_item restituisce un dizionario
        except Exception as e:
            print(f"Errore durante il parsing di un articolo: {e}")

    return formatted_news


# Parsing delle notizie
def parse_news_item(item):
    """
    Decodifica e costruisce la struttura di una singola notizia adattata al nuovo schema del database.
    """
    return {
        # Campi da salvare in meta_articoli
        "img_url": item.get("metadata", {}).get("image", ""),
        "cryptopanic_url": item.get("url", "URL non disponibile"),
        "original_url": "",  # Sarà popolato successivamente dallo scraping
        "data": datetime.strptime(item.get("published_at", "1970-01-01T00:00:00Z"), "%Y-%m-%dT%H:%M:%SZ").strftime("%Y/%m/%d"),
        "negativo": item.get("votes", {}).get("negative", 0),
        "positivo": item.get("votes", {}).get("positive", 0),
        "importante": item.get("votes", {}).get("important", 0),
        "categoria": None,  # La categoria sarà assegnata manualmente
        "url_scraped": False,  # Inizialmente non è stato fatto lo scraping
        "html_scraped": False,  # Inizialmente non è stato fatto lo scraping
        "esiste_descrizione": None,  # Da aggiornare dopo lo scraping

        # Campi da salvare in descrizione_articoli
        "titolo": html.unescape(item.get("title", "Titolo non disponibile")),
        "full_article_html": None,  # Sarà popolato successivamente dallo scraping
        "short_resume": None,  # Conterrà un breve riasssunto generato dall' AI
        "long_resume": None  # Conterrà un lungo riassunto generato dall' AI
    }



#recupera le news finchè non trova una news già inserita
def fetch_news_until_existing():
    """
    Recupera le nuove notizie fino a trovare una già presente nel database.
    - Recupera una pagina alla volta, fino a un massimo di 10.
    - Confronta ogni notizia con la data e il titolo delle ultime 3 notizie nel database.
    - Se trova una notizia con stessa data e titolo, interrompe il recupero e restituisce le nuove notizie.

    Returns:
        int: Numero di nuove notizie salvate nel database.
    """
    # Recupera le ultime 3 notizie con data e titolo dal database
    recent_news = database.get_last_three_news()

    if not recent_news:
        print(" Nessuna notizia presente nel database. Inizializzarlo!")
        return 0

    print("\n Ultime 3 notizie nel database:")
    for data, titolo in recent_news:
        print(f"- {data}: {titolo}")

    all_news = []
    
    for page in range(1, 11):  # Scansiona dalla pagina 1 alla 10
        raw_news = fetch_page(page)  # Recupera e formatta la pagina

        if not raw_news:
            print(f" Pagina {page}: nessuna notizia trovata.")
            break

        print(f" Pagina {page} recuperata con successo.")

        for news in raw_news:
            # Controlla se la notizia è già presente nel database
            for db_data, db_titolo in recent_news:
                if news["data"] == db_data and news["titolo"] == db_titolo:
                    print(f" Notizia già presente: '{news['titolo']}'. Interruzione del recupero.")
                    all_news.reverse() 
                    saved_count = database.save_news_to_db(all_news)
                    print(f"{saved_count} nuove notizie salvate nel database.")
                    return 0

            all_news.append(news)
        
    all_news.reverse() 
    saved_count = database.save_news_to_db(all_news)
    print(f"{saved_count} nuove notizie salvate nel database.")







