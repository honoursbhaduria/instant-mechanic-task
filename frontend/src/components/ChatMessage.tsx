'use client';

import React from 'react';
import { User, Wrench, Volume2, FileVideo } from 'lucide-react';
import { Message } from '@/lib/types';

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex w-full gap-3 ${isUser ? 'justify-end' : 'justify-start'} animate-in fade-in duration-200`}>
      {/* Assistant Avatar */}
      {!isUser && (
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-amber-500 to-orange-500 text-neutral-950 shadow-md">
          <Wrench className="h-5 w-5" />
        </div>
      )}

      {/* Message Content Bubble */}
      <div
        className={`max-w-[85%] sm:max-w-[75%] rounded-2xl p-4 shadow-md ${
          isUser
            ? 'rounded-tr-none bg-amber-500 text-neutral-950 font-medium'
            : 'rounded-tl-none border border-neutral-800 bg-neutral-900 text-neutral-200'
        }`}
      >
        {!isUser && (
          <div className="mb-1 flex items-center gap-1.5 text-[11px] font-semibold tracking-wider uppercase text-amber-400">
            <span>Instant Mechanic</span>
            <span className="rounded bg-amber-500/20 px-1 py-0.2 text-[9px] text-amber-300">
              Senior Tech
            </span>
          </div>
        )}

        {/* Media rendering */}
        {message.media_url && (
          <div className="mb-2.5 overflow-hidden rounded-xl border border-neutral-700/50 bg-black/40">
            {message.media_type === 'image' && (
              <img
                src={message.media_url}
                alt="Uploaded car image"
                className="max-h-60 w-auto rounded-lg object-contain"
              />
            )}

            {message.media_type === 'audio' && (
              <div className="p-3">
                <div className="flex items-center gap-2 mb-1.5 text-xs font-semibold text-neutral-300">
                  <Volume2 className="h-4 w-4 text-amber-400" />
                  <span>Audio Recording / Sound Sample</span>
                </div>
                <audio controls src={message.media_url} className="w-full h-8" />
              </div>
            )}

            {message.media_type === 'video' && (
              <div className="p-2">
                <div className="flex items-center gap-2 mb-1.5 text-xs font-semibold text-neutral-300">
                  <FileVideo className="h-4 w-4 text-amber-400" />
                  <span>Video Clip</span>
                </div>
                <video controls src={message.media_url} className="max-h-60 w-full rounded-lg" />
              </div>
            )}
          </div>
        )}

        {/* Text content */}
        <p className="whitespace-pre-line text-sm leading-relaxed">
          {message.content}
        </p>

        {/* Timestamp */}
        {message.created_at && (
          <div
            className={`mt-1.5 text-[10px] ${
              isUser ? 'text-neutral-900/70 text-right' : 'text-neutral-500 text-left'
            }`}
          >
            {new Date(message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        )}
      </div>

      {/* User Avatar */}
      {isUser && (
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-neutral-800 text-neutral-300 border border-neutral-700">
          <User className="h-5 w-5" />
        </div>
      )}
    </div>
  );
}
