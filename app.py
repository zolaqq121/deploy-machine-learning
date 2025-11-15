import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt  
from urllib.error import URLError  # Untuk error handling jika menggunakan URL

# Judul 
st.title("Analisis sentmen World of Airports")

# Adaptasi template: Fungsi untuk load data (dari template, tapi disesuaikan untuk CSV lokal)
@st.cache_data
def get_review_data() -> pd.DataFrame:
    # Asli template: Mengambil dari AWS S3
    # aws_bucket_url = "https://streamlit-demo-data.s3-us-west-2.amazonaws.com"
    # df = pd.read_csv(aws_bucket_url + "/agri.csv.gz")
    # return df.set_index("Region")
    
    # Adaptasi: Mengambil dari CSV lokal (sesuai aplikasi asli Anda)
    df = pd.read_csv('hasil_scrapping_WOA.csv')  # Ganti path jika perlu
    df['at'] = pd.to_datetime(df['at'])  # Konversi ke datetime
    # Set index berdasarkan sentimen untuk multiselect (mirip template)
    return df.set_index("sentiment")

try:
    df = get_review_data()
    
    # Adaptasi multiselect: Pilih sentimen (bukan negara)
    sentiments = st.multiselect(
        "Pilih Sentimen", list(df.index.unique()), ["positif", "netral"]  # Default pilih beberapa
    )
    if not sentiments:
        st.error("Pilih setidaknya satu sentimen.")
    else:
        data = df.loc[sentiments]
        
        # Tampilkan dataframe (mirip template)
        st.subheader("Data Ulasan Berdasarkan Sentimen")
        st.dataframe(data.sort_index())
        
        # Adaptasi chart: Visualisasi skor berdasarkan waktu (dari kolom 'at')
        # Reset index dan melt untuk chart (mirip template)
        data_reset = data.reset_index()
        data_chart = data_reset[['at', 'score', 'sentiment']].copy()
        data_chart['at'] = data_chart['at'].dt.year  # Ambil tahun dari tanggal
        data_chart = data_chart.groupby(['at', 'sentiment'])['score'].mean().reset_index()  # Rata-rata skor per tahun
        
        # Chart Altair (area chart, mirip template)
        chart = (
            alt.Chart(data_chart)
            .mark_area(opacity=0.3)
            .encode(
                x="at:O",  # Tahun sebagai ordinal
                y=alt.Y("score:Q", stack=None),  # Skor sebagai quantitative
                color="sentiment:N",  # Warna berdasarkan sentimen
            )
        )
        st.altair_chart(chart, use_container_width=True)

except URLError as e:
    st.error(f"Error koneksi: {e.reason}")  # Jika menggunakan URL S3
except FileNotFoundError:
    st.error("File CSV tidak ditemukan. Pastikan path benar.")

# Bagian asli aplikasi Anda tetap ada (distribusi skor, sentimen, dll.)
st.header("Distribusi Skor Ulasan")
fig, ax = plt.subplots()
df.reset_index()['score'].value_counts().sort_index().plot(kind='bar', ax=ax)
ax.set_xlabel('Skor')
ax.set_ylabel('Jumlah')
st.pyplot(fig)

st.header("Distribusi Sentimen")
fig2, ax2 = plt.subplots()
df.reset_index()['sentiment'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax2)
ax2.set_ylabel('')
st.pyplot(fig2)

st.header("Statistik Dasar")
df_reset = df.reset_index()
st.write(f"Jumlah Ulasan: {len(df_reset)}")
st.write(f"Rata-rata Skor: {df_reset['score'].mean():.2f}")
st.write(f"Sentimen Terbanyak: {df_reset['sentiment'].mode()[0]}")