import streamlit as st
import pandas as pd
import numpy as np
import statsmodels.api as sm
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Setări inițiale
st.set_page_config(page_title="Regresie Multiplă", layout="wide")
st.title("📊 Model de Regresie Multiplă folosind Statsmodels")
st.markdown("""
Această aplicație construiește un model de regresie multiplă pentru a prezice succesul pieselor muzicale pe baza diferitelor caracteristici.
""")

# Încarcă fișierul CSV
csv_path = "data/data_with_encoding.csv"
try:
    df = pd.read_csv(csv_path)
    st.success("Fișierul a fost încărcat cu succes!")
except FileNotFoundError:
    st.error(f"Fișierul '{csv_path}' nu a fost găsit. Verifică dacă calea este corectă.")
    st.stop()

# Funcție pentru a categoriza succesul piesei în funcție de numărul de streamuri
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

# Categorizarea succesului piesei
df['success_category'] = df['streams'].apply(categorize_streams)

# Encoding etichete
label_encoder = LabelEncoder()
df['success_label'] = label_encoder.fit_transform(df['success_category'])

df_numeric = df.drop(columns=['track_name']).select_dtypes(include=[np.number])
correlation_matrix = df_numeric.corr()
st.subheader("📈 Matrice de corelație")
st.write(correlation_matrix)

df = df.dropna()

# Selectează caracteristicile pentru modelul de regresie multiplă
feature_cols = [
    'bpm', 'key_encoded', 'mode_encoded', 'danceability_%', 'valence_%',
    'energy_%', 'acousticness_%', 'liveness_%', 'speechiness_%',
    'in_spotify_playlists', 'in_spotify_charts',
    'in_apple_playlists', 'in_apple_charts',
    'in_deezer_playlists', 'in_deezer_charts',
    'in_shazam_charts', 'genre_freq_encoded', 'country_list_encoded',
    'released_month', 'released_year', 'released_day', 'artist_count'
]

# Verificare dacă există coloană lipsă
missing_cols = [col for col in feature_cols if col not in df.columns]
if missing_cols:
    st.error(f"Coloanele lipsă: {missing_cols}")
    st.stop()

X = df[feature_cols]
y = df['streams']  # folosim 'streams' pentru succesul piesei

# Scalează datele
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Împărțirea datelor în seturi de train și test
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

# Adaugă o coloană de intercept (constantă) pentru regresia multiplă
X_train_sm = sm.add_constant(X_train)
X_test_sm = sm.add_constant(X_test)

# Creează modelul de regresie multiplă
model = sm.OLS(y_train, X_train_sm).fit()

# Afișează sumarul modelului
st.subheader("📊 Rezultatele modelului de regresie multiplă")
st.write(model.summary())

# Prezice pe setul de test
y_pred = model.predict(X_test_sm)

# Vizualizare rezultatelor: Prețul prezis vs. Prețul real
st.subheader("📈 Compararea valorilor prezise cu cele reale")
fig, ax = plt.subplots(figsize=(7, 5))
ax.scatter(y_test, y_pred)
ax.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='red', lw=2)  # Linie diagonală
ax.set_xlabel('Real Stream Values')
ax.set_ylabel('Predicted Stream Values')
ax.set_title('Comparația valorilor reale cu cele prezise')
st.pyplot(fig)

# Calcularea erorii medii absolute (MAE)
mae = np.mean(np.abs(y_test - y_pred))
st.write(f"💡 Erroare Medie Absolută (MAE): {mae:.2f}")

# Vizualizarea distribuției reziduurilor
residuals = y_test - y_pred
fig, ax = plt.subplots(figsize=(12, 5))
sns.histplot(residuals, kde=True, ax=ax, color='blue', bins=30)
ax.set_xlabel('Reziduuri')
ax.set_title('Distribuția Reziduurilor')
st.pyplot(fig)



st.subheader("📊 Corelațiile între variabilele explicative")
fig, ax = plt.subplots(figsize=(12, 5))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5, ax=ax)
st.pyplot(fig)

