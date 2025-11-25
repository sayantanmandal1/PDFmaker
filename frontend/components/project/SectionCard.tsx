'use client';

import { useState } from 'react';
import { Section, RefinementHistory } from '@/types';
import { RefinementPrompt } from './RefinementPrompt';
import { FeedbackButtons } from './FeedbackButtons';
import { CommentBox } from './CommentBox';
import { contentApi } from '@/lib/content-api';

interface SectionCardProps {
  section: Section;
  onUpdate: (section: Section) => void;
}

export function SectionCard({ section, onUpdate }: SectionCardProps) {
  const [isRefining, setIsRefining] = useState(false);
  const [refinementHistory, setRefinementHistory] = useState<RefinementHistory[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const [showRefinement, setShowRefinement] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState(section.content || '');
  const [isSaving, setIsSaving] = useState(false);

  const handleRefine = async (prompt: string) => {
    setIsRefining(true);
    setError(null);

    try {
      const response = await contentApi.refineSection(section.id, { prompt });
      onUpdate(response.section);
      
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
      const history = await contentApi.getSectionRefinementHistory(section.id);
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
    setEditedContent(section.content || '');
    setIsEditing(true);
    setError(null);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditedContent(section.content || '');
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
      const response = await contentApi.updateSection(section.id, {
        content: editedContent,
      });
      onUpdate(response.section);
      setIsEditing(false);
    } catch (err: any) {
      setError(err.message || 'Failed to save changes');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <article className="bg-white/5 backdrop-blur-md border border-white/10 rounded-lg shadow-xl overflow-hidden">
      {/* Section Header */}
      <header className="bg-gradient-to-r from-red-500 to-yellow-500 px-4 sm:px-6 py-3 sm:py-4">
        <h2 className="text-lg sm:text-xl md:text-2xl font-bold text-white break-words">{section.header}</h2>
      </header>

      {/* Section Content */}
      <div className="p-4 sm:p-6">
        {section.content ? (
          isEditing ? (
            <div className="space-y-4">
              <textarea
                value={editedContent}
                onChange={(e) => setEditedContent(e.target.value)}
                className="w-full min-h-[300px] px-4 py-3 text-sm sm:text-base text-white bg-white/5 border border-white/20 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent resize-y transition-all duration-200"
                placeholder="Enter section content..."
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
                  {section.content}
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
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <p className="text-gray-300 text-base sm:text-lg">No content generated yet</p>
            <p className="text-gray-500 text-xs sm:text-sm mt-2">
              Content will appear here after generation
            </p>
          </div>
        )}

        {/* Feedback and Comments */}
        {section.content && (
          <div className="mt-6 pt-6 border-t border-white/10 space-y-6">
            {/* Feedback Buttons */}
            <FeedbackButtons
              contentId={section.id}
              contentType="section"
            />

            {/* Refinement Controls */}
            <div>
              <button
                onClick={handleToggleRefinement}
                className="mb-4 text-yellow-400 hover:text-yellow-300 font-medium text-xs sm:text-sm flex items-center space-x-2 focus:outline-none focus:underline transition-colors duration-200"
                aria-expanded={showRefinement}
                aria-controls="refinement-section"
              >
                <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span>{showRefinement ? 'Hide' : 'Show'} Refinement Controls</span>
              </button>

              {showRefinement && (
                <div id="refinement-section">
                  <RefinementPrompt
                    onRefine={handleRefine}
                    isRefining={isRefining}
                    refinementHistory={refinementHistory}
                    onLoadHistory={loadRefinementHistory}
                    showHistory={showHistory}
                    onToggleHistory={() => setShowHistory(!showHistory)}
                  />
                </div>
              )}

              {error && !isRefining && (
                <div 
                  className="mt-4 flex items-start space-x-2 text-red-400 text-xs sm:text-sm bg-red-500/10 backdrop-blur-sm border border-red-500/20 p-3 rounded-lg"
                  role="alert"
                >
                  <svg className="w-5 h-5 shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <p className="font-medium">{error}</p>
                    <button
                      onClick={() => setError(null)}
                      className="mt-2 text-red-300 hover:text-red-200 underline text-xs focus:outline-none focus:ring-2 focus:ring-red-500 rounded transition-colors duration-200"
                      aria-label="Dismiss error"
                    >
                      Dismiss
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Comments Section */}
            <div className="pt-4 sm:pt-6 border-t border-white/10">
              <CommentBox
                contentId={section.id}
                contentType="section"
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
                d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14"
              />
            </svg>
            <span>Section {section.position + 1}</span>
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
            <time dateTime={section.updated_at}>
              Updated {new Date(section.updated_at).toLocaleDateString()}
            </time>
          </div>
        </div>
      </footer>
    </article>
  );
}
