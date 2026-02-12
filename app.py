import streamlit as st
import time
from src.ingestion import ingest_all_docs
from src.agent import LegalAgent
import os

# Sayfa Ayarları
st.set_page_config(page_title="Multi-Law Legal Agent", page_icon="⚖️", layout="centered")
st.title("Komşuluk & Apartman Hukuku Asistanı")
st.caption("Kat Mülkiyeti • Borçlar Kanunu • Anayasa")

# --- 1. SİSTEM BAŞLATMA ---
if "agent_system" not in st.session_state:
    with st.spinner("Sistem kuruluyor..."):
        try:
            # Otomatik Ingestion (Eksik veri varsa tamamlar)
            ingest_all_docs(force_recreate=False)
            
            # Ajanı Başlat
            st.session_state.agent_system = LegalAgent()
            
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
                cevap, kaynaklar = st.session_state.agent_system.ask(prompt)
                
                # 2. Cevabı yazdır
                st.markdown(cevap)
                
                # 3. Şeffaflık: Hangi kanun kitabını açtığını kullanıcıya göster
                if kaynaklar:
                    st.info(f"🔍 Başvurulan Kaynaklar: {', '.join(kaynaklar)}")
                
                # 4. Geçmişe kaydet
                st.session_state.messages.append({"role": "assistant", "content": cevap})
            
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")

