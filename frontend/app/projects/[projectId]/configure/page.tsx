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
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading project...</p>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  if (error && !project) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <button
              onClick={handleBack}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
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
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center">
                <button
                  onClick={handleBack}
                  className="mr-4 text-gray-600 hover:text-gray-900"
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
                <h1 className="text-xl font-semibold text-gray-900">
                  Configure Project
                </h1>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            {/* Project Info */}
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                {project?.name}
              </h2>
              <div className="flex gap-4 text-sm text-gray-600">
                <span className="capitalize">Type: {project?.document_type}</span>
                <span>•</span>
                <span>Topic: {project?.topic}</span>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
                <p className="text-red-800">{error}</p>
              </div>
            )}

            {/* AI Template Generator */}
            {project && (
              <div className="bg-white shadow rounded-lg p-6 mb-6">
                <AITemplateGenerator
                  projectId={projectId}
                  documentType={project.document_type}
                  topic={project.topic}
                  onTemplateAccepted={handleTemplateAccepted}
                  disabled={isSaving}
                />
              </div>
            )}

            {/* Configuration Editor */}
            <div className="bg-white shadow rounded-lg p-6 mb-6">
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

            {/* Content Generation */}
            {project && (sections.length > 0 || slides.length > 0) && (
              <div className="bg-white shadow rounded-lg p-6">
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
