from logos_data import LOGOS
import streamlit as st
import sqlite3
from datetime import datetime, date
import pandas as pd
import time

# Sayfa yapılandırması
st.set_page_config(
    page_title="Kişisel Günlük",
    page_icon="📔",
    layout="wide"
)

# Veritabanı bağlantısı
def get_connection():
    conn = sqlite3.connect('gunluk.db')
    return conn

# Veritabanı tablolarını oluştur
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Günlük tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gunluk (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih DATE NOT NULL,
            baslik TEXT,
            icerik TEXT NOT NULL,
            olusturma_zamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Haftalık şarkılar tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sarkilar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih DATE NOT NULL,
            sarki_adi TEXT NOT NULL,
            sanatci TEXT,
            notlar TEXT,
            olusturma_zamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Kitaplar tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kitaplar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih DATE NOT NULL,
            kitap_adi TEXT NOT NULL,
            yazar TEXT,
            sayfa_sayisi INTEGER,
            durum TEXT,
            notlar TEXT,
            olusturma_zamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Filmler tablosu
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS filmler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih DATE NOT NULL,
            film_adi TEXT NOT NULL,
            yonetmen TEXT,
            yil INTEGER,
            puan INTEGER,
            notlar TEXT,
            olusturma_zamani TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Veritabanını başlat
create_tables()

# Stil - TAM YEŞİL TEMA
st.markdown("""
    <style>
    /* Streamlit'in tüm container'larını yeşil yap */
    .stApp {
        background: linear-gradient(135deg, #1a3a2e 0%, #2d5f4a 100%) !important;
    }
    
    /* Block container */
    .block-container {
        background: transparent !important;
    }
    
    /* Ana sayfa arka planı */
    .main {
        background: transparent !important;
        padding: 2rem;
    }
    
    /* Tüm yazıları pembe yap */
    .main *, .stApp * {
        color: #ff69b4 !important;
    }
    
    /* Başlıklar */
    h1, h2, h3, h4, h5, h6 {
        color: #ff1493 !important;
    }
    
    /* TextArea */
    .stTextArea textarea {
        font-size: 16px;
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #ff69b4 !important;
        border: 1px solid rgba(255, 105, 180, 0.5) !important;
    }
    
    /* Text Input */
    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #ff69b4 !important;
        border: 1px solid rgba(255, 105, 180, 0.5) !important;
    }
    
    /* Number Input */
    .stNumberInput input {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #ff69b4 !important;
        border: 1px solid rgba(255, 105, 180, 0.5) !important;
    }
    
    /* Select Box */
    .stSelectbox select {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #ff69b4 !important;
        border: 1px solid rgba(255, 105, 180, 0.5) !important;
    }
    
    /* Date Input */
    .stDateInput input {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: #ff69b4 !important;
        border: 1px solid rgba(255, 105, 180, 0.5) !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: rgba(45, 95, 74, 0.5) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a3a2e 0%, #2d5f4a 100%) !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #ff69b4 !important;
    }
    
    /* Info box */
    .stAlert {
        background-color: rgba(45, 95, 74, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    /* Metric */
    [data-testid="stMetricValue"] {
        color: #ff1493 !important;
    }
    
    /* Form */
    .stForm {
        background-color: rgba(45, 95, 74, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px;
        padding: 20px;
    }
    
    /* Beyaz arka planları gizle */
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    
    /* Animasyonlar */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
    
    .intro-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        width: 100vw;
        position: fixed;
        top: 0;
        left: 0;
        background: linear-gradient(135deg, #1a3a2e 0%, #2d5f4a 100%);
        z-index: 9999;
        animation: fadeIn 0.5s ease-in;
    }
    .intro-text {
        font-size: 10rem;
        font-weight: bold;
        background: linear-gradient(135deg, #4ade80 0%, #22c55e 50%, #16a34a 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 1rem;
    }
    .fade-out-letter {
        animation: fadeOut 1s ease-out forwards;
    }
    </style>
""", unsafe_allow_html=True)

# Session state için intro ve kategori kontrolü
if 'intro_gosterildi' not in st.session_state:
    st.session_state.intro_gosterildi = False
    st.session_state.animasyon_asamasi = 1

if 'secili_kategori' not in st.session_state:
    st.session_state.secili_kategori = None

# INTRO ANIMASYONU
if not st.session_state.intro_gosterildi:
    intro_placeholder = st.empty()
    
    # Aşama 1: NISA göster (2 saniye)
    if st.session_state.animasyon_asamasi == 1:
        with intro_placeholder.container():
            st.markdown("""
                <div class='intro-container'>
                    <div class='intro-text'>NISA</div>
                </div>
            """, unsafe_allow_html=True)
        time.sleep(2)
        st.session_state.animasyon_asamasi = 2
        st.rerun()
    
    # Aşama 2: N ve S yavaşça kaybolsun (1.5 saniye)
    elif st.session_state.animasyon_asamasi == 2:
        with intro_placeholder.container():
            st.markdown("""
                <div class='intro-container'>
                    <div class='intro-text'>
                        <span class='fade-out-letter'>N</span>I<span class='fade-out-letter'>S</span>A
                    </div>
                </div>
            """, unsafe_allow_html=True)
        time.sleep(1.5)
        st.session_state.animasyon_asamasi = 3
        st.rerun()
    
    # Aşama 3: AI göster (2 saniye)
    elif st.session_state.animasyon_asamasi == 3:
        with intro_placeholder.container():
            st.markdown("""
                <div class='intro-container'>
                    <div class='intro-text'>AI</div>
                </div>
            """, unsafe_allow_html=True)
        time.sleep(2)
        st.session_state.intro_gosterildi = True
        st.session_state.animasyon_asamasi = 1
        st.rerun()

# Ana Sayfa - Kategori Seçimi
if st.session_state.secili_kategori is None:
    st.title("📔 Kişisel Günlük Uygulaması")
    st.markdown("### 🎯 Hangi kategoriye gitmek istersiniz?")
    st.markdown("---")
    
    # 4 kategori kartı - 2x2 düzen - YEŞİL TONLARI VE LOGOLAR
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%); 
                        padding: 2rem; border-radius: 15px; text-align: center; 
                        color: white; margin-bottom: 20px; box-shadow: 0 6px 20px rgba(22, 163, 74, 0.4);'>
                <div style='text-align: center; margin-bottom: 1rem;'>
                    <img src='data:image/png;base64,{LOGOS["gunluk"]}' style='max-width: 150px;'>
                </div>
                <div style='font-size: 1.8rem; font-weight: bold; margin-bottom: 0.5rem;'>GÜNLÜK</div>
                <div style='font-size: 1rem; opacity: 0.95;'>Günlük düşüncelerini kaydet</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("📝 GÜNLÜK'e Git", key="btn_gunluk", use_container_width=True, type="primary"):
            st.session_state.secili_kategori = "📝 Günlük"
            st.rerun()
    
    with col2:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #059669 0%, #10b981 100%); 
                        padding: 2rem; border-radius: 15px; text-align: center; 
                        color: white; margin-bottom: 20px; box-shadow: 0 6px 20px rgba(5, 150, 105, 0.4);'>
                <div style='text-align: center; margin-bottom: 1rem;'>
                    <img src='data:image/png;base64,{LOGOS["muzik"]}' style='max-width: 150px;'>
                </div>
                <div style='font-size: 1.8rem; font-weight: bold; margin-bottom: 0.5rem;'>MÜZİK</div>
                <div style='font-size: 1rem; opacity: 0.95;'>Sevdiğin şarkıları kaydet</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎵 MÜZİK'e Git", key="btn_muzik", use_container_width=True, type="primary"):
            st.session_state.secili_kategori = "🎵 Haftalık Şarkılar"
            st.rerun()
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #14b8a6 0%, #2dd4bf 100%); 
                        padding: 2rem; border-radius: 15px; text-align: center; 
                        color: white; margin-bottom: 20px; box-shadow: 0 6px 20px rgba(20, 184, 166, 0.4);'>
                <div style='text-align: center; margin-bottom: 1rem;'>
                    <img src='data:image/png;base64,{LOGOS["kitap"]}' style='max-width: 150px;'>
                </div>
                <div style='font-size: 1.8rem; font-weight: bold; margin-bottom: 0.5rem;'>KİTAP</div>
                <div style='font-size: 1rem; opacity: 0.95;'>Okuduğun kitapları takip et</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("📚 KİTAP'a Git", key="btn_kitap", use_container_width=True, type="primary"):
            st.session_state.secili_kategori = "📚 Kitaplar"
            st.rerun()
    
    with col4:
        st.markdown(f"""
            <div style='background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%); 
                        padding: 2rem; border-radius: 15px; text-align: center; 
                        color: white; margin-bottom: 20px; box-shadow: 0 6px 20px rgba(13, 148, 136, 0.4);'>
                <div style='text-align: center; margin-bottom: 1rem;'>
                    <img src='data:image/png;base64,{LOGOS["film"]}' style='max-width: 150px;'>
                </div>
                <div style='font-size: 1.8rem; font-weight: bold; margin-bottom: 0.5rem;'>FİLM</div>
                <div style='font-size: 1rem; opacity: 0.95;'>İzlediğin filmleri değerlendir</div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎬 FİLM'e Git", key="btn_film", use_container_width=True, type="primary"):
            st.session_state.secili_kategori = "🎬 Filmler"
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #ff69b4; margin-top: 2rem;'>📔 Tüm verileriniz güvende!</div>",
        unsafe_allow_html=True
    )
    
    st.stop()

# Kategori seçildiyse devam et
kategori = st.session_state.secili_kategori

# Sidebar
with st.sidebar:
    st.header("📋 Navigasyon")
    
    # Ana sayfaya dön butonu
    if st.button("🏠 Ana Sayfaya Dön", use_container_width=True, type="secondary"):
        st.session_state.secili_kategori = None
        st.rerun()
    
    st.markdown("---")
    
    # Mevcut kategori
    st.info(f"**Şu an:** {kategori}")
    
    st.markdown("---")
    st.subheader("⚙️ İşlemler")
    islem = st.radio(
        "Ne yapmak istersiniz?",
        ["Yeni Ekle", "Geçmişi Görüntüle"]
    )

# Başlık
st.title("📔 Kişisel Günlük Uygulaması")
st.markdown("---")

# ===== GÜNLÜK KATEGORİSİ =====
if kategori == "📝 Günlük":
    st.header("📝 Günlük")
    
    if islem == "Yeni Ekle":
        st.subheader("Yeni Günlük Girişi")
        
        with st.form("gunluk_form"):
            tarih = st.date_input("Tarih", value=date.today())
            baslik = st.text_input("Başlık (İsteğe bağlı)")
            icerik = st.text_area("Günlük İçeriği", height=300, placeholder="Bugün neler oldu?")
            
            submit = st.form_submit_button("💾 Kaydet", use_container_width=True)
            
            if submit:
                if icerik:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO gunluk (tarih, baslik, icerik) VALUES (?, ?, ?)",
                        (tarih, baslik, icerik)
                    )
                    conn.commit()
                    conn.close()
                    st.success("✅ Günlük kaydedildi!")
                else:
                    st.error("⚠️ Lütfen içerik yazın!")
    
    else:  # Geçmişi Görüntüle
        st.subheader("Geçmiş Günlükler")
        
        conn = get_connection()
        df = pd.read_sql_query(
            "SELECT * FROM gunluk ORDER BY tarih DESC", 
            conn
        )
        conn.close()
        
        if not df.empty:
            # Arama ve filtreleme
            col1, col2 = st.columns([3, 1])
            with col1:
                arama = st.text_input("🔍 Ara (başlık veya içerik)")
            with col2:
                st.write("")
                st.write("")
                if st.button("🗑️ Tümünü Sil", type="secondary"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM gunluk")
                    conn.commit()
                    conn.close()
                    st.rerun()
            
            if arama:
                df = df[
                    df['baslik'].str.contains(arama, case=False, na=False) |
                    df['icerik'].str.contains(arama, case=False, na=False)
                ]
            
            for _, row in df.iterrows():
                with st.expander(f"📅 {row['tarih']} - {row['baslik'] if row['baslik'] else 'Başlıksız'}"):
                    st.write(row['icerik'])
                    
                    col1, col2 = st.columns([6, 1])
                    with col2:
                        if st.button("🗑️", key=f"del_gunluk_{row['id']}"):
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.execute("DELETE FROM gunluk WHERE id = ?", (row['id'],))
                            conn.commit()
                            conn.close()
                            st.rerun()
        else:
            st.info("Henüz günlük kaydı yok.")

# ===== ŞARKILAR KATEGORİSİ =====
elif kategori == "🎵 Haftalık Şarkılar":
    st.header("🎵 Haftalık En Sevdiğim Şarkılar")
    
    if islem == "Yeni Ekle":
        st.subheader("Yeni Şarkı Ekle")
        
        with st.form("sarki_form"):
            tarih = st.date_input("Tarih", value=date.today())
            sarki_adi = st.text_input("Şarkı Adı *", placeholder="Şarkı adını girin")
            sanatci = st.text_input("Sanatçı", placeholder="Sanatçı adı")
            notlar = st.text_area("Notlar / Neden sevdim?", height=150, placeholder="Bu şarkıyı neden sevdin?")
            
            submit = st.form_submit_button("💾 Kaydet", use_container_width=True)
            
            if submit:
                if sarki_adi:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO sarkilar (tarih, sarki_adi, sanatci, notlar) VALUES (?, ?, ?, ?)",
                        (tarih, sarki_adi, sanatci, notlar)
                    )
                    conn.commit()
                    conn.close()
                    st.success("✅ Şarkı kaydedildi!")
                else:
                    st.error("⚠️ Lütfen şarkı adını girin!")
    
    else:  # Geçmişi Görüntüle
        st.subheader("Şarkı Geçmişi")
        
        conn = get_connection()
        df = pd.read_sql_query(
            "SELECT * FROM sarkilar ORDER BY tarih DESC", 
            conn
        )
        conn.close()
        
        if not df.empty:
            col1, col2 = st.columns([3, 1])
            with col2:
                st.write("")
                st.write("")
                if st.button("🗑️ Tümünü Sil", type="secondary"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM sarkilar")
                    conn.commit()
                    conn.close()
                    st.rerun()
            
            for _, row in df.iterrows():
                with st.expander(f"🎵 {row['sarki_adi']} - {row['sanatci'] if row['sanatci'] else 'Bilinmeyen Sanatçı'}"):
                    st.write(f"**📅 Tarih:** {row['tarih']}")
                    if row['notlar']:
                        st.write(f"**💭 Notlar:** {row['notlar']}")
                    
                    if st.button("🗑️", key=f"del_sarki_{row['id']}"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM sarkilar WHERE id = ?", (row['id'],))
                        conn.commit()
                        conn.close()
                        st.rerun()
        else:
            st.info("Henüz şarkı kaydı yok.")

# ===== KİTAPLAR KATEGORİSİ =====
elif kategori == "📚 Kitaplar":
    st.header("📚 Okuduğum Kitaplar")
    
    if islem == "Yeni Ekle":
        st.subheader("Yeni Kitap Ekle")
        
        with st.form("kitap_form"):
            tarih = st.date_input("Tarih", value=date.today())
            kitap_adi = st.text_input("Kitap Adı *", placeholder="Kitap adını girin")
            yazar = st.text_input("Yazar", placeholder="Yazar adı")
            
            col1, col2 = st.columns(2)
            with col1:
                sayfa_sayisi = st.number_input("Sayfa Sayısı", min_value=0, value=0)
            with col2:
                durum = st.selectbox("Durum", ["Okudum", "Okuyorum", "Okuyacağım"])
            
            notlar = st.text_area("Notlar / İnceleme", height=200, placeholder="Kitap hakkında düşünceleriniz...")
            
            submit = st.form_submit_button("💾 Kaydet", use_container_width=True)
            
            if submit:
                if kitap_adi:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO kitaplar (tarih, kitap_adi, yazar, sayfa_sayisi, durum, notlar) VALUES (?, ?, ?, ?, ?, ?)",
                        (tarih, kitap_adi, yazar, sayfa_sayisi, durum, notlar)
                    )
                    conn.commit()
                    conn.close()
                    st.success("✅ Kitap kaydedildi!")
                else:
                    st.error("⚠️ Lütfen kitap adını girin!")
    
    else:  # Geçmişi Görüntüle
        st.subheader("Kitap Listesi")
        
        conn = get_connection()
        df = pd.read_sql_query(
            "SELECT * FROM kitaplar ORDER BY tarih DESC", 
            conn
        )
        conn.close()
        
        if not df.empty:
            # Filtre
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                durum_filtre = st.selectbox("Durum Filtrele", ["Tümü", "Okudum", "Okuyorum", "Okuyacağım"])
            with col3:
                st.write("")
                st.write("")
                if st.button("🗑️ Tümünü Sil", type="secondary"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM kitaplar")
                    conn.commit()
                    conn.close()
                    st.rerun()
            
            if durum_filtre != "Tümü":
                df = df[df['durum'] == durum_filtre]
            
            # İstatistikler
            st.markdown("### 📊 İstatistikler")
            col1, col2, col3 = st.columns(3)
            with col1:
                okudum = len(df[df['durum'] == 'Okudum'])
                st.metric("Okuduğum Kitaplar", okudum)
            with col2:
                okuyorum = len(df[df['durum'] == 'Okuyorum'])
                st.metric("Okumakta", okuyorum)
            with col3:
                okuyacagim = len(df[df['durum'] == 'Okuyacağım'])
                st.metric("Okuyacağım", okuyacagim)
            
            st.markdown("---")
            
            for _, row in df.iterrows():
                durum_emoji = {"Okudum": "✅", "Okuyorum": "📖", "Okuyacağım": "📝"}
                with st.expander(f"{durum_emoji.get(row['durum'], '📚')} {row['kitap_adi']} - {row['yazar'] if row['yazar'] else 'Bilinmeyen Yazar'}"):
                    st.write(f"**📅 Tarih:** {row['tarih']}")
                    st.write(f"**📄 Sayfa:** {row['sayfa_sayisi']}")
                    st.write(f"**📊 Durum:** {row['durum']}")
                    if row['notlar']:
                        st.write(f"**💭 Notlar:** {row['notlar']}")
                    
                    if st.button("🗑️", key=f"del_kitap_{row['id']}"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM kitaplar WHERE id = ?", (row['id'],))
                        conn.commit()
                        conn.close()
                        st.rerun()
        else:
            st.info("Henüz kitap kaydı yok.")

# ===== FİLMLER KATEGORİSİ =====
elif kategori == "🎬 Filmler":
    st.header("🎬 İzlediğim Filmler")
    
    if islem == "Yeni Ekle":
        st.subheader("Yeni Film Ekle")
        
        with st.form("film_form"):
            tarih = st.date_input("İzleme Tarihi", value=date.today())
            film_adi = st.text_input("Film Adı *", placeholder="Film adını girin")
            yonetmen = st.text_input("Yönetmen", placeholder="Yönetmen adı")
            
            col1, col2 = st.columns(2)
            with col1:
                yil = st.number_input("Yapım Yılı", min_value=1900, max_value=2030, value=2024)
            with col2:
                puan = st.slider("Puanım", 1, 10, 5)
            
            notlar = st.text_area("İnceleme / Düşünceler", height=200, placeholder="Film hakkında düşünceleriniz...")
            
            submit = st.form_submit_button("💾 Kaydet", use_container_width=True)
            
            if submit:
                if film_adi:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO filmler (tarih, film_adi, yonetmen, yil, puan, notlar) VALUES (?, ?, ?, ?, ?, ?)",
                        (tarih, film_adi, yonetmen, yil, puan, notlar)
                    )
                    conn.commit()
                    conn.close()
                    st.success("✅ Film kaydedildi!")
                else:
                    st.error("⚠️ Lütfen film adını girin!")
    
    else:  # Geçmişi Görüntüle
        st.subheader("Film Geçmişi")
        
        conn = get_connection()
        df = pd.read_sql_query(
            "SELECT * FROM filmler ORDER BY tarih DESC", 
            conn
        )
        conn.close()
        
        if not df.empty:
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                puan_filtre = st.selectbox("Puana Göre Filtrele", ["Tümü"] + list(range(1, 11)))
            with col3:
                st.write("")
                st.write("")
                if st.button("🗑️ Tümünü Sil", type="secondary"):
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM filmler")
                    conn.commit()
                    conn.close()
                    st.rerun()
            
            if puan_filtre != "Tümü":
                df = df[df['puan'] == puan_filtre]
            
            # İstatistikler
            st.markdown("### 📊 İstatistikler")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Toplam Film", len(df))
            with col2:
                if len(df) > 0:
                    st.metric("Ortalama Puan", f"{df['puan'].mean():.1f}/10")
                else:
                    st.metric("Ortalama Puan", "0/10")
            with col3:
                if len(df) > 0:
                    en_yuksek = df.loc[df['puan'].idxmax()]
                    st.metric("En Yüksek Puan", f"{en_yuksek['puan']}/10")
                else:
                    st.metric("En Yüksek Puan", "0/10")
            
            st.markdown("---")
            
            for _, row in df.iterrows():
                yildiz = "⭐" * row['puan']
                with st.expander(f"🎬 {row['film_adi']} ({row['yil']}) - {yildiz}"):
                    st.write(f"**📅 İzleme Tarihi:** {row['tarih']}")
                    st.write(f"**🎥 Yönetmen:** {row['yonetmen'] if row['yonetmen'] else 'Bilinmiyor'}")
                    st.write(f"**⭐ Puanım:** {row['puan']}/10")
                    if row['notlar']:
                        st.write(f"**💭 İnceleme:** {row['notlar']}")
                    
                    if st.button("🗑️", key=f"del_film_{row['id']}"):
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM filmler WHERE id = ?", (row['id'],))
                        conn.commit()
                        conn.close()
                        st.rerun()
        else:
            st.info("Henüz film kaydı yok.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #ff69b4;'>📔 Kişisel Günlük Uygulaması - Tüm verileriniz güvende!</div>",
    unsafe_allow_html=True
)