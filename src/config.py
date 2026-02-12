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
        "name": "Türk Borçlar Kanunu",
        "description": "Kira sözleşmeleri, borç ilişkileri, alacak-verecek davaları, tazminat ve sözleşme hukuku.",
        "path": os.path.join(DATA_DIR, "borclar-kanunu.pdf"), # Dosya yoksa ingest sırasında uyarır
        "collection": "law_tbk"
    },
    "anayasa": {
        "name": "T.C. Anayasası",
        "description": "Temel hak ve özgürlükler, devletin yapısı, vatandaşlık hakları ve anayasal düzen.",
        "path": os.path.join(DATA_DIR, "anayasa.pdf"),
        "collection": "law_anayasa"
    }
}

# RAG Parametreleri (Varsayılan)
# Her doküman için özel ayar yapılmazsa bunlar geçerli olur.
CHUNK_SIZE = 2000      # v2 ile aynı tutuldu
CHUNK_OVERLAP = 400    # v2 ile aynı tutuldu
TOP_K = 4

