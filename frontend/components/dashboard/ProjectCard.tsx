'use client';

import { Project } from '@/types';
import { formatDistanceToNow } from 'date-fns';

interface ProjectCardProps {
  project: Project;
  onDelete: (projectId: string) => void;
  onSelect: (projectId: string) => void;
}

export function ProjectCard({ project, onDelete, onSelect }: ProjectCardProps) {
  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm(`Are you sure you want to delete "${project.name}"?`)) {
      onDelete(project.id);
    }
  };

  const getDocumentTypeIcon = () => {
    return project.document_type === 'word' ? '📄' : '📊';
  };

  const getStatusColor = () => {
    switch (project.status) {
      case 'configuring':
        return 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30';
      case 'generating':
        return 'bg-blue-500/20 text-blue-400 border border-blue-500/30';
      case 'ready':
        return 'bg-green-500/20 text-green-400 border border-green-500/30';
      case 'ready_for_refinement':
        return 'bg-amber-500/20 text-amber-400 border border-amber-500/30';
      case 'partially_generated':
        return 'bg-purple-500/20 text-purple-400 border border-purple-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border border-gray-500/30';
    }
  };

  return (
    <article
      className="bg-white/5 backdrop-blur-md rounded-xl border border-white/10 cursor-pointer transition-all duration-300 hover:scale-105 hover:shadow-xl hover:shadow-red-500/20 hover:border-red-500/30 focus-within:ring-2 focus-within:ring-red-500/50 group"
      onClick={() => onSelect(project.id)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onSelect(project.id);
        }
      }}
      aria-label={`Open project ${project.name}`}
    >
      <div className="p-4 sm:p-6">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center space-x-2 sm:space-x-3 min-w-0 flex-1">
            <div className="text-xl sm:text-2xl shrink-0 bg-gradient-to-br from-red-500 to-yellow-500 p-2 rounded-lg" aria-hidden="true">
              {getDocumentTypeIcon()}
            </div>
            <div className="min-w-0 flex-1">
              <h3 className="text-base sm:text-lg font-semibold text-white truncate group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-red-400 group-hover:to-yellow-400 group-hover:bg-clip-text transition-all duration-300">
                {project.name}
              </h3>
              <p className="text-xs sm:text-sm text-gray-400 capitalize">
                {project.document_type} Document
              </p>
            </div>
          </div>
          <button
            onClick={handleDelete}
            className="text-gray-400 hover:text-red-400 transition-all duration-300 p-1 shrink-0 focus:outline-none focus:ring-2 focus:ring-red-500 rounded hover:scale-110"
            aria-label={`Delete project ${project.name}`}
            title="Delete project"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>

        <div className="mt-3 sm:mt-4">
          <p className="text-xs sm:text-sm text-gray-300 line-clamp-2">
            {project.topic}
          </p>
        </div>

        {/* Glassmorphic Footer */}
        <div className="mt-3 sm:mt-4 pt-3 sm:pt-4 border-t border-white/10 bg-white/5 -mx-4 sm:-mx-6 px-4 sm:px-6 py-3 rounded-b-xl">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <span 
              className={`inline-flex items-center px-2.5 py-1 rounded-lg text-xs font-medium ${getStatusColor()}`}
              aria-label={`Project status: ${project.status}`}
            >
              {project.status.replace(/_/g, ' ')}
            </span>
            <div className="text-xs text-gray-400">
              <span className="sr-only">Last updated: </span>
              Updated {formatDistanceToNow(new Date(project.updated_at), { addSuffix: true })}
            </div>
          </div>
        </div>
      </div>
    </article>
  );
}