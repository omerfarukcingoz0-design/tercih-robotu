import pandas as pd
import streamlit as st

# Sayfa Başlığı
st.set_page_config(page_title="Benim Tercih Robotum", layout="wide")


# 1. Excel/CSV Verisini Oku
@st.cache_data
def veri_al():
    return pd.read_csv("universiteler.csv")


try:
    df = veri_al()
except:
    st.error(
        "Klasörde 'universiteler.csv' dosyası bulunamadı! Lütfen kontrol et."
    )
    st.stop()


# 2. Gelme İhtimalini Hesaplayan Mantık
def ihtimal_hesapla(senin_siralamandi, bolum_siralamasi):
    fark = senin_siralamandi - bolum_siralamasi

    if fark <= -15000:
        return "🟢 Çok Yüksek (Garanti gibi)"
    elif -15000 < fark <= 0:
        return "🟢 Yüksek (Büyük ihtimal gelir)"
    elif 0 < fark <= 10000:
        return "🟡 Orta (Sınırda, riskli)"
    else:
        return "🔴 Düşük (Zor / Sürpriz)"


# 3. Sol Taraf (Filtre Paneli)
st.sidebar.header("⚙️ Filtreler")

senin_siralaman = st.sidebar.number_input(
    "YKS Sıralamanı Gir:", min_value=1, value=50000
)
secilen_puan = st.sidebar.selectbox(
    "Puan Türü:", ["Tümü"] + list(df["Puan_Türü"].unique())
)
secilen_sehir = st.sidebar.multiselect("Şehir:", df["Şehir"].unique())
arama = st.sidebar.text_input("Bölüm veya Üniversite Ara:", value="")

# 4. Filtreleme İşlemi
sonuc_df = df.copy()

if secilen_puan != "Tümü":
    sonuc_df = sonuc_df[sonuc_df["Puan_Türü"] == secilen_puan]

if secilen_sehir:
    sonuc_df = sonuc_df[sonuc_df["Şehir"].isin(secilen_sehir)]

if arama:
    sonuc_df = sonuc_df[
        sonuc_df["Üniversite"].str.contains(arama, case=False)
        | sonuc_df["Bölüm"].str.contains(arama, case=False)
    ]

# 5. Hesaplama Sonuçlarını Ekle
ihtimaller = []
for index, satir in sonuc_df.iterrows():
    durum = ihtimal_hesapla(senin_siralaman, satir["Sıralama_2025"])
    ihtimaller.append(durum)

sonuc_df["Gelme İhtimali"] = ihtimaller

# 6. Ekrana Bas
st.title("🎓 Benim Özel YKS Tercih Robotum")
st.write(f"**Girilen Sıralama:** {senin_siralaman:,}")

st.dataframe(
    sonuc_df[
        [
            "Gelme İhtimali",
            "Üniversite",
            "Bölüm",
            "Şehir",
            "Burs",
            "Sıralama_2025",
        ]
    ],
    use_container_width=True,
)