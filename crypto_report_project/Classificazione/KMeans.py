import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from kneed import KneeLocator
import nltk
from nltk.corpus import stopwords

# Scaricare le stopwords italiane di NLTK (solo la prima volta)
#nltk.download('stopwords')
italian_stopwords = stopwords.words('italian')

# Caricare il dataset
file_path = "Dataset/dataset_KMeans.csv"
df = pd.read_csv(file_path)

# Rimuovere eventuali righe con valori mancanti in 'long_resume'
df = df.dropna(subset=['long_resume'])

# Convertire il testo in numeri con TF-IDF
vectorizer = TfidfVectorizer(stop_words=italian_stopwords, max_features=5000)
X_tfidf = vectorizer.fit_transform(df['long_resume'])

# Determinare il numero ottimale di cluster usando la curva del gomito
inertia_values = []
clusters_range = range(1, 11)

for k in clusters_range:
    kmeans = KMeans(n_clusters=k, n_init=5, init='random', random_state=42)
    kmeans.fit(X_tfidf)
    inertia_values.append(kmeans.inertia_)

# Identificare il "gomito" nella curva
knee_locator = KneeLocator(clusters_range, inertia_values, curve="convex", direction="decreasing")
optimal_clusters = knee_locator.elbow

# Plottare la curva del gomito
plt.figure(figsize=(8, 5))
plt.plot(clusters_range, inertia_values, marker='o', linestyle='--')
plt.xlabel("Numero di cluster")
plt.ylabel("Inertia")
plt.title("Curva del Gomito per determinare il numero di cluster ottimale")
plt.axvline(optimal_clusters, color='r', linestyle='--')
plt.show()

# Eseguire K-Means con il numero ottimale di cluster
kmeans = KMeans(n_clusters=optimal_clusters, n_init=5, init='random', random_state=42)
df['categoria'] = kmeans.fit_predict(X_tfidf)

# Salvare il dataset aggiornato
output_file = "../Dataset/dataset_KMeans_classificato.csv"
df.to_csv(output_file, index=False)

print(f"Dataset classificato salvato in {output_file}")

