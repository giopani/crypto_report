import fetchNews
import scraping
import summary
import Classificazione.classificazioneNB as classificazioneNB
import KnowledgeGraph_and_Prolog.generateKnowledgeBaseSettimanale
import KnowledgeGraph_and_Prolog.generateGraphSettimanale
import KnowledgeGraph_and_Prolog.queryProlog

#FUNZIONI PER INIZIALIZZAZIONE
#NON ESEGUIRE POICHE' DATABASE GIA' ESISTENTE
#database.create_database()
#fetchNews.fetch_news_in_range2(1,10)

#recupera il link cryptopanic dei nuovi articoli
fetchNews.fetch_news_until_existing()

#recupera l'url originale dell'articolo
scraping.get_original_urls()

#recupera il contenuto dell' articolo dall' url originale
scraping.fetch_and_store_html()

#riassume l'articolo (ricordarsi di modificare l'API con l'API generata da GoogleColab)
summary.summarize_articles()

#classfica i nuovi articoli estratti
classificazioneNB.classificaNewArticle()

#Creazione della Knwoledge Base e del Grafo ed esecuzione delle query
KnowledgeGraph_and_Prolog.generateKnowledgeBaseSettimanale.genera_kb_settimanale()
KnowledgeGraph_and_Prolog.generateGraphSettimanale.generate_graph_settimanale()
KnowledgeGraph_and_Prolog.queryProlog.execute_queryProlog()
