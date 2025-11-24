'use client';

interface DocumentTypeSelectorProps {
  value: 'word' | 'powerpoint';
  onChange: (type: 'word' | 'powerpoint') => void;
  disabled?: boolean;
}

export function DocumentTypeSelector({ value, onChange, disabled }: DocumentTypeSelectorProps) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-3">
        Document Type
      </label>
      <div className="space-y-3">
        <label className="flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all hover:bg-gray-50 has-[:checked]:border-blue-500 has-[:checked]:bg-blue-50">
          <input
            type="radio"
            name="document_type"
            value="word"
            checked={value === 'word'}
            onChange={(e) => onChange(e.target.value as 'word' | 'powerpoint')}
            disabled={disabled}
            className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300"
          />
          <div className="ml-3 flex-1">
            <div className="flex items-center">
              <span className="text-2xl mr-2">📄</span>
              <div>
                <div className="text-sm font-medium text-gray-900">Word Document</div>
                <div className="text-xs text-gray-500">Create a structured document with sections</div>
              </div>
            </div>
          </div>
        </label>
        
        <label className="flex items-center p-4 border-2 rounded-lg cursor-pointer transition-all hover:bg-gray-50 has-[:checked]:border-blue-500 has-[:checked]:bg-blue-50">
          <input
            type="radio"
            name="document_type"
            value="powerpoint"
            checked={value === 'powerpoint'}
            onChange={(e) => onChange(e.target.value as 'word' | 'powerpoint')}
            disabled={disabled}
            className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300"
          />
          <div className="ml-3 flex-1">
            <div className="flex items-center">
              <span className="text-2xl mr-2">📊</span>
              <div>
                <div className="text-sm font-medium text-gray-900">PowerPoint Presentation</div>
                <div className="text-xs text-gray-500">Create a slide-based presentation</div>
              </div>
            </div>
          </div>
        </label>
      </div>
    </div>
  );
}
