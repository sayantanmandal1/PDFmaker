'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { projectsApi } from '@/lib/projects-api';
import { Project, Section, Slide } from '@/types';
import { SectionCard, SlideCard, ExportButton } from '@/components/project';

export default function DocumentEditorPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.projectId as string;

  const [project, setProject] = useState<Project | null>(null);
  const [sections, setSections] = useState<Section[]>([]);
  const [slides, setSlides] = useState<Slide[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProject();
  }, [projectId]);

  const loadProject = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await projectsApi.getProject(projectId);
      setProject(response.project);
      
      if (response.sections) {
        // Sort sections by position
        const sortedSections = [...response.sections].sort((a, b) => a.position - b.position);
        setSections(sortedSections);
      }
      
      if (response.slides) {
        // Sort slides by position
        const sortedSlides = [...response.slides].sort((a, b) => a.position - b.position);
        setSlides(sortedSlides);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load project');
    } finally {
      setLoading(false);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const handleNext = () => {
    const maxIndex = project?.document_type === 'word' ? sections.length - 1 : slides.length - 1;
    if (currentIndex < maxIndex) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handleSectionUpdate = (updatedSection: Section) => {
    setSections(sections.map(s => s.id === updatedSection.id ? updatedSection : s));
  };

  const handleSlideUpdate = (updatedSlide: Slide) => {
    setSlides(slides.map(s => s.id === updatedSlide.id ? updatedSlide : s));
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-transparent border-t-red-500 border-r-yellow-500 mx-auto"></div>
          <p className="mt-4 text-gray-300">Loading project...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="bg-white/5 backdrop-blur-md border border-white/10 p-8 rounded-lg shadow-xl max-w-md w-full">
          <div className="text-red-500 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-white text-center mb-2">Error Loading Project</h2>
          <p className="text-gray-300 text-center mb-6">{error}</p>
          <button
            onClick={() => router.push('/dashboard')}
            className="w-full bg-gradient-to-r from-red-500 to-yellow-500 text-white py-2 px-4 rounded-md hover:from-red-600 hover:to-yellow-600 transition-all duration-200"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!project) {
    return null;
  }

  const isWord = project.document_type === 'word';
  const items = isWord ? sections : slides;
  const totalItems = items.length;
  const currentItem = items[currentIndex];

  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="bg-white/5 backdrop-blur-md border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <button
                onClick={() => router.push('/dashboard')}
                className="text-gray-300 hover:text-white mb-2 flex items-center transition-colors duration-200"
              >
                <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Back to Dashboard
              </button>
              <h1 className="text-2xl font-bold text-white">{project.name}</h1>
              <p className="text-sm text-gray-400 mt-1">
                {isWord ? 'Word Document' : 'PowerPoint Presentation'} • {project.topic}
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm text-gray-300">
                  {isWord ? 'Section' : 'Slide'} {currentIndex + 1} of {totalItems}
                </p>
              </div>
              {totalItems > 0 && (
                <ExportButton 
                  projectId={projectId} 
                  projectName={project.name}
                  documentType={project.document_type}
                />
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {totalItems === 0 ? (
          <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-lg shadow-xl p-8 text-center">
            <p className="text-gray-300">No content available. Please generate content first.</p>
            <button
              onClick={() => router.push(`/projects/${projectId}/configure`)}
              className="mt-4 bg-gradient-to-r from-red-500 to-yellow-500 text-white py-2 px-4 rounded-md hover:from-red-600 hover:to-yellow-600 transition-all duration-200"
            >
              Go to Configuration
            </button>
          </div>
        ) : (
          <>
            {/* Content Card */}
            <div className="mb-6">
              {isWord && currentItem ? (
                <SectionCard
                  section={currentItem as Section}
                  onUpdate={handleSectionUpdate}
                />
              ) : currentItem ? (
                <SlideCard
                  slide={currentItem as Slide}
                  onUpdate={handleSlideUpdate}
                />
              ) : null}
            </div>

            {/* Navigation */}
            <div className="flex items-center justify-between bg-white/5 backdrop-blur-md border border-white/10 rounded-lg shadow-xl p-4">
              <button
                onClick={handlePrevious}
                disabled={currentIndex === 0}
                className={`flex items-center px-4 py-2 rounded-md transition-all duration-200 ${
                  currentIndex === 0
                    ? 'bg-white/5 text-gray-500 cursor-not-allowed'
                    : 'bg-white/10 text-white hover:bg-white/20 hover:scale-105'
                }`}
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
                Previous
              </button>

              <div className="flex space-x-2">
                {items.map((_, index) => (
                  <button
                    key={index}
                    onClick={() => setCurrentIndex(index)}
                    className={`w-3 h-3 rounded-full transition-all duration-200 ${
                      index === currentIndex 
                        ? 'bg-gradient-to-r from-red-500 to-yellow-500 scale-125' 
                        : 'bg-white/20 hover:bg-white/40'
                    }`}
                    aria-label={`Go to ${isWord ? 'section' : 'slide'} ${index + 1}`}
                  />
                ))}
              </div>

              <button
                onClick={handleNext}
                disabled={currentIndex === totalItems - 1}
                className={`flex items-center px-4 py-2 rounded-md transition-all duration-200 ${
                  currentIndex === totalItems - 1
                    ? 'bg-white/5 text-gray-500 cursor-not-allowed'
                    : 'bg-white/10 text-white hover:bg-white/20 hover:scale-105'
                }`}
              >
                Next
                <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
