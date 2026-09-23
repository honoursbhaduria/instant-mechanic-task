'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { X, Loader2 } from 'lucide-react';
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

    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateStr = tomorrow.toISOString().split('T')[0];
    setPreferredDate(dateStr);

    api.getVehicleMakes()
      .then((res) => {
        if (res?.makes) setMakes(res.makes);
      })
      .catch(() => {});
  }, [diagnosis]);

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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/40 backdrop-blur-xs animate-in fade-in duration-150">
      <div className="relative w-full max-w-lg rounded-3xl border border-stone-200/90 bg-[#faf9f5] overflow-hidden max-h-[92vh] flex flex-col text-stone-900 shadow-2xs">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-stone-200/80 bg-white/80 backdrop-blur-md px-5 sm:px-6 py-4">
          <div>
            <h2 className="text-base sm:text-lg font-bold text-black iosevka-charon-bold tracking-tight">
              {confirmedBooking ? 'Booking Confirmed' : 'Book a Certified Mechanic'}
            </h2>
            <p className="text-xs text-stone-500 mt-0.5">
              {confirmedBooking
                ? 'Your service request has been registered.'
                : 'Fast doorstep or garage repair dispatch across Delhi NCR'}
            </p>
          </div>

          <button
            onClick={handleClose}
            className="rounded-full p-1.5 text-stone-400 hover:bg-stone-100 hover:text-black transition-colors"
            title="Close"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="overflow-y-auto p-5 sm:p-6 space-y-4">
          {/* Success Screen */}
          {confirmedBooking ? (
            <div className="space-y-5 text-center py-2">
              <div>
                <h3 className="text-xl sm:text-2xl font-bold text-black iosevka-charon-bold">
                  Booking Confirmed
                </h3>
                <p className="mt-1 text-xs text-stone-500">
                  Our mechanic will contact you prior to arrival.
                </p>
              </div>

              {/* Booking Summary Box */}
              <div className="rounded-2xl border border-stone-200 bg-white p-4 sm:p-5 text-left space-y-2.5">
                <div className="flex justify-between items-center pb-2 border-b border-stone-100">
                  <span className="text-xs font-mono text-stone-500">Booking ID:</span>
                  <span className="font-mono text-sm font-bold text-black">
                    #{confirmedBooking.id}
                  </span>
                </div>

                <div className="flex justify-between items-center pb-2 border-b border-stone-100">
                  <span className="text-xs font-mono text-stone-500">Service:</span>
                  <span className="text-xs font-bold text-stone-900 text-right max-w-[220px]">
                    {confirmedBooking.service}
                  </span>
                </div>

                <div className="flex justify-between items-center pb-2 border-b border-stone-100">
                  <span className="text-xs font-mono text-stone-500">Customer:</span>
                  <span className="text-xs font-bold text-stone-900">
                    {confirmedBooking.customer_name} ({confirmedBooking.phone})
                  </span>
                </div>

                <div className="flex justify-between items-center pb-2 border-b border-stone-100">
                  <span className="text-xs font-mono text-stone-500">Vehicle:</span>
                  <span className="text-xs font-bold text-stone-900">
                    {confirmedBooking.vehicle}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 pt-1">
                  <div>
                    <span className="text-[10px] font-mono text-stone-400 block uppercase">Date</span>
                    <span className="text-xs font-bold text-stone-900">
                      {confirmedBooking.preferred_date}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] font-mono text-stone-400 block uppercase">Time</span>
                    <span className="text-xs font-bold text-stone-900">
                      {confirmedBooking.preferred_time}
                    </span>
                  </div>
                </div>
              </div>

              <div className="flex flex-col sm:flex-row gap-2.5 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    handleClose();
                    router.push(`/booking/${confirmedBooking.id}`);
                  }}
                  className="btn-metal-shine flex-1 inline-flex items-center justify-center rounded-xl px-4 py-2.5 text-xs sm:text-sm font-bold active:scale-95"
                >
                  <span className="relative z-10">View Full Details</span>
                </button>
                <button
                  type="button"
                  onClick={handleClose}
                  className="rounded-xl border border-stone-300 bg-white px-4 py-2.5 text-xs sm:text-sm font-semibold text-stone-700 hover:bg-stone-50 transition-colors"
                >
                  Back to Chat
                </button>
              </div>
            </div>
          ) : (
            /* Booking Form */
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800">
                  {error.message}
                </div>
              )}

              {/* Service Title */}
              <div>
                <label className="block text-[11px] font-mono font-bold uppercase tracking-wider text-stone-600 mb-1.5">
                  Service / Repair Needed
                </label>
                <input
                  type="text"
                  required
                  value={service}
                  onChange={(e) => setService(e.target.value)}
                  className="w-full rounded-xl border border-stone-300 bg-white px-3.5 py-2.5 text-xs sm:text-sm text-stone-900 placeholder-stone-400 focus:border-stone-500 focus:outline-none"
                  placeholder="CV Joint & Axle Inspection / Replacement"
                />
              </div>

              {/* Customer Name & Phone */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-mono font-bold uppercase tracking-wider text-stone-600 mb-1.5">
                    Your Full Name
                  </label>
                  <input
                    type="text"
                    required
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                    className="w-full rounded-xl border border-stone-300 bg-white px-3.5 py-2.5 text-xs sm:text-sm text-stone-900 placeholder-stone-400 focus:border-stone-500 focus:outline-none"
                    placeholder="e.g. Honours"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-mono font-bold uppercase tracking-wider text-stone-600 mb-1.5">
                    Phone Number
                  </label>
                  <input
                    type="tel"
                    required
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    className="w-full rounded-xl border border-stone-300 bg-white px-3.5 py-2.5 text-xs sm:text-sm text-stone-900 placeholder-stone-400 focus:border-stone-500 focus:outline-none"
                    placeholder="e.g. 9876543210"
                  />
                </div>
              </div>

              {/* Vehicle input */}
              <div>
                <label className="block text-[11px] font-mono font-bold uppercase tracking-wider text-stone-600 mb-1.5">
                  Vehicle Make & Model
                </label>
                <div className="mb-2">
                  <input
                    type="text"
                    required
                    value={vehicle}
                    onChange={(e) => setVehicle(e.target.value)}
                    className="w-full rounded-xl border border-stone-300 bg-white px-3.5 py-2.5 text-xs sm:text-sm text-stone-900 placeholder-stone-400 focus:border-stone-500 focus:outline-none"
                    placeholder="e.g. Hyundai Creta 2022"
                  />
                </div>

                {/* Optional NHTSA Vehicle Selector */}
                <div className="rounded-xl border border-stone-200 bg-stone-50 p-2.5 text-xs space-y-1.5">
                  <span className="text-[10px] font-mono text-stone-500 block">
                    Or select from vehicle database (NHTSA):
                  </span>
                  <div className="grid grid-cols-2 gap-2">
                    <select
                      value={selectedMake}
                      onChange={(e) => {
                        const m = e.target.value;
                        setSelectedMake(m);
                        if (m) setVehicle(m);
                      }}
                      className="rounded-lg border border-stone-300 bg-white px-2.5 py-1.5 text-xs text-stone-800 focus:border-stone-500 focus:outline-none"
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
                      className="rounded-lg border border-stone-300 bg-white px-2.5 py-1.5 text-xs text-stone-800 focus:border-stone-500 focus:outline-none disabled:opacity-40"
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
                  <label className="block text-[11px] font-mono font-bold uppercase tracking-wider text-stone-600 mb-1.5">
                    Preferred Date
                  </label>
                  <input
                    type="date"
                    required
                    value={preferredDate}
                    onChange={(e) => setPreferredDate(e.target.value)}
                    className="w-full rounded-xl border border-stone-300 bg-white px-3.5 py-2 text-xs sm:text-sm text-stone-900 focus:border-stone-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-[11px] font-mono font-bold uppercase tracking-wider text-stone-600 mb-1.5">
                    Preferred Time Slot
                  </label>
                  <select
                    value={preferredTime}
                    onChange={(e) => setPreferredTime(e.target.value)}
                    className="w-full rounded-xl border border-stone-300 bg-white px-3.5 py-2 text-xs sm:text-sm text-stone-900 focus:border-stone-500 focus:outline-none"
                  >
                    {availableTimes.map((t) => (
                      <option key={t} value={t}>
                        {t}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Additional Notes */}
              <div>
                <label className="block text-[11px] font-mono font-bold uppercase tracking-wider text-stone-600 mb-1.5">
                  Additional Notes (Optional)
                </label>
                <textarea
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="e.g. Please check both front axles and bring brake pads."
                  className="w-full rounded-xl border border-stone-300 bg-white p-3 text-xs text-stone-900 placeholder-stone-400 focus:border-stone-500 focus:outline-none"
                />
              </div>

              {/* Submit CTA */}
              <div className="pt-2">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="btn-metal-shine w-full inline-flex items-center justify-center rounded-xl py-3 px-5 text-xs sm:text-sm font-bold active:scale-[0.99] disabled:opacity-50"
                >
                  {isSubmitting ? (
                    <span className="relative z-10 flex items-center gap-2">
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Confirming Booking...
                    </span>
                  ) : (
                    <span className="relative z-10">
                      Confirm & Book Mechanic
                    </span>
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
