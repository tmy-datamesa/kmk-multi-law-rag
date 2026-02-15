import os
import chromadb
from chromadb.utils import embedding_functions
from src import config


def get_chroma_client():
    """
    ChromaDB İstemcisini Getir
    --------------------------
    Bu fonksiyon, vektör veritabanı ile bağlantıyı kurar.
    
    Çıktı:
        - chromadb.PersistentClient: Veritabanı istemcisi
    
    Not:
        Tüm uygulama boyunca tek bir istemci kullanılması önerilir.
    """
    try:
        # Yerel veritabanı kullanılıyor (data/chroma_db)
        return chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
    except Exception as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        raise e


def get_embedding_function():
    """
    Embedding (Vektörleştirme) Fonksiyonunu Getir
    ---------------------------------------------
    Metinleri sayısal vektörlere çeviren yapay zeka modelini hazırlar.
    
    Model:
        - text-embedding-3-small (OpenAI)
        
    Kullanım:
        Bu fonksiyon hem veri yüklerken (ingestion) hem de soru sorarken (retrieval)
        aynı standartta olmalıdır.
    """
    if not config.OPENAI_API_KEY:
        raise ValueError("HATA: .env dosyasında OPENAI_API_KEY eksik!")

    return embedding_functions.OpenAIEmbeddingFunction(
        api_key=config.OPENAI_API_KEY,
        model_name=config.EMBEDDING_MODEL
    )
