'use client';

interface TopicInputProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export function TopicInput({ value, onChange, disabled }: TopicInputProps) {
  return (
    <div>
      <label htmlFor="topic" className="block text-sm font-medium text-gray-700 mb-2">
        Main Topic
      </label>
      <textarea
        id="topic"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        rows={4}
        className="block w-full border-gray-300 rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm disabled:bg-gray-100 disabled:cursor-not-allowed"
        placeholder="Describe the main topic or theme for your document. Be as specific as possible to get better AI-generated content."
        required
      />
      <p className="mt-2 text-xs text-gray-500">
        Tip: Include key points or specific areas you want the document to cover.
      </p>
    </div>
  );
}
