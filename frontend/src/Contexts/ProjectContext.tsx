import React, { createContext, useContext, ReactNode, useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { Project, ProjectUpdate } from "../types/project.ts";
import { getProjectById, updateProject as updateProjectAPI } from "../services/api";

export interface ProjectContextType {
  project: Project | null;
  loading: boolean;
  error: string | null;
  refetchProject: () => Promise<void>;
  updateProjectData: (updates: Partial<Project>) => void;
  updateProject: (updates: ProjectUpdate) => Promise<void>;
  isUpdating: boolean;
}

const defaultProjectContext: ProjectContextType = {
  project: null,
  loading: true,
  error: null,
  refetchProject: async () => {},
  updateProjectData: () => {},
  updateProject: async () => {},
  isUpdating: false,
};

const ProjectContext = createContext<ProjectContextType>(defaultProjectContext);

export const ProjectProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProject = async () => {
    if (!projectId) {
      setError("No project ID provided");
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const projectData = await getProjectById(projectId);
      setProject(projectData);
    } catch (err) {
      console.error("Error fetching project:", err);
      setError(err instanceof Error ? err.message : "Failed to fetch project");
      setProject(null);
    } finally {
      setLoading(false);
    }
  };

  const refetchProject = async () => {
    await fetchProject();
  };

  const updateProjectData = (updates: Partial<Project>) => {
    if (project) {
      setProject({ ...project, ...updates });
    }
  };

  const updateProject = async (updates: ProjectUpdate) => {
    if (!projectId || !project) {
      throw new Error("No project available to update");
    }

    try {
      setIsUpdating(true);
      setError(null);

      // Optimistic update - immediately update the UI
      const optimisticUpdate = { 
        ...project, 
        ...updates,
        // Ensure the updated_at field is updated
        updated_at: new Date().toISOString()
      } as Project;
      setProject(optimisticUpdate);

      // Make API call to persist changes
      const updatedProject = await updateProjectAPI(projectId, updates);
      
      // Update with the actual response from the server
      setProject(updatedProject);
      
    } catch (err) {
      console.error("Error updating project:", err);
      
      // Revert optimistic update on error
      await fetchProject();
      
      const errorMessage = err instanceof Error ? err.message : "Failed to update project";
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsUpdating(false);
    }
  };

  useEffect(() => {
    fetchProject();
  }, [projectId]);

  const contextValue: ProjectContextType = {
    project,
    loading,
    error,
    refetchProject,
    updateProjectData,
    updateProject,
    isUpdating,
  };

  return (
    <ProjectContext.Provider value={contextValue}>
      {children}
    </ProjectContext.Provider>
  );
};

export const useProject = (): ProjectContextType => {
  const context = useContext(ProjectContext);
  if (!context) {
    throw new Error("useProject must be used within a ProjectProvider");
  }
  return context;
};
