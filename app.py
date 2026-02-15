import streamlit as st
import time
from src.agent import LegalRAG
from src import config

# ==============================================================================
# 1. SAYFA AYARLARI (Page Config)
# ==============================================================================
st.set_page_config(
    page_title="Multi-Law Legal Agent",
    page_icon="⚖️",
    layout="centered"
)
st.title("⚖️ Komşuluk & Apartman Hukuku Asistanı")
st.caption("Uzmanlık Alanı: Site Yönetimi, Komşuluk İlişkileri ve Apartman Sorunları (KMK Odaklı)")

# ==============================================================================
# 1.5. YAN MENÜ (Sidebar) - Teknik Bilgiler
# ==============================================================================
with st.sidebar:
    st.header("🛠️ Teknik Detaylar")
    st.caption("Bu ayarlar sabittir, sadece bilgi amaçlı gösterilmektedir.")
    
    st.markdown("### 🧠 Model Yapısı")
    st.markdown(f"**LLM:** `{config.LLM_MODEL}`")
    st.markdown(f"**Embedding:** `{config.EMBEDDING_MODEL}`")
    st.markdown(f"**Vektör DB:** `ChromaDB` (Local)")
    
    st.divider()
    
    st.markdown("### ⚙️ Parametreler")
    # Temperature'ı görselleştirmek için disabled slider kullanıyoruz
    st.slider(
        label="Yaratıcılık (Temperature)",
        min_value=0.0, 
        max_value=1.0, 
        value=config.TEMPERATURE,
        disabled=True, 
        help="Modelin belirlenmiş yaratıcılık seviyesi (0.0 = Deterministik)"
    )
    
    st.markdown(f"**Top-K:** `{config.TOP_K}` (Getirilen Parça Sayısı)")
    st.markdown(f"**Chunk Size:** `{config.CHUNK_SIZE}` karakter")

# ==============================================================================
# 2. SİSTEM BAŞLATMA (Initialization)
# ==============================================================================
# Streamlit her etkileşimde kodu baştan çalıştırır.
# Bu yüzden RAG sistemini "Session State" içinde tutuyoruz ki her seferinde tekrar yüklenmesin.
if "rag_system" not in st.session_state:
    with st.spinner("Yasal Asistan ve Kütüphane hazırlanıyor..."):
        try:
            # Arka plandaki Yapay Zeka motorunu başlat (Agent sınıfı)
            st.session_state.rag_system = LegalRAG()
            
            st.success("Sistem Hazır! Sorunuzu sorabilirsiniz.")
            time.sleep(1) # Kullanıcının başarı mesajını görmesi için kısa bekleme
            st.rerun()    # Sayfayı yenile ve temiz bir başlangıç yap
        except Exception as e:
            st.error(f"Sistem başlatılamadı: {e}")
            st.stop()

# ==============================================================================
# 3. SOHBET GEÇMİŞİ (Chat History)
# ==============================================================================
# Mesajları ekranda tutmak için liste oluşturuyoruz
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Merhabalar. Apartman yönetimi, kiracı hakları veya komşuluk ilişkileri hakkında sorularınızı yanıtlayabilirim."}
    ]

# Geçmiş mesajları ekrana yeniden yazdır (Her rerun'da çalışır)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==============================================================================
# 4. KULLANICI ETKİLEŞİMİ (User Input)
# ==============================================================================
if prompt := st.chat_input("Sorunuzu buraya yazın..."):
    # 1. Kullanıcı mesajını ekrana ekle
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Asistan Cevabını Oluştur
    with st.chat_message("assistant"):
        with st.spinner("Kanun maddeleri taranıyor..."):
            try:
                # --- RAG AKIŞI BAŞLIYOR ---
                # Ajan; planlama yapar, gerekli kanunu bulur, okur ve cevaplar.
                cevap, kaynaklar = st.session_state.rag_system.generate_answer(prompt)
                
                # Cevabı Göster
                st.markdown(cevap)
                
                # Şeffaflık: Hangi kaynaktan bilgi alındığını göster
                if kaynaklar:
                    with st.expander("📚 Başvurulan Kanun Maddeleri ve Kaynaklar"):
                        for i, doc in enumerate(kaynaklar):
                            # doc artık bir sözlük: {'mid': ..., 'content': ..., 'metadata': ...}
                            source_name = doc['metadata']['doc_name']
                            content = doc['content']
                            
                            st.markdown(f"**Kaynak {i+1}: {source_name}**")
                            # Çok uzun metinleri görsel açıdan kırp
                            clean_doc = content if len(content) < 600 else content[:600] + "..."
                            st.markdown(f"> {clean_doc}")
                            st.divider()
                
                # Cevabı hafızaya kaydet (Geçmişte kalsın)
                st.session_state.messages.append({"role": "assistant", "content": cevap})
            
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")
