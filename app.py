import pandas as pd
import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Marco Asensio (enbüyük fener)",
    page_icon="💛💙",
    layout="wide",
)

# Resim URL'si
bg_image_url = "https://img.piri.net/piri/upload/3/2026/5/25/d40fffbf-marco-asensio-kadroya-alindi-mi-ispanya-milli-takiminin-dunya-kupasi-kadrosu-belli-oldu.webp"

# --- CSS TASARIMI ---
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

    /* FISTIK YEŞİLİ BUL LAN BUTONU TASARIMI */
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
    div.stButton > button:hover {{
        background-color: #059669 !important;
        color: #ffffff !important;
        transform: scale(1.02);
        box-shadow: 0 6px 25px rgba(16, 185, 129, 0.8) !important;
    }}
</style>
""",
    unsafe_allow_html=True,
)


def tr_lower(text):
    if not isinstance(text, str):
        return ""
    return (
        text.replace("İ", "i")
        .replace("I", "ı")
        .replace("Ğ", "ğ")
        .replace("Ü", "ü")
        .replace("Ş", "ş")
        .replace("Ö", "ö")
        .replace("Ç", "ç")
        .lower()
    )


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


def olasilik_hesapla(ogrenci_sira, bolum_sira):
    try:
        bolum_sira = float(bolum_sira)
        if pd.isna(bolum_sira) or bolum_sira <= 0:
            return "NAH GİDERSİN", "badge-riskli"
    except:
        return "NAH GİDERSİN", "badge-riskli"

    fark = ogrenci_sira - bolum_sira

    if fark <= -10000:
        return "GELİR BU", "badge-guvenli"
    elif -10000 < fark <= 5000:
        return "KISMET KANKA", "badge-dengeli"
    else:
        return "NAH GİDERSİN", "badge-riskli"


if "tercihler" not in st.session_state:
    st.session_state.tercihler = []

if "arama_yapildi" not in st.session_state:
    st.session_state.arama_yapildi = False

# --- BAŞLIKLAR ---
st.markdown(
    '<div class="asensio-title">Marco Asensio (enbüyük fener)</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="asensio-subtitle">💛💙 Kanka Tercih Robotu (Ağlama Masası)</div>',
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
            placeholder="Şehir seç...",
            label_visibility="collapsed",
        )

    with f2:
        st.caption("HANGİ ÜNİVERSİTE")
        universiteler = (
            sorted(
                [
                    str(x)
                    for x in df["Üniversite"].dropna().unique()
                    if str(x).strip() != ""
                ]
            )
            if "Üniversite" in df.columns
            else []
        )
        secilen_unis = st.multiselect(
            "Üniversite Seçin",
            universiteler,
            placeholder="Üni seç veya yaz...",
            label_visibility="collapsed",
        )

    with f3:
        st.caption("HANGİ BÖLÜM")
        bolumler = (
            sorted(
                [
                    str(x)
                    for x in df["Bölüm"].dropna().unique()
                    if str(x).strip() != ""
                ]
            )
            if "Bölüm" in df.columns
            else []
        )
        secilen_bolumler = st.multiselect(
            "Bölüm Seçin",
            bolumler,
            placeholder="Bölüm seç veya yaz...",
            label_visibility="collapsed",
        )

    with f4:
        st.caption("PARA VERCEK MİSİN (BURS DURUMU)")
        burs_secimi = st.selectbox(
            "Burs Durumu",
            ["TÜMÜ", "Burslu", "%50 İndirimli", "%25 İndirimli", "Ücretli"],
            label_visibility="collapsed",
        )

    st.write("")
    btn_col1, btn_col2, btn_col3 = st.columns([3, 6, 3])
    with btn_col2:
        if st.button("🚀 BUL LAN", key="btn_search_main", use_container_width=True):
            st.session_state.arama_yapildi = True

    st.markdown("</div>", unsafe_allow_html=True)


tab1, tab2 = st.tabs(
    [
        "🔍 SONUÇLAR ALLAH BÜYÜK",
        "📋 Yandık Listesi (Kaydedilenler)",
    ]
)

with tab1:
    if not st.session_state.arama_yapildi:
        st.info("👈 Filtreleri ayarla, sonra yeşil **BUL LAN** butonuna bas kanka!")
    else:
        temp_df = df.copy()

        # Puan Türü Filtresi
        if secilen_puan != "TÜMÜ" and "Puan_Türü" in temp_df.columns:
            temp_df = temp_df[
                temp_df["Puan_Türü"].astype(str).str.upper() == secilen_puan
            ]

        # Şehir Filtresi
        if secilen_sehirler and "Şehir" in temp_df.columns:
            secilen_sehirler_tr = [tr_lower(s) for s in secilen_sehirler]
            temp_df = temp_df[
                temp_df["Şehir"].apply(
                    lambda x: any(s in tr_lower(str(x)) for s in secilen_sehirler_tr)
                )
            ]

        # Üniversite Filtresi (Açılır Liste Çoklu Seçim)
        if secilen_unis and "Üniversite" in temp_df.columns:
            secilen_unis_tr = [tr_lower(u) for u in secilen_unis]
            temp_df = temp_df[
                temp_df["Üniversite"].apply(
                    lambda x: any(u in tr_lower(str(x)) for u in secilen_unis_tr)
                )
            ]

        # Bölüm Filtresi (Açılır Liste Çoklu Seçim)
        if secilen_bolumler and "Bölüm" in temp_df.columns:
            secilen_bolumler_tr = [tr_lower(b) for b in secilen_bolumler]
            temp_df = temp_df[
                temp_df["Bölüm"].apply(
                    lambda x: any(b in tr_lower(str(x)) for b in secilen_bolumler_tr)
                )
            ]

        # Burs / İndirim Filtresi
        if burs_secimi != "TÜMÜ" and "Bölüm" in temp_df.columns:
            burs_query = tr_lower(burs_secimi)
            temp_df = temp_df[
                temp_df["Bölüm"].apply(lambda x: burs_query in tr_lower(str(x)))
            ]

        if temp_df.empty:
            st.warning(
                "⚠️ Kanka aradığın kriterlerde sonuç çıkmadı! Seçimleri biraz gevşetip tekrar 'BUL LAN'a bas."
            )
        else:
            st.markdown(f"### 📍 Aha Sana **{len(temp_df)}** Tane Yer Buldum")

            sira_col = "Sıralama" if "Sıralama" in temp_df.columns else "sıralama"
            gosterilecek_df = temp_df.head(100)

            for idx, row in gosterilecek_df.iterrows():
                bolum_sira = row.get(sira_col, 0)
                durum, badge_class = olasilik_hesapla(ogrenci_sira, bolum_sira)

                uni_adi = row.get("Üniversite", "Üniversite Belirtilmemiş")
                bolum_adi = row.get("Bölüm", "Bölüm Belirtilmemiş")
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
                            <div class="stat-value" style="color: #ffed00;">{f"{int(bolum_sira):,}" if pd.notna(bolum_sira) and str(bolum_sira).replace('.','',1).isdigit() else bolum_sira}</div>
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
        st.warning("Boş boş bakma kanka, bir iki bölüm ekle önce.")
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
