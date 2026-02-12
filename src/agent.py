from openai import OpenAI
import json
from src import config
from src.rag_engine import LegalRAGTool
from src import utils

class LegalAgent:
    """
    SİSTEMİN BEYNİ (ROUTER)
    Kullanıcının sorusunu analiz eder ve hangi kanuna (Tool) bakması gerektiğine
    karar verir.
    """
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.chroma_client = utils.get_chroma_client()
        
        # ARAÇLARI HAZIRLA 
        # Her bir kanun için bir RAG motoru başlatıyoruz
        self.tools_map = {}
        for key, info in config.LEGAL_DOCS.items():
            self.tools_map[key] = LegalRAGTool(info["collection"], self.chroma_client)
            
    def _get_system_prompt(self):
        """Ajanın kimliğini ve kurallarını belirler."""
        return """
        Sen Kıdemli bir Türk Hukuku Asistanısın.
        
        GÖREVİN:
        Kullanıcının sorusunu analiz et ve cevaplamak için en uygun kanun kaynağını (Tool) seç.
        
        KURALLAR:
        1. Sorunun bağlamına göre (kira, apartman, haklar vb.) doğru aracı çağır.
        2. Aracıdan gelen bilgiyi kullanarak vatandaşa nazik, net ve hukuki dayanaklı cevap ver.
        3. Cevabına mutlaka kaynak belirterek başla (Örn: "Kat Mülkiyeti Kanunu'na göre...").
        4. Eğer sorunun cevabı ÇAĞIRDIĞIN ARAÇTAN gelen bilgide yoksa, uydurma.
        """

    def _get_openai_tools_definition(self):
        """
        OpenAI'a elimizdeki alet çantasını (Tools) tanıtıyoruz.
        Buradaki açıklamalar (description) modelin doğru aracı seçmesi için kritiktir.
        """
        tools = []
        for key, info in config.LEGAL_DOCS.items():
            tool_def = {
                "type": "function",
                "function": {
                    "name": f"search_{key}",
                    "description": f"Şu konularda arama yap: {info['description']}",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Aranacak hukuki kavram veya soru cümlesi"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
            tools.append(tool_def)
        return tools

    def ask(self, user_query):
        """
        Ajan Akışı:
        1. Düşün (Hangi araca ihtiyacım var?)
        2. Aracı Çağır (RAG Retrieval)
        3. Cevabı Sentezle (Generation)
        """
        
        # 1. ADIM: OpenAI'a soruyu ve aletleri gönder
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": user_query}
        ]
        
        tool_definitions = self._get_openai_tools_definition()
        
        response = self.client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=messages,
            tools=tool_definitions,
            tool_choice="auto" # Model kendi karar versin
        )
        
        msg = response.choices[0].message
        tool_calls = msg.tool_calls
        
        used_sources = [] # Hangi kaynakları kullandığımızı takip edelim

        # 2. Eğer model araç kullanmak istediyse
        if tool_calls:
            # Modelin "şu fonksiyonu çalıştır" emrini burada yakalıyoruz
            messages.append(msg) # Konuşma geçmişine ekle
            
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                query = args.get("query")
                
                # Fonksiyon isminden hangi kanun olduğunu anla (search_kmk -> kmk)
                doc_key = func_name.replace("search_", "")
                
                print(f"Ajan Kararı: {doc_key.upper()} kaynağına bakılıyor... ('{query}')")
                
                # İlgili RAG motorunu çalıştır
                rag_tool = self.tools_map.get(doc_key)
                
                if rag_tool:
                    # RAG motorunu çalıştır ve kanun maddelerini getir
                    context = rag_tool.get_context(query)
                    content = context if context else "Bu konuda veritabanında bilgi bulunamadı."
                    
                    if context:
                        used_sources.append(config.LEGAL_DOCS[doc_key]['name'])
                    
                    # Bulunan kanun maddelerini modele "Kanıt" olarak geri ver
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": content
                    })

            # Adım 3: Kanun maddeleriyle birlikte Nihai Cevabı (Final Answer) iste
            final_response = self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=messages
            )
            return final_response.choices[0].message.content, used_sources
        
        else:
            # Model hiç araç kullanmadıysa (Selamlaşma vb.) direk cevap ver
            return msg.content, []


