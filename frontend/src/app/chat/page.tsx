'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import {
  Send,
  Mic,
  RotateCcw,
  Sparkles,
  Loader2,
  Car,
  X,
  FileAudio,
  FileVideo,
  FileImage,
  ArrowLeft,
  History,
  ChevronRight
} from 'lucide-react';
import { api, parseApiError, ApiError } from '@/lib/api';
import { Message, Diagnosis, UploadResponse } from '@/lib/types';
import ChatMessage from '@/components/ChatMessage';
import DiagnosisCard from '@/components/DiagnosisCard';
import BookingModal from '@/components/BookingModal';
import MediaUploader from '@/components/MediaUploader';
import AudioRecorder from '@/components/AudioRecorder';
import ErrorAlert from '@/components/ErrorAlert';
import { TruckLoaderOverlay } from '@/components/TruckLoader';

export default function ChatPage() {
  // Smooth Truck Loader before opening the chatbot
  const [showInitialLoader, setShowInitialLoader] = useState(true);
  const [loaderFadeOut, setLoaderFadeOut] = useState(false);

  useEffect(() => {
    // Start exit fade after 800ms
    const fadeTimer = setTimeout(() => {
      setLoaderFadeOut(true);
    }, 800);
    // Remove from DOM after fade completes
    const removeTimer = setTimeout(() => {
      setShowInitialLoader(false);
    }, 1300);

    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(removeTimer);
    };
  }, []);

  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content:
        'Describe what your vehicle is experiencing—such as symptoms, strange noises, warning lights, or breakdown conditions. You can also upload a photo, video, or voice recording of your engine sound.',
      created_at: new Date().toISOString(),
    },
  ]);

  const [conversationId, setConversationId] = useState<number | null>(null);
  const [inputText, setInputText] = useState('');
  const [vehicleInfo, setVehicleInfo] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isDiagnosing, setIsDiagnosing] = useState(false);
  const [canDiagnose, setCanDiagnose] = useState(false);

  // Attached media ready to send with next message
  const [attachedMedia, setAttachedMedia] = useState<UploadResponse | null>(null);
  const [showVoiceRecorder, setShowVoiceRecorder] = useState(false);

  // Diagnosis & Booking
  const [latestDiagnosis, setLatestDiagnosis] = useState<Diagnosis | null>(null);
  const [isBookingOpen, setIsBookingOpen] = useState(false);
  const [selectedDiagnosisForBooking, setSelectedDiagnosisForBooking] = useState<Diagnosis | null>(null);

  // Error handling
  const [error, setError] = useState<ApiError | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const quickSymptoms = [
    'Hyundai Creta clicking noise when turning steering',
    'Maruti Swift engine cranks but will not start',
    'Honda City brake pedal feels soft and spongy',
    'White smoke and burning smell from exhaust'
  ];

  // Check for pre-filled query from home page
  useEffect(() => {
    const prefill = sessionStorage.getItem('initial_mechanic_query');
    if (prefill) {
      sessionStorage.removeItem('initial_mechanic_query');
      sendMessage(prefill);
    }
  }, []);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, latestDiagnosis, showVoiceRecorder]);

  const sendMessage = async (overrideText?: string, overrideMedia?: UploadResponse) => {
    const textToSend = overrideText !== undefined ? overrideText.trim() : inputText.trim();
    const mediaToSend = overrideMedia !== undefined ? overrideMedia : attachedMedia;

    if (!textToSend && !mediaToSend) return;

    setError(null);
    setInputText('');
    setAttachedMedia(null);
    setShowVoiceRecorder(false);

    // Optimistically add user message to thread
    const userMsg: Message = {
      role: 'user',
      content: textToSend || `[Uploaded ${mediaToSend?.media_type || 'Media'}]`,
      media_url: mediaToSend?.file_url,
      media_type: mediaToSend?.media_type || 'text',
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await api.sendChatMessage({
        message: textToSend,
        conversation_id: conversationId,
        media_url: mediaToSend?.file_url,
        media_type: mediaToSend?.media_type,
      });

      setConversationId(response.conversation_id);
      if (response.vehicle_info) {
        setVehicleInfo(response.vehicle_info);
      }
      setCanDiagnose(Boolean(response.can_diagnose));

      // Append assistant reply
      const assistantMsg: Message = {
        role: 'assistant',
        content: response.reply,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setIsLoading(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleRunDiagnosis = async () => {
    if (!conversationId) return;

    setError(null);
    setIsDiagnosing(true);

    try {
      const diag = await api.requestDiagnosis(conversationId);
      setLatestDiagnosis(diag);
      setCanDiagnose(false);

      // Append notification to chat
      const summaryMsg: Message = {
        role: 'assistant',
        content: `Vehicle Diagnostic Report completed based on 10,000+ automotive repair patterns. See the itemized breakdown below to dispatch a certified mobile mechanic.`,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, summaryMsg]);
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setIsDiagnosing(false);
    }
  };

  const handleOpenBooking = (diagnosis: Diagnosis) => {
    setSelectedDiagnosisForBooking(diagnosis);
    setIsBookingOpen(true);
  };

  const handleResetChat = () => {
    setConversationId(null);
    setVehicleInfo('');
    setCanDiagnose(false);
    setLatestDiagnosis(null);
    setAttachedMedia(null);
    setShowVoiceRecorder(false);
    setError(null);
    setMessages([
      {
        role: 'assistant',
        content:
          'Fresh diagnostic session started! 🔧\n\n' +
          'Tell me about your car problem, vehicle make/model, and any sounds or symptoms you noticed.',
        created_at: new Date().toISOString(),
      },
    ]);
  };

  return (
    <div className="min-h-screen bg-[#faf9f5] text-stone-900 font-sans relative flex flex-col overflow-x-hidden selection:bg-red-600 selection:text-white">
      {/* Smooth Animated Truck Loader from Uiverse.io by vinodjangid07 before opening chat bot */}
      {showInitialLoader && (
        <TruckLoaderOverlay
          message="INITIALIZING DIAGNOSTICS..."
          subMessage="Loading diagnostic engine..."
          fadeOut={loaderFadeOut}
        />
      )}

      {/* Overlay when executing AI Diagnosis */}
      {isDiagnosing && (
        <TruckLoaderOverlay
          message="GENERATING PRECISION DIAGNOSIS..."
          subMessage="Cross-referencing telemetry, acoustic samples, and OEM repair database..."
        />
      )}

      {/* Background Subtle Tech Grid Layer matching landing page */}
      <div
        className="fixed inset-0 pointer-events-none bg-grid-subtle opacity-90 z-0"
        style={{
          maskImage: 'radial-gradient(ellipse 75% 65% at 50% 30%, #000 70%, transparent 100%)',
          WebkitMaskImage: 'radial-gradient(ellipse 75% 65% at 50% 30%, #000 70%, transparent 100%)'
        }}
      />

      {/* ============================================================ */}
      {/* 1. TOP HEADER (MATCHING LANDING PAGE CAPSULE STYLE)          */}
      {/* ============================================================ */}
      <header className="relative z-20 w-full max-w-5xl mx-auto pt-3 sm:pt-4 px-2 sm:px-4 shrink-0">
        <div className="rounded-full bg-white/85 backdrop-blur-md border border-stone-200/80 px-3 sm:px-5 py-2 sm:py-2.5 flex items-center justify-between shadow-xs">
          
          {/* Left: Back button + Brand Logo */}
          <div className="flex items-center gap-2 sm:gap-3.5 shrink-0">
            <Link
              href="/"
              className="flex items-center justify-center rounded-full p-1.5 text-stone-700 hover:bg-stone-100 hover:text-black transition-colors"
              title="Back to Instant Mechanic Home"
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
          </div>

          {/* Right: Actions */}
          <div className="flex items-center gap-1.5 sm:gap-2">
            {/* Vehicle Info Badge if detected */}
            {vehicleInfo && (
              <span className="hidden sm:inline-flex items-center gap-1.5 rounded-full bg-stone-100 border border-stone-200 px-3 py-1 text-xs font-mono font-bold text-stone-900">
                <Car className="h-3.5 w-3.5 text-red-600" />
                <span>{vehicleInfo}</span>
              </span>
            )}

            {/* Run Diagnosis CTA Button (Shining Metal Effect) */}
            {canDiagnose && (
              <button
                onClick={handleRunDiagnosis}
                disabled={isDiagnosing}
                className="btn-metal-shine inline-flex items-center gap-1.5 rounded-full px-4 py-1.5 text-xs font-bold active:scale-95 disabled:opacity-50"
              >
                {isDiagnosing ? (
                  <>
                    <Loader2 className="h-3.5 w-3.5 animate-spin relative z-10" />
                    <span className="relative z-10">Analyzing...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="h-3.5 w-3.5 text-amber-400 relative z-10 animate-pulse" />
                    <span className="relative z-10">Run Diagnosis</span>
                  </>
                )}
              </button>
            )}

            {/* Reset Session */}
            <button
              onClick={handleResetChat}
              className="flex items-center justify-center rounded-full p-2 text-stone-600 hover:bg-stone-100 hover:text-black transition-colors"
              title="Start New Session"
            >
              <RotateCcw className="h-4 w-4" />
            </button>

            {/* History Link */}
            <Link
              href="/history"
              className="flex items-center justify-center rounded-full p-2 text-stone-600 hover:bg-stone-100 hover:text-black transition-colors"
              title="Diagnosis History"
            >
              <History className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </header>

      {/* ============================================================ */}
      {/* 2. CHAT WORKSPACE CONTAINER (GLASSMORPHISM CARD)             */}
      {/* ============================================================ */}
      <main className="relative z-10 flex-1 w-full max-w-5xl mx-auto px-2 sm:px-4 py-3 sm:py-5 flex flex-col min-h-0">
        <div className="rounded-3xl border border-white/80 bg-white/75 backdrop-blur-md shadow-xs flex-1 flex flex-col overflow-hidden">
          
          {/* ========================================================== */}
          {/* 3. MESSAGE STREAM                                          */}
          {/* ========================================================== */}
          <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
            
            {/* Messages list */}
            {messages.map((msg, index) => (
              <ChatMessage key={index} message={msg} />
            ))}

            {/* Quick Suggestion Chips if initial message */}
            {messages.length === 1 && (
              <div className="my-4 pt-2">
                <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-stone-500 block mb-2.5 text-left">
                  Common Issue Prompts
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-left">
                  {quickSymptoms.map((symptom, idx) => (
                    <button
                      key={idx}
                      onClick={() => sendMessage(symptom)}
                      className="rounded-xl border border-stone-200 bg-white/90 p-3 text-xs text-stone-800 hover:border-stone-400 hover:bg-stone-50 transition-colors flex items-center justify-between group shadow-2xs"
                    >
                      <span className="font-medium text-stone-900 leading-snug">{symptom}</span>
                      <ChevronRight className="h-3.5 w-3.5 text-stone-400 group-hover:text-black transition-colors shrink-0 ml-2" />
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Diagnosis Card if generated */}
            {latestDiagnosis && (
              <DiagnosisCard
                diagnosis={latestDiagnosis}
                onBookMechanic={handleOpenBooking}
              />
            )}

            {/* Loading / Evaluating Indicator */}
            {isLoading && (
              <div className="flex w-full justify-start animate-in fade-in duration-150">
                <div className="rounded-2xl rounded-tl-xs bg-white text-stone-900 border border-stone-200/90 px-4 py-3 shadow-xs text-xs flex items-center gap-2.5">
                  <Loader2 className="h-4 w-4 animate-spin text-red-600" />
                  <span className="font-mono text-stone-700 font-medium">Evaluating vehicle symptoms...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* ========================================================== */}
          {/* 4. ATTACHED MEDIA PREVIEW CHIP (IF FILE SELECTED)          */}
          {/* ========================================================== */}
          {attachedMedia && (
            <div className="border-t border-stone-200/70 bg-stone-50/90 px-4 py-2 flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs font-semibold text-stone-900">
                {attachedMedia.media_type === 'image' && <FileImage className="h-4 w-4 text-stone-700" />}
                {attachedMedia.media_type === 'audio' && <FileAudio className="h-4 w-4 text-red-600" />}
                {attachedMedia.media_type === 'video' && <FileVideo className="h-4 w-4 text-amber-600" />}
                <span className="truncate max-w-[200px] sm:max-w-xs">{attachedMedia.file_name}</span>
                <span className="text-[10px] font-mono text-stone-500">({(attachedMedia.file_size / 1024).toFixed(0)} KB)</span>
              </div>
              <button
                onClick={() => setAttachedMedia(null)}
                className="text-stone-500 hover:text-red-600 p-1 rounded-full transition-colors"
                title="Remove attachment"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          )}

          {/* ========================================================== */}
          {/* 5. BOTTOM INPUT BAR                                        */}
          {/* ========================================================== */}
          <footer className="border-t border-stone-200/80 bg-white/90 p-2.5 sm:p-3.5 backdrop-blur-sm shrink-0">
            {showVoiceRecorder ? (
              <AudioRecorder
                onAudioUploaded={(upload) => {
                  setShowVoiceRecorder(false);
                  sendMessage('[Recorded engine audio sample]', upload);
                }}
                onError={(err) => setError(err)}
                onCancel={() => setShowVoiceRecorder(false)}
              />
            ) : (
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  sendMessage();
                }}
                className="flex items-center gap-2"
              >
                {/* Media Attachment Popover */}
                <MediaUploader
                  onMediaUploaded={(upload) => setAttachedMedia(upload)}
                  onError={(err) => setError(err)}
                  disabled={isLoading}
                />

                {/* Voice Note Mic Button */}
                <button
                  type="button"
                  onClick={() => setShowVoiceRecorder(true)}
                  disabled={isLoading}
                  className="flex items-center justify-center rounded-full p-2 text-stone-600 hover:text-black hover:bg-stone-100 transition-colors active:scale-95 disabled:opacity-50"
                  title="Record Engine Noise (Acoustic Audio)"
                >
                  <Mic className="h-5 w-5" />
                </button>

                {/* Input Field */}
                <div className="flex-1 relative">
                  <input
                    ref={inputRef}
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Describe your car symptoms (e.g. grinding noise when braking, smoke from bonnet)..."
                    disabled={isLoading}
                    className="w-full rounded-full border border-stone-300 bg-white py-2.5 px-4 text-xs sm:text-sm text-stone-900 placeholder-stone-400 focus:border-stone-900 focus:outline-none shadow-2xs font-medium"
                  />
                </div>

                {/* Send Button: Shining Metal Effect */}
                <button
                  type="submit"
                  disabled={isLoading || (!inputText.trim() && !attachedMedia)}
                  className="btn-metal-shine flex h-10 w-10 shrink-0 items-center justify-center rounded-full active:scale-95 disabled:opacity-40"
                  title="Send Message"
                >
                  <Send className="h-4 w-4 text-white relative z-10" />
                </button>
              </form>
            )}
          </footer>
        </div>
      </main>

      {/* Booking Modal */}
      <BookingModal
        diagnosis={selectedDiagnosisForBooking}
        isOpen={isBookingOpen}
        onClose={() => setIsBookingOpen(false)}
      />

      {/* Floating Error Alert */}
      <ErrorAlert
        error={error}
        onDismiss={() => setError(null)}
        onRetry={() => {
          setError(null);
          sendMessage();
        }}
      />
    </div>
  );
}
