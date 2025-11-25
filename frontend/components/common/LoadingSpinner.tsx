'use client';

import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  className?: string;
  label?: string;
}

export function LoadingSpinner({ size = 'md', className = '', label = 'Loading...' }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-8 h-8 border-3',
    lg: 'w-12 h-12 border-4',
    xl: 'w-16 h-16 border-4',
  };

  return (
    <div className={`flex items-center justify-center ${className}`} role="status" aria-label={label}>
      <div
        className={`${sizeClasses[size]} border-transparent border-t-red-500 border-r-yellow-500 rounded-full animate-spin`}
        style={{
          background: 'conic-gradient(from 0deg, #ef4444, #f59e0b, transparent)',
          WebkitMask: 'radial-gradient(farthest-side, transparent calc(100% - 3px), white 0)',
          mask: 'radial-gradient(farthest-side, transparent calc(100% - 3px), white 0)',
        }}
        aria-hidden="true"
      />
      <span className="sr-only">{label}</span>
    </div>
  );
}

interface LoadingOverlayProps {
  message?: string;
}

export function LoadingOverlay({ message = 'Loading...' }: LoadingOverlayProps) {
  return (
    <div
      className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50"
      role="status"
      aria-label={message}
    >
      <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-lg p-6 sm:p-8 shadow-xl max-w-sm w-full mx-4">
        <div className="flex flex-col items-center">
          <LoadingSpinner size="lg" label={message} />
          <p className="mt-4 text-white text-center">{message}</p>
        </div>
      </div>
    </div>
  );
}

interface LoadingStateProps {
  message?: string;
  className?: string;
}

export function LoadingState({ message = 'Loading...', className = '' }: LoadingStateProps) {
  return (
    <div className={`flex flex-col items-center justify-center py-12 ${className}`} role="status" aria-label={message}>
      <LoadingSpinner size="lg" label={message} />
      <p className="mt-4 text-gray-300">{message}</p>
    </div>
  );
}
