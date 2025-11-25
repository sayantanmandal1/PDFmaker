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
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState(slide.content || '');
  const [isSaving, setIsSaving] = useState(false);

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

  const handleEdit = () => {
    setEditedContent(slide.content || '');
    setIsEditing(true);
    setError(null);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditedContent(slide.content || '');
    setError(null);
  };

  const handleSaveEdit = async () => {
    if (!editedContent.trim()) {
      setError('Content cannot be empty');
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      const response = await contentApi.updateSlide(slide.id, {
        content: editedContent,
      });
      onUpdate(response.slide);
      setIsEditing(false);
    } catch (err: any) {
      setError(err.message || 'Failed to save changes');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <article className="bg-white/5 backdrop-blur-md border border-white/10 rounded-lg shadow-xl overflow-hidden">
      {/* Slide Title */}
      <header className="bg-gradient-to-r from-red-500 to-yellow-500 px-4 sm:px-6 py-3 sm:py-4">
        <h2 className="text-lg sm:text-xl md:text-2xl font-bold text-white break-words">{slide.title}</h2>
      </header>

      {/* Slide Content */}
      <div className="p-4 sm:p-6">
        {slide.content ? (
          isEditing ? (
            <div className="space-y-4">
              <textarea
                value={editedContent}
                onChange={(e) => setEditedContent(e.target.value)}
                className="w-full min-h-[200px] px-4 py-3 text-sm sm:text-base text-white bg-white/5 border border-white/20 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent resize-y transition-all duration-200"
                placeholder="Enter slide content (keep it concise for presentations)..."
              />
              <div className="flex gap-3">
                <button
                  onClick={handleSaveEdit}
                  disabled={isSaving || !editedContent.trim()}
                  className="px-6 py-2 bg-gradient-to-r from-red-500 to-yellow-500 text-white rounded-md hover:from-red-600 hover:to-yellow-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium"
                >
                  {isSaving ? 'Saving...' : 'Save Changes'}
                </button>
                <button
                  onClick={handleCancelEdit}
                  disabled={isSaving}
                  className="px-6 py-2 bg-white/10 text-white rounded-md hover:bg-white/20 disabled:opacity-50 transition-all duration-200 font-medium"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div>
              <div className="flex justify-end mb-2">
                <button
                  onClick={handleEdit}
                  className="text-yellow-400 hover:text-yellow-300 font-medium text-sm flex items-center gap-2 transition-colors duration-200"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                  Edit Content
                </button>
              </div>
              <div className="prose prose-sm sm:prose max-w-none">
                <div className="text-sm sm:text-base text-gray-200 leading-relaxed whitespace-pre-wrap break-words">
                  {slide.content}
                </div>
              </div>
            </div>
          )
        ) : (
          <div className="text-center py-8 sm:py-12">
            <svg
              className="w-12 h-12 sm:w-16 sm:h-16 mx-auto text-gray-500 mb-4"
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
            <p className="text-gray-300 text-base sm:text-lg">No content generated yet</p>
            <p className="text-gray-500 text-xs sm:text-sm mt-2">
              Content will appear here after generation
            </p>
          </div>
        )}

        {/* Feedback and Comments */}
        {slide.content && (
          <div className="mt-6 pt-6 border-t border-white/10 space-y-6">
            {/* Feedback Buttons */}
            <FeedbackButtons
              contentId={slide.id}
              contentType="slide"
            />

            {/* Refinement Controls */}
            <div>
              <button
                onClick={handleToggleRefinement}
                className="mb-4 text-yellow-400 hover:text-yellow-300 font-medium text-sm flex items-center space-x-2 transition-colors duration-200"
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
                <div className="mt-4 flex items-start space-x-2 text-red-400 text-sm bg-red-500/10 backdrop-blur-sm border border-red-500/20 p-3 rounded-lg">
                  <svg className="w-5 h-5 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <div>
                  <p className="font-medium">{error}</p>
                  <button
                    onClick={() => setError(null)}
                    className="mt-2 text-red-300 hover:text-red-200 underline text-xs transition-colors duration-200"
                  >
                    Dismiss
                  </button>
                </div>
              </div>
              )}
            </div>

            {/* Comments Section */}
            <div className="pt-6 border-t border-white/10">
              <CommentBox
                contentId={slide.id}
                contentType="slide"
              />
            </div>
          </div>
        )}
      </div>

      {/* Metadata Footer */}
      <footer className="bg-white/5 backdrop-blur-sm px-4 sm:px-6 py-3 border-t border-white/10">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 text-xs sm:text-sm text-gray-400">
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
