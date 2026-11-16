"""Additive, bounded educational endpoints; original detection API is unchanged."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.schemas import AutomatonDescription
from app.automata_catalog import AUTOMATA_BY_ID
from app.engines.teaching import Thompson, simulate, closure, minimize, equivalent, determinize
router=APIRouter(prefix='/api/lab',tags=['Automata Theory'])

class LabModel(AutomatonDescription):
    @model_validator(mode='after')
    def bounded_and_unambiguous(self):
        if len(self.states)>256 or len(self.alphabet)>32 or len(self.transitions)>8192:
            raise ValueError('Educational limits: 256 states, 32 alphabet symbols, 8192 transition entries.')
        if any(len(s)>64 for s in self.states) or any(not a or len(a)>32 for a in self.alphabet):
            raise ValueError('State names: at most 64 characters. Symbols: 1–32 characters.')
        seen=set()
        for t in self.transitions:
            key=(t.from_state,t.symbol)
            if self.automaton_type=='dfa' and key in seen: raise ValueError('DFA transitions must have a unique (state, symbol) key.')
            seen.add(key)
        return self
class StrictRequest(BaseModel):
    model_config=ConfigDict(extra='forbid')
class ThompsonRequest(StrictRequest):
    expression: str=Field(min_length=1,max_length=128)
    input_text: str=Field(default='',max_length=256)
class ModelRequest(StrictRequest):
    automaton: LabModel | None=None
class EquivalenceRequest(StrictRequest):
    left: LabModel
    right: LabModel
class ClosureRequest(ModelRequest):
    state: str=Field(default='s0',max_length=64)
class SimulationRequest(StrictRequest):
    automaton: LabModel
    symbols: list[str]=Field(default_factory=list,max_length=256)

def source(value):
    return value.model_dump(mode='json') if value else AUTOMATA_BY_ID['nfa_phishing_branches'].model_dump(mode='json')
def guarded(function,*args):
    try: return function(*args)
    except (ValueError,KeyError) as error: raise HTTPException(status_code=422,detail=str(error)) from error
@router.post('/thompson')
def thompson(request:ThompsonRequest):
    result=guarded(lambda:Thompson(request.expression).parse())
    if len(result['model']['alphabet'])>32: raise HTTPException(status_code=422,detail='At most 32 distinct literal symbols are supported.')
    result['simulation']=simulate(result['model'],list(request.input_text))
    return result
@router.post('/minimize')
def minimize_route(request:ModelRequest): return guarded(minimize,source(request.automaton))
@router.post('/equivalence')
def equivalence_route(request:EquivalenceRequest): return guarded(equivalent,source(request.left),source(request.right))
@router.post('/closure')
def closure_route(request:ClosureRequest):
    model=source(request.automaton)
    if request.state not in model['states']: raise HTTPException(status_code=422,detail='Selected state does not belong to the automaton.')
    found,steps=closure(model,[request.state]);return dict(model=model,closure=found,steps=steps)
@router.post('/simulate')
def simulate_route(request:SimulationRequest): return simulate(source(request.automaton),request.symbols)
