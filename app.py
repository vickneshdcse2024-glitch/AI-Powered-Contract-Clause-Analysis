import streamlit as st, json, os
from pathlib import Path
from dotenv import load_dotenv
from src.document_parser import parse_document
from src.clause_detector import detect_clauses
from src.comparison_engine import compare_checklist
from src.database import init_db,save_document,list_documents,annotate,get_annotations,delete_document
from src.report_generator import csv_export,json_export,pdf_export
load_dotenv(); init_db()
st.set_page_config(page_title='Contract Clause Analysis',page_icon='📄',layout='wide')
st.title('AI-Powered Contract Clause Analysis')
st.caption('Review assistance only — not a substitute for qualified legal advice. Original uploads are analyzed in memory; stored analysis records are local.')
sections=['Home Dashboard','Upload Contract','Checklist Management','Clause Analysis','Checklist Comparison','Review Flags','Human Review','Reports and Export','Settings']
section=st.sidebar.radio('Navigation',sections)
docs=list_documents();
if section=='Home Dashboard':
    st.subheader('Home Dashboard'); st.write('Local contract review workspace')
    cols=st.columns(4); cols[0].metric('Documents processed',len(docs)); clauses=sum(len(json.loads(d['clauses_json'])) for d in docs); cols[1].metric('Clauses identified',clauses)
    cmp=[x for d in docs for x in json.loads(d['comparison_json'] or '[]')]; cols[2].metric('Items requiring review',sum(x['status'] in ('NEEDS HUMAN REVIEW','UNREADABLE / EXTRACTION INCOMPLETE') for x in cmp)); cols[3].metric('Wording deviations',sum(x['status']=='WORDING DEVIATION' for x in cmp))
    st.dataframe([{'Name':d['name'],'Type':d['doc_type'],'Version':d['version'],'Status':d['status'],'Created':d['created_at']} for d in docs],use_container_width=True)
elif section=='Checklist Management':
    st.subheader('Checklist Management'); name=st.text_input('Checklist name',value='My approved checklist')
    raw=st.text_area('Checklist items (one category per line)',value='Payment Terms\nTermination\nConfidentiality\nLiability\nRenewal\nGoverning Law')
    st.caption('Optional JSON upload format: [{"category":"Payment Terms","expected_wording":"...","notes":"..."}]')
    f=st.file_uploader('Upload checklist JSON',type=['json'])
    if f:
        try: items=json.loads(f.getvalue()); st.session_state.items=items; st.success(f'Loaded {len(items)} checklist items')
        except Exception as e: st.error(f'Invalid JSON checklist: {e}')
    else: st.session_state.items=[{'category':x.strip(),'expected_wording':'','notes':''} for x in raw.splitlines() if x.strip()]
    st.json(st.session_state.items)
    st.info('Checklists are available for this browser session; use JSON upload for reusable approved checklist files.')
elif section=='Upload Contract':
    st.subheader('Upload Contract'); f=st.file_uploader('PDF or DOCX (max configured 25 MB)',type=['pdf','docx'])
    name=st.text_input('Contract name'); dtype=st.text_input('Document type'); version=st.text_input('Version',value='1.0')
    items=st.session_state.get('items',[{'category':x,'expected_wording':'','notes':''} for x in ['Payment Terms','Termination','Confidentiality','Liability','Renewal','Governing Law']])
    if st.button('Analyze contract',type='primary',disabled=not f):
        limit=int(os.getenv('MAX_UPLOAD_MB','25'))*1024*1024
        if len(f.getvalue())>limit: st.error('File exceeds configured size limit.')
        else:
            try:
                with st.spinner('Extracting text and identifying evidence…'):
                    pages=parse_document(f.name,f.getvalue()); clauses=detect_clauses(pages); comparison=compare_checklist(items,clauses,pages)
                    payload={'name':name or f.name,'doc_type':dtype,'version':version,'filename':f.name,'pages':[p.__dict__ for p in pages],'clauses':clauses,'comparison':comparison}
                    did=save_document(payload); st.success(f'Analysis saved as record #{did}.')
                    st.write(f'{len(clauses)} clause matches; {sum(not x.readable for x in pages)} unreadable/incomplete pages.')
            except Exception as e: st.error(f'Could not process document: {e}')
elif section in ('Clause Analysis','Checklist Comparison','Review Flags','Human Review','Reports and Export'):
    st.subheader(section)
    if not docs: st.info('No documents analyzed yet. Use Upload Contract to begin.')
    else:
        selected=st.selectbox('Select contract',docs,format_func=lambda d:f"#{d['id']} — {d['name']} ({d['version']})")
        did=selected['id']; clauses=json.loads(selected['clauses_json']); comp=json.loads(selected['comparison_json'] or '[]'); pages=json.loads(selected['pages_json']); anns=get_annotations(did)
        if section=='Clause Analysis':
            st.dataframe(clauses,use_container_width=True)
            for c in clauses:
                with st.expander(f"{c['category']} — page/reference {c['page']}"): st.write('Source text (verbatim):'); st.code(c['text']); st.caption(c['evidence'])
        elif section=='Checklist Comparison': st.dataframe(comp,use_container_width=True)
        elif section=='Review Flags':
            st.caption('Flags are conservative prompts for reviewer attention, not legal conclusions.')
            for c in clauses:
                text=c['text'].lower(); reasons=[]
                if c['category'] in ('Liability','Indemnification') and any(k in text for k in ['any and all','unlimited','regardless of']): reasons.append('Broad wording pattern detected')
                if c['category']=='Renewal' and 'automatic' in text: reasons.append('Automatic renewal language detected')
                if c['category']=='Termination' and any(k in text for k in ['ninety days','90 days','one hundred eighty']): reasons.append('Extended notice period wording may merit review')
                if reasons: st.warning(f"{c['category']} | page {c['page']}: {'; '.join(reasons)}"); st.code(c['text'])
            for r in comp:
                if r['status']!='PRESENT': st.warning(f"{r['category']}: {r['status']} — {r['evidence']}")
        elif section=='Human Review':
            st.dataframe(anns,use_container_width=True); target=st.text_input('Finding/category'); decision=st.selectbox('Decision',['Pending','Accepted','Dismissed','Corrected']); reviewer=st.text_input('Reviewer',value='Reviewer'); note=st.text_area('Annotation / reason')
            if st.button('Save review note'):
                if decision=='Dismissed' and not note.strip(): st.error('Provide a reason to dismiss a finding.')
                else: annotate(did,target,decision,note,reviewer); st.success('Review entry saved; refresh to see it.')
            st.subheader('Extraction completeness'); st.write([{'page/paragraph':x['page'],'readable':x['readable'],'note':x['note']} for x in pages])
        else:
            payload={'name':selected['name'],'version':selected['version'],'filename':selected['filename'],'clauses':clauses,'comparison':comp,'annotations':anns,'limitations':'Extraction quality depends on the source file. OCR is not included; unreadable pages are not treated as proof of absence.'}
            st.download_button('Download CSV',csv_export(clauses,comp),'review.csv','text/csv'); st.download_button('Download JSON',json_export(payload),'review.json','application/json'); st.download_button('Download PDF report',pdf_export(payload),'review-report.pdf','application/pdf')
            if st.button('Delete document and associated review data'):
                delete_document(did); st.success('Document analysis and annotations deleted. Refresh page.')
elif section=='Settings':
    st.subheader('Settings & limitations'); st.write('Database:',os.getenv('DB_PATH','data/app.db')); st.write('Maximum upload MB:',os.getenv('MAX_UPLOAD_MB','25')); st.write('Retention days:',os.getenv('RETENTION_DAYS','90'))
    st.warning('Local demo has no authentication or encryption at rest. Restrict access to the machine and filesystem. No uploaded original is retained; analysis text is stored in SQLite. Set file/database permissions and configure backups/deletion for production.')
    st.write('Optional AI is off by default. Set AI_ENABLED=true plus AI_BASE_URL, AI_API_KEY, AI_MODEL only for an explicitly approved provider. Contract text may leave the machine when enabled. Rule-based mode remains available if the provider fails.')
