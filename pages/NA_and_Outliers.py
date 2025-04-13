import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from pages.Vizualizari import convert_numeric_columns, afiseaza_info_df

st.set_page_config(page_title="NA_Outliers", layout="wide")
st.title("Tratarea valorilor lipsă și a outlierilor")

df = pd.read_csv("data/spotify-2023-updated.csv", encoding="ISO-8859-1")
df.columns = df.columns.str.strip()
convert_numeric_columns(df)
# afiseaza_info_df(df)

# Codul tău cu tratarea NA + outlieri
st.subheader("Tratarea valorilor lipsă")

df_clean=df.copy()
missing_vals = df_clean.isnull().sum()
missing_percent = (missing_vals / len(df_clean)) * 100
missing_df = pd.DataFrame({
    'Missing Values': missing_vals,
    'Percentage': missing_percent
})
missing_df = missing_df[missing_df['Missing Values'] > 0].sort_values('Percentage', ascending=False)

plt.figure(figsize=(7, 2))
missing_df['Percentage'].plot(kind='barh', color='blue')
plt.title('Procentul valorilor lipsă per coloană')
plt.xlabel('Procent (%)')
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()

st.table(missing_df)
st.pyplot(plt)

def fill_na_object(df, column_name):
    """
    Completăm valorile lipsă dintr-o coloană cu valoarea modului (cea mai frecventă valoare)
    pentru coloane de tip categoric.
    """
    if df[column_name].isnull().sum() > 0:
        mode_value = df[column_name].mode()[0]  # Obținem valoarea modului
        df[column_name] = df[column_name].fillna(mode_value)
        print(f"Coloana '{column_name}' a fost completată cu moda: {mode_value}")
    return df

def fill_na_numeric(df, column_name):
    """
    Conversie a unei coloane care poate fi de tip object sau alt tip într-un tip numeric (de exemplu, int sau float),
    și completarea valorilor lipsă cu mediana.
    """
    # Conversia coloanei într-un tip numeric, tratând valorile care nu pot fi convertite
    df[column_name] = pd.to_numeric(df[column_name], errors='coerce')

    # Verificăm dacă există valori lipsă și le completăm cu mediana
    if df[column_name].isnull().sum() > 0:
        median_value = df[column_name].median()  # Obținem mediana
        df[column_name] = df[column_name].fillna(median_value)
        print(f"Coloana '{column_name}' a fost completată cu mediana: {median_value}")
    return df

df_clean = fill_na_object(df_clean, 'key')
df_clean = fill_na_numeric(df_clean, 'in_shazam_charts')


# Afișează numărul de valori lipsă după completare
missing_after = df_clean[['key', 'in_shazam_charts']].isnull().sum().reset_index()
missing_after.columns = ['Coloana', 'Valori lipsă după']
st.table(missing_after)


# 2. Analiza distribuției datelor pentru variabilele numerice
st.subheader("Analiza distribuției datelor pentru variabile numerice")

numerical_cols = df_clean.select_dtypes(include=[np.number]).columns
n_cols = 3
n_rows = len(numerical_cols) // n_cols + (len(numerical_cols) % n_cols > 0)


# Funcția pentru a vizualiza histograma și a decide care coloane au outlieri
def display_histograms_and_select_outliers(df):
    outlier_columns = []
    st.subheader("Distribuția variabilelor numerice (Histograme)")
    plt.figure(figsize=(6 * n_cols, 4 * n_rows))
    for i, col in enumerate(numerical_cols):
        plt.subplot(n_rows, n_cols, i + 1)
        plt.hist(df[col].dropna(), bins=30, edgecolor='black', color='skyblue')
        plt.title(f'Distribuția: {col}')
        plt.xlabel(col)
        plt.ylabel('Frecvență')
        if df_clean[col].skew() > 1:  # Poți ajusta acest prag
            outlier_columns.append(col)
    plt.subplots_adjust(hspace=0.5, wspace=0.3)  # hspace: distanța verticală, wspace: distanța orizontală
    st.pyplot(plt)
    plt.close()
    return outlier_columns

outlier_columns = display_histograms_and_select_outliers(df)

if outlier_columns:
    st.write("Următoarele coloane au fost identificate ca având outlieri și vor fi curățate:")
    st.table(outlier_columns)
else:
    st.write("Nu s-au identificat outlieri evidenți în variabilele numerice.")


# 3. Density Plots pentru variabilele numerice
st.subheader("Density Plots pentru variabile numerice")

plt.figure(figsize=(6 * n_cols, 4 * n_rows))
for i, col in enumerate(numerical_cols):
    plt.subplot(n_rows, n_cols, i + 1)
    sns.kdeplot(df_clean[col].dropna(), shade=True, color='orange')
    plt.title(f'Distribuția (Density Plot): {col}')
    plt.xlabel(col)
    plt.ylabel('Frecvență')

plt.tight_layout()
st.pyplot(plt)

st.write("Vom elimina coloana `instrumentalness` din analiza.")
if 'instrumentalness_%' in df_clean.columns:
    df_clean = df_clean.drop(columns=['instrumentalness_%'])
    st.write("Coloana 'instrumentalness_%' a fost eliminată din analiza.")
else:
    st.write("Coloana 'instrumentalness_%' nu există în setul de date, nu a fost eliminată.")

st.write("""
      **Concluzii din analiza distribuțiilor:**
      - După analizarea density plots pentru variabilele numerice, nu am observat variabile care să prezinte distribuții cu mai multe vârfuri semnificative (distribuții multimodale).
      - Distribuțiile pentru majoritatea variabilelor sunt unimodale, ceea ce sugerează că nu există segmente de date foarte diferite.
      - În general, nu am identificat variabile cu diferențe semnificative între grupuri (cum ar fi melodiile de lux versus cele accesibile).
      - Distribuțiile nu sunt extrem de asimetrice (fără capete foarte lungi), ceea ce sugerează că nu este necesar să aplicăm transformări logaritmice pentru a gestiona outlieri puternici.""")


# 7. Pair Plots (pentru o selecție mică de variabile numerice)
st.subheader("Pair Plots pentru variabile numerice")

# Alege variabile numerice relevante pentru pair plot
selected_numerical_cols = numerical_cols[:5]  # Selectează primele 5 coloane numerice pentru pair plot

sns.pairplot(df[selected_numerical_cols].dropna())
st.pyplot(plt)


# --- SECTIUNEA 4: Valori extreme (outlieri) ---
st.subheader(" Valori extreme (Outlieri)")

st.markdown("""
Outlierii sunt valori care se abat puternic de la restul datelor. Pot fi erori de introducere, dar uneori sunt pur și simplu excepții (ex: piese virale, artiști extrem de populari etc.). 
Mai jos folosim metoda IQR pentru a identifica valorile extreme.
""")

def find_outliers_iqr(df, col):
    Q1 = df[col].quantile(0.25)  # Calculăm Q1
    Q3 = df[col].quantile(0.75)  # Calculăm Q3
    IQR = Q3 - Q1  # Intervalul intercuartilic
    lower_bound = Q1 - 1.5 * IQR # Limita inferioară
    upper_bound = Q3 + 1.5 * IQR # Limita superioară
    outliers_df = df[(df[col] < lower_bound) | (df[col] > upper_bound)]  # Selectăm outlierii
    return lower_bound, upper_bound, outliers_df

# Coloane relevante pe care le-ai menționat
relevant_cols = [
    'artist_count',
    'in_spotify_playlists', 'in_spotify_charts', 'streams', 'in_apple_playlists', 'in_apple_charts',
    'in_deezer_playlists', 'in_deezer_charts', 'in_shazam_charts',
    'liveness_%', 'speechiness_%'
]



# Calculăm outlieri pentru fiecare coloană relevantă
for col in relevant_cols:
    if col in df_clean.columns:
        st.markdown(f"###  Coloana: `{col}`")

        # Detectare outlieri
        lower, upper, outliers = find_outliers_iqr(df_clean, col)
        st.write(f"🔹 Limita inferioară: `{lower:,.0f}`")
        st.write(f"🔹 Limita superioară: `{upper:,.0f}`")
        st.write(f"🔹 Număr de outlieri: `{len(outliers)}` din `{len(df_clean)}`")

        # Boxplot interactiv cu Plotly
        fig_box = px.box(df_clean, y=col)
        st.plotly_chart(fig_box, use_container_width=True)

        st.markdown("---")

st.write("""
### Tratare outliers -> Aplicarea Logaritmicii
Logaritmica este aplicată pe variabilele care prezintă o gamă largă de valori și outlieri semnificativi, care pot afecta modelele de machine learning sau analizele statistice. Această transformare ajută la reducerea asimetriilor și a influenței valorilor extreme asupra distribuției datelor.

#### Variabile pe care am aplicat logaritmica:
1. **streams**: Aceasta are o gamă largă de valori, inclusiv outlieri mari, care pot afecta performanța modelelor. Logaritmica ajută la reducerea impactului acestora.
2. **in_spotify_playlists**: Această variabilă are și ea outlieri semnificativi și valori mari, iar logaritmica o face mai uniform distribuită.
3. **in_deezer_playlists**: Similar cu `in_spotify_playlists`, aceasta prezintă o gamă largă de valori cu outlieri, iar logaritmica ajută la îmbunătățirea distribuției.
4. **in_shazam_charts**: Aceasta are un număr mare de outlieri, iar aplicarea logaritmicii ajută la normalizarea distribuției.

După aplicarea logaritmicii, distribuțiile acestor variabile vor fi mai echilibrate, iar influența valorilor extreme va fi redusă.
""")

# Aplicarea logaritmicii pe variabilele cu valori mari sau asimetrice
df['streams_log'] = np.log1p(df['streams'])  # Transformare logaritmică
df['in_spotify_playlists_log'] = np.log1p(df['in_spotify_playlists'])
df['in_deezer_playlists_log'] = np.log1p(df['in_deezer_playlists'])
df['in_shazam_charts_log'] = np.log1p(df['in_shazam_charts'])

fig, axes = plt.subplots(4, 2, figsize=(14, 12))

# Before and After for 'streams'
sns.histplot(df['streams'], kde=True, ax=axes[0, 0], color='blue')
axes[0, 0].set_title('Distribuția înainte de logaritmică: streams')

sns.histplot(df['streams_log'], kde=True, ax=axes[0, 1], color='orange')
axes[0, 1].set_title('Distribuția după logaritmică: streams')

# Before and After for 'in_spotify_playlists'
sns.histplot(df['in_spotify_playlists'], kde=True, ax=axes[1, 0], color='blue')
axes[1, 0].set_title('Distribuția înainte de logaritmică: in_spotify_playlists')

sns.histplot(df['in_spotify_playlists_log'], kde=True, ax=axes[1, 1], color='orange')
axes[1, 1].set_title('Distribuția după logaritmică: in_spotify_playlists')

# Before and After for 'in_deezer_playlists'
sns.histplot(df['in_deezer_playlists'], kde=True, ax=axes[2, 0], color='blue')
axes[2, 0].set_title('Distribuția înainte de logaritmică: in_deezer_playlists')

sns.histplot(df['in_deezer_playlists_log'], kde=True, ax=axes[2, 1], color='orange')
axes[2, 1].set_title('Distribuția după logaritmică: in_deezer_playlists')

# Before and After for 'in_shazam_charts'
sns.histplot(df['in_shazam_charts'], kde=True, ax=axes[3, 0], color='blue')
axes[3, 0].set_title('Distribuția înainte de logaritmică: in_shazam_charts')

sns.histplot(df['in_shazam_charts_log'], kde=True, ax=axes[3, 1], color='orange')
axes[3, 1].set_title('Distribuția după logaritmică: in_shazam_charts')

# Ajustăm aspectul pentru a nu se suprapune subgrafurile
plt.tight_layout()

# Afișăm figura
st.pyplot(fig)

output_file = "data/data_cleaned_spotify.csv"

# Crearea folderului 'data' dacă nu există deja
os.makedirs(os.path.dirname(output_file), exist_ok=True)

# Salvarea DataFrame-ului curat într-un fișier Excel
df_clean.to_csv(output_file, index=False)

numerical_cols = df_clean.select_dtypes(include=[np.number]).columns
corr_matrix = df_clean[numerical_cols].corr()

# Vizualizăm matricea de corelație cu un heatmap
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title("Matricea de corelație pentru variabilele numerice")
plt.tight_layout()
plt.show()

st.pyplot(plt)
