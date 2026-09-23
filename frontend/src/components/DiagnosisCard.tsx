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
          bg: 'bg-rose-50 text-rose-700 border-rose-200',
          badgeBg: 'bg-red-600 text-white',
          icon: ShieldAlert,
          label: 'HIGH SEVERITY',
        };
      case 'low':
        return {
          bg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
          badgeBg: 'bg-emerald-600 text-white',
          icon: CheckCircle2,
          label: 'LOW SEVERITY',
        };
      case 'medium':
      default:
        return {
          bg: 'bg-amber-50 text-amber-900 border-amber-200',
          badgeBg: 'bg-amber-500 text-stone-950 font-bold',
          icon: AlertTriangle,
          label: 'MODERATE SEVERITY',
        };
    }
  };

  const config = getSeverityConfig(diagnosis.severity);
  const SeverityIcon = config.icon;

  return (
    <div className="my-4 overflow-hidden rounded-2xl border border-white/80 bg-white/90 backdrop-blur-md shadow-xs transition-all max-w-[95%] sm:max-w-[85%] mx-auto text-left">
      {/* Header bar */}
      <div className="flex items-center justify-between border-b border-stone-200/80 bg-stone-100/70 px-4 sm:px-5 py-3">
        <div className="flex items-center gap-2.5">
          <div className="rounded-xl bg-white border border-stone-200 p-2 text-stone-900 shadow-xs">
            <Wrench className="h-4 w-4 text-red-600" />
          </div>
          <div>
            <h3 className="text-xs sm:text-sm font-bold tracking-tight text-stone-900 iosevka-charon-bold">
              Automotive Diagnostic Report
            </h3>
            {diagnosis.vehicle && (
              <p className="text-[11px] font-mono font-bold text-stone-600">Vehicle: {diagnosis.vehicle}</p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[10px] font-mono font-bold ${config.badgeBg}`}>
            <SeverityIcon className="h-3 w-3" />
            <span>{config.label}</span>
          </span>
        </div>
      </div>

      <div className="space-y-3.5 p-4 sm:p-5">
        {/* Possible Issue */}
        <div>
          <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-stone-500">
            Identified Issue
          </span>
          <p className="mt-0.5 text-base sm:text-lg font-black text-stone-950 iosevka-charon-bold">
            {diagnosis.diagnosis}
          </p>
        </div>

        {/* Reasoning */}
        {diagnosis.reasoning && (
          <div className="rounded-xl bg-stone-50/80 p-3.5 border border-stone-200">
            <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-stone-600">
              Technical Analysis & Telemetry
            </span>
            <p className="mt-1 text-xs text-stone-800 leading-relaxed font-medium">
              {diagnosis.reasoning}
            </p>
          </div>
        )}

        {/* Recommended Service */}
        <div className="rounded-xl border border-stone-200 bg-white p-3.5 shadow-xs">
          <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-red-600">
            Recommended Repair / Service
          </span>
          <p className="mt-0.5 text-xs sm:text-sm font-bold text-stone-900">
            {diagnosis.service || diagnosis.recommendation}
          </p>
        </div>

        {/* Safety Warning */}
        {diagnosis.safety_warning && (
          <div className="flex items-start gap-2 rounded-xl border border-red-200 bg-red-50/80 p-3 text-xs text-red-900">
            <AlertTriangle className="h-4 w-4 shrink-0 text-red-600 mt-0.5" />
            <p className="leading-snug font-medium">{diagnosis.safety_warning}</p>
          </div>
        )}

        {/* Action Button: Shining Metal Effect */}
        <div className="pt-2">
          <button
            onClick={() => onBookMechanic(diagnosis)}
            className="btn-metal-shine flex w-full items-center justify-center gap-2 rounded-xl px-5 py-3 text-xs sm:text-sm font-bold active:scale-[0.99] shadow-sm"
          >
            <Calendar className="h-4 w-4 text-amber-400 relative z-10" />
            <span className="relative z-10">Dispatch Verified Mechanic for This Service</span>
            <ArrowRight className="h-4 w-4 ml-1 text-stone-300 relative z-10" />
          </button>
        </div>
      </div>
    </div>
  );
}
