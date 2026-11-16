/**
 * Clean formal automata specifications & graph definitions
 * Designed for clear academic viva presentation
 */

export const DFA_DEFINITION = {
  id: "dfa_win_prize_now",
  name: "DFA: WIN PRIZE NOW",
  description: "Recognizes exactly the complete token sequence: WIN → PRIZE → NOW. Order matters; missing, out-of-order, or extra tokens cause transition to dead state q_dead.",
  language: "L = { 'WIN PRIZE NOW' }",
  formal: {
    Q: ["q0", "q1", "q2", "q3", "q_dead"],
    Sigma: ["WIN", "PRIZE", "NOW", "other"],
    q0: "q0",
    F: ["q3"],
    deadState: "q_dead"
  },
  nodes: [
    {
      id: "q0",
      type: "automataNode",
      position: { x: 70, y: 90 },
      data: { label: "q0", isStart: true, isAccept: false, isDead: false }
    },
    {
      id: "q1",
      type: "automataNode",
      position: { x: 260, y: 90 },
      data: { label: "q1", isStart: false, isAccept: false, isDead: false }
    },
    {
      id: "q2",
      type: "automataNode",
      position: { x: 450, y: 90 },
      data: { label: "q2", isStart: false, isAccept: false, isDead: false }
    },
    {
      id: "q3",
      type: "automataNode",
      position: { x: 640, y: 90 },
      data: { label: "q3", isStart: false, isAccept: true, isDead: false }
    },
    {
      id: "q_dead",
      type: "automataNode",
      position: { x: 355, y: 240 },
      data: { label: "q_dead", isStart: false, isAccept: false, isDead: true }
    }
  ],
  edges: [
    { id: "e-q0-q1", source: "q0", target: "q1", label: "WIN" },
    { id: "e-q1-q2", source: "q1", target: "q2", label: "PRIZE" },
    { id: "e-q2-q3", source: "q2", target: "q3", label: "NOW" },
    { id: "e-q0-dead", source: "q0", target: "q_dead", label: "other", style: { strokeDasharray: "4 4" } },
    { id: "e-q1-dead", source: "q1", target: "q_dead", label: "other", style: { strokeDasharray: "4 4" } },
    { id: "e-q2-dead", source: "q2", target: "q_dead", label: "other", style: { strokeDasharray: "4 4" } },
    { id: "e-q3-dead", source: "q3", target: "q_dead", label: "extra token", style: { strokeDasharray: "4 4" } },
    { id: "e-dead-dead", source: "q_dead", target: "q_dead", label: "any" }
  ]
};

export const NFA_DEFINITION = {
  id: "nfa_phishing_branches",
  name: "NFA: Multi-Branch Phishing Recognizer",
  description: "Recognizes three configured threat sequences via epsilon (ε) branching from initial state s0. Epsilon transitions allow the automaton to move to a branch without reading an input token.",
  language: "L = { 'WIN PRIZE NOW', 'CLAIM REWARD NOW', 'ACCOUNT VERIFY IMMEDIATELY' }",
  formal: {
    Q: ["s0", "w0", "w1", "w2", "w3", "c0", "c1", "c2", "c3", "a0", "a1", "a2", "a3"],
    Sigma: ["WIN", "PRIZE", "NOW", "CLAIM", "REWARD", "ACCOUNT", "VERIFY", "IMMEDIATELY", "ε"],
    q0: "s0",
    F: ["w3", "c3", "a3"]
  },
  nodes: [
    {
      id: "s0",
      type: "automataNode",
      position: { x: 50, y: 180 },
      data: { label: "s0", isStart: true, isAccept: false, isDead: false }
    },
    // Branch 1: WIN PRIZE NOW
    { id: "w0", type: "automataNode", position: { x: 210, y: 50 }, data: { label: "w0", isStart: false, isAccept: false, isDead: false } },
    { id: "w1", type: "automataNode", position: { x: 370, y: 50 }, data: { label: "w1", isStart: false, isAccept: false, isDead: false } },
    { id: "w2", type: "automataNode", position: { x: 530, y: 50 }, data: { label: "w2", isStart: false, isAccept: false, isDead: false } },
    { id: "w3", type: "automataNode", position: { x: 690, y: 50 }, data: { label: "w3", isStart: false, isAccept: true, isDead: false } },

    // Branch 2: CLAIM REWARD NOW
    { id: "c0", type: "automataNode", position: { x: 210, y: 180 }, data: { label: "c0", isStart: false, isAccept: false, isDead: false } },
    { id: "c1", type: "automataNode", position: { x: 370, y: 180 }, data: { label: "c1", isStart: false, isAccept: false, isDead: false } },
    { id: "c2", type: "automataNode", position: { x: 530, y: 180 }, data: { label: "c2", isStart: false, isAccept: false, isDead: false } },
    { id: "c3", type: "automataNode", position: { x: 690, y: 180 }, data: { label: "c3", isStart: false, isAccept: true, isDead: false } },

    // Branch 3: ACCOUNT VERIFY IMMEDIATELY
    { id: "a0", type: "automataNode", position: { x: 210, y: 310 }, data: { label: "a0", isStart: false, isAccept: false, isDead: false } },
    { id: "a1", type: "automataNode", position: { x: 370, y: 310 }, data: { label: "a1", isStart: false, isAccept: false, isDead: false } },
    { id: "a2", type: "automataNode", position: { x: 530, y: 310 }, data: { label: "a2", isStart: false, isAccept: false, isDead: false } },
    { id: "a3", type: "automataNode", position: { x: 690, y: 310 }, data: { label: "a3", isStart: false, isAccept: true, isDead: false } }
  ],
  edges: [
    // Epsilon moves
    { id: "e-s0-w0", source: "s0", target: "w0", label: "ε", style: { strokeDasharray: "4 4" } },
    { id: "e-s0-c0", source: "s0", target: "c0", label: "ε", style: { strokeDasharray: "4 4" } },
    { id: "e-s0-a0", source: "s0", target: "a0", label: "ε", style: { strokeDasharray: "4 4" } },

    // Branch 1
    { id: "e-w0-w1", source: "w0", target: "w1", label: "WIN" },
    { id: "e-w1-w2", source: "w1", target: "w2", label: "PRIZE" },
    { id: "e-w2-w3", source: "w2", target: "w3", label: "NOW" },

    // Branch 2
    { id: "e-c0-c1", source: "c0", target: "c1", label: "CLAIM" },
    { id: "e-c1-c2", source: "c1", target: "c2", label: "REWARD" },
    { id: "e-c2-c3", source: "c2", target: "c3", label: "NOW" },

    // Branch 3
    { id: "e-a0-a1", source: "a0", target: "a1", label: "ACCOUNT" },
    { id: "e-a1-a2", source: "a1", target: "a2", label: "VERIFY" },
    { id: "e-a2-a3", source: "a2", target: "a3", label: "IMMEDIATELY" }
  ]
};
