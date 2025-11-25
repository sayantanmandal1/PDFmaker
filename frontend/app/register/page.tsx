'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { RegisterForm } from '@/components/auth/RegisterForm';
import { useAuth } from '@/contexts/AuthContext';
import { useEffect } from 'react';

export default function RegisterPage() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  // Redirect to dashboard if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  const handleAuthSuccess = () => {
    router.push('/dashboard');
  };

  const switchToLogin = () => {
    router.push('/login');
  };

  return (
    <div className="min-h-screen bg-black relative overflow-hidden flex flex-col justify-center py-12 px-4 sm:px-6 lg:px-8">
      {/* Animated gradient background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-red-500/20 via-transparent to-transparent animate-pulse"></div>
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-yellow-500/20 via-transparent to-transparent animate-pulse" style={{ animationDelay: '1s' }}></div>
      </div>

      {/* Header with gradient accents */}
      <div className="relative z-10 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold mb-2 bg-gradient-to-r from-red-500 to-yellow-500 bg-clip-text text-transparent">
            AI Document Generator
          </h1>
          <p className="text-gray-400">
            Create professional documents with AI assistance
          </p>
        </div>
      </div>

      {/* Form container with frosted glass effect */}
      <div className="relative z-10 mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl shadow-2xl py-8 px-4 sm:px-10">
          <RegisterForm
            onSuccess={handleAuthSuccess}
            onSwitchToLogin={switchToLogin}
          />
        </div>
      </div>
    </div>
  );
}