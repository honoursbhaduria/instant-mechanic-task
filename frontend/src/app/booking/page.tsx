'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Calendar, Search, Wrench, Car, ArrowRight, Loader2 } from 'lucide-react';
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
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
      case 'pending':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/30';
      case 'completed':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/30';
      case 'cancelled':
        return 'bg-neutral-800 text-neutral-400 border-neutral-700';
      default:
        return 'bg-neutral-800 text-neutral-300';
    }
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-neutral-800 pb-5">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-amber-400">
            <Calendar className="h-4 w-4" />
            <span>Service Appointments</span>
          </div>
          <h1 className="text-2xl font-extrabold text-white sm:text-3xl mt-1">
            Mechanic Bookings
          </h1>
          <p className="text-sm text-neutral-400">
            Track confirmed appointments, mechanic arrival times, and requested repair services.
          </p>
        </div>

        {/* Quick ID Search */}
        <form onSubmit={handleSearch} className="flex items-center gap-2 max-w-xs">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-neutral-500" />
            <input
              type="text"
              placeholder="Search Booking #..."
              value={searchId}
              onChange={(e) => setSearchId(e.target.value)}
              className="w-full rounded-xl border border-neutral-800 bg-neutral-900/80 py-2 pl-9 pr-3 text-xs text-white placeholder-neutral-500 focus:border-amber-500 focus:outline-none"
            />
          </div>
          <button
            type="submit"
            className="rounded-xl bg-neutral-800 px-3 py-2 text-xs font-semibold text-neutral-200 hover:bg-neutral-700 transition-colors"
          >
            Find
          </button>
        </form>
      </div>

      {/* Bookings List */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 text-neutral-400">
          <Loader2 className="h-8 w-8 animate-spin text-amber-500 mb-3" />
          <p className="text-sm">Retrieving mechanic bookings...</p>
        </div>
      ) : bookings.length === 0 ? (
        <div className="rounded-2xl border border-neutral-800 bg-neutral-900/40 p-12 text-center max-w-md mx-auto space-y-4">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-amber-500/10 text-amber-400">
            <Calendar className="h-7 w-7" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">No Bookings Found</h3>
            <p className="text-xs text-neutral-400 mt-1">
              You haven&apos;t scheduled any mechanic appointments yet. Complete a diagnosis to book verified service.
            </p>
          </div>
          <Link
            href="/chat"
            className="inline-flex items-center gap-2 rounded-xl bg-amber-500 px-4 py-2 text-xs font-bold text-neutral-950 shadow-md hover:bg-amber-400"
          >
            <Wrench className="h-3.5 w-3.5" />
            <span>Start Vehicle Diagnosis</span>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {bookings.map((booking) => (
            <div
              key={booking.id}
              className="flex flex-col justify-between overflow-hidden rounded-2xl border border-neutral-800 bg-neutral-900/60 p-5 shadow-lg transition-all hover:border-amber-500/40 hover:bg-neutral-900"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs font-bold text-amber-400">
                    Booking #{booking.id}
                  </span>
                  <span
                    className={`rounded-full border px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider ${getStatusBadge(
                      booking.status
                    )}`}
                  >
                    {booking.status}
                  </span>
                </div>

                <div>
                  <h3 className="text-base font-bold text-white">
                    {booking.service}
                  </h3>
                  <div className="mt-1 flex items-center gap-1.5 text-xs text-neutral-400">
                    <Car className="h-3.5 w-3.5 text-amber-400" />
                    <span>{booking.vehicle}</span>
                  </div>
                </div>

                <div className="rounded-xl bg-neutral-950/60 p-3 border border-neutral-800/80 space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-neutral-500">Customer:</span>
                    <span className="font-medium text-neutral-200">{booking.customer_name}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-neutral-500">Phone:</span>
                    <span className="font-mono text-neutral-200">{booking.phone}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-neutral-500">Schedule:</span>
                    <span className="font-semibold text-amber-300">
                      {booking.preferred_date} at {booking.preferred_time}
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-neutral-800/80 flex items-center justify-between text-xs">
                <span className="text-neutral-500">
                  {booking.created_at ? new Date(booking.created_at).toLocaleDateString() : ''}
                </span>
                <Link
                  href={`/booking/${booking.id}`}
                  className="flex items-center gap-1 font-semibold text-amber-400 hover:text-amber-300"
                >
                  <span>View Details</span>
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}

      <ErrorAlert
        error={error}
        onDismiss={() => setError(null)}
        onRetry={fetchBookings}
      />
    </div>
  );
}
