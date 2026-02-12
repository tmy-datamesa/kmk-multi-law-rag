# 🤖 Multi-Law Agentic RAG (V3)

Bu proje, tek bir kanun yerine **birden fazla hukuk kaynağını (KMK, TBK, Anayasa vb.)** yönetebilen, "Ajan (Agent)" tabanlı bir yapay zeka sistemidir.

## 🌟 Nedir Farkı? (V2 vs V3)

*   **V2 (Eski):** Sadece Kat Mülkiyeti Kanunu'nu bilen, "tek fonksiyonlu" bir araçtı.
*   **V3 (Yeni):** Akıllı bir **Yönlendirici (Router)** içerir. Sorunuza bakar, hangi kanunun uzmanlık alanına girdiğine karar verir ve o kanunu açıp okur.

Örneğin:
*   *"Aidat ödemezsem ne olur?"* -> **Otomatik olarak KMK (Kat Mülkiyeti)** kitabını açar.
*   *"Kiracı depozitosu iade edilmedi"* -> **Otomatik olarak TBK (Borçlar Kanunu)** kitabını açar.

## 📂 Mimari (Agentic RAG)

Sistem **"OpenAI Tools"** teknolojisini kullanarak çalışır:
1.  **Agent**: Kullanıcı sorusunu analiz eder.
2.  **Tools**:
    *   `search_kmk()`: Kat Mülkiyeti Kanunu (Ana Kaynak).
    *   `search_tbk()`: Türk Borçlar Kanunu (Kira/Komşuluk).
    *   `search_tmk()`: Türk Medeni Kanunu (Mülkiyet/Komşuluk Hakları).
    *   `search_asansor()`: Asansör Bakım Yönetmeliği.
    *   `search_yangin()`: Yangın Koruma Yönetmeliği.
    *   `search_anayasa()`: Anayasa (Haklar).
3.  **RAG Engine**: Seçilen alet çalışır, veritabanından bilgi çeker ve ajana verir.


## 🛠️ Kurulum

```bash
# 1. Klasöre girin
cd kmk-multi-law-rag

# 2. Kurulumu yapın
make setup

# 3. .env dosyasını ayarlayın
# (OPENAI_API_KEY ve CHROMA_API_KEY gereklidir)

# 4. Verileri yükleyin (PDF'ler taranır)
make ingest

# 5. Başlatın
make run
```

## 📚 Yeni Kanun Nasıl Eklenir?
Sadece `src/config.py` dosyasına yeni bir blok eklemeniz yeterlidir:
```python
"ticaret_kanunu": {
    "name": "Türk Ticaret Kanunu",
    "description": "Şirketler ve ticari işler için...",
    "path": "data/ttk.pdf",
    "collection": "law_ttk"
}
```
Sistem otomatik olarak bunu tanır ve Ajanın yeteneklerine ekler.
