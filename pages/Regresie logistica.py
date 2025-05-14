from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
import matplotlib.pyplot as plt
import seaborn as sns

# Setări inițiale
st.set_page_config(page_title="Prelucrări Statistice", layout="wide")
st.title("🎵Regresie logistica")
st.markdown("""
Această aplicație permite scalarea și clusterizarea pieselor muzicale folosind KMeans.
""")

# Încarcă direct fișierul CSV dintr-o cale fixă
csv_path = "data/data_with_encoding.csv"

try:
    df = pd.read_csv(csv_path)
    st.success("Fișierul a fost încărcat cu succes!")
except FileNotFoundError:
    st.error(f"Fișierul '{csv_path}' nu a fost găsit. Verifică dacă calea este corectă.")
    st.stop()

# Funcție de categorizare a succesului pe baza numărului de streamuri
def categorize_streams(value):
    if value >= 700_000_000:
        return "Very High"
    elif value >= 500_000_000:
        return "High"
    elif value >= 300_000_000:
        return "Mid"
    elif value >= 150_000_000:
        return "Low"
    else:
        return "Very Low"

df['success_category'] = df['streams'].apply(categorize_streams)

# Afișează distribuția categoriilor de succes
st.subheader("📊 Distribuția categoriilor de succes")
success_counts = df['success_category'].value_counts().sort_index()
st.bar_chart(success_counts)
st.write(success_counts)

# Encoder pentru etichete
label_encoder = LabelEncoder()
df['success_label'] = label_encoder.fit_transform(df['success_category'])

# Afișează corespondentele între categorii și etichete
label_map = dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_)))
st.write("Corespondență categorii → labeluri:", label_map)

# Selectezi feature-urile (X) și ținta (y)
feature_cols = [
    'bpm', 'key_encoded', 'mode_encoded', 'danceability_%', 'valence_%',
    'energy_%', 'acousticness_%', 'liveness_%', 'speechiness_%',
    'in_spotify_playlists', 'in_spotify_charts',
    'in_apple_playlists', 'in_apple_charts',
    'in_deezer_playlists', 'in_deezer_charts',
    'in_shazam_charts', 'genre_freq_encoded', 'country_list_encoded',
    'released_month', 'released_year', 'released_day', 'artist_count'
]

# Verificare că toate coloanele există
missing_cols = [col for col in feature_cols if col not in df.columns]
if missing_cols:
    st.error(f"Coloanele lipsă: {missing_cols}")
    st.stop()

X = df[feature_cols]
y = df['success_label']

# Scalează datele
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Împarte în train și test
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y)

# Antrenare model regresie logistică
model = LogisticRegression(multi_class='multinomial', solver='lbfgs', max_iter=1000)
model.fit(X_train, y_train)

# Predicții pe datele de test
y_pred = model.predict(X_test)

# Matricea de confuzie
st.subheader("📈 Matrice de Confuzie")
conf_matrix = confusion_matrix(y_test, y_pred)
st.write(conf_matrix)

# Vizualizarea matricei de confuzie cu ajutorul unui heatmap
fig, ax = plt.subplots(figsize=(7, 3))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap="Blues", xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_, ax=ax)
ax.set_title('Matricea de Confuzie')
ax.set_xlabel('Predicții')
ax.set_ylabel('Realitate')
st.pyplot(fig)

# Raport de clasificare
st.subheader("📋 Raport de clasificare")
report = classification_report(y_test, y_pred, target_names=label_encoder.classes_, output_dict=True)
st.dataframe(pd.DataFrame(report).transpose())

# Calcularea și afișarea curbei ROC și AUC
y_prob = model.predict_proba(X_test)
fpr, tpr, _ = roc_curve(y_test, y_prob[:, 1], pos_label=1)
roc_auc = auc(fpr, tpr)

st.subheader("📉 Curba ROC")
fig, ax = plt.subplots(figsize=(7,3))
ax.plot(fpr, tpr, color='orange', lw=2, label=f'Curba ROC (AUC = {roc_auc:.2f})')
ax.plot([0, 1], [0, 1], color='blue', lw=2, linestyle='--')  # Linia aleatorie
ax.set_xlabel('False Positive Rate (FPR)')
ax.set_ylabel('True Positive Rate (TPR)')
ax.set_title('Curba ROC')
ax.legend(loc='lower right')
st.pyplot(fig)

# Afișează acuratețea modelului
accuracy = model.score(X_test, y_test)
st.write(f"Acuratețea modelului: {accuracy:.2f}")

