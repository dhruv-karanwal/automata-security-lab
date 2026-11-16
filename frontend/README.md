# Automata Security Lab frontend

React/Vite + Tailwind + React Flow, with the shared dark palette in `src/index.css`.

Routes: `/` Analyze Email; `/engine?detector=dfa|nfa` Detection Engine; `/lab?tool=subset|regex|minimize|equivalence|closure` Automata Lab; `/theory` Theory & Viva. `/about` remains available and `/how-it-works` redirects to `/theory`.

Live analysis, PDF extraction, simulation and algorithms use FastAPI. No automatic illustrative fallback or permanent email storage. Existing illustrative utility tests remain, but live workspaces never use them as backend responses.

See the root README for setup, run commands, detection semantics, grammar and demo. On this machine run:

```powershell
npm.cmd run dev -- --host 127.0.0.1 --port 3001 --strictPort --config vite.local.config.ts
```

Open http://localhost:3001. With free port 3000 use the original config and matching backend CORS. API base for original config: `VITE_API_BASE_URL`; the fallback config uses same-origin `/api` proxying to 127.0.0.1:8000.

```powershell
npm.cmd run lint
npm.cmd run build
npx.cmd --no-install tsx --test src/utils/engine.test.ts src/utils/traceModel.test.ts
```

Pure trace-projection tests verify epsilon branches/cycles, unexpected-token edges and cursor bounds. Browser verification covers mounted controls, graph state and API error behavior. Main pages are lazy-loaded so React Flow stays out of the initial email-analysis bundle.
