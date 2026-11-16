"""Finite-automata teaching algorithms. Independent of email classification.

All symbols are explicit strings. Missing DFA transitions reject through an
implicit nonaccepting sink; epsilon is None and is never an alphabet symbol.
"""
from collections import defaultdict, deque
from app.engines.subset_construction import convert_nfa_to_dfa


def pack(states, alphabet, start, accepting, edges, kind='nfa', name='Educational automaton'):
    grouped = defaultdict(set)
    for source, symbol, target in edges:
        grouped[(source, symbol)].add(target)
    return dict(automaton_id='educational', name=name, description='Computed educational automaton; not a new email rule.', automaton_type=kind,
                states=list(states), alphabet=sorted(alphabet), start_state=start, accepting_states=sorted(accepting),
                transitions=[dict(from_state=s, symbol=a, to_states=sorted(ts)) for (s,a),ts in grouped.items()])


def relation(model):
    output = defaultdict(set)
    for t in model['transitions']:
        output[t['from_state'], t['symbol']].update(t['to_states'])
    return {k:frozenset(v) for k,v in output.items()}


def closure(model, seeds):
    rel=relation(model)
    found=set(seeds); queue=deque(sorted(found))
    steps=[dict(source=None, target=None, newly_discovered=sorted(found), closure=sorted(found), explanation='Initial seed set; zero epsilon moves.')]
    while queue:
        source=queue.popleft()
        for target in sorted(rel.get((source,None),())):
            fresh=target not in found
            if fresh: found.add(target); queue.append(target)
            steps.append(dict(source=source,target=target,newly_discovered=[target] if fresh else [],closure=sorted(found),explanation='Discover through epsilon.' if fresh else 'Already discovered; do not expand again.'))
    return sorted(found),steps


def simulate(model, symbols):
    active, initial = closure(model,[model['start_state']])
    trace=[dict(step=0,symbol=None,states_before=[model['start_state']],states_after=active,closure_before=[model['start_state']],move_result=[model['start_state']],closure_steps=initial,remaining_input=symbols,explanation='Take the initial epsilon closure.')]
    rel=relation(model)
    for i,symbol in enumerate(symbols):
        before=active; direct=set()
        for source in before: direct.update(rel.get((source,symbol),()))
        active,expansion=closure(model,direct)
        trace.append(dict(step=i+1,symbol=symbol,states_before=before,states_after=active,closure_before=before,move_result=sorted(direct),closure_steps=expansion,remaining_input=symbols[i+1:],explanation=f'Consume {symbol!r}, union every destination, then expand epsilon closure.'))
    return dict(accepted=bool(set(active)&set(model['accepting_states'])),active_states=active,trace=trace)


class Thompson:
    """Grammar: union := concat ('|' concat)*; concat := repeat+;
    repeat := atom '*'?; atom := literal | '(' union ')'.
    Literals: ASCII letters, digits and _@.!:/-. Whitespace is ignored in the
    expression only. Input strings remain case-sensitive, literal characters.
    """
    def __init__(self, expression):
        self.expr=''.join(expression.split()); self.pos=0; self.states=[]; self.edges=[]; self.fragments=[]
        if not self.expr: raise ValueError('Enter a nonempty expression, for example WIN|CLAIM.')
        if len(self.expr)>64: raise ValueError('Expressions are limited to 64 non-whitespace characters.')

    def state(self):
        name=f't{len(self.states)}'; self.states.append(name); return name

    def fragment(self, operation, start, end, created, edges, ast):
        self.edges.extend(edges)
        self.fragments.append(dict(step=len(self.fragments)+1,operation=operation,start_state=start,accepting_state=end,created_states=created,
            created_transitions=[dict(from_state=s,symbol=a,to_states=[t]) for s,a,t in edges],states=list(self.states),transitions=[dict(from_state=s,symbol=a,to_states=[t]) for s,a,t in self.edges],explanation=f'{operation}: fragment {start} → {end}.'))
        return start,end,ast

    def peek(self): return self.expr[self.pos] if self.pos<len(self.expr) else None

    def parse(self):
        start,end,ast=self.union()
        if self.pos!=len(self.expr): raise ValueError(f'Unexpected {self.peek()!r} at position {self.pos+1}.')
        alphabet={a for _,a,_ in self.edges if a is not None}
        return dict(model=pack(self.states,alphabet,start,[end],self.edges,name='Thompson email-fragment expression'),syntax_tree=ast,fragments=self.fragments,grammar='literal, concatenation, |, *, parentheses; precedence: * > concatenation > |; case-sensitive character symbols.')

    def union(self):
        left=self.concat()
        while self.peek()=='|':
            self.pos+=1; right=self.concat(); start=self.state(); end=self.state()
            left=self.fragment('union',start,end,[start,end],[(start,None,left[0]),(start,None,right[0]),(left[1],None,end),(right[1],None,end)],dict(type='union',children=[left[2],right[2]]))
        return left

    def concat(self):
        if self.peek() is None or self.peek() in '|)': raise ValueError(f'Expected a literal or parenthesized expression at position {self.pos+1}; empty alternatives/groups are unsupported.')
        left=self.repeat()
        while self.peek() is not None and self.peek() not in '|)':
            right=self.repeat()
            left=self.fragment('concatenation',left[0],right[1],[],[(left[1],None,right[0])],dict(type='concat',children=[left[2],right[2]]))
        return left

    def repeat(self):
        atom=self.atom()
        if self.peek()=='*':
            self.pos+=1; start=self.state(); end=self.state()
            atom=self.fragment('Kleene star',start,end,[start,end],[(start,None,atom[0]),(start,None,end),(atom[1],None,atom[0]),(atom[1],None,end)],dict(type='star',children=[atom[2]]))
            if self.peek()=='*': raise ValueError(f'Repeated star at position {self.pos+1}; use one * operator.')
        return atom

    def atom(self):
        token=self.peek()
        if token=='(':
            self.pos+=1; result=self.union()
            if self.peek()!=')': raise ValueError(f'Missing closing parenthesis near position {self.pos+1}.')
            self.pos+=1; return result
        if token is not None and token.isascii() and (token.isalnum() or token in '_@.!:/-'):
            self.pos+=1; start=self.state(); end=self.state()
            return self.fragment(f'literal {token}',start,end,[start,end],[(start,token,end)],dict(type='literal',value=token))
        raise ValueError(f'Unsupported symbol {token!r} at position {self.pos+1}. Use ASCII literals, |, *, and parentheses; no Python regex classes, escapes or anchors.')


def determinize(model):
    if model['automaton_type']=='dfa': return model
    result=convert_nfa_to_dfa(states=set(model['states']),alphabet=set(model['alphabet']),start_state=model['start_state'],accepting_states=set(model['accepting_states']),transition_relation=relation(model))
    return pack([s.state_id for s in result.states],result.alphabet,result.start_state,result.accepting_states,[(t.from_state,t.symbol,t.to_state) for t in result.transitions],kind='dfa',name='Subset DFA')


def completed(model):
    """Materialize a sink, then keep only reachable states."""
    model=determinize(model); states=set(model['states']); alphabet=model['alphabet']; rel=relation(model)
    sink='__sink__'
    while sink in states: sink+='_'  # never collide with a user state
    delta={(s,a):next(iter(ts)) for (s,a),ts in rel.items()}
    missing=any((s,a) not in delta for s in states for a in alphabet)
    if missing:
        for s in states|{sink}:
            for a in alphabet: delta.setdefault((s,a),sink)
        states.add(sink)
    reachable={model['start_state']}; queue=deque(reachable)
    while queue:
        source=queue.popleft()
        for a in alphabet:
            target=delta[source,a]
            if target not in reachable: reachable.add(target);queue.append(target)
    output=pack(sorted(reachable),alphabet,model['start_state'],set(model['accepting_states'])&reachable,[(s,a,delta[s,a]) for s in sorted(reachable) for a in alphabet],kind='dfa',name='Reachable total DFA')
    return output,delta,sorted(set(model['states'])-reachable)


def minimize(model):
    total,delta,removed=completed(model); accept=set(total['accepting_states']); alphabet=total['alphabet']
    partitions=[p for p in [set(total['states'])-accept,accept] if p]
    snapshots=[dict(partitions=[sorted(p) for p in partitions],splits=[],explanation='Initial accepting and non-accepting partitions; unreachable states removed.')]
    while True:
        block={s:i for i,p in enumerate(partitions) for s in p}; refined=[]; splits=[]
        for p in partitions:
            groups=defaultdict(set)
            for s in sorted(p): groups[tuple(block[delta[s,a]] for a in alphabet)].add(s)
            refined.extend(groups.values())
            if len(groups)>1: splits.append(dict(block=sorted(p),groups=[dict(states=sorted(g),signature=list(signature)) for signature,g in groups.items()]))
        if not splits: break
        partitions=refined
        snapshots.append(dict(partitions=[sorted(p) for p in partitions],splits=splits,explanation='Split states whose destinations belong to different partition blocks for at least one alphabet symbol. Signatures follow alphabet order.'))
    names={s:f'M{i}' for i,p in enumerate(partitions) for s in p}; edges=[]
    for p in partitions:
        representative=sorted(p)[0]
        for a in alphabet: edges.append((names[representative],a,names[delta[representative,a]]))
    minimal=pack([f'M{i}' for i in range(len(partitions))],alphabet,names[total['start_state']],{names[s] for s in accept},edges,'dfa','Minimized email-pattern DFA')
    return dict(original=model,total_model=total,model=minimal,steps=snapshots,classes=[dict(state=f'M{i}',members=sorted(p)) for i,p in enumerate(partitions)],removed_unreachable=removed,before_count=len(total['states']),after_count=len(minimal['states']))


def equivalent(left,right):
    left=determinize(left);right=determinize(right)
    alphabet=sorted(set(left['alphabet'])|set(right['alphabet']))
    lrel=relation(left);rrel=relation(right)
    def dest(rel,s,a,model):
        # The original detector's catalog uses an abstract OTHER category.
        # Preserve its actual unexpected-token path when aligning alphabets.
        if model.get('automaton_id')=='dfa_win_prize_now' and a not in model['alphabet']:
            a='other'
        return next(iter(rel.get((s,a),())),None) if s is not None else None
    start=(left['start_state'],right['start_state']);queue=deque([start]);parents={start:None};steps=[]
    while queue:
        pair=queue.popleft(); la=pair[0] in left['accepting_states'];ra=pair[1] in right['accepting_states']
        steps.append(dict(left=pair[0],right=pair[1],left_accepting=la,right_accepting=ra,distinguishing=la!=ra))
        if la!=ra:
            word=[];path=[pair];cursor=pair
            while parents[cursor] is not None:
                previous,symbol=parents[cursor];word.append(symbol);path.append(previous);cursor=previous
            return dict(equivalent=False,witness=list(reversed(word)),path=[dict(left=l,right=r) for l,r in reversed(path)],exploration=steps,left=left,right=right,alphabet=alphabet)
        for a in alphabet:
            target=(dest(lrel,pair[0],a,left),dest(rrel,pair[1],a,right))
            if target not in parents:
                if len(parents)>=16384: raise ValueError('Product exploration exceeds 16,384 pairs; no equivalence verdict was made.')
                parents[target]=(pair,a);queue.append(target)
    return dict(equivalent=True,witness=None,path=[],exploration=steps,left=left,right=right,alphabet=alphabet)
