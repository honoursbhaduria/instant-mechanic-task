'use client';

import React from 'react';
import { Wrench, AlertTriangle, ShieldAlert, CheckCircle2, Calendar, ArrowRight } from 'lucide-react';
import { Diagnosis } from '@/lib/types';

interface DiagnosisCardProps {
  diagnosis: Diagnosis;
  onBookMechanic: (diagnosis: Diagnosis) => void;
}

export default function DiagnosisCard({ diagnosis, onBookMechanic }: DiagnosisCardProps) {
  const getSeverityConfig = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'high':
        return {
          bg: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
          badgeBg: 'bg-rose-500 text-white',
          icon: ShieldAlert,
          label: 'HIGH SEVERITY',
        };
      case 'low':
        return {
          bg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
          badgeBg: 'bg-emerald-500 text-white',
          icon: CheckCircle2,
          label: 'LOW SEVERITY',
        };
      case 'medium':
      default:
        return {
          bg: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
          badgeBg: 'bg-amber-500 text-neutral-950 font-bold',
          icon: AlertTriangle,
          label: 'MEDIUM SEVERITY',
        };
    }
  };

  const config = getSeverityConfig(diagnosis.severity);
  const SeverityIcon = config.icon;

  return (
    <div className="my-4 overflow-hidden rounded-2xl border border-neutral-700 bg-neutral-900 shadow-2xl transition-all">
      {/* Header bar */}
      <div className="flex items-center justify-between border-b border-neutral-800 bg-neutral-950/60 px-5 py-3.5">
        <div className="flex items-center gap-2.5">
          <div className="rounded-lg bg-amber-500/20 p-1.5 text-amber-400">
            <Wrench className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-sm font-bold tracking-wide text-neutral-100">
              Diagnostic Assessment
            </h3>
            {diagnosis.vehicle && (
              <p className="text-xs text-neutral-400">Vehicle: {diagnosis.vehicle}</p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[11px] font-bold ${config.badgeBg}`}>
            <SeverityIcon className="h-3 w-3" />
            <span>{config.label}</span>
          </span>
        </div>
      </div>

      <div className="space-y-4 p-5">
        {/* Possible Issue */}
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-neutral-400">
            Possible Issue
          </span>
          <p className="mt-1 text-base font-bold text-white sm:text-lg">
            {diagnosis.diagnosis}
          </p>
        </div>

        {/* Reasoning */}
        {diagnosis.reasoning && (
          <div className="rounded-xl bg-neutral-950/50 p-3.5 border border-neutral-800/80">
            <span className="text-xs font-semibold uppercase tracking-wider text-neutral-400">
              Technical Reasoning
            </span>
            <p className="mt-1 text-xs text-neutral-300 leading-relaxed sm:text-sm">
              {diagnosis.reasoning}
            </p>
          </div>
        )}

        {/* Recommended Service */}
        <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-3.5">
          <span className="text-xs font-semibold uppercase tracking-wider text-amber-400">
            Recommended Service
          </span>
          <p className="mt-0.5 text-sm font-bold text-neutral-100 sm:text-base">
            {diagnosis.service || diagnosis.recommendation}
          </p>
        </div>

        {/* Safety Warning */}
        {diagnosis.safety_warning && (
          <div className="flex items-start gap-2.5 rounded-xl border border-rose-500/20 bg-rose-500/10 p-3 text-xs text-rose-300">
            <AlertTriangle className="h-4 w-4 shrink-0 text-rose-400 mt-0.5" />
            <p className="leading-snug">{diagnosis.safety_warning}</p>
          </div>
        )}

        {/* Action Button */}
        <div className="pt-2">
          <button
            onClick={() => onBookMechanic(diagnosis)}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 px-5 py-3 text-sm font-bold text-neutral-950 shadow-lg shadow-amber-500/20 transition-all hover:opacity-95 hover:shadow-amber-500/30 active:scale-[0.99]"
          >
            <Calendar className="h-4 w-4" />
            <span>Book Mechanic for This Service</span>
            <ArrowRight className="h-4 w-4 ml-1" />
          </button>
        </div>
      </div>
    </div>
  );
}
