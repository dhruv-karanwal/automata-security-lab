import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import { PATTERNS_DATA } from '../data/patternsData.js';

export default function PatternExplorerPage() {
  const [copiedId, setCopiedId] = useState(null);

  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 1500);
  };

  return (
    <div className="space-y-5 max-w-5xl">
      {/* Title & Subtitle */}
      <div>
        <h1 className="text-xl font-bold text-[#243247]">Pattern Explorer</h1>
        <p className="text-xs text-[#68778B] mt-0.5">
          Configured regular expression rules for email threats.
        </p>
      </div>

      {/* Clean Table / List of Rules */}
      <div className="bg-white rounded-lg border border-[#E1E6ED] overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-50 border-b border-[#E1E6ED] text-[#68778B] font-semibold">
                <th className="py-2.5 px-3 w-48">Rule Name</th>
                <th className="py-2.5 px-3 w-56">Regex Expression</th>
                <th className="py-2.5 px-3">What It Detects</th>
                <th className="py-2.5 px-3">Matching Example</th>
                <th className="py-2.5 px-3">Limitation / False Positive</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E1E6ED]">
              {PATTERNS_DATA.map((rule) => (
                <tr key={rule.id} className="hover:bg-slate-50/50">
                  <td className="py-3 px-3 align-top font-bold text-[#243247]">
                    {rule.name}
                  </td>
                  <td className="py-3 px-3 align-top font-mono">
                    <div className="bg-slate-50 p-1.5 rounded border border-[#E1E6ED] text-[#168C83] break-all relative group">
                      <code>{rule.regex}</code>
                      <button
                        onClick={() => handleCopy(rule.id, rule.regex)}
                        className="ml-1 text-[10px] text-slate-400 hover:text-slate-700 underline inline-block"
                        title="Copy regex"
                      >
                        {copiedId === rule.id ? 'Copied' : 'Copy'}
                      </button>
                    </div>
                  </td>
                  <td className="py-3 px-3 align-top text-slate-700 leading-relaxed">
                    {rule.detects}
                  </td>
                  <td className="py-3 px-3 align-top font-mono text-[11px] text-slate-800 break-all">
                    <span className="bg-emerald-50 text-emerald-800 px-1.5 py-0.5 rounded border border-emerald-200 inline-block">
                      {rule.exampleMatch}
                    </span>
                  </td>
                  <td className="py-3 px-3 align-top text-[#68778B] text-[11px] leading-relaxed">
                    {rule.limitation}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Viva Note */}
      <div className="p-3 bg-slate-50 rounded-lg border border-[#E1E6ED] text-xs text-[#68778B]">
        <strong>Viva explanation note:</strong> Regular expressions here perform substring scanning across email content. Unlike finite automata which read whole token sequences from start to finish, regular expressions match local substrings anywhere within message headers and body text.
      </div>
    </div>
  );
}
