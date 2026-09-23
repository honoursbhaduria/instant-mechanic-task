'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import {
  History,
  Wrench,
  Calendar,
  Car,
  ArrowRight,
  ArrowLeft,
  Loader2,
  MessageSquare,
  Sparkles
} from 'lucide-react';
import { api, parseApiError, ApiError } from '@/lib/api';
import { Conversation, Diagnosis } from '@/lib/types';
import BookingModal from '@/components/BookingModal';
import ErrorAlert from '@/components/ErrorAlert';

export default function HistoryPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);

  // Selected diagnosis for booking
  const [selectedDiagnosis, setSelectedDiagnosis] = useState<Diagnosis | null>(null);
  const [isBookingOpen, setIsBookingOpen] = useState(false);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listConversations();
      setConversations(data);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleBookFromHistory = (diag: Diagnosis) => {
    setSelectedDiagnosis(diag);
    setIsBookingOpen(true);
  };

  return (
    <div className="min-h-screen bg-[#faf9f5] text-stone-900 font-sans relative flex flex-col overflow-x-hidden selection:bg-red-600 selection:text-white">
      {/* Background Subtle Tech Grid Layer matching landing page */}
      <div
        className="fixed inset-0 pointer-events-none bg-grid-subtle opacity-90 z-0"
        style={{
          maskImage: 'radial-gradient(ellipse 75% 65% at 50% 30%, #000 70%, transparent 100%)',
          WebkitMaskImage: 'radial-gradient(ellipse 75% 65% at 50% 30%, #000 70%, transparent 100%)'
        }}
      />

      {/* Floating Capsule Header matching landing and chat pages */}
      <header className="relative z-20 w-full max-w-5xl mx-auto pt-3 sm:pt-4 px-2 sm:px-4 shrink-0">
        <div className="rounded-full bg-white/85 backdrop-blur-md border border-stone-200/80 px-3 sm:px-5 py-2 sm:py-2.5 flex items-center justify-between shadow-xs">
          {/* Left: Back button + Brand Logo */}
          <div className="flex items-center gap-2 sm:gap-3.5 shrink-0">
            <Link
              href="/chat"
              className="flex items-center justify-center rounded-full p-1.5 text-stone-700 hover:bg-stone-100 hover:text-black transition-colors"
              title="Back to Diagnostics"
            >
              <ArrowLeft className="h-4 w-4" />
            </Link>

            <Link href="/" className="flex items-center transition-opacity hover:opacity-90 shrink-0">
              <div className="relative h-6 w-24 sm:w-28">
                <Image
                  src="/brand-logo.png"
                  alt="Instant Mechanic Logo"
                  fill
                  className="object-contain"
                  priority
                />
              </div>
            </Link>

            <div className="hidden sm:flex items-center gap-2 pl-3 border-l border-stone-200 text-xs font-mono">
              <History className="h-3.5 w-3.5 text-stone-500" />
              <span className="font-bold text-stone-900 iosevka-charon-bold">DIAGNOSIS HISTORY</span>
            </div>
          </div>

          {/* Right: New Consultation CTA */}
          <div className="flex items-center gap-2">
            <Link
              href="/chat"
              className="btn-metal-shine inline-flex items-center gap-1.5 rounded-full px-4 py-1.5 text-xs font-bold active:scale-95"
            >
              <Sparkles className="h-3.5 w-3.5 text-amber-400 relative z-10" />
              <span className="relative z-10">New Consultation</span>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="relative z-10 flex-1 w-full max-w-5xl mx-auto px-2 sm:px-4 py-6 sm:py-8 space-y-6">
        {/* Title area */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-2 pb-3 border-b border-stone-200/70">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-black iosevka-charon-bold tracking-tight">
              Diagnostic & Consultation Records
            </h1>
            <p className="text-xs text-stone-500 mt-1">
              Review past vehicle diagnoses, symptom assessments, and repair recommendations.
            </p>
          </div>
          {conversations.length > 0 && (
            <span className="text-xs font-mono text-stone-500">
              Total Sessions: <span className="font-bold text-black">{conversations.length}</span>
            </span>
          )}
        </div>

        {/* Loading State */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-stone-500">
            <Loader2 className="h-7 w-7 animate-spin text-red-600 mb-3" />
            <p className="text-xs font-mono">Loading consultation history...</p>
          </div>
        ) : conversations.length === 0 ? (
          /* Empty State */
          <div className="rounded-3xl border border-white/80 bg-white/75 backdrop-blur-md p-10 text-center max-w-md mx-auto space-y-4 shadow-xs">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-50 text-red-600 border border-red-100">
              <Wrench className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-black iosevka-charon-bold">No Consultations Yet</h3>
              <p className="text-xs text-stone-500 mt-1">
                You haven&apos;t run any vehicle diagnoses yet. Start a session to diagnose strange noises, engine codes, or breakdown issues.
              </p>
            </div>
            <Link
              href="/chat"
              className="btn-metal-shine inline-flex items-center gap-2 rounded-full px-5 py-2 text-xs font-bold active:scale-95 mx-auto"
            >
              <span className="relative z-10">Start Vehicle Diagnosis</span>
              <ArrowRight className="h-3.5 w-3.5 relative z-10" />
            </Link>
          </div>
        ) : (
          /* Conversation Sessions List */
          <div className="space-y-4">
            {conversations.map((conv) => {
              const hasDiagnoses = conv.diagnoses && conv.diagnoses.length > 0;
              const messageCount = conv.messages?.length || 0;

              return (
                <div
                  key={conv.id}
                  className="rounded-2xl border border-stone-200/80 bg-white/80 backdrop-blur-md overflow-hidden transition-colors hover:border-stone-400/80 shadow-2xs"
                >
                  {/* Card Header Strip */}
                  <div className="flex flex-wrap items-center justify-between gap-3 border-b border-stone-200/70 bg-stone-50/70 px-4 sm:px-6 py-3">
                    <div className="flex items-center gap-3">
                      <span className="font-mono text-xs font-bold text-black iosevka-charon-bold">
                        Session #{conv.id}
                      </span>
                      {conv.vehicle_info && (
                        <span className="inline-flex items-center gap-1.5 rounded-full bg-white border border-stone-200 px-2.5 py-0.5 text-xs font-mono font-medium text-stone-800">
                          <Car className="h-3 w-3 text-red-600" />
                          <span>{conv.vehicle_info}</span>
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-3 text-xs font-mono text-stone-500">
                      <span className="flex items-center gap-1">
                        <MessageSquare className="h-3.5 w-3.5 text-stone-400" />
                        <span>{messageCount} {messageCount === 1 ? 'msg' : 'msgs'}</span>
                      </span>
                      <span>•</span>
                      <span>{new Date(conv.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>

                  {/* Card Body */}
                  <div className="p-4 sm:p-6 space-y-4">
                    {hasDiagnoses ? (
                      <div className="space-y-3">
                        <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-stone-500 block">
                          Diagnostic Reports ({conv.diagnoses.length})
                        </span>
                        <div className="space-y-2.5">
                          {conv.diagnoses.map((diag) => (
                            <div
                              key={diag.id}
                              className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-xl border border-stone-200 bg-white p-4"
                            >
                              <div className="space-y-1 max-w-2xl">
                                <div className="flex items-center gap-2 flex-wrap">
                                  <h4 className="text-sm font-bold text-stone-900 iosevka-charon-bold">
                                    {diag.diagnosis}
                                  </h4>
                                  <span
                                    className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border ${
                                      diag.severity === 'high'
                                        ? 'bg-red-50 text-red-700 border-red-200'
                                        : diag.severity === 'low'
                                        ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                                        : 'bg-amber-50 text-amber-800 border-amber-200'
                                    }`}
                                  >
                                    {diag.severity.toUpperCase()} PRIORITY
                                  </span>
                                </div>
                                <p className="text-xs text-stone-700">
                                  <span className="font-semibold text-stone-900">Recommended Service:</span> {diag.service}
                                </p>
                                {diag.reasoning && (
                                  <p className="text-xs text-stone-500 line-clamp-2">
                                    {diag.reasoning}
                                  </p>
                                )}
                              </div>

                              <button
                                onClick={() => handleBookFromHistory(diag)}
                                className="btn-metal-shine inline-flex shrink-0 items-center justify-center gap-1.5 rounded-full px-4 py-2 text-xs font-bold active:scale-95"
                              >
                                <Calendar className="h-3.5 w-3.5 text-amber-400 relative z-10" />
                                <span className="relative z-10">Book Mechanic</span>
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <p className="text-xs text-stone-500 italic">
                        Consultation session was preliminary without a formal diagnostic assessment report.
                      </p>
                    )}

                    {/* Recent Message preview */}
                    {conv.messages && conv.messages.length > 0 && (
                      <div className="border-t border-stone-100 pt-3">
                        <span className="text-[11px] font-mono font-semibold text-stone-400 block mb-0.5">
                          Last Message:
                        </span>
                        <p className="text-xs text-stone-700 truncate">
                          &quot;{conv.messages[conv.messages.length - 1].content}&quot;
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </main>

      {/* Booking Modal */}
      <BookingModal
        diagnosis={selectedDiagnosis}
        isOpen={isBookingOpen}
        onClose={() => setIsBookingOpen(false)}
      />

      {/* Error alert */}
      <ErrorAlert
        error={error}
        onDismiss={() => setError(null)}
        onRetry={fetchHistory}
      />
    </div>
  );
}
