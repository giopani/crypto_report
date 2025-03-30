import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import nltk
from nltk.corpus import stopwords
import numpy as np
import pickle

# Scaricare le stopwords italiane di NLTK (solo la prima volta)
# nltk.download('stopwords')
italian_stopwords = stopwords.words('italian')

# Caricare il dataset etichettato
file_path = 'summary_categorized.csv'
df = pd.read_csv(file_path)

# Rimuovere eventuali righe con valori mancanti
df = df.dropna(subset=['long_resume', 'category'])

# Convertire il testo in numeri con TF-IDF
vectorizer = TfidfVectorizer(stop_words=italian_stopwords, max_features=5000)
X_tfidf = vectorizer.fit_transform(df['long_resume'])
y = df['category']

# Suddividere i dati in training e test set (80% - 20%)
X_train, X_test, y_train, y_test = train_test_split(X_tfidf, y, test_size=0.2, random_state=42)

# Inizializzare e addestrare il modello Naive Bayes
model = MultinomialNB(alpha=0.1)  # Regolazione del parametro alpha per Laplace Smoothing()
model.fit(X_train, y_train)

# Prevedere le categorie sul set di test
y_pred = model.predict(X_test)

# Valutare il modello
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuratezza del modello: {accuracy:.2f}")

# Stampare il classification report
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Stampare la matrice di confusione
conf_matrix = confusion_matrix(y_test, y_pred)
labels = sorted(df['category'].unique())  # Ordinare i nomi delle classi

# Normalizzare la matrice per mostrare le proporzioni
conf_matrix_norm = conf_matrix.astype('float') / conf_matrix.sum(axis=1)[:, np.newaxis]

# Plot della matrice di confusione
plt.figure(figsize=(14, 10))  # Aumenta la dimensione della figura
sns.heatmap(conf_matrix_norm, annot=True, cmap='Blues', fmt='.2%', xticklabels=labels, yticklabels=labels)
plt.xticks(rotation=45, ha='right', fontsize=10)  # Ruota le etichette e riduce il testo
plt.yticks(fontsize=10)  # Riduce il testo delle etichette Y
plt.title('Matrice di Confusione Normalizzata (Proporzioni %)')
plt.xlabel('Previsioni')
plt.ylabel('Vero Valore')
plt.tight_layout()  # Per garantire che tutto rientri nel grafico
plt.show()

# Salvare il modello e il vettorizzatore
with open('modello_naive_bayes.pkl', 'wb') as model_file:
    pickle.dump(model, model_file)

with open('vectorizer_tfidf.pkl', 'wb') as vectorizer_file:
    pickle.dump(vectorizer, vectorizer_file)

print('Modello e vettorizzatore salvati correttamente.')
