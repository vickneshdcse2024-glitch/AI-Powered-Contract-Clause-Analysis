import difflib

def compare_checklist(items, clauses, pages):
    incomplete=any(not p.readable for p in pages)
    results=[]
    for item in items:
        cat=item.get('category','')
        matches=[c for c in clauses if c['category'].lower()==cat.lower()]
        expected=item.get('expected_wording','').strip()
        if not matches:
            status='NEEDS HUMAN REVIEW' if incomplete else 'MISSING'
            evidence='No matching text was detected.' if not incomplete else 'No matching text detected, but extraction has unreadable/incomplete content; absence cannot be established.'
            actual=''
        else:
            actual='\n'.join(c['text'] for c in matches)
            if not expected: status='PRESENT'; evidence='Category evidence detected; no template wording supplied.'
            elif actual.strip().lower()==expected.lower(): status='PRESENT'; evidence='Detected wording exactly matches the approved text.'
            else:
                ratio=difflib.SequenceMatcher(None,expected.lower(),actual.lower()).ratio()
                status='WORDING DEVIATION' if ratio>=0.35 else 'NEEDS HUMAN REVIEW'
                evidence=f'Expected wording differs from detected source text (text similarity {ratio:.0%}; not a legal assessment).'
        results.append({'category':cat,'status':status,'expected':expected,'actual':actual,'evidence':evidence,'notes':item.get('notes','')})
    return results
