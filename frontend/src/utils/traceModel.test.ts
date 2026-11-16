import test from 'node:test';
import assert from 'node:assert/strict';
import {traceFrame,edgeKey,closureSteps,moveCursor} from './traceModel.js';
const model={automaton_type:'nfa',states:['s','a','b','f'],alphabet:['WIN'],start_state:'s',accepting_states:['f'],transitions:[{from_state:'s',symbol:null,to_states:['a','b']},{from_state:'a',symbol:null,to_states:['s']},{from_state:'a',symbol:'WIN',to_states:['f']}]};
test('epsilon expansion terminates on cycles and preserves branches',()=>{const steps=closureSteps(model,['s']);assert.deepEqual(steps.at(-1)!.closure,['a','b','s']);assert.equal(steps.length,4)});
test('initial projection highlights epsilon edges, never unconsumed ordinary edges',()=>{const f=traceFrame(model,[{step:0,symbol:null,states_before:['s'],states_after:['s','a','b'],remaining_input:['WIN']}],0);assert.deepEqual(f.active,['s','a','b']);assert.ok(f.edges.includes(edgeKey('s',null,'b')));assert.ok(!f.edges.includes(edgeKey('a','WIN','f')))});
test('projection never invents edges between visited states',()=>{const f=traceFrame(model,[{step:1,symbol:'WIN',states_before:['s','a','b'],states_after:['f'],remaining_input:[]}],0);assert.deepEqual(f.edges,[edgeKey('a','WIN','f')]);assert.deepEqual(f.move,['f'])});
test('unexpected DFA tokens follow the actual other transition',()=>{const d={...model,automaton_type:'dfa',alphabet:['WIN','other'],transitions:[{from_state:'s',symbol:'WIN',to_states:['f']},{from_state:'s',symbol:'other',to_states:['b']}]};assert.deepEqual(traceFrame(d,[{step:1,symbol:'UNEXPECTED',states_before:['s'],states_after:['b']}],0).edges,[edgeKey('s','other','b')])});
test('back next reset respect cursor bounds',()=>{assert.equal(moveCursor(0,'back',3),0);assert.equal(moveCursor(3,'next',3),3);assert.equal(moveCursor(2,'reset',3),0);assert.equal(moveCursor(1,'next',3),2)});

