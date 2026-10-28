import sqlite3, json, os
from pathlib import Path
DB_PATH=os.getenv('DB_PATH',str(Path(__file__).resolve().parents[1]/'data'/'app.db'))
def connect(path=None):
    c=sqlite3.connect(path or DB_PATH); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON'); return c
def init_db(path=None):
    c=connect(path); c.executescript("""
    CREATE TABLE IF NOT EXISTS documents(id INTEGER PRIMARY KEY, name TEXT NOT NULL, doc_type TEXT, version TEXT, filename TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, status TEXT DEFAULT 'processed', pages_json TEXT, clauses_json TEXT, comparison_json TEXT);
    CREATE TABLE IF NOT EXISTS checklists(id INTEGER PRIMARY KEY, name TEXT NOT NULL, items_json TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS reviewer_annotations(id INTEGER PRIMARY KEY, document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE, target TEXT, decision TEXT, note TEXT, reviewer TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS audit_events(id INTEGER PRIMARY KEY, document_id INTEGER, event TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE INDEX IF NOT EXISTS idx_annotations_doc ON reviewer_annotations(document_id);
    """); c.commit(); c.close()
def save_document(doc,path=None):
    c=connect(path); cur=c.execute('INSERT INTO documents(name,doc_type,version,filename,pages_json,clauses_json,comparison_json) VALUES(?,?,?,?,?,?,?)',(doc['name'],doc.get('doc_type',''),doc.get('version',''),doc['filename'],json.dumps(doc['pages']),json.dumps(doc['clauses']),json.dumps(doc.get('comparison',[])))); did=cur.lastrowid; c.execute('INSERT INTO audit_events(document_id,event) VALUES(?,?)',(did,'Document analyzed')); c.commit(); c.close(); return did
def list_documents(path=None):
    c=connect(path); rows=[dict(x) for x in c.execute('SELECT * FROM documents ORDER BY created_at DESC')]; c.close(); return rows
def annotate(document_id,target,decision,note,reviewer='Reviewer',path=None):
    c=connect(path); c.execute('INSERT INTO reviewer_annotations(document_id,target,decision,note,reviewer) VALUES(?,?,?,?,?)',(document_id,target,decision,note,reviewer)); c.execute('INSERT INTO audit_events(document_id,event) VALUES(?,?)',(document_id,'Review annotation added')); c.commit(); c.close()
def get_annotations(document_id,path=None):
    c=connect(path); r=[dict(x) for x in c.execute('SELECT * FROM reviewer_annotations WHERE document_id=? ORDER BY created_at',(document_id,))]; c.close(); return r
def delete_document(document_id,path=None):
    c=connect(path); c.execute('DELETE FROM documents WHERE id=?',(document_id,)); c.commit(); c.close()
