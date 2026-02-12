from src import config, utils

class LegalRAGTool:

    """
    Tekil RAG Motoru 
    
    Bu sınıfın tek görevi:
    Kendisine verilen ÖZEL bir koleksiyon (Örn: Sadece KMK veya Sadece TBK) içinde
    arama yapmaktır. Agent bu aracı çağırır.
    """
    def __init__(self, collection_name, client=None):
        # Veritabanı bağlantısını ve Embedding fonksiyonunu al
        self.client = client or utils.get_chroma_client()
        self.embedding_fn = utils.get_embedding_function()
        
        # Spesifik koleksiyona bağlan
        self.collection = self.client.get_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )

    def retrieve(self, query):
        """
        Vektör Araması: Soruyu sayıya çevir ve en yakın 4 maddeyi bul.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=config.TOP_K
        )
        # Eğer sonuç varsa ilk listeyi dön, yoksa boş liste dön
        return results['documents'][0] if results['documents'] else []

    def get_context(self, query):
        """
        LLM için hazırlık: Bulunan maddeleri alt alta birleştirip tek bir metin yapar.
        """
        docs = self.retrieve(query)
        return "\n\n---\n\n".join(docs) if docs else None


