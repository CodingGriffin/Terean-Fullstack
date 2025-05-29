import React, { useState, useEffect} from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../../Components/navbar/Navbar";
import { Toast } from "../../Components/Toast/Toast";
import SectionHeader from "../../Components/SectionHeader/SectionHeader";
import { getAllProjects, createProject} from "../../services/api";
import { addToast } from "../../store/slices/toastSlice";
import { useAppDispatch } from "../../hooks/useAppDispatch";
import { DataManager } from "../../Features/DataManger/DataManager";
import { GeometryManager } from "../../Features/DataManger/GeometryManager/GeometryManager";
import RecordManager from "../../Features/DataManger/RecordManager/RecordManger";
import { FreqSlowManger } from "../../Features/DataManger/FreqSlowManager/FreqSlowManager";
import Pagination from "../../Components/Pagination/Pagination";

interface Project {
  id: string;
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
}

interface ProjectCreate {
  name: string;
  status?: string;
  priority?: string;
  survey_date?: string;
  received_date?: string;
  client?: string;
  geometry?: string;
  record_options?: string;
  plot_limits?: string;
  freq?: string;
  slow?: string;
  picks?: string;
  disper_settings?: string;
}

interface FilterState {
  status?: string[];
  not_status?: string[];
  priority?: string[];
  not_priority?: string[];
  name_search?: string;
  survey_date_start?: string;
  survey_date_end?: string;
  received_date_start?: string;
  received_date_end?: string;
  sort_by: 'name' | 'status' | 'priority' | 'survey_date' | 'received_date';
  sort_order: 'asc' | 'desc';
}

interface ProjectsResponse {
  items: Project[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

const ProjectsPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const [projectsData, setProjectsData] = useState<ProjectsResponse>({
    items: [],
    total: 0,
    page: 1,
    size: 20,
    pages: 1
  });
  const [loading, setLoading] = useState(true);
  const [showNewProjectModal, setShowNewProjectModal] = useState(false);
  const [showFilterModal, setShowFilterModal] = useState(false);
  const [newProject, setNewProject] = useState<ProjectCreate>({
    name: '',
    status: 'not_started',
    priority: 'medium',
    client: '',
    geometry: '[]',
    record_options: '[]',
    plot_limits: JSON.stringify({
      numFreq: 50,
      maxFreq: 50,
      numSlow: 50,
      maxSlow: 0.015
    }),
    freq: '[]',
    slow: '[]',
    picks: '[]',
    disper_settings: JSON.stringify({
      layers: [
        {startDepth: 0.0, endDepth: 30.0, velocity: 760.0, density: 2.0, ignore: 0},
        {startDepth: 30.0, endDepth: 44.0, velocity: 1061.0, density: 2.0, ignore: 0},
        {startDepth: 44.0, endDepth: 144.0, velocity: 1270.657, density: 2.0, ignore: 0}
      ],
      displayUnits: "m",
      asceVersion: "ASCE 7-22",
      curveAxisLimits: {
        xmin: 0.001,
        xmax: 0.6,
        ymin: 30,
        ymax: 500
      },
      modelAxisLimits: {
        xmin: 50,
        xmax: 1400,
        ymin: 0,
        ymax: 50
      },
      numPoints: 10,
      velocityUnit: "velocity",
      periodUnit: "period",
      velocityReversed: false,
      periodReversed: false,
      axesSwapped: false
    })
  });
  const [currentPage, setCurrentPage] = useState(1);
  const [totalProjects, setTotalProjects] = useState(0);
  const [pageSize, setPageSize] = useState(20);
  const navigate = useNavigate();
  
  const [filters, setFilters] = useState<FilterState>({
    status: [],
    not_status: [],
    priority: [],
    not_priority: [],
    name_search: '',
    survey_date_start: '',
    survey_date_end: '',
    received_date_start: '',
    received_date_end: '',
    sort_by: 'name',
    sort_order: 'asc'
  });

  const [useCustomId, setUseCustomId] = useState(false);
  const [customProjectId, setCustomProjectId] = useState('');
  
  const [showDataManagerForNewProject, setShowDataManagerForNewProject] = useState(false);
  const [currentProjectId, setCurrentProjectId] = useState<string | null>(null);

  const [uploadFiles, setUploadFiles] = useState<any[]>([]);
  const [savedGeometry, setSavedGeometry] = useState<any[]>([]);
  const [savedRecordOptions, setSavedRecordOptions] = useState<any[]>([]);
  const [savedFreqSettings, setSavedFreqSettings] = useState({ numFreq: 50, maxFreq: 50 });
  const [savedSlowSettings, setSavedSlowSettings] = useState({ numSlow: 50, maxSlow: 0.015 });

  useEffect(() => {
    fetchProjects();
  }, [currentPage, pageSize, filters]);

  const fetchProjects = async () => {
    setLoading(true);
    try {
      const skip = (currentPage - 1) * pageSize;
      
      const cleanFilters = { ...filters };
      
      if (!cleanFilters.survey_date_start) delete cleanFilters.survey_date_start;
      if (!cleanFilters.survey_date_end) delete cleanFilters.survey_date_end;
      if (!cleanFilters.received_date_start) delete cleanFilters.received_date_start;
      if (!cleanFilters.received_date_end) delete cleanFilters.received_date_end;
      
      if (!cleanFilters.status?.length) delete cleanFilters.status;
      if (!cleanFilters.not_status?.length) delete cleanFilters.not_status;
      if (!cleanFilters.priority?.length) delete cleanFilters.priority;
      if (!cleanFilters.not_priority?.length) delete cleanFilters.not_priority;
      
      if (!cleanFilters.name_search) delete cleanFilters.name_search;
      
      const data = await getAllProjects({
        skip,
        limit: pageSize,
        ...cleanFilters
      });
      
      setProjectsData(data);
      
      setTotalProjects(data.total);
    } catch (error) {
      console.error("Error fetching projects:", error);
      dispatch(addToast({
        message: "Failed to load projects",
        type: "error",
        duration: 5000
      }));
    } finally {
      setLoading(false);
    }
  };

  const handleUploadFiles = async (files: File[]) => {
    if (!files.length) return;
    
    try {
      setUploadFiles(Array.from(files).map(file => ({
        file,
        name: file.name,
        size: file.size,
        type: file.type
      })));
    } catch (error) {
      console.error("Error handling files:", error);
      dispatch(addToast({
        message: "Failed to process files",
        type: "error",
        duration: 5000
      }));
    }
  };

  const handleCreateProject = async () => {
    if (!newProject.name.trim()) {
      dispatch(addToast({
        message: "Project name is required",
        type: "error",
        duration: 5000
      }));
      return;
    }
    
    try {
      const projectToCreate: ProjectCreate = {
        name: newProject.name
      };
      
      if (newProject.status) projectToCreate.status = newProject.status;
      if (newProject.priority) projectToCreate.priority = newProject.priority;
      if (newProject.client) projectToCreate.client = newProject.client;
      if (newProject.survey_date) projectToCreate.survey_date = newProject.survey_date;
      if (newProject.received_date) projectToCreate.received_date = newProject.received_date;
      
      if (savedGeometry.length > 0) {
        projectToCreate.geometry = JSON.stringify(savedGeometry);
      }
      
      if (savedRecordOptions.length > 0) {
        projectToCreate.record_options = JSON.stringify(savedRecordOptions);
      }
      
      if (savedFreqSettings.numFreq !== 50 || savedFreqSettings.maxFreq !== 50 || 
          savedSlowSettings.numSlow !== 50 || savedSlowSettings.maxSlow !== 0.015) {
        projectToCreate.plot_limits = JSON.stringify({
          numFreq: savedFreqSettings.numFreq,
          maxFreq: savedFreqSettings.maxFreq,
          numSlow: savedSlowSettings.numSlow,
          maxSlow: savedSlowSettings.maxSlow
        });
      }
      
      const projectId = useCustomId && customProjectId.trim() ? customProjectId.trim() : undefined;
      
      const createdProject = await createProject(projectToCreate, projectId);
      
      if (uploadFiles.length > 0) {
        try {
          const formData = new FormData();
          uploadFiles.forEach(fileObj => {
            formData.append('files', fileObj.file);
          });
          await fetch(`${process.env.REACT_APP_API_URL || ''}/project/${createdProject.id}/upload-files`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: formData
          });
          
          dispatch(addToast({
            message: `${uploadFiles.length} files uploaded successfully`,
            type: "success",
            duration: 5000
          }));
        } catch (error) {
          console.error("Error uploading files:", error);
          dispatch(addToast({
            message: "Failed to upload files, but project was created",
            type: "warning",
            duration: 5000
          }));
        }
      }
      
      setNewProject({
        name: '',
        status: 'not_started',
        priority: 'medium',
        client: '',
        geometry: '[]',
        record_options: '[]',
        plot_limits: JSON.stringify({
          numFreq: 50,
          maxFreq: 50,
          numSlow: 50,
          maxSlow: 0.015
        }),
        freq: '[]',
        slow: '[]',
        picks: '[]',
        disper_settings: JSON.stringify({
          layers: [
            {startDepth: 0.0, endDepth: 30.0, velocity: 760.0, density: 2.0, ignore: 0},
            {startDepth: 30.0, endDepth: 44.0, velocity: 1061.0, density: 2.0, ignore: 0},
            {startDepth: 44.0, endDepth: 144.0, velocity: 1270.657, density: 2.0, ignore: 0}
          ],
          displayUnits: "m",
          asceVersion: "ASCE 7-22",
          curveAxisLimits: {
            xmin: 0.001,
            xmax: 0.6,
            ymin: 30,
            ymax: 500
          },
          modelAxisLimits: {
            xmin: 50,
            xmax: 1400,
            ymin: 0,
            ymax: 50
          },
          numPoints: 10,
          velocityUnit: "velocity",
          periodUnit: "period",
          velocityReversed: false,
          periodReversed: false,
          axesSwapped: false
        })
      });
      setCustomProjectId('');
      setUseCustomId(false);
      setSavedGeometry([]);
      setSavedRecordOptions([]);
      setUploadFiles([]);
      setSavedFreqSettings({ numFreq: 50, maxFreq: 50 });
      setSavedSlowSettings({ numSlow: 50, maxSlow: 0.015 });
      setShowNewProjectModal(false);
      
      dispatch(addToast({
        message: `Project "${projectToCreate.name}" created successfully`,
        type: "success",
        duration: 5000
      }));
      
      fetchProjects();
      
      navigate(`/projects/${createdProject.id}`);
    } catch (error) {
      console.error("Error creating project:", error);
      dispatch(addToast({
        message: "Failed to create project",
        type: "error",
        duration: 5000
      }));
    }
  };

  const handleFilterChange = (newFilters: Partial<FilterState>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    setCurrentPage(1); 
  };

  const clearFilters = () => {
    setFilters({
      status: [],
      not_status: [],
      priority: [],
      not_priority: [],
      name_search: '',
      survey_date_start: '',
      survey_date_end: '',
      received_date_start: '',
      received_date_end: '',
      sort_by: 'name',
      sort_order: 'asc'
    });
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return "N/A";
    return new Date(dateString).toLocaleDateString();
  };

  const handleDateChange = (field: keyof FilterState, value: string) => {
    if (!value) {
      handleFilterChange({ [field]: '' });
      return;
    }
    
    try {
      const date = new Date(value);
      if (isNaN(date.getTime())) {
        handleFilterChange({ [field]: '' });
        return;
      }
      
      const formattedDate = date.toISOString().split('T')[0];
      handleFilterChange({ [field]: formattedDate });
    } catch (error) {
      console.error(`Error formatting date for ${field}:`, error);
      handleFilterChange({ [field]: '' });
    }
  };

  return (
    <>
      <Navbar />
      <div className="w-full">
        <Toast />
        <div className="container-fluid">
          <div className="row mb-4">
            <div className="col-12">
              <SectionHeader title="Projects">
                <div className="d-flex gap-2">
                  <button 
                    className="btn btn-primary btn-sm"
                    onClick={() => setShowNewProjectModal(true)}
                  >
                    New Project
                  </button>
                  <button 
                    className="btn btn-outline-secondary btn-sm"
                    onClick={() => setShowFilterModal(true)}
                  >
                    <i className="bi bi-funnel"></i> Filter
                  </button>
                  <button 
                    className="btn btn-outline-secondary btn-sm"
                    onClick={fetchProjects}
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        Loading...
                      </>
                    ) : "Refresh"}
                  </button>
                </div>
              </SectionHeader>
            </div>
          </div>

          {/* Quick search bar */}
          <div className="row mb-4">
            <div className="col-md-6">
              <div className="input-group">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Search by project name..."
                  value={filters.name_search}
                  onChange={(e) => handleFilterChange({ name_search: e.target.value })}
                />
                <button 
                  className="btn btn-outline-secondary" 
                  type="button"
                  onClick={() => handleFilterChange({ name_search: '' })}
                >
                  Clear
                </button>
                <button 
                  className="btn btn-primary" 
                  type="button"
                  onClick={fetchProjects}
                >
                  Search
                </button>
              </div>
            </div>
            <div className="col-md-6 text-end">
              <div className="btn-group">
                <button 
                  className="btn btn-outline-secondary dropdown-toggle" 
                  type="button" 
                  data-bs-toggle="dropdown"
                >
                  Sort: {filters.sort_by} ({filters.sort_order})
                </button>
                <ul className="dropdown-menu">
                  <li><h6 className="dropdown-header">Sort by</h6></li>
                  <li><button className="dropdown-item" onClick={() => handleFilterChange({ sort_by: 'name' })}>Name</button></li>
                  <li><button className="dropdown-item" onClick={() => handleFilterChange({ sort_by: 'status' })}>Status</button></li>
                  <li><button className="dropdown-item" onClick={() => handleFilterChange({ sort_by: 'priority' })}>Priority</button></li>
                  <li><button className="dropdown-item" onClick={() => handleFilterChange({ sort_by: 'survey_date' })}>Survey Date</button></li>
                  <li><button className="dropdown-item" onClick={() => handleFilterChange({ sort_by: 'received_date' })}>Received Date</button></li>
                  <li><hr className="dropdown-divider" /></li>
                  <li><h6 className="dropdown-header">Order</h6></li>
                  <li><button className="dropdown-item" onClick={() => handleFilterChange({ sort_order: 'asc' })}>Ascending</button></li>
                  <li><button className="dropdown-item" onClick={() => handleFilterChange({ sort_order: 'desc' })}>Descending</button></li>
                </ul>
              </div>
            </div>
          </div>

          {loading ? (
            <div className="d-flex justify-content-center my-5">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          ) : (
            <>
              <div className="row g-4">
                {projectsData.items.length === 0 ? (
                  <div className="col-12 text-center my-5">
                    <p className="lead">No projects found. Create a new project to get started.</p>
                  </div>
                ) : (
                  projectsData.items.map(project => (
                    <div className="col-md-4 col-lg-3" key={project.id}>
                      <div 
                        className="card shadow-sm h-100" 
                        onClick={() => navigate(`/projects/${project.id}`)}
                        style={{ cursor: 'pointer' }}
                      >
                        <div className="card-body d-flex flex-column">
                          <h5 className="card-title">{project.name || `Project ${project.id}`}</h5>
                          <p className="card-text text-muted small">ID: {project.id}</p>
                          
                          {project.status && (
                            <span className="badge bg-info mb-2">{project.status}</span>
                          )}
                          
                          {project.priority && (
                            <span className="badge bg-warning text-dark mb-2 ms-1">{project.priority}</span>
                          )}
                          
                          <div className="mt-2 small">
                            {project.survey_date && (
                              <p className="mb-1">
                                <strong>Survey Date:</strong> {formatDate(project.survey_date)}
                              </p>
                            )}
                            
                            {project.received_date && (
                              <p className="mb-1">
                                <strong>Received Date:</strong> {formatDate(project.received_date)}
                              </p>
                            )}
                          </div>
                          
                          <button 
                            className="btn btn-outline-primary mt-auto"
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/projects/${project.id}`);
                            }}
                          >
                            View Project
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Pagination */}
              <div className="row mt-3">
                <div className="col-12 d-flex justify-content-center align-items-center">
                  <div className="d-flex align-items-center">
                    <span className="me-2">Items per page:</span>
                    <select 
                      className="form-select form-select-sm" 
                      value={pageSize}
                      onChange={(e) => {
                        setPageSize(Number(e.target.value));
                        setCurrentPage(1); 
                      }}
                      style={{ width: 'auto' }}
                    >
                      <option value={10}>10</option>
                      <option value={20}>20</option>
                      <option value={50}>50</option>
                      <option value={100}>100</option>
                    </select>
                  </div>
                  <div className="ms-4">
                    <span>Showing {(currentPage - 1) * pageSize + 1} to {Math.min(currentPage * pageSize, totalProjects)} of {totalProjects} projects</span>
                  </div>
                </div>
              </div>
              <div className="row mt-4">
                <div className="col-12 d-flex justify-content-center">
                  <Pagination
                    currentPage={currentPage - 1} 
                    totalPages={projectsData.pages}
                    onPageChange={(page) => setCurrentPage(page + 1)} 
                    size="md"
                    className="mb-4"
                    prevLabel="Previous"
                    nextLabel="Next"
                    boundaryCount={1}
                    siblingCount={1}
                    maxVisiblePages={7}
                    showEllipsis={true}
                  />
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* New Project Modal */}
      {showNewProjectModal && (
        <div className="modal d-block" tabIndex={-1} style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-xl">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Create New Project</h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={() => setShowNewProjectModal(false)}
                ></button>
              </div>
              <div className="modal-body">
                <div className="row">
                  <div className="col-md-4">
                    <div className="mb-3">
                      <label htmlFor="projectName" className="form-label">Project Name</label>
                      <input 
                        type="text" 
                        className="form-control" 
                        id="projectName" 
                        value={newProject.name}
                        onChange={(e) => setNewProject({...newProject, name: e.target.value})}
                        placeholder="Enter project name"
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            handleCreateProject();
                          }
                        }}
                      />
                    </div>
                    
                    <div className="mb-3">
                      <label htmlFor="projectClient" className="form-label">Client</label>
                      <input 
                        type="text" 
                        className="form-control" 
                        id="projectClient" 
                        value={newProject.client || ''}
                        onChange={(e) => setNewProject({...newProject, client: e.target.value})}
                        placeholder="Enter client name"
                      />
                    </div>
                    
                    <div className="mb-3">
                      <label htmlFor="projectStatus" className="form-label">Status</label>
                      <select 
                        className="form-select" 
                        id="projectStatus"
                        value={newProject.status || 'not_started'}
                        onChange={(e) => setNewProject({...newProject, status: e.target.value})}
                      >
                        <option value="not_started">Not Started</option>
                        <option value="in_progress">In Progress</option>
                        <option value="completed">Completed</option>
                        <option value="blocked">Blocked</option>
                      </select>
                    </div>
                    
                    <div className="mb-3">
                      <label htmlFor="projectPriority" className="form-label">Priority</label>
                      <select 
                        className="form-select" 
                        id="projectPriority"
                        value={newProject.priority || 'medium'}
                        onChange={(e) => setNewProject({...newProject, priority: e.target.value})}
                      >
                        <option value="very_low">Very Low</option>
                        <option value="low">Low</option>
                        <option value="medium">Medium</option>
                        <option value="high">High</option>
                        <option value="very_high">Very High</option>
                      </select>
                    </div>
                    <div className="mb-3">
                      <div className="form-check">
                        <input
                          className="form-check-input"
                          type="checkbox"
                          id="useCustomId"
                          checked={useCustomId}
                          onChange={(e) => setUseCustomId(e.target.checked)}
                        />
                        <label className="form-check-label" htmlFor="useCustomId">
                          Use custom project ID
                        </label>
                      </div>
                    </div>
                    {useCustomId && (
                      <div className="mb-3">
                        <label htmlFor="customProjectId" className="form-label">Custom Project ID</label>
                        <input
                          type="text"
                          className="form-control"
                          id="customProjectId"
                          value={customProjectId}
                          onChange={(e) => setCustomProjectId(e.target.value)}
                          placeholder="Enter custom project ID"
                        />
                        <small className="text-muted">
                          If left empty, a project ID will be generated automatically.
                        </small>
                      </div>
                    )}
                    <div className="mb-3">
                      <label htmlFor="surveyDate" className="form-label">Survey Date</label>
                      <input 
                        type="date" 
                        className="form-control" 
                        id="surveyDate" 
                        value={newProject.survey_date || ''}
                        onChange={(e) => setNewProject({...newProject, survey_date: e.target.value})}
                      />
                    </div>
                    <div className="mb-3">
                      <label htmlFor="receivedDate" className="form-label">Received Date</label>
                      <input 
                        type="date" 
                        className="form-control" 
                        id="receivedDate" 
                        value={newProject.received_date || ''}
                        onChange={(e) => setNewProject({...newProject, received_date: e.target.value})}
                      />
                    </div>
                  </div>
                  <div className="col-md-8">
                    <div className="container p-3">
                      <div className="row mt-3 gy-5">
                        <div className="col border m-3 p-3">
                          <GeometryManager
                            geometry={savedGeometry}
                            onGeometryChange={(geometry) => setSavedGeometry(geometry)}
                          />
                        </div>
                        <div className="col border m-3 p-3">
                          <RecordManager
                            onUploadFiles={(files) => files && handleUploadFiles(files.map(f => f.file).filter(Boolean) as File[])}
                            onFilesChange={(data) => setUploadFiles(Object.values(data).filter(Boolean) as File[])}
                            recordOptions={savedRecordOptions}
                            recordUploadFiles={Object.fromEntries(uploadFiles.map((file, index) => [`file-${index}`, file]))}
                            onRecordOptionsChange={(recordOptions) => setSavedRecordOptions(recordOptions)}
                          />
                        </div>
                      </div>
                      <div className="row">
                        <div className="col border m-3">
                          <FreqSlowManger
                            numFreq={savedFreqSettings.numFreq}
                            maxFreq={savedFreqSettings.maxFreq}
                            numSlow={savedSlowSettings.numSlow}
                            maxSlow={savedSlowSettings.maxSlow}
                            onNumFreqChange={(value) => setSavedFreqSettings({...savedFreqSettings, numFreq: value})}
                            onMaxFreqChange={(value) => setSavedFreqSettings({...savedFreqSettings, maxFreq: value})}
                            onNumSlowChange={(value) => setSavedSlowSettings({...savedSlowSettings, numSlow: value})}
                            onMaxSlowChange={(value) => setSavedSlowSettings({...savedSlowSettings, maxSlow: value})}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => setShowNewProjectModal(false)}
                >
                  Cancel
                </button>
                <button 
                  type="button" 
                  className="btn btn-primary"
                  onClick={handleCreateProject}
                >
                  Create Project
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filter Modal */}
      {showFilterModal && (
        <div className="modal d-block" tabIndex={-1} style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Filter Projects</h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={() => setShowFilterModal(false)}
                ></button>
              </div>
              <div className="modal-body">
                <div className="row mb-3">
                  <div className="col-md-6">
                    <label className="form-label">Status</label>
                    <div className="d-flex flex-wrap gap-2">
                      {['not_started', 'in_progress', 'completed', 'blocked'].map(status => (
                        <div className="form-check" key={status}>
                          <input 
                            className="form-check-input" 
                            type="checkbox" 
                            id={`status-${status}`}
                            checked={filters.status?.includes(status) || false}
                            onChange={(e) => {
                              if (e.target.checked) {
                                handleFilterChange({ status: [...(filters.status || []), status] });
                              } else {
                                handleFilterChange({ 
                                  status: filters.status?.filter(s => s !== status) || []
                                });
                              }
                            }}
                          />
                          <label className="form-check-label" htmlFor={`status-${status}`}>
                            {status.replace('_', ' ')}
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="col-md-6">
                    <label className="form-label">Priority</label>
                    <div className="d-flex flex-wrap gap-2">
                      {['very_high', 'high', 'medium', 'low', 'very_low'].map(priority => (
                        <div className="form-check" key={priority}>
                          <input 
                            className="form-check-input" 
                            type="checkbox" 
                            id={`priority-${priority}`}
                            checked={filters.priority?.includes(priority) || false}
                            onChange={(e) => {
                              if (e.target.checked) {
                                handleFilterChange({ priority: [...(filters.priority || []), priority] });
                              } else {
                                handleFilterChange({ 
                                  priority: filters.priority?.filter(p => p !== priority) || []
                                });
                              }
                            }}
                          />
                          <label className="form-check-label" htmlFor={`priority-${priority}`}>
                            {priority.replace('_', ' ')}
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
                
                <div className="row mb-3">
                  <div className="col-md-6">
                    <label className="form-label">Survey Date Range</label>
                    <div className="input-group mb-2">
                      <span className="input-group-text">From</span>
                      <input 
                        type="date" 
                        className="form-control"
                        value={filters.survey_date_start}
                        onChange={(e) => handleDateChange('survey_date_start', e.target.value)}
                      />
                    </div>
                    <div className="input-group">
                      <span className="input-group-text">To</span>
                      <input 
                        type="date" 
                        className="form-control"
                        value={filters.survey_date_end}
                        onChange={(e) => handleDateChange('survey_date_end', e.target.value)}
                      />
                    </div>
                  </div>
                  <div className="col-md-6">
                    <label className="form-label">Received Date Range</label>
                    <div className="input-group mb-2">
                      <span className="input-group-text">From</span>
                      <input 
                        type="date" 
                        className="form-control"
                        value={filters.received_date_start}
                        onChange={(e) => handleDateChange('received_date_start', e.target.value)}
                      />
                    </div>
                    <div className="input-group">
                      <span className="input-group-text">To</span>
                      <input 
                        type="date" 
                        className="form-control"
                        value={filters.received_date_end}
                        onChange={(e) => handleDateChange('received_date_end', e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-outline-secondary" 
                  onClick={clearFilters}
                >
                  Clear All Filters
                </button>
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => setShowFilterModal(false)}
                >
                  Cancel
                </button>
                <button 
                  type="button" 
                  className="btn btn-primary"
                  onClick={() => {
                    fetchProjects();
                    setShowFilterModal(false);
                  }}
                >
                  Apply Filters
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {showDataManagerForNewProject && currentProjectId && (
        <div className="modal show d-block" tabIndex={-1} style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-xl">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Configure Project Data</h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={() => {
                    setShowDataManagerForNewProject(false);
                    navigate(`/projects/${currentProjectId}`);
                  }}
                ></button>
              </div>
              <div className="modal-body p-0">
                <DataManager 
                  projectId={currentProjectId}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ProjectsPage;
