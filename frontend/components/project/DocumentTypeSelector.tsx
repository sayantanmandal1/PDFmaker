'use client';

interface DocumentTypeSelectorProps {
  value: 'word' | 'powerpoint';
  onChange: (type: 'word' | 'powerpoint') => void;
  disabled?: boolean;
}

export function DocumentTypeSelector({ value, onChange, disabled }: DocumentTypeSelectorProps) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-300 mb-4">
        Document Type
      </label>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* Word Document Card */}
        <label 
          className={`
            relative flex flex-col items-center p-6 
            bg-white/5 backdrop-blur-md border-2 rounded-lg 
            cursor-pointer transition-all duration-200
            hover:scale-105 hover:bg-white/10 hover:shadow-xl hover:shadow-red-500/20
            ${value === 'word' 
              ? 'border-red-500 shadow-lg shadow-red-500/30 bg-white/10' 
              : 'border-white/20 hover:border-white/30'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <input
            type="radio"
            name="document_type"
            value="word"
            checked={value === 'word'}
            onChange={(e) => onChange(e.target.value as 'word' | 'powerpoint')}
            disabled={disabled}
            className="sr-only"
          />
          
          {/* Icon with gradient accent */}
          <div className={`
            text-5xl mb-4 transition-all duration-200
            ${value === 'word' ? 'scale-110' : ''}
          `}>
            <div className={`
              inline-block p-3 rounded-lg
              ${value === 'word' 
                ? 'bg-gradient-to-br from-red-500/20 to-yellow-500/20' 
                : 'bg-white/5'
              }
            `}>
              📄
            </div>
          </div>
          
          <div className="text-center">
            <div className={`
              text-base font-semibold mb-2 transition-colors duration-200
              ${value === 'word' ? 'text-white' : 'text-gray-200'}
            `}>
              Word Document
            </div>
            <div className="text-xs text-gray-400">
              Create a structured document with sections
            </div>
          </div>
          
          {/* Selected indicator */}
          {value === 'word' && (
            <div className="absolute top-3 right-3">
              <svg
                className="w-6 h-6 text-red-500"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
          )}
        </label>
        
        {/* PowerPoint Card */}
        <label 
          className={`
            relative flex flex-col items-center p-6 
            bg-white/5 backdrop-blur-md border-2 rounded-lg 
            cursor-pointer transition-all duration-200
            hover:scale-105 hover:bg-white/10 hover:shadow-xl hover:shadow-yellow-500/20
            ${value === 'powerpoint' 
              ? 'border-yellow-500 shadow-lg shadow-yellow-500/30 bg-white/10' 
              : 'border-white/20 hover:border-white/30'
            }
            ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <input
            type="radio"
            name="document_type"
            value="powerpoint"
            checked={value === 'powerpoint'}
            onChange={(e) => onChange(e.target.value as 'word' | 'powerpoint')}
            disabled={disabled}
            className="sr-only"
          />
          
          {/* Icon with gradient accent */}
          <div className={`
            text-5xl mb-4 transition-all duration-200
            ${value === 'powerpoint' ? 'scale-110' : ''}
          `}>
            <div className={`
              inline-block p-3 rounded-lg
              ${value === 'powerpoint' 
                ? 'bg-gradient-to-br from-yellow-500/20 to-red-500/20' 
                : 'bg-white/5'
              }
            `}>
              📊
            </div>
          </div>
          
          <div className="text-center">
            <div className={`
              text-base font-semibold mb-2 transition-colors duration-200
              ${value === 'powerpoint' ? 'text-white' : 'text-gray-200'}
            `}>
              PowerPoint Presentation
            </div>
            <div className="text-xs text-gray-400">
              Create a slide-based presentation
            </div>
          </div>
          
          {/* Selected indicator */}
          {value === 'powerpoint' && (
            <div className="absolute top-3 right-3">
              <svg
                className="w-6 h-6 text-yellow-500"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
            </div>
          )}
        </label>
      </div>
    </div>
  );
}
