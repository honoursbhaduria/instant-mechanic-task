'use client';

import React, { useRef, useState } from 'react';
import { Image as ImageIcon, Music, Video, Loader2 } from 'lucide-react';
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

  const imageInputRef = useRef<HTMLInputElement>(null);
  const audioInputRef = useRef<HTMLInputElement>(null);
  const videoInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Reset input so same file can be re-selected if needed
    e.target.value = '';

    // Validate size client-side (25MB limit)
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
    <div className="flex items-center gap-1">
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
        <div className="flex items-center gap-2 rounded-lg bg-neutral-800/80 px-2.5 py-1 text-xs text-amber-400">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>Uploading {uploadProgress > 0 ? `${uploadProgress}%` : ''}</span>
        </div>
      ) : (
        <>
          {/* Image button */}
          <button
            type="button"
            onClick={() => imageInputRef.current?.click()}
            disabled={disabled}
            className="flex items-center justify-center rounded-lg p-2 text-neutral-400 transition-colors hover:bg-neutral-800 hover:text-amber-400 active:scale-95 disabled:opacity-50"
            title="Upload photo / diagram"
          >
            <ImageIcon className="h-5 w-5" />
          </button>

          {/* Audio file button */}
          <button
            type="button"
            onClick={() => audioInputRef.current?.click()}
            disabled={disabled}
            className="flex items-center justify-center rounded-lg p-2 text-neutral-400 transition-colors hover:bg-neutral-800 hover:text-amber-400 active:scale-95 disabled:opacity-50"
            title="Upload engine/brake sound clip"
          >
            <Music className="h-5 w-5" />
          </button>

          {/* Video file button */}
          <button
            type="button"
            onClick={() => videoInputRef.current?.click()}
            disabled={disabled}
            className="flex items-center justify-center rounded-lg p-2 text-neutral-400 transition-colors hover:bg-neutral-800 hover:text-amber-400 active:scale-95 disabled:opacity-50"
            title="Upload short video of issue"
          >
            <Video className="h-5 w-5" />
          </button>
        </>
      )}
    </div>
  );
}
