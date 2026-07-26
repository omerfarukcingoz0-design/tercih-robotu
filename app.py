import pandas as pd
import streamlit as st

# Sayfa Yapılandırması (Marco Asensio & En Büyük Fener Teması)
st.set_page_config(
    page_title="Marco Asensio (enbüyük fener)",
    page_icon="💛💙",
    layout="wide",
)

# Resim URL'si
bg_image_url = "https://img.piri.net/piri/upload/3/2026/5/25/d40fffbf-marco-asensio-kadroya-alindi-mi-ispanya-milli-takiminin-dunya-kupasi-kadrosu-belli-oldu.webp"

# --- SARI-LACİVERT & ASENSIO GÖRSEL ARKA PLANLI CSS TASARIMI ---
st.markdown(
    f"""
<style>
    /* Arka Plan: Marco Asensio Fotoğrafı + Karartma Kaplaması */
    .stApp {{
        background: linear-gradient(rgba(0, 12, 30, 0.85), rgba(0, 8, 20, 0.90)), url("{bg_image_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: #ffffff;
    }}
    
    /* Sarı & Lacivert Başlık Stili */
    .asensio-title {{
        font-size: 42px;
        font-weight: 900;
        background: linear-gradient(90deg, #ffed00, #ffffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 4px 15px rgba(255, 237, 0, 0.4);
        margin-bottom: 5px;
    }}
    
    .asensio-subtitle {{
        color: #ffed00;
        font-size: 18px;
        font-weight: 700;
        letter-spacing: 1px;
        margin-bottom: 25px;
        text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.8);
    }}

    /* Üst Hero Arama Paneli */
    .hero-panel {{
        background: rgba(0, 26, 58, 0.75);
        border: 2px solid #ffed00;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(255, 237, 0, 0.2);
        backdrop-filter: blur(12px);
    }}
    
    /* Kart Tasarımı (Sarı-Lacivert Detaylı) */
    .card {{
        background: rgba(10, 25, 47, 0.85);
        border: 1px solid rgba(255, 237, 0, 0.3);
        border-left: 5px solid #ffed00;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(8px);
    }}
    
    /* Rozetler */
    .badge-guvenli {{ background-color: #10b981; color: #ffffff; font-weight: bold; padding: 6px 16px; border-radius: 20px; font-size: 13px; display: inline-block; }}
    .badge-dengeli {{ background-color: #f59e0b; color: #ffffff; font-weight: bold; padding: 6px 16px; border-radius: 20px; font-size: 13px; display: inline-block; }}
    .badge-riskli {{ background-color: #ef4444; color: #ffffff; font-weight: bold; padding: 6px 16px; border-radius: 20px; font-size: 13px; display: inline-block; }}
    
    /* İstatistik Kutuları */
    .stat-box {{
        background: rgba(0, 12, 30, 0.85);
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        border: 1px solid rgba(255, 237, 0, 0.25);
    }}
    .stat-title {{ font-size: 11px; color: #ffed00; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; }}
    .stat-value {{ font-size: 20px; color: #ffffff; font-weight: 800; margin-top: 2px; }}
</style>
""",
    unsafe_allow_html=True,
)


# Veri Yükleme ve Sütun Yapısını Temizleme
@st.cache_data
def veri_yukle():
    df = pd.read_csv("tum_bolumler.csv")
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
            return "RİSKLİ", "badge-riskli"
    except:
        return "RİSKLİ", "badge-riskli"

    fark = ogrenci_sira - bolum_sira

    if fark <= -10000:
        return "GÜVENLİ", "badge-guvenli"
    elif -10000 < fark <= 5000:
        return "DENGELİ", "badge-dengeli"
    else:
        return "RİSKLİ", "badge-riskli"


if "tercihler" not in st.session_state:
    st.session_state.tercihler = []

# --- ÜST BAŞLIKLAR & ASENSIO İMZASI ---
st.markdown(
    '<div class="asensio-title">Marco Asensio (enbüyük fener)</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="asensio-subtitle">💛💙 Marco Asensio (enbüyük fener) Akıllı Analiz Portalı</div>',
    unsafe_allow_html=True,
)

# --- ÜST MODERN ARAMA PANELİ ---
with st.container():
    st.markdown('<div class="hero-panel">', unsafe_allow_html=True)

    # 1. Satır: Puan Türü + Sıralama Input
    c1, c2 = st.columns([6, 4])
    with c1:
        st.caption("PUAN TÜRÜ")
        puan_turleri = ["TÜMÜ", "SAY", "EA", "SÖZ", "DİL", "TYT"]
        secilen_puan = st.radio(
            "Puan Türü", puan_turleri, horizontal=True, label_visibility="collapsed"
        )
    with c2:
        st.caption("BAŞARI SIRALAMAN")
        ogrenci_sira = st.number_input(
            "Başarı Sıralaman",
            min_value=1,
            value=50000,
            step=1000,
            label_visibility="collapsed",
        )

    st.write("---")

    # 2. Satır: Şehir, Üniversite Adı, Bölüm Adı
    f1, f2, f3 = st.columns(3)
    with f1:
        st.caption("ŞEHİR SÜZGEÇİ")
        sehirler = (
            sorted(
                [
                    str(x)
                    for x in df["Şehir"].dropna().unique()
                    if str(x).strip() != ""
                ]
            )
            if "Şehir" in df.columns
            else []
        )
        secilen_sehirler = st.multiselect(
            "Şehir Seçin",
            sehirler,
            placeholder="Şehir Seçiniz...",
            label_visibility="collapsed",
        )

    with f2:
        st.caption("ÜNİVERSİTE ARA")
        arama_uni = st.text_input(
            "Üniversite",
            placeholder="Örn: Boğaziçi, Koç, İTÜ...",
            label_visibility="collapsed",
        )

    with f3:
        st.caption("BÖLÜM ARA")
        arama_bolum = st.text_input(
            "Bölüm",
            placeholder="Örn: Bilgisayar, İşletme...",
            label_visibility="collapsed",
        )

    st.write("---")

    # 3. Satır: Durum Filtresi
    d1, d2, d3, d4 = st.columns([2, 2, 2, 4])
    with d1:
        chk_guvenli = st.checkbox("🟢 GÜVENLİ", value=True)
    with d2:
        chk_dengeli = st.checkbox("🟡 DENGELİ", value=True)
    with d3:
        chk_riskli = st.checkbox("🔴 RİSKLİ", value=True)

    st.markdown("</div>", unsafe_allow_html=True)


# Durum Listesi
secilen_durumlar = []
if chk_guvenli:
    secilen_durumlar.append("GÜVENLİ")
if chk_dengeli:
    secilen_durumlar.append("DENGELİ")
if chk_riskli:
    secilen_durumlar.append("RİSKLİ")


# --- FİLTRELEME MANTIĞI ---
filtreli_df = pd.DataFrame()

if (
    arama_uni
    or arama_bolum
    or secilen_sehirler
    or (secilen_puan != "TÜMÜ")
):
    temp_df = df.copy()

    if secilen_puan != "TÜMÜ" and "Puan_Türü" in temp_df.columns:
        temp_df = temp_df[
            temp_df["Puan_Türü"].astype(str).str.upper() == secilen_puan
        ]

    if secilen_sehirler and "Şehir" in temp_df.columns:
        temp_df = temp_df[temp_df["Şehir"].astype(str).isin(secilen_sehirler)]

    if arama_uni and "Üniversite" in temp_df.columns:
        temp_df = temp_df[
            temp_df["Üniversite"]
            .astype(str)
            .str.contains(arama_uni, case=False, na=False)
        ]

    if arama_bolum and "Bölüm" in temp_df.columns:
        temp_df = temp_df[
            temp_df["Bölüm"]
            .astype(str)
            .str.contains(arama_bolum, case=False, na=False)
        ]

    filtreli_df = temp_df


# --- LİSTELEME EKRANI ---
tab1, tab2 = st.tabs(
    [
        "🔍 Marco Asensio (enbüyük fener) - Sonuçlar",
        "📋 Marco Asensio (enbüyük fener) - Listem",
    ]
)

with tab1:
    if (
        not arama_uni
        and not arama_bolum
        and not secilen_sehirler
        and secilen_puan == "TÜMÜ"
        and filtreli_df.empty
    ):
        st.info(
            "👈 **Marco Asensio (enbüyük fener)** arama panelinden Bölüm, Üniversite veya Şehir seçerek sorgulama yapın."
        )
    else:
        st.markdown(
            f"### 📍 Marco Asensio (enbüyük fener) - **{len(filtreli_df)}** Program Buldu"
        )

        sira_col = "Sıralama" if "Sıralama" in filtreli_df.columns else "sıralama"

        for idx, row in filtreli_df.iterrows():
            bolum_sira = row.get(sira_col, 0)
            durum, badge_class = olasilik_hesapla(ogrenci_sira, bolum_sira)

            if durum not in secilen_durumlar:
                continue

            uni_adi = row.get("Üniversite", "Üniversite Belirtilmemiş")
            bolum_adi = row.get("Bölüm", "Bölüm Belirtilmemiş")
            fakulte = row.get("Fakülte", "")
            sehir = row.get("Şehir", "")
            puan_turu = row.get("Puan_Türü", "")

            # Kart Arayüzü
            st.markdown(
                f"""
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <h3 style="margin: 0 0 6px 0; font-size: 22px; color: #ffed00;">{bolum_adi}</h3>
                        <p style="margin: 0; color: #ffffff; font-weight: 700; font-size: 15px;">{uni_adi} · {sehir}</p>
                        <p style="margin: 4px 0 0 0; color: #94a3b8; font-size: 13px;">{fakulte}</p>
                    </div>
                    <div>
                        <span class="{badge_class}">{durum}</span>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 20px;">
                    <div class="stat-box">
                        <div class="stat-title">TABAN SIRALAMASI</div>
                        <div class="stat-value" style="color: #ffed00;">{f"{int(bolum_sira):,}" if pd.notna(bolum_sira) and str(bolum_sira).isdigit() else bolum_sira}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-title">PUAN TÜRÜ</div>
                        <div class="stat-value">{puan_turu}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-title">ŞEHİR</div>
                        <div class="stat-value">{sehir}</div>
                    </div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Tercih Ekle / Çıkar
            tercih_item = {
                "Üniversite": uni_adi,
                "Bölüm": bolum_adi,
                "Şehir": sehir,
                "Sıralama": bolum_sira,
                "Durum": durum,
            }

            c_btn1, _ = st.columns([3, 7])
            with c_btn1:
                if tercih_item in st.session_state.tercihler:
                    if st.button(
                        f"✓ Listede Ekli (Çıkar)",
                        key=f"btn_rem_{idx}",
                        type="secondary",
                    ):
                        st.session_state.tercihler.remove(tercih_item)
                        st.rerun()
                else:
                    if st.button(
                        f"➕ Tercih Listeme Ekle",
                        key=f"btn_add_{idx}",
                        type="primary",
                    ):
                        st.session_state.tercihler.append(tercih_item)
                        st.rerun()

            st.write("")


with tab2:
    st.subheader("📌 Marco Asensio (enbüyük fener) - Özel Listeniz")

    if not st.session_state.tercihler:
        st.warning("Henüz listenize hiç bölüm eklemediniz.")
    else:
        tercih_df = pd.DataFrame(st.session_state.tercihler)
        st.dataframe(tercih_df, use_container_width=True)

        csv_data = tercih_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Marco Asensio (enbüyük fener) Listesini İndir (Excel / CSV)",
            data=csv_data,
            file_name="marco_asensio_tercih_listem.csv",
            mime="text/csv",
        )
