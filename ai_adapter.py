"""Optional external AI adapter intentionally disabled unless explicitly configured."""
import os
class AIAdapter:
    def __init__(self):
        self.enabled=os.getenv('AI_ENABLED','false').lower()=='true'
        self.api_key=os.getenv('AI_API_KEY'); self.base_url=os.getenv('AI_BASE_URL'); self.model=os.getenv('AI_MODEL')
    def available(self): return bool(self.enabled and self.api_key and self.base_url and self.model)
    def explain(self,text):
        if not self.available(): return {'mode':'rule-based','text':'AI unavailable or not configured; rule-based findings only.'}
        try:
            from openai import OpenAI
            client=OpenAI(api_key=self.api_key,base_url=self.base_url,timeout=15)
            r=client.chat.completions.create(model=self.model,messages=[{'role':'system','content':'Summarize only the supplied contract text. State uncertainty. Not legal advice.'},{'role':'user','content':text}],max_tokens=300)
            return {'mode':'AI-generated','text':r.choices[0].message.content}
        except Exception as e: return {'mode':'rule-based fallback','text':f'AI request failed ({type(e).__name__}); continue with evidence-based rule findings.'}
