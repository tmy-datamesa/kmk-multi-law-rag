from openai import OpenAI
import json
from src import config
from src.rag_engine import LegalRAGTool
from src import utils

class LegalRAG:
    """
    RAG SİSTEMİ (ROUTER + RETRIEVER + GENERATOR)
    
    Tek bir sınıfta tüm RAG akışını yönetir:
    1. Router: Hangi kanuna bakılacak? (LLM Function Calling ile)
    2. Retriever: Seçilen kanundan ve ilgili parçaları bul.
    3. Generator: Bulunan parçalarla cevabı üret.
    """
    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.chroma_client = utils.get_chroma_client()
        
        # ARAÇLARI HAZIRLA (Her kanun için RAG motoru)
        self.tools_map = {}
        for key, info in config.LEGAL_DOCS.items():
            self.tools_map[key] = LegalRAGTool(info["collection"], self.chroma_client)
            
    def _get_system_prompt(self):
        """Ajanın kimliğini ve kurallarını belirler."""
        return """
        Sen Uzman bir Türk Hukuku Asistanısın. Alanın: Apartman, Site ve Komşuluk Hukuku.
        
        KURALLAR:
        1. Soruya en uygun kanun kaynağını (Tool) kullanarak cevap ver.
        2. Cevabına "X Kanunu'nun Y Maddesi'ne göre..." gibi atıfla başla.
        3. Bilgi yoksa uydurma, "Bilgi bulunamadı" de.
        4. Hukuk dışı konularda cevap verme.
        """

    def _get_openai_tools(self):
        """OpenAI'a 'Benim elimde şu arama fonksiyonları var' diyoruz."""
        tools = []
        for key, info in config.LEGAL_DOCS.items():
            tool_def = {
                "type": "function",
                "function": {
                    "name": f"search_{key}",
                    "description": info['description'],
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Aranacak konu"}
                        },
                        "required": ["query"]
                    }
                }
            }
            tools.append(tool_def)
        return tools

    def generate_answer(self, user_query):
        """
        ANA AKIŞ (Main Flow)
        --------------------
        1. DÜŞÜNME (Planning): Soruyu analiz et, hangi kanuna ihtiyaç var?
        2. ARAMA (Retrieval): Seçilen kanun kitabından ilgili maddeleri bul.
        3. CEVAPLAMA (Generation): Bulunan maddeleri kullanarak cevabı yaz.
        """
        
        # 1. ADIM: İSTEM (Prompt) Hazırlığı
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": user_query}
        ]
        
        # LLM'e araçları (tools) tanıtıyoruz
        response = self.client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=messages,
            tools=self._get_openai_tools(),
            tool_choice="auto" # Kararı yapay zekaya bırak
        )
        
        msg = response.choices[0].message
        tool_calls = msg.tool_calls
        
        used_sources = [] 
        
        # 2. ADIM: ARAÇ KULLANIMI (Tool Execution)
        if tool_calls:
            # Yapay zeka "Şu kanuna bakmam lazım" dedi.
            messages.append(msg) # Bu kararı hafızaya ekle
            
            for tool_call in tool_calls:
                # Hangi fonksiyonu çağırdı? (Örn: search_kmk)
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                query = args.get("query")
                
                # Fonksiyon isminden kanun kodunu çıkar (search_kmk -> kmk)
                doc_key = func_name.replace("search_", "")
                
                # İlgili Arama Motorunu (RAG Tool) getir
                rag_tool = self.tools_map.get(doc_key)
                
                if rag_tool:
                    # VERİTABANI ARAMASI YAP
                    context_list = rag_tool.get_context(query)
                    
                    if context_list:
                        # LLM için metinleri birleştir
                        context_str = "\n".join([item['content'] for item in context_list])
                        
                        # Kullanıcıya göstermek için kaynakları listeye ekle
                        for item in context_list:
                            # Format: **Belge Adı** \n İçerik
                            source_simple = f"**{item['metadata']['doc_name']}**\n{item['content']}"
                            used_sources.append(source_simple)
                    else:
                        context_str = "Veritabanında ilgili bilgi bulunamadı."

                    # 3. ADIM: ARAMA SONUCUNU YAPAY ZEKAYA GERİ VER
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": context_str
                    })

            # 4. ADIM: SON CEVABI ÜRET (Generation)
            final_response = self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=messages
            )
            return final_response.choices[0].message.content, used_sources
        
        else:
            # Araç kullanmadıysa (Selamlaşma vb.) direk cevap ver
            return msg.content, []


