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
    <div className="w-full max-w-md mx-auto px-4 sm:px-6">
      <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6" aria-label="Login form">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900 text-center mb-4 sm:mb-6">
            Sign In
          </h2>
        </div>

        {error && (
          <div 
            className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 sm:px-4 sm:py-3 rounded-md text-sm sm:text-base"
            role="alert"
            aria-live="polite"
          >
            {error}
          </div>
        )}

        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
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
            className={`w-full px-3 py-2 text-sm sm:text-base text-gray-900 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              formErrors.email ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder="Enter your email"
            aria-invalid={!!formErrors.email}
            aria-describedby={formErrors.email ? 'email-error' : undefined}
          />
          {formErrors.email && (
            <p id="email-error" className="mt-1 text-xs sm:text-sm text-red-600" role="alert">
              {formErrors.email}
            </p>
          )}
        </div>

        <div>
          <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
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
              className={`w-full px-3 py-2 pr-10 text-sm sm:text-base text-gray-900 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                formErrors.password ? 'border-red-300' : 'border-gray-300'
              }`}
              style={{ WebkitTextSecurity: showPassword ? 'none' : 'disc' } as React.CSSProperties}
              placeholder="Enter your password"
              aria-invalid={!!formErrors.password}
              aria-describedby={formErrors.password ? 'password-error' : undefined}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-500 hover:text-gray-700 focus:outline-none transition-colors"
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
            <p id="password-error" className="mt-1 text-xs sm:text-sm text-red-600" role="alert">
              {formErrors.password}
            </p>
          )}
        </div>

        <div>
          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center py-2.5 sm:py-3 px-4 border border-transparent rounded-md shadow-sm text-sm sm:text-base font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            aria-busy={isLoading}
          >
            {isLoading ? 'Signing In...' : 'Sign In'}
          </button>
        </div>

        {onSwitchToRegister && (
          <div className="text-center">
            <p className="text-xs sm:text-sm text-gray-600">
              Don't have an account?{' '}
              <button
                type="button"
                onClick={onSwitchToRegister}
                className="font-medium text-blue-600 hover:text-blue-500 focus:outline-none focus:underline"
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