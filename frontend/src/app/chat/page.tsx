'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  Wrench,
  Send,
  Mic,
  RotateCcw,
  Sparkles,
  Loader2,
  Car,
  X,
  FileAudio,
  FileVideo,
  FileImage
} from 'lucide-react';
import { api, parseApiError, ApiError } from '@/lib/api';
import { Message, Diagnosis, UploadResponse } from '@/lib/types';
import ChatMessage from '@/components/ChatMessage';
import DiagnosisCard from '@/components/DiagnosisCard';
import BookingModal from '@/components/BookingModal';
import MediaUploader from '@/components/MediaUploader';
import AudioRecorder from '@/components/AudioRecorder';
import ErrorAlert from '@/components/ErrorAlert';

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content:
        'Hello! I am your Instant Mechanic senior automotive diagnostic technician. 🔧\n\n' +
        'Please describe what your car is experiencing—for example: "My Hyundai Creta makes a clicking noise when turning left", or upload an audio clip of the engine or photo of the problem.',
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
        content: `Diagnostic Report generated for your vehicle. Review the details below and book a technician when ready.`,
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
    <div className="mx-auto flex h-[calc(100vh-4rem)] w-full max-w-5xl flex-col p-2 sm:p-4">
      {/* Top Bar with Conversation Info & Reset */}
      <div className="flex items-center justify-between rounded-2xl border border-neutral-800 bg-neutral-900/90 px-4 py-3 shadow-md backdrop-blur-md mb-3">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 text-neutral-950 font-bold shadow-md">
            <Wrench className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-white">AutoMechanic AI</h2>
              <span className="inline-block h-2 w-2 rounded-full bg-emerald-500" />
            </div>
            <div className="flex items-center gap-2 text-xs text-neutral-400">
              {conversationId && (
                <span className="font-mono text-[11px] text-neutral-400">Session #{conversationId}</span>
              )}
              {vehicleInfo && (
                <span className="flex items-center gap-1 rounded bg-neutral-800 px-2 py-0.5 text-[11px] font-semibold text-amber-300">
                  <Car className="h-3 w-3" /> {vehicleInfo}
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {canDiagnose && (
            <button
              onClick={handleRunDiagnosis}
              disabled={isDiagnosing}
              className="flex items-center gap-1.5 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 px-3 py-1.5 text-xs font-bold text-neutral-950 shadow-md transition-all hover:scale-105 active:scale-95 disabled:opacity-50 animate-pulse"
            >
              {isDiagnosing ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-3.5 w-3.5" />
                  <span>Run Diagnosis</span>
                </>
              )}
            </button>
          )}

          <button
            onClick={handleResetChat}
            className="flex items-center gap-1 rounded-xl border border-neutral-800 bg-neutral-800/80 px-2.5 py-1.5 text-xs font-medium text-neutral-300 hover:bg-neutral-800 hover:text-white transition-colors"
            title="Start new conversation"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">New Chat</span>
          </button>
        </div>
      </div>

      {/* Message Stream */}
      <div className="flex-1 overflow-y-auto rounded-2xl border border-neutral-800/80 bg-neutral-950/60 p-4 sm:p-6 space-y-4 shadow-inner">
        {messages.map((msg, index) => (
          <ChatMessage key={index} message={msg} />
        ))}

        {/* Diagnosis Card if generated */}
        {latestDiagnosis && (
          <DiagnosisCard
            diagnosis={latestDiagnosis}
            onBookMechanic={handleOpenBooking}
          />
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex items-center gap-2 text-xs text-neutral-400 p-2">
            <Loader2 className="h-4 w-4 animate-spin text-amber-500" />
            <span>Technician is evaluating symptoms...</span>
          </div>
        )}

        {/* Prompt to diagnose if ready */}
        {canDiagnose && !latestDiagnosis && !isLoading && (
          <div className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-center space-y-2">
            <p className="text-xs sm:text-sm font-semibold text-amber-300">
              Sufficient details gathered! You can now generate the mechanical diagnosis.
            </p>
            <button
              onClick={handleRunDiagnosis}
              disabled={isDiagnosing}
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 px-5 py-2 text-xs font-bold text-neutral-950 shadow-md transition-transform hover:scale-105 active:scale-95"
            >
              {isDiagnosing ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Generating Diagnostic Report...</span>
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  <span>Generate Mechanical Diagnosis 🔧</span>
                </>
              )}
            </button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Media Attachment Preview Chip */}
      {attachedMedia && (
        <div className="mt-2 flex items-center justify-between rounded-xl border border-amber-500/30 bg-neutral-900/90 px-3.5 py-2 text-xs text-amber-300 shadow-md">
          <div className="flex items-center gap-2 truncate">
            {attachedMedia.media_type === 'image' && <FileImage className="h-4 w-4 shrink-0" />}
            {attachedMedia.media_type === 'audio' && <FileAudio className="h-4 w-4 shrink-0" />}
            {attachedMedia.media_type === 'video' && <FileVideo className="h-4 w-4 shrink-0" />}
            <span className="truncate">{attachedMedia.file_name}</span>
            <span className="text-[10px] text-neutral-500">
              ({(attachedMedia.file_size / 1024).toFixed(0)} KB)
            </span>
          </div>

          <button
            onClick={() => setAttachedMedia(null)}
            className="rounded p-1 text-neutral-400 hover:text-white"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        </div>
      )}

      {/* Voice Recorder Overlay or Input Bar */}
      <div className="mt-3">
        {showVoiceRecorder ? (
          <AudioRecorder
            onAudioUploaded={(upload) => {
              setShowVoiceRecorder(false);
              sendMessage('[Recorded voice sound sample]', upload);
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
            className="flex items-center gap-2 rounded-2xl border border-neutral-800 bg-neutral-900/90 p-2 shadow-xl backdrop-blur-md"
          >
            {/* Media Uploaders (Image, Audio, Video) */}
            <MediaUploader
              onMediaUploaded={(upload) => setAttachedMedia(upload)}
              onError={(err) => setError(err)}
              disabled={isLoading}
            />

            {/* Voice Recorder trigger */}
            <button
              type="button"
              onClick={() => setShowVoiceRecorder(true)}
              disabled={isLoading}
              className="flex items-center justify-center rounded-lg p-2 text-neutral-400 transition-colors hover:bg-neutral-800 hover:text-rose-400 active:scale-95 disabled:opacity-50"
              title="Record sound using microphone"
            >
              <Mic className="h-5 w-5" />
            </button>

            {/* Message input */}
            <input
              ref={inputRef}
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Type your car problem (e.g. clicking noise while turning left)..."
              disabled={isLoading}
              className="flex-1 bg-transparent px-2 text-sm text-white placeholder-neutral-500 focus:outline-none disabled:opacity-50"
            />

            {/* Send button */}
            <button
              type="submit"
              disabled={isLoading || (!inputText.trim() && !attachedMedia)}
              className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 text-neutral-950 font-bold shadow-md transition-all hover:opacity-95 active:scale-95 disabled:opacity-40"
              title="Send message"
            >
              <Send className="h-4 w-4" />
            </button>
          </form>
        )}
      </div>

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
