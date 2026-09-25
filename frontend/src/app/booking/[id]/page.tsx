'use client';

import React, { useEffect, useState, useCallback } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useParams } from 'next/navigation';
import {
  CheckCircle2,
  Calendar,
  Clock,
  Car,
  User,
  Phone,
  Wrench,
  ArrowLeft,
  Loader2,
  AlertTriangle,
  Printer
} from 'lucide-react';
import { api, parseApiError, ApiError } from '@/lib/api';
import { Booking } from '@/lib/types';
import ErrorAlert from '@/components/ErrorAlert';

export default function BookingDetailPage() {
  const params = useParams();
  const id = params?.id as string;

  const [booking, setBooking] = useState<Booking | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);

  const fetchBookingDetails = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getBooking(id);
      setBooking(data);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    if (id) {
      fetchBookingDetails();
    }
  }, [id, fetchBookingDetails]);

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="min-h-screen bg-[#faf9f5] text-stone-900 font-sans relative flex flex-col overflow-x-clip selection:bg-red-600 selection:text-white">
      {/* Background Subtle Tech Grid matching landing page */}
      <div
        className="fixed inset-0 pointer-events-none bg-grid-subtle opacity-90 z-0"
        style={{
          maskImage: 'radial-gradient(ellipse 75% 65% at 50% 30%, #000 70%, transparent 100%)',
          WebkitMaskImage: 'radial-gradient(ellipse 75% 65% at 50% 30%, #000 70%, transparent 100%)'
        }}
      />

      {/* Floating Capsule Header */}
      <header className="relative z-20 w-full max-w-3xl mx-auto pt-3 sm:pt-4 px-2 sm:px-4 shrink-0">
        <div className="rounded-full bg-white/85 backdrop-blur-md border border-stone-200/80 px-3 sm:px-5 py-2 sm:py-2.5 flex items-center justify-between shadow-xs">
          <div className="flex items-center gap-2 sm:gap-3.5 shrink-0">
            <Link
              href="/booking"
              className="flex items-center justify-center rounded-full p-1.5 text-stone-700 hover:bg-stone-100 hover:text-black transition-colors"
              title="Back to All Bookings"
            >
              <ArrowLeft className="h-4 w-4" />
            </Link>

            <Link href="/" className="flex items-center transition-opacity hover:opacity-90 shrink-0">
              <div className="relative h-5 sm:h-6 w-20 sm:w-28">
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
              <Calendar className="h-3.5 w-3.5 text-stone-500" />
              <span className="font-bold text-stone-900 iosevka-charon-bold">BOOKING #{id}</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Link
              href="/chat"
              className="btn-metal-shine inline-flex items-center gap-1.5 rounded-full px-4 py-1.5 text-xs font-bold active:scale-95"
            >
              <Wrench className="h-3.5 w-3.5 relative z-10" />
              <span className="relative z-10">Diagnostics</span>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 flex-1 w-full max-w-3xl mx-auto px-2 sm:px-4 py-6 sm:py-8 space-y-6">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-stone-500">
            <Loader2 className="h-7 w-7 animate-spin text-red-600 mb-3" />
            <p className="text-xs font-mono">Fetching booking #{id} details...</p>
          </div>
        ) : error || !booking ? (
          <div className="rounded-3xl border border-white/80 bg-white/75 backdrop-blur-md p-10 text-center max-w-md mx-auto space-y-4 shadow-xs">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-50 text-red-600 border border-red-100">
              <AlertTriangle className="h-5 w-5" />
            </div>
            <h2 className="text-lg font-bold text-black iosevka-charon-bold">Booking Not Found</h2>
            <p className="text-xs text-stone-500">
              {error?.message || `We could not find booking #${id}. Please check the booking ID and try again.`}
            </p>
            <div className="pt-2 flex justify-center gap-2.5">
              <Link
                href="/booking"
                className="rounded-full border border-stone-300 bg-white px-4 py-2 text-xs font-semibold text-stone-800 hover:bg-stone-50 transition-colors"
              >
                All Bookings
              </Link>
              <Link
                href="/chat"
                className="btn-metal-shine inline-flex items-center gap-1.5 rounded-full px-4 py-2 text-xs font-bold active:scale-95"
              >
                <span className="relative z-10">Start New Diagnosis</span>
              </Link>
            </div>
          </div>
        ) : (
          <div className="rounded-3xl border border-stone-200/80 bg-white/85 backdrop-blur-md overflow-hidden shadow-2xs">
            {/* Banner */}
            <div className="border-b border-stone-200 bg-stone-50/80 p-6 sm:p-8 flex flex-col sm:flex-row items-center gap-5 text-center sm:text-left">
              <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-700 border border-emerald-200">
                <CheckCircle2 className="h-8 w-8" />
              </div>

              <div className="space-y-1">
                <div className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-mono font-bold text-emerald-700 border border-emerald-200">
                  <span>STATUS: {booking.status.toUpperCase()}</span>
                </div>
                <h1 className="text-xl sm:text-2xl font-bold text-black iosevka-charon-bold">
                  Booking Confirmed
                </h1>
                <p className="text-xs text-stone-500">
                  A certified mobile mechanic has been assigned to your service request.
                </p>
              </div>
            </div>

            {/* Details Section */}
            <div className="p-6 sm:p-8 space-y-6">
              {/* Key Highlights Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 rounded-2xl bg-stone-50 p-5 border border-stone-200/80">
                <div>
                  <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-stone-500">
                    Booking ID
                  </span>
                  <p className="text-lg font-bold font-mono text-stone-900 mt-0.5">
                    #{booking.id}
                  </p>
                </div>

                <div>
                  <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-stone-500">
                    Requested Service
                  </span>
                  <p className="text-sm font-bold text-stone-900 mt-0.5">
                    {booking.service}
                  </p>
                </div>

                <div className="border-t border-stone-200/80 pt-3">
                  <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-stone-500 flex items-center gap-1.5">
                    <Calendar className="h-3.5 w-3.5 text-stone-600" />
                    <span>Scheduled Date</span>
                  </span>
                  <p className="text-sm font-bold text-stone-900 mt-1">
                    {booking.preferred_date}
                  </p>
                </div>

                <div className="border-t border-stone-200/80 pt-3">
                  <span className="text-[11px] font-mono font-semibold uppercase tracking-wider text-stone-500 flex items-center gap-1.5">
                    <Clock className="h-3.5 w-3.5 text-stone-600" />
                    <span>Time Window</span>
                  </span>
                  <p className="text-sm font-bold text-stone-900 mt-1">
                    {booking.preferred_time}
                  </p>
                </div>
              </div>

              {/* Customer & Vehicle Information */}
              <div className="rounded-2xl border border-stone-200 bg-white p-5 space-y-3">
                <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-stone-500">
                  Customer & Vehicle Details
                </h3>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div className="flex items-center gap-2 text-stone-600">
                    <User className="h-4 w-4 text-stone-400 shrink-0" />
                    <span>Customer: <strong className="text-stone-900">{booking.customer_name}</strong></span>
                  </div>

                  <div className="flex items-center gap-2 text-stone-600">
                    <Phone className="h-4 w-4 text-stone-400 shrink-0" />
                    <span>Phone: <strong className="text-stone-900 font-mono">{booking.phone}</strong></span>
                  </div>

                  <div className="flex items-center gap-2 text-stone-600 sm:col-span-2">
                    <Car className="h-4 w-4 text-red-600 shrink-0" />
                    <span>Vehicle: <strong className="text-stone-900">{booking.vehicle}</strong></span>
                  </div>

                  {booking.notes && (
                    <div className="sm:col-span-2 pt-2 border-t border-stone-100 text-stone-500 italic">
                      Special Note: &quot;{booking.notes}&quot;
                    </div>
                  )}
                </div>
              </div>

              {/* Linked Diagnosis Report */}
              {booking.diagnosis_details && (
                <div className="rounded-2xl border border-stone-200 bg-stone-50/70 p-5 space-y-2">
                  <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-stone-600 flex items-center gap-1.5">
                    <Wrench className="h-3.5 w-3.5 text-red-600" />
                    <span>Linked Diagnostic Summary</span>
                  </h3>
                  <p className="text-sm font-bold text-stone-900">
                    {booking.diagnosis_details.diagnosis}
                  </p>
                  {booking.diagnosis_details.reasoning && (
                    <p className="text-xs text-stone-600 leading-relaxed">
                      {booking.diagnosis_details.reasoning}
                    </p>
                  )}
                </div>
              )}

              {/* Actions */}
              <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-stone-200">
                <button
                  onClick={handlePrint}
                  className="flex items-center gap-1.5 rounded-full border border-stone-300 bg-white px-4 py-2 text-xs font-semibold text-stone-800 hover:bg-stone-50 transition-colors"
                >
                  <Printer className="h-4 w-4" />
                  <span>Print Service Pass</span>
                </button>

                <Link
                  href="/chat"
                  className="btn-metal-shine inline-flex items-center gap-1.5 rounded-full px-5 py-2 text-xs font-bold active:scale-95"
                >
                  <Wrench className="h-3.5 w-3.5 relative z-10" />
                  <span className="relative z-10">Back to AI Diagnostics</span>
                </Link>
              </div>
            </div>
          </div>
        )}
      </main>

      <ErrorAlert
        error={error}
        onDismiss={() => setError(null)}
      />
    </div>
  );
}
