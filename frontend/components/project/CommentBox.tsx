'use client';

import { useState, useEffect } from 'react';
import { Comment, ApiError } from '@/types';
import { contentApi } from '@/lib/content-api';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';
import { LoadingSpinner } from '@/components/common';

interface CommentBoxProps {
  contentId: string;
  contentType: 'section' | 'slide';
}

export function CommentBox({ contentId, contentType }: CommentBoxProps) {
  const { user } = useAuth();
  const { showSuccess, showError } = useToast();
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [editingCommentId, setEditingCommentId] = useState<string | null>(null);
  const [editingText, setEditingText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Reset state when contentId changes
    setComments([]);
    setNewComment('');
    setEditingCommentId(null);
    setEditingText('');
    setError(null);
    
    // Load comments for the new content
    loadComments();
  }, [contentId, contentType]);

  const loadComments = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const loadedComments = contentType === 'section'
        ? await contentApi.getSectionComments(contentId)
        : await contentApi.getSlideComments(contentId);
      
      // Ensure we have a valid array and filter out any invalid entries
      const validComments = Array.isArray(loadedComments) 
        ? loadedComments.filter(c => c && c.id && c.comment_text) 
        : [];
      
      setComments(validComments);
    } catch (err) {
      const apiError = err as ApiError;
      const errorMessage = apiError.detail || 'Failed to load comments';
      
      // Only show error if it's not a 404 (no comments yet)
      if (apiError.status_code !== 404) {
        setError(errorMessage);
      }
      
      console.error('Failed to load comments:', err);
      setComments([]); // Reset to empty array on error
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newComment.trim()) {
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const response = contentType === 'section'
        ? await contentApi.addSectionComment(contentId, { comment_text: newComment })
        : await contentApi.addSlideComment(contentId, { comment_text: newComment });
      
      setComments([...comments, response.comment]);
      setNewComment('');
      showSuccess('Comment added successfully');
    } catch (err) {
      const apiError = err as ApiError;
      const errorMessage = apiError.detail || 'Failed to add comment';
      setError(errorMessage);
      showError(errorMessage);
      console.error('Failed to add comment:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleEditComment = async (commentId: string) => {
    if (!editingText.trim()) {
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await contentApi.updateComment(commentId, { comment_text: editingText });
      
      setComments(comments.map(c => c.id === commentId ? response.comment : c));
      setEditingCommentId(null);
      setEditingText('');
      showSuccess('Comment updated successfully');
    } catch (err) {
      const apiError = err as ApiError;
      const errorMessage = apiError.detail || 'Failed to update comment';
      setError(errorMessage);
      showError(errorMessage);
      console.error('Failed to update comment:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteComment = async (commentId: string) => {
    if (!confirm('Are you sure you want to delete this comment?')) {
      return;
    }

    setError(null);

    try {
      await contentApi.deleteComment(commentId);
      setComments(comments.filter(c => c.id !== commentId));
      showSuccess('Comment deleted successfully');
    } catch (err) {
      const apiError = err as ApiError;
      const errorMessage = apiError.detail || 'Failed to delete comment';
      setError(errorMessage);
      showError(errorMessage);
      console.error('Failed to delete comment:', err);
    }
  };

  const startEditing = (comment: Comment) => {
    setEditingCommentId(comment.id);
    setEditingText(comment.comment_text);
  };

  const cancelEditing = () => {
    setEditingCommentId(null);
    setEditingText('');
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    
    return date.toLocaleDateString();
  };

  return (
    <div className="space-y-4">
      <h3 className="text-base sm:text-lg font-semibold text-gray-800 flex items-center">
        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>
        <span>Comments ({comments.length})</span>
      </h3>

      {error && (
        <div 
          className="bg-red-50 border border-red-200 text-red-700 px-3 sm:px-4 py-2 sm:py-3 rounded-lg text-xs sm:text-sm"
          role="alert"
        >
          {error}
        </div>
      )}

      {/* Add Comment Form */}
      <form onSubmit={handleAddComment} className="space-y-2" aria-label="Add comment form">
        <label htmlFor="new-comment" className="sr-only">Add a comment</label>
        <textarea
          id="new-comment"
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          placeholder="Add a comment..."
          rows={3}
          className="w-full px-3 sm:px-4 py-2 text-sm sm:text-base text-black border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
          disabled={isSubmitting}
          aria-label="Comment text"
        />
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isSubmitting || !newComment.trim()}
            className="px-3 sm:px-4 py-2 text-sm sm:text-base bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            aria-busy={isSubmitting}
          >
            {isSubmitting ? 'Adding...' : 'Add Comment'}
          </button>
        </div>
      </form>

      {/* Comments List */}
      {isLoading ? (
        <div className="text-center py-4" role="status" aria-label="Loading comments">
          <LoadingSpinner size="md" label="Loading comments" />
          <p className="text-gray-500 mt-2 text-sm">Loading comments...</p>
        </div>
      ) : comments.length === 0 ? (
        <div className="text-center py-6 sm:py-8 bg-gray-50 rounded-lg">
          <svg className="w-10 h-10 sm:w-12 sm:h-12 mx-auto text-gray-300 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
          <p className="text-gray-500 text-sm sm:text-base">No comments yet</p>
          <p className="text-gray-400 text-xs sm:text-sm mt-1">Be the first to comment!</p>
        </div>
      ) : (
        <div className="space-y-3" role="list" aria-label="Comments">
          {(Array.isArray(comments) ? comments : []).filter(comment => comment && comment.id).map((comment) => (
            <article key={comment.id} className="bg-gray-50 rounded-lg p-3 sm:p-4 border border-gray-200">
              {editingCommentId === comment.id ? (
                <div className="space-y-2">
                  <label htmlFor={`edit-comment-${comment.id}`} className="sr-only">Edit comment</label>
                  <textarea
                    id={`edit-comment-${comment.id}`}
                    value={editingText}
                    onChange={(e) => setEditingText(e.target.value)}
                    rows={3}
                    className="w-full px-3 py-2 text-sm sm:text-base text-black border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                    disabled={isSubmitting}
                  />
                  <div className="flex justify-end space-x-2">
                    <button
                      onClick={cancelEditing}
                      disabled={isSubmitting}
                      className="px-3 py-1.5 text-gray-600 hover:text-gray-800 text-xs sm:text-sm focus:outline-none focus:underline"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleEditComment(comment.id)}
                      disabled={isSubmitting || !editingText.trim()}
                      className="px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      aria-busy={isSubmitting}
                    >
                      {isSubmitting ? 'Saving...' : 'Save'}
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="flex items-start justify-between mb-2 gap-2">
                    <div className="flex items-center space-x-2 min-w-0 flex-1">
                      <div 
                        className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold text-sm shrink-0"
                        aria-hidden="true"
                      >
                        {user?.name?.charAt(0).toUpperCase() || 'U'}
                      </div>
                      <div className="min-w-0">
                        <p className="text-xs sm:text-sm font-medium text-gray-900 truncate">{user?.name || 'User'}</p>
                        <time className="text-xs text-gray-500" dateTime={comment.created_at}>
                          {formatDate(comment.created_at)}
                        </time>
                      </div>
                    </div>
                    
                    {user && comment.user_id === user.id && (
                      <div className="flex space-x-1 shrink-0">
                        <button
                          onClick={() => startEditing(comment)}
                          className="p-1 text-gray-400 hover:text-blue-600 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
                          aria-label="Edit comment"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                            />
                          </svg>
                        </button>
                        <button
                          onClick={() => handleDeleteComment(comment.id)}
                          className="p-1 text-gray-400 hover:text-red-600 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500 rounded"
                          aria-label="Delete comment"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                            />
                          </svg>
                        </button>
                      </div>
                    )}
                  </div>
                  <p className="text-xs sm:text-sm text-gray-700 whitespace-pre-wrap wrap-break-word">{comment.comment_text}</p>
                </>
              )}
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
