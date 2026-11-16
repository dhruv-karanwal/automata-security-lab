"""Language-level regressions for the new educational algorithms and boundaries."""
from itertools import product
import re
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.engines.teaching import Thompson, simulate, pack, minimize, equivalent, closure, determinize
from app.engines.subset_construction import convert_nfa_to_dfa
from app.automata_catalog import AUTOMATA_BY_ID
client=TestClient(app)

@pytest.mark.parametrize('expr',['a','ab','a|b','a*','(a|b)*a','a(b|a)*','WIN|CLAIM','(a*)*'])
def test_thompson_agrees_with_independent_python_regex_for_supported_grammar(expr):
    model=Thompson(expr).parse()['model']
    for n in range(5):
        for symbols in product('ab',repeat=n):
            word=''.join(symbols)
            assert simulate(model,list(word))['accepted'] == bool(re.fullmatch(expr,word))
    if expr=='WIN|CLAIM':
        assert simulate(model,list('WIN'))['accepted']
        assert simulate(model,list('CLAIM'))['accepted']
        assert not simulate(model,list('win'))['accepted']

@pytest.mark.parametrize('expr',['','a|','|a','()','(a','a)','*a','a**','a+','[a]','a?','a\\d','é'])
def test_invalid_grammar_has_useful_errors(expr):
    with pytest.raises(ValueError): Thompson(expr).parse()

def test_closure_expands_epsilon_cycles_once():
    m=pack(['s','a','b'],['x'],'s',['b'],[('s',None,'a'),('a',None,'s'),('a',None,'b')])
    found,steps=closure(m,['s']);assert found==['a','b','s'];assert len(steps)==4

def test_partition_refinement_removes_unreachable_and_preserves_language_exactly():
    m=pack(['s','a','b','unused'],['x','y'],'s',['a','b'],[('s','x','a'),('s','y','b'),('a','x','a'),('a','y','b'),('b','x','a'),('b','y','b'),('unused','x','unused'),('unused','y','unused')],'dfa')
    r=minimize(m);assert r['after_count']==2;assert r['removed_unreachable']==['unused'];assert equivalent(m,r['model'])['equivalent']

def test_minimization_splits_non_equivalent_states_with_explanation():
    m=Thompson('WIN|CLAIM').parse()['model'];r=minimize(m)
    assert len(r['steps'])>1;assert r['steps'][1]['splits'];assert equivalent(m,r['model'])['equivalent']

def test_minimization_handles_partial_dfa_and_dead_state():
    m=pack(['s','f'],['x'],'s',['f'],[('s','x','f')],'dfa')
    r=minimize(m);assert r['after_count']==3;assert equivalent(m,r['model'])['equivalent']

@pytest.mark.parametrize('accept',[[],['s']])
def test_minimization_handles_empty_alphabet_and_uniform_acceptance(accept):
    m=pack(['s'],[],'s',accept,[],'dfa');r=minimize(m);assert r['after_count']==1;assert equivalent(m,r['model'])['equivalent']

def test_exact_equivalence_returns_empty_witness_when_initial_acceptance_differs():
    a=pack(['s'],[],'s',['s'],[],'dfa');b=pack(['s'],[],'s',[],[],'dfa')
    r=equivalent(a,b);assert not r['equivalent'];assert r['witness']==[];assert len(r['path'])==1

def test_exact_equivalence_returns_shortest_distinguishing_input_and_paths():
    a=Thompson('WIN').parse()['model'];b=Thompson('WIN|CLAIM').parse()['model'];r=equivalent(a,b)
    assert not r['equivalent'];assert ''.join(r['witness'])=='CLAIM';assert len(r['path'])==len(r['witness'])+1
    assert simulate(a,r['witness'])['accepted']!=simulate(b,r['witness'])['accepted']

def test_missing_transitions_and_different_alphabets_use_implicit_sinks():
    a=pack(['s'],['x'],'s',[],[],'dfa');b=pack(['s'],['y'],'s',[],[('s','y','s')],'dfa')
    assert equivalent(a,b)['equivalent']

def test_configured_nfa_subset_and_minimized_dfa_exact_equivalence():
    m=AUTOMATA_BY_ID['nfa_phishing_branches'].model_dump(mode='json');d=determinize(m)
    assert equivalent(m,d)['equivalent'];assert equivalent(d,minimize(d)['model'])['equivalent']

def test_subset_budget_errors_without_false_equivalence_verdict():
    m=Thompson('ab').parse()['model']
    from app.engines.teaching import relation
    with pytest.raises(ValueError,match='limit'):
        convert_nfa_to_dfa(states=set(m['states']),alphabet=set(m['alphabet']),start_state=m['start_state'],accepting_states=set(m['accepting_states']),transition_relation=relation(m),max_states=1)

def test_lab_endpoints_use_real_algorithms_and_preserve_original_analysis():
    r=client.post('/api/lab/thompson',json={'expression':'WIN|CLAIM','input_text':'CLAIM'});assert r.status_code==200;r=r.json();assert r['simulation']['accepted'];assert r['fragments'];assert r['syntax_tree']['type']=='union'
    mini=client.post('/api/lab/minimize',json={});assert mini.status_code==200
    nfa=AUTOMATA_BY_ID['nfa_phishing_branches'].model_dump(mode='json')
    eq=client.post('/api/lab/equivalence',json={'left':nfa,'right':mini.json()['model']});assert eq.status_code==200;assert eq.json()['equivalent']
    c=client.post('/api/lab/closure',json={'state':'s0'});assert c.json()['closure']==['a0','c0','s0','w0']
    s=client.post('/api/lab/simulate',json={'automaton':r['model'],'symbols':list('WIN')});assert s.json()['accepted']
    old=client.post('/api/analyze',json={'body':'WIN PRIZE NOW','mode':'combined'}).json();assert old['classification']=='suspicious';assert old['risk_score']==100

def test_lab_validation_limits_and_invalid_dfa_definitions():
    assert client.post('/api/lab/thompson',json={'expression':'a+'}).status_code==422
    assert client.post('/api/lab/thompson',json={'expression':'a'*65}).status_code==422
    assert client.post('/api/lab/closure',json={'state':'unknown'}).status_code==422
    m=pack(['s','f'],['x'],'s',['f'],[('s','x','s'),('s','x','f')],'dfa')
    assert client.post('/api/lab/minimize',json={'automaton':m}).status_code==422
    m=pack(['s'],['x'],'s',[],[('s','x','s')],'dfa');m['transitions']*=2
    assert client.post('/api/lab/minimize',json={'automaton':m}).status_code==422

def test_product_budget_returns_error_instead_of_bounded_equivalence():
    def cycle(size):
        names=[str(i) for i in range(size)]
        return pack(names,['x'],'0',[],[(str(i),'x',str((i+1)%size)) for i in range(size)],'dfa')
    with pytest.raises(ValueError,match='no equivalence verdict'):
        equivalent(cycle(129),cycle(131))

def test_configured_dfa_other_category_preserves_real_counterexample_path():
    left=AUTOMATA_BY_ID['dfa_win_prize_now'].model_dump(mode='json')
    right=AUTOMATA_BY_ID['nfa_phishing_branches'].model_dump(mode='json')
    r=equivalent(left,right)
    assert not r['equivalent']
    assert r['path'][1]['left']=='q_dead'
