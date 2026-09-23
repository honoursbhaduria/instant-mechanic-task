'use client';

import React, { useRef, useState } from 'react';
import { Paperclip, Image as ImageIcon, Music, Video, Loader2 } from 'lucide-react';
import { api, parseApiError, ApiError } from '@/lib/api';
import { UploadResponse } from '@/lib/types';

interface MediaUploaderProps {
  onMediaUploaded: (upload: UploadResponse) => void;
  onError: (err: ApiError) => void;
  disabled?: boolean;
}

export default function MediaUploader({ onMediaUploaded, onError, disabled = false }: MediaUploaderProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [menuOpen, setMenuOpen] = useState(false);

  const imageInputRef = useRef<HTMLInputElement>(null);
  const audioInputRef = useRef<HTMLInputElement>(null);
  const videoInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    e.target.value = '';
    setMenuOpen(false);

    if (file.size > 25 * 1024 * 1024) {
      onError({
        status: 413,
        message: `File "${file.name}" is too large (${(file.size / (1024 * 1024)).toFixed(1)}MB). Maximum allowed size is 25MB.`,
      });
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      const upload = await api.uploadMedia(file, (progressEvent) => {
        if (progressEvent.total) {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percent);
        }
      });
      onMediaUploaded(upload);
    } catch (err) {
      onError(parseApiError(err));
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  return (
    <div className="relative flex items-center">
      {/* Hidden file inputs */}
      <input
        ref={imageInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp,image/gif"
        onChange={handleFileChange}
        className="hidden"
      />
      <input
        ref={audioInputRef}
        type="file"
        accept="audio/mpeg,audio/wav,audio/ogg,audio/m4a,audio/webm"
        onChange={handleFileChange}
        className="hidden"
      />
      <input
        ref={videoInputRef}
        type="file"
        accept="video/mp4,video/webm,video/quicktime"
        onChange={handleFileChange}
        className="hidden"
      />

      {isUploading ? (
        <div className="flex items-center gap-1.5 rounded-full bg-stone-100 px-3 py-1 text-xs text-stone-900 font-mono font-bold border border-stone-200">
          <Loader2 className="h-3.5 w-3.5 animate-spin text-red-600" />
          <span>Uploading {uploadProgress > 0 ? `${uploadProgress}%` : ''}</span>
        </div>
      ) : (
        <div className="flex items-center gap-0.5">
          {/* Paperclip attachment button */}
          <button
            type="button"
            onClick={() => setMenuOpen(!menuOpen)}
            disabled={disabled}
            className="flex items-center justify-center rounded-full p-2 text-stone-700 hover:text-black hover:bg-stone-100 transition-colors active:scale-95 disabled:opacity-50"
            title="Attach Media (Image, Audio, Video)"
          >
            <Paperclip className="h-5 w-5" />
          </button>

          {/* Quick Popover Menu */}
          {menuOpen && (
            <div className="absolute bottom-full left-0 mb-3 flex flex-col gap-1 rounded-2xl bg-white border border-stone-200 p-2 shadow-lg z-30 animate-in fade-in slide-in-from-bottom-2 duration-150 w-44">
              <button
                type="button"
                onClick={() => {
                  setMenuOpen(false);
                  imageInputRef.current?.click();
                }}
                className="flex items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-semibold text-stone-900 hover:bg-stone-100 transition-colors text-left"
              >
                <div className="flex h-7 w-7 items-center justify-center rounded-full bg-stone-100 text-stone-800 border border-stone-200">
                  <ImageIcon className="h-4 w-4" />
                </div>
                <span>Photos & Docs</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  setMenuOpen(false);
                  audioInputRef.current?.click();
                }}
                className="flex items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-semibold text-stone-900 hover:bg-stone-100 transition-colors text-left"
              >
                <div className="flex h-7 w-7 items-center justify-center rounded-full bg-red-50 text-red-600 border border-red-200">
                  <Music className="h-4 w-4" />
                </div>
                <span>Engine Audio</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  setMenuOpen(false);
                  videoInputRef.current?.click();
                }}
                className="flex items-center gap-2.5 rounded-xl px-3 py-2 text-xs font-semibold text-stone-900 hover:bg-stone-100 transition-colors text-left"
              >
                <div className="flex h-7 w-7 items-center justify-center rounded-full bg-amber-50 text-amber-700 border border-amber-200">
                  <Video className="h-4 w-4" />
                </div>
                <span>Issue Video</span>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
