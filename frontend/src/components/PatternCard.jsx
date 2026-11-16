import React, { useState } from 'react';
import { Copy, Check, AlertTriangle, ShieldCheck, Tag, Info } from 'lucide-react';

/**
 * Reusable Pattern Card representing a regex or threat rule definition
 */
export default function PatternCard({ pattern }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(pattern.regex);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getCategoryBadgeClass = (category) => {
    switch (category) {
      case 'url':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'email':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'phrase':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      case 'punctuation':
        return 'bg-rose-100 text-rose-800 border-rose-200';
      case 'suspicious_url':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      default:
        return 'bg-slate-100 text-slate-800 border-slate-200';
    }
  };

  return (
    <div className="bg-white rounded-xl border border-[#E2E8F0] shadow-sm hover:shadow transition-shadow overflow-hidden flex flex-col justify-between">
      {/* Header */}
      <div className="p-5 border-b border-[#E2E8F0]/70">
        <div className="flex items-center justify-between gap-2 mb-2">
          <span className="font-mono text-xs font-bold text-[#0F9D91] bg-[#0F9D91]/10 px-2 py-0.5 rounded">
            {pattern.id}
          </span>
          <span className={`text-[11px] font-semibold px-2 py-0.5 rounded border ${getCategoryBadgeClass(pattern.category)}`}>
            {pattern.categoryLabel || pattern.category}
          </span>
        </div>
        <h3 className="text-base font-bold text-[#172B4D] leading-snug">
          {pattern.name}
        </h3>
        <p className="text-xs text-slate-600 mt-2 leading-relaxed">
          {pattern.description}
        </p>
      </div>

      {/* Regex Code Block */}
      <div className="px-5 py-3 bg-slate-50 border-b border-[#E2E8F0]">
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
            Regular Expression
          </span>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 text-[11px] font-medium text-slate-600 hover:text-[#0F9D91] transition-colors"
            title="Copy regex"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-600" />
                <span className="text-emerald-600 font-semibold">Copied</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>
        <div className="bg-[#172B4D] text-emerald-400 p-2.5 rounded-lg font-mono text-xs overflow-x-auto selection:bg-emerald-800">
          <code>{pattern.regex}</code>
        </div>
      </div>

      {/* Examples & Relevance */}
      <div className="p-5 space-y-3 text-xs">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <div className="p-2.5 bg-emerald-50/60 rounded-lg border border-emerald-100">
            <span className="font-semibold text-emerald-800 block mb-1">Example Match:</span>
            <code className="font-mono text-[11px] text-emerald-900 break-all">{pattern.exampleMatch}</code>
          </div>
          <div className="p-2.5 bg-slate-100/70 rounded-lg border border-slate-200">
            <span className="font-semibold text-slate-700 block mb-1">Example Nonmatch:</span>
            <code className="font-mono text-[11px] text-slate-700 break-all">{pattern.exampleNonMatch}</code>
          </div>
        </div>

        <div className="pt-2">
          <div className="flex items-start gap-1.5 text-slate-700">
            <Info className="w-4 h-4 text-[#3578E5] shrink-0 mt-0.5" />
            <div>
              <strong className="text-slate-900">Security Relevance: </strong>
              <span>{pattern.relevance}</span>
            </div>
          </div>
        </div>

        <div className="p-2.5 bg-amber-50/70 rounded-lg border border-amber-200/70 text-amber-900 flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
          <div>
            <strong className="font-semibold text-amber-950">Limitations & False Positives: </strong>
            <span className="text-amber-900/90 leading-relaxed">{pattern.limitations}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
