import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt
from urllib.error import URLError
from textblob import TextBlob  # Fitur baru untuk analisis sentimen input teks

# Judul
st.title("Analisis Sentimen World of Airports")

# Adaptasi template: Fungsi untuk load data
@st.cache_data
def get_review_data() -> pd.DataFrame:
    df = pd.read_csv('hasil_scrapping_WOA.csv')
    df['at'] = pd.to_datetime(df['at'])
    return df.set_index("sentiment")

try:
    df = get_review_data()

    sentiments = st.multiselect(
        "Pilih Sentimen", list(df.index.unique()), ["positif", "netral"]
    )
    if not sentiments:
        st.error("Pilih setidaknya satu sentimen.")
    else:
        data = df.loc[sentiments]

        st.subheader("Data Ulasan Berdasarkan Sentimen")
        st.dataframe(data.sort_index())

        data_reset = data.reset_index()
        data_chart = data_reset[['at', 'score', 'sentiment']].copy()
        data_chart['at'] = data_chart['at'].dt.year
        data_chart = data_chart.groupby(['at', 'sentiment'])['score'].mean().reset_index()

        chart = (
            alt.Chart(data_chart)
            .mark_area(opacity=0.3)
            .encode(
                x="at:O",
                y=alt.Y("score:Q", stack=None),
                color="sentiment:N",
            )
        )
        st.altair_chart(chart, use_container_width=True)

except URLError as e:
    st.error(f"Error koneksi: {e.reason}")
except FileNotFoundError:
    st.error("File CSV tidak ditemukan. Pastikan path benar.")

# Distribusi Skor
st.header("Distribusi Skor Ulasan")
fig, ax = plt.subplots()
df.reset_index()['score'].value_counts().sort_index().plot(kind='bar', ax=ax)
ax.set_xlabel('Skor')
ax.set_ylabel('Jumlah')
st.pyplot(fig)

# Distribusi Sentimen
st.header("Distribusi Sentimen")
fig2, ax2 = plt.subplots()
df.reset_index()['sentiment'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax2)
ax2.set_ylabel('')
st.pyplot(fig2)

# Statistik Dasar
df_reset = df.reset_index()
st.header("Statistik Dasar")
st.write(f"Jumlah Ulasan: {len(df_reset)}")
st.write(f"Rata-rata Skor: {df_reset['score'].mean():.2f}")
st.write(f"Sentimen Terbanyak: {df_reset['sentiment'].mode()[0]}")

# ---------------------------
# FITUR BARU: INPUT TEKS & HASIL SENTIMEN
# ---------------------------
st.header("Analisis Sentimen dari Input Teks")
user_text = st.text_area("Masukkan kalimat ulasan:")

if st.button("Analisis Sentimen"):
    if user_text.strip() == "":
        st.warning("Masukkan teks terlebih dahulu.")
    else:
        blob = TextBlob(user_text)
        polarity = blob.sentiment.polarity

        if polarity > 0:
            hasil = "positif"
        elif polarity < 0:
            hasil = "negatif"
        else:
            hasil = "netral"

        st.subheader("Hasil Analisis:")
        st.write(f"Sentimen: **{hasil}**")
        st.write(f"Nilai polaritas: {polarity:.3f}")
