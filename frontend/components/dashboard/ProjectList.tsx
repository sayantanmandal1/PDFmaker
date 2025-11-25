'use client';

import { Project } from '@/types';
import { ProjectCard } from './ProjectCard';

interface ProjectListProps {
  projects: Project[];
  onDeleteProject: (projectId: string) => void;
  onSelectProject: (projectId: string) => void;
  isLoading?: boolean;
}

export function ProjectList({ 
  projects, 
  onDeleteProject, 
  onSelectProject, 
  isLoading 
}: ProjectListProps) {
  if (isLoading) {
    return (
      <div 
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6"
        role="status"
        aria-label="Loading projects"
      >
        {[...Array(6)].map((_, index) => (
          <div key={index} className="bg-white/5 backdrop-blur-md rounded-xl border border-white/10 animate-pulse">
            <div className="p-4 sm:p-6">
              <div className="flex items-start justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-red-500/30 to-yellow-500/30 rounded-lg"></div>
                  <div>
                    <div className="h-5 bg-white/10 rounded w-32 mb-2"></div>
                    <div className="h-4 bg-white/10 rounded w-24"></div>
                  </div>
                </div>
                <div className="w-5 h-5 bg-white/10 rounded"></div>
              </div>
              <div className="mt-4">
                <div className="h-4 bg-white/10 rounded w-full mb-2"></div>
                <div className="h-4 bg-white/10 rounded w-3/4"></div>
              </div>
              <div className="mt-4 pt-4 border-t border-white/10">
                <div className="flex items-center justify-between">
                  <div className="h-6 bg-white/10 rounded w-20"></div>
                  <div className="h-4 bg-white/10 rounded w-24"></div>
                </div>
              </div>
            </div>
          </div>
        ))}
        <span className="sr-only">Loading projects...</span>
      </div>
    );
  }

  if (projects.length === 0) {
    return (
      <div className="text-center py-8 sm:py-12 px-4">
        <div className="mx-auto w-20 h-20 sm:w-24 sm:h-24 bg-white/5 backdrop-blur-md border border-white/10 rounded-full flex items-center justify-center mb-4">
          <svg className="w-10 h-10 sm:w-12 sm:h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 className="text-base sm:text-lg font-medium text-white mb-2">No projects yet</h3>
        <p className="text-sm sm:text-base text-gray-400 mb-6 max-w-md mx-auto">
          Get started by creating your first AI-generated document project.
        </p>
      </div>
    );
  }

  return (
    <div 
      className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6"
      role="list"
      aria-label="Project list"
    >
      {projects.map((project) => (
        <ProjectCard
          key={project.id}
          project={project}
          onDelete={onDeleteProject}
          onSelect={onSelectProject}
        />
      ))}
    </div>
  );
}