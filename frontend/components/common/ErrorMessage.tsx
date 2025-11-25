'use client';

import React from 'react';

interface ErrorMessageProps {
  message: string;
  title?: string;
  onRetry?: () => void;
  className?: string;
}

export function ErrorMessage({ message, title = 'Error', onRetry, className = '' }: ErrorMessageProps) {
  return (
    <div className={`bg-red-500/10 backdrop-blur-md border border-red-500/30 rounded-lg p-4 sm:p-6 ${className}`} role="alert">
      <div className="flex items-start">
        <div className="shrink-0">
          <svg
            className="w-5 h-5 text-red-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-red-200">{title}</h3>
          <p className="mt-1 text-sm text-red-300">{message}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-3 text-sm font-medium text-red-400 hover:text-red-300 focus:outline-none focus:underline transition-colors"
            >
              Try again
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

interface InlineErrorProps {
  message: string;
  className?: string;
}

export function InlineError({ message, className = '' }: InlineErrorProps) {
  return (
    <div className={`flex items-center gap-2 text-red-400 text-sm ${className}`} role="alert">
      <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <span>{message}</span>
    </div>
  );
}

interface EmptyStateProps {
  title: string;
  message: string;
  icon?: React.ReactNode;
  action?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
}

export function EmptyState({ title, message, icon, action, className = '' }: EmptyStateProps) {
  return (
    <div className={`text-center py-12 px-4 ${className}`}>
      {icon ? (
        <div className="mx-auto w-20 h-20 sm:w-24 sm:h-24 mb-4">{icon}</div>
      ) : (
        <div className="mx-auto w-20 h-20 sm:w-24 sm:h-24 bg-white/5 backdrop-blur-md border border-white/10 rounded-full flex items-center justify-center mb-4">
          <svg className="w-10 h-10 sm:w-12 sm:h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
        </div>
      )}
      <h3 className="text-base sm:text-lg font-medium text-white mb-2">{title}</h3>
      <p className="text-sm sm:text-base text-gray-400 mb-6 max-w-md mx-auto">{message}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-gradient-to-r from-red-500 to-yellow-500 hover:from-red-600 hover:to-yellow-600 hover:shadow-lg hover:shadow-red-500/50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-black focus:ring-red-500 transition-all duration-200"
        >
          {action.label}
        </button>
      )}
    </div>
  );
}
