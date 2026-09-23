'use client';

import React from 'react';
import { Volume2, FileVideo, User } from 'lucide-react';
import { Message } from '@/lib/types';

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  const timeString = message.created_at
    ? new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    : '';

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} animate-in fade-in duration-150`}>
      {/* Message Content Bubble */}
      <div
        className={`relative max-w-[88%] sm:max-w-[78%] rounded-2xl p-4 sm:p-5 shadow-xs text-sm transition-all ${
          isUser
            ? 'rounded-tr-xs bg-stone-900 text-white border border-stone-800'
            : 'rounded-tl-xs bg-white/95 text-stone-900 border border-stone-200/90 backdrop-blur-sm'
        }`}
      >
        {/* Sender Header for user */}
        {isUser && (
          <div className="mb-1.5 flex items-center gap-1.5 text-[11px] font-mono font-semibold text-stone-400">
            <User className="h-3 w-3 text-stone-400" />
            <span>You</span>
          </div>
        )}

        {/* Media rendering */}
        {message.media_url && (
          <div className="mb-3 overflow-hidden rounded-xl border border-stone-200/80 bg-stone-50">
            {message.media_type === 'image' && (
              /* eslint-disable-next-line @next/next/no-img-element */
              <img
                src={message.media_url}
                alt="Uploaded car diagnostic image"
                className="max-h-64 w-auto rounded-lg object-contain mx-auto"
              />
            )}

            {message.media_type === 'audio' && (
              <div className="p-3 bg-white">
                <div className="flex items-center gap-2 mb-1.5 text-xs font-mono font-bold text-red-600">
                  <Volume2 className="h-4 w-4" />
                  <span>Acoustic Audio Waveform</span>
                </div>
                <audio controls src={message.media_url} className="w-full h-8" />
              </div>
            )}

            {message.media_type === 'video' && (
              <div className="p-2 bg-white">
                <div className="flex items-center gap-2 mb-1.5 text-xs font-mono font-bold text-red-600">
                  <FileVideo className="h-4 w-4" />
                  <span>Diagnostic Video Clip</span>
                </div>
                <video controls src={message.media_url} className="max-h-60 w-full rounded-lg" />
              </div>
            )}
          </div>
        )}

        {/* Text content */}
        <p className={`whitespace-pre-line leading-relaxed font-normal ${isUser ? 'text-stone-100' : 'text-stone-900'}`}>
          {message.content}
        </p>

        {/* Footer: Timestamp */}
        <div className={`mt-2 flex items-center justify-end select-none font-mono text-[10px] ${isUser ? 'text-stone-400' : 'text-stone-400'}`}>
          <span>{timeString}</span>
        </div>
      </div>
    </div>
  );
}
