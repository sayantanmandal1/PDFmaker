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
        <div className="min-h-screen bg-gray-50">
          <nav className="bg-white shadow">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex items-center">
                  <h1 className="text-xl font-semibold text-gray-900">
                    AI Document Generator
                  </h1>
                </div>
                <div className="flex items-center space-x-4">
                  <span className="text-gray-700">
                    Welcome, {user?.name}
                  </span>
                  <button
                    onClick={logout}
                    className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
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
              <div className="flex justify-between items-center mb-8">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">My Projects</h2>
                  <p className="text-gray-600 mt-1">
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