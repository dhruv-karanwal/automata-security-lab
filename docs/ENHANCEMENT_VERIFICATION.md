# Enhancement verification — 29 October 2026

## Outcome

All five requested implementation phases are complete within the explicitly documented supported grammar and resource limits. The main experience remains local email-pattern analysis. Four primary sections are Analyze Email, Detection Engine, Automata Lab and Theory & Viva. No runtime dependencies or technology-stack changes were added. No external analysis, ML, storage, Git commits, pushes or publishing were introduced.

Work was performed in `C:\Users\tanis\OneDrive\Documents\ChatGPT\Automata-Email-Detector-local`. The older saved project and original transferred archive remain untouched. A source-only pre-edit snapshot is retained at `verification/pre-enhancement-source.zip` (no dependencies or credentials).

## Baseline and final checks

| Check | Baseline | Final |
|---|---|---|
| Complete backend pytest | 73 passed | 109 passed |
| Existing plus new frontend tests | 7 passed | 12 passed |
| npm run lint (tsc --noEmit) | passed | passed |
| npm run build | passed | passed |
| pip check | passed during setup | passed |
| Existing live HTTP harness | passed during setup | 21 checks + CORS preflight passed |

All original tests are preserved byte-for-byte. Original DFA, epsilon-NFA and six-regex definitions, PDF extraction, catalog, API schemas and dependency manifest are unchanged. The existing subset converter gained a bounded-state safeguard; actual email-analysis semantics/response contracts did not change. Production pages are lazy-loaded; initial JS bundle is approximately 288 kB before gzip, with React Flow in an advanced-route shared chunk. Vite's existing non-fatal __dirname future-config-loader warning remains.

New backend tests compare supported Thompson languages to independent Python regex, check precedence/invalid grammar/epsilon cycles, unreachable and dead-state handling, minimization by exact equivalence, different alphabets/missing transitions, shortest and empty witnesses, original OTHER-category paths, API validation and explicit resource-limit failures. Frontend tests verify actual edge projection, epsilon branching/cycles and bounded navigation; they are complemented by actual mounted browser checks below.

## Actual browser verification

Performed against the real running FastAPI backend through the local Vite proxy, not by source inspection alone:

- Analyze pasted subject/body input; all four detection modes render real backend results.
- Choose a synthetic valid PDF through the browser file chooser, review extracted text, edit it and observe User-edited text.
- Upload invalid-signature, malformed, encrypted, textless, oversized and empty PDFs: each produced a meaningful error. Oversize is blocked in-browser; the independent live HTTP harness confirms backend 413 too.
- Ordinary text renders no configured match and the explicit no-safety-guarantee warning.
- Unicode-leading email text highlights correct source spans using code-point offsets. Supported regex phrase opens an explicitly isolated phrase trace; full-field automata findings open their complete source field.
- DFA Next/Back/Play/Pause/Reset and keyboard End on the step slider synchronize graph active state, current transition/table, position and trace. Empty input rejection verified.
- NFA initially shows s0, w0, c0, a0 active simultaneously, then w1 after WIN, and w3 at final acceptance.
- NFA-to-DFA current move/closure, discovered subsets, generated graph and final complete table verified.
- Thompson fragments and generated simulation verified for WIN|CLAIM with input CLAIM; invalid WIN+ produces a syntax-position error.
- Partition-refinement split explanations, stable classes and minimized graph/table verified.
- Exact NFA/minimized-DFA equivalence verified. Configured DFA/NFA comparison yields ACCOUNT VERIFY IMMEDIATELY; final corrected DFA path is q0 → q_dead → q_dead → q_dead. Expression (WIN)* versus WIN yields the empty-string witness.
- Epsilon explorer reaches the real final closure {a0,c0,s0,w0}; Theory & Viva and grammar content render.
- Actual backend process was stopped: analysis rendered HTTP 502 / Analysis unavailable with zero success banners. Backend was restarted and real analysis recovered. This was a real process outage, not a fabricated response or mocked fetch.
- Phone viewport 390×844: navigation opens/closes, engine controls work, and document width equals viewport content width (no horizontal page overflow). Graphs remain pannable and refit on resize; manual zoom is not reset on every trace step. Viewport override reset afterward.
- Fresh browser load of final DFA graph: five nodes, eight grouped transition edges, no console warnings/errors. Temporary HMR warnings while changing graph handles/types were resolved by clean reload; final clean-load behavior is verified.

Screenshots: `verification/enhancement-analyzer.jpg`, `enhancement-analyzer-full.jpg`, `enhancement-engine.jpg`, `enhancement-mobile.jpg`, `enhancement-outage.jpg`. Earlier setup screenshots are historical. Browser interactions were driven through the available browser tool; they are not represented as a newly committed Playwright test suite. Broader cross-browser, assistive-technology and performance audits were not performed.

## Running application and restart

Frontend: http://localhost:3001. Backend: http://127.0.0.1:8000; API docs: http://127.0.0.1:8000/docs. Both remain running. Existing Grafana occupies port 3000 and was not disturbed.

Restart in two terminals only after stopping the corresponding existing server:

```powershell
Set-Location 'C:\Users\tanis\OneDrive\Documents\ChatGPT\Automata-Email-Detector-local\backend'
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```powershell
Set-Location 'C:\Users\tanis\OneDrive\Documents\ChatGPT\Automata-Email-Detector-local\frontend'
npm.cmd run dev -- --host 127.0.0.1 --port 3001 --strictPort --config vite.local.config.ts
```

Root README contains fresh-setup commands and the original port-3000 option. `SETUP_VERIFICATION.md` records the historical pre-enhancement setup; this report supersedes its feature/source-change section.

## Limits and intentional exclusions

- Thompson grammar is the documented formal subset, not arbitrary Python regex. It is character-based and case-sensitive; the preserved email automata are whitespace-token based and case-insensitive. Dot is literal; no classes/escapes/anchors/+/? are supported.
- Expressions: 64 non-whitespace characters / 32 distinct literals. Lab models: 256 states / 32 symbols / 8192 transition entries. Determinization limit: 256 subsets; product limit: 16,384 pairs. Limits return explicit errors with no false verdict.
- The lab operates on supported computed/configured models. No visual arbitrary-automaton editor, import/export project system or persistence was requested or added; API accepts validated supported model definitions.
- No OCR or production phishing classifier. Pattern matches and heuristic scores retain their original limitations. Framework temporary multipart spooling remains possible; no permanent upload storage is introduced.
- Original legacy illustrative utility code is retained for its existing tests, but live workflows never silently substitute it for failed backend calls.
- Existing port-3000 conflict and non-fatal Vite config warning remain. All requested algorithm workspaces are implemented; no feature is labeled complete solely from a diagram.

## Complete source/documentation change inventory

Generated files (dependencies, dist, caches, logs, screenshots and JSON verification output) are separate from this source inventory. No original source file was deleted. Machine-readable list: `verification/enhancement-source-changes.json`.

| File | Change | Reason |
|---|---|---|
| `README.md` | modified | Current setup/run commands, routes, demo, semantics, grammar and limits. |
| `backend/app/engines/subset_construction.py` | modified | Optional 256-subset resource guard for constructed educational NFAs. |
| `backend/app/engines/teaching.py` | added | Thompson parser/construction, epsilon closure/simulation, completion, refinement and exact product search. |
| `backend/app/lab.py` | added | Validated bounded educational API requests/endpoints, without changing detection API. |
| `backend/app/main.py` | modified | Register the additive educational router; preserve original routes. |
| `backend/tests/test_teaching.py` | added | Language-level algorithm regressions, API validation, exact witnesses and resource limits. |
| `docs/ENHANCEMENT_AUDIT.md` | added | Pre-edit source audit and baseline results. |
| `docs/ENHANCEMENT_VERIFICATION.md` | added | Final verified results, remaining limits and complete change inventory. |
| `docs/PROJECT_REPORT.md` | modified | Actual algorithms, formal definitions, APIs, complexity, testing and viva content. |
| `frontend/README.md` | modified | Frontend routes, proxy/run commands and verification. |
| `frontend/format-enhancement.mjs` | added | Formatting helper using already-installed esbuild; no project dependency added. |
| `frontend/src/App.jsx` | modified | Four primary routes, legacy redirects and lazy-loaded advanced pages. |
| `frontend/src/components/AutomataGraph.jsx` | modified | Reuse React Flow with real transition identities, grouped labels, readable fallback lanes/loops and resize refit. |
| `frontend/src/components/AutomataNode.jsx` | modified | Accessible start/accept/active/dead state markers and graph handles. |
| `frontend/src/components/ExecutionTraceView.jsx` | modified | Reusable trace table synchronized to the playback cursor. |
| `frontend/src/components/Header.jsx` | modified | Shared workspace header and real backend health status. |
| `frontend/src/components/NfaToDfaConversion.jsx` | modified | Stepwise real subset result, source/generated graphs, subsets and synchronized table. |
| `frontend/src/components/ResultsPanel.jsx` | modified | Compact verdict/evidence, Unicode highlighting, accepted-state previews and source-aware trace links. |
| `frontend/src/components/Sidebar.jsx` | modified | Four-section responsive navigation. |
| `frontend/src/components/StepControls.jsx` | added | Shared Next/Back/Play/Pause/Reset and keyboard-operable slider; timer cleanup. |
| `frontend/src/components/TransitionTable.jsx` | added | Accessible text alternative from actual model transitions and current edges. |
| `frontend/src/components/studios/ClosureStudio.jsx` | added | Dedicated closure algorithm controls, computed intermediate results and visualization. |
| `frontend/src/components/studios/EquivalenceStudio.jsx` | added | Dedicated equivalence algorithm controls, computed intermediate results and visualization. |
| `frontend/src/components/studios/MinimizeStudio.jsx` | added | Dedicated minimize algorithm controls, computed intermediate results and visualization. |
| `frontend/src/components/studios/RegexStudio.jsx` | added | Dedicated regex algorithm controls, computed intermediate results and visualization. |
| `frontend/src/components/ui.jsx` | added | Shared panels, page intros, metrics and error states. |
| `frontend/src/hooks/useJob.js` | added | Shared explicit asynchronous operation/loading/error state. |
| `frontend/src/index.css` | modified | Fixed dark palette, shared UI tokens, responsive/keyboard/reduced-motion styling. |
| `frontend/src/pages/AboutPage.jsx` | modified | Consistent dark scope/privacy view. |
| `frontend/src/pages/AutomataLabPage.jsx` | modified | Real backend DFA/NFA playback and evidence-to-trace navigation. |
| `frontend/src/pages/DashboardPage.jsx` | modified | Subject/body and PDF analysis with validated inputs, shared state and real API results. |
| `frontend/src/pages/TeachingLabPage.jsx` | added | Route-aware five-tool lab workspace. |
| `frontend/src/pages/TheoryAboutPage.jsx` | modified | Actual concepts, grammar, fixed-rule catalogue, complexity and viva questions. |
| `frontend/src/services/api.js` | modified | Explicit lab requests; correct backend startup hint. |
| `frontend/src/utils/traceModel.js` | added | Pure edge identity, closure and trace projections; no coincidental visited-node paths. |
| `frontend/src/utils/traceModel.test.ts` | added | Branch/cycle, real-edge and cursor-bound regressions. |
