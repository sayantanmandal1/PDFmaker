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
      className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
      New Project
    </button>
  );
}