import networkx as nx
from pyvis.network import Network
from pyswip import Prolog

def generate_graph_settimanale():
    # Inizializziamo Prolog
    prolog = Prolog()
    prolog.consult(r"knowledgeBaseSettimanale.pl")

    # Creiamo il grafo
    G = nx.DiGraph()

    # Colori per i nodi in base alla categoria
    node_colors = {
        'person': 'green',
        'crypto': 'orange',
        'financial_institution': 'red',
        'company': 'purple',
        'article': 'lightblue'
    }

    # Aggiungiamo nodi per le entità (People, Crypto, Financial Institutions, Companies)
    for entity_type, color in [('person', 'green'), ('crypto', 'orange'), 
                            ('financial_institution', 'red'), ('company', 'purple')]:
        query = list(prolog.query(f"{entity_type}(Entity)."))
        for result in query:
            entity = result['Entity']
            G.add_node(entity, label=entity, color=color)

    # Aggiungiamo relazioni Founder
    query = list(prolog.query("founder(Founder, Entity)."))
    for result in query:
        founder = result['Founder']
        entity = result['Entity']
        G.add_edge(founder, entity, label="Founder")

    # Aggiungiamo relazioni President
    query = list(prolog.query("president(President, Institution)."))
    for result in query:
        president = result['President']
        institution = result['Institution']
        G.add_edge(president, institution, label="President")

    # Aggiungiamo relazioni CEO
    query = list(prolog.query("ceo(CEO, Company)."))
    for result in query:
        ceo = result['CEO']
        company = result['Company']
        G.add_edge(ceo, company, label="CEO")

    # Aggiungiamo gli articoli e le loro menzioni
    query = list(prolog.query("article(ArticleID, Date)."))
    for result in query:
        article_id = result['ArticleID']
        G.add_node(article_id, label=str(article_id), color='lightblue')
        
        mention_query = list(prolog.query(f"mention({article_id}, Entity)."))
        for mention in mention_query:
            entity = mention['Entity']
            G.add_edge(article_id, entity, label="Mentions")

    # Visualizzazione con Pyvis
    net = Network(notebook=True, cdn_resources='in_line')
    net.from_nx(G)
    net.repulsion(node_distance=300, central_gravity=0.3, spring_length=100, spring_strength=0.05)
    net.show_buttons(filter_=['physics'])  # Aggiunge i controlli per modificare la fisica del grafo

    # Generazione dell'HTML del grafo
    html_content = net.generate_html()
    with open("knowledgeGraphSettimanale.html", "w", encoding="utf-8") as f:
        f.write(html_content)



