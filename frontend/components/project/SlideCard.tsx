'use client';

import { useState } from 'react';
import { Slide, RefinementHistory } from '@/types';
import { RefinementPrompt } from './RefinementPrompt';
import { FeedbackButtons } from './FeedbackButtons';
import { CommentBox } from './CommentBox';
import { contentApi } from '@/lib/content-api';

interface SlideCardProps {
  slide: Slide;
  onUpdate: (slide: Slide) => void;
}

export function SlideCard({ slide, onUpdate }: SlideCardProps) {
  const [isRefining, setIsRefining] = useState(false);
  const [refinementHistory, setRefinementHistory] = useState<RefinementHistory[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [showRefinement, setShowRefinement] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRefine = async (prompt: string) => {
    setIsRefining(true);
    setError(null);

    try {
      const response = await contentApi.refineSlide(slide.id, { prompt });
      onUpdate(response.slide);
      
      // Reload history after successful refinement
      await loadRefinementHistory();
    } catch (err: any) {
      const errorMessage = err.message || 'Failed to refine content';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsRefining(false);
    }
  };

  const loadRefinementHistory = async () => {
    try {
      const history = await contentApi.getSlideRefinementHistory(slide.id);
      setRefinementHistory(history);
    } catch (err) {
      console.error('Failed to load refinement history:', err);
    }
  };

  const handleToggleRefinement = () => {
    setShowRefinement(!showRefinement);
    setError(null);
  };

  return (
    <article className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Slide Title */}
      <header className="bg-gradient-to-r from-purple-600 to-purple-700 px-4 sm:px-6 py-3 sm:py-4">
        <h2 className="text-lg sm:text-xl md:text-2xl font-bold text-white break-words">{slide.title}</h2>
      </header>

      {/* Slide Content */}
      <div className="p-4 sm:p-6">
        {slide.content ? (
          <div className="prose prose-sm sm:prose max-w-none">
            <div className="text-sm sm:text-base text-gray-800 leading-relaxed whitespace-pre-wrap break-words">
              {slide.content}
            </div>
          </div>
        ) : (
          <div className="text-center py-8 sm:py-12">
            <svg
              className="w-12 h-12 sm:w-16 sm:h-16 mx-auto text-gray-300 mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"
              />
            </svg>
            <p className="text-gray-500 text-base sm:text-lg">No content generated yet</p>
            <p className="text-gray-400 text-xs sm:text-sm mt-2">
              Content will appear here after generation
            </p>
          </div>
        )}

        {/* Feedback and Comments */}
        {slide.content && (
          <div className="mt-6 pt-6 border-t border-gray-200 space-y-6">
            {/* Feedback Buttons */}
            <FeedbackButtons
              contentId={slide.id}
              contentType="slide"
            />

            {/* Refinement Controls */}
            <div>
              <button
                onClick={handleToggleRefinement}
                className="mb-4 text-purple-600 hover:text-purple-700 font-medium text-sm flex items-center space-x-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span>{showRefinement ? 'Hide' : 'Show'} Refinement Controls</span>
              </button>

              {showRefinement && (
                <RefinementPrompt
                  onRefine={handleRefine}
                  isRefining={isRefining}
                  refinementHistory={refinementHistory}
                  onLoadHistory={loadRefinementHistory}
                  showHistory={showHistory}
                  onToggleHistory={() => setShowHistory(!showHistory)}
                />
              )}

              {error && !isRefining && (
                <div className="mt-4 flex items-start space-x-2 text-red-600 text-sm bg-red-50 p-3 rounded-lg">
                  <svg className="w-5 h-5 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="font-medium">{error}</p>
                  <button
                    onClick={() => setError(null)}
                    className="mt-2 text-red-700 hover:text-red-800 underline text-xs"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
              )}
            </div>

            {/* Comments Section */}
            <div className="pt-6 border-t border-gray-200">
              <CommentBox
                contentId={slide.id}
                contentType="slide"
              />
            </div>
          </div>
        )}
      </div>

      {/* Metadata Footer */}
      <footer className="bg-gray-50 px-4 sm:px-6 py-3 border-t border-gray-200">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 text-xs sm:text-sm text-gray-600">
          <div className="flex items-center">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"
              />
            </svg>
            <span>Slide {slide.position + 1}</span>
          </div>
          <div className="flex items-center">
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <time dateTime={slide.updated_at}>
              Updated {new Date(slide.updated_at).toLocaleDateString()}
            </time>
          </div>
        </div>
      </footer>
    </article>
  );
}
