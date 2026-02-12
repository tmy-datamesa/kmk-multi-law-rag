import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# ==============================================================================
# API VE İSTEMCİ AYARLARI
# ==============================================================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")

# ==============================================================================
# MODEL AYARLARI
# ==============================================================================
LLM_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

# ==============================================================================
# BİLGİ BANKASI (BELGELER)
# ==============================================================================
# Ajanın erişebileceği hukuk kaynakları burada tanımlanır.
# Yeni bir kanun eklemek için buraya yeni bir blok eklemeniz yeterlidir.
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

LEGAL_DOCS = {
    "kmk": {
        "name": "Kat Mülkiyeti Kanunu",
        "description": "Apartman, site yönetimi, aidat, komşuluk ilişkileri ve kat malikleri kurulu hakkında sorular.",
        "path": os.path.join(DATA_DIR, "kat-mulkiyeti.pdf"),
        "collection": "law_kmk"
    },
    "tbk": {
        "name": "Türk Borçlar Kanunu (İlgili Maddeler)",
        "description": "Sadece kira sözleşmeleri, kiracı-ev sahibi ilişkileri ve komşuluktan doğan zararlar.",
        "path": os.path.join(DATA_DIR, "borclar-kanunu.pdf"), # Dosya yoksa ingest sırasında uyarır
        "collection": "law_tbk"
    },
    "anayasa": {
        "name": "T.C. Anayasası (İlgili Maddeler)",
        "description": "Konut dokunulmazlığı, mülkiyet hakkı ve özel hayatın gizliliği (Komşuluk bağlamında).",
        "path": os.path.join(DATA_DIR, "anayasa.pdf"),
        "collection": "law_anayasa"
    },
    "tmk": {
        "name": "Türk Medeni Kanunu (İlgili Maddeler)",
        "description": "Komşuluk hakları, mülkiyet kısıtlamaları, taşkınlık ve irtifak hakları.",
        "path": os.path.join(DATA_DIR, "medeni_kanun.pdf"),
        "collection": "law_tmk"
    },
    "asansor": {
        "name": "Asansör İşletme ve Bakım Yönetmeliği",
        "description": "Asansörlerin bakımı, yıllık kontrolleri, kırmızı etiket, mühürleme ve yönetici sorumlulukları.",
        "path": os.path.join(DATA_DIR, "asansor_yonetmeligi.pdf"),
        "collection": "reg_asansor"
    },
    "yangin": {
        "name": "Binaların Yangından Korunması Yönetmeliği",
        "description": "Yangın merdiveni, yangın tüpleri, kaçış yolları ve binadaki teknik yangın güvenlik önlemleri.",
        "path": os.path.join(DATA_DIR, "yangin_yonetmeligi.pdf"),
        "collection": "reg_yangin"
    }
}



# RAG Parametreleri (Varsayılan)
CHUNK_SIZE = 2000      # v2 ile aynı tutuldu
CHUNK_OVERLAP = 400    # v2 ile aynı tutuldu
TOP_K = 4

