import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Navbar from "../../Components/navbar/Navbar";
import { Toast } from "../../Components/Toast/Toast";
import SectionHeader from "../../Components/SectionHeader/SectionHeader";
import { Modal } from "../../Components/Modal/Modal";
import { GeometryManager } from "../../Features/DataManger/GeometryManager/GeometryManager";
import { getProjectById, getPicks, getSgyFilesByProject } from "../../services/api";
import { addToast } from "../../store/slices/toastSlice";
import { useAppDispatch } from "../../hooks/useAppDispatch";
import { GeometryItem } from "../../types/geometry";
import { PickData } from "../../types/data";

interface ProjectFile {
  id: string;
  name: string;
  original_name?: string;
  size?: number;
  upload_date?: string;
  file_type?: string;
  type?: string;
}

interface SgyFile {
  id: string;
  original_name: string;
  size?: number;
  upload_date?: string;
  type?: string;
}

interface Project {
  id: string;
  name: string;
  records?: SgyFile[];
  additional_files?: ProjectFile[];
  geometry?: GeometryItem[];
}

const DataManagementPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [project, setProject] = useState<Project | null>(null);
  const [picks, setPicks] = useState<PickData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set());
  
  const [modals, setModals] = useState({
    geometry: false,
    records: false,
    picks: false,
    additionalFiles: false,
    velocityModel: false,
    reports: false,
  });

  useEffect(() => {
    fetchProjectData();
  }, [projectId]);

  const fetchProjectData = async () => {
    if (!projectId) return;
    
    setLoading(true);
    try {
      const [projectData, picksData, sgyFilesData] = await Promise.all([
        getProjectById(projectId),
        getPicks(projectId).catch(() => ({ data: [] })), // Don't fail if picks don't exist
        getSgyFilesByProject(projectId).catch(() => []) // Don't fail if no SGY files
      ]);
      
      // Merge SGY files data into project data
      const projectWithSgyFiles = {
        ...projectData,
        records: sgyFilesData
      };
      
      setProject(projectWithSgyFiles);
      setPicks(picksData.data || []);
    } catch (error) {
      console.error("Error fetching project data:", error);
      dispatch(addToast({
        message: "Failed to load project data",
        type: "error",
        duration: 5000
      }));
    } finally {
      setLoading(false);
    }
  };

  const handleModals = (modalName: string, value: boolean) => {
    setModals(prev => ({ ...prev, [modalName]: value }));
  };

  const handleGeometryChange = (newGeometry: GeometryItem[]) => {
    if (project) {
      setProject({ ...project, geometry: newGeometry });
    }
  };

  const handleDownloadSgyFile = async (fileId: string, fileName: string) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'}/sgy-files/download_file/${fileId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) throw new Error('Download failed');
      
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      dispatch(addToast({
        message: `Downloaded ${fileName}`,
        type: "success",
        duration: 3000
      }));
    } catch (error) {
      console.error("Error downloading file:", error);
      dispatch(addToast({
        message: "Failed to download file",
        type: "error",
        duration: 5000
      }));
    }
  };

  const handleDownloadAllSgy = async () => {
    if (!projectId) return;
    
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'}/sgy-files/download_project_sgy/${projectId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) throw new Error('Download failed');
      
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `project_${projectId}_records.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      dispatch(addToast({
        message: "Downloaded all SGY files",
        type: "success",
        duration: 3000
      }));
    } catch (error) {
      console.error("Error downloading files:", error);
      dispatch(addToast({
        message: "Failed to download files",
        type: "error",
        duration: 5000
      }));
    }
  };

  const handleDownloadAdditionalFile = async (fileId: string, fileName: string) => {
    if (!projectId) return;
    
    try {
      const response = await fetch(`${import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'}/projects/${projectId}/files/${fileId}/download`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) throw new Error('Download failed');
      
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      dispatch(addToast({
        message: `Downloaded ${fileName}`,
        type: "success",
        duration: 3000
      }));
    } catch (error) {
      console.error("Error downloading file:", error);
      dispatch(addToast({
        message: "Failed to download file",
        type: "error",
        duration: 5000
      }));
    }
  };

  const handleDownloadSelectedAdditionalFiles = async () => {
    if (selectedFiles.size === 0) {
      dispatch(addToast({
        message: "No files selected",
        type: "warning",
        duration: 3000
      }));
      return;
    }

    // For now, download files individually
    // TODO: Implement bulk download API endpoint
    const selectedFilesList = Array.from(selectedFiles);
    for (const fileId of selectedFilesList) {
      const file = project?.additional_files?.find(f => f.id === fileId);
      if (file) {
        await handleDownloadAdditionalFile(fileId, file.original_name || file.name);
      }
    }
    
    setSelectedFiles(new Set());
  };

  const handleDownloadPicks = () => {
    if (picks.length === 0) {
      dispatch(addToast({
        message: "No picks to download",
        type: "warning",
        duration: 3000
      }));
      return;
    }
    
    const pointsData = picks.map(p => `${p.d1.toFixed(6)} ${p.d2.toFixed(6)} ${p.frequency.toFixed(6)} ${p.d3.toFixed(6)} ${p.slowness.toFixed(6)} ${p.d4.toFixed(6)} ${p.d5.toFixed(6)}`).join('\n');
    const blob = new Blob([pointsData], { type: 'text/plain' });
    
    // Create filename with project name
    const projectName = project?.name || 'project';
    const filename = `${projectName}_picks.pck`;
    
    // Use showSaveFilePicker API for native file save dialog
    try {
      (window as unknown as { showSaveFilePicker: (options: any) => Promise<any> })
        .showSaveFilePicker({
          suggestedName: filename,
          types: [
            {
              description: "Picked Points",
              accept: {
                "text/plain": [".pck"],
              },
            },
          ],
        })
        .then(async (handle: any) => {
          const writable = await handle.createWritable();
          await writable.write(blob);
          await writable.close();
          
          dispatch(addToast({
            message: "Picks saved successfully",
            type: "success",
            duration: 3000
          }));
        });
    } catch (err) {
      console.error("Error saving file:", err);
      dispatch(addToast({
        message: "Failed to save file. Downloading instead.",
        type: "warning",
        duration: 3000
      }));
      
      // Fallback to download link if native file picker fails
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      dispatch(addToast({
        message: "Downloaded picks",
        type: "success",
        duration: 3000
      }));
    }
  };

  const toggleFileSelection = (fileId: string) => {
    const newSelected = new Set(selectedFiles);
    if (newSelected.has(fileId)) {
      newSelected.delete(fileId);
    } else {
      newSelected.add(fileId);
    }
    setSelectedFiles(newSelected);
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return "Unknown size";
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return "Unknown date";
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="w-full">
          <Toast />
          <div className="container-fluid py-4">
            <div className="d-flex justify-content-center align-items-center" style={{ minHeight: "60vh" }}>
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="w-full">
        <Toast />
        <div className="container-fluid">
          <div className="row mb-4">
            <div className="col-12">
              <SectionHeader title={`Data Management - ${project?.name || projectId}`}>
                <div className="d-flex gap-2">
                  <button 
                    className="btn btn-sm btn-outline-info"
                    onClick={() => navigate(`/projects/${projectId}/picks`)}
                  >
                    Go to Picks
                  </button>
                  <button 
                    className="btn btn-sm btn-outline-info"
                    onClick={() => navigate(`/projects/${projectId}/disper`)}
                  >
                    Go to Disper
                  </button>
                  <button 
                    className="btn btn-sm btn-outline-secondary"
                    onClick={() => navigate(`/projects/${projectId}`)}
                  >
                    Back to Project
                  </button>
                </div>
              </SectionHeader>
            </div>
          </div>

          {/* Data Management Cards */}
          <div className="row g-4">
            {/* Geometry Card */}
            <div className="col-md-6 col-lg-4">
              <div className="card h-100 shadow-sm">
                <div className="card-body d-flex flex-column">
                  <h5 className="card-title">
                    <i className="bi bi-geo-alt me-2 text-primary"></i>
                    Geometry
                  </h5>
                  <p className="card-text text-muted">
                    Manage survey geometry points and configurations.
                  </p>
                  <div className="mt-auto">
                    <p className="mb-2">
                      <strong>Points:</strong> {project?.geometry?.length || 0}
                    </p>
                    <button 
                      className="btn btn-primary w-100"
                      onClick={() => handleModals("geometry", true)}
                    >
                      Manage Geometry
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Records Card */}
            <div className="col-md-6 col-lg-4">
              <div className="card h-100 shadow-sm">
                <div className="card-body d-flex flex-column">
                  <h5 className="card-title">
                    <i className="bi bi-file-earmark-binary me-2 text-primary"></i>
                    Records
                  </h5>
                  <p className="card-text text-muted">
                    View and download SGY seismic data files.
                  </p>
                  <div className="mt-auto">
                    <p className="mb-2">
                      <strong>Files:</strong> {project?.records?.length || 0}
                    </p>
                    <button 
                      className="btn btn-primary w-100"
                      onClick={() => handleModals("records", true)}
                    >
                      Manage Records
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Picks Card */}
            <div className="col-md-6 col-lg-4">
              <div className="card h-100 shadow-sm">
                <div className="card-body d-flex flex-column">
                  <h5 className="card-title">
                    <i className="bi bi-cursor me-2 text-primary"></i>
                    Picks
                  </h5>
                  <p className="card-text text-muted">
                    View and download dispersion curve picks.
                  </p>
                  <div className="mt-auto">
                    <p className="mb-2">
                      <strong>Points:</strong> {picks.length}
                    </p>
                    <button 
                      className="btn btn-primary w-100"
                      onClick={() => handleModals("picks", true)}
                    >
                      Manage Picks
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Additional Files Card */}
            <div className="col-md-6 col-lg-4">
              <div className="card h-100 shadow-sm">
                <div className="card-body d-flex flex-column">
                  <h5 className="card-title">
                    <i className="bi bi-files me-2 text-primary"></i>
                    Additional Files
                  </h5>
                  <p className="card-text text-muted">
                    Manage project documents and additional files.
                  </p>
                  <div className="mt-auto">
                    <p className="mb-2">
                      <strong>Files:</strong> {project?.additional_files?.length || 0}
                    </p>
                    <button 
                      className="btn btn-primary w-100"
                      onClick={() => handleModals("additionalFiles", true)}
                    >
                      Manage Files
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Velocity Model Card */}
            <div className="col-md-6 col-lg-4">
              <div className="card h-100 shadow-sm">
                <div className="card-body d-flex flex-column">
                  <h5 className="card-title">
                    <i className="bi bi-layers me-2 text-primary"></i>
                    Velocity Model
                  </h5>
                  <p className="card-text text-muted">
                    View and download 1d velocity model - as images or as a model file.
                  </p>
                  <div className="mt-auto">
                    <p className="mb-2 text-muted">
                      <em>Coming soon...</em>
                    </p>
                    <button 
                      className="btn btn-secondary w-100"
                      onClick={() => handleModals("velocityModel", true)}
                      disabled
                    >
                      Manage Model
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Reports Card */}
            <div className="col-md-6 col-lg-4">
              <div className="card h-100 shadow-sm">
                <div className="card-body d-flex flex-column">
                  <h5 className="card-title">
                    <i className="bi bi-file-text me-2 text-primary"></i>
                    Reports
                  </h5>
                  <p className="card-text text-muted">
                    Generate and manage project reports.
                  </p>
                  <div className="mt-auto">
                    <p className="mb-2 text-muted">
                      <em>Coming soon...</em>
                    </p>
                    <button 
                      className="btn btn-secondary w-100"
                      onClick={() => handleModals("reports", true)}
                      disabled
                    >
                      Manage Reports
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Geometry Modal */}
      <Modal 
        isOpen={modals.geometry}
        onClose={() => handleModals("geometry", false)}
        className="modal-lg"
      >
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Geometry Management</h5>
            <button 
              type="button" 
              className="btn-close" 
              onClick={() => handleModals("geometry", false)}
            ></button>
          </div>
          <div className="modal-body">
            <GeometryManager
              geometry={project?.geometry || []}
              onGeometryChange={handleGeometryChange}
            />
          </div>
        </div>
      </Modal>

      {/* Records Modal */}
      <Modal 
        isOpen={modals.records}
        onClose={() => handleModals("records", false)}
        className="modal-lg"
      >
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Records Management</h5>
            <button 
              type="button" 
              className="btn-close" 
              onClick={() => handleModals("records", false)}
            ></button>
          </div>
          <div className="modal-body">
            <div className="mb-3">
              <div className="d-flex justify-content-between align-items-center">
                <h6>SGY Files ({project?.records?.length || 0})</h6>
                {project?.records && project.records.length > 0 && (
                  <button 
                    className="btn btn-sm btn-primary"
                    onClick={handleDownloadAllSgy}
                  >
                    <i className="bi bi-download me-1"></i>
                    Download All
                  </button>
                )}
              </div>
            </div>
            {project?.records && project.records.length > 0 ? (
              <div className="table-responsive">
                <table className="table table-hover">
                  <thead>
                    <tr>
                      <th>File Name</th>
                      <th>Size</th>
                      <th>Date Added</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {project.records.map((record) => (
                      <tr key={record.id}>
                        <td>{record.original_name}</td>
                        <td>{formatFileSize(record.size)}</td>
                        <td>{formatDate(record.upload_date)}</td>
                        <td>
                          <button
                            className="btn btn-sm btn-outline-primary"
                            onClick={() => handleDownloadSgyFile(record.id, record.original_name)}
                          >
                            <i className="bi bi-download me-1"></i>
                            Download
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-muted">No SGY files found for this project.</p>
            )}
          </div>
        </div>
      </Modal>

      {/* Picks Modal */}
      <Modal 
        isOpen={modals.picks}
        onClose={() => handleModals("picks", false)}
      >
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Picks Management</h5>
            <button 
              type="button" 
              className="btn-close" 
              onClick={() => handleModals("picks", false)}
            ></button>
          </div>
          <div className="modal-body">
            <div className="text-center">
              <h6>Current Picks: {picks.length}</h6>
              <p className="text-muted mb-4">
                Download your dispersion curve picks as a .pck file.
              </p>
              <button 
                className="btn btn-primary"
                onClick={handleDownloadPicks}
                disabled={picks.length === 0}
              >
                <i className="bi bi-download me-2"></i>
                Download Picks
              </button>
            </div>
          </div>
        </div>
      </Modal>

      {/* Additional Files Modal */}
      <Modal 
        isOpen={modals.additionalFiles}
        onClose={() => handleModals("additionalFiles", false)}
        className="modal-lg"
      >
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Additional Files Management</h5>
            <button 
              type="button" 
              className="btn-close" 
              onClick={() => handleModals("additionalFiles", false)}
            ></button>
          </div>
          <div className="modal-body">
            <div className="mb-3">
              <div className="d-flex justify-content-between align-items-center">
                <h6>Additional Files ({project?.additional_files?.length || 0})</h6>
                {selectedFiles.size > 0 && (
                  <button 
                    className="btn btn-sm btn-primary"
                    onClick={handleDownloadSelectedAdditionalFiles}
                  >
                    <i className="bi bi-download me-1"></i>
                    Download Selected ({selectedFiles.size})
                  </button>
                )}
              </div>
            </div>
            {project?.additional_files && project.additional_files.length > 0 ? (
              <div className="table-responsive">
                <table className="table table-hover">
                  <thead>
                    <tr>
                      <th>
                        <input 
                          type="checkbox" 
                          className="form-check-input"
                          checked={selectedFiles.size === project.additional_files.length}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setSelectedFiles(new Set(project.additional_files!.map(f => f.id)));
                            } else {
                              setSelectedFiles(new Set());
                            }
                          }}
                        />
                      </th>
                      <th>File Name</th>
                      <th>Type</th>
                      <th>Size</th>
                      <th>Date Added</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {project.additional_files.map((file) => (
                      <tr key={file.id}>
                        <td>
                          <input 
                            type="checkbox" 
                            className="form-check-input"
                            checked={selectedFiles.has(file.id)}
                            onChange={() => toggleFileSelection(file.id)}
                          />
                        </td>
                        <td>{file.original_name || file.name}</td>
                        <td>
                          <span className="badge bg-secondary">
                            {file.file_type || file.type || 'Unknown'}
                          </span>
                        </td>
                        <td>{formatFileSize(file.size)}</td>
                        <td>{formatDate(file.upload_date)}</td>
                        <td>
                          <button
                            className="btn btn-sm btn-outline-primary"
                            onClick={() => handleDownloadAdditionalFile(file.id, file.original_name || file.name)}
                          >
                            <i className="bi bi-download me-1"></i>
                            Download
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-muted">No additional files found for this project.</p>
            )}
          </div>
        </div>
      </Modal>

      {/* Velocity Model Modal */}
      <Modal 
        isOpen={modals.velocityModel}
        onClose={() => handleModals("velocityModel", false)}
      >
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Velocity Model Management</h5>
            <button 
              type="button" 
              className="btn-close" 
              onClick={() => handleModals("velocityModel", false)}
            ></button>
          </div>
          <div className="modal-body">
            <div className="text-center">
              <i className="bi bi-layers display-1 text-muted mb-3"></i>
              <h6>Velocity Model Management</h6>
              <p className="text-muted">
                This feature is coming soon.
              </p>
            </div>
          </div>
        </div>
      </Modal>

      {/* Reports Modal */}
      <Modal 
        isOpen={modals.reports}
        onClose={() => handleModals("reports", false)}
      >
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Reports Management</h5>
            <button 
              type="button" 
              className="btn-close" 
              onClick={() => handleModals("reports", false)}
            ></button>
          </div>
          <div className="modal-body">
            <div className="text-center">
              <i className="bi bi-file-text display-1 text-muted mb-3"></i>
              <h6>Reports Management</h6>
              <p className="text-muted">
                This feature is coming soon. You'll be able to generate and manage project reports here.
              </p>
            </div>
          </div>
        </div>
      </Modal>
    </>
  );
};

export default DataManagementPage; 
