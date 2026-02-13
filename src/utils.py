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
        - chromadb.CloudClient: Veritabanı istemcisi
    
    Not:
        Tüm uygulama boyunca tek bir istemci kullanılması önerilir.
    """
    if not config.CHROMA_API_KEY:
        raise ValueError("HATA: .env dosyasında CHROMA_API_KEY eksik! Lütfen kontrol edin.")

    try:
        # Cloud sürümü kullanılıyor
        return chromadb.CloudClient(
            api_key=config.CHROMA_API_KEY,
            tenant=os.getenv("CHROMA_TENANT", "default_tenant"),
            database=os.getenv("CHROMA_DATABASE", "default_database")
        )
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
