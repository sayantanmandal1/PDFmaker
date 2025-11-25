'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastContext';
import { ProjectList, CreateProjectButton } from '@/components/dashboard';
import { projectsApi } from '@/lib/projects-api';
import { Project, ApiError } from '@/types';
import { ErrorBoundary, ErrorMessage } from '@/components/common';

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const router = useRouter();
  const { showSuccess, showError } = useToast();
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await projectsApi.getProjects();
      setProjects(response.projects);
    } catch (err) {
      console.error('Failed to load projects:', err);
      const apiError = err as ApiError;
      const errorMessage = apiError.detail || 'Failed to load projects. Please try again.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteProject = async (projectId: string) => {
    try {
      await projectsApi.deleteProject(projectId);
      setProjects(prev => prev.filter(p => p.id !== projectId));
      showSuccess('Project deleted successfully');
    } catch (err) {
      console.error('Failed to delete project:', err);
      const apiError = err as ApiError;
      showError(apiError.detail || 'Failed to delete project. Please try again.');
    }
  };

  const handleSelectProject = (projectId: string) => {
    const project = projects.find(p => p.id === projectId);
    if (project) {
      // Navigate based on project status
      switch (project.status) {
        case 'configuring':
          router.push(`/projects/${projectId}/configure`);
          break;
        case 'generating':
        case 'ready':
        case 'ready_for_refinement':
        case 'partially_generated':
          router.push(`/projects/${projectId}/editor`);
          break;
        default:
          // For any other status, go to configure page
          router.push(`/projects/${projectId}/configure`);
      }
    }
  };

  return (
    <ProtectedRoute>
      <ErrorBoundary>
        <div className="min-h-screen bg-[#0a0a0a]">
          {/* Glassmorphic Navigation Bar */}
          <nav className="bg-white/5 backdrop-blur-md border-b border-white/10 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex items-center">
                  <h1 className="text-xl font-semibold bg-gradient-to-r from-red-500 to-yellow-500 bg-clip-text text-transparent">
                    AI Document Generator
                  </h1>
                </div>
                <div className="flex items-center space-x-4">
                  <span className="text-gray-300 text-sm sm:text-base">
                    Welcome, {user?.name}
                  </span>
                  <button
                    onClick={logout}
                    className="bg-gradient-to-r from-red-500 to-yellow-500 hover:from-red-600 hover:to-yellow-600 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 hover:scale-105 hover:shadow-lg hover:shadow-red-500/50"
                  >
                    Logout
                  </button>
                </div>
              </div>
            </div>
          </nav>

          <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
            <div className="px-4 py-6 sm:px-0">
              {/* Header */}
              <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-8 gap-4">
                <div>
                  <h2 className="text-2xl sm:text-3xl font-bold text-white">My Projects</h2>
                  <p className="text-gray-400 mt-1 text-sm sm:text-base">
                    Create and manage your AI-generated documents
                  </p>
                </div>
                <CreateProjectButton isLoading={isLoading} />
              </div>

              {/* Error Message */}
              {error && (
                <ErrorMessage
                  message={error}
                  title="Failed to load projects"
                  onRetry={loadProjects}
                  className="mb-6"
                />
              )}

              {/* Projects List */}
              <ProjectList
                projects={projects}
                onDeleteProject={handleDeleteProject}
                onSelectProject={handleSelectProject}
                isLoading={isLoading}
              />
            </div>
          </main>
        </div>
      </ErrorBoundary>
    </ProtectedRoute>
  );
}