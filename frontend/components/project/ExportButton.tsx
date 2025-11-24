'use client';

import { useState } from 'react';
import { projectsApi } from '@/lib/projects-api';
import { useToast } from '@/contexts/ToastContext';
import { ApiError } from '@/types';
import { LoadingSpinner } from '@/components/common';

interface ExportButtonProps {
  projectId: string;
  projectName: string;
  documentType: 'word' | 'powerpoint';
}

export default function ExportButton({ projectId, projectName, documentType }: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);
  const { showSuccess, showError } = useToast();

  const handleExport = async () => {
    try {
      setIsExporting(true);

      // Call the export API
      const blob = await projectsApi.exportProject(projectId);

      // Create a download link and trigger download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Set filename based on document type
      const extension = documentType === 'word' ? 'docx' : 'pptx';
      link.download = `${projectName.replace(/\s+/g, '_')}.${extension}`;
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      // Show success message
      showSuccess('Document exported successfully!');

    } catch (err) {
      console.error('Export error:', err);
      const apiError = err as ApiError;
      showError(apiError.detail || 'Failed to export document. Please try again.');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <button
      onClick={handleExport}
      disabled={isExporting}
      className={`flex items-center px-4 sm:px-6 py-2 sm:py-2.5 rounded-md text-sm sm:text-base font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 ${
        isExporting
          ? 'bg-gray-400 text-white cursor-not-allowed'
          : 'bg-green-600 text-white hover:bg-green-700'
      }`}
      aria-busy={isExporting}
      aria-label={`Export ${documentType === 'word' ? 'document' : 'presentation'}`}
    >
      {isExporting ? (
        <>
          <div className="mr-2">
            <LoadingSpinner size="sm" label="Exporting" />
          </div>
          <span>Exporting...</span>
        </>
      ) : (
        <>
          <svg
            className="w-4 h-4 sm:w-5 sm:h-5 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
            />
          </svg>
          <span className="hidden sm:inline">Export {documentType === 'word' ? 'Document' : 'Presentation'}</span>
          <span className="sm:hidden">Export</span>
        </>
      )}
    </button>
  );
}
