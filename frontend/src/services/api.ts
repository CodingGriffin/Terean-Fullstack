// eslint-disable-next-line @typescript-eslint/ban-ts-comment
//@ts-nocheck
import axios from 'axios';

import {GeometryItem} from '../types/geometry';
import {RecordOption} from '../types/record';
import {PickData} from '../types/data';
import {RecordUploadFile} from '../types/record';

const API_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000/';

const api = axios.create({
    baseURL: API_URL,
});

api.interceptors.request.use(function (config) {
  config.headers["Authorization"] = `Bearer ${localStorage.getItem('token')}`;
  return config;
});

export const processGrids = async (
    _projectId: string,
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

    return api.post(`/process/grids`, formData);
};

export const processFrequencyWithSgy = async (
    sgyFile: File,
    maxFrequency: number,
    numFreqPoints: number
) => {
    const formData = new FormData();

    formData.append('sgy_file', sgyFile);
    formData.append('max_frequency', maxFrequency.toString());
    formData.append('num_freq_points', numFreqPoints.toString());

    return api.post('/process/frequency_with_sgy', formData);
};

export const processFrequencyWithParams = async (
    nSamples: number,
    sampleRate: number,
    maxFrequency: number,
    numFreqPoints: number
) => {
    const formData = new FormData();

    formData.append('n_samples', nSamples.toString());
    formData.append('sample_rate', sampleRate.toString());
    formData.append('max_frequency', maxFrequency.toString());
    formData.append('num_freq_points', numFreqPoints.toString());

    return api.post('/process/frequency_with_params', formData);
};

export const processSlownessWithParams = async (
    maxSlow: number,
    numSlowPoints: number
) => {
    const formData = new FormData();

    formData.append('max_slow', maxSlow.toString());
    formData.append('num_slow_points', numSlowPoints.toString());

    return api.post('/process/frequency_with_params', formData);
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

export const uploadSgyFilesWithIds = async (uploadFiles: RecordUploadFile[]) => {
    if (!uploadFiles || uploadFiles.length === 0) {
        throw new Error("No files provided for upload");
    }

    const validUploads = uploadFiles.filter(upload => upload.file !== null);

    if (validUploads.length === 0) {
        throw new Error("No valid files to upload");
    }

    const formData = new FormData();

    console.log("Uploading files with IDs:", validUploads.map(u => ({id: u.id, name: u.file?.name})));

    validUploads.forEach(upload => {
        if (upload.file) {
            formData.append('files', upload.file);
        }
    });

    validUploads.forEach(upload => {
        formData.append('file_ids', upload.id);
    });

    try {
        const response = await api.post('/upload-sgy-with-id', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        console.log("Upload with IDs response:", response.data);
        return response;
    } catch (error) {
        console.error("Error in uploadSgyFilesWithIds:", error);
        throw error;
    }
};

export const getFileInfo = async (fileId: string) => {
    try {
        const response = await api.get(`/file-info/${fileId}`);
        return response.data;
    } catch (error) {
        console.error("Error in getFileInfo:", error);
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
    const response = await api.post(`/project/create${queryParams}`, projectData);
    return response.data;
  } catch (error) {
    console.error('Error creating project:', error);
    throw error;
  }
};

export const autoFitVelocityModel = async (picks: any) => {
    const formData = new FormData();
    formData.append('picks', JSON.stringify(picks));
    
    return api.post('/process/auto-velocity-model', formData);
};
