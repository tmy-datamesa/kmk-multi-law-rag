import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from src import config, utils

def load_pdf(file_path):
    if not os.path.exists(file_path):
        return None
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def chunk_text(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        separators=[
            "\nKISIM ", "\nBÖLÜM ", "\nMadde ", "\nEk Madde ", "\nGeçici Madde ",
            "\n", " ", ""
        ],
        is_separator_regex=True
    )
    return text_splitter.split_text(text)

def ingest_all_docs(force_recreate=False):
    """
    Config dosyasındaki TÜM belgeleri sırayla işler ve veritabanına yükler.
    
    Bu fonksiyon bir nevi "Kütüphaneci" gibidir:
    1. Rafları (Koleksiyonları) kontrol eder.
    2. Eksik kitap varsa PDF'i okur.
    3. Sayfaları parçalar ve rafa yerleştirir.
    """
    client = utils.get_chroma_client()
    embedding_fn = utils.get_embedding_function()
    
    # Config dosyasındaki her bir kanun tanımı için döngü
    for key, doc_info in config.LEGAL_DOCS.items():
        col_name = doc_info["collection"]
        pdf_path = doc_info["path"]
        
        # 1. TEMİZLİK: Eğer 'force_recreate=True' ise eski veriyi sil
        if force_recreate:
            try:
                client.delete_collection(col_name)
            except:
                pass # Zaten yoksa hata verme, devam et

        # 2. HAZIRLIK: Koleksiyonu (Tabloyu) getir veya oluştur
        collection = client.get_or_create_collection(
            name=col_name,
            embedding_function=embedding_fn
        )

        # 3. KONTROL: Veri zaten var mı? Varsa tekrar yükleme yapma (Zaman kaybı önlenir)
        if collection.count() == 0 or force_recreate:
            raw_text = load_pdf(pdf_path)
            
            if raw_text:
                # Metni parçalara böl (Chunking)
                chunks = chunk_text(raw_text)
                
                # Her parçaya benzersiz ID ve Metadata ver
                ids = [f"{key}_{i}" for i in range(len(chunks))]
                
                # Metadata: Bu parça hangi kitaptan geldi? (Örn: source='kmk')
                metadatas = [{"source": key, "doc_name": doc_info["name"]} for _ in chunks]
                
                # Veritabanına kaydet
                collection.add(documents=chunks, ids=ids, metadatas=metadatas)
                print(f"✅ Yüklendi: {doc_info['name']} ({len(chunks)} parça)")


if __name__ == "__main__":
    # Tek başına çalıştırılırsa verileri tazeler
    ingest_all_docs(force_recreate=True)
