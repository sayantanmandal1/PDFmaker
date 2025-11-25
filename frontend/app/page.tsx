'use client';

import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import Link from 'next/link';
import { Sparkles, FileText, RefreshCw, Download } from 'lucide-react';
import LiquidEther from '@/components/background/background';

export default function Home() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        router.push('/dashboard');
      }
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <div className="relative">
          <div className="w-12 h-12 rounded-full border-4 border-transparent border-t-red-500 border-r-yellow-500 animate-spin"></div>
        </div>
      </div>
    );
  }

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

      {/* Hero section with glassmorphic container */}
      <div className="relative z-10 sm:mx-auto sm:w-full sm:max-w-2xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-4 bg-gradient-to-r from-red-500 to-yellow-500 bg-clip-text text-transparent">
            AI Document Generator
          </h1>
          <p className="text-lg sm:text-xl text-gray-300 mb-8">
            Create professional documents with AI assistance
          </p>
        </div>

        {/* CTA buttons with gradient backgrounds */}
        <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl shadow-2xl p-6 sm:p-8 mb-12">
          <div className="space-y-4">
            <Link
              href="/login"
              className="w-full flex justify-center py-3 px-6 rounded-lg text-base font-medium text-white bg-gradient-to-r from-red-500 to-yellow-500 hover:from-red-600 hover:to-yellow-600 hover:shadow-lg hover:shadow-red-500/50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-black focus:ring-red-500 transition-all duration-200 hover:scale-105 active:scale-95"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="w-full flex justify-center py-3 px-6 rounded-lg text-base font-medium text-white bg-white/5 backdrop-blur-md border border-white/10 hover:bg-white/10 hover:border-white/20 hover:shadow-lg hover:shadow-white/10 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-black focus:ring-white/50 transition-all duration-200 hover:scale-105 active:scale-95"
            >
              Create Account
            </Link>
          </div>
        </div>

        {/* Feature list with icons and glassmorphic cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-6 hover:bg-white/10 hover:scale-105 transition-all duration-200 group">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-red-500 to-yellow-500 flex items-center justify-center group-hover:shadow-lg group-hover:shadow-red-500/50 transition-shadow duration-200">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
              </div>
              <div>
                <h3 className="text-white font-medium mb-1">AI-Powered Generation</h3>
                <p className="text-gray-400 text-sm">Intelligent content creation with advanced AI</p>
              </div>
            </div>
          </div>

          <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-6 hover:bg-white/10 hover:scale-105 transition-all duration-200 group">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-red-500 to-yellow-500 flex items-center justify-center group-hover:shadow-lg group-hover:shadow-red-500/50 transition-shadow duration-200">
                  <FileText className="w-5 h-5 text-white" />
                </div>
              </div>
              <div>
                <h3 className="text-white font-medium mb-1">Multiple Formats</h3>
                <p className="text-gray-400 text-sm">Word & PowerPoint document creation</p>
              </div>
            </div>
          </div>

          <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-6 hover:bg-white/10 hover:scale-105 transition-all duration-200 group">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-red-500 to-yellow-500 flex items-center justify-center group-hover:shadow-lg group-hover:shadow-red-500/50 transition-shadow duration-200">
                  <RefreshCw className="w-5 h-5 text-white" />
                </div>
              </div>
              <div>
                <h3 className="text-white font-medium mb-1">Iterative Refinement</h3>
                <p className="text-gray-400 text-sm">Continuously improve your content</p>
              </div>
            </div>
          </div>

          <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-6 hover:bg-white/10 hover:scale-105 transition-all duration-200 group">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-red-500 to-yellow-500 flex items-center justify-center group-hover:shadow-lg group-hover:shadow-red-500/50 transition-shadow duration-200">
                  <Download className="w-5 h-5 text-white" />
                </div>
              </div>
              <div>
                <h3 className="text-white font-medium mb-1">Professional Export</h3>
                <p className="text-gray-400 text-sm">Download polished, ready-to-use documents</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
