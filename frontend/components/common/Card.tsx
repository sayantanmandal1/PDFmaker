'use client';

import React from 'react';

export interface CardProps {
  variant?: 'default' | 'glass' | 'strong-glass' | 'gradient-header';
  hover?: boolean;
  children: React.ReactNode;
  className?: string;
  header?: React.ReactNode;
  footer?: React.ReactNode;
}

export function Card({ 
  variant = 'default', 
  hover = false,
  children, 
  className = '',
  header,
  footer,
}: CardProps) {
  const baseClasses = 'rounded-lg transition-all duration-200';
  
  const variantClasses = {
    default: 'bg-white/5 backdrop-blur-md border border-white/10',
    glass: 'bg-white/5 backdrop-blur-md border border-white/10',
    'strong-glass': 'bg-white/8 backdrop-blur-lg border border-white/15',
    'gradient-header': 'bg-white/5 backdrop-blur-md border border-white/10 overflow-hidden',
  };
  
  const hoverClasses = hover 
    ? 'hover:scale-[1.02] hover:shadow-xl hover:shadow-red-500/10 hover:border-white/20 cursor-pointer' 
    : '';
  
  const shadowClasses = 'shadow-lg shadow-black/20';
  
  if (variant === 'gradient-header') {
    return (
      <div className={`${baseClasses} ${variantClasses[variant]} ${hoverClasses} ${shadowClasses} ${className}`}>
        {header && (
          <div className="bg-gradient-to-r from-red-500 to-yellow-500 px-6 py-4">
            {header}
          </div>
        )}
        <div className="p-6">
          {children}
        </div>
        {footer && (
          <div className="px-6 py-4 border-t border-white/10 bg-white/5">
            {footer}
          </div>
        )}
      </div>
    );
  }
  
  return (
    <div className={`${baseClasses} ${variantClasses[variant]} ${hoverClasses} ${shadowClasses} ${className}`}>
      {header && (
        <div className="px-6 py-4 border-b border-white/10">
          {header}
        </div>
      )}
      <div className="p-6">
        {children}
      </div>
      {footer && (
        <div className="px-6 py-4 border-t border-white/10 bg-white/5">
          {footer}
        </div>
      )}
    </div>
  );
}

export interface CardHeaderProps {
  children: React.ReactNode;
  className?: string;
}

export function CardHeader({ children, className = '' }: CardHeaderProps) {
  return (
    <div className={`text-lg font-semibold text-white ${className}`}>
      {children}
    </div>
  );
}

export interface CardBodyProps {
  children: React.ReactNode;
  className?: string;
}

export function CardBody({ children, className = '' }: CardBodyProps) {
  return (
    <div className={`text-gray-300 ${className}`}>
      {children}
    </div>
  );
}

export interface CardFooterProps {
  children: React.ReactNode;
  className?: string;
}

export function CardFooter({ children, className = '' }: CardFooterProps) {
  return (
    <div className={`text-sm text-gray-400 ${className}`}>
      {children}
    </div>
  );
}
