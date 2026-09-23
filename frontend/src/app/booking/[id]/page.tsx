'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
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
  Printer,
  ShieldCheck
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

  useEffect(() => {
    if (id) {
      fetchBookingDetails();
    }
  }, [id]);

  const fetchBookingDetails = async () => {
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
  };

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="flex min-h-[60vh] flex-col items-center justify-center py-20 text-neutral-400">
        <Loader2 className="h-8 w-8 animate-spin text-amber-500 mb-3" />
        <p className="text-sm">Fetching booking #{id} details...</p>
      </div>
    );
  }

  if (error || !booking) {
    return (
      <div className="mx-auto max-w-lg px-4 py-16 text-center space-y-4">
        <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-rose-500/10 text-rose-400">
          <AlertTriangle className="h-7 w-7" />
        </div>
        <h2 className="text-xl font-bold text-white">Booking Not Found</h2>
        <p className="text-sm text-neutral-400">
          {error?.message || `We could not find booking #${id}. Please check the booking ID and try again.`}
        </p>
        <div className="pt-2 flex justify-center gap-3">
          <Link
            href="/booking"
            className="rounded-xl border border-neutral-800 bg-neutral-900 px-4 py-2 text-xs font-semibold text-neutral-300 hover:bg-neutral-800"
          >
            All Bookings
          </Link>
          <Link
            href="/chat"
            className="rounded-xl bg-amber-500 px-4 py-2 text-xs font-bold text-neutral-950 hover:bg-amber-400"
          >
            Start New Diagnosis
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6 space-y-6">
      {/* Back button */}
      <div>
        <Link
          href="/booking"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-neutral-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          <span>Back to All Bookings</span>
        </Link>
      </div>

      {/* Main Confirmation Card */}
      <div className="overflow-hidden rounded-3xl border border-neutral-800 bg-neutral-900 shadow-2xl">
        {/* Banner */}
        <div className="bg-gradient-to-r from-emerald-600/30 via-emerald-500/20 to-neutral-950 p-6 sm:p-8 border-b border-neutral-800 text-center sm:text-left flex flex-col sm:flex-row items-center gap-5">
          <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-emerald-500 text-neutral-950 shadow-xl shadow-emerald-500/20">
            <CheckCircle2 className="h-10 w-10" />
          </div>

          <div>
            <div className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/20 px-2.5 py-0.5 text-xs font-bold text-emerald-300 mb-1 border border-emerald-500/30">
              <ShieldCheck className="h-3.5 w-3.5" />
              <span>Status: {booking.status.toUpperCase()}</span>
            </div>
            <h1 className="text-2xl font-black text-white sm:text-3xl">
              Booking Confirmed ✅
            </h1>
            <p className="text-xs text-neutral-300 mt-1">
              A certified mobile mechanic has been assigned to your service request.
            </p>
          </div>
        </div>

        {/* Details Section */}
        <div className="p-6 sm:p-8 space-y-6">
          {/* Key Metric Highlights */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 rounded-2xl bg-neutral-950/80 p-5 border border-neutral-800/80">
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-neutral-500">
                Booking ID
              </span>
              <p className="text-xl font-black font-mono text-amber-400 mt-0.5">
                #{booking.id}
              </p>
            </div>

            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-neutral-500">
                Requested Service
              </span>
              <p className="text-base font-bold text-white mt-0.5">
                {booking.service}
              </p>
            </div>

            <div className="border-t border-neutral-800/60 pt-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-neutral-500 flex items-center gap-1.5">
                <Calendar className="h-3.5 w-3.5 text-amber-400" />
                <span>Date</span>
              </span>
              <p className="text-sm font-bold text-neutral-200 mt-1">
                {booking.preferred_date}
              </p>
            </div>

            <div className="border-t border-neutral-800/60 pt-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-neutral-500 flex items-center gap-1.5">
                <Clock className="h-3.5 w-3.5 text-amber-400" />
                <span>Time Slot</span>
              </span>
              <p className="text-sm font-bold text-neutral-200 mt-1">
                {booking.preferred_time}
              </p>
            </div>
          </div>

          {/* Customer & Vehicle Info */}
          <div className="rounded-2xl border border-neutral-800 bg-neutral-950/40 p-5 space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-amber-400">
              Customer & Vehicle Details
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="flex items-center gap-2 text-neutral-300">
                <User className="h-4 w-4 text-neutral-500 shrink-0" />
                <span>Customer: <strong className="text-white">{booking.customer_name}</strong></span>
              </div>

              <div className="flex items-center gap-2 text-neutral-300">
                <Phone className="h-4 w-4 text-neutral-500 shrink-0" />
                <span>Phone: <strong className="text-white font-mono">{booking.phone}</strong></span>
              </div>

              <div className="flex items-center gap-2 text-neutral-300 sm:col-span-2">
                <Car className="h-4 w-4 text-neutral-500 shrink-0" />
                <span>Vehicle: <strong className="text-white">{booking.vehicle}</strong></span>
              </div>

              {booking.notes && (
                <div className="sm:col-span-2 pt-2 border-t border-neutral-800 text-neutral-400 italic">
                  Note: &quot;{booking.notes}&quot;
                </div>
              )}
            </div>
          </div>

          {/* Linked Diagnosis Report if available */}
          {booking.diagnosis_details && (
            <div className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-5 space-y-2">
              <h3 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
                <Wrench className="h-4 w-4" />
                <span>Linked Diagnostic Summary</span>
              </h3>
              <p className="text-sm font-bold text-white">
                {booking.diagnosis_details.diagnosis}
              </p>
              {booking.diagnosis_details.reasoning && (
                <p className="text-xs text-neutral-300 leading-relaxed">
                  {booking.diagnosis_details.reasoning}
                </p>
              )}
            </div>
          )}

          {/* Actions */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-neutral-800">
            <button
              onClick={handlePrint}
              className="flex items-center gap-1.5 rounded-xl border border-neutral-800 bg-neutral-800/60 px-4 py-2.5 text-xs font-semibold text-neutral-300 hover:bg-neutral-800 transition-colors"
            >
              <Printer className="h-4 w-4" />
              <span>Print Service Pass</span>
            </button>

            <Link
              href="/chat"
              className="flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 px-5 py-2.5 text-xs font-bold text-neutral-950 shadow-md transition-transform hover:scale-105 active:scale-95"
            >
              <Wrench className="h-4 w-4" />
              <span>Back to Mechanic Chat</span>
            </Link>
          </div>
        </div>
      </div>

      <ErrorAlert
        error={error}
        onDismiss={() => setError(null)}
      />
    </div>
  );
}
