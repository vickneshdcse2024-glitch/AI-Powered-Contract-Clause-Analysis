import json
from src.document_parser import parse_document
from src.clause_detector import detect_clauses
from src.comparison_engine import compare_checklist
from src.database import init_db,save_document,annotate,get_annotations,delete_document,list_documents
from src.report_generator import csv_export,json_export,pdf_export
from docx import Document
import io

def test_docx_parse_and_clause():
    d=Document(); d.add_paragraph('1. Payment Terms. Customer shall pay invoices within thirty days.'); b=io.BytesIO(); d.save(b)
    pages=parse_document('x.docx',b.getvalue()); clauses=detect_clauses(pages)
    assert pages[0].readable and any(x['category']=='Payment Terms' for x in clauses)

def test_pdf_extract():
    import fitz
    d=fitz.open(); p=d.new_page(); p.insert_text((50,50),'Confidentiality: parties shall protect confidential information.'); data=d.tobytes()
    assert 'Confidentiality' in parse_document('x.pdf',data)[0].text

def test_comparison_unreadable_not_missing():
    pages=[type('P',(),{'readable':False})()]
    result=compare_checklist([{'category':'Payment Terms'}],[],pages)
    assert result[0]['status']=='NEEDS HUMAN REVIEW'

def test_db_and_exports(tmp_path):
    db=str(tmp_path/'t.db'); init_db(db)
    payload={'name':'Synthetic','filename':'x.docx','pages':[],'clauses':[],'comparison':[]}
    i=save_document(payload,db); annotate(i,'Payment','Accepted','Checked',path=db)
    assert len(get_annotations(i,db))==1 and len(list_documents(db))==1
    assert 'category' in csv_export([{'category':'Payment Terms','text':'text','page':1}],[])
    assert json.loads(json_export({'ok':True}))['ok']
    assert pdf_export({'name':'Test','clauses':[],'comparison':[]}).startswith(b'%PDF')
    delete_document(i,db); assert not list_documents(db)

def test_invalid_file():
    import pytest
    with pytest.raises(ValueError): parse_document('bad.txt',b'bad')
