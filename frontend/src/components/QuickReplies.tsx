'use client';

import React from 'react';
import { Sparkles, CornerDownLeft } from 'lucide-react';

interface QuickRepliesProps {
  replies: string[];
  onSelect: (reply: string) => void;
  disabled?: boolean;
}

export default function QuickReplies({
  replies,
  onSelect,
  disabled = false,
}: QuickRepliesProps) {
  if (!replies || replies.length === 0) return null;

  return (
    <div className="flex flex-wrap items-center gap-1.5 pt-1.5 pb-1 px-1">
      <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-stone-600 flex items-center gap-1 mr-1">
        <Sparkles className="h-3 w-3 text-amber-500" />
        Quick Reply:
      </span>
      {replies.map((reply, idx) => {
        const isRunDiagnosis = reply.toLowerCase().includes('run diagnosis');
        return (
          <button
            key={idx}
            type="button"
            disabled={disabled}
            onClick={() => onSelect(reply)}
            className={`group inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold transition-all active:scale-95 disabled:opacity-50 ${
              isRunDiagnosis
                ? 'bg-red-600 text-white hover:bg-red-700 shadow-sm border border-red-600'
                : 'bg-white/90 text-stone-800 border border-stone-300 hover:border-stone-900 hover:bg-stone-50 shadow-2xs'
            }`}
          >
            <span>{reply}</span>
            <CornerDownLeft className="h-3 w-3 opacity-40 group-hover:opacity-100 transition-opacity" />
          </button>
        );
      })}
    </div>
  );
}
