'use client';

import React, { useEffect } from 'react';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface ToastProps {
  id: string;
  message: string;
  type: ToastType;
  duration?: number;
  onClose: (id: string) => void;
}

export function Toast({ id, message, type, duration = 5000, onClose }: ToastProps) {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose(id);
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [id, duration, onClose]);

  const getIcon = () => {
    switch (type) {
      case 'success':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        );
      case 'error':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        );
      case 'warning':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        );
      case 'info':
        return (
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
    }
  };

  const getBackgroundColor = () => {
    switch (type) {
      case 'success':
        return 'bg-yellow-500/10 backdrop-blur-md border-yellow-500/30';
      case 'error':
        return 'bg-red-500/10 backdrop-blur-md border-red-500/30';
      case 'warning':
        return 'bg-yellow-500/10 backdrop-blur-md border-yellow-500/30';
      case 'info':
        return 'bg-white/5 backdrop-blur-md border-white/20';
    }
  };

  const getTextColor = () => {
    switch (type) {
      case 'success':
        return 'text-yellow-200';
      case 'error':
        return 'text-red-200';
      case 'warning':
        return 'text-yellow-200';
      case 'info':
        return 'text-gray-200';
    }
  };

  const getIconColor = () => {
    switch (type) {
      case 'success':
        return 'text-yellow-400';
      case 'error':
        return 'text-red-400';
      case 'warning':
        return 'text-yellow-400';
      case 'info':
        return 'text-blue-400';
    }
  };

  return (
    <div
      className={`flex items-start gap-3 p-4 rounded-lg border shadow-xl ${getBackgroundColor()} animate-slide-in`}
      role="alert"
      aria-live="polite"
      style={{
        animation: 'slideInRight 0.3s ease-out',
      }}
    >
      <div className={`shrink-0 mt-0.5 ${getIconColor()}`}>{getIcon()}</div>
      <div className={`flex-1 text-sm ${getTextColor()}`}>{message}</div>
      <button
        onClick={() => onClose(id)}
        className={`shrink-0 ${getTextColor()} hover:opacity-70 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-black focus:ring-white/50 rounded transition-opacity`}
        aria-label="Close notification"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}
