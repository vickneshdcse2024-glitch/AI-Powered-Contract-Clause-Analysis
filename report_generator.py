import csv,io,json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def csv_export(clauses,comparison):
    s=io.StringIO(); w=csv.writer(s); w.writerow(['type','category','status','text/evidence','page/reference']);
    for c in clauses: w.writerow(['Clause',c['category'],'',c['text'],c['page']])
    for c in comparison: w.writerow(['Checklist',c['category'],c['status'],c['evidence'],''])
    return s.getvalue()
def json_export(payload): return json.dumps(payload,ensure_ascii=False,indent=2)
def pdf_export(payload):
    b=io.BytesIO(); c=canvas.Canvas(b,pagesize=letter); y=750
    def line(s):
        nonlocal y
        if y<55: c.showPage(); y=750
        c.drawString(48,y,str(s)[:115]); y-=15
    line('Contract Clause Analysis — Review Report'); line(f"Contract: {payload.get('name','')}"); line(f"Version: {payload.get('version','')}"); line('Generated observations are not legal advice; human review required.'); line('')
    line('CLAUSE INVENTORY')
    for x in payload.get('clauses',[]): line(f"{x['category']} | page {x['page']} | {x['text']}")
    line('CHECKLIST COMPARISON')
    for x in payload.get('comparison',[]): line(f"{x['category']} — {x['status']}: {x['evidence']}")
    line('REVIEW NOTES')
    for x in payload.get('annotations',[]): line(f"{x['decision']} / {x['target']}: {x['note']}")
    c.save(); return b.getvalue()
