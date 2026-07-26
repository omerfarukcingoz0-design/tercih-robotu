import pandas as pd
import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Marco Asensio | YKS Tercih Robotu",
    page_icon="🎓",
    layout="wide",
)

# Koyu Tema ve Modern Arayüz CSS
st.markdown(
    """
<style>
    .stApp {
        background-color: #0e1117;
    }
    .metric-box {
        background-color: #1e222d;
        padding: 12px 20px;
        border-radius: 10px;
        border: 1px solid #2e3440;
        text-align: center;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Veri Yükleme ve Sütun İsimlerini Otomatik Esnek Eşleme
@st.cache_data
def veri_yukle():
    df = pd.read_csv("tum_bolumler.csv")

    # Kolon İsimlerini Akıllıca Algıla
    renames = {}
    for col in df.columns:
        c = str(col).lower().strip()
        if any(x in c for x in ["uni", "üniversite", "universite"]):
            renames[col] = "Üniversite"
        elif any(x in c for x in ["isim", "program", "bölüm", "bolum"]):
            renames[col] = "Bölüm"
        elif any(x in c for x in ["sira", "sıra"]):
            renames[col] = "Sıralama"
        elif any(x in c for x in ["tur", "tür", "puan"]):
            renames[col] = "Puan_Türü"
        elif any(x in c for x in ["il", "sehir", "şehir"]):
            renames[col] = "Şehir"
        elif any(x in c for x in ["fakulte", "fakülte"]):
            renames[col] = "Fakülte"

    df = df.rename(columns=renames)
    return df


try:
    df = veri_yukle()
except Exception as e:
    st.error(
        f"Veri yükleme hatası! 'tum_bolumler.csv' dosyasını kontrol edin: {e}"
    )
    st.stop()


# Olasılık Algoritması
def olasilik_hesapla(ogrenci_sira, bolum_sira):
    try:
        bolum_sira = float(bolum_sira)
        if pd.isna(bolum_sira) or bolum_sira <= 0:
            return "🔴 Dolmadı / Veri Yok"
    except:
        return "🔴 Veri Yok"

    fark = ogrenci_sira - bolum_sira

    if fark <= -20000:
        return "🟢 Garantiye Yakın"
    elif -20000 < fark <= 0:
        return "🟢 Yüksek İhtimal"
    elif 0 < fark <= 15000:
        return "🟡 Orta / Sınırda"
    else:
        return "🔴 Düşük / Sürpriz"


# Tercih Listesi Oturum Hafızası
if "tercih_listesi" not in st.session_state:
    st.session_state.tercih_listesi = []

# --- SOL PANEL (FİLTRELER) ---
st.sidebar.title("🎯 Tercih Filtreleri")

ogrenci_sira = st.sidebar.number_input(
    "YKS Sıralamanız:", min_value=1, value=50000, step=1000
)

# Puan Türü Filtresi (Güvenli Kontrol)
puan_turleri = ["Tümü"]
if "Puan_Türü" in df.columns:
    puan_turleri += [
        str(x) for x in df["Puan_Türü"].dropna().unique() if str(x).strip() != ""
    ]
secilen_puan = st.sidebar.selectbox("Puan Türü:", puan_turleri)

# Şehir Filtresi (Güvenli Kontrol)
sehirler = []
if "Şehir" in df.columns:
    sehirler = [
        str(x) for x in df["Şehir"].dropna().unique() if str(x).strip() != ""
    ]
secilen_sehirler = st.sidebar.multiselect("Şehir Seçimi:", sehirler)

# İhtimal Filtresi
ihtimal_filtresi = st.sidebar.multiselect(
    "Gelme İhtimali:",
    [
        "🟢 Garantiye Yakın",
        "🟢 Yüksek İhtimal",
        "🟡 Orta / Sınırda",
        "🔴 Düşük / Sürpriz",
        "🔴 Dolmadı / Veri Yok",
    ],
    default=[
        "🟢 Garantiye Yakın",
        "🟢 Yüksek İhtimal",
        "🟡 Orta / Sınırda",
        "🔴 Düşük / Sürpriz",
    ],
)

# Arama Metni
arama_metni = st.sidebar.text_input(
    "🔍 Üniversite veya Bölüm Ara:", placeholder="Örn: Bilgisayar, Koç..."
)

# --- VERİ FİLTRELEME İŞLEMLERİ ---
filtreli_df = df.copy()

if "Puan_Türü" in filtreli_df.columns and secilen_puan != "Tümü":
    filtreli_df = filtreli_df[
        filtreli_df["Puan_Türü"].astype(str) == secilen_puan
    ]

if "Şehir" in filtreli_df.columns and secilen_sehirler:
    filtreli_df = filtreli_df[
        filtreli_df["Şehir"].astype(str).isin(secilen_sehirler)
    ]

if arama_metni:
    uni_mask = (
        filtreli_df["Üniversite"]
        .astype(str)
        .str.contains(arama_metni, case=False, na=False)
        if "Üniversite" in filtreli_df.columns
        else False
    )
    bolum_mask = (
        filtreli_df["Bölüm"]
        .astype(str)
        .str.contains(arama_metni, case=False, na=False)
        if "Bölüm" in filtreli_df.columns
        else False
    )
    filtreli_df = filtreli_df[uni_mask | bolum_mask]

# Olasılık Hesapla
sira_col = "Sıralama" if "Sıralama" in filtreli_df.columns else df.columns[-1]

olasiliklar = []
for _, row in filtreli_df.iterrows():
    durum = olasilik_hesapla(ogrenci_sira, row[sira_col])
    olasiliklar.append(durum)

filtreli_df.insert(0, "Gelme İhtimali", olasiliklar)

# İhtimal Filtresi Uygula
filtreli_df = filtreli_df[filtreli_df["Gelme İhtimali"].isin(ihtimal_filtresi)]

# --- ANA EKRAN ---
st.title("🎓 YKS Tercih & Analiz Robotu")

# Üst Gösterge Kutuları
c1, c2 = st.columns(2)
with c1:
    st.metric("Sıralamanız", f"{ogrenci_sira:,}")
with c2:
    st.metric("Bulunan Program Sayısı", f"{len(filtreli_df):,}")

# Tablo Listeleme
st.subheader("Üniversite ve Bölüm Sonuçları")

# Gösterilecek Temiz Kolonlar
kolonlar = [
    col
    for col in [
        "Gelme İhtimali",
        "Üniversite",
        "Fakülte",
        "Bölüm",
        "Puan_Türü",
        "Şehir",
        "Sıralama",
    ]
    if col in filtreli_df.columns
]

if len(kolonlar) < 2:
    kolonlar = filtreli_df.columns  # Ne olursa olsun göster

st.dataframe(filtreli_df[kolonlar], use_container_width=True, hide_index=True)
