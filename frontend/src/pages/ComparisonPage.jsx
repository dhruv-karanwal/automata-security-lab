import React, { useState } from 'react';
import { Play, AlertCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { analyzeEmail } from '../services/api.js';
import { runIllustrativeAnalysis } from '../utils/illustrativeEngine.js';
import ExecutionTraceView from '../components/ExecutionTraceView.jsx';

export default function ComparisonPage({ isConnected }) {
  const [inputText, setInputText] = useState('WIN PRIZE NOW');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [backendError, setBackendError] = useState(null);
  const [isOfflineDemo, setIsOfflineDemo] = useState(false);
  const [showDfaTrace, setShowDfaTrace] = useState(false);
  const [showNfaTrace, setShowNfaTrace] = useState(false);

  const presets = [
    { label: 'WIN PRIZE NOW', text: 'WIN PRIZE NOW' },
    { label: 'CLAIM REWARD NOW', text: 'CLAIM REWARD NOW' },
    { label: 'ACCOUNT VERIFY IMMEDIATELY', text: 'ACCOUNT VERIFY IMMEDIATELY' },
    { label: 'WIN PRIZE NOW EXTRA', text: 'WIN PRIZE NOW EXTRA' },
    { label: 'https://example.com/login!!!', text: 'https://example.com/login!!!' }
  ];

  const handleCompare = async (e) => {
    if (e) e.preventDefault();
    if (!inputText.trim()) {
      alert('Please enter an input string to compare.');
      return;
    }

    setIsLoading(true);
    setBackendError(null);
    setIsOfflineDemo(false);

    try {
      // Calls real backend with mode: combined
      const data = await analyzeEmail({ subject: '', body: inputText, mode: 'combined' });
      setResult(data);
    } catch (err) {
      console.warn('Backend compare failed:', err);
      setBackendError(err);
      setResult(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRunOfflineCompare = () => {
    setIsLoading(true);
    setBackendError(null);
    setTimeout(() => {
      const data = runIllustrativeAnalysis('', inputText, 'combined');
      setResult(data);
      setIsOfflineDemo(true);
      setIsLoading(false);
    }, 200);
  };

  return (
    <div className="space-y-5 max-w-4xl">
      {/* Page Title & Subtitle */}
      <div>
        <h1 className="text-xl font-bold text-[#243247]">Detector Comparison</h1>
        <p className="text-xs text-[#68778B] mt-0.5">
          Compare how DFA, NFA, and Regex process the same input.
        </p>
      </div>

      {/* Input Field & Compare Button */}
      <div className="bg-white rounded-lg border border-[#E1E6ED] p-4 space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <label htmlFor="compare-input" className="text-xs font-semibold text-[#243247]">
            Input text to test across all three detectors:
          </label>
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-[11px] text-[#68778B]">Test strings:</span>
            {presets.map((p) => (
              <button
                key={p.label}
                type="button"
                onClick={() => {
                  setInputText(p.text);
                  setResult(null);
                  setBackendError(null);
                }}
                className="px-2 py-0.5 rounded border border-[#E1E6ED] bg-slate-50 hover:bg-slate-100 text-[11px] text-slate-700 font-mono"
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-2">
          <input
            id="compare-input"
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="e.g. WIN PRIZE NOW"
            className="flex-1 text-xs font-mono px-3 py-2 rounded border border-[#E1E6ED] focus:outline-none focus:border-[#168C83]"
          />
          <button
            type="button"
            onClick={handleCompare}
            disabled={isLoading}
            className="px-4 py-2 rounded text-xs font-bold bg-[#168C83] text-white hover:bg-[#12726a] disabled:opacity-50 flex items-center justify-center gap-1.5 cursor-pointer"
          >
            <Play className="w-3.5 h-3.5 fill-white" />
            <span>{isLoading ? 'Comparing...' : 'Compare'}</span>
          </button>
        </div>
      </div>

      {/* Backend Offline Error Message */}
      {backendError && (
        <div className="bg-white rounded-lg border border-rose-200 p-4 text-xs space-y-2">
          <div className="flex items-center gap-2 text-rose-700 font-bold">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>Backend Comparison Unavailable</span>
          </div>
          <p className="text-slate-700 leading-relaxed">
            {backendError.message}
          </p>
          {backendError.isConnectionRefused && (
            <div className="pt-2 border-t border-rose-100 flex items-center justify-between flex-wrap gap-2">
              <span className="text-[11px] text-[#68778B]">
                Tip: You can start FastAPI, or run the comparison with local student logic for viva demo.
              </span>
              <button
                onClick={handleRunOfflineCompare}
                className="px-2.5 py-1 text-xs font-semibold rounded bg-[#168C83] text-white hover:bg-[#12726a]"
              >
                Compare with Local Logic
              </button>
            </div>
          )}
        </div>
      )}

      {/* Comparison Results Table */}
      {result && (
        <div className="bg-white rounded-lg border border-[#E1E6ED] p-5 space-y-4">
          {isOfflineDemo && (
            <div className="px-3 py-1 rounded bg-amber-50 border border-amber-200 text-amber-900 text-[11px]">
              <strong>[Demo Mode]</strong> Compared using local student rules (backend offline).
            </div>
          )}

          <div className="overflow-x-auto border border-[#E1E6ED] rounded">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-slate-50 border-b border-[#E1E6ED] text-[#68778B] font-semibold">
                  <th className="py-2.5 px-3 w-32">Detector</th>
                  <th className="py-2.5 px-3 w-64">What it recognizes</th>
                  <th className="py-2.5 px-3 w-28">Result</th>
                  <th className="py-2.5 px-3">Explanation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#E1E6ED]">
                {/* DFA Row */}
                <tr className="hover:bg-slate-50/50">
                  <td className="py-3 px-3 font-bold text-[#243247]">DFA</td>
                  <td className="py-3 px-3 font-mono text-[11px] text-slate-700">
                    Exactly: WIN PRIZE NOW
                  </td>
                  <td className="py-3 px-3">
                    {result.dfa?.isAccepted ? (
                      <span className="font-bold text-emerald-700">Accepted</span>
                    ) : (
                      <span className="font-medium text-rose-700">Rejected</span>
                    )}
                  </td>
                  <td className="py-3 px-3 text-slate-600 leading-relaxed">
                    {result.dfa?.explanation}
                  </td>
                </tr>

                {/* NFA Row */}
                <tr className="hover:bg-slate-50/50">
                  <td className="py-3 px-3 font-bold text-[#243247]">NFA</td>
                  <td className="py-3 px-3 font-mono text-[11px] text-slate-700">
                    3 branches: WIN PRIZE NOW, CLAIM REWARD NOW, ACCOUNT VERIFY IMMEDIATELY
                  </td>
                  <td className="py-3 px-3">
                    {result.nfa?.isAccepted ? (
                      <span className="font-bold text-emerald-700">Accepted</span>
                    ) : (
                      <span className="font-medium text-rose-700">Rejected</span>
                    )}
                  </td>
                  <td className="py-3 px-3 text-slate-600 leading-relaxed">
                    {result.nfa?.explanation}
                  </td>
                </tr>

                {/* Regex Row */}
                <tr className="hover:bg-slate-50/50">
                  <td className="py-3 px-3 font-bold text-[#243247]">Regex</td>
                  <td className="py-3 px-3 text-[11px] text-slate-700">
                    Configured rules (URLs, emails, phrases, exclamation marks)
                  </td>
                  <td className="py-3 px-3">
                    {result.regex?.hasMatches ? (
                      <span className="font-bold text-amber-700">
                        {result.regex.matchCount} matched
                      </span>
                    ) : (
                      <span className="text-slate-500">No match</span>
                    )}
                  </td>
                  <td className="py-3 px-3 text-slate-600 leading-relaxed">
                    {result.regex?.summary}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Expandable Traces */}
          <div className="pt-2 border-t border-[#E1E6ED] space-y-3">
            <div className="flex items-center gap-4 text-xs">
              {result.dfa && (
                <button
                  type="button"
                  onClick={() => setShowDfaTrace(!showDfaTrace)}
                  className="text-[#168C83] hover:underline font-semibold flex items-center gap-1"
                >
                  <span>{showDfaTrace ? 'Hide DFA trace' : 'View DFA trace'}</span>
                  {showDfaTrace ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                </button>
              )}

              {result.nfa && (
                <button
                  type="button"
                  onClick={() => setShowNfaTrace(!showNfaTrace)}
                  className="text-[#3B78C8] hover:underline font-semibold flex items-center gap-1"
                >
                  <span>{showNfaTrace ? 'Hide NFA trace' : 'View NFA trace'}</span>
                  {showNfaTrace ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                </button>
              )}
            </div>

            {showDfaTrace && result.dfa && (
              <ExecutionTraceView
                trace={result.dfa.trace}
                isAccepted={result.dfa.isAccepted}
                title="DFA Trace Table"
              />
            )}

            {showNfaTrace && result.nfa && (
              <ExecutionTraceView
                trace={result.nfa.trace}
                isAccepted={result.nfa.isAccepted}
                title="NFA Trace Table"
              />
            )}
          </div>
        </div>
      )}

      {/* Mandatory Viva Explanation Note */}
      <div className="p-4 bg-slate-50 rounded-lg border border-[#E1E6ED] text-xs text-slate-700 space-y-1.5 leading-relaxed">
        <div className="font-bold text-[#243247]">Important Theoretical Note:</div>
        <p>
          DFA and NFA have the same expressive power when recognizing the same regular language. In this project, their configured languages differ, and the regex engine uses separate rules. Therefore, their results may differ.
        </p>
      </div>
    </div>
  );
}
