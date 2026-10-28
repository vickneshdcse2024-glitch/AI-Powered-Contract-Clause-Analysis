from dataclasses import dataclass, asdict
from pathlib import Path
import fitz
from docx import Document

@dataclass
class PageText:
    page: int
    text: str
    readable: bool
    note: str = ''

def parse_document(filename: str, data: bytes):
    ext=Path(filename).suffix.lower()
    if ext=='.pdf':
        try: doc=fitz.open(stream=data,filetype='pdf')
        except Exception as e: raise ValueError(f'Could not read PDF: {e}')
        pages=[]
        for i,page in enumerate(doc):
            text=page.get_text('text') or ''
            good=len(text.strip())>=20
            pages.append(PageText(i+1,text,good,'' if good else 'Unreadable or OCR Required'))
        if not pages: raise ValueError('PDF contains no pages')
        return pages
    if ext=='.docx':
        try: doc=Document(__import__('io').BytesIO(data))
        except Exception as e: raise ValueError(f'Could not read DOCX: {e}')
        paras=[x.text for x in doc.paragraphs if x.text.strip()]
        # DOCX has no stable pagination; paragraph positions are references, not page numbers.
        return [PageText(i+1,t,True,'DOCX paragraph reference; page unavailable') for i,t in enumerate(paras)] or [PageText(1,'',False,'Empty document')]
    raise ValueError('Unsupported file type. Upload PDF or DOCX.')
