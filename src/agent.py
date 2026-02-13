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
        TEK FONKSİYON: Soru -> Cevap + Kaynaklar
        """
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": user_query}
        ]
        
        # 1. LLM'e Sor (Hangi araca ihtiyacın var?)
        response = self.client.chat.completions.create(
            model=config.LLM_MODEL,
            messages=messages,
            tools=self._get_openai_tools(),
            tool_choice="auto"
        )
        
        msg = response.choices[0].message
        tool_calls = msg.tool_calls
        
        used_sources = [] 
        
        # 2. Eğer LLM araç kullanmak istediyse (Genelde ister)
        if tool_calls:
            messages.append(msg) # Geçmişe ekle
            
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                query = args.get("query")
                
                # Hangi kanun? (search_kmk -> kmk)
                doc_key = func_name.replace("search_", "")
                
                rag_tool = self.tools_map.get(doc_key)
                if rag_tool:
                    # RAG Araması Yap
                    context_list = rag_tool.get_context(query)
                    
                    if context_list:
                        # Context'i birleştir
                        context_str = "\n".join([item['content'] for item in context_list])
                        
                        # Kaynak listesini hazırla (Sadece Başlık + İçerik)
                        for item in context_list:
                             # "KMK Madde X..." formatında basit string
                            source_simple = f"**{item['metadata']['doc_name']}**\n{item['content']}"
                            used_sources.append(source_simple)
                    else:
                        context_str = "Veritabanında bilgi yok."

                    # Sonucu LLM'e geri ver
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": func_name,
                        "content": context_str
                    })

            # 3. Final Cevabı Üret
            final_response = self.client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=messages
            )
            return final_response.choices[0].message.content, used_sources
        
        else:
            # Araç kullanmadıysa (Selam, Nasılsın vb.)
            return msg.content, []


