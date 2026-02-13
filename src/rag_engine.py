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
        
        # Sonuçları işle ve yapılandır
        structured_results = []
        if results['documents'] and results['documents'][0]:
            docs = results['documents'][0]
            metas = results['metadatas'][0] if results['metadatas'] else [{}] * len(docs)
            
            for doc, meta in zip(docs, metas):
                structured_results.append({
                    "content": doc,
                    "metadata": meta
                })
                
        return structured_results

    def get_context(self, query):
        """
        LLM için hazırlık: Bulunan maddeleri ve metadataları döner.
        """
        return self.retrieve(query)


