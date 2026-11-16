# Automata Security Lab — Technical Report

## 1. Project and purpose

**Email Spam & Phishing Pattern Recognition using DFA, epsilon-NFA and Regular Expressions.** This local academic application demonstrates transparent finite-language recognition and formal transformations. It is not a production phishing classifier. Email analysis remains the main entry point; all lab examples use configured email phrases or simple email-related character expressions.

## 2. Architecture and implementation

React 19/Vite/Tailwind provides four primary workspaces, with React Flow graphs in dedicated engine/lab routes. FastAPI/Pydantic validates requests, pypdf extracts selectable PDF text, and Python executes independent detection engines. No database, ML, mailbox integration, API key or external analysis is required. Educational operations are isolated in `app/engines/teaching.py` and additive `/api/lab` routes; they never alter classification rules.

```text
PDF or pasted email → review subject/body → FastAPI validation
   → whole-field DFA / whole-field ε-NFA / fixed substring regex
   → independent results + evidence + traces → reviewable UI

Finding → source-field simulation (or explicitly isolated regex phrase)
   → synchronized graph / active set / actual transitions / trace cursor

Lab → subset construction / Thompson / minimization / exact product / closure
```

## 3. Email language definitions

### DFA

Q = {q0,q1,q2,q3,q_dead}; alphabet = {WIN,PRIZE,NOW,other}; start q0; F = {q3}. Tokens are split on whitespace and uppercased. Transition q0/WIN→q1; q1/PRIZE→q2; q2/NOW→q3. Every other pair enters q_dead, which loops for every symbol. Therefore L = {WIN PRIZE NOW}. Empty, incomplete, reordered, punctuated or extra-token strings reject unless they exactly satisfy this token language. The catalog exposes the total transition table.

### Epsilon-NFA

Q = {s0,w0,w1,w2,w3,c0,c1,c2,c3,a0,a1,a2,a3}; start s0; F = {w3,c3,a3}. Epsilon is not an input symbol. From s0, epsilon edges reach w0,c0,a0. Branch transitions are:

| Branch | Transitions |
|---|---|
| Reward | w0 —WIN→ w1 —PRIZE→ w2 —NOW→ w3 |
| Claim | c0 —CLAIM→ c1 —REWARD→ c2 —NOW→ c3 |
| Verify | a0 —ACCOUNT→ a1 —VERIFY→ a2 —IMMEDIATELY→ a3 |

L is exactly those three complete phrases, using the same case-insensitive whitespace tokenization as the DFA. Simulation maintains every active state, takes epsilon closure initially and after moves, and accepts only if the final active set intersects F. Unknown token moves may produce the empty set.

### Fixed Python regex rules

The six rules recognize HTTP(S) URLs, simplified email addresses, the three configured phrases, and two or more exclamation marks. Python `re.finditer` scans subject/body independently and reports exact original text and Unicode code-point offsets. These are substring matches rather than whole-field acceptance; a URL or address may be entirely legitimate. The actual expressions are defined in `regex_engine.py` and displayed in the Theory page explanation/detection evidence, not generated from the lab grammar.

### Orchestration and limitations

Automata use the body when nonblank, otherwise subject. Regex scans both. Modes dfa/nfa/regex execute only the selected engine; combined executes all three. Any configured match yields `suspicious`; otherwise `no_configured_patterns_matched` plus a safety warning. DFA/NFA acceptance scores 100, regex 20 per distinct matched rule up to 100, combined maximum. This score has no statistical interpretation. Counts overlap across detectors.

## 4. PDF and privacy behavior

`POST /api/pdf/extract` accepts `.pdf`, allowed PDF/octet-stream MIME and a near-leading `%PDF-` signature; reads up to 10 MB + one byte and rejects oversize, empty, malformed, encrypted or textless files with meaningful errors. pypdf extracts text from memory; uploaded bytes are not intentionally retained by application code. Framework multipart handling may spool larger files into temporary OS storage. OCR is not present. Layout may change reading order, so the UI exposes editable extracted text and labels edits. No subject/sender metadata is invented. All email strings are React text, not injected HTML; detected URLs are not fetched.

## 5. Interactive experience

Routes: `/` Analyze Email, `/engine?detector=dfa|nfa`, `/lab?tool=...`, `/theory`. `/about` remains and `/how-it-works` redirects. The existing Lab and React Flow components were connected and enhanced rather than replacing backend detection.

A shared playback cursor drives graph state, exact transition identities, consumed/current tokens, previous/current state sets, next transition, remaining input, transition-table cells and trace row. Next/Back/Play/Pause/Reset plus a native keyboard-operable slider are available. Autoplay is explicit; reduced-motion CSS disables decorative animation. Acceptance is labeled final only once the entire input is consumed. Graph start/accept/dead/active indicators have text/shape as well as color; tables provide text alternatives. There is no automatic offline replacement of a failed API response.

Email evidence can be located in its original field using code-point-aware highlighting. DFA/NFA findings open their complete source field and actual backend trace. A supported regex phrase can separately open an **isolated phrase** simulation, explicitly warning that this does not establish whole-email acceptance. Other Python regex findings are explained without inventing equivalent automata.

## 6. Genuine algorithms

### Epsilon closure

A queue/visited-set traversal follows only epsilon edges, starting with the seed itself. Each traversed edge, newly discovered state, current closure and final set are exposed. A visited set makes epsilon cycles terminate. The explorer uses the configured NFA, not a separate invented graph.

### NFA to DFA

The reusable subset algorithm starts at epsilon-closure({q0}); for every reachable subset T and symbol a computes U = epsilon-closure(move(T,a)). New subsets enter a queue. A subset accepts iff it intersects the original accepting set; the empty subset becomes D_dead. The studio uses the real existing backend conversion response and incrementally synchronizes discovered states, edges, subset labels and the table. No state/edge counts are hardcoded.

### Thompson regex to epsilon-NFA

The parser grammar is:

```text
union  := concat ('|' concat)*
concat := repeat+
repeat := atom '*'?
atom   := literal | '(' union ')'
```

Literals are ASCII letters/digits and `_@.!:/-`; dot is literal. Precedence is star, concatenation, union. Expression whitespace is ignored; example input is literal, case-sensitive characters. Empty groups/alternatives, repeated star, classes, escapes, +, ?, anchors and unsupported characters return syntax errors with positions. Empty input can still belong to a starred language. This is intentionally distinct from Python regex and token-level detection.

Literal fragments allocate entry/exit and one labeled edge. Concatenation adds an epsilon edge. Union introduces branching and joining states/epsilon edges. Star adds bypass, entry, repeat and exit epsilon edges. The response exposes AST, intermediate fragment snapshots, new states/edges and the final automaton. Simulation performs genuine epsilon-NFA execution over the constructed graph. Example `WIN|CLAIM` accepts those exact character strings; `(WIN)*` also accepts empty input.

### DFA minimization

Epsilon-NFAs are determinized first. Missing deterministic transitions receive an explicit rejecting sink with a collision-free name. Unreachable states are removed. Initial non-accepting/accepting blocks are refined by destination-block signatures for every alphabet symbol until no split remains. Each split exposes its old block, resulting groups and signatures. A quotient DFA contains one state per stable block. Tests use exact language equivalence, not only sample strings, to validate preservation. UI shows original reachable total graph, partitions, split explanations, stable classes, minimized graph/table and computed before/after counts.

### Exact equivalence

Supported epsilon-NFAs are correctly determinized. BFS explores product pairs over the union alphabet; missing transitions go to an implicit rejecting sink (None/⊥, never a user-state collision). If exactly one component accepts, parent links reconstruct a shortest distinguishing symbol sequence and both state paths. Initial acceptance disagreement returns the empty witness []. If the entire reachable product is exhausted, witness is null and the languages are equivalent. Finite sample comparisons are not used as a verdict. UI supports configured detectors, NFA versus minimized result, or two email-fragment expressions; generic supported models are accepted by the API.

## 7. API

Existing contracts remain intact:

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/health` | Backend health |
| POST | `/api/pdf/extract` | Multipart extraction |
| POST | `/api/analyze` | `{subject,body,mode}` detection |
| GET | `/api/automata` | Catalog |
| GET | `/api/automata/{id}` | Formal definition |
| POST | `/api/automata/{id}/simulate` | `{input_text}` computed trace |
| GET | `/api/automata/{id}/convert-to-dfa` | Configured NFA subset construction |

Additive educational API:

| POST route | Request |
|---|---|
| `/api/lab/thompson` | `{expression,input_text?}` |
| `/api/lab/minimize` | `{automaton?}`; defaults to configured NFA |
| `/api/lab/equivalence` | `{left,right}` formal automata |
| `/api/lab/closure` | `{automaton?,state}`; defaults to configured NFA |
| `/api/lab/simulate` | `{automaton,symbols}` explicit symbol list |

An automaton follows the existing catalog shape: id/name/description/type, states, alphabet, start_state, accepting_states, transitions with from_state/symbol/to_states. References and DFA determinism are validated. Lab requests forbid unknown fields; malformed grammar/models/limits return 422. GET `/docs` exposes full schemas. Existing analysis validation and response keys are unchanged.

## 8. Complexity and bounds

Let n be input length, q states, e edges, k alphabet size, and m expression length. Core DFA execution is O(n) with O(1) current-state memory; token lists and traces require additional storage. Epsilon-NFA simulation is O(n(q+e)) graph work. Closure is O(q+e) graph work. Subset construction can require O(2^q k(q+e)) time and O(2^q(q+k)) space. Thompson core construction is linear in m, but retained educational snapshots cost O(m²). This simple partition refinement has O(kq²) worst-case time and O(kq) tables, plus partition history. Exact product traversal has O(k q1 q2) time/O(q1 q2) space after possible exponential determinization. Stable sorting, verbose histories and response serialization add cost; remaining-input suffix copies can make simulation trace storage quadratic in n.

Safeguards: 10 MB PDFs; 10,000 combined email characters; expression 64 non-whitespace characters/128 raw and 32 distinct literals; constructed-string or generic-symbol simulation length 256; generic lab models ≤256 states, ≤32 symbols, ≤8192 transition entries. Subset construction caps at 256 states; product BFS caps at 16,384 pairs. A bound failure returns an explicit error with no equivalence verdict.

## 9. Testing and results

Baseline and final evidence are separated in `ENHANCEMENT_AUDIT.md` and `ENHANCEMENT_VERIFICATION.md`. Baseline was 73 backend and 7 frontend tests, with lint/build passing. Added tests cover Thompson precedence/grammar/language against independent Python regex on the supported subset, invalid syntax, epsilon cycles, exact counterexamples including empty input, partial DFAs/different alphabets, unreachable/dead states, minimization preservation by exact equivalence, API validation/limits, and trace projections/cursor bounds. Existing engine, PDF, evidence and combined-mode tests remain unchanged.

Browser verification exercises real file chooser/PDF extraction, pasted text, backend results, evidence links, playback and graph synchronization, subset construction, Thompson errors and simulation, partition refinement, equivalent/non-equivalent languages and epsilon closure. It is not a broad cross-browser/performance audit. See final verification for observed counts and screenshots.

## 10. Setup and demonstration

See root README for exact Windows/macOS setup and commands. On this machine the working app uses localhost:3001 because existing Grafana occupies 3000; a development proxy routes to real 127.0.0.1:8000 without changing backend CORS. Original localhost:3000 configuration still works when that port is free. Run pytest inside backend; run npm lint/build and both existing/new tsx tests inside frontend.

Demo: analyze WIN PRIZE NOW; locate evidence; open DFA, step forward/back, and try extra tokens. Switch to epsilon-NFA and inspect its initial parallel closure. Generate equivalent DFA and explore each subset. Construct WIN|CLAIM and simulate CLAIM. Minimize the configured recognizer and compare exactly. Compare single-phrase and three-phrase languages to obtain a real distinguishing phrase. Compare (WIN)* and WIN for the empty-string counterexample.

## 11. Viva answers and limitations

- **Why regex matches while an automaton rejects:** substring versus whole-input scope.
- **Why epsilon is not an alphabet symbol:** it consumes no input.
- **Why several states are active:** the NFA preserves every live branch.
- **Why determinization can grow exponentially:** states correspond to subsets of Q.
- **Why refinement preserves language:** merged states cannot be distinguished by any future symbol sequence at the stable partition.
- **Why equivalence is exact:** every reachable product pair is covered unless an explicit resource error stops the operation.
- **Why score is not probability:** it is a fixed deterministic rule formula with no calibration dataset.

False positives and false negatives are expected. The simplified Python URL/email rules are not full protocol/RFC validation. The existing illustrative tokenizer differs from backend whitespace semantics; live views use backend data only. No arbitrary Python regex is converted by Thompson. No OCR, arbitrary automaton editor, persistence/export project system, production email gateway or measured phishing-accuracy claim is included. Educational workspaces demonstrate supported finite automata within documented limits.

## 12. References

Sipser, *Introduction to the Theory of Computation*; Hopcroft, Motwani and Ullman, *Introduction to Automata Theory, Languages, and Computation*; Python `re` documentation; FastAPI/Pydantic, React and React Flow official documentation. Algorithm implementations and tests in this repository are the authoritative specification for the demonstrated subset and limitations.
