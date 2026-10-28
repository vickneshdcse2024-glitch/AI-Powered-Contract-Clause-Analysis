import re

PATTERNS={
'Payment Terms':r'payment|invoice|fees|charges|due date', 'Termination':r'terminat|terminate|termination',
'Confidentiality':r'confidential|non-disclosure|proprietary information', 'Liability':r'liabilit',
'Indemnification':r'indemnif|hold harmless', 'Renewal':r'renew|auto(?:matic)?ally renew',
'Governing Law':r'governing law|laws of|governed by', 'Dispute Resolution':r'arbitrat|dispute resolution|mediat',
'Data Protection':r'data protection|personal data|privacy|security incident', 'Intellectual Property':r'intellectual propert|ownership of (?:work|deliverables)|copyright',
'Representations and Warranties':r'represent(?:s|ation)|warrant(?:y|ies)', 'Force Majeure':r'force majeure|beyond (?:its|the party.s) reasonable control',
'Limitation of Liability':r'limitation of liability|liability shall not exceed|cap on liability',
'Contract Duration':r'term of this agreement|initial term|effective date', 'Notice Requirements':r'notice[s]? (?:must|shall|will)|written notice'}

def detect_clauses(pages):
    out=[]
    for pg in pages:
        text=pg.text
        # Keep paragraph/line source excerpts verbatim; do not synthesize clause wording.
        chunks=[x.strip() for x in re.split(r'(?<=[.!?])\s+|\n+',text) if x.strip()]
        for i,chunk in enumerate(chunks):
            for category,pattern in PATTERNS.items():
                if re.search(pattern,chunk,re.I):
                    heading=''
                    m=re.match(r'^((?:\d+(?:\.\d+)*|[A-Z])\s*[.)-]?\s*[^.]{0,90})',chunk)
                    if m: heading=m.group(1)
                    out.append({'category':category,'text':chunk,'reference':heading or f'Extract {i+1}','page':pg.page,'summary':chunk[:220], 'method':'Rule-based keyword match','evidence':chunk,'confidence':'Evidence found; human confirmation required'})
    # Deduplicate exact category+source excerpt, preserving source.
    seen=set(); result=[]
    for x in out:
        k=(x['category'],x['page'],x['text'])
        if k not in seen: seen.add(k); result.append(x)
    return result
