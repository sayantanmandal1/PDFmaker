'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { DocumentTypeSelector, TopicInput } from '@/components/project';
import { projectsApi } from '@/lib/projects-api';
import { ProjectCreate } from '@/types';
import { Sparkles, ArrowLeft, ArrowRight } from 'lucide-react';

export default function NewProjectPage() {
  const router = useRouter();
  const [formData, setFormData] = useState<ProjectCreate>({
    name: '',
    document_type: 'word',
    topic: ''
  });
  const [isCreating, setIsCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name.trim() || !formData.topic.trim()) {
      setError('Please fill in all required fields');
      return;
    }

    try {
      setIsCreating(true);
      setError(null);
      const response = await projectsApi.createProject(formData);
      
      // Navigate to configuration page after successful creation
      router.push(`/projects/${response.project.id}/configure`);
    } catch (err: any) {
      console.error('Failed to create project:', err);
      setError(err.message || 'Failed to create project. Please try again.');
      setIsCreating(false);
    }
  };

  const handleCancel = () => {
    router.push('/dashboard');
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[#0a0a0a] relative overflow-hidden">
        {/* Animated gradient background */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-red-500/10 via-transparent to-transparent animate-pulse"></div>
          <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-yellow-500/10 via-transparent to-transparent animate-pulse" style={{ animationDelay: '1s' }}></div>
        </div>

        {/* Glassmorphic Navigation Bar */}
        <nav className="bg-white/5 backdrop-blur-md border-b border-white/10 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center h-16">
              <button
                onClick={handleCancel}
                className="mr-4 text-gray-300 hover:text-white transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-red-500 rounded-lg p-2"
                aria-label="Back to dashboard"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-red-500 to-yellow-500 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-lg sm:text-xl font-semibold bg-gradient-to-r from-red-500 to-yellow-500 bg-clip-text text-transparent">
                  Create New Project
                </h1>
              </div>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="relative z-10 max-w-4xl mx-auto py-8 sm:py-12 px-4 sm:px-6 lg:px-8">
          {/* Hero Section */}
          <div className="text-center mb-8 sm:mb-12 animate-fade-in">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-4">
              Start Your Next
              <span className="block bg-gradient-to-r from-red-500 to-yellow-500 bg-clip-text text-transparent">
                AI-Powered Document
              </span>
            </h2>
            <p className="text-base sm:text-lg text-gray-300 max-w-2xl mx-auto">
              Set up your project details below. You'll configure the document structure and generate content in the next step.
            </p>
          </div>

          {/* Form Container */}
          <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl shadow-2xl p-6 sm:p-8 lg:p-10 animate-scale-in">
            {/* Error Message */}
            {error && (
              <div className="mb-6 bg-red-500/10 backdrop-blur-sm border border-red-500/30 rounded-lg p-4 animate-slide-in">
                <div className="flex items-start">
                  <div className="shrink-0">
                    <svg className="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="ml-3 flex-1">
                    <p className="text-sm text-red-300">{error}</p>
                  </div>
                  <button
                    onClick={() => setError(null)}
                    className="ml-auto shrink-0 text-red-400 hover:text-red-300 focus:outline-none focus:ring-2 focus:ring-red-500 rounded transition-colors duration-200"
                    aria-label="Dismiss error"
                  >
                    <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-8">
              {/* Project Name */}
              <div className="space-y-2">
                <label htmlFor="name" className="block text-sm font-medium text-gray-300">
                  Project Name <span className="text-red-400">*</span>
                </label>
                <div className="relative">
                  <input
                    type="text"
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    disabled={isCreating}
                    className="block w-full px-4 py-3 bg-black/40 border border-white/20 rounded-lg text-white placeholder-gray-500 transition-all duration-200 focus:outline-none focus:bg-white/5 focus:backdrop-blur-md focus:border-transparent focus:ring-2 focus:ring-red-500/50 focus:shadow-lg focus:shadow-red-500/20 disabled:opacity-50 disabled:cursor-not-allowed text-base"
                    placeholder="e.g., Q4 Marketing Strategy, Product Launch Plan"
                    required
                    aria-required="true"
                  />
                </div>
                <p className="text-xs text-gray-400 mt-1">
                  Give your project a descriptive name to easily identify it later
                </p>
              </div>

              {/* Document Type Selector */}
              <div className="space-y-3">
                <label className="block text-sm font-medium text-gray-300">
                  Document Type <span className="text-red-400">*</span>
                </label>
                <DocumentTypeSelector
                  value={formData.document_type}
                  onChange={(type) => setFormData({ ...formData, document_type: type })}
                  disabled={isCreating}
                />
              </div>

              {/* Topic Input */}
              <div className="space-y-2">
                <TopicInput
                  value={formData.topic}
                  onChange={(topic) => {
                    console.log('Topic changed:', topic);
                    setFormData({ ...formData, topic });
                  }}
                  disabled={isCreating}
                />
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row justify-end gap-3 pt-6 border-t border-white/10">
                <button
                  type="button"
                  onClick={handleCancel}
                  disabled={isCreating}
                  className="w-full sm:w-auto px-6 py-3 text-base font-medium text-white bg-white/5 backdrop-blur-md border border-white/10 hover:bg-white/10 hover:border-white/20 hover:shadow-lg hover:shadow-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-black focus:ring-white/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:scale-105 active:scale-95 disabled:transform-none"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isCreating || !formData.name.trim() || !formData.topic.trim()}
                  className="w-full sm:w-auto px-6 py-3 text-base font-medium text-white bg-gradient-to-r from-red-500 to-yellow-500 hover:from-red-600 hover:to-yellow-600 hover:shadow-xl hover:shadow-red-500/50 rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-black focus:ring-red-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 hover:scale-105 active:scale-95 disabled:transform-none inline-flex items-center justify-center"
                  onClick={() => console.log('Button clicked. Form data:', formData)}
                >
                  {isCreating ? (
                    <>
                      <div className="w-5 h-5 mr-2 border-2 border-transparent border-t-white border-r-white rounded-full animate-spin"></div>
                      Creating Project...
                    </>
                  ) : (
                    <>
                      Continue to Configuration
                      <ArrowRight className="ml-2 w-5 h-5" />
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>

          {/* Help Text */}
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-400">
              Need help? Check out our{' '}
              <button className="text-yellow-400 hover:text-yellow-300 underline focus:outline-none transition-colors duration-200">
                documentation
              </button>
              {' '}or{' '}
              <button className="text-yellow-400 hover:text-yellow-300 underline focus:outline-none transition-colors duration-200">
                watch a tutorial
              </button>
            </p>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
