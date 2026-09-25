'use client';

import React, { useState, useEffect, useRef, Suspense } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { useSearchParams } from 'next/navigation';
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
import { Message, Diagnosis, UploadResponse, DiagnosticQuestion } from '@/lib/types';
import ChatMessage from '@/components/ChatMessage';
import DiagnosisCard from '@/components/DiagnosisCard';
import BookingModal from '@/components/BookingModal';
import MediaUploader from '@/components/MediaUploader';
import AudioRecorder from '@/components/AudioRecorder';
import ErrorAlert from '@/components/ErrorAlert';
import DiagnosticProgress from '@/components/DiagnosticProgress';
import QuickReplies from '@/components/QuickReplies';
import { TruckLoaderOverlay } from '@/components/TruckLoader';

const INITIAL_MECHANIC_GREETING =
  'Hello, I am your Instant Mechanic senior automotive diagnostic technician.\n\n' +
  'Describe what your vehicle is experiencing—whether it is an impact or collision, strange noises, ' +
  'warning lights, fluid leaks, or breakdown conditions. Tell me what happened, and I will conduct ' +
  'a step-by-step diagnostic assessment.';

function ChatWorkspace() {
  const searchParams = useSearchParams();
  const sessionQueryId = searchParams.get('id') || searchParams.get('session');

  // Animated truck loader during initial page mount
  const [showInitialLoader, setShowInitialLoader] = useState(true);
  const [loaderFadeOut, setLoaderFadeOut] = useState(false);

  useEffect(() => {
    const fadeTimer = setTimeout(() => {
      setLoaderFadeOut(true);
    }, 700);
    const removeTimer = setTimeout(() => {
      setShowInitialLoader(false);
    }, 1200);

    return () => {
      clearTimeout(fadeTimer);
      clearTimeout(removeTimer);
    };
  }, []);

  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: INITIAL_MECHANIC_GREETING,
      created_at: new Date().toISOString(),
    },
  ]);

  // Two-Call Dynamic Diagnostic Session State
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [activeQuestion, setActiveQuestion] = useState<DiagnosticQuestion | null>(null);
  const [diagnosticStatus, setDiagnosticStatus] = useState<string>('awaiting_incident');
  const [diagnosticProgress, setDiagnosticProgress] = useState<{
    answered: number;
    total: number;
    percentage: number;
  }>({
    answered: 0,
    total: 0,
    percentage: 0,
  });

  const [inputText, setInputText] = useState('');
  const [vehicleInfo, setVehicleInfo] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isDiagnosing, setIsDiagnosing] = useState(false);
  const [quickReplies, setQuickReplies] = useState<string[]>([]);

  // Media attachments
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
    'My Bugatti got hit by a road corner',
    'Hyundai Creta clicking noise when turning steering',
    'Honda City brake pedal feels soft and spongy',
    'White smoke and burning smell from exhaust',
  ];

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, latestDiagnosis, showVoiceRecorder]);

  // Restore session from query parameter or sessionStorage prefill
  useEffect(() => {
    if (sessionQueryId) {
      loadSessionById(sessionQueryId);
    } else {
      const prefill = sessionStorage.getItem('initial_mechanic_query');
      if (prefill) {
        sessionStorage.removeItem('initial_mechanic_query');
        sendMessage(prefill);
      }
    }
  }, [sessionQueryId]);

  const loadSessionById = async (id: string | number) => {
    setIsLoading(true);
    setError(null);
    try {
      const idStr = String(id);
      if (idStr.startsWith('diag_')) {
        const res = await api.getDiagnosticSession(idStr);
        if (res.success && res.data) {
          const { session, progress, message: activeMsg, question, assessment } = res.data;
          setSessionId(session.id);
          setDiagnosticStatus(session.status);
          if (progress) setDiagnosticProgress(progress);
          if (question) setActiveQuestion(question);

          if (assessment) {
            const sev = assessment.severity || 'caution';
            const mappedSev = (sev === 'critical' || sev === 'high') ? 'high' : (sev === 'low' ? 'low' : 'medium');
            const diag: Diagnosis = {
              id: res.data.diagnosis_id || 1,
              symptoms: assessment.summary,
              diagnosis: assessment.primary_concern || assessment.summary,
              severity: mappedSev,
              confidence: 'high',
              recommendation: (assessment.recommended_actions || []).join('\n• '),
              service: assessment.primary_concern || 'Automotive Inspection & Repair',
              reasoning: assessment.summary,
              source: 'gemini',
              created_at: new Date().toISOString(),
            };
            setLatestDiagnosis(diag);
            setMessages([
              {
                role: 'assistant',
                content: `Diagnostic Report: ${diag.service}`,
                diagnosis: diag,
                created_at: new Date().toISOString(),
              },
            ]);
          } else if (activeMsg) {
            setMessages([
              {
                role: 'assistant',
                content: activeMsg.content,
                created_at: new Date().toISOString(),
              },
            ]);
          }
        }
      } else {
        const conv = await api.getConversation(id);
        if (conv.vehicle_info) {
          setVehicleInfo(conv.vehicle_info);
        }
        const timeline: Message[] = [...(conv.messages || [])];
        if (conv.diagnoses && conv.diagnoses.length > 0) {
          for (const d of conv.diagnoses) {
            timeline.push({
              role: 'assistant',
              content: `Diagnostic Report: ${d.service}`,
              diagnosis: d,
              created_at: d.created_at,
            });
          }
          setLatestDiagnosis(conv.diagnoses[conv.diagnoses.length - 1]);
        }
        timeline.sort((a, b) => new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime());
        if (timeline.length > 0) {
          setMessages(timeline);
        }
      }
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

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
      if (!sessionId || diagnosticStatus === 'awaiting_incident') {
        // Start dynamic session (Gemini Call #1: Interview Planner)
        const response = await api.createDiagnosticSession({
          message: textToSend,
          vehicle_id: vehicleInfo || undefined,
        });

        if (response.success && response.data) {
          const { session, progress, message: assistantReply, question } = response.data;
          if (session && session.id) {
            setSessionId(session.id);
            setDiagnosticStatus(session.status);
            setActiveQuestion(question || null);
            if (progress) setDiagnosticProgress(progress);
            if (question?.options && question.options.length > 0) {
              setQuickReplies(question.options.map((o) => o.label));
            } else {
              setQuickReplies([]);
            }
          }
          if (assistantReply?.content) {
            const assistantMsg: Message = {
              role: 'assistant',
              content: assistantReply.content,
              created_at: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, assistantMsg]);
          }
        }
      } else {
        // Answer current question or process user inquiry (0 Gemini calls)
        const qId = activeQuestion?.id || '';
        const response = await api.submitDiagnosticAnswer(sessionId, qId, textToSend);

        if (response.success && response.data) {
          const { session, progress, message: assistantReply, question } = response.data;
          if (session) {
            setDiagnosticStatus(session.status);
          }
          if (progress) {
            setDiagnosticProgress(progress);
          }

          if (session?.status === 'ready_for_assessment') {
            setActiveQuestion(null);
            setQuickReplies(['Run Diagnostic Assessment']);
          } else if (question) {
            setActiveQuestion(question);
            if (question.options && question.options.length > 0) {
              setQuickReplies(question.options.map((o) => o.label));
            } else {
              setQuickReplies([]);
            }
          }

          if (assistantReply?.content) {
            const assistantMsg: Message = {
              role: 'assistant',
              content: assistantReply.content,
              created_at: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, assistantMsg]);
          }
        }
      }
    } catch (err) {
      setError(parseApiError(err));
    } finally {
      setIsLoading(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const handleSelectQuickReply = (reply: string) => {
    if (reply.toLowerCase().includes('run diagnostic') || reply.toLowerCase().includes('assessment')) {
      handleRunDiagnosis();
    } else {
      sendMessage(reply);
    }
  };

  const handleRunDiagnosis = async () => {
    if (!sessionId) return;

    setError(null);
    setIsDiagnosing(true);
    setQuickReplies([]);

    try {
      const response = await api.assessDiagnosticSession(sessionId);
      if (response.success && response.data && response.data.assessment) {
        const assessment = response.data.assessment;
        const sev = assessment.severity || 'caution';
        const mappedSev = (sev === 'critical' || sev === 'high') ? 'high' : (sev === 'low' ? 'low' : 'medium');

        const diag: Diagnosis = {
          id: response.data.diagnosis_id || Date.now(),
          symptoms: messages.find((m) => m.role === 'user')?.content || 'Vehicle Incident Assessment',
          diagnosis: assessment.primary_concern || assessment.summary,
          severity: mappedSev,
          confidence: 'high',
          recommendation: (assessment.recommended_actions || []).join('\n• '),
          service: assessment.primary_concern || 'Automotive Inspection & Diagnostic Service',
          reasoning: assessment.summary,
          safety_warning: assessment.safety?.message || (mappedSev === 'high' ? 'Do not drive vehicle until inspected.' : undefined),
          vehicle: vehicleInfo || 'Vehicle',
          source: 'gemini',
          created_at: new Date().toISOString(),
        };

        setLatestDiagnosis(diag);
        setDiagnosticStatus('completed');

        const diagMsg: Message = {
          role: 'assistant',
          content: `Diagnostic Report: ${diag.service}`,
          diagnosis: diag,
          created_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, diagMsg]);
      }
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
    setSessionId(null);
    setActiveQuestion(null);
    setVehicleInfo('');
    setDiagnosticStatus('awaiting_incident');
    setQuickReplies([]);
    setDiagnosticProgress({ answered: 0, total: 0, percentage: 0 });
    setLatestDiagnosis(null);
    setAttachedMedia(null);
    setShowVoiceRecorder(false);
    setError(null);
    setMessages([
      {
        role: 'assistant',
        content: INITIAL_MECHANIC_GREETING,
        created_at: new Date().toISOString(),
      },
    ]);
  };

  const canRunAssessment = diagnosticStatus === 'ready_for_assessment';

  return (
    <div className="min-h-[100dvh] h-[100dvh] max-h-[100dvh] bg-[#faf9f5] text-stone-900 font-sans relative flex flex-col overflow-hidden selection:bg-red-600 selection:text-white">
      {/* Animated Truck Loader during initial mount */}
      {showInitialLoader && (
        <TruckLoaderOverlay
          message="INITIALIZING DIAGNOSTICS..."
          subMessage="Loading AI diagnostic technician..."
          fadeOut={loaderFadeOut}
        />
      )}

      {/* Overlay when executing AI Diagnosis (Gemini Call #2) */}
      {isDiagnosing && (
        <TruckLoaderOverlay
          message="SYNTHESIZING EXPERT ASSESSMENT..."
          subMessage="Cross-referencing telemetry, impact mechanics, and OEM repair database..."
        />
      )}

      {/* Background Subtle Tech Grid Layer */}
      <div
        className="fixed inset-0 pointer-events-none bg-grid-subtle opacity-90 z-0"
        style={{
          maskImage: 'radial-gradient(ellipse 75% 65% at 50% 30%, #000 70%, transparent 100%)',
          WebkitMaskImage: 'radial-gradient(ellipse 75% 65% at 50% 30%, #000 70%, transparent 100%)',
        }}
      />

      {/* Header bar */}
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
          </div>

          {/* Right: Actions */}
          <div className="flex items-center gap-1.5 sm:gap-2">
            {vehicleInfo && (
              <span className="hidden sm:inline-flex items-center gap-1.5 rounded-full bg-stone-100 border border-stone-200 px-3 py-1 text-xs font-mono font-bold text-stone-900">
                <Car className="h-3.5 w-3.5 text-red-600" />
                <span>{vehicleInfo}</span>
              </span>
            )}

            {/* Run Assessment CTA Button */}
            {canRunAssessment && (
              <button
                onClick={handleRunDiagnosis}
                disabled={isDiagnosing}
                className="btn-metal-shine inline-flex items-center gap-1.5 rounded-full px-4 py-1.5 text-xs font-bold active:scale-95 disabled:opacity-50"
              >
                {isDiagnosing ? (
                  <>
                    <Loader2 className="h-3.5 w-3.5 animate-spin relative z-10" />
                    <span className="relative z-10">Assessing...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="h-3.5 w-3.5 text-amber-400 relative z-10 animate-pulse" />
                    <span className="relative z-10">Run Assessment</span>
                  </>
                )}
              </button>
            )}

            {/* Reset Session */}
            <button
              onClick={handleResetChat}
              className="flex items-center justify-center rounded-full p-2 text-stone-600 hover:bg-stone-100 hover:text-black transition-colors"
              title="Start New Diagnostic Session"
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

      {/* Main Workspace Container */}
      <main className="relative z-10 flex-1 w-full max-w-5xl mx-auto px-1.5 sm:px-4 py-1.5 sm:py-5 flex flex-col min-h-0 overflow-hidden">
        <div className="rounded-2xl sm:rounded-3xl border border-white/80 bg-white/75 backdrop-blur-md shadow-xs flex-1 flex flex-col overflow-hidden">
          {/* Dynamic Diagnostic Progress Telemetry */}
          {diagnosticProgress.total > 0 && (
            <div className="p-2.5 sm:p-4 pb-0 shrink-0">
              <DiagnosticProgress
                answered={diagnosticProgress.answered}
                total={diagnosticProgress.total}
                percentage={diagnosticProgress.percentage}
                status={diagnosticStatus}
                vehicleInfo={vehicleInfo}
              />
            </div>
          )}

          {/* Message Stream */}
          <div className="flex-1 overflow-y-auto p-3 sm:p-6 space-y-3 sm:space-y-4">
            {messages.map((msg, index) => (
              <div key={index} className="space-y-4">
                {msg.diagnosis ? (
                  <DiagnosisCard
                    diagnosis={msg.diagnosis}
                    onBookMechanic={handleOpenBooking}
                  />
                ) : (
                  <ChatMessage message={msg} />
                )}
              </div>
            ))}

            {/* Common issue prompts (only on initial screen) */}
            {messages.length === 1 && (
              <div className="my-4 pt-2">
                <span className="text-[11px] font-mono font-bold uppercase tracking-wider text-stone-500 block mb-2.5 text-left">
                  Sample Incident & Problem Prompts
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

            {/* Loading / Evaluating Indicator */}
            {isLoading && (
              <div className="flex w-full justify-start animate-in fade-in duration-150">
                <div className="rounded-2xl rounded-tl-xs bg-white text-stone-900 border border-stone-200/90 px-4 py-3 shadow-xs text-xs flex items-center gap-2.5">
                  <Loader2 className="h-4 w-4 animate-spin text-red-600" />
                  <span className="font-mono text-stone-700 font-medium">
                    {!sessionId ? 'Analyzing incident & planning interview...' : 'Processing answer & evaluating next question...'}
                  </span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Attached Media Preview */}
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

          {/* Bottom Input Bar */}
          <footer className="border-t border-stone-200/80 bg-white/90 p-2 sm:p-3.5 backdrop-blur-sm shrink-0">
            {quickReplies.length > 0 && !showVoiceRecorder && (
              <div className="mb-1.5 sm:mb-2 overflow-x-auto pb-0.5">
                <QuickReplies
                  replies={quickReplies}
                  onSelect={handleSelectQuickReply}
                  disabled={isLoading || isDiagnosing}
                />
              </div>
            )}
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
                className="flex items-center gap-1.5 sm:gap-2"
              >
                <MediaUploader
                  onMediaUploaded={(upload) => setAttachedMedia(upload)}
                  onError={(err) => setError(err)}
                  disabled={isLoading}
                />

                <button
                  type="button"
                  onClick={() => setShowVoiceRecorder(true)}
                  disabled={isLoading}
                  className="flex items-center justify-center rounded-full p-1.5 sm:p-2 text-stone-600 hover:text-black hover:bg-stone-100 transition-colors active:scale-95 disabled:opacity-50"
                  title="Record Engine Noise (Acoustic Audio)"
                >
                  <Mic className="h-4 w-4 sm:h-5 sm:w-5" />
                </button>

                <div className="flex-1 relative">
                  <input
                    ref={inputRef}
                    type="text"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder={
                      !sessionId
                        ? 'Describe vehicle problem or incident...'
                        : 'Type your answer or explanation...'
                    }
                    disabled={isLoading}
                    className="w-full rounded-full border border-stone-300 bg-white py-2 sm:py-2.5 px-3.5 sm:px-4 text-xs sm:text-sm text-stone-900 placeholder-stone-400 focus:border-stone-900 focus:outline-none shadow-2xs font-medium"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isLoading || (!inputText.trim() && !attachedMedia)}
                  className="btn-metal-shine flex h-9 w-9 sm:h-10 sm:w-10 shrink-0 items-center justify-center rounded-full active:scale-95 disabled:opacity-40"
                  title="Send Message"
                >
                  <Send className="h-3.5 w-3.5 sm:h-4 sm:w-4 text-white relative z-10" />
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

      {/* Error Alert */}
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

export default function ChatPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-[#faf9f5] flex flex-col items-center justify-center">
          <Loader2 className="h-7 w-7 animate-spin text-red-600 mb-2" />
          <span className="text-xs font-mono text-stone-500">Loading diagnostic workspace...</span>
        </div>
      }
    >
      <ChatWorkspace />
    </Suspense>
  );
}
