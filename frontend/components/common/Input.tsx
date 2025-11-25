'use client';

import React from 'react';

export interface InputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
  className?: string;
}

export function Input({ 
  label, 
  error, 
  icon, 
  className = '',
  id,
  ...props 
}: InputProps) {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
  
  return (
    <div className={`w-full ${className}`}>
      {label && (
        <label 
          htmlFor={inputId} 
          className="block text-sm font-medium text-gray-300 mb-2"
        >
          {label}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
            {icon}
          </div>
        )}
        <input
          id={inputId}
          className={`
            w-full px-4 py-2.5 
            bg-black/40 
            border border-white/20 
            rounded-lg 
            text-white placeholder-gray-500
            transition-all duration-200
            focus:outline-none 
            focus:bg-white/5 
            focus:backdrop-blur-md
            focus:border-transparent
            focus:ring-2 
            focus:ring-red-500/50 
            focus:shadow-lg 
            focus:shadow-red-500/20
            disabled:opacity-50 
            disabled:cursor-not-allowed
            ${icon ? 'pl-10' : ''}
            ${error ? 'border-red-500 focus:ring-red-500' : ''}
          `}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={error ? `${inputId}-error` : undefined}
          {...props}
        />
      </div>
      {error && (
        <p 
          id={`${inputId}-error`}
          className="mt-2 text-sm text-red-400 flex items-center gap-1"
          role="alert"
        >
          <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {error}
        </p>
      )}
    </div>
  );
}

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  className?: string;
}

export function Textarea({ 
  label, 
  error, 
  className = '',
  id,
  ...props 
}: TextareaProps) {
  const textareaId = id || `textarea-${Math.random().toString(36).substr(2, 9)}`;
  
  return (
    <div className={`w-full ${className}`}>
      {label && (
        <label 
          htmlFor={textareaId} 
          className="block text-sm font-medium text-gray-300 mb-2"
        >
          {label}
        </label>
      )}
      <textarea
        id={textareaId}
        className={`
          w-full px-4 py-2.5 
          bg-black/40 
          border border-white/20 
          rounded-lg 
          text-white placeholder-gray-500
          transition-all duration-200
          focus:outline-none 
          focus:bg-white/5 
          focus:backdrop-blur-md
          focus:border-transparent
          focus:ring-2 
          focus:ring-red-500/50 
          focus:shadow-lg 
          focus:shadow-red-500/20
          disabled:opacity-50 
          disabled:cursor-not-allowed
          resize-none
          ${error ? 'border-red-500 focus:ring-red-500' : ''}
        `}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={error ? `${textareaId}-error` : undefined}
        {...props}
      />
      {error && (
        <p 
          id={`${textareaId}-error`}
          className="mt-2 text-sm text-red-400 flex items-center gap-1"
          role="alert"
        >
          <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {error}
        </p>
      )}
    </div>
  );
}
