# Local setup and verification — 28 October 2026

## Location and preservation

Working copy: C:\Users\tanis\OneDrive\Documents\ChatGPT\Automata-Email-Detector-local
Original saved project: C:\Users\tanis\OneDrive\Documents\ChatGPT\automata-email_detector
Archive: C:\Users\tanis\Downloads\Automata-Email-Detector.zip

The saved project is an older/different implementation (no PDF endpoint, JavaScript frontend, port 5173). The archive contains the requested PDF application. Extracted its source into a new sibling folder without overwriting either original. The saved repository has an unborn HEAD and untracked source; no Git initialization, commits, pushes, or worktree changes were made.

Archive inspection found macOS metadata, transferred .venv, node_modules, dist, Python/pytest caches, .env.example files, an inspection folder, and a nested ZIP. These were excluded from the fresh working copy. No credentials were printed. No new distributable archive was created.

Structure:
- backend/app/main.py: FastAPI routes and orchestration
- backend/app/schemas.py: API validation and response contracts
- backend/app/pdf_extraction.py: bounded PDF extraction
- backend/app/engines/: DFA, epsilon-NFA, regex, subset construction
- backend/tests/: complete pytest suite
- frontend/src/: React pages, components, API service, state, illustrative engine
- frontend/package-lock.json: npm dependency lock
- docs/PROJECT_REPORT.md and root README.md: original documentation

## Dependencies

Python 3.13.7; Node.js v22.20.0; npm 10.9.3. No global installation or prerequisite replacement was necessary.
Created a fresh backend/.venv and installed backend/requirements.txt. Imports verified: FastAPI 0.115.12, Uvicorn 0.34.2, Pydantic 2.14.1, pypdf 6.1.3, python-multipart 0.0.20; HTTPX 0.28.1, pytest 8.3.5, AnyIO 4.9.0. pip check passed.
Ran npm ci --no-audit --no-fund against the existing package-lock.json: 204 packages installed; Vite resolved to 8.3.5. Existing @google/genai dependency was retained for lockfile fidelity, but source inspection found no application usage; no AI service, key, or external analysis was introduced.

## Verification

- Full backend pytest -v: 73 passed, 0 failed.
- Frontend npm run lint (TypeScript noEmit): passed.
- Frontend npm run build: passed.
- Existing npx --no-install tsx --test src/utils/engine.test.ts: 7 passed, 0 failed.
- Local fallback config lint and build: passed.
- Live HTTP integration: 21 checks plus CORS preflight passed. Detailed responses: verification/api-results.json; repeatable harness: verify_local.py.
- Health: GET http://127.0.0.1:8000/api/health returns status ok and project Automata Security Lab.
- OpenAPI confirms /api/health, /api/pdf/extract, /api/analyze, /api/automata, /api/automata/{automaton_id}, its /simulate POST, and /convert-to-dfa GET.
- Extraction followed by analysis passed in dfa, nfa, regex, combined modes. Catalog, both simulators, subset construction and no-match classification passed.
- Live PDF responses: valid/ordinary 200; invalid signature, malformed, encrypted, textless and empty 400; oversized 413; non-PDF extension 415.
- CORS permits the original http://localhost:3000 origin. Local fallback uses same-origin Vite proxy to real 127.0.0.1:8000; backend CORS is unchanged.

## Actual browser interactions

Performed in the in-app browser at http://localhost:3001:
- App loaded and displayed Backend: Connected.
- Uploaded a synthetic valid text PDF through the real file chooser. Extracted WIN PRIZE NOW appeared before analysis.
- Edited extracted text to CLAIM REWARD NOW; User-edited text appeared.
- Real backend analysis rendered DFA rejection, NFA acceptance, regex match, score, verified-backend banner, evidence and source offsets.
- Exercised all four detector mode buttons with successful real analysis.
- Ordinary text rendered No Configured Suspicious Patterns Detected, score 0, and explicit warnings that no match does not guarantee safety.
- Uploaded invalid, malformed, encrypted, textless, oversized and empty PDFs; meaningful visible errors appeared for each. Oversized upload was blocked client-side; the live API independently rejected it too.
- Simulated an unavailable analysis backend by temporarily targeting an unused local port in the development proxy. Browser showed HTTP 502 Backend Connection Error; success banner was absent. The real backend process was NOT shut down for this test. Restored proxy, reloaded, uploaded and analyzed successfully afterward.
- Final screenshot: verification/browser-success.jpg. App tab retained.

These browser checks are distinct from source inspection, unit tests and live HTTP checks. Physical backend shutdown was not tested.

## Running servers and port limitation

Backend remains running at 127.0.0.1:8000 (listener PID 20528; launcher PID 13036 at verification).
Frontend remains running at 127.0.0.1:3001, accessible as http://localhost:3001 (persistent tool terminal session 45672).

The requested http://localhost:3000 is occupied by existing Grafana PID 5888. A strict Vite bind to 127.0.0.1:3000 failed with EACCES; browser navigation confirmed Grafana at localhost:3000/login. Grafana was left untouched. The user was asked about the conflict; no response had arrived during verification. Port 3001 is the working fallback, not an assertion that the requested port 3000 was achieved.

Automatic approval review rejected a backend restart command and a detached frontend launch command, without further reason. Backend was left running and frontend was launched successfully in a supported persistent terminal session.

## Restart commands (Windows PowerShell, separate terminals)

Run only after the corresponding existing server has stopped, to avoid duplicate listeners.

Backend:
```powershell
Set-Location 'C:\Users\tanis\OneDrive\Documents\ChatGPT\Automata-Email-Detector-local\backend'
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend (current Grafana-preserving fallback):
```powershell
Set-Location 'C:\Users\tanis\OneDrive\Documents\ChatGPT\Automata-Email-Detector-local\frontend'
npm.cmd run dev -- --host 127.0.0.1 --port 3001 --strictPort --config vite.local.config.ts
```
Open http://localhost:3001. API docs: http://127.0.0.1:8000/docs.

If port 3000 is freed later, use the original frontend config and matching existing backend CORS:
```powershell
Set-Location 'C:\Users\tanis\OneDrive\Documents\ChatGPT\Automata-Email-Detector-local\frontend'
npm.cmd run dev -- --host 127.0.0.1 --port 3000 --strictPort
```
Then open http://localhost:3000.

## Every source/config change

No original application source, manifest, lockfile, detection engine, test, or API contract remains modified. SHA-256 comparison of 51 relevant extracted source/manifest/documentation files matched the archive. A temporary backend CORS edit was fully reverted.

Added frontend/vite.local.config.ts only: extends the original Vite configuration, directs the browser API base to localhost:3001, and proxies /api to the real loopback backend. This resolves the occupied port without changing backend CORS or stopping Grafana. The temporary outage test route has been removed.

Added verification harness verify_local.py, verification/api-results.json, synthetic PDF fixtures, screenshot, this report, and generated local dependency/build/cache/log files. These are verification/setup artifacts, not replacement application code. No uploaded user email was retained.

## Remaining limitations

- Requested port 3000 remains occupied by Grafana; working URL is port 3001.
- Vite emits a non-fatal future native-config-loader warning about existing __dirname usage; lint/build pass. npm emitted an existing dependency deprecation notice for node-domexception.
- Existing UI error help uses uvicorn main:app, which is not the correct restart command for this layout; use app.main:app above.
- OCR is absent by design; scanned/image-only PDFs require OCR elsewhere. Exact automata recognize configured whole-input phrases only. The heuristic score is not a calibrated threat probability.
- Extraction reads bounded bytes into memory and adds no permanent upload storage. FastAPI/Starlette multipart handling may spool larger multipart files into OS temporary storage before application extraction; this pre-existing framework behavior was not changed.
- Browser outage check used a refused proxy target, not physical process shutdown. No broad cross-browser, accessibility, or performance audit was performed.

