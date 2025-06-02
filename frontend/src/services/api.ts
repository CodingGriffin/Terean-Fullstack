// eslint-disable-next-line @typescript-eslint/ban-ts-comment
//@ts-nocheck
import axios from 'axios';

import {GeometryItem} from '../types/geometry';
import {RecordOption} from '../types/record';
import {PickData} from '../types/data';

const API_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/';

const api = axios.create({
    baseURL: API_URL,
});

api.interceptors.request.use(function (config) {
  config.headers["Authorization"] = `Bearer ${localStorage.getItem('token')}`;
  return config;
});

export const processGrids = async (
    projectId: string,
    recordOptions: string,
    geometryData: string,
    maxSlowness: number,
    maxFrequency: number,
    numSlowPoints: number,
    numFreqPoints: number,
    returnFreqAndSlow: boolean = true
) => {
    const formData = new FormData();

    formData.append('record_options', recordOptions);
    formData.append('geometry_data', geometryData);
    formData.append('max_slowness', maxSlowness.toString());
    formData.append('max_frequency', maxFrequency.toString());
    formData.append('num_slow_points', numSlowPoints.toString());
    formData.append('num_freq_points', numFreqPoints.toString());
    formData.append('return_freq_and_slow', returnFreqAndSlow.toString());
    formData.append('project_id', projectId);

    return api.post(`/process/grids`, formData);
};

//disper-settings
export const saveDisperSettings = async (projectId: string, disperData: any) => {
    return api.post(`/project/${projectId}/disper-settings`, disperData);
};

export const getDisperSettings = async (projectId: string) => {
    try {
        // TODO: Convert this to use api.get
        const response = await api.get(`/project/${projectId}/disper-settings`);
        if (response.status !== 200) {
            throw new Error(`Failed to fetch disper settings: ${response.statusText}`);
        }
        return response.data;
    } catch (error) {
        console.error('Error fetching disper settings:', error);
        throw error;
    }
};

//options
export const saveOptions = async (projectId: string | undefined,
                                  geometry: GeometryItem[],
                                  records: RecordOption[],
                                  plotLimits: {
                                      numFreq: number
                                      maxFreq: number,
                                      numSlow: number,
                                      maxSlow: number
                                  }) => {

    return api.post(`/project/${projectId}/options`, {
        geometry,
        records,
        plotLimits
    });
};

export const saveRecordOptions = async (projectId: string | undefined, records: RecordOption[]) => {
    if (!projectId) {
        throw new Error("Project ID is required to save record options");
    }
    
    // Get current options first to preserve geometry and plotLimits
    const currentOptions = await getOptions(projectId);
    const { geometry, plotLimits } = currentOptions.data;
    
    // Save with updated records but preserved geometry and plotLimits
    return api.post(`/project/${projectId}/options`, {
        geometry,
        records,
        plotLimits
    });
};

export const getOptions = async (projectId: string) => {
    return api.get(`/project/${projectId}/options`);
};

//picks
export const savePicks = async (projectId: string | undefined, picks: PickData[]) => {
    return api.post(`/project/${projectId}/picks`, picks);
};

export const getPicks = async (projectId: string) => {
    return api.get(`/project/${projectId}/picks`);
};

export const uploadSgyFilesToProject = async (files: File[], projectId: string) => {
  console.log('=== uploadSgyFilesToProject START ===');
  console.log('Files received:', files);
  console.log('Project ID:', projectId);
  
  if (!files || files.length === 0) {
    console.error('No files provided for upload');
    throw new Error("No files provided for upload");
  }

  // Filter out any null or undefined files
  const validFiles = files.filter(file => file !== null && file !== undefined);
  console.log('Valid files after filtering:', validFiles);

  if (validFiles.length === 0) {
    console.error('No valid files to upload after filtering');
    throw new Error("No valid files to upload");
  }

  const formData = new FormData();

  console.log("Preparing to upload files:", validFiles.map(f => ({
    name: f.name,
    size: f.size,
    type: f.type
  })));
  
  // Only append the actual files, not IDs since backend generates them
  validFiles.forEach((file, index) => {
    console.log(`Appending file ${index}:`, file.name);
    formData.append('files', file);
  });

  console.log("Uploading files to project:", projectId);
  console.log("FormData prepared with", validFiles.length, "files");
  
  try {
    const response = await api.post(`/sgy-files/project/${projectId}/upload`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    console.log("=== Upload Response ===");
    console.log("Status:", response.status);
    console.log("Response data:", response.data);
    console.log("File infos returned:", response.data.file_infos);
    
    return response;
  } catch (error) {
    console.error("=== Upload Error ===");
    console.error("Error uploading SEG-Y files:", error);
    if (error.response) {
      console.error("Error response data:", error.response.data);
      console.error("Error status:", error.response.status);
    }
    throw error;
  }
};

export const getSgyFilesByProject = async (projectId: string) => {
  try {
    const response = await api.get(`/sgy-files/project/${projectId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching SGY files for project ${projectId}:`, error);
    throw error;
  }
};

export const downloadSgyFile = async (fileId: string) => {
  try {
    const response = await api.get(`/sgy-files/download_file/${fileId}`, {
      responseType: 'blob'
    });
    return response.data;
  } catch (error) {
    console.error(`Error downloading SGY file ${fileId}:`, error);
    throw error;
  }
};

export const downloadAllSgyFiles = async (projectId: string) => {
  try {
    const response = await api.get(`/sgy-files/download_project_sgy/${projectId}`, {
      responseType: 'blob'
    });
    return response.data;
  } catch (error) {
    console.error(`Error downloading all SGY files for project ${projectId}:`, error);
    throw error;
  }
};

export const downloadAdditionalFile = async (projectId: string, fileId: string) => {
  try {
    const response = await api.get(`/project/${projectId}/files/${fileId}/download`, {
      responseType: 'blob'
    });
    return response.data;
  } catch (error) {
    console.error(`Error downloading additional file ${fileId}:`, error);
    throw error;
  }
};

export const uploadAdditionalFiles = async (projectId: string, files: File[]) => {
  try {
    const formData = new FormData();
    
    files.forEach((file) => {
      formData.append('files', file);
    });

    const response = await api.post(`/project/${projectId}/upload-files`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    return response.data;
  } catch (error) {
    console.error(`Error uploading additional files to project ${projectId}:`, error);
    throw error;
  }
};

export const getAllProjects = async (params: {
  skip?: number;
  limit?: number;
  status?: string[];
  not_status?: string[];
  priority?: string[];
  not_priority?: string[];
  name_search?: string;
  survey_date_start?: string;
  survey_date_end?: string;
  received_date_start?: string;
  received_date_end?: string;
  sort_by?: 'name' | 'status' | 'priority' | 'survey_date' | 'received_date';
  sort_order?: 'asc' | 'desc';
} = {}) => {
  try {
    const defaultParams = {
      skip: 0,
      limit: 100,
      sort_by: 'name' as const,
      sort_order: 'asc' as const
    };

    const queryParams = { ...defaultParams, ...params };
    
    const cleanParams: Record<string, any> = {};
    
    Object.entries(queryParams).forEach(([key, value]) => {
      if ((key.includes('date') && value === '') || 
          (Array.isArray(value) && value.length === 0)) {
        return;
      }
      
      cleanParams[key] = value;
    });
    
    const response = await api.get('/project', {
      params: cleanParams,
      paramsSerializer: {
        indexes: null 
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('Error fetching projects:', error);
    throw error;
  }
};

export const getProjectById = async (projectId: string) => {
  try {
    const response = await api.get(`/project/${projectId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching project ${projectId}:`, error);
    throw error;
  }
};

export const createProject = async (projectData: ProjectCreate, projectId?: string) => {
  try {
    const queryParams = projectId ? `?project_id=${projectId}` : '';
    const requestUrl = `/project/create${queryParams}`;
    
    // Create FormData and add project data as JSON string
    const formData = new FormData();
    formData.append('project_data', JSON.stringify(projectData));
    
    // Log the request details
    console.log('=== CREATE PROJECT REQUEST ===');
    console.log('URL:', requestUrl);
    console.log('Project Data being sent:', JSON.stringify(projectData, null, 2));
    console.log('Sending as FormData with project_data field');
    
    const response = await api.post(requestUrl, formData, {
      headers: {
        // Let axios set the Content-Type with boundary for multipart/form-data
      }
    });
    
    console.log('=== CREATE PROJECT RESPONSE ===');
    console.log('Response Status:', response.status);
    console.log('Response Data:', response.data);
    
    return response.data;
  } catch (error) {
    console.error('=== CREATE PROJECT ERROR ===');
    console.error('Error details:', error);
    if (error.response) {
      console.error('Error response:', error.response.data);
      console.error('Error status:', error.response.status);
    }
    throw error;
  }
};

export const createProjectWithFiles = async (
  projectData: ProjectCreate, 
  projectId?: string,
  sgyFiles?: File[],
  additionalFiles?: File[]
) => {
  try {
    const queryParams = projectId ? `?project_id=${projectId}` : '';
    const requestUrl = `/project/create${queryParams}`;
    
    // Create FormData and add project data as JSON string
    const formData = new FormData();
    formData.append('project_data', JSON.stringify(projectData));
    
    // Add SGY files if provided
    if (sgyFiles && sgyFiles.length > 0) {
      sgyFiles.forEach((file) => {
        formData.append('sgy_files', file);
      });
    }
    
    // Add additional files if provided
    if (additionalFiles && additionalFiles.length > 0) {
      additionalFiles.forEach((file) => {
        formData.append('additional_files', file);
      });
    }
    
    console.log('=== CREATE PROJECT WITH FILES REQUEST ===');
    console.log('URL:', requestUrl);
    console.log('Project Data:', JSON.stringify(projectData, null, 2));
    console.log('Number of SGY files:', sgyFiles?.length || 0);
    console.log('Number of additional files:', additionalFiles?.length || 0);
    
    const response = await api.post(requestUrl, formData, {
      headers: {
        // Let axios set the Content-Type with boundary for multipart/form-data
      }
    });
    
    console.log('=== CREATE PROJECT WITH FILES RESPONSE ===');
    console.log('Response Status:', response.status);
    console.log('Response Data:', response.data);
    
    return response.data;
  } catch (error) {
    console.error('=== CREATE PROJECT WITH FILES ERROR ===');
    console.error('Error details:', error);
    if (error.response) {
      console.error('Error response:', error.response.data);
      console.error('Error status:', error.response.status);
    }
    throw error;
  }
};

export const updateProject = async (projectId: string, updates: {
  name?: string;
  status?: string;
  priority?: string;
  survey_date?: string | null;
  received_date?: string | null;
}) => {
  try {
    const response = await api.patch(`/project/${projectId}`, updates);
    return response.data;
  } catch (error) {
    console.error(`Error updating project ${projectId}:`, error);
    throw error;
  }
};

export const generateResultsEmail = async (
  projectId: string, 
  velocityModelFile: File, 
  clientName: string, 
  clientEmail: string
) => {
  try {
    const formData = new FormData();
    
    formData.append('velocity_model', velocityModelFile);
    formData.append('client_name', clientName);
    formData.append('client_email', clientEmail);
    
    console.log('=== GENERATE RESULTS EMAIL REQUEST ===');
    console.log('Project ID:', projectId);
    console.log('Velocity Model File:', velocityModelFile.name);
    console.log('Client Name:', clientName);
    console.log('Client Email:', clientEmail);
    
    const response = await api.post(`/project/${projectId}/generate-results-email`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    console.log('=== GENERATE RESULTS EMAIL RESPONSE ===');
    console.log('Response Status:', response.status);
    console.log('Response Data:', response.data);
    
    return response.data;
  } catch (error) {
    console.error(`Error generating results email for project ${projectId}:`, error);
    if (error.response) {
      console.error('Error response:', error.response.data);
      console.error('Error status:', error.response.status);
    }
    throw error;
  }
};
