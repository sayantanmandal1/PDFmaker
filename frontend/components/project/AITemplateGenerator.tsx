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
      setError(err.detail || err.message || 'Failed to generate template');
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
      {/* Generate Button */}
      {!generatedTemplate && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-start gap-4">
            <div className="shrink-0">
              <svg
                className="w-6 h-6 text-blue-600"
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
            <div className="flex-1">
              <h4 className="text-lg font-semibold text-gray-900 mb-2">
                AI-Powered Template Generation
              </h4>
              <p className="text-sm text-gray-700 mb-4">
                Let AI suggest a document structure based on your topic: "{topic}". 
                You can review, edit, or discard the suggestions before applying them.
              </p>
              <button
                onClick={handleGenerate}
                disabled={isGenerating || disabled}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
              >
                {isGenerating ? (
                  <span className="flex items-center gap-2">
                    <svg
                      className="animate-spin h-5 w-5"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
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

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <svg
              className="w-5 h-5 text-red-600 shrink-0 mt-0.5"
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
              <p className="text-sm text-red-800">{error}</p>
              <button
                onClick={handleGenerate}
                className="mt-2 text-sm text-red-600 hover:text-red-800 font-medium"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Generated Template Display */}
      {generatedTemplate && !isEditing && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <div className="mb-4">
            <h4 className="text-lg font-semibold text-gray-900 mb-2">
              AI-Generated {itemsLabel}
            </h4>
            <p className="text-sm text-gray-700">
              Review the suggested structure below. You can accept it as-is, edit it, or discard it.
            </p>
          </div>

          <div className="space-y-2 mb-6">
            {generatedTemplate.map((item, index) => (
              <div
                key={index}
                className="flex items-center gap-3 p-3 bg-white border border-gray-200 rounded-lg"
              >
                <span className="shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-green-100 text-green-800 text-sm font-medium">
                  {index + 1}
                </span>
                <span className="flex-1 text-gray-900">{item}</span>
              </div>
            ))}
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleAccept}
              className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors font-medium"
            >
              Accept Template
            </button>
            <button
              onClick={handleEdit}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
            >
              Edit Template
            </button>
            <button
              onClick={handleDiscard}
              className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors font-medium"
            >
              Discard
            </button>
          </div>
        </div>
      )}

      {/* Template Editing Interface */}
      {isEditing && (
        <div className="bg-white border border-gray-300 rounded-lg p-6">
          <div className="mb-4">
            <h4 className="text-lg font-semibold text-gray-900 mb-2">
              Edit {itemsLabel}
            </h4>
            <p className="text-sm text-gray-600">
              Modify the suggested {itemsLabel.toLowerCase()} below. You can edit, add, or remove items.
            </p>
          </div>

          <div className="space-y-3 mb-6">
            {editableTemplate.map((item, index) => (
              <div key={index} className="flex items-center gap-3">
                <span className="shrink-0 w-8 h-8 flex items-center justify-center rounded-full bg-blue-100 text-blue-800 text-sm font-medium">
                  {index + 1}
                </span>
                <input
                  type="text"
                  value={item}
                  onChange={(e) => handleItemChange(index, e.target.value)}
                  placeholder={`${itemLabel} ${index + 1}`}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <button
                  onClick={() => handleRemoveItem(index)}
                  className="p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded transition-colors"
                  title="Remove"
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
            className="mb-6 px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors font-medium"
          >
            + Add {itemLabel}
          </button>

          <div className="flex gap-3 pt-4 border-t border-gray-200">
            <button
              onClick={handleAccept}
              disabled={editableTemplate.some(item => !item.trim())}
              className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium"
            >
              Accept Edited Template
            </button>
            <button
              onClick={handleDiscard}
              className="px-6 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors font-medium"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
