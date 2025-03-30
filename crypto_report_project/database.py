import sqlite3
import config

#funzione per la creazione del database
def create_database():
    
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()

    # Creazione della tabella per i metadati degli articoli
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meta_articoli (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        img_url VARCHAR(512),
        cryptopanic_url VARCHAR(512),
        original_url VARCHAR(512) DEFAULT '',
        data DATE NOT NULL,
        negativo INT DEFAULT 0,
        positivo INT DEFAULT 0,
        importante INT DEFAULT 0,
        categoria VARCHAR(100),
        url_scraped BOOLEAN DEFAULT FALSE,
        html_scraped BOOLEAN DEFAULT FALSE,    
        esiste_descrizione BOOLEAN DEFAULT NULL
    );
    """)

    # Creazione della tabella per le descrizioni complete (contenuto estratto via web scraping o AI)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS descrizione_articoli (
        id_articolo INTEGER PRIMARY KEY,
        titolo VARCHAR(512),
        short_descrizione VARCHAR(512),
        full_article_html TEXT,  
        short_resume_html TEXT,
        long_resume_html TEXT,
        FOREIGN KEY (id_articolo) REFERENCES articoli_meta(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()



#funzione per salvare le news nel db
def save_news_to_db(news_list):
    """
    Salva le notizie recuperate nel database nelle tabelle `meta_articoli` e `descrizione_articoli`.
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    inserted_count = 0

    for news in news_list:
        try:
            # Inserisce i metadati in meta_articoli
            cursor.execute("""
            INSERT INTO meta_articoli 
            (img_url, cryptopanic_url, original_url, data, negativo, positivo, importante, categoria, url_scraped, html_scraped, esiste_descrizione)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                news["img_url"],
                news["cryptopanic_url"],
                news["original_url"],
                news["data"],
                news["negativo"],
                news["positivo"],
                news["importante"],
                news["categoria"],
                news["url_scraped"],
                news["html_scraped"],
                news["esiste_descrizione"],
            ))

            # Recupera l'ID generato
            article_id = cursor.lastrowid

            # Inserisce la descrizione nella tabella descrizione_articoli
            cursor.execute("""
            INSERT INTO descrizione_articoli (id_articolo, titolo, full_article_html, short_resume, long_resume)
            VALUES (?, ?, ?, ?, ?)
            """, (
                article_id,
                news["titolo"],
                news["full_article_html"],
                news["short_resume"],
                news["long_resume"]
            ))

            inserted_count += 1

        except Exception as e:
            print(f" Errore durante l'inserimento dell'articolo '{news['titolo']}': {e}")

    conn.commit()
    conn.close()
    return inserted_count



def get_last_three_news():
    """
    Recupera le date e i titoli delle ultime 3 notizie con ID più alto dal database.
    Ora i dati vengono presi dalla nuova struttura `meta_articoli` e `descrizione_articoli`.

    Returns:
        list: Lista di tuple [(data1, titolo1), (data2, titolo2), (data3, titolo3)]
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()

    # Recupera le date e i titoli delle ultime 3 notizie con ID più alto
    cursor.execute("""
        SELECT m.data, d.titolo 
        FROM meta_articoli AS m
        JOIN descrizione_articoli AS d ON m.id = d.id_articolo
        ORDER BY m.id DESC
        LIMIT 3
    """)

    recent_news_rows = cursor.fetchall()  # Lista di tuple [(data1, titolo1), (data2, titolo2), (data3, titolo3)]

    conn.close()
    return recent_news_rows





def get_articles_without_original_url():
    """
    Recupera gli articoli dalla tabella `meta_articoli` che non hanno ancora un `original_url`
    e che non sono stati ancora processati (`url_scraped = FALSE`).

    Returns:
        list: Lista di tuple contenenti (id, cryptopanic_url).
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, cryptopanic_url 
            FROM meta_articoli 
            WHERE original_url = '' AND url_scraped = FALSE
        """)
        
        articles = cursor.fetchall()  # Restituisce una lista di tuple (id, cryptopanic_url)
        return articles

    except sqlite3.Error as e:
        print(f" Errore durante il recupero degli articoli senza original_url: {e}")
        return []

    finally:
        conn.close()



def update_original_url(article_id, original_url):
    """
    Aggiorna il campo `original_url` di un articolo nella tabella `meta_articoli`.

    Args:
        article_id (int): ID dell'articolo.
        original_url (str): URL originale estratto da CryptoPanic.
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE meta_articoli
            SET original_url = ?
            WHERE id = ?
        """, (original_url, article_id))

        conn.commit()
        print(f"URL originale aggiornato per l'articolo ID {article_id}.")

    except sqlite3.Error as e:
        print(f" Errore durante l'aggiornamento di original_url per l'articolo ID {article_id}: {e}")

    finally:
        conn.close()



def mark_url_scraped(article_id):
    """
    Imposta il campo `url_scraped` a TRUE per un articolo, segnalando che l'URL è stato processato.

    Args:
        article_id (int): ID dell'articolo.
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE meta_articoli
            SET url_scraped = TRUE
            WHERE id = ?
        """, (article_id,))

        conn.commit()
        print(f" Articolo ID {article_id} segnato come `url_scraped = TRUE`.")

    except sqlite3.Error as e:
        print(f" Errore durante l'aggiornamento di url_scraped per l'articolo ID {article_id}: {e}")

    finally:
        conn.close()




#recupera gli articoli per cui è presente l'url ma non è stata ancora recuperata la pagina html
def get_articles_without_html():
    """
    Recupera gli ID e gli original_url degli articoli che non hanno ancora un codice HTML salvato.
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, original_url FROM meta_articoli 
    WHERE html_scraped = FALSE AND original_url IS NOT NULL AND original_url != ''
    """)

    articles = cursor.fetchall()  # Lista di tuple [(id1, original_url1), (id2, original_url2), ...]
    conn.close()
    
    return articles


# Query per selezionare gli articoli da riassumere
def get_articles_to_summarize():
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_articolo, full_article_html 
        FROM descrizione_articoli
        WHERE resume_generated = 0 
        AND full_article_html IS NOT NULL
        AND full_article_html != ""
    """)

    articles = cursor.fetchall()  # Lista di tuple [(id1, original_url1), (id2, original_url2), ...]
    conn.close()
    
    return articles


# Query per salvare i riassunti
def save_article_summary(id_articolo,short_summary,long_summary):
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE descrizione_articoli 
        SET short_resume = ?, long_resume = ?, resume_generated = TRUE 
        WHERE id_articolo = ?
        """, (short_summary, long_summary, id_articolo))
    
    conn.commit()
    conn.close()

# Query per segnare comunuque l'articolo come processato
def mark_article_as_processed(id_articolo):
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE descrizione_articoli 
        SET resume_generated = TRUE 
        WHERE id_articolo = ?
        """, (id_articolo))
    
    conn.commit()
    conn.close()
    














