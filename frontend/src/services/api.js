/**
 * Dedicated API Service Layer for Automata Security Lab
 * Connects to FastAPI backend at VITE_API_BASE_URL (default http://localhost:8000)
 */

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Backend wire types use snake_case. UI-specific camelCase fields are created
 * only in this service so page components do not need to understand both forms.
 *
 * @typedef {'combined'|'dfa'|'nfa'|'regex'} AnalysisMode
 * @typedef {{subject: string, body: string, mode: AnalysisMode}} AnalyzeEmailRequest
 * @typedef {{step: number, input_index: number, symbol: string|null, states_before: string[], states_after: string[], explanation: string}} TraceStep
 * @typedef {{pattern_id: string, name: string, category: string, evidence: Array<{source: 'subject'|'body', text: string, start_index: number, end_index: number}>}} MatchedPattern
 */

/**
 * Custom API Error class containing request metadata
 */
export class ApiError extends Error {
  constructor(message, status = null, details = null, isConnectionRefused = false) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
    this.isConnectionRefused = isConnectionRefused;
    this.endpoint = details?.endpoint || '';
  }
}

/**
 * Centralized fetch helper with timeout, error extraction, and network handling
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  const defaultHeaders = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };
  if (options.body instanceof FormData) {
    delete config.headers['Content-Type'];
  }

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 8000);

    const response = await fetch(url, {
      ...config,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    let data = null;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      const text = await response.text();
      try {
        data = JSON.parse(text);
      } catch {
        data = { message: text };
      }
    }

    if (!response.ok) {
      throw new ApiError(
        data?.detail || data?.message || `Backend returned status ${response.status} (${response.statusText})`,
        response.status,
        { endpoint, url, payload: data }
      );
    }

    return data;
  } catch (err) {
    if (err instanceof ApiError) {
      throw err;
    }

    const isAbort = err.name === 'AbortError';
    const isConnRefused = err.message.includes('Failed to fetch') ||
                          err.message.includes('NetworkError') ||
                          err.message.includes('Load failed') ||
                          isAbort;

    const friendlyMessage = isConnRefused
      ? `Cannot connect to FastAPI backend at ${API_BASE_URL}. Ensure the Python FastAPI server is running (e.g. uvicorn app.main:app --reload).`
      : err.message || 'An unexpected error occurred while communicating with the backend.';

    throw new ApiError(
      friendlyMessage,
      null,
      { endpoint, url, originalError: err.message },
      isConnRefused
    );
  }
}

function normalizeTrace(trace = [], engine = 'dfa') {
  return trace.map((row) => ({
    ...row,
    consumedToken: row.symbol,
    state: engine === 'dfa' ? row.states_after?.at(-1) : undefined,
    activeStates: engine === 'nfa' ? row.states_after : undefined,
    action: row.explanation,
  }));
}

function normalizeAutomatonResult(result, engine) {
  if (!result) return null;
  return {
    ...result,
    isAccepted: result.accepted,
    finalState: result.final_states?.at(-1) || null,
    finalActiveStates: result.active_states || [],
    matchedBranches: (result.matched_patterns || []).map((pattern) => pattern.pattern_id),
    trace: normalizeTrace(result.trace, engine),
  };
}

function normalizeRegexResult(result) {
  if (!result) return null;
  const matches = (result.matched_patterns || []).map((pattern) => ({
    ...pattern,
    ruleId: pattern.pattern_id,
    count: pattern.evidence.length,
    instances: pattern.evidence.map((item) => item.text),
    relevance: pattern.explanation,
  }));
  return {
    ...result,
    hasMatches: result.matched,
    matchCount: matches.length,
    matches,
    summary: result.explanation,
  };
}

function normalizeAnalysisResponse(data) {
  return {
    ...data,
    isIllustrative: false,
    assessment: data.classification === 'suspicious'
      ? 'Suspicious Patterns Detected'
      : 'No Configured Suspicious Patterns Detected',
    riskScore: data.risk_score,
    dfa: normalizeAutomatonResult(data.dfa_result, 'dfa'),
    nfa: normalizeAutomatonResult(data.nfa_result, 'nfa'),
    regex: normalizeRegexResult(data.regex_result),
  };
}

function normalizeSimulationResponse(data) {
  return {
    ...data,
    isAccepted: data.accepted,
    finalState: data.final_states?.at(-1) || null,
    finalActiveStates: data.active_states || [],
    trace: normalizeTrace(data.trace, data.automaton_type),
  };
}

/**
 * Check backend health status
 * GET /api/health
 */
export async function getHealth() {
  return request('/api/health', { method: 'GET' });
}

/** Upload one PDF for local backend text extraction. */
export async function extractPdf(file) {
  const formData = new FormData();
  formData.append('file', file);
  return request('/api/pdf/extract', { method: 'POST', body: formData });
}

/**
 * Get all available automata definitions
 * GET /api/automata
 */
export async function getAutomata() {
  return request('/api/automata', { method: 'GET' });
}

/**
 * Get specific automaton details by ID
 * GET /api/automata/{automaton_id}
 */
export async function getAutomaton(automatonId) {
  return request(`/api/automata/${encodeURIComponent(automatonId)}`, { method: 'GET' });
}

/**
 * Construct an equivalent DFA from a configured epsilon-NFA.
 * GET /api/automata/{automaton_id}/convert-to-dfa
 */
export async function convertNfaToDfa(automatonId) {
  return request(
    `/api/automata/${encodeURIComponent(automatonId)}/convert-to-dfa`,
    { method: 'GET' }
  );
}

/**
 * Run email pattern analysis across selected engines
 * POST /api/analyze
 * @param {{ subject: string, body: string, mode: 'combined'|'dfa'|'nfa'|'regex' }} payload
 */
export async function analyzeEmail({ subject, body, mode = 'combined' }) {
  const data = await request('/api/analyze', {
    method: 'POST',
    body: JSON.stringify({
      subject: subject || '',
      body: body || '',
      mode: mode || 'combined'
    })
  });
  return normalizeAnalysisResponse(data);
}

/**
 * Run step-by-step automata simulation
 * POST /api/automata/{automaton_id}/simulate
 * @param {string} automatonId
 * @param {{ input: string|string[] }} payload UI input accepted for compatibility
 */
export async function simulateAutomaton(automatonId, { input }) {
  const inputText = Array.isArray(input) ? input.join(' ') : (input || '');
  const data = await request(`/api/automata/${encodeURIComponent(automatonId)}/simulate`, {
    method: 'POST',
    body: JSON.stringify({
      input_text: inputText
    })
  });
  return normalizeSimulationResponse(data);
}

/** Educational algorithms are explicit backend requests, never detector fallbacks. */
export function labRequest(operation,payload={}){
  return request(`/api/lab/${operation}`,{method:'POST',body:JSON.stringify(payload)});
}
