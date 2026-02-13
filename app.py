import streamlit as st
import time
from src.agent import LegalRAG

# ==============================================================================
# 1. SAYFA AYARLARI (Page Config)
# ==============================================================================
st.set_page_config(page_title="Multi-Law Legal Agent", page_icon="⚖️", layout="centered")
st.title("Komşuluk & Apartman Hukuku Asistanı")
st.caption("KMK • TBK • TMK • Yönetmelikler")

# ==============================================================================
# 2. SİSTEM BAŞLATMA (Initialization)
# ==============================================================================
# RAG sistemini sadece bir kere başlatıp hafızada (session_state) tutuyoruz.
if "rag_system" not in st.session_state:
    with st.spinner("Yasal Asistan hazırlanıyor..."):
        try:
            # Arka plandaki Yapay Zeka motorunu başlat
            st.session_state.rag_system = LegalRAG()
            
            st.success("Sistem Hazır!")
            time.sleep(0.5)
            st.rerun()
        except Exception as e:
            st.error(f"Sistem başlatılamadı: {e}")
            st.stop()


# ==============================================================================
# 3. SOHBET GEÇMİŞİ (Chat History)
# ==============================================================================
# Mesajları ekranda tutmak için liste oluşturuyoruz
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Merhabalar. Size hangi kanun kapsamında yardımcı olabilirim?"}]

# Geçmiş mesajları ekrana yeniden yazdır
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ==============================================================================
# 4. KULLANICI ETKİLEŞİMİ (User Input)
# ==============================================================================
if prompt := st.chat_input("Sorunuzu yazın..."):
    # Kullanıcı mesajını ekle ve göster
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Asistan Cevabı
    with st.chat_message("assistant"):
        with st.spinner("Kanunlar taranıyor..."):
            try:
                # ------------------------------------------------------------------
                # BU SATIR TÜM SİHRİN GERÇEKLEŞTİĞİ YERDİR!
                # 1. Router: Hangi kanuna bakayım?
                # 2. Retriever: Bilgiyi bul
                # 3. Generator: Cevabı yaz
                # ------------------------------------------------------------------
                cevap, kaynaklar = st.session_state.rag_system.generate_answer(prompt)
                
                # Cevabı ekrana yaz
                st.markdown(cevap)
                
                # Kaynakları göster (Şeffaflık)
                if kaynaklar:
                    with st.expander("📚 Başvurulan Kaynaklar"):
                        for i, doc in enumerate(kaynaklar):
                            st.markdown(f"**Kaynak {i+1}:**")
                            # Çok uzun metinleri kırp (UI düzgün görünsün)
                            clean_doc = doc if len(doc) < 500 else doc[:500] + "..."
                            st.markdown(f"> {clean_doc}")
                            st.divider()
                
                # Cevabı hafızaya kaydet
                st.session_state.messages.append({"role": "assistant", "content": cevap})
            
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")
