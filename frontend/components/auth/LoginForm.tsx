'use client';

import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { LoginCredentials } from '@/types';
import { Eye, EyeOff } from 'lucide-react';

interface LoginFormProps {
  onSuccess?: () => void;
  onSwitchToRegister?: () => void;
}

export function LoginForm({ onSuccess, onSwitchToRegister }: LoginFormProps) {
  const { login, isLoading, error, clearError } = useAuth();
  const [formData, setFormData] = useState<LoginCredentials>({
    email: '',
    password: '',
  });
  const [formErrors, setFormErrors] = useState<Partial<LoginCredentials>>({});
  const [showPassword, setShowPassword] = useState(false);

  const validateForm = (): boolean => {
    const errors: Partial<LoginCredentials> = {};

    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'Email is invalid';
    }

    if (!formData.password) {
      errors.password = 'Password is required';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    try {
      await login(formData);
      onSuccess?.();
    } catch (error) {
      // Error is handled by the AuthContext
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear field error when user starts typing
    if (formErrors[name as keyof LoginCredentials]) {
      setFormErrors(prev => ({ ...prev, [name]: undefined }));
    }
    
    // Clear auth error when user starts typing
    if (error) {
      clearError();
    }
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <form onSubmit={handleSubmit} className="space-y-5" aria-label="Login form">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-white text-center mb-6">
            Sign In
          </h2>
        </div>

        {error && (
          <div 
            className="bg-red-500/10 backdrop-blur-sm border border-red-500/30 text-red-400 px-4 py-3 rounded-lg text-sm flex items-center gap-2"
            role="alert"
            aria-live="polite"
          >
            <svg className="w-5 h-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
            Email Address
          </label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            value={formData.email}
            onChange={handleInputChange}
            className={`w-full px-4 py-2.5 bg-black/40 border rounded-lg text-white placeholder-gray-500 transition-all duration-200 focus:outline-none focus:bg-white/5 focus:backdrop-blur-md focus:border-transparent focus:ring-2 focus:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed ${
              formErrors.email 
                ? 'border-red-500 focus:ring-red-500 focus:shadow-red-500/20' 
                : 'border-white/20 focus:ring-red-500/50 focus:shadow-red-500/20'
            }`}
            placeholder="Enter your email"
            aria-invalid={!!formErrors.email}
            aria-describedby={formErrors.email ? 'email-error' : undefined}
          />
          {formErrors.email && (
            <p id="email-error" className="mt-2 text-sm text-red-400 flex items-center gap-1" role="alert">
              <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {formErrors.email}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
            Password
          </label>
          <div className="relative">
            <input
              id="password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              autoComplete="current-password"
              required
              value={formData.password}
              onChange={handleInputChange}
              className={`w-full px-4 py-2.5 pr-12 bg-black/40 border rounded-lg text-white placeholder-gray-500 transition-all duration-200 focus:outline-none focus:bg-white/5 focus:backdrop-blur-md focus:border-transparent focus:ring-2 focus:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed ${
                formErrors.password 
                  ? 'border-red-500 focus:ring-red-500 focus:shadow-red-500/20' 
                  : 'border-white/20 focus:ring-red-500/50 focus:shadow-red-500/20'
              }`}
              style={{ WebkitTextSecurity: showPassword ? 'none' : 'disc' } as React.CSSProperties}
              placeholder="Enter your password"
              aria-invalid={!!formErrors.password}
              aria-describedby={formErrors.password ? 'password-error' : undefined}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-white focus:outline-none transition-all duration-200"
              aria-label={showPassword ? 'Hide password' : 'Show password'}
            >
              {showPassword ? (
                <EyeOff className="h-5 w-5 transition-transform duration-200 hover:scale-110" />
              ) : (
                <Eye className="h-5 w-5 transition-transform duration-200 hover:scale-110" />
              )}
            </button>
          </div>
          {formErrors.password && (
            <p id="password-error" className="mt-2 text-sm text-red-400 flex items-center gap-1" role="alert">
              <svg className="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {formErrors.password}
            </p>
          )}
        </div>

        <div>
          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center py-3 px-4 rounded-lg text-base font-medium text-white bg-gradient-to-r from-red-500 to-yellow-500 hover:from-red-600 hover:to-yellow-600 hover:shadow-lg hover:shadow-red-500/50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-black focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:scale-105 active:scale-95 disabled:transform-none"
            aria-busy={isLoading}
          >
            {isLoading ? 'Signing In...' : 'Sign In'}
          </button>
        </div>

        {onSwitchToRegister && (
          <div className="text-center">
            <p className="text-sm text-gray-400">
              Don't have an account?{' '}
              <button
                type="button"
                onClick={onSwitchToRegister}
                className="font-medium text-transparent bg-gradient-to-r from-red-500 to-yellow-500 bg-clip-text hover:from-red-400 hover:to-yellow-400 focus:outline-none focus:underline transition-all duration-200"
                aria-label="Switch to registration form"
              >
                Sign up
              </button>
            </p>
          </div>
        )}
      </form>
    </div>
  );
}