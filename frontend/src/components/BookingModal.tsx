'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { X, Calendar, Clock, User, Phone, Car, Wrench, CheckCircle, Loader2, ArrowRight } from 'lucide-react';
import { api, parseApiError, ApiError } from '@/lib/api';
import { Diagnosis, Booking } from '@/lib/types';

interface BookingModalProps {
  diagnosis: Diagnosis | null;
  isOpen: boolean;
  onClose: () => void;
  onBookingSuccess?: (booking: Booking) => void;
}

export default function BookingModal({ diagnosis, isOpen, onClose, onBookingSuccess }: BookingModalProps) {
  const router = useRouter();

  // Form fields
  const [customerName, setCustomerName] = useState('');
  const [phone, setPhone] = useState('');
  const [vehicle, setVehicle] = useState('');
  const [preferredDate, setPreferredDate] = useState('');
  const [preferredTime, setPreferredTime] = useState('11:00 AM');
  const [service, setService] = useState('');
  const [notes, setNotes] = useState('');

  // Vehicle selector helper states
  const [makes, setMakes] = useState<string[]>([]);
  const [selectedMake, setSelectedMake] = useState('');
  const [models, setModels] = useState<string[]>([]);
  const [loadingModels, setLoadingModels] = useState(false);

  // Submission & Confirmation state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [confirmedBooking, setConfirmedBooking] = useState<Booking | null>(null);

  // Initialize defaults from diagnosis
  useEffect(() => {
    if (diagnosis) {
      setService(diagnosis.service || diagnosis.recommendation || 'General Mechanic Inspection');
      if (diagnosis.vehicle) {
        setVehicle(diagnosis.vehicle);
      }
    }

    // Default preferred date to tomorrow's date
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateStr = tomorrow.toISOString().split('T')[0];
    setPreferredDate(dateStr);

    // Fetch vehicle makes list for full vehicle database access
    api.getVehicleMakes()
      .then((res) => {
        if (res?.makes) setMakes(res.makes);
      })
      .catch(() => {});
  }, [diagnosis]);

  // When user selects a make from the vehicle helper dropdown
  useEffect(() => {
    if (!selectedMake) {
      setModels([]);
      return;
    }
    setLoadingModels(true);
    api.getVehicleModels(selectedMake)
      .then((res) => {
        setModels(res.models || []);
      })
      .catch(() => {})
      .finally(() => setLoadingModels(false));
  }, [selectedMake]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validation
    if (!customerName.trim() || customerName.trim().length < 2) {
      setError({ status: 400, message: 'Please enter your full name (minimum 2 characters).' });
      return;
    }
    if (!phone.trim() || phone.replace(/\D/g, '').length < 10) {
      setError({ status: 400, message: 'Please enter a valid 10-digit phone number.' });
      return;
    }
    if (!vehicle.trim()) {
      setError({ status: 400, message: 'Please specify your vehicle make & model.' });
      return;
    }
    if (!preferredDate) {
      setError({ status: 400, message: 'Please select a preferred date.' });
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await api.createBooking({
        diagnosis_id: diagnosis?.id || null,
        customer_name: customerName.trim(),
        phone: phone.trim(),
        vehicle: vehicle.trim(),
        preferred_date: preferredDate,
        preferred_time: preferredTime,
        service: service.trim(),
        notes: notes.trim(),
      });

      setConfirmedBooking(result);
      if (onBookingSuccess) {
        onBookingSuccess(result);
      }
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setConfirmedBooking(null);
    setError(null);
    onClose();
  };

  const availableTimes = [
    '09:00 AM',
    '10:30 AM',
    '11:00 AM',
    '01:00 PM',
    '02:30 PM',
    '04:00 PM',
    '05:30 PM',
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg rounded-2xl border border-neutral-800 bg-neutral-900 shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-neutral-800 bg-neutral-950/80 px-6 py-4">
          <div className="flex items-center gap-2.5">
            <div className="rounded-lg bg-amber-500/20 p-2 text-amber-400">
              <Wrench className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">
                {confirmedBooking ? 'Booking Confirmed' : 'Book a Certified Mechanic'}
              </h2>
              <p className="text-xs text-neutral-400">
                {confirmedBooking
                  ? 'Your service request has been registered.'
                  : 'Fast doorstep or garage repair dispatch'}
              </p>
            </div>
          </div>

          <button
            onClick={handleClose}
            className="rounded-lg p-1.5 text-neutral-400 hover:bg-neutral-800 hover:text-white transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="overflow-y-auto p-6 space-y-4">
          {/* Success Screen */}
          {confirmedBooking ? (
            <div className="space-y-6 text-center py-4">
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400 ring-8 ring-emerald-500/10">
                <CheckCircle className="h-10 w-10" />
              </div>

              <div>
                <h3 className="text-2xl font-extrabold text-white">
                  Booking Confirmed ✅
                </h3>
                <p className="mt-1 text-sm text-neutral-400">
                  Our mechanic team has received your service appointment.
                </p>
              </div>

              {/* Booking Summary Box */}
              <div className="rounded-xl border border-neutral-800 bg-neutral-950/70 p-5 text-left space-y-3">
                <div className="flex justify-between items-center pb-2 border-b border-neutral-800/80">
                  <span className="text-xs font-medium text-neutral-400">Booking ID:</span>
                  <span className="font-mono text-base font-bold text-amber-400">
                    #{confirmedBooking.id}
                  </span>
                </div>

                <div className="flex justify-between items-center pb-2 border-b border-neutral-800/80">
                  <span className="text-xs font-medium text-neutral-400">Service:</span>
                  <span className="text-xs font-bold text-neutral-100 text-right max-w-[240px]">
                    {confirmedBooking.service}
                  </span>
                </div>

                <div className="flex justify-between items-center pb-2 border-b border-neutral-800/80">
                  <span className="text-xs font-medium text-neutral-400">Customer:</span>
                  <span className="text-xs font-semibold text-neutral-200">
                    {confirmedBooking.customer_name} ({confirmedBooking.phone})
                  </span>
                </div>

                <div className="flex justify-between items-center pb-2 border-b border-neutral-800/80">
                  <span className="text-xs font-medium text-neutral-400">Vehicle:</span>
                  <span className="text-xs font-semibold text-neutral-200">
                    {confirmedBooking.vehicle}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 pt-1">
                  <div>
                    <span className="text-[11px] text-neutral-400 block">Date</span>
                    <span className="text-xs font-bold text-amber-300">
                      {confirmedBooking.preferred_date}
                    </span>
                  </div>
                  <div>
                    <span className="text-[11px] text-neutral-400 block">Time</span>
                    <span className="text-xs font-bold text-amber-300">
                      {confirmedBooking.preferred_time}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  type="button"
                  onClick={() => {
                    handleClose();
                    router.push(`/booking/${confirmedBooking.id}`);
                  }}
                  className="flex-1 flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 px-4 py-2.5 text-sm font-bold text-neutral-950 shadow-md transition-transform active:scale-95"
                >
                  <span>View Full Details</span>
                  <ArrowRight className="h-4 w-4" />
                </button>
                <button
                  type="button"
                  onClick={handleClose}
                  className="rounded-xl border border-neutral-800 px-4 py-2.5 text-sm font-semibold text-neutral-300 hover:bg-neutral-800 transition-colors"
                >
                  Back to Chat
                </button>
              </div>
            </div>
          ) : (
            /* Booking Form */
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-300">
                  {error.message}
                </div>
              )}

              {/* Service Title */}
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-neutral-400 mb-1.5">
                  Service / Repair Needed
                </label>
                <div className="relative">
                  <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-neutral-500">
                    <Wrench className="h-4 w-4" />
                  </div>
                  <input
                    type="text"
                    required
                    value={service}
                    onChange={(e) => setService(e.target.value)}
                    className="w-full rounded-xl border border-neutral-800 bg-neutral-950/80 py-2.5 pl-10 pr-3 text-sm text-white placeholder-neutral-500 focus:border-amber-500 focus:outline-none"
                    placeholder="e.g. CV Joint Inspection"
                  />
                </div>
              </div>

              {/* Customer Name & Phone */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-neutral-400 mb-1.5">
                    Your Full Name
                  </label>
                  <div className="relative">
                    <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-neutral-500">
                      <User className="h-4 w-4" />
                    </div>
                    <input
                      type="text"
                      required
                      value={customerName}
                      onChange={(e) => setCustomerName(e.target.value)}
                      className="w-full rounded-xl border border-neutral-800 bg-neutral-950/80 py-2.5 pl-10 pr-3 text-sm text-white placeholder-neutral-500 focus:border-amber-500 focus:outline-none"
                      placeholder="e.g. Honours"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-neutral-400 mb-1.5">
                    Phone Number
                  </label>
                  <div className="relative">
                    <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-neutral-500">
                      <Phone className="h-4 w-4" />
                    </div>
                    <input
                      type="tel"
                      required
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      className="w-full rounded-xl border border-neutral-800 bg-neutral-950/80 py-2.5 pl-10 pr-3 text-sm text-white placeholder-neutral-500 focus:border-amber-500 focus:outline-none"
                      placeholder="e.g. 9876543210"
                    />
                  </div>
                </div>
              </div>

              {/* Vehicle input + NHTSA Quick Vehicle Database Selector */}
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-neutral-400 mb-1.5">
                  Vehicle Make & Model
                </label>
                <div className="relative mb-2">
                  <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-neutral-500">
                    <Car className="h-4 w-4" />
                  </div>
                  <input
                    type="text"
                    required
                    value={vehicle}
                    onChange={(e) => setVehicle(e.target.value)}
                    className="w-full rounded-xl border border-neutral-800 bg-neutral-950/80 py-2.5 pl-10 pr-3 text-sm text-white placeholder-neutral-500 focus:border-amber-500 focus:outline-none"
                    placeholder="e.g. Hyundai Creta 2022"
                  />
                </div>

                {/* Optional NHTSA Vehicle Selector */}
                <div className="rounded-xl border border-neutral-800/80 bg-neutral-950/40 p-2.5 text-xs space-y-2">
                  <span className="text-[11px] font-medium text-neutral-400">
                    Select from vehicle database (NHTSA):
                  </span>
                  <div className="grid grid-cols-2 gap-2">
                    <select
                      value={selectedMake}
                      onChange={(e) => {
                        const m = e.target.value;
                        setSelectedMake(m);
                        if (m) setVehicle(m);
                      }}
                      className="rounded-lg border border-neutral-800 bg-neutral-900 px-2.5 py-1.5 text-xs text-neutral-200 focus:border-amber-500 focus:outline-none"
                    >
                      <option value="">Choose Make...</option>
                      {makes.map((m) => (
                        <option key={m} value={m}>
                          {m}
                        </option>
                      ))}
                    </select>

                    <select
                      disabled={!selectedMake || loadingModels}
                      onChange={(e) => {
                        if (e.target.value) {
                          setVehicle(`${selectedMake} ${e.target.value}`);
                        }
                      }}
                      className="rounded-lg border border-neutral-800 bg-neutral-900 px-2.5 py-1.5 text-xs text-neutral-200 focus:border-amber-500 focus:outline-none disabled:opacity-40"
                    >
                      <option value="">
                        {loadingModels ? 'Loading models...' : 'Choose Model...'}
                      </option>
                      {models.slice(0, 100).map((mod) => (
                        <option key={mod} value={mod}>
                          {mod}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Preferred Date & Time */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-neutral-400 mb-1.5">
                    Preferred Date
                  </label>
                  <div className="relative">
                    <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-neutral-500">
                      <Calendar className="h-4 w-4" />
                    </div>
                    <input
                      type="date"
                      required
                      value={preferredDate}
                      onChange={(e) => setPreferredDate(e.target.value)}
                      className="w-full rounded-xl border border-neutral-800 bg-neutral-950/80 py-2.5 pl-10 pr-3 text-sm text-white focus:border-amber-500 focus:outline-none"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold uppercase tracking-wider text-neutral-400 mb-1.5">
                    Preferred Time Slot
                  </label>
                  <div className="relative">
                    <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3 text-neutral-500">
                      <Clock className="h-4 w-4" />
                    </div>
                    <select
                      value={preferredTime}
                      onChange={(e) => setPreferredTime(e.target.value)}
                      className="w-full rounded-xl border border-neutral-800 bg-neutral-950/80 py-2.5 pl-10 pr-3 text-sm text-white focus:border-amber-500 focus:outline-none"
                    >
                      {availableTimes.map((t) => (
                        <option key={t} value={t}>
                          {t}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Additional Notes */}
              <div>
                <label className="block text-xs font-semibold uppercase tracking-wider text-neutral-400 mb-1.5">
                  Additional Notes (Optional)
                </label>
                <textarea
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="e.g. Please check both front axles and bring brake pads."
                  className="w-full rounded-xl border border-neutral-800 bg-neutral-950/80 p-3 text-xs text-white placeholder-neutral-500 focus:border-amber-500 focus:outline-none"
                />
              </div>

              {/* Submit CTA */}
              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 px-5 py-3 text-sm font-bold text-neutral-950 shadow-lg shadow-amber-500/20 transition-all hover:opacity-95 disabled:opacity-50 active:scale-[0.99]"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Confirming Booking...</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle className="h-4 w-4" />
                      <span>Confirm & Book Mechanic</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
