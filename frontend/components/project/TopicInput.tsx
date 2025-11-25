'use client';

interface TopicInputProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export function TopicInput({ value, onChange, disabled }: TopicInputProps) {
  return (
    <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-lg p-6 shadow-lg shadow-black/20">
      <label htmlFor="topic" className="block text-sm font-medium text-gray-300 mb-3">
        Main Topic
      </label>
      <textarea
        id="topic"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        rows={4}
        className="
          block w-full px-4 py-3
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
          disabled:opacity-50 
          disabled:cursor-not-allowed
          resize-none
        "
        placeholder="Describe the main topic or theme for your document. Be as specific as possible to get better AI-generated content."
        required
      />
      <div className="mt-3 flex items-start gap-2">
        <svg
          className="w-4 h-4 text-yellow-500 shrink-0 mt-0.5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <p className="text-xs text-gray-400">
          Tip: Include key points or specific areas you want the document to cover.
        </p>
      </div>
    </div>
  );
}
