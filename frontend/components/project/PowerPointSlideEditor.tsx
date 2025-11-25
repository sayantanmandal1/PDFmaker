'use client';

import { useState } from 'react';
import { SlideConfig } from '@/types';

interface PowerPointSlideEditorProps {
  slides: SlideConfig[];
  onSlidesChange: (slides: SlideConfig[]) => void;
  onSave: () => void;
  isSaving: boolean;
  saveSuccess: boolean;
}

export function PowerPointSlideEditor({
  slides,
  onSlidesChange,
  onSave,
  isSaving,
  saveSuccess,
}: PowerPointSlideEditorProps) {
  const [slideCount, setSlideCount] = useState<string>(
    slides.length > 0 ? slides.length.toString() : ''
  );

  const handleSlideCountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSlideCount(value);

    const count = parseInt(value, 10);
    if (!isNaN(count) && count > 0 && count <= 100) {
      // Create or adjust slides array
      const newSlides: SlideConfig[] = [];
      for (let i = 0; i < count; i++) {
        newSlides.push({
          title: slides[i]?.title || '',
          position: i,
        });
      }
      onSlidesChange(newSlides);
    } else if (value === '') {
      // Clear slides if input is empty
      onSlidesChange([]);
    }
  };

  const handleSlideTitleChange = (index: number, title: string) => {
    const updatedSlides = slides.map((slide, i) =>
      i === index ? { ...slide, title } : slide
    );
    onSlidesChange(updatedSlides);
  };

  return (
    <div className="space-y-4 sm:space-y-6 bg-white/5 backdrop-blur-md border border-white/10 rounded-xl p-4 sm:p-6">
      <div>
        <h3 className="text-base sm:text-lg font-semibold text-white mb-2 sm:mb-4">
          Presentation Configuration
        </h3>
        <p className="text-xs sm:text-sm text-gray-300 mb-4">
          Specify the number of slides and provide a title for each slide in your PowerPoint presentation.
        </p>
      </div>

      {/* Slide Count Input */}
      <div className="space-y-2">
        <label
          htmlFor="slideCount"
          className="block text-sm font-medium text-gray-200"
        >
          Number of Slides
        </label>
        <input
          id="slideCount"
          type="number"
          min="1"
          max="100"
          value={slideCount}
          onChange={handleSlideCountChange}
          placeholder="Enter number of slides (e.g., 10)"
          className="w-full px-3 sm:px-4 py-2 text-sm sm:text-base bg-black/40 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/50 focus:border-red-500/50 focus:bg-white/5 transition-all duration-200"
          disabled={isSaving}
          aria-describedby="slide-count-help"
        />
        <p id="slide-count-help" className="text-xs text-gray-400">
          Enter a number between 1 and 100
        </p>
      </div>

      {/* Slide Titles */}
      {slides.length > 0 && (
        <div className="space-y-3 sm:space-y-4">
          <h4 className="text-sm sm:text-base font-medium text-white">
            Slide Titles ({slides.length} slides)
          </h4>
          <div className="space-y-2 sm:space-y-3" role="list" aria-label="Slide titles">
            {slides.map((slide, index) => (
              <div key={index} className="flex items-center gap-2 sm:gap-3 p-2 sm:p-3 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg hover:bg-white/10 hover:border-white/20 transition-all duration-200" role="listitem">
                <div className="shrink-0 w-10 sm:w-12 text-center">
                  <span 
                    className="inline-flex items-center justify-center w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-gradient-to-r from-red-500/20 to-yellow-500/20 border border-red-500/30 text-yellow-400 text-xs sm:text-sm font-medium"
                    aria-label={`Slide ${index + 1}`}
                  >
                    {index + 1}
                  </span>
                </div>
                <label htmlFor={`slide-title-${index}`} className="sr-only">
                  Slide {index + 1} title
                </label>
                <input
                  id={`slide-title-${index}`}
                  type="text"
                  value={slide.title}
                  onChange={(e) => handleSlideTitleChange(index, e.target.value)}
                  placeholder={`Slide ${index + 1} title`}
                  className="flex-1 px-3 sm:px-4 py-2 text-sm sm:text-base bg-black/40 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500/50 focus:border-red-500/50 focus:bg-white/5 transition-all duration-200"
                  disabled={isSaving}
                  aria-label={`Title for slide ${index + 1}`}
                />
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {slides.length === 0 && slideCount === '' && (
        <div className="text-center py-8 sm:py-12 bg-white/5 backdrop-blur-sm border-2 border-dashed border-white/10 rounded-lg">
          <p className="text-sm sm:text-base text-gray-400 px-4">
            Enter the number of slides above to get started.
          </p>
        </div>
      )}

      {/* Save Button */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-4 pt-4 border-t border-white/10">
        <button
          onClick={onSave}
          disabled={slides.length === 0 || isSaving}
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
