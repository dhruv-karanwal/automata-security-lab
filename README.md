# Automata Security Lab

A local email spam/phishing **pattern-recognition demonstrator**, combining PDF/text analysis with transparent DFA, epsilon-NFA and fixed regex engines. A match is not proof of phishing; no configured match is not a safety guarantee. No ML, external analysis service, API key, database or permanent email history is used.

## Existing stack and layout

- `backend/app/`: FastAPI schemas/routes, PDF extraction and detection engines.
- `backend/app/engines/teaching.py`, `backend/app/lab.py`: additive educational algorithms/API.
- `backend/tests/`: detection, PDF, schema, conversion and teaching regression tests.
- `frontend/src/`: React/Vite, Tailwind, React Flow, shared design/trace components and pages.
- `docs/PROJECT_REPORT.md`: formal definitions, semantics, algorithms, API, complexity, limitations and viva guide.
- `docs/ENHANCEMENT_AUDIT.md`: baseline audit; `docs/ENHANCEMENT_VERIFICATION.md`: final results/change inventory.

## Setup (Windows PowerShell)

Prerequisites verified here: Python 3.13.7, Node 22.20.0, npm 10.9.3. From this project root:

```powershell
python -m venv backend/.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
npm.cmd --prefix frontend ci
```

For macOS/Linux use `python3 -m venv backend/.venv`, `backend/.venv/bin/python`, and `npm` in the equivalent commands.

## Run (two terminals)

Backend:

```powershell
Set-Location 'C:\Users\tanis\OneDrive\Documents\ChatGPT\Automata-Email-Detector-local\backend'
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend on this machine, where Grafana already occupies port 3000:

```powershell
Set-Location 'C:\Users\tanis\OneDrive\Documents\ChatGPT\Automata-Email-Detector-local\frontend'
npm.cmd run dev -- --host 127.0.0.1 --port 3001 --strictPort --config vite.local.config.ts
```

Open **http://localhost:3001**. This local Vite config proxies `/api` to the real loopback backend. It does not substitute offline results. Backend docs: http://127.0.0.1:8000/docs.

When port 3000 is available, use the original config:

```powershell
npm.cmd run dev -- --host 127.0.0.1 --port 3000 --strictPort
```

Then open http://localhost:3000, the backend's original explicit CORS origin. `VITE_API_BASE_URL` optionally configures the API URL for the original config. Do not start duplicate listeners; stop each server with Ctrl+C first. No unrelated process needs to be stopped for port 3001.

## Four workspaces and demonstration

1. **Analyze Email `/`**: upload a text PDF (10 MB maximum), review/edit extracted body and optional subject, or paste text. Try `WIN PRIZE NOW` and analyze in combined mode. Inspect evidence, field-relative offsets, trace tables and the computed accepted-state preview. `Locate in email` highlights the exact Unicode span. A detector finding opens its real computation; supported regex phrase findings can open an explicitly labeled isolated-phrase simulation, not a claim that the complete email was accepted.
2. **Detection Engine `/engine?detector=dfa` or `nfa`**: run real backend simulation and use Next, Back, Play, Pause, Reset or the keyboard-operable step slider. Graph, current transition, active states, remaining input, trace row and transition table share the same cursor. Try `WIN PRIZE`, `PRIZE WIN NOW`, an extra token or empty input to demonstrate rejection. Epsilon-NFA initially activates `{s0,w0,c0,a0}` together.
3. **Automata Lab `/lab`**: choose subset construction, Thompson expression construction/simulation, partition-refinement minimization, exact equivalence, or epsilon closure. Each exposes computed intermediate steps. Compare the configured NFA to its minimized DFA for equivalence; compare the configured single-phrase DFA to the three-phrase NFA for a shortest distinguishing token sequence. For an empty-string witness compare `(WIN)*` with `WIN` in expression mode.
4. **Theory & Viva `/theory`**: formal definitions, actual grammar, algorithm explanations/complexity, limitations and expandable viva answers. Legacy `/how-it-works` redirects here; `/about` remains available.

## Preserved detection semantics

- DFA: case-insensitive **whitespace tokens**, accepts exactly `WIN PRIZE NOW`; punctuation is not stripped.
- Epsilon-NFA: exactly `WIN PRIZE NOW`, `CLAIM REWARD NOW`, or `ACCOUNT VERIFY IMMEDIATELY` after consuming the whole selected field.
- Automata analyze body, or subject when body is blank. Six fixed Python regex rules scan subject and body separately for URLs, email addresses, the three phrases, and repeated exclamation marks.
- Evidence offsets are zero-based, end-exclusive Unicode code-point offsets into the original field. React renders plain text.
- Combined mode preserves each independent detector result and takes the maximum educational score. Accepted DFA/NFA: 100; regex: 20 per distinct matched rule, capped at 100. This is not a calibrated probability.
- Subject and body together: at most 10,000 characters. PDF input must be a nonempty PDF with valid extension, MIME and signature. Malformed, encrypted and textless PDFs are rejected; no OCR. Application extraction is in memory; Starlette may temporarily spool larger multipart uploads at OS level. No permanent upload storage is added.

## Educational grammar and bounds

Thompson syntax: literal symbols, concatenation, union `|`, Kleene star `*`, parentheses. Precedence is `*` > concatenation > union. Literals are ASCII letters/digits and `_@.!:/-`; a dot is literal. Expression whitespace is ignored, input whitespace is not. Matching is **case-sensitive characters**, separate from token-based detection and from Python regex rules. Empty alternatives/groups and repeated `**` are invalid. Example `(WIN|CLAIM)*` accepts the empty string and concatenated phrase fragments.

Limits: expression 64 non-whitespace characters (128 raw), 32 distinct literals, simulation 256 characters/symbols; general lab models 256 states / 32 alphabet symbols / 8192 transition entries. Determinization caps at 256 subsets and product exploration at 16,384 pairs. Exceeding a bound returns an error, never a sampled equivalence claim.

## Verify

```powershell
Set-Location backend
.\.venv\Scripts\python.exe -m pytest -v
Set-Location ../frontend
npm.cmd run lint
npm.cmd run build
npx.cmd --no-install tsx --test src/utils/engine.test.ts src/utils/traceModel.test.ts
```

Run pytest from `backend/` (or set PYTHONPATH explicitly); the transferred project expects that import root. Browser checks and exact final counts are recorded in the verification document. No new dependencies were installed for the enhancement.
