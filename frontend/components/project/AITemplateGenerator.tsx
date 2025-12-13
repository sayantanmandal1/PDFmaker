'use client';

import { useState } from 'react';
import { SectionConfig, SlideConfig } from '@/types';

interface AITemplateGeneratorProps {
  projectId: string;
  documentType: 'word' | 'powerpoint';
  topic: string;
  onTemplateAccepted: (items: string[]) => void;
  disabled?: boolean;
}

export function AITemplateGenerator({
  projectId,
  documentType,
  topic,
  onTemplateAccepted,
  disabled = false,
}: AITemplateGeneratorProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedTemplate, setGeneratedTemplate] = useState<string[] | null>(null);
  const [editableTemplate, setEditableTemplate] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);

  const handleGenerate = async () => {
    try {
      setIsGenerating(true);
      setError(null);
      setGeneratedTemplate(null);

      const { projectsApi } = await import('@/lib/projects-api');
      
      const data = await projectsApi.generateTemplate(projectId, {
        topic,
        document_type: documentType,
      });
      
      const items = documentType === 'word' 
        ? data.template.headers 
        : data.template.slide_titles;
      
      setGeneratedTemplate(items || []);
      setEditableTemplate([...(items || [])]);
    } catch (err: any) {
      console.error('Template generation error:', err);
      
      // Handle different error types
      let errorMessage = 'Failed to generate template';
      
      if (err && typeof err === 'object') {
        if (err.detail) {
          errorMessage = err.detail;
        } else if (err.message) {
          errorMessage = err.message;
        } else if (typeof err === 'string') {
          errorMessage = err;
        }
      } else if (typeof err === 'string') {
        errorMessage = err;
      }
      
      setError(errorMessage);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleAccept = () => {
    if (isEditing) {
      // Accept edited template
      onTemplateAccepted(editableTemplate);
    } else {
      // Accept original template
      onTemplateAccepted(generatedTemplate || []);
    }
    handleDiscard();
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleDiscard = () => {
    setGeneratedTemplate(null);
    setEditableTemplate([]);
    setIsEditing(false);
    setError(null);
  };

  const handleItemChange = (index: number, value: string) => {
    const updated = [...editableTemplate];
    updated[index] = value;
    setEditableTemplate(updated);
  };

  const handleAddItem = () => {
    setEditableTemplate([...editableTemplate, '']);
  };

  const handleRemoveItem = (index: number) => {
    const updated = editableTemplate.filter((_, i) => i !== index);
    setEditableTemplate(updated);
  };

  const itemLabel = documentType === 'word' ? 'Section Header' : 'Slide Title';
  const itemsLabel = documentType === 'word' ? 'Section Headers' : 'Slide Titles';

  return (
    <div className="space-y-4">
      {/* Generate Button - Prominent Glassmorphic Panel */}
      {!generatedTemplate && (
        <div className="bg-gradient-to-br from-red-500/10 to-yellow-500/10 backdrop-blur-md border border-white/20 rounded-lg p-6 shadow-lg shadow-red-500/10">
          <div className="flex items-start gap-4">
            <div className="shrink-0">
              <div className="p-3 bg-gradient-to-br from-red-500/20 to-yellow-500/20 rounded-lg">
                <svg
                  className="w-6 h-6 text-yellow-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                  />
                </svg>
              </div>
            </div>
            <div className="flex-1">
              <h4 className="text-lg font-semibold text-white mb-2">
                AI-Powered Template Generation
              </h4>
              <p className="text-sm text-gray-300 mb-4">
                Let AI suggest a document structure based on your topic: <span className="text-yellow-400 font-medium">"{topic}"</span>. 
                You can review, edit, or discard the suggestions before applying them.
              </p>
              <button
                onClick={handleGenerate}
                disabled={isGenerating || disabled}
                className="
                  px-6 py-2.5 
                  bg-gradient-to-r from-red-500 to-yellow-500 
                  text-white font-medium rounded-lg 
                  hover:from-red-600 hover:to-yellow-600 
                  hover:scale-105 hover:shadow-lg hover:shadow-red-500/50
                  disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
                  transition-all duration-200
                  focus:outline-none focus:ring-2 focus:ring-red-500/50 focus:ring-offset-2 focus:ring-offset-black
                "
              >
                {isGenerating ? (
                  <span className="flex items-center gap-2">
                    <div
                      className="w-5 h-5 border-2 border-transparent border-t-white border-r-white rounded-full animate-spin"
                    />
                    Generating Template...
                  </span>
                ) : (
                  'Generate Template with AI'
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Error Message - Red-tinted Glassmorphic */}
      {error && (
        <div className="bg-red-500/10 backdrop-blur-md border border-red-500/30 rounded-lg p-4 shadow-lg shadow-red-500/10">
          <div className="flex items-start gap-3">
            <svg
              className="w-5 h-5 text-red-400 shrink-0 mt-0.5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
            <div className="flex-1">
              <p className="text-sm text-red-300">{error}</p>
              <button
                onClick={handleGenerate}
                className="mt-2 text-sm text-red-400 hover:text-red-300 font-medium transition-colors duration-200"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Generated Template Display - Glassmorphic Card */}
      {generatedTemplate && !isEditing && (
        <div className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 backdrop-blur-md border border-green-500/30 rounded-lg p-6 shadow-lg shadow-green-500/10">
          <div className="mb-4">
            <h4 className="text-lg font-semibold text-white mb-2">
              AI-Generated {itemsLabel}
            </h4>
            <p className="text-sm text-gray-300">
              Review the suggested structure below. You can accept it as-is, edit it, or discard it.
            </p>
          </div>

          <div className="space-y-2 mb-6">
            {generatedTemplate.map((item, index) => (
              <div
                key={index}
                className="flex items-center gap-3 p-3 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg hover:bg-white/10 transition-all duration-200"
              >
                <span className="shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-gradient-to-br from-green-500/30 to-emerald-500/30 text-green-300 text-sm font-medium border border-green-500/30">
                  {index + 1}
                </span>
                <span className="flex-1 text-white">{item}</span>
              </div>
            ))}
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              onClick={handleAccept}
              className="
                px-6 py-2 
                bg-gradient-to-r from-green-500 to-emerald-500 
                text-white font-medium rounded-lg 
                hover:from-green-600 hover:to-emerald-600 
                hover:scale-105 hover:shadow-lg hover:shadow-green-500/50
                transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:ring-offset-2 focus:ring-offset-black
              "
            >
              Accept Template
            </button>
            <button
              onClick={handleEdit}
              className="
                px-6 py-2 
                bg-white/5 backdrop-blur-md border border-white/20 
                text-white font-medium rounded-lg 
                hover:bg-white/10 hover:border-white/30 
                hover:scale-105 hover:shadow-lg hover:shadow-white/10
                transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-white/50 focus:ring-offset-2 focus:ring-offset-black
              "
            >
              Edit Template
            </button>
            <button
              onClick={handleDiscard}
              className="
                px-6 py-2 
                bg-transparent border border-white/30 
                text-gray-300 font-medium rounded-lg 
                hover:bg-white/5 hover:border-white/40 hover:text-white
                transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-white/50 focus:ring-offset-2 focus:ring-offset-black
              "
            >
              Discard
            </button>
          </div>
        </div>
      )}

      {/* Template Editing Interface - Glassmorphic Card */}
      {isEditing && (
        <div className="bg-white/5 backdrop-blur-md border border-white/20 rounded-lg p-6 shadow-lg shadow-black/20">
          <div className="mb-4">
            <h4 className="text-lg font-semibold text-white mb-2">
              Edit {itemsLabel}
            </h4>
            <p className="text-sm text-gray-300">
              Modify the suggested {itemsLabel.toLowerCase()} below. You can edit, add, or remove items.
            </p>
          </div>

          <div className="space-y-3 mb-6">
            {editableTemplate.map((item, index) => (
              <div key={index} className="flex items-center gap-3">
                <span className="shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-gradient-to-br from-red-500/30 to-yellow-500/30 text-yellow-300 text-sm font-medium border border-yellow-500/30">
                  {index + 1}
                </span>
                <input
                  type="text"
                  value={item}
                  onChange={(e) => handleItemChange(index, e.target.value)}
                  placeholder={`${itemLabel} ${index + 1}`}
                  className="
                    flex-1 px-4 py-2.5
                    bg-black/40 
                    border border-white/20 
                    rounded-lg 
                    text-white placeholder-gray-500
                    transition-all duration-200
                    focus:outline-none 
                    focus:bg-white/5 
                    focus:backdrop-blur-md
                    focus:border-transparent
                    focus:ring-2 
                    focus:ring-red-500/50 
                    focus:shadow-lg 
                    focus:shadow-red-500/20
                  "
                />
                <button
                  onClick={() => handleRemoveItem(index)}
                  className="
                    p-2 text-red-400 
                    hover:text-red-300 hover:bg-red-500/10 
                    rounded-lg transition-all duration-200
                    focus:outline-none focus:ring-2 focus:ring-red-500/50
                  "
                  title="Remove"
                  aria-label={`Remove ${itemLabel} ${index + 1}`}
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              </div>
            ))}
          </div>

          <button
            onClick={handleAddItem}
            className="
              mb-6 px-4 py-2 
              bg-white/5 border border-white/20 
              text-gray-300 font-medium rounded-lg 
              hover:bg-white/10 hover:border-white/30 hover:text-white
              transition-all duration-200
              focus:outline-none focus:ring-2 focus:ring-white/50 focus:ring-offset-2 focus:ring-offset-black
            "
          >
            + Add {itemLabel}
          </button>

          <div className="flex flex-wrap gap-3 pt-4 border-t border-white/10">
            <button
              onClick={handleAccept}
              disabled={editableTemplate.some(item => !item.trim())}
              className="
                px-6 py-2 
                bg-gradient-to-r from-green-500 to-emerald-500 
                text-white font-medium rounded-lg 
                hover:from-green-600 hover:to-emerald-600 
                hover:scale-105 hover:shadow-lg hover:shadow-green-500/50
                disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
                transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:ring-offset-2 focus:ring-offset-black
              "
            >
              Accept Edited Template
            </button>
            <button
              onClick={handleDiscard}
              className="
                px-6 py-2 
                bg-transparent border border-white/30 
                text-gray-300 font-medium rounded-lg 
                hover:bg-white/5 hover:border-white/40 hover:text-white
                transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-white/50 focus:ring-offset-2 focus:ring-offset-black
              "
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
