'use client';

import { useState } from 'react';
import { contentApi } from '@/lib/content-api';
import { useToast } from '@/contexts/ToastContext';
import { ApiError } from '@/types';

interface FeedbackButtonsProps {
  contentId: string;
  contentType: 'section' | 'slide';
  initialFeedback?: 'like' | 'dislike' | null;
}

export function FeedbackButtons({ contentId, contentType, initialFeedback = null }: FeedbackButtonsProps) {
  const [feedback, setFeedback] = useState<'like' | 'dislike' | null>(initialFeedback);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { showSuccess, showError } = useToast();

  const handleFeedback = async (feedbackType: 'like' | 'dislike') => {
    // If clicking the same feedback, do nothing
    if (feedback === feedbackType) {
      return;
    }

    setIsSubmitting(true);

    try {
      if (contentType === 'section') {
        await contentApi.addSectionFeedback(contentId, { feedback_type: feedbackType });
      } else {
        await contentApi.addSlideFeedback(contentId, { feedback_type: feedbackType });
      }
      
      setFeedback(feedbackType);
      showSuccess(`Feedback recorded: ${feedbackType}`);
    } catch (err) {
      const apiError = err as ApiError;
      const errorMessage = apiError.detail || 'Failed to submit feedback';
      showError(errorMessage);
      console.error('Failed to submit feedback:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div 
      className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-2"
      role="group"
      aria-label="Content feedback"
    >
      <span className="text-xs sm:text-sm text-gray-600 sm:mr-2">How is this content?</span>
      
      <div className="flex items-center gap-2">
        <button
          onClick={() => handleFeedback('like')}
          disabled={isSubmitting}
          className={`flex items-center space-x-1 px-2.5 sm:px-3 py-1.5 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 ${
            feedback === 'like'
              ? 'bg-green-100 text-green-700 border-2 border-green-500'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200 border-2 border-transparent'
          } ${isSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
          aria-label="Like this content"
          aria-pressed={feedback === 'like'}
        >
          <svg
            className="w-4 h-4 sm:w-5 sm:h-5"
            fill={feedback === 'like' ? 'currentColor' : 'none'}
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5"
            />
          </svg>
          <span className="text-xs sm:text-sm font-medium">Like</span>
        </button>

        <button
          onClick={() => handleFeedback('dislike')}
          disabled={isSubmitting}
          className={`flex items-center space-x-1 px-2.5 sm:px-3 py-1.5 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 ${
            feedback === 'dislike'
              ? 'bg-red-100 text-red-700 border-2 border-red-500'
              : 'bg-gray-100 text-gray-600 hover:bg-gray-200 border-2 border-transparent'
          } ${isSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
          aria-label="Dislike this content"
          aria-pressed={feedback === 'dislike'}
        >
          <svg
            className="w-4 h-4 sm:w-5 sm:h-5"
            fill={feedback === 'dislike' ? 'currentColor' : 'none'}
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M10 14H5.236a2 2 0 01-1.789-2.894l3.5-7A2 2 0 018.736 3h4.018a2 2 0 01.485.06l3.76.94m-7 10v5a2 2 0 002 2h.096c.5 0 .905-.405.905-.904 0-.715.211-1.413.608-2.008L17 13V4m-7 10h2m5-10h2a2 2 0 012 2v6a2 2 0 01-2 2h-2.5"
            />
          </svg>
          <span className="text-xs sm:text-sm font-medium">Dislike</span>
        </button>
      </div>
    </div>
  );
}
