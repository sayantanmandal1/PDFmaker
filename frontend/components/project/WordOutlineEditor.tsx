'use client';

import { useState } from 'react';
import { SectionConfig } from '@/types';

interface WordOutlineEditorProps {
  sections: SectionConfig[];
  onSectionsChange: (sections: SectionConfig[]) => void;
  onSave: () => void;
  isSaving: boolean;
  saveSuccess: boolean;
}

export function WordOutlineEditor({
  sections,
  onSectionsChange,
  onSave,
  isSaving,
  saveSuccess,
}: WordOutlineEditorProps) {
  const [newSectionHeader, setNewSectionHeader] = useState('');

  const handleAddSection = () => {
    if (newSectionHeader.trim()) {
      const newSection: SectionConfig = {
        header: newSectionHeader.trim(),
        position: sections.length,
      };
      onSectionsChange([...sections, newSection]);
      setNewSectionHeader('');
    }
  };

  const handleRemoveSection = (index: number) => {
    const updatedSections = sections
      .filter((_, i) => i !== index)
      .map((section, i) => ({ ...section, position: i }));
    onSectionsChange(updatedSections);
  };

  const handleMoveUp = (index: number) => {
    if (index === 0) return;
    const updatedSections = [...sections];
    [updatedSections[index - 1], updatedSections[index]] = [
      updatedSections[index],
      updatedSections[index - 1],
    ];
    const reindexed = updatedSections.map((section, i) => ({
      ...section,
      position: i,
    }));
    onSectionsChange(reindexed);
  };

  const handleMoveDown = (index: number) => {
    if (index === sections.length - 1) return;
    const updatedSections = [...sections];
    [updatedSections[index], updatedSections[index + 1]] = [
      updatedSections[index + 1],
      updatedSections[index],
    ];
    const reindexed = updatedSections.map((section, i) => ({
      ...section,
      position: i,
    }));
    onSectionsChange(reindexed);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleAddSection();
    }
  };

  return (
    <div className="space-y-4 sm:space-y-6">
      <div>
        <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-2 sm:mb-4">
          Document Outline
        </h3>
        <p className="text-xs sm:text-sm text-gray-600 mb-4">
          Add section headers to structure your Word document. You can reorder them using the arrow buttons.
        </p>
      </div>

      {/* Add Section Input */}
      <div className="flex flex-col sm:flex-row gap-2">
        <label htmlFor="new-section-header" className="sr-only">New section header</label>
        <input
          id="new-section-header"
          type="text"
          value={newSectionHeader}
          onChange={(e) => setNewSectionHeader(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Enter section header (e.g., Introduction, Background)"
          className="flex-1 px-3 sm:px-4 py-2 text-sm sm:text-base border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          disabled={isSaving}
          aria-label="Section header"
        />
        <button
          onClick={handleAddSection}
          disabled={!newSectionHeader.trim() || isSaving}
          className="px-4 sm:px-6 py-2 text-sm sm:text-base bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 whitespace-nowrap"
        >
          Add Section
        </button>
      </div>

      {/* Sections List */}
      {sections.length > 0 ? (
        <div className="space-y-2" role="list" aria-label="Document sections">
          {sections.map((section, index) => (
            <div
              key={index}
              className="flex items-center gap-2 sm:gap-3 p-3 sm:p-4 bg-white border border-gray-200 rounded-lg hover:border-gray-300 transition-colors"
              role="listitem"
            >
              <div className="flex-1 min-w-0">
                <span className="text-sm sm:text-base text-gray-900 font-medium break-words">
                  {index + 1}. {section.header}
                </span>
              </div>

              {/* Reorder Buttons */}
              <div className="flex gap-1 shrink-0">
                <button
                  onClick={() => handleMoveUp(index)}
                  disabled={index === 0 || isSaving}
                  className="p-1.5 sm:p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded disabled:text-gray-300 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
                  aria-label={`Move section ${index + 1} up`}
                  title="Move up"
                >
                  <svg
                    className="w-4 h-4 sm:w-5 sm:h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 15l7-7 7 7"
                    />
                  </svg>
                </button>
                <button
                  onClick={() => handleMoveDown(index)}
                  disabled={index === sections.length - 1 || isSaving}
                  className="p-1.5 sm:p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded disabled:text-gray-300 disabled:cursor-not-allowed transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
                  aria-label={`Move section ${index + 1} down`}
                  title="Move down"
                >
                  <svg
                    className="w-4 h-4 sm:w-5 sm:h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    aria-hidden="true"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </button>
              </div>

              {/* Delete Button */}
              <button
                onClick={() => handleRemoveSection(index)}
                disabled={isSaving}
                className="p-1.5 sm:p-2 text-red-600 hover:text-red-800 hover:bg-red-50 rounded disabled:text-gray-300 disabled:cursor-not-allowed transition-colors shrink-0 focus:outline-none focus:ring-2 focus:ring-red-500"
                aria-label={`Remove section ${index + 1}`}
                title="Remove section"
              >
                <svg
                  className="w-4 h-4 sm:w-5 sm:h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
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
      ) : (
        <div className="text-center py-8 sm:py-12 bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg">
          <p className="text-sm sm:text-base text-gray-500 px-4">
            No sections added yet. Add your first section header above.
          </p>
        </div>
      )}

      {/* Save Button */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4 pt-4 border-t border-gray-200">
        <button
          onClick={onSave}
          disabled={sections.length === 0 || isSaving}
          className="w-full sm:w-auto px-6 sm:px-8 py-2.5 sm:py-3 text-sm sm:text-base bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          aria-busy={isSaving}
        >
          {isSaving ? 'Saving...' : 'Save Configuration'}
        </button>

        {saveSuccess && (
          <div 
            className="flex items-center gap-2 text-green-600"
            role="status"
            aria-live="polite"
          >
            <svg
              className="w-5 h-5 shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
            <span className="text-sm sm:text-base font-medium">Configuration saved successfully!</span>
          </div>
        )}
      </div>
    </div>
  );
}
