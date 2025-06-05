export interface ProjectFile {
  id: string;
  name: string;
  original_name?: string;
  size?: number;
  upload_date?: string;
  file_type?: string;
  type?: string;
}

export interface SgyFile {
  id: string;
  name: string;
  original_name?: string;
  size?: number;
  upload_date?: string;
  file_type?: string;
  project_id: string;
}

export interface Client {
  id: number;
  name: string;
  email?: string;
  phone?: string;
  company?: string;
}

export interface Project {
  id: string;
  name: string;
  status?: 'not_started' | 'in_progress' | 'completed' | 'blocked' | 'on_hold';
  priority?: 'very_low' | 'low' | 'medium' | 'high' | 'very_high';
  survey_date?: string;
  received_date?: string;
  geometry?: string;
  record_options?: string;
  plot_limits?: string;
  freq?: string;
  slow?: string;
  picks?: string;
  disper_settings?: string;
  display_units?: 'meters' | 'feet';
  asce_version?: 'asce_716' | 'asce_722';
  client_id?: number;
  client?: Client;
  records?: SgyFile[];
  additional_files?: ProjectFile[];
  created_at?: string;
  updated_at?: string;
}

export interface ProjectCreate {
  name: string;
  status?: string;
  priority?: string;
  survey_date?: string;
  received_date?: string;
  geometry?: string;
  record_options?: string;
  plot_limits?: string;
  freq?: string;
  slow?: string;
  picks?: string;
  disper_settings?: string;
  display_units?: 'meters' | 'feet';
  asce_version?: 'asce_716' | 'asce_722';
  client_id?: number;
}

export interface ProjectUpdate {
  name?: string;
  status?: string;
  priority?: string;
  survey_date?: string | null;
  received_date?: string | null;
  display_units?: 'meters' | 'feet';
  asce_version?: 'asce_716' | 'asce_722';
  client_id?: number;
}

export interface ProjectListResponse {
  items: Project[];
  total: number;
  page: number;
  size: number;
  pages: number;
} 