'use client';

import { useRouter } from 'next/navigation';

interface CreateProjectButtonProps {
  isLoading?: boolean;
}

export function CreateProjectButton({ isLoading }: CreateProjectButtonProps) {
  const router = useRouter();

  const handleClick = () => {
    router.push('/new-project');
  };

  return (
    <button
      onClick={handleClick}
      disabled={isLoading}
      className="inline-flex items-center px-5 py-2.5 sm:px-6 sm:py-3 border border-transparent text-sm font-medium rounded-lg shadow-lg text-white bg-gradient-to-r from-red-500 to-yellow-500 hover:from-red-600 hover:to-yellow-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 focus:ring-offset-[#0a0a0a] disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 hover:scale-105 hover:shadow-xl hover:shadow-red-500/50 active:scale-95 min-h-[44px] min-w-[44px]"
    >
      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
      New Project
    </button>
  );
}