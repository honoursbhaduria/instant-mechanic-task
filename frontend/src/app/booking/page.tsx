'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { Calendar, Search, Wrench, Car, ArrowRight, ArrowLeft, Loader2, Sparkles } from 'lucide-react';
import { api, parseApiError, ApiError } from '@/lib/api';
import { Booking } from '@/lib/types';
import ErrorAlert from '@/components/ErrorAlert';

export default function BookingsPage() {
  const router = useRouter();
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchId, setSearchId] = useState('');
  const [error, setError] = useState<ApiError | null>(null);

  useEffect(() => {
    fetchBookings();
  }, []);

  const fetchBookings = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listBookings();
      setBookings(data);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchId.trim()) return;
    router.push(`/booking/${searchId.trim()}`);
  };

  const getStatusBadge = (status: string) => {
    switch (status.toLowerCase()) {
      case 'confirmed':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200';
      case 'pending':
        return 'bg-amber-50 text-amber-800 border-amber-200';
      case 'completed':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'cancelled':
        return 'bg-stone-100 text-stone-600 border-stone-200';
      default:
        return 'bg-stone-100 text-stone-700 border-stone-200';
    }
  };

  return (
    <div className="min-h-screen bg-[#faf9f5] text-stone-900 font-sans relative flex flex-col overflow-x-clip selection:bg-red-600 selection:text-white">
      {/* Background Subtle Tech Grid Layer matching landing page */}
      <div
        className="fixed inset-0 pointer-events-none bg-grid-subtle opacity-90 z-0"
        style={{
          maskImage: 'radial-gradient(ellipse 75% 65% at 50% 30%, #000 70%, transparent 100%)',
          WebkitMaskImage: 'radial-gradient(ellipse 75% 65% at 50% 30%, #000 70%, transparent 100%)'
        }}
      />

      {/* Floating Capsule Header */}
      <header className="relative z-20 w-full max-w-5xl mx-auto pt-3 sm:pt-4 px-2 sm:px-4 shrink-0">
        <div className="rounded-full bg-white/85 backdrop-blur-md border border-stone-200/80 px-3 sm:px-5 py-2 sm:py-2.5 flex items-center justify-between shadow-xs">
          <div className="flex items-center gap-2 sm:gap-3.5 shrink-0">
            <Link
              href="/"
              className="flex items-center justify-center rounded-full p-1.5 text-stone-700 hover:bg-stone-100 hover:text-black transition-colors"
              title="Back to Home"
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
              <span className="font-bold text-stone-900 iosevka-charon-bold">BOOKINGS</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Link
              href="/chat"
              className="btn-metal-shine inline-flex items-center gap-1.5 rounded-full px-3.5 sm:px-4 py-1.5 text-xs font-bold active:scale-95 whitespace-nowrap"
            >
              <Sparkles className="h-3.5 w-3.5 text-amber-400 relative z-10" />
              <span className="relative z-10 hidden xs:inline">New Consultation</span>
              <span className="relative z-10 xs:hidden">Consult</span>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="relative z-10 flex-1 w-full max-w-5xl mx-auto px-2 sm:px-4 py-6 sm:py-8 space-y-6">
        {/* Title and search bar */}
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 pb-3 border-b border-stone-200/70">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-black iosevka-charon-bold tracking-tight">
              Mechanic Bookings
            </h1>
            <p className="text-xs text-stone-500 mt-1">
              Track confirmed appointments, mechanic dispatch arrival times, and repair orders.
            </p>
          </div>

          {/* Quick ID Search */}
          <form onSubmit={handleSearch} className="flex items-center gap-2 w-full max-w-none sm:max-w-xs">
            <div className="relative flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-stone-400" />
              <input
                type="text"
                placeholder="Search Booking #..."
                value={searchId}
                onChange={(e) => setSearchId(e.target.value)}
                className="w-full rounded-full border border-stone-300 bg-white py-1.5 pl-8 pr-3 text-xs text-stone-900 placeholder-stone-400 focus:border-stone-500 focus:outline-none"
              />
            </div>
            <button
              type="submit"
              className="rounded-full bg-stone-900 px-3.5 py-1.5 text-xs font-semibold text-white hover:bg-black transition-colors"
            >
              Find
            </button>
          </form>
        </div>

        {/* Bookings List */}
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-stone-500">
            <Loader2 className="h-7 w-7 animate-spin text-red-600 mb-3" />
            <p className="text-xs font-mono">Retrieving mechanic bookings...</p>
          </div>
        ) : bookings.length === 0 ? (
          <div className="rounded-3xl border border-white/80 bg-white/75 backdrop-blur-md p-10 text-center max-w-md mx-auto space-y-4 shadow-xs">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-50 text-red-600 border border-red-100">
              <Calendar className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-black iosevka-charon-bold">No Bookings Found</h3>
              <p className="text-xs text-stone-500 mt-1">
                You haven&apos;t scheduled any mechanic appointments yet. Complete a diagnosis to book verified service.
              </p>
            </div>
            <Link
              href="/chat"
              className="btn-metal-shine inline-flex items-center gap-2 rounded-full px-5 py-2 text-xs font-bold active:scale-95 mx-auto"
            >
              <Wrench className="h-3.5 w-3.5 relative z-10" />
              <span className="relative z-10">Start Vehicle Diagnosis</span>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {bookings.map((booking) => (
              <div
                key={booking.id}
                className="flex flex-col justify-between rounded-2xl border border-stone-200/80 bg-white/85 backdrop-blur-md p-5 shadow-2xs hover:border-stone-400 transition-colors"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-stone-900 iosevka-charon-bold">
                      Booking #{booking.id}
                    </span>
                    <span
                      className={`rounded-full border px-2.5 py-0.5 text-[10px] font-mono font-bold uppercase tracking-wider ${getStatusBadge(
                        booking.status
                      )}`}
                    >
                      {booking.status}
                    </span>
                  </div>

                  <div>
                    <h3 className="text-sm font-bold text-stone-900">
                      {booking.service}
                    </h3>
                    <div className="mt-1 flex items-center gap-1.5 text-xs text-stone-600">
                      <Car className="h-3.5 w-3.5 text-red-600" />
                      <span>{booking.vehicle}</span>
                    </div>
                  </div>

                  <div className="rounded-xl bg-stone-50 p-3 border border-stone-200/80 space-y-1.5 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-stone-500">Customer:</span>
                      <span className="font-medium text-stone-900">{booking.customer_name}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-stone-500">Phone:</span>
                      <span className="font-mono text-stone-900">{booking.phone}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-stone-500">Schedule:</span>
                      <span className="font-semibold text-stone-900">
                        {booking.preferred_date} at {booking.preferred_time}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="mt-4 pt-3 border-t border-stone-100 flex items-center justify-between text-xs">
                  <span className="text-stone-400 font-mono text-[11px]">
                    {booking.created_at ? new Date(booking.created_at).toLocaleDateString() : ''}
                  </span>
                  <Link
                    href={`/booking/${booking.id}`}
                    className="flex items-center gap-1 font-semibold text-stone-900 hover:text-red-600 transition-colors"
                  >
                    <span>View Details</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      <ErrorAlert
        error={error}
        onDismiss={() => setError(null)}
        onRetry={fetchBookings}
      />
    </div>
  );
}
