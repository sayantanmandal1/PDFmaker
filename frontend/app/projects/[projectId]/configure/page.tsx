'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { WordOutlineEditor, PowerPointSlideEditor, AITemplateGenerator, GenerationProgress } from '@/components/project';
import { projectsApi } from '@/lib/projects-api';
import { Project, SectionConfig, SlideConfig } from '@/types';

export default function ConfigurePage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.projectId as string;

  const [project, setProject] = useState<Project | null>(null);
  const [sections, setSections] = useState<SectionConfig[]>([]);
  const [slides, setSlides] = useState<SlideConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProject();
  }, [projectId]);

  const loadProject = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await projectsApi.getProject(projectId);
      setProject(response.project);
      
      // Load existing sections if any (for Word documents)
      if (response.sections && response.sections.length > 0) {
        const sectionConfigs: SectionConfig[] = response.sections
          .sort((a, b) => a.position - b.position)
          .map(section => ({
            header: section.header,
            position: section.position,
          }));
        setSections(sectionConfigs);
      }
      
      // Load existing slides if any (for PowerPoint presentations)
      if (response.slides && response.slides.length > 0) {
        const slideConfigs: SlideConfig[] = response.slides
          .sort((a, b) => a.position - b.position)
          .map(slide => ({
            title: slide.title,
            position: slide.position,
          }));
        setSlides(slideConfigs);
      }
    } catch (err: any) {
      console.error('Failed to load project:', err);
      setError(err.message || 'Failed to load project');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      setSaveSuccess(false);
      setError(null);

      // Send appropriate configuration based on document type
      const config = project?.document_type === 'word' 
        ? { sections } 
        : { slides };
      
      await projectsApi.updateConfiguration(projectId, config);
      
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      console.error('Failed to save configuration:', err);
      setError(err.message || 'Failed to save configuration');
    } finally {
      setIsSaving(false);
    }
  };

  const handleBack = () => {
    router.push('/dashboard');
  };

  const handleGenerationComplete = () => {
    // Navigate to editor view after generation completes
    router.push(`/projects/${projectId}/editor`);
  };

  const handleTemplateAccepted = (items: string[]) => {
    if (project?.document_type === 'word') {
      // Convert template items to section configs
      const newSections: SectionConfig[] = items.map((header, index) => ({
        header,
        position: index,
      }));
      setSections(newSections);
    } else {
      // Convert template items to slide configs
      const newSlides: SlideConfig[] = items.map((title, index) => ({
        title,
        position: index,
      }));
      setSlides(newSlides);
    }
  };

  if (isLoading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-transparent border-t-red-500 border-r-yellow-500 mx-auto"></div>
            <p className="mt-4 text-gray-300">Loading project...</p>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  if (error && !project) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-[#0a0a0a] flex items-center justify-center">
          <div className="text-center bg-white/5 backdrop-blur-md border border-white/10 rounded-lg p-8 max-w-md mx-4">
            <p className="text-red-400 mb-6">{error}</p>
            <button
              onClick={handleBack}
              className="px-6 py-2 bg-gradient-to-r from-red-500 to-yellow-500 text-white rounded-lg hover:from-red-600 hover:to-yellow-600 hover:scale-105 transition-all duration-200"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[#0a0a0a]">
        {/* Glassmorphic Navigation */}
        <nav className="bg-white/5 backdrop-blur-md border-b border-white/10 sticky top-0 z-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <button
                  onClick={handleBack}
                  className="mr-4 text-gray-300 hover:text-white transition-colors duration-200 hover:scale-110"
                  aria-label="Back to dashboard"
                >
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15 19l-7-7 7-7"
                    />
                  </svg>
                </button>
                <h1 className="text-xl font-semibold text-white">
                  Configure Project
                </h1>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-4xl mx-auto py-8 sm:px-6 lg:px-8">
          <div className="px-4 sm:px-0 space-y-6">
            {/* Project Info - Glassmorphic Card */}
            <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-lg p-6 shadow-lg shadow-black/20">
              <h2 className="text-2xl font-bold text-white mb-3">
                {project?.name}
              </h2>
              <div className="flex flex-wrap gap-4 text-sm text-gray-300">
                <span className="capitalize flex items-center gap-2">
                  <span className="text-yellow-500">Type:</span>
                  <span className="text-white">{project?.document_type}</span>
                </span>
                <span className="text-white/30">•</span>
                <span className="flex items-center gap-2">
                  <span className="text-yellow-500">Topic:</span>
                  <span className="text-white">{project?.topic}</span>
                </span>
              </div>
            </div>

            {/* Error Message - Red-tinted Glassmorphic */}
            {error && (
              <div className="bg-red-500/10 backdrop-blur-md border border-red-500/30 rounded-lg p-4 shadow-lg shadow-red-500/10">
                <div className="flex items-start gap-3">
                  <svg
                    className="w-5 h-5 text-red-400 shrink-0 mt-0.5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <p className="text-red-300 flex-1">{error}</p>
                </div>
              </div>
            )}

            {/* AI Template Generator - Glassmorphic Container */}
            {project && (
              <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-lg p-6 shadow-lg shadow-black/20">
                <AITemplateGenerator
                  projectId={projectId}
                  documentType={project.document_type}
                  topic={project.topic}
                  onTemplateAccepted={handleTemplateAccepted}
                  disabled={isSaving}
                />
              </div>
            )}

            {/* Configuration Editor - Glassmorphic Container */}
            <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-lg p-6 shadow-lg shadow-black/20">
              {project?.document_type === 'word' ? (
                <WordOutlineEditor
                  sections={sections}
                  onSectionsChange={setSections}
                  onSave={handleSave}
                  isSaving={isSaving}
                  saveSuccess={saveSuccess}
                />
              ) : (
                <PowerPointSlideEditor
                  slides={slides}
                  onSlidesChange={setSlides}
                  onSave={handleSave}
                  isSaving={isSaving}
                  saveSuccess={saveSuccess}
                />
              )}
            </div>

            {/* Content Generation - Glassmorphic Container */}
            {project && (sections.length > 0 || slides.length > 0) && (
              <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-lg p-6 shadow-lg shadow-black/20">
                <GenerationProgress
                  projectId={projectId}
                  documentType={project.document_type}
                  onGenerationComplete={handleGenerationComplete}
                  disabled={isSaving}
                />
              </div>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
