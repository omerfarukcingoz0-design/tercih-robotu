import io
import pandas as pd
import streamlit as st

# Sayfa Yapılandırması (Açık ve Modern Arayüz)
st.set_page_config(
    page_title="Marco Asensio | YKS Tercih Robotu",
    page_icon="🎓",
    layout="wide",
)

# Derece Kampüsü Tarzı Modern Beyaz CSS Tasarımı
st.markdown(
    """
<style>
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }
    .card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .badge-guvenli { background-color: #dcfce7; color: #15803d; font-weight: bold; padding: 4px 12px; border-radius: 20px; font-size: 13px; }
    .badge-dengeli { background-color: #fef3c7; color: #b45309; font-weight: bold; padding: 4px 12px; border-radius: 20px; font-size: 13px; }
    .badge-riskli { background-color: #fee2e2; color: #b91c1c; font-weight: bold; padding: 4px 12px; border-radius: 20px; font-size: 13px; }
    .stat-box {
        background-color: #f1f5f9;
        border-radius: 12px;
        padding: 10px 15px;
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    .stat-title { font-size: 11px; color: #64748b; font-weight: bold; text-transform: uppercase; }
    .stat-value { font-size: 18px; color: #0f172a; font-weight: 800; }
</style>
""",
    unsafe_allow_html=True,
)


# Veri Yükleme ve Sütun Yapısını Düzeltme
@st.cache_data
def veri_yukle():
    df = pd.read_csv("tum_bolumler.csv")

    # Sütun isimlerini küçültüp temizleme
    df.columns = [str(col).strip().lower() for col in df.columns]

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
    burs_col = sutun_bul(["burs", "ucret", "ücret"])

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
    if burs_col:
        renames[burs_col] = "Burs"

    return df.rename(columns=renames)


try:
    df = veri_yukle()
except Exception as e:
    st.error(f"Veri yüklenemedi: {e}")
    st.stop()


# Olasılık Hesabı
def olasilik_hesapla(ogrenci_sira, bolum_sira):
    try:
        bolum_sira = float(bolum_sira)
        if pd.isna(bolum_sira) or bolum_sira <= 0:
            return "VERİ YOK", "badge-riskli"
    except:
        return "VERİ YOK", "badge-riskli"

    fark = ogrenci_sira - bolum_sira

    if fark <= -10000:
        return "GÜVENLİ", "badge-guvenli"
    elif -10000 < fark <= 5000:
        return "DENGELİ", "badge-dengeli"
    else:
        return "RİSKLİ", "badge-riskli"


# Session State (Tercih Listesi Hafızası)
if "tercihler" not in st.session_state:
    st.session_state.tercihler = []

# --- SOL PANEL FİLTRELERİ ---
st.sidebar.title("🎯 Tercih Robotu Filtreleri")

ogrenci_sira = st.sidebar.number_input(
    "YKS Sıralamanız:", min_value=1, value=50000, step=1000
)

arama_metni = st.sidebar.text_input(
    "🔍 Bölüm veya Üniversite Adı:", placeholder="Örn: İşletme, Koç..."
)

# Şehir Seçimi
sehirler = (
    sorted(
        [str(x) for x in df["Şehir"].dropna().unique() if str(x).strip() != ""]
    )
    if "Şehir" in df.columns
    else []
)
secilen_sehirler = st.sidebar.multiselect("Şehir Seçin:", sehirler)

# Puan Türü
puan_turleri = (
    ["Tümü"]
    + sorted(
        [
            str(x)
            for x in df["Puan_Türü"].dropna().unique()
            if str(x).strip() != ""
        ]
    )
    if "Puan_Türü" in df.columns
    else ["Tümü"]
)
secilen_puan = st.sidebar.selectbox("Puan Türü:", puan_turleri)

# İhtimal Filtresi
durum_filtresi = st.sidebar.multiselect(
    "Durum:",
    ["GÜVENLİ", "DENGELİ", "RİSKLİ"],
    default=["GÜVENLİ", "DENGELİ", "RİSKLİ"],
)


# --- FİLTRELEME MANTIĞI ---
# Başlangıçta boş gelmesi için filtre kriteri aranıyor
filtreli_df = pd.DataFrame()

if arama_metni or secilen_sehirler or (secilen_puan != "Tümü"):
    temp_df = df.copy()

    if secilen_puan != "Tümü" and "Puan_Türü" in temp_df.columns:
        temp_df = temp_df[temp_df["Puan_Türü"].astype(str) == secilen_puan]

    if secilen_sehirler and "Şehir" in temp_df.columns:
        temp_df = temp_df[temp_df["Şehir"].astype(str).isin(secilen_sehirler)]

    if arama_metni:
        u_mask = (
            temp_df["Üniversite"]
            .astype(str)
            .str.contains(arama_metni, case=False, na=False)
            if "Üniversite" in temp_df.columns
            else False
        )
        b_mask = (
            temp_df["Bölüm"]
            .astype(str)
            .str.contains(arama_metni, case=False, na=False)
            if "Bölüm" in temp_df.columns
            else False
        )
        temp_df = temp_df[u_mask | b_mask]

    filtreli_df = temp_df


# --- ANA EKRAN SEKMELERİ ---
st.title("🎓 YKS Tercih Robotu")

tab1, tab2 = st.tabs(["🔍 Bölüm Arama", "📋 Tercih Listem"])

with tab1:
    if (
        not arama_metni
        and not secilen_sehirler
        and secilen_puan == "Tümü"
        and filtreli_df.empty
    ):
        st.info(
            "👈 Lütfen sol taraftaki filtre alanından **Bölüm Adı (Örn: İşletme)** veya **Şehir** girerek aramayı başlatın."
        )
    else:
        st.write(
            f"**Girilen Sıralama:** {ogrenci_sira:,} | **Bulunan Sonuç:** {len(filtreli_df)} Program"
        )

        sira_col = "Sıralama" if "Sıralama" in filtreli_df.columns else "sıralama"

        for idx, row in filtreli_df.iterrows():
            bolum_sira = row.get(sira_col, 0)
            durum, badge_class = olasilik_hesapla(ogrenci_sira, bolum_sira)

            # Durum Filtresi Kontrolü
            if durum not in durum_filtresi:
                continue

            uni_adi = row.get("Üniversite", "Üniversite Belirtilmemiş")
            bolum_adi = row.get("Bölüm", "Bölüm Belirtilmemiş")
            fakulte = row.get("Fakülte", "")
            sehir = row.get("Şehir", "")
            puan_turu = row.get("Puan_Türü", "")

            # Derece Kampüsü Kart Arayüzü
            with st.container():
                st.markdown(
                    f"""
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h3 style="margin: 0; color: #0f172a; font-size: 20px;">{bolum_adi}</h3>
                        <span class="{badge_class}">{durum}</span>
                    </div>
                    <p style="margin: 5px 0 15px 0; color: #0284c7; font-weight: 600;">{uni_adi} · {sehir}</p>
                    <p style="margin: 0 0 15px 0; color: #64748b; font-size: 13px;">{fakulte}</p>
                    
                    <div style="display: flex; gap: 15px; margin-bottom: 15px;">
                        <div class="stat-box" style="flex: 1;">
                            <div class="stat-title">TABAN SIRALAMASI</div>
                            <div class="stat-value">{bolum_sira if pd.notna(bolum_sira) else '—'}</div>
                        </div>
                        <div class="stat-box" style="flex: 1;">
                            <div class="stat-title">PUAN TÜRÜ</div>
                            <div class="stat-value">{puan_turu}</div>
                        </div>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                # Listeme Ekle / Çıkar Butonu
                tercih_item = {
                    "Üniversite": uni_adi,
                    "Bölüm": bolum_adi,
                    "Şehir": sehir,
                    "Sıralama": bolum_sira,
                    "Durum": durum,
                }

                if tercih_item in st.session_state.tercihler:
                    if st.button(
                        f"✓ Listede Ekli (Çıkar)", key=f"btn_remove_{idx}"
                    ):
                        st.session_state.tercihler.remove(tercih_item)
                        st.rerun()
                else:
                    if st.button(
                        f"+ Tercih Listeme Ekle", key=f"btn_add_{idx}"
                    ):
                        st.session_state.tercihler.append(tercih_item)
                        st.rerun()

                st.write("")


with tab2:
    st.subheader("📌 Oluşturduğunuz Tercih Listesi")

    if not st.session_state.tercihler:
        st.warning("Henüz listenize hiç bölüm eklemediniz.")
    else:
        tercih_df = pd.DataFrame(st.session_state.tercihler)
        st.dataframe(tercih_df, use_container_width=True)

        # Excel / CSV İndirme Butonu
        csv_data = tercih_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Tercih Listemi İndir (CSV/Excel)",
            data=csv_data,
            file_name="tercih_listem.csv",
            mime="text/csv",
        )
