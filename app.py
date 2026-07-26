import pandas as pd
import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Marco Asensio | YKS Tercih Robotu",
    page_icon="🎓",
    layout="wide",
)

# Özel CSS ile Modern Görünüm ve Kart Tasarımları
st.markdown(
    """
<style>
    .stApp {
        background-color: #0e1117;
    }
    .metric-card {
        background-color: #1e222d;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2e3440;
        margin-bottom: 10px;
    }
    .badge-garanti { background-color: #10B981; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px; }
    .badge-yuksek { background-color: #059669; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px; }
    .badge-orta { background-color: #F59E0B; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px; }
    .badge-dusuk { background-color: #EF4444; color: white; padding: 4px 8px; border-radius: 6px; font-weight: bold; font-size: 12px; }
</style>
""",
    unsafe_allow_html=True,
)


# Veri Yükleme ve Ön İşleme
@st.cache_data
def veri_yukle():
    df = pd.read_csv("tum_bolumler.csv")

    # Kolon İsimlerini Düzenle ve Temizle
    col_map = {}
    for col in df.columns:
        c_lower = col.lower()
        if "uni" in c_lower or "üniversite" in c_lower:
            col_map[col] = "Üniversite"
        elif "isim" in c_lower or "program" in c_lower or "bölüm" in c_lower:
            col_map[col] = "Bölüm"
        elif "sira" in c_lower or "sıra" in c_lower:
            col_map[col] = "Sıralama"
        elif "tur" in c_lower or "tür" in c_lower or "puan" in c_lower:
            col_map[col] = "Puan_Türü"
        elif "il" in c_lower or "şehir" in c_lower:
            col_map[col] = "Şehir"
        elif "fakulte" in c_lower or "fakülte" in c_lower:
            col_map[col] = "Fakülte"

    df = df.rename(columns=col_map)
    return df


try:
    df = veri_yukle()
except Exception as e:
    st.error(
        f"Veri yüklenirken hata oluştu! 'tum_bolumler.csv' kontrol edilmeli: {e}"
    )
    st.stop()


# Olasılık Algoritması
def olasilik_detay(ogrenci_sira, bolum_sira):
    try:
        bolum_sira = float(bolum_sira)
        if pd.isna(bolum_sira) or bolum_sira <= 0:
            return "Veri Yok", "🔴", "badge-dusuk"
    except:
        return "Veri Yok", "🔴", "badge-dusuk"

    fark = ogrenci_sira - bolum_sira

    if fark <= -20000:
        return "Garantiye Yakın", "🟢", "badge-garanti"
    elif -20000 < fark <= 0:
        return "Yüksek İhtimal", "🟢", "badge-yuksek"
    elif 0 < fark <= 15000:
        return "Orta / Sınırda", "🟡", "badge-orta"
    else:
        return "Düşük / Sürpriz", "🔴", "badge-dusuk"


# Oturum Hafızası (Tercih Listesi İçin)
if "tercih_listesi" not in st.session_state:
    st.session_state.tercih_listesi = []

# --- SOL PANEL (GELİŞMİŞ FİLTRELER) ---
st.sidebar.title("🎯 Tercih Filtreleri")

ogrenci_sira = st.sidebar.number_input(
    "YKS Sıralamanız:", min_value=1, value=50000, step=1000
)

# Puan Türü Filtresi
puan_turleri = (
    ["Tümü"] + list(df["Puan_Türü"].dropna().unique())
    if "Puan_Türü" in df.columns
    else ["Tümü"]
)
secilen_puan = st.sidebar.selectbox("Puan Türü:", puan_turleri)

# Şehir Filtresi
sehirler = (
    list(df["Şehir"].dropna().unique()) if "Şehir" in df.columns else []
)
secilen_sehirler = st.sidebar.multiselect("Şehir Seçimi:", sehirler)

# Gelme İhtimali Filtresi
ihtimal_filtresi = st.sidebar.multiselect(
    "Gelme İhtimali:",
    ["Garantiye Yakın", "Yüksek İhtimal", "Orta / Sınırda", "Düşük / Sürpriz"],
    default=[
        "Garantiye Yakın",
        "Yüksek İhtimal",
        "Orta / Sınırda",
        "Düşük / Sürpriz",
    ],
)

# Arama Arama Metni
arama_metni = st.sidebar.text_input(
    "🔍 Üniversite / Bölüm Ara:", placeholder="Örn: Bilgisayar, Koç..."
)

# --- VERİ FİLTRELEME ---
filtreli_df = df.copy()

if "Puan_Türü" in filtreli_df.columns and secilen_puan != "Tümü":
    filtreli_df = filtreli_df[filtreli_df["Puan_Türü"] == secilen_puan]

if "Şehir" in filtreli_df.columns and secilen_sehirler:
    filtreli_df = filtreli_df[filtreli_df["Şehir"].isin(secilen_sehirler)]

if arama_metni:
    mask = filtreli_df["Üniversite"].astype(str).str.contains(
        arama_metni, case=False, na=False
    ) | filtreli_df["Bölüm"].astype(str).str.contains(
        arama_metni, case=False, na=False
    )
    filtreli_df = filtreli_df[mask]

# Olasılıkları Hesapla ve Ekle
ihtimaller = []
badgeler = []
simgeler = []

sira_col = "Sıralama" if "Sıralama" in filtreli_df.columns else df.columns[-1]

for _, row in filtreli_df.iterrows():
    durum, simge, badge = olasilik_detay(ogrenci_sira, row[sira_col])
    ihtimaller.append(durum)
    simgeler.append(simge)
    badgeler.append(badge)

filtreli_df["İhtimal"] = ihtimaller
filtreli_df["Simge"] = simgeler
filtreli_df["Badge"] = badgeler

# İhtimal Filtresini Uygula
filtreli_df = filtreli_df[filtreli_df["İhtimal"].isin(ihtimal_filtresi)]

# --- ANA EKRAN ---
st.title("🎓 YKS Tercih & Analiz Robotu")

# Üst Bilgi Kartları
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Girilen Sıralama", f"{ogrenci_sira:,}")
with col2:
    st.metric("Bulunan Program Sayısı", f"{len(filtreli_df):,}")
with col3:
    st.metric("Tercih Listenizdeki Bölüm", f"{len(st.session_state.tercih_listesi)}")

tab1, tab2 = st.tabs(["🏛️ Program Listesi", "📋 Tercih Listem"])

with tab1:
    st.subheader("Üniversite ve Bölüm Sonuçları")

    # Tablo Görünümü ve Liste Formatı Düzenleme
    gosterilecek_kolonlar = []
    for col in [
        "Simge",
        "İhtimal",
        "Üniversite",
        "Fakülte",
        "Bölüm",
        "Puan_Türü",
        "Şehir",
        "Sıralama",
    ]:
        if col in filtreli_df.columns:
            gosterilecek_kolonlar.append(col)

    # Temiz Streamlit Veri Tablosu
    st.dataframe(
        filtreli_df[gosterilecek_kolonlar],
        use_container_width=True,
        hide_index=True,
    )

with tab2:
    st.subheader("Seçtiğiniz Tercih Listesi")
    if len(st.session_state.tercih_listesi) == 0:
        st.info(
            "Henüz preference listenize bölüm eklemediniz. Program listesinden ekleme yapabilirsiniz."
        )
    else:
        tercih_df = pd.DataFrame(st.session_state.tercih_listesi)
        st.dataframe(tercih_df, use_container_width=True)
