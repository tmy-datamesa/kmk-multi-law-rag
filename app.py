import streamlit as st
import time
from src.agent import LegalRAG

# Sayfa Ayarları
st.set_page_config(page_title="Multi-Law Legal Agent", page_icon="⚖️", layout="centered")
st.title("Komşuluk & Apartman Hukuku Asistanı")
st.caption("KMK • TBK • TMK • Yönetmelikler")

# --- 1. SİSTEM BAŞLATMA ---
if "rag_system" not in st.session_state:
    with st.spinner("Sistem kuruluyor..."):
        try:
            # Ajanı Başlat
            st.session_state.rag_system = LegalRAG()
            
            st.success("Ajan Göreve Hazır!")
            time.sleep(0.5)
            st.rerun()
        except Exception as e:
            st.error(f"Sistem hatası: {e}")
            st.stop()


# --- 2. SOHBET ARAYÜZÜ ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Merhabalar. Size hangi kanun kapsamında yardımcı olabilirim?"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Sorunuzu yazın..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Asistan Cevabı
    with st.chat_message("assistant"):
        with st.spinner("Düşünüyor..."):
            try:
                # 1. Ajan'a sor (Arka planda hangi kanuna bakacağına o karar verir)
                cevap, kaynaklar = st.session_state.rag_system.generate_answer(prompt)
                
                # 2. Cevabı yazdır
                st.markdown(cevap)
                
                # 3. Kaynak Gösterimi (Kullanıcı İsteği)
                if kaynaklar:
                    with st.expander("📚 Kaynaklar"):
                        for i, doc in enumerate(kaynaklar):
                            st.markdown(f"**Kaynak {i+1}:**")
                            # Çok uzunsa kısaltalım
                            clean_doc = doc if len(doc) < 500 else doc[:500] + "..."
                            st.markdown(f"> {clean_doc}")
                            st.divider()
                
                # 4. Geçmişe kaydet
                st.session_state.messages.append({"role": "assistant", "content": cevap})
            
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")

