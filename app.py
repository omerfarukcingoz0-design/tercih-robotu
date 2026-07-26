import pandas as pd
import streamlit as st

# Sayfa Ayarları
st.set_page_config(
    page_title="Marco Asensio YKS Tercih Robotu", layout="wide"
)


# 1. Veri Yükleme
@st.cache_data
def veri_yukle():
    # YÖK Atlas Dataset
    df = pd.read_csv("tum_bolumler.csv")
    return df


try:
    df = veri_yukle()
except Exception as e:
    st.error(f"Veri yüklenirken hata oluştu: {e}")
    st.stop()

# 2. Gelme Olasılığı Algoritması
def olasilik_hesapla(ogrenci_sira, bolum_sira):
    try:
        bolum_sira = float(bolum_sira)
        if pd.isna(bolum_sira) or bolum_sira <= 0:
            return "🔴 Dolmadı / Veri Yok"
    except:
        return "🔴 Veri Yok"

    fark = ogrenci_sira - bolum_sira

    if fark <= -15000:
        return "🟢 Çok Yüksek (Garantiye Yakın)"
    elif -15000 < fark <= 0:
        return "🟢 Yüksek (Büyük İhtimal)"
    elif 0 < fark <= 10000:
        return "🟡 Orta / Riskli (Sınırda)"
    else:
        return "🔴 Düşük (Sürpriz / Zor)"


# 3. Sol Panel Filtreleri
st.sidebar.header("🎯 Tercih Filtreleri")

ogrenci_sira = st.sidebar.number_input(
    "YKS Sıralamanız:", min_value=1, value=50000, step=500
)

# Arama Metni
arama_metni = st.sidebar.text_input(
    "Üniversite veya Bölüm Ara:", placeholder="Örn: İşletme, Bilgisayar..."
)

# Dinamik Kolon Tespiti (Veri setindeki uygun sütunları bulur)
olasi_universite_col = [
    col
    for col in df.columns
    if "uni" in col.lower() or "üniversite" in col.lower()
]
olasi_bolum_col = [
    col
    for col in df.columns
    if "program" in col.lower() or "bölüm" in col.lower()
]
olasi_sira_col = [
    col
    for col in df.columns
    if "sıra" in col.lower() or "sira" in col.lower()
]

uni_col = olasi_universite_col[0] if olasi_universite_col else df.columns[0]
bolum_col = olasi_bolum_col[0] if olasi_bolum_col else df.columns[1]
sira_col = olasi_sira_col[0] if olasi_sira_col else df.columns[-1]

# Filtreleme
filtreli_df = df.copy()

if arama_metni:
    filtreli_df = filtreli_df[
        filtreli_df[uni_col]
        .astype(str)
        .str.contains(arama_metni, case=False, na=False)
        | filtreli_df[bolum_col]
        .astype(str)
        .str.contains(arama_metni, case=False, na=False)
    ]

# Olasılık Hesaplama
olasiliklar = []
for _, row in filtreli_df.iterrows():
    durum = olasilik_hesapla(ogrenci_sira, row[sira_col])
    olasiliklar.append(durum)

filtreli_df.insert(0, "Gelme İhtimali", olasiliklar)

# 4. Ana Ekran
st.title("🎓 YKS Tercih Robotu")
st.write(
    f"**Girilen Sıralama:** {ogrenci_sira:,} | **Bulunan Sonuç:** {len(filtreli_df)} Program"
)

# Tablo
st.dataframe(filtreli_df, use_container_width=True)
