'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { RegisterForm } from '@/components/auth/RegisterForm';
import { useAuth } from '@/contexts/AuthContext';
import { useEffect } from 'react';
import LiquidEther from '@/components/background/background';

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
      {/* Animated LiquidEther background */}
      <div className="absolute inset-0 overflow-hidden">
        <LiquidEther
          colors={['#5227FF', '#FF9FFC', '#B19EEF']}
          mouseForce={20}
          cursorSize={100}
          isViscous={false}
          viscous={30}
          iterationsViscous={32}
          iterationsPoisson={32}
          resolution={0.5}
          isBounce={false}
          autoDemo={true}
          autoSpeed={0.5}
          autoIntensity={2.2}
          takeoverDuration={0.25}
          autoResumeDelay={3000}
          autoRampDuration={0.6}
        />
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