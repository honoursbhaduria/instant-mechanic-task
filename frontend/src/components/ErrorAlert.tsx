'use client';

import React from 'react';
import { AlertTriangle, X, RefreshCw } from 'lucide-react';
import { ApiError } from '@/lib/api';

interface ErrorAlertProps {
  error: ApiError | null;
  onDismiss: () => void;
  onRetry?: () => void;
}

export default function ErrorAlert({ error, onDismiss, onRetry }: ErrorAlertProps) {
  if (!error) return null;

  const getStatusBadge = (status: number) => {
    switch (status) {
      case 400:
        return 'HTTP 400: Invalid Request';
      case 404:
        return 'HTTP 404: Not Found';
      case 413:
        return 'HTTP 413: File Too Large';
      case 415:
        return 'HTTP 415: Unsupported Format';
      case 429:
        return 'HTTP 429: Rate Limit / Busy';
      case 500:
        return 'HTTP 500: Server Error';
      default:
        return `HTTP ${status}: Error`;
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 max-w-md animate-in slide-in-from-bottom-4 duration-300">
      <div className="rounded-xl border border-rose-500/30 bg-neutral-900/95 p-4 shadow-2xl backdrop-blur-md">
        <div className="flex items-start gap-3">
          <div className="rounded-full bg-rose-500/20 p-2 text-rose-400">
            <AlertTriangle className="h-5 w-5" />
          </div>

          <div className="flex-1">
            <div className="flex items-center gap-2">
              <span className="rounded bg-rose-500/20 px-2 py-0.5 text-[11px] font-bold text-rose-300">
                {getStatusBadge(error.status)}
              </span>
            </div>
            <p className="mt-1 text-sm font-medium text-neutral-200">
              {error.message}
            </p>
            {Boolean(error.details && typeof error.details === 'object') && (
              <p className="mt-1 text-xs text-neutral-400 font-mono">
                {JSON.stringify(error.details)}
              </p>
            )}

            <div className="mt-3 flex items-center gap-2">
              {onRetry && (
                <button
                  onClick={onRetry}
                  className="flex items-center gap-1.5 rounded-md bg-rose-500/20 px-2.5 py-1 text-xs font-semibold text-rose-300 hover:bg-rose-500/30 transition-colors"
                >
                  <RefreshCw className="h-3.5 w-3.5" />
                  Try Again
                </button>
              )}
              <button
                onClick={onDismiss}
                className="rounded-md px-2.5 py-1 text-xs font-medium text-neutral-400 hover:bg-neutral-800 transition-colors"
              >
                Dismiss
              </button>
            </div>
          </div>

          <button
            onClick={onDismiss}
            className="text-neutral-500 hover:text-neutral-300 p-1"
            title="Dismiss error"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
