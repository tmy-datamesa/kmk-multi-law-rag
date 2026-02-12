PYTHON = python3
PIP = pip

.PHONY: setup ingest run clean

# Kurulum
setup:
	$(PIP) install -r requirements.txt
	@echo "✅ Kurulum Tamamlandı! .env dosyanızı oluşturmayı unutmayın."

# Veri Yükleme (Tüm kanunları tarar)
ingest:
	@echo "📚 Kütüphane Güncelleniyor..."
	$(PYTHON) -c "from src.ingestion import ingest_all_docs; ingest_all_docs(force_recreate=True)"

# Uygulamayı Başlat
run:
	streamlit run app.py

# Temizlik
clean:
	rm -rf __pycache__ src/__pycache__
