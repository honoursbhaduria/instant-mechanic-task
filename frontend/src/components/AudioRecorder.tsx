'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Trash2, Send, Loader2 } from 'lucide-react';
import { api, parseApiError, ApiError } from '@/lib/api';
import { UploadResponse } from '@/lib/types';

interface AudioRecorderProps {
  onAudioUploaded: (upload: UploadResponse) => void;
  onError: (err: ApiError) => void;
  onCancel: () => void;
}

export default function AudioRecorder({ onAudioUploaded, onError, onCancel }: AudioRecorderProps) {
  const [duration, setDuration] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const cleanup = useCallback(() => {
    if (timerRef.current) clearInterval(timerRef.current);
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
  }, []);

  const startRecording = useCallback(async () => {
    audioChunksRef.current = [];
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop());

        if (audioChunksRef.current.length === 0) return;

        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const audioFile = new File([audioBlob], `mechanic_voice_${Date.now()}.webm`, {
          type: 'audio/webm',
        });

        setIsUploading(true);
        try {
          const res = await api.uploadMedia(audioFile);
          onAudioUploaded(res);
        } catch (err) {
          onError(parseApiError(err));
          onCancel();
        } finally {
          setIsUploading(false);
        }
      };

      mediaRecorder.start();
      setDuration(0);

      timerRef.current = setInterval(() => {
        setDuration((prev) => prev + 1);
      }, 1000);
    } catch {
      onError({
        status: 400,
        message: 'Could not access microphone. Please ensure microphone permissions are granted.',
      });
      onCancel();
    }
  }, [onAudioUploaded, onError, onCancel]);

  useEffect(() => {
    startRecording();
    return () => {
      cleanup();
    };
  }, [startRecording, cleanup]);

  const stopAndSend = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      if (timerRef.current) clearInterval(timerRef.current);
      mediaRecorderRef.current.stop();
    }
  };

  const cancelRecording = () => {
    cleanup();
    audioChunksRef.current = [];
    onCancel();
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex items-center justify-between gap-3 rounded-xl border border-rose-500/30 bg-neutral-900/90 px-4 py-2.5 shadow-lg backdrop-blur-md">
      <div className="flex items-center gap-3">
        <div className="relative flex h-3 w-3">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-rose-400 opacity-75" />
          <span className="relative inline-flex h-3 w-3 rounded-full bg-rose-500" />
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-rose-300">
            {isUploading ? 'Uploading Audio...' : 'Recording Sound...'}
          </span>
          <span className="font-mono text-xs text-neutral-400">{formatDuration(duration)}</span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        {isUploading ? (
          <div className="flex items-center gap-2 text-xs text-amber-400">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Analyzing...</span>
          </div>
        ) : (
          <>
            <button
              onClick={cancelRecording}
              className="rounded-lg p-1.5 text-neutral-400 hover:bg-neutral-800 hover:text-neutral-200 transition-colors"
              title="Cancel recording"
            >
              <Trash2 className="h-4 w-4" />
            </button>
            <button
              onClick={stopAndSend}
              className="flex items-center gap-1.5 rounded-lg bg-rose-600 px-3 py-1.5 text-xs font-semibold text-white shadow-md hover:bg-rose-500 transition-colors"
              title="Send audio recording"
            >
              <Send className="h-3.5 w-3.5" />
              <span>Send Audio</span>
            </button>
          </>
        )}
      </div>
    </div>
  );
}
