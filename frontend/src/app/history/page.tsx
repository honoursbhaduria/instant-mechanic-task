'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { History, Wrench, Calendar, Car, ArrowRight, Loader2, MessageSquare } from 'lucide-react';
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
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-neutral-800 pb-5">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-amber-400">
            <History className="h-4 w-4" />
            <span>Audit & Diagnosis Trail</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white sm:text-3xl mt-1">
            Diagnostic & Conversation History
          </h1>
          <p className="text-sm text-neutral-400">
            View all past vehicle consultations, diagnostic assessments, and recommendations.
          </p>
        </div>

        <Link
          href="/chat"
          className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 px-4 py-2.5 text-xs font-bold text-neutral-950 shadow-md transition-transform hover:scale-105 active:scale-95"
        >
          <Wrench className="h-4 w-4" />
          <span>Start New Consultation</span>
        </Link>
      </div>

      {/* Content */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 text-neutral-400">
          <Loader2 className="h-8 w-8 animate-spin text-amber-500 mb-3" />
          <p className="text-sm">Loading consultation history...</p>
        </div>
      ) : conversations.length === 0 ? (
        <div className="rounded-2xl border border-neutral-800 bg-neutral-900/40 p-12 text-center max-w-md mx-auto space-y-4">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-amber-500/10 text-amber-400">
            <Wrench className="h-7 w-7" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">No Consultations Yet</h3>
            <p className="text-xs text-neutral-400 mt-1">
              You haven&apos;t run any vehicle diagnoses yet. Start a chat with the AI Mechanic to get an assessment!
            </p>
          </div>
          <Link
            href="/chat"
            className="inline-flex items-center gap-2 rounded-xl bg-amber-500 px-4 py-2 text-xs font-bold text-neutral-950 shadow-md hover:bg-amber-400"
          >
            <span>Diagnose Your Car</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
      ) : (
        <div className="space-y-6">
          {conversations.map((conv) => {
            const hasDiagnoses = conv.diagnoses && conv.diagnoses.length > 0;
            const messageCount = conv.messages?.length || 0;

            return (
              <div
                key={conv.id}
                className="overflow-hidden rounded-2xl border border-neutral-800 bg-neutral-900/60 shadow-lg transition-all hover:border-neutral-700"
              >
                {/* Conversation Header */}
                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-neutral-800/80 bg-neutral-950/60 px-5 py-3">
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs font-bold text-amber-400">
                      Session #{conv.id}
                    </span>
                    {conv.vehicle_info && (
                      <span className="flex items-center gap-1 rounded bg-neutral-800 px-2 py-0.5 text-xs font-semibold text-neutral-200">
                        <Car className="h-3 w-3 text-amber-400" />
                        {conv.vehicle_info}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-3 text-xs text-neutral-400">
                    <span className="flex items-center gap-1">
                      <MessageSquare className="h-3.5 w-3.5" />
                      {messageCount} {messageCount === 1 ? 'message' : 'messages'}
                    </span>
                    <span>•</span>
                    <span>{new Date(conv.created_at).toLocaleDateString()}</span>
                  </div>
                </div>

                {/* Conversation Details & Diagnoses */}
                <div className="p-5 space-y-4">
                  {/* Diagnoses cards */}
                  {hasDiagnoses ? (
                    <div className="space-y-3">
                      <span className="text-[11px] font-bold uppercase tracking-wider text-amber-400">
                        Diagnostic Assessment(s):
                      </span>
                      {conv.diagnoses.map((diag) => (
                        <div
                          key={diag.id}
                          className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 rounded-xl border border-neutral-800 bg-neutral-950/60 p-4"
                        >
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <h4 className="text-sm font-bold text-white">
                                {diag.diagnosis}
                              </h4>
                              <span
                                className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                                  diag.severity === 'high'
                                    ? 'bg-rose-500/20 text-rose-300'
                                    : diag.severity === 'low'
                                    ? 'bg-emerald-500/20 text-emerald-300'
                                    : 'bg-amber-500/20 text-amber-300'
                                }`}
                              >
                                {diag.severity.toUpperCase()}
                              </span>
                            </div>
                            <p className="text-xs text-neutral-300">
                              <span className="text-neutral-500">Recommended:</span> {diag.service}
                            </p>
                            {diag.reasoning && (
                              <p className="text-xs text-neutral-400 line-clamp-2">
                                {diag.reasoning}
                              </p>
                            )}
                          </div>

                          <button
                            onClick={() => handleBookFromHistory(diag)}
                            className="flex shrink-0 items-center justify-center gap-1.5 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 px-4 py-2 text-xs font-bold text-neutral-950 shadow-md transition-transform hover:scale-105 active:scale-95"
                          >
                            <Calendar className="h-3.5 w-3.5" />
                            <span>Book Mechanic</span>
                          </button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-xs text-neutral-400 italic">
                      Consultation was ongoing or preliminary without a final diagnostic report.
                    </p>
                  )}

                  {/* Recent Message preview */}
                  {conv.messages && conv.messages.length > 0 && (
                    <div className="border-t border-neutral-800/60 pt-3">
                      <span className="text-[11px] font-semibold text-neutral-500">Last Message:</span>
                      <p className="text-xs text-neutral-300 truncate mt-0.5">
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
