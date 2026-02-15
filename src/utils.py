import os
import chromadb
from chromadb.utils import embedding_functions
from src import config


def get_chroma_client():
    """
    ChromaDB İstemcisini Getir
    --------------------------
    Bu fonksiyon, UZAK (Cloud) vektör veritabanı ile bağlantıyı kurar.
    Yerel veritabanı desteği kaldırılmıştır.
    
    Çıktı:
        - chromadb.HttpClient: Veritabanı istemcisi
    
    Not:
        .env dosyasında CHROMA_HOST tanımlı olmalıdır.
    """
    try:
        # Cloud ChromaDB Bağlantısı (Zorunlu)
        settings = chromadb.config.Settings()
        if config.CHROMA_API_KEY:
            settings.chroma_client_auth_provider = "chromadb.auth.token_authn.TokenAuthClientProvider"
            settings.chroma_client_auth_credentials = config.CHROMA_API_KEY
        
        client = chromadb.HttpClient(
            host=config.CHROMA_HOST,
            port=config.CHROMA_PORT,
            ssl=config.CHROMA_SSL,
            settings=settings
        )
        print(f"☁️ Cloud ChromaDB Bağlandı (ZORUNLU): {config.CHROMA_HOST}")
        return client
        
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
