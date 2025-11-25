'use client';

import { useState } from 'react';
import { projectsApi } from '@/lib/projects-api';
import { useToast } from '@/contexts/ToastContext';
import { ApiError } from '@/types';
import { LoadingSpinner } from '@/components/common';

interface GenerationProgressProps {
  projectId: string;
  documentType: 'word' | 'powerpoint';
  onGenerationComplete: () => void;
  disabled?: boolean;
}

export function GenerationProgress({
  projectId,
  documentType,
  onGenerationComplete,
  disabled = false,
}: GenerationProgressProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { showSuccess, showWarning } = useToast();
  const [progress, setProgress] = useState<{
    status: string;
    message: string;
  } | null>(null);

  const handleGenerate = async () => {
    try {
      setIsGenerating(true);
      setError(null);
      setProgress({ status: 'generating', message: 'Generating content...' });

      const response = await projectsApi.generateContent(projectId);

      setProgress({
        status: response.status,
        message: response.message,
      });

      // Show appropriate toast based on status
      if (response.status === 'success') {
        showSuccess('Content generated successfully!');
      } else if (response.status === 'partial') {
        showWarning('Some content was generated. Check the editor for details.');
      }

      // Wait a moment to show success message
      setTimeout(() => {
        onGenerationComplete();
      }, 1500);
    } catch (err) {
      console.error('Failed to generate content:', err);
      const apiError = err as ApiError;
      const errorMessage = apiError.detail || 'Failed to generate content';
      setError(errorMessage);
      setProgress(null);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleRetry = () => {
    setError(null);
    handleGenerate();
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-white">
            Generate Content
          </h3>
          <p className="text-sm text-gray-300 mt-1">
            Use AI to generate content for all {documentType === 'word' ? 'sections' : 'slides'}
          </p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={disabled || isGenerating}
          className="
            px-6 py-2.5 
            bg-gradient-to-r from-green-500 to-emerald-500 
            text-white font-medium rounded-lg 
            hover:from-green-600 hover:to-emerald-600 
            hover:scale-105 hover:shadow-lg hover:shadow-green-500/50
            disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
            transition-all duration-200
            focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:ring-offset-2 focus:ring-offset-black
            whitespace-nowrap
          "
        >
          {isGenerating ? 'Generating...' : 'Generate Content'}
        </button>
      </div>

      {/* Progress Indicator with Animated Gradient */}
      {isGenerating && (
        <div className="bg-gradient-to-br from-red-500/10 to-yellow-500/10 backdrop-blur-md border border-white/20 rounded-lg p-4 shadow-lg shadow-red-500/10">
          <div className="flex items-center space-x-3">
            <LoadingSpinner size="sm" label="Generating content" />
            <div className="flex-1">
              <p className="text-sm font-medium text-white">
                {progress?.message || 'Generating content...'}
              </p>
              <p className="text-xs text-gray-300 mt-1">
                This may take a few moments
              </p>
            </div>
          </div>
          {/* Animated progress bar */}
          <div className="mt-3 h-2 bg-black/40 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-red-500 to-yellow-500 animate-pulse"
              style={{ width: '100%' }}
            />
          </div>
        </div>
      )}

      {/* Success Message - Green-tinted Glassmorphic */}
      {!isGenerating && progress && progress.status === 'success' && (
        <div className="bg-green-500/10 backdrop-blur-md border border-green-500/30 rounded-lg p-4 shadow-lg shadow-green-500/10">
          <div className="flex items-center space-x-3">
            <div className="shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-green-500/20">
              <svg
                className="w-5 h-5 text-green-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium text-green-300">
                {progress.message}
              </p>
              <p className="text-xs text-green-400 mt-1">
                Redirecting to editor...
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Partial Success Message - Yellow-tinted Glassmorphic */}
      {!isGenerating && progress && progress.status === 'partial' && (
        <div className="bg-yellow-500/10 backdrop-blur-md border border-yellow-500/30 rounded-lg p-4 shadow-lg shadow-yellow-500/10">
          <div className="flex items-start space-x-3">
            <div className="shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-yellow-500/20 mt-0.5">
              <svg
                className="w-5 h-5 text-yellow-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium text-yellow-300">
                {progress.message}
              </p>
              <p className="text-xs text-yellow-400 mt-1">
                Some content was generated successfully. Redirecting to editor...
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error Message with Retry - Red-tinted Glassmorphic */}
      {error && (
        <div className="bg-red-500/10 backdrop-blur-md border border-red-500/30 rounded-lg p-4 shadow-lg shadow-red-500/10">
          <div className="flex items-start justify-between gap-3">
            <div className="flex items-start space-x-3 flex-1">
              <div className="shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-red-500/20 mt-0.5">
                <svg
                  className="w-5 h-5 text-red-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium text-red-300">
                  Generation Failed
                </p>
                <p className="text-xs text-red-400 mt-1">{error}</p>
              </div>
            </div>
            <button
              onClick={handleRetry}
              disabled={isGenerating}
              className="
                shrink-0 px-4 py-1.5 text-sm 
                bg-red-500 text-white font-medium rounded-lg 
                hover:bg-red-600 hover:scale-105
                disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
                transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-red-500/50
              "
            >
              Retry
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
