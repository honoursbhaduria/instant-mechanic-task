'use client';

import React from 'react';
import { HelpCircle, CheckCircle2, Sparkles } from 'lucide-react';

interface DiagnosticProgressProps {
  answered: number;
  total: number;
  percentage: number;
  status: 'planning' | 'collecting_answers' | 'ready_for_assessment' | 'assessing' | 'completed' | 'failed' | string;
  vehicleInfo?: string;
}

export default function DiagnosticProgress({
  answered,
  total,
  percentage,
  status,
  vehicleInfo
}: DiagnosticProgressProps) {
  const isReady = status === 'ready_for_assessment';
  const isCompleted = status === 'completed';
  const isAssessing = status === 'assessing';

  return (
    <div className="rounded-2xl border border-stone-200/90 bg-white/95 p-3.5 sm:p-4 shadow-2xs backdrop-blur-sm">
      <div className="flex items-center justify-between mb-2.5 border-b border-stone-100 pb-2">
        <div className="flex items-center gap-2">
          <span className={`inline-block h-2 w-2 rounded-full ${
            isCompleted
              ? 'bg-emerald-600'
              : isReady
              ? 'bg-amber-500 animate-pulse'
              : 'bg-red-600 animate-pulse'
          }`} />
          <h4 className="text-[11px] font-mono font-bold tracking-wider text-stone-900 uppercase">
            Diagnostic Interview Progress
          </h4>
          {vehicleInfo && (
            <span className="hidden sm:inline-block text-[11px] font-medium text-stone-500 truncate max-w-xs">
              • {vehicleInfo}
            </span>
          )}
        </div>
        <span className="text-[11px] font-mono font-semibold text-stone-600">
          {total > 0 ? (
            isCompleted
              ? 'Assessment Finalized'
              : isReady
              ? 'All Questions Answered (100%)'
              : `Question ${answered + 1} of ${total} (${percentage}%)`
          ) : (
            'Analyzing Incident...'
          )}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-stone-100 rounded-full h-1.5 mb-2.5 overflow-hidden">
        <div
          className={`h-1.5 rounded-full transition-all duration-500 ease-out ${
            isCompleted
              ? 'bg-emerald-600'
              : isReady
              ? 'bg-amber-500'
              : 'bg-red-600'
          }`}
          style={{ width: `${Math.max(percentage, total > 0 ? 5 : 0)}%` }}
        />
      </div>

      {/* Status banner */}
      <div className="flex items-center justify-between text-xs text-stone-600">
        <div className="flex items-center gap-1.5">
          {isCompleted ? (
            <>
              <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
              <span className="text-[11px] font-medium text-emerald-800">
                Precision diagnostic assessment completed. View report and recommendations below.
              </span>
            </>
          ) : isAssessing ? (
            <>
              <Sparkles className="h-3.5 w-3.5 text-amber-500 animate-spin shrink-0" />
              <span className="text-[11px] font-medium text-amber-800">
                Synthesizing diagnostic assessment from incident transcript...
              </span>
            </>
          ) : isReady ? (
            <>
              <CheckCircle2 className="h-3.5 w-3.5 text-amber-600 shrink-0" />
              <span className="text-[11px] font-medium text-amber-900 font-semibold">
                Sufficient evidence collected. Ready to generate comprehensive diagnosis.
              </span>
            </>
          ) : (
            <>
              <HelpCircle className="h-3.5 w-3.5 text-stone-400 shrink-0" />
              <span className="text-[11px] text-stone-600">
                Gathering case-specific evidence: Answer each targeted question to diagnose your vehicle.
              </span>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
