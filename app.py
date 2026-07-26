import pandas as pd
import streamlit as st
import unicodedata

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Marco Asensio (enbüyük fener)",
    page_icon="💛💙",
    layout="wide",
)

bg_image_url = "https://img.piri.net/piri/upload/3/2026/5/25/d40fffbf-marco-asensio-kadroya-alindi-mi-ispanya-milli-takiminin-dunya-kupasi-kadrosu-belli-oldu.webp"
small_logo_url = (
    "https://image.fanatik.com.tr/i/fanatik/75/0x410/66ebd8349321aeccbdc731f7.jpg"
)

# CSS TASARIMI
st.markdown(
    f"""
<style>
    .stApp {{
        background: linear-gradient(rgba(0, 12, 30, 0.85), rgba(0, 8, 20, 0.90)), url("{bg_image_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: #ffffff;
    }}
    
    .asensio-title {{
        font-size: 40px;
        font-weight: 900;
        background: linear-gradient(90deg, #ffed00, #ffffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 4px 15px rgba(255, 237, 0, 0.4);
        margin-bottom: 5px;
    }}
    
    .asensio-subtitle {{
        color: #ffed00;
        font-size: 16px;
        font-weight: 700;
        margin-bottom: 25px;
        text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.8);
    }}

    .hero-panel {{
        background: rgba(0, 26, 58, 0.75);
        border: 2px solid #ffed00;
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(255, 237, 0, 0.2);
        backdrop-filter: blur(12px);
    }}
    
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
    
    .badge-guvenli {{ background-color: #10b981; color: #ffffff; font-weight: bold; padding: 6px 16px; border-radius: 20px; font-size: 13px; display: inline-block; }}
    .badge-dengeli {{ background-color: #f59e0b; color: #ffffff; font-weight: bold; padding: 6px 16px; border-radius: 20px; font-size: 13px; display: inline-block; }}
    .badge-riskli {{ background-color: #ef4444; color: #ffffff; font-weight: bold; padding: 6px 16px; border-radius: 20px; font-size: 13px; display: inline-block; }}
    
    .stat-box {{
        background: rgba(0, 12, 30, 0.85);
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        border: 1px solid rgba(255, 237, 0, 0.25);
    }}
    .stat-title {{ font-size: 11px; color: #ffed00; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; }}
    .stat-value {{ font-size: 20px; color: #ffffff; font-weight: 800; margin-top: 2px; }}

    div.stButton > button {{
        background-color: #10b981 !important;
        color: #022c22 !important;
        font-weight: 900 !important;
        font-size: 20px !important;
        border-radius: 12px !important;
        border: 2px solid #34d399 !important;
        padding: 12px 28px !important;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.6) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }}

    .scoreboard-img {{
        width: 100%;
        max-width: 280px;
        height: auto;
        border-radius: 20px;
        border: 3px solid #ffed00;
        box-shadow: 0 0 20px rgba(255, 237, 0, 0.6);
        display: block;
        margin-left: auto;
    }}
</style>
""",
    unsafe_allow_html=True,
)


def norm(text):
    if not isinstance(text, str):
        return ""
    text = (
        text.replace("İ", "i")
        .replace("I", "ı")
        .replace("Ğ", "ğ")
        .replace("Ü", "ü")
        .replace("Ş", "ş")
        .replace("Ö", "ö")
        .replace("Ç", "ç")
    )
    text = text.lower()
    return "".join(
        c
        for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


@st.cache_data
def veri_yukle():
    df = pd.read_csv("tum_bolumler.csv")
    df.columns = df.columns.str.strip()

    # Sütun isimlerini akıllı eşleme ile düzelt
    rename_mapping = {}
    for col in df.columns:
        c_low = norm(col)
        if "universite" in c_low or "uni" in c_low:
            rename_mapping[col] = "Üniversite"
        elif "bolum" in c_low or "program" in c_low:
            rename_mapping[col] = "Bölüm"
        elif "sira" in c_low or "2023" in c_low or "2024" in c_low:
            rename_mapping[col] = "Sıralama"
        elif "puan" in c_low or "tur" in c_low:
            rename_mapping[col] = "Puan_Türü"
        elif c_low in ["sehir", "il", "il adi", "sehir adi"]:
            rename_mapping[col] = "Şehir"
        elif "fakulte" in c_low:
            rename_mapping[col] = "Fakülte"

    df = df.rename(columns=rename_mapping)

    # Zorunlu kolon kontrolü - Yoksa oluşturur patlamayı önler
    for req in ["Üniversite", "Bölüm", "Sıralama", "Puan_Türü", "Şehir"]:
        if req not in df.columns:
            df[req] = "Belirtilmedi"

    # Şehir sütunundaki sayısal değerleri veya boşlukları temizle
    df["Şehir"] = df["Şehir"].astype(str).replace(r"^\d+(\.\d+)?$", "", regex=True)

    return df


try:
    df = veri_yukle()
except Exception as e:
    st.error(f"CSV Yüklenirken Hata Oluştu: {e}")
    st.stop()


def olasilik_hesapla(ogrenci_sira, bolum_sira):
    try:
        bolum_sira = float(
            str(bolum_sira)
            .replace(".", "")
            .replace(",", ".")
            .replace(" ", "")
            .strip()
        )
        if pd.isna(bolum_sira) or bolum_sira <= 0:
            return "NAH GİDERSİN", "badge-riskli"
    except:
        return "NAH GİDERSİN", "badge-riskli"

    fark = ogrenci_sira - bolum_sira
    if fark <= -10000:
        return "GELİR BU", "badge-guvenli"
    elif -10000 < fark <= 5000:
        return "KISMET", "badge-dengeli"
    else:
        return "NAH GİDERSİN", "badge-riskli"


if "tercihler" not in st.session_state:
    st.session_state.tercihler = []
if "arama_yapildi" not in st.session_state:
    st.session_state.arama_yapildi = False

# BAŞLIK
head_col1, head_col2 = st.columns([7, 3])
with head_col1:
    st.markdown(
        '<div class="asensio-title">Marco Asensio (enbüyük fener)</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="asensio-subtitle">💛💙 Tercih Robotu (Ağlama Masası)</div>',
        unsafe_allow_html=True,
    )
with head_col2:
    st.markdown(
        f'<img src="{small_logo_url}" class="scoreboard-img">',
        unsafe_allow_html=True,
    )

with st.container():
    st.markdown('<div class="hero-panel">', unsafe_allow_html=True)

    c1, c2 = st.columns([6, 4])
    with c1:
        st.caption("HANGİ ALANDAN PATLADIN")
        puan_turleri = ["TÜMÜ", "SAY", "EA", "SÖZ", "DİL", "TYT"]
        secilen_puan = st.radio(
            "Puan Türü", puan_turleri, horizontal=True, label_visibility="collapsed"
        )
    with c2:
        st.caption("KAÇ SIRALAMA YAPTIN LAN ENAYİ")
        ogrenci_sira = st.number_input(
            "Başarı Sıralaman",
            min_value=1,
            value=610340,
            step=1000,
            label_visibility="collapsed",
        )

    st.write("---")

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        st.caption("HANGİ ŞEHİR")
        sehirler = sorted(
            [
                str(x).strip()
                for x in df["Şehir"].dropna().unique()
                if str(x).strip() not in ["", "nan", "Belirtilmedi"]
                and not str(x).replace(".", "").isdigit()
            ]
        )
        secilen_sehirler = st.multiselect(
            "Şehir Seçin",
            sehirler,
            placeholder="Şehir seç...",
            label_visibility="collapsed",
        )

    with f2:
        st.caption("HANGİ ÜNİVERSİTE")
        # .get() ve güvenli kontrol eklendi:
        uni_series = (
            df["Üniversite"] if "Üniversite" in df.columns else pd.Series([])
        )
        universiteler = sorted(
            [
                str(x).strip()
                for x in uni_series.dropna().unique()
                if str(x).strip() not in ["", "nan", "Belirtilmedi"]
                and not str(x).replace(".", "").isdigit()
            ]
        )
        secilen_unis = st.multiselect(
            "Üniversite Seçin",
            universiteler,
            placeholder="Üni seç veya yaz...",
            label_visibility="collapsed",
        )

    with f3:
        st.caption("HANGİ BÖLÜM")
        bolum_series = df["Bölüm"] if "Bölüm" in df.columns else pd.Series([])
        bolumler = sorted(
            [
                str(x).strip()
                for x in bolum_series.dropna().unique()
                if str(x).strip() not in ["", "nan", "Belirtilmedi"]
                and not str(x).replace(".", "").isdigit()
            ]
        )
        secilen_bolumler = st.multiselect(
            "Bölüm Seçin",
            bolumler,
            placeholder="Bölüm seç veya yaz...",
            label_visibility="collapsed",
        )

    with f4:
        st.caption("PARA VERCEK MİSİN (BURS DURUMU)")
        burs_secenekleri = [
            "Burslu",
            "%50 İndirimli",
            "%25 İndirimli",
            "Ücretli",
            "Ücretsiz",
        ]
        secilen_burslar = st.multiselect(
            "Burs Durumu",
            burs_secenekleri,
            placeholder="Burs / İndirim seç...",
            label_visibility="collapsed",
        )

    st.write("")
    btn_col1, btn_col2, btn_col3 = st.columns([3, 6, 3])
    with btn_col2:
        if st.button("🚀 BUL LAN", key="btn_search_main", use_container_width=True):
            st.session_state.arama_yapildi = True

    st.markdown("</div>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(
    ["🔍 SONUÇLAR ALLAH BÜYÜK", "📋 Yandık Listesi (Kaydedilenler)"]
)

with tab1:
    if not st.session_state.arama_yapildi:
        st.info("👈 Filtreleri ayarla, sonra yeşil BUL LAN butonuna bas!")
    else:
        temp_df = df.copy()

        # 1. Puan Türü Filtresi
        if secilen_puan != "TÜMÜ":
            p_target = norm(secilen_puan)
            temp_df = temp_df[
                temp_df["Puan_Türü"]
                .astype(str)
                .apply(lambda x: p_target in norm(x))
            ]

        # 2. Şehir Filtresi
        if secilen_sehirler:
            s_targets = [norm(s) for s in secilen_sehirler]
            temp_df = temp_df[
                temp_df["Şehir"].apply(
                    lambda x: any(starg in norm(str(x)) for starg in s_targets)
                )
            ]

        # 3. Üniversite Filtresi
        if secilen_unis:
            u_targets = [norm(u) for u in secilen_unis]
            temp_df = temp_df[
                temp_df["Üniversite"].apply(
                    lambda x: any(utarg in norm(str(x)) for utarg in u_targets)
                )
            ]

        # 4. Bölüm Filtresi
        if secilen_bolumler:
            b_targets = [norm(b) for b in secilen_bolumler]
            temp_df = temp_df[
                temp_df["Bölüm"].apply(
                    lambda x: any(btarg in norm(str(x)) for btarg in b_targets)
                )
            ]

        # 5. Burs Filtresi
        if secilen_burslar:
            burs_keywords = []
            for b in secilen_burslar:
                b_norm = norm(b)
                if "50" in b_norm:
                    burs_keywords.append("50")
                elif "25" in b_norm:
                    burs_keywords.append("25")
                elif "burslu" in b_norm:
                    burs_keywords.append("burslu")
                elif "ucretli" in b_norm:
                    burs_keywords.append("ucretli")
                elif "ucretsiz" in b_norm:
                    burs_keywords.append("ucretsiz")

            if burs_keywords:
                temp_df = temp_df[
                    temp_df["Bölüm"].apply(
                        lambda x: any(k in norm(str(x)) for k in burs_keywords)
                    )
                ]

        if temp_df.empty:
            st.warning("⚠️ Sonuç çıkmadı!")
        else:
            st.markdown(f"### 📍 Aha Sana **{len(temp_df)}** Tane Yer Buldum")

            gosterilecek_df = temp_df.head(100)

            for idx, row in gosterilecek_df.iterrows():
                bolum_sira = row.get("Sıralama", 0)
                durum, badge_class = olasilik_hesapla(ogrenci_sira, bolum_sira)

                uni_adi = row.get("Üniversite", "Belirtilmedi")
                bolum_adi = row.get("Bölüm", "Belirtilmedi")
                fakulte = row.get("Fakülte", "")
                sehir = row.get("Şehir", "")
                puan_turu = row.get("Puan_Türü", "")

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
                            <div class="stat-title">KAÇLA KAPATMIŞ</div>
                            <div class="stat-value" style="color: #ffed00;">{bolum_sira}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-title">ALAN</div>
                            <div class="stat-value">{puan_turu}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-title">MEMLEKET</div>
                            <div class="stat-value">{sehir}</div>
                        </div>
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )

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
                            f"✓ Vazgeçtim At Bunu",
                            key=f"btn_rem_{idx}",
                            type="secondary",
                        ):
                            st.session_state.tercihler.remove(tercih_item)
                            st.rerun()
                    else:
                        if st.button(
                            f"➕ Yandık, Ekle Listeye",
                            key=f"btn_add_{idx}",
                            type="primary",
                        ):
                            st.session_state.tercihler.append(tercih_item)
                            st.rerun()

                st.write("")

with tab2:
    st.subheader("📌 Son Çare Tercih Listen")

    if not st.session_state.tercihler:
        st.warning("Boş boş bakma, bir iki bölüm ekle önce.")
    else:
        tercih_df = pd.DataFrame(st.session_state.tercihler)
        st.dataframe(tercih_df, use_container_width=True)

        csv_data = tercih_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Çıktı Al Babana Göster (CSV İndir)",
            data=csv_data,
            file_name="asensio_tercihlerim.csv",
            mime="text/csv",
        )
