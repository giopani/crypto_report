import sqlite3
import time
import config
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import database
from bs4 import BeautifulSoup
import re
import cleanHtml
#from webdriver_manager.chrome import ChromeDriverManager



# Recupera l'URL originale di un singolo articolo
def get_original_url(cryptopanic_url):
    """
    Recupera l'URL originale della notizia dalla pagina di CryptoPanic.

    Args:
        cryptopanic_url (str): URL della notizia su CryptoPanic.

    Returns:
        str: URL originale dell'articolo, o None se non viene trovato.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Modalità headless per non aprire il browser
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver_path = r"C:\\Users\\gioel\\OneDrive\\TESI\\chromedriver.exe"
    service = Service(driver_path)
    
    # Massimo 3 tentativi per recuperare l'URL
    for attempt in range(3):
        driver = webdriver.Chrome(service=service, options=chrome_options)
        try:
            driver.get(cryptopanic_url)
            time.sleep(3)  # Attendere il caricamento della pagina

            try:
                # Trova il titolo dell'articolo e cliccaci sopra
                article_title = driver.find_element(By.XPATH, "//h1[contains(@class, 'post-title')]//span[contains(@class, 'text')]")
                print(f"Titolo dell'articolo: {article_title.text}")
                article_title.click()
                
                time.sleep(3)  # Attendi il caricamento della nuova pagina
                
                # Passa alla nuova scheda se aperta
                if len(driver.window_handles) > 1:
                    driver.switch_to.window(driver.window_handles[1])
                    time.sleep(3)  # Attendi il caricamento
                
                # Ottieni l'URL finale dell'articolo
                article_url = driver.current_url
            
            except Exception as e:
                article_url = f"Errore nel trovare o cliccare il link dell'articolo: {e}"
            
            driver.quit()
            return article_url

        except Exception as e:
            print(f"Errore durante l'estrazione dell'URL originale da {cryptopanic_url} (Tentativo {attempt+1}/3): {e}")
        
        finally:
            driver.quit()
        
        time.sleep(2)  # Attesa prima di riprovare

    return None  # Ritorna None se tutti i tentativi falliscono

# Ciclo per gestire il recupero di tutti gli original_url
def get_original_urls():
    """
    Recupera gli articoli non ancora processati (`original_url` vuoto e `url_scraped=FALSE`),
    estrae l'`original_url` da CryptoPanic e aggiorna il database.
    """
    articles = database.get_articles_without_original_url()

    if not articles:
        print(" Nessun articolo da processare. Il database è aggiornato.")
        return

    for article_id, cryptopanic_url in articles:
        print(f"\n Elaborazione articolo ID {article_id}...")

        original_url = get_original_url(cryptopanic_url)

        if original_url:
            print(f"RL originale trovato: {original_url}")
        else:
            print(f" Nessun URL trovato per {cryptopanic_url}. Impostato `url_scraped = TRUE`.")

        database.update_original_url(article_id, original_url) #segnala l'articolo come processato
        database.mark_url_scraped(article_id)
        time.sleep(1.5)  # Attende tra un articolo e l'altro per evitare blocchi

    print("\n Completato l'aggiornamento degli URL originali!")                                                        



# Funzione per recuperare l'HTML di una pagina con Selenium
def fetch_html_content(url):
    """
    Recupera il codice HTML di una pagina utilizzando Selenium.

    Args:
        url (str): L'URL della pagina da scaricare.

    Returns:
        str: Il codice HTML della pagina, oppure None in caso di errore.
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    #disabilitato rilevamento selenium
    #chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    #chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    #chrome_options.add_experimental_option("useAutomationExtension", False)


    driver_path = r"C:\Users\gioel\OneDrive\TESI\chromedriver.exe"
    service = Service(driver_path)
    #al poso delle due righe sopra mettere solo questa sotto
    #service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)

        # Attende che la pagina sia completamente caricata
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        html_content = driver.page_source
        return html_content

    except Exception as e:
        print(f"Errore durante lo scraping della pagina {url}: {e}")
        return None

    finally:
        driver.quit()  # Chiude il browser


# Funzione per scaricare HTML, estrarre il contenuto pulito e salvarlo nel database
def fetch_and_store_html():
    """
    Recupera gli articoli con original_url valorizzato, url_scraped=True e html_scraped=False,
    esegue lo scraping dell'intera pagina, estrae il testo utile e salva tutto nel database.
    """
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()

    # Seleziona gli articoli da processare
    cursor.execute("""
        SELECT id, original_url 
        FROM meta_articoli 
        WHERE original_url <> '' 
        AND url_scraped = TRUE 
        AND html_scraped = FALSE
    """)
    
    articles = cursor.fetchall()  # Lista di tuple [(id1, original_url1), (id2, original_url2), ...]

    if not articles:
        print("Nessun articolo da processare, il database è aggiornato.")
        conn.close()
        return

    for article_id, original_url in articles:
        print(f"\n Elaborazione articolo ID {article_id}...")

        # Recupera l'HTML della pagina
        html_content = fetch_html_content(original_url)

        if html_content:
            # Estrai il contenuto utile dai tag selezionati
            cleaned_html = cleanHtml.clean_html_content(html_content)

            try:
                # Salva **SOLO** l'HTML pulito nella colonna `html`, mentre `full_descrizione` rimane vuota
                cursor.execute("""
                    UPDATE descrizione_articoli
                    SET full_article_html = ?
                    WHERE id_articolo = ?
                """, (cleaned_html, article_id))

                # Segna l'articolo come `html_scraped = TRUE`
                cursor.execute("""
                    UPDATE meta_articoli
                    SET html_scraped = TRUE
                    WHERE id = ?
                """, (article_id,))

                conn.commit()  # Salva immediatamente ogni aggiornamento
                print(f" HTML pulito salvato per l'articolo ID {article_id}.")

            except Exception as e:
                print(f" Errore durante il salvataggio dell'HTML per l'articolo ID {article_id}: {e}")

        else:
            print(f" HTML non disponibile per l'articolo ID {article_id}.")

        # Attende per evitare problemi di rate-limiting
        time.sleep(2)

    conn.close()
    print("\n Completato il salvataggio degli HTML puliti!")
















