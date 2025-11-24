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
        return 'bg-yellow-100 text-yellow-800';
      case 'generating':
        return 'bg-blue-100 text-blue-800';
      case 'ready':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <article
      className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer border border-gray-200 focus-within:ring-2 focus-within:ring-blue-500"
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
            <span className="text-xl sm:text-2xl shrink-0" aria-hidden="true">
              {getDocumentTypeIcon()}
            </span>
            <div className="min-w-0 flex-1">
              <h3 className="text-base sm:text-lg font-semibold text-gray-900 truncate">
                {project.name}
              </h3>
              <p className="text-xs sm:text-sm text-gray-600 capitalize">
                {project.document_type} Document
              </p>
            </div>
          </div>
          <button
            onClick={handleDelete}
            className="text-gray-400 hover:text-red-600 transition-colors p-1 shrink-0 focus:outline-none focus:ring-2 focus:ring-red-500 rounded"
            aria-label={`Delete project ${project.name}`}
            title="Delete project"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>

        <div className="mt-3 sm:mt-4">
          <p className="text-xs sm:text-sm text-gray-700 line-clamp-2">
            {project.topic}
          </p>
        </div>

        <div className="mt-3 sm:mt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <span 
            className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor()}`}
            aria-label={`Project status: ${project.status}`}
          >
            {project.status}
          </span>
          <div className="text-xs text-gray-500">
            <span className="sr-only">Last updated: </span>
            Updated {formatDistanceToNow(new Date(project.updated_at), { addSuffix: true })}
          </div>
        </div>
      </div>
    </article>
  );
}