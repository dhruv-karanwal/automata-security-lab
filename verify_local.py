from pathlib import Path
import sys, json, httpx
sys.path.insert(0, str(Path.cwd() / 'backend'))
from tests.test_pdf_extraction import make_text_pdf, make_blank_pdf
from app.pdf_extraction import MAX_PDF_SIZE
root=Path.cwd()/'verification'
root.mkdir(exist_ok=True)
fixtures={'valid.pdf':make_text_pdf('WIN PRIZE NOW'),'ordinary.pdf':make_text_pdf('Team meeting tomorrow'),'invalid.pdf':b'not a PDF','malformed.pdf':b'%PDF-1.7\nbroken','encrypted.pdf':make_blank_pdf(encrypted=True),'textless.pdf':make_blank_pdf(),'oversized.pdf':b'%PDF-1.7\n'+b'0'*MAX_PDF_SIZE,'empty.pdf':b''}
for name,data in fixtures.items(): (root/name).write_bytes(data)
c=httpx.Client(base_url='http://127.0.0.1:8000',timeout=30)
checks=[]
def record(name,r,status=200):
    assert r.status_code==status,(name,r.status_code,r.text)
    checks.append({'check':name,'status':r.status_code,'response':r.json()})
record('health',c.get('/api/health'))
spec=c.get('/openapi.json').json(); print('Routes:',list(spec['paths']))
for name,data in fixtures.items():
    status=200 if name in ['valid.pdf','ordinary.pdf'] else 413 if name=='oversized.pdf' else 400
    r=c.post('/api/pdf/extract',files={'file':(name,data,'application/pdf')}); record(name,r,status)
    if name=='valid.pdf':
        assert r.json()['extracted_text']=='WIN PRIZE NOW'
        for mode in ['dfa','nfa','regex','combined']:
            a=c.post('/api/analyze',json={'subject':'','body':r.json()['extracted_text'],'mode':mode}); record('extract then '+mode,a)
            assert a.json()['classification']=='suspicious'
record('non-PDF extension',c.post('/api/pdf/extract',files={'file':('invalid.txt',b'text','text/plain')}),415)
r=c.post('/api/analyze',json={'body':'Team meeting tomorrow','mode':'combined'}); record('no match',r); assert r.json()['classification']=='no_configured_patterns_matched'
record('catalog',c.get('/api/automata'))
for aid in ['dfa_win_prize_now','nfa_phishing_branches']:
    record(aid,c.get('/api/automata/'+aid))
    r=c.post('/api/automata/'+aid+'/simulate',json={'input_text':'WIN PRIZE NOW'}); record(aid+' simulation',r); assert r.json()['accepted']
record('subset construction',c.get('/api/automata/nfa_phishing_branches/convert-to-dfa'))
r=c.options('/api/analyze',headers={'Origin':'http://localhost:3000','Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'content-type'}); assert r.headers['access-control-allow-origin']=='http://localhost:3000'
(root/'api-results.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print('Live HTTP checks passed:',len(checks),'plus CORS preflight')
import fastapi,uvicorn,pydantic,pypdf,multipart
print('Imports:',{m.__name__:m.__version__ for m in [fastapi,uvicorn,pydantic,pypdf,multipart]})
