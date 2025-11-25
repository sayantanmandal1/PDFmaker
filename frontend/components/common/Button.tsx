'use client';

import React from 'react';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  className?: string;
}

export function Button({ 
  variant = 'primary', 
  size = 'md', 
  children, 
  className = '',
  disabled = false,
  ...props 
}: ButtonProps) {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-black disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none';
  
  const variantClasses = {
    primary: 'bg-gradient-to-r from-red-500 to-yellow-500 text-white hover:from-red-600 hover:to-yellow-600 hover:shadow-lg hover:shadow-red-500/50 focus:ring-red-500',
    secondary: 'bg-white/5 backdrop-blur-md border border-white/10 text-white hover:bg-white/10 hover:border-white/20 hover:shadow-lg hover:shadow-white/10 focus:ring-white/50',
    ghost: 'bg-transparent border border-white/20 text-white hover:bg-white/5 hover:border-white/30 focus:ring-white/50',
    danger: 'bg-red-600 text-white hover:bg-red-700 hover:shadow-lg hover:shadow-red-600/50 focus:ring-red-500',
  };
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };
  
  const hoverScaleClass = !disabled ? 'hover:scale-105 active:scale-95' : '';
  
  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${hoverScaleClass} ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}
