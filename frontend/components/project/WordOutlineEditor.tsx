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
    <div className="space-y-4 sm:space-y-6 bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-4 sm:p-6">
      <div>
        <h3 className="text-base sm:text-lg font-semibold text-white mb-2 sm:mb-4">
          Document Outline
        </h3>
        <p className="text-xs sm:text-sm text-gray-300 mb-4">
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
          className="flex-1 px-3 sm:px-4 py-2 text-sm sm:text-base bg-black/40 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/50 focus:border-red-500/50 focus:bg-white/5 transition-all duration-200"
          disabled={isSaving}
          aria-label="Section header"
        />
        <button
          onClick={handleAddSection}
          disabled={!newSectionHeader.trim() || isSaving}
          className="px-4 sm:px-6 py-2 text-sm sm:text-base bg-gradient-to-r from-red-500 to-yellow-500 text-white rounded-lg hover:from-red-600 hover:to-yellow-600 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed transition-all duration-200 font-medium focus:outline-none focus:ring-2 focus:ring-red-500/50 whitespace-nowrap"
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
              className="flex items-center gap-2 sm:gap-3 p-3 sm:p-4 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg hover:bg-white/10 hover:border-white/20 hover:scale-[1.01] transition-all duration-200"
              role="listitem"
            >
              <div className="flex-1 min-w-0">
                <span className="text-sm sm:text-base text-white font-medium break-words">
                  {index + 1}. {section.header}
                </span>
              </div>

              {/* Reorder Buttons */}
              <div className="flex gap-1 shrink-0">
                <button
                  onClick={() => handleMoveUp(index)}
                  disabled={index === 0 || isSaving}
                  className="p-1.5 sm:p-2 text-gray-300 hover:text-white hover:bg-white/10 rounded disabled:text-gray-600 disabled:cursor-not-allowed transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-red-500/50"
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
                  className="p-1.5 sm:p-2 text-gray-300 hover:text-white hover:bg-white/10 rounded disabled:text-gray-600 disabled:cursor-not-allowed transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-red-500/50"
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
                className="p-1.5 sm:p-2 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded disabled:text-gray-600 disabled:cursor-not-allowed transition-all duration-200 shrink-0 focus:outline-none focus:ring-2 focus:ring-red-500/50"
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
        <div className="text-center py-8 sm:py-12 bg-white/5 backdrop-blur-sm border-2 border-dashed border-white/10 rounded-lg">
          <p className="text-sm sm:text-base text-gray-400 px-4">
            No sections added yet. Add your first section header above.
          </p>
        </div>
      )}

      {/* Save Button */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4 pt-4 border-t border-white/10">
        <button
          onClick={onSave}
          disabled={sections.length === 0 || isSaving}
          className="w-full sm:w-auto px-6 sm:px-8 py-2.5 sm:py-3 text-sm sm:text-base bg-gradient-to-r from-red-500 to-yellow-500 text-white rounded-lg hover:from-red-600 hover:to-yellow-600 disabled:from-gray-600 disabled:to-gray-600 disabled:cursor-not-allowed transition-all duration-200 font-medium focus:outline-none focus:ring-2 focus:ring-red-500/50"
          aria-busy={isSaving}
        >
          {isSaving ? 'Saving...' : 'Save Configuration'}
        </button>

        {saveSuccess && (
          <div 
            className="flex items-center gap-2 text-yellow-400"
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
