import test from 'node:test';
import assert from 'node:assert/strict';
import { tokenizeText } from './tokenizer.js';
import { simulateDFA, simulateNFA, runRegexScan, runIllustrativeAnalysis } from './illustrativeEngine.js';
import {
  createInitialEmailWorkspaceState,
  emailWorkspaceReducer,
} from '../state/emailWorkspaceState.js';

test('tokenizeText extracts clean uppercase tokens', () => {
  const tokens = tokenizeText('WIN PRIZE NOW');
  assert.deepEqual(tokens, ['WIN', 'PRIZE', 'NOW']);

  const punctuated = tokenizeText('WIN, PRIZE! NOW?');
  assert.deepEqual(punctuated, ['WIN', 'PRIZE', 'NOW']);

  const empty = tokenizeText('');
  assert.deepEqual(empty, []);
});

test('DFA strictly accepts "WIN PRIZE NOW" only', () => {
  // Correct sequence
  const acceptedResult = simulateDFA(['WIN', 'PRIZE', 'NOW']);
  assert.equal(acceptedResult.isAccepted, true);
  assert.equal(acceptedResult.finalState, 'q3');

  // Wrong token order
  const wrongOrder = simulateDFA(['PRIZE', 'WIN', 'NOW']);
  assert.equal(wrongOrder.isAccepted, false);
  assert.equal(wrongOrder.finalState, 'q_dead');

  // Extra tokens (rejection required by prompt)
  const extraTokens = simulateDFA(['WIN', 'PRIZE', 'NOW', 'EXTRA']);
  assert.equal(extraTokens.isAccepted, false);
  assert.equal(extraTokens.finalState, 'q_dead');

  // Incomplete sequence
  const incomplete = simulateDFA(['WIN', 'PRIZE']);
  assert.equal(incomplete.isAccepted, false);
  assert.equal(incomplete.finalState, 'q2');
});

test('NFA recognizes three distinct phishing branches', () => {
  // Branch 1: WIN PRIZE NOW
  const branch1 = simulateNFA(['WIN', 'PRIZE', 'NOW']);
  assert.equal(branch1.isAccepted, true);
  assert.ok(branch1.finalActiveStates.includes('w3'));

  // Branch 2: CLAIM REWARD NOW
  const branch2 = simulateNFA(['CLAIM', 'REWARD', 'NOW']);
  assert.equal(branch2.isAccepted, true);
  assert.ok(branch2.finalActiveStates.includes('c3'));

  // Branch 3: ACCOUNT VERIFY IMMEDIATELY
  const branch3 = simulateNFA(['ACCOUNT', 'VERIFY', 'IMMEDIATELY']);
  assert.equal(branch3.isAccepted, true);
  assert.ok(branch3.finalActiveStates.includes('a3'));

  // Unrecognized sequence
  const invalid = simulateNFA(['HELLO', 'TEAM', 'AGENDA']);
  assert.equal(invalid.isAccepted, false);
});

test('Regex engine detects URLs and repeated punctuation', () => {
  const scan = runRegexScan(
    'Account notification',
    'Please review this link: https://example.com/verify-account!!! and confirm'
  );

  assert.equal(scan.hasMatches, true);
  const ruleIds = scan.matches.map(m => m.ruleId);
  assert.ok(ruleIds.includes('RULE-URL'));
  assert.ok(ruleIds.includes('RULE-EXCLAMATION'));
});

test('Assessment labels follow security safety rules', () => {
  const detected = runIllustrativeAnalysis(
    'Reward Alert',
    'WIN PRIZE NOW',
    'combined'
  );
  assert.equal(detected.assessment, 'Suspicious Patterns Detected');

  const clean = runIllustrativeAnalysis(
    'Team Meeting',
    'Please review the agenda tomorrow.',
    'combined'
  );
  // Never label safe! Must be "No Configured Suspicious Patterns Detected"
  assert.equal(clean.assessment, 'No Configured Suspicious Patterns Detected');
});

test('email workspace state survives route changes until an explicit action changes it', () => {
  let state = createInitialEmailWorkspaceState();
  assert.equal(state.subject, '');
  assert.equal(state.body, '');

  state = emailWorkspaceReducer(state, { type: 'EDIT_SUBJECT', value: 'Custom subject' });
  state = emailWorkspaceReducer(state, { type: 'EDIT_BODY', value: 'Custom body text' });
  state = emailWorkspaceReducer(state, { type: 'SET_MODE', mode: 'regex' });
  state = emailWorkspaceReducer(state, {
    type: 'ANALYSIS_SUCCESS',
    result: { mode: 'regex', assessment: 'Suspicious Patterns Detected' },
    isOfflineDemo: false,
  });

  // Route navigation does not dispatch a workspace action, so the provider-held
  // object remains unchanged while Dashboard unmounts and mounts again.
  assert.equal(state.subject, 'Custom subject');
  assert.equal(state.body, 'Custom body text');
  assert.equal(state.selectedSampleKey, '');
  assert.equal(state.mode, 'regex');
  assert.deepEqual(state.result, {
    mode: 'regex',
    assessment: 'Suspicious Patterns Detected',
  });
});

test('loading extracted PDF text and clearing update the shared workspace intentionally', () => {
  let state = createInitialEmailWorkspaceState();
  state = emailWorkspaceReducer(state, {
    type: 'PDF_EXTRACTED',
    payload: {
      filename: 'saved-email.pdf',
      extracted_text: 'Please review https://example.com',
      extraction_note: 'Extracted locally.',
      page_count: 1,
    },
  });

  assert.equal(state.pdfFilename, 'saved-email.pdf');
  assert.equal(state.body, 'Please review https://example.com');
  assert.equal(state.isUserEdited, false);

  state = emailWorkspaceReducer(state, { type: 'EDIT_BODY', value: 'Reviewed text' });
  assert.equal(state.isUserEdited, true);

  state = emailWorkspaceReducer(state, { type: 'SET_MODE', mode: 'regex' });
  state = emailWorkspaceReducer(state, { type: 'CLEAR' });
  assert.equal(state.subject, '');
  assert.equal(state.body, '');
  assert.equal(state.selectedSampleKey, '');
  assert.equal(state.pdfFilename, '');
  assert.equal(state.originalExtractedText, '');
  assert.equal(state.result, null);
  assert.equal(state.mode, 'regex');
});
