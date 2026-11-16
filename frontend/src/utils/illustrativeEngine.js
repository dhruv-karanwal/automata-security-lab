/**
 * Illustrative Client-Side Automata & Regex Engine
 * Used for educational simulation previews and testable verification.
 * Clearly tagged with illustrative metadata.
 */

import { PATTERNS_DATA } from '../data/patternsData.js';
import { tokenizeText } from './tokenizer.js';

/**
 * Simulates the deterministic finite automaton for "WIN PRIZE NOW"
 * @param {string[]|string} input - Token array or raw string
 * @returns {{
 *   automatonId: string,
 *   type: string,
 *   isAccepted: boolean,
 *   finalState: string,
 *   visitedStates: string[],
 *   tokensCount: number,
 *   tokens: string[],
 *   trace: object[],
 *   explanation: string
 * }} execution result and trace
 */
export function simulateDFA(input) {
  const tokens = Array.isArray(input) ? input : tokenizeText(input);
  const trace = [];
  let currentState = 'q0';
  const visitedStates = ['q0'];

  trace.push({
    step: 0,
    state: 'q0',
    consumedToken: null,
    remainingTokens: [...tokens],
    action: 'Initial state q0 reached (Start)',
    transitionNote: 'Expecting token WIN'
  });

  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];
    const prev = currentState;
    let next;
    let note;

    if (currentState === 'q0') {
      if (token === 'WIN') {
        next = 'q1';
        note = "δ(q0, 'WIN') → q1 (Matched 1st token)";
      } else {
        next = 'q_dead';
        note = `δ(q0, '${token}') → q_dead (Unexpected token; expected WIN)`;
      }
    } else if (currentState === 'q1') {
      if (token === 'PRIZE') {
        next = 'q2';
        note = "δ(q1, 'PRIZE') → q2 (Matched 2nd token)";
      } else {
        next = 'q_dead';
        note = `δ(q1, '${token}') → q_dead (Unexpected token; expected PRIZE)`;
      }
    } else if (currentState === 'q2') {
      if (token === 'NOW') {
        next = 'q3';
        note = "δ(q2, 'NOW') → q3 (Matched 3rd token: ACCEPTING)";
      } else {
        next = 'q_dead';
        note = `δ(q2, '${token}') → q_dead (Unexpected token; expected NOW)`;
      }
    } else if (currentState === 'q3') {
      next = 'q_dead';
      note = `δ(q3, '${token}') → q_dead (Extra token rejected! DFA recognizes strictly 3-token sequence)`;
    } else {
      next = 'q_dead';
      note = `δ(q_dead, '${token}') → q_dead (Trap state self-loop)`;
    }

    currentState = next;
    visitedStates.push(next);

    trace.push({
      step: i + 1,
      state: currentState,
      consumedToken: token,
      remainingTokens: tokens.slice(i + 1),
      action: currentState === 'q_dead' ? 'Trapped in q_dead' : `Transitioned from ${prev} to ${next}`,
      transitionNote: note
    });
  }

  const isAccepted = currentState === 'q3';

  return {
    automatonId: 'dfa_win_prize_now',
    type: 'DFA',
    isAccepted,
    finalState: currentState,
    visitedStates,
    tokensCount: tokens.length,
    tokens,
    trace,
    explanation: isAccepted
      ? "The complete token sequence matched 'WIN PRIZE NOW' exactly and halted in accepting state q3."
      : currentState === 'q_dead'
      ? "Input deviated from the strict sequence 'WIN PRIZE NOW' or contained extra tokens, halting in dead/trap state q_dead."
      : `Input ended prematurely at state ${currentState} before reaching the accepting state q3.`
  };
}

/**
 * Simulates non-deterministic finite automaton with epsilon branching
 * Recognizes:
 *  - "WIN PRIZE NOW"
 *  - "CLAIM REWARD NOW"
 *  - "ACCOUNT VERIFY IMMEDIATELY"
 * @param {string[]|string} input
 */
export function simulateNFA(input) {
  const tokens = Array.isArray(input) ? input : tokenizeText(input);
  const trace = [];

  // Epsilon-closure of start state s0 includes branch heads: w0, c0, a0
  let currentStates = new Set(['s0', 'w0', 'c0', 'a0']);
  const visitedStates = new Set(['s0', 'w0', 'c0', 'a0']);

  trace.push({
    step: 0,
    activeStates: Array.from(currentStates),
    consumedToken: null,
    remainingTokens: [...tokens],
    action: 'Initial state s0 active with ε-closure: {s0, w0, c0, a0}',
    notes: 'Non-deterministic branches active simultaneously for WIN, CLAIM, and ACCOUNT patterns.'
  });

  for (let i = 0; i < tokens.length; i++) {
    const token = tokens[i];
    const nextStates = new Set();
    const branchActions = [];

    // Evaluate Branch 1 (WIN PRIZE NOW)
    if (currentStates.has('w0') && token === 'WIN') {
      nextStates.add('w1');
      branchActions.push("Branch 1: w0 --[WIN]--> w1");
    }
    if (currentStates.has('w1') && token === 'PRIZE') {
      nextStates.add('w2');
      branchActions.push("Branch 1: w1 --[PRIZE]--> w2");
    }
    if (currentStates.has('w2') && token === 'NOW') {
      nextStates.add('w3');
      branchActions.push("Branch 1: w2 --[NOW]--> w3 (ACCEPT)");
    }

    // Evaluate Branch 2 (CLAIM REWARD NOW)
    if (currentStates.has('c0') && token === 'CLAIM') {
      nextStates.add('c1');
      branchActions.push("Branch 2: c0 --[CLAIM]--> c1");
    }
    if (currentStates.has('c1') && token === 'REWARD') {
      nextStates.add('c2');
      branchActions.push("Branch 2: c1 --[REWARD]--> c2");
    }
    if (currentStates.has('c2') && token === 'NOW') {
      nextStates.add('c3');
      branchActions.push("Branch 2: c2 --[NOW]--> c3 (ACCEPT)");
    }

    // Evaluate Branch 3 (ACCOUNT VERIFY IMMEDIATELY)
    if (currentStates.has('a0') && token === 'ACCOUNT') {
      nextStates.add('a1');
      branchActions.push("Branch 3: a0 --[ACCOUNT]--> a1");
    }
    if (currentStates.has('a1') && token === 'VERIFY') {
      nextStates.add('a2');
      branchActions.push("Branch 3: a1 --[VERIFY]--> a2");
    }
    if (currentStates.has('a2') && token === 'IMMEDIATELY') {
      nextStates.add('a3');
      branchActions.push("Branch 3: a2 --[IMMEDIATELY]--> a3 (ACCEPT)");
    }

    currentStates = nextStates;
    nextStates.forEach(s => visitedStates.add(s));

    trace.push({
      step: i + 1,
      activeStates: Array.from(currentStates),
      consumedToken: token,
      remainingTokens: tokens.slice(i + 1),
      action: branchActions.length > 0 ? branchActions.join(' | ') : 'No branch had a valid transition for this token (branch died)',
      notes: `Active states remaining: {${Array.from(currentStates).join(', ') || '∅'}}`
    });
  }

  const acceptStates = ['w3', 'c3', 'a3'];
  const matchedAcceptStates = acceptStates.filter(s => currentStates.has(s));
  const isAccepted = matchedAcceptStates.length > 0;

  const branchNames = [];
  if (currentStates.has('w3')) branchNames.push("'WIN PRIZE NOW' (Branch 1)");
  if (currentStates.has('c3')) branchNames.push("'CLAIM REWARD NOW' (Branch 2)");
  if (currentStates.has('a3')) branchNames.push("'ACCOUNT VERIFY IMMEDIATELY' (Branch 3)");

  return {
    automatonId: 'nfa_phishing_branches',
    type: 'NFA',
    isAccepted,
    finalActiveStates: Array.from(currentStates),
    visitedStates: Array.from(visitedStates),
    matchedAcceptStates,
    matchedBranches: branchNames,
    tokensCount: tokens.length,
    tokens,
    trace,
    explanation: isAccepted
      ? `NFA accepted via branch(es): ${branchNames.join(', ')}. One or more non-deterministic paths reached accepting states.`
      : currentStates.size === 0
      ? 'All non-deterministic branches died before consuming the full input.'
      : `Input completed but active states {${Array.from(currentStates).join(', ')}} do not intersect accept states {w3, c3, a3}.`
  };
}

/**
 * Executes configured regex catalogue against subject and body
 * @param {string} subject
 * @param {string} body
 */
export function runRegexScan(subject = '', body = '') {
  const combinedText = `${subject}\n${body}`;
  const matches = [];

  for (const rule of PATTERNS_DATA) {
    try {
      const reg = new RegExp(rule.regex, 'gi');
      const foundMatches = [];
      let m;
      while ((m = reg.exec(combinedText)) !== null) {
        foundMatches.push({
          matchText: m[0],
          index: m.index
        });
        // Avoid infinite loop on zero-width match
        if (m.index === reg.lastIndex) reg.lastIndex++;
      }

      if (foundMatches.length > 0) {
        matches.push({
          ruleId: rule.id,
          name: rule.name,
          category: rule.category,
          categoryLabel: rule.categoryLabel,
          regex: rule.regex,
          count: foundMatches.length,
          instances: foundMatches.map(f => f.matchText).slice(0, 5),
          relevance: rule.relevance,
          limitations: rule.limitations
        });
      }
    } catch (err) {
      console.error(`Regex evaluation error for ${rule.id}:`, err);
    }
  }

  return {
    detector: 'Regex Rule Engine',
    hasMatches: matches.length > 0,
    matchCount: matches.length,
    matches,
    summary: matches.length > 0
      ? `Detected ${matches.length} matching regular expression pattern(s) across message text.`
      : 'No configured regular expressions matched the analyzed subject and body.'
  };
}

/**
 * Runs illustrative multi-detector analysis
 * @param {string} subject
 * @param {string} body
 * @param {'combined'|'dfa'|'nfa'|'regex'} mode
 */
export function runIllustrativeAnalysis(subject = '', body = '', mode = 'combined') {
  const textForAutomata = body.trim() || subject.trim();
  const tokens = tokenizeText(textForAutomata);

  let dfaResult = null;
  let nfaResult = null;
  let regexResult = null;

  if (mode === 'combined' || mode === 'dfa') {
    dfaResult = simulateDFA(tokens);
  }
  if (mode === 'combined' || mode === 'nfa') {
    nfaResult = simulateNFA(tokens);
  }
  if (mode === 'combined' || mode === 'regex') {
    regexResult = runRegexScan(subject, body);
  }

  const suspiciousDetected = Boolean(
    (dfaResult && dfaResult.isAccepted) ||
    (nfaResult && nfaResult.isAccepted) ||
    (regexResult && regexResult.hasMatches)
  );

  const assessment = suspiciousDetected
    ? 'Suspicious Patterns Detected'
    : 'No Configured Suspicious Patterns Detected';

  return {
    isIllustrative: true,
    mode,
    assessment,
    tokens,
    dfa: dfaResult,
    nfa: nfaResult,
    regex: regexResult,
    timestamp: new Date().toISOString()
  };
}
