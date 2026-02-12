import os
import chromadb
from chromadb.utils import embedding_functions
from src import config


def get_chroma_client():
    """
    ChromaDB Cloud istemcisini başlatır.
    Sadece tek bir istemci (Client) tüm koleksiyonları yönetir.
    """
    if not config.CHROMA_API_KEY:
        raise ValueError("HATA: .env dosyasında CHROMA_API_KEY eksik.")

    try:
        return chromadb.CloudClient(
            api_key=config.CHROMA_API_KEY,
            tenant=os.getenv("CHROMA_TENANT", "default_tenant"), # Opsiyonel
            database=os.getenv("CHROMA_DATABASE", "default_database") # Opsiyonel
        )
    except Exception as e:
        raise e


def get_embedding_function():
    """
    OpenAI Embedding fonksiyonunu döndürür.
    Tüm kanunlar bu standart fonksiyonla vektörleştirilir.
    """
    if not config.OPENAI_API_KEY:
        raise ValueError("HATA: OPENAI_API_KEY eksik.")

    return embedding_functions.OpenAIEmbeddingFunction(
        api_key=config.OPENAI_API_KEY,
        model_name=config.EMBEDDING_MODEL
    )
