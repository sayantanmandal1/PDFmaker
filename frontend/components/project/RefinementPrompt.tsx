'use client';

import { useState } from 'react';
import { RefinementHistory, ApiError } from '@/types';
import { useToast } from '@/contexts/ToastContext';
import { LoadingSpinner, InlineError } from '@/components/common';

interface RefinementPromptProps {
  onRefine: (prompt: string) => Promise<void>;
  isRefining: boolean;
  refinementHistory: RefinementHistory[];
  onLoadHistory: () => void;
  showHistory: boolean;
  onToggleHistory: () => void;
}

export function RefinementPrompt({
  onRefine,
  isRefining,
  refinementHistory,
  onLoadHistory,
  showHistory,
  onToggleHistory,
}: RefinementPromptProps) {
  const [prompt, setPrompt] = useState('');
  const [error, setError] = useState<string | null>(null);
  const { showSuccess, showError } = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      setError('Please enter refinement instructions');
      return;
    }

    setError(null);
    
    try {
      await onRefine(prompt.trim());
      setPrompt(''); // Clear the input after successful refinement
      showSuccess('Content refined successfully!');
    } catch (err) {
      const apiError = err as ApiError;
      const errorMessage = apiError.detail || 'Failed to refine content. Please try again.';
      setError(errorMessage);
      showError(errorMessage);
    }
  };

  const handleToggleHistory = () => {
    if (!showHistory && refinementHistory.length === 0) {
      onLoadHistory();
    }
    onToggleHistory();
  };

  return (
    <div className="space-y-4 bg-white/5 backdrop-blur-md border border-white/10 rounded-lg p-4">
      {/* Refinement Form */}
      <form onSubmit={handleSubmit} className="space-y-3" aria-label="Content refinement form">
        <div>
          <label htmlFor="refinement-prompt" className="block text-sm font-medium text-gray-300 mb-2">
            Refine Content
          </label>
          <textarea
            id="refinement-prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Enter instructions to refine this content (e.g., 'Make it more concise', 'Add more technical details', 'Simplify the language')"
            className="w-full px-3 sm:px-4 py-2 sm:py-3 text-sm sm:text-base text-white bg-white/5 border border-white/20 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none transition-all duration-200"
            rows={3}
            disabled={isRefining}
            aria-invalid={!!error}
            aria-describedby={error ? 'refinement-error' : undefined}
          />
        </div>

        {error && (
          <InlineError message={error} />
        )}

        <button
          type="submit"
          disabled={isRefining || !prompt.trim()}
          className="w-full bg-gradient-to-r from-red-500 to-yellow-500 text-white px-4 sm:px-6 py-2.5 sm:py-3 rounded-lg text-sm sm:text-base font-medium hover:from-red-600 hover:to-yellow-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center space-x-2 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          aria-busy={isRefining}
        >
          {isRefining ? (
            <>
              <LoadingSpinner size="sm" label="Refining content" />
              <span>Refining...</span>
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              <span>Refine Content</span>
            </>
          )}
        </button>
      </form>

      {/* Refinement History Toggle */}
      {refinementHistory.length > 0 && (
        <button
          onClick={handleToggleHistory}
          className="w-full text-left px-3 sm:px-4 py-2 text-xs sm:text-sm text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-all duration-200 flex items-center justify-between focus:outline-none focus:ring-2 focus:ring-red-500"
          aria-expanded={showHistory}
          aria-controls="refinement-history"
        >
          <span className="flex items-center space-x-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Refinement History ({refinementHistory.length})</span>
          </span>
          <svg
            className={`w-5 h-5 transition-transform duration-200 ${showHistory ? 'rotate-180' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      )}

      {/* Refinement History Display */}
      {showHistory && refinementHistory.length > 0 && (
        <div 
          id="refinement-history"
          className="border border-white/10 rounded-lg overflow-hidden bg-white/5 backdrop-blur-sm"
          role="region"
          aria-label="Refinement history"
        >
          <div className="bg-white/5 px-3 sm:px-4 py-2 border-b border-white/10">
            <h4 className="text-xs sm:text-sm font-medium text-gray-300">Previous Refinements</h4>
          </div>
          <div className="divide-y divide-white/10 max-h-96 overflow-y-auto">
            {refinementHistory.map((history) => (
              <article key={history.id} className="p-3 sm:p-4 hover:bg-white/5 transition-colors duration-200">
                <div className="flex items-start justify-between mb-2">
                  <time className="text-xs text-gray-400" dateTime={history.created_at}>
                    {new Date(history.created_at).toLocaleString()}
                  </time>
                </div>
                <div className="text-xs sm:text-sm">
                  <p className="font-medium text-gray-300 mb-1">Instruction:</p>
                  <p className="text-gray-400 italic mb-3">&quot;{history.refinement_prompt}&quot;</p>
                  
                  {history.previous_content && history.new_content && (
                    <details className="mt-2">
                      <summary className="cursor-pointer text-yellow-400 hover:text-yellow-300 text-xs font-medium focus:outline-none focus:underline transition-colors duration-200">
                        View content changes
                      </summary>
                      <div className="mt-2 space-y-2 text-xs">
                        <div>
                          <p className="font-medium text-gray-300 mb-1">Before:</p>
                          <p className="text-gray-400 bg-red-500/10 p-2 rounded border border-red-500/20 line-clamp-3">
                            {history.previous_content}
                          </p>
                        </div>
                        <div>
                          <p className="font-medium text-gray-300 mb-1">After:</p>
                          <p className="text-gray-400 bg-green-500/10 p-2 rounded border border-green-500/20 line-clamp-3">
                            {history.new_content}
                          </p>
                        </div>
                      </div>
                    </details>
                  )}
                </div>
              </article>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
