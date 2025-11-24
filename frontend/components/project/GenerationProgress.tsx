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
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Generate Content
          </h3>
          <p className="text-sm text-gray-600 mt-1">
            Use AI to generate content for all {documentType === 'word' ? 'sections' : 'slides'}
          </p>
        </div>
        <button
          onClick={handleGenerate}
          disabled={disabled || isGenerating}
          className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {isGenerating ? 'Generating...' : 'Generate Content'}
        </button>
      </div>

      {/* Progress Indicator */}
      {isGenerating && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <LoadingSpinner size="sm" label="Generating content" />
            <div>
              <p className="text-sm font-medium text-blue-900">
                {progress?.message || 'Generating content...'}
              </p>
              <p className="text-xs text-blue-700 mt-1">
                This may take a few moments
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Success Message */}
      {!isGenerating && progress && progress.status === 'success' && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center space-x-3">
            <svg
              className="w-5 h-5 text-green-600"
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
            <div>
              <p className="text-sm font-medium text-green-900">
                {progress.message}
              </p>
              <p className="text-xs text-green-700 mt-1">
                Redirecting to editor...
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Partial Success Message */}
      {!isGenerating && progress && progress.status === 'partial' && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <svg
              className="w-5 h-5 text-yellow-600 mt-0.5"
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
            <div className="flex-1">
              <p className="text-sm font-medium text-yellow-900">
                {progress.message}
              </p>
              <p className="text-xs text-yellow-700 mt-1">
                Some content was generated successfully. Redirecting to editor...
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error Message with Retry */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3">
              <svg
                className="w-5 h-5 text-red-600 mt-0.5"
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
              <div className="flex-1">
                <p className="text-sm font-medium text-red-900">
                  Generation Failed
                </p>
                <p className="text-xs text-red-700 mt-1">{error}</p>
              </div>
            </div>
            <button
              onClick={handleRetry}
              disabled={isGenerating}
              className="ml-4 px-3 py-1 text-sm bg-red-600 text-white rounded hover:bg-red-700 disabled:bg-gray-400 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
