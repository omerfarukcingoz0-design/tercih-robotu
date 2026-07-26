import pandas as pd
import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Marco Asensio | YKS Tercih Robotu",
    page_icon="🎓",
    layout="wide",
)

# Koyu Tema ve Arayüz Tasarımı
st.markdown(
    """
<style>
    .stApp {
        background-color: #0e1117;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Veri Yükleme ve Sütun İsimlerini Temizleme
@st.cache_data
def veri_yukle():
    df = pd.read_csv("tum_bolumler.csv")

    # Sütun isimlerini küçük harfe çevirip boşlukları temizleyelim
    df.columns = [str(col).strip().lower() for col in df.columns]

    # Esnek Sütun Yakalama
    def sutun_bul(anahtar_kelimeler):
        for col in df.columns:
            if any(k in col for k in anahtar_kelimeler):
                return col
        return None

    uni_col = sutun_bul(["uni", "üniversite", "universite"])
    bolum_col = sutun_bul(["isim", "program", "bölüm", "bolum"])
    sira_col = sutun_bul(["sira", "sıra"])
    puan_col = sutun_bul(["tur", "tür", "puan"])
    sehir_col = sutun_bul(["il", "sehir", "şehir"])
    fakulte_col = sutun_bul(["fakulte", "fakülte"])

    # Standart isimlere dönüştür
    renames = {}
    if uni_col:
        renames[uni_col] = "Üniversite"
    if bolum_col:
        renames[bolum_col] = "Bölüm"
    if sira_col:
        renames[sira_col] = "Sıralama"
    if puan_col:
        renames[puan_col] = "Puan_Türü"
    if sehir_col:
        renames[sehir_col] = "Şehir"
    if fakulte_col:
        renames[fakulte_col] = "Fakülte"

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


# --- SOL PANEL (FİLTRELER) ---
st.sidebar.title("🎯 Tercih Filtreleri")

ogrenci_sira = st.sidebar.number_input(
    "YKS Sıralamanız:", min_value=1, value=50000, step=1000
)

# Puan Türü Filtresi (Güvenli Yöntem)
if "Puan_Türü" in df.columns:
    puan_listesi = ["Tümü"] + [
        str(x) for x in df["Puan_Türü"].dropna().unique() if str(x).strip() != ""
    ]
else:
    puan_listesi = ["Tümü"]
secilen_puan = st.sidebar.selectbox("Puan Türü:", puan_listesi)

# Şehir Filtresi (Güvenli Yöntem)
if "Şehir" in df.columns:
    sehir_listesi = [
        str(x) for x in df["Şehir"].dropna().unique() if str(x).strip() != ""
    ]
else:
    sehir_listesi = []
secilen_sehirler = st.sidebar.multiselect("Şehir Seçimi:", sehir_listesi)

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

# Olasılık Hesaplama
sira_col = "Sıralama" if "Sıralama" in filtreli_df.columns else df.columns[-1]

olasiliklar = []
for _, row in filtreli_df.iterrows():
    durum = olasilik_hesapla(ogrenci_sira, row[sira_col])
    olasiliklar.append(durum)

filtreli_df.insert(0, "Gelme İhtimali", olasiliklar)

# İhtimal Filtresi Uygulama
if ihtimal_filtresi:
    filtreli_df = filtreli_df[
        filtreli_df["Gelme İhtimali"].isin(ihtimal_filtresi)
    ]

# --- ANA EKRAN ---
st.title("🎓 YKS Tercih & Analiz Robotu")

# Üst Göstergeler
c1, c2 = st.columns(2)
with c1:
    st.metric("Girilen Sıralama", f"{ogrenci_sira:,}")
with c2:
    st.metric("Bulunan Program Sayısı", f"{len(filtreli_df):,}")

# Tablo Gösterimi
st.subheader("Üniversite ve Bölüm Sonuçları")

# Gösterilecek Temiz Kolon Sırası
oncelikli_kolonlar = [
    "Gelme İhtimali",
    "Üniversite",
    "Fakülte",
    "Bölüm",
    "Puan_Türü",
    "Şehir",
    "Sıralama",
]
gosterilecek = [col for col in oncelikli_kolonlar if col in filtreli_df.columns]

if not gosterilecek:
    gosterilecek = filtreli_df.columns

st.dataframe(filtreli_df[gosterilecek], use_container_width=True, hide_index=True)
