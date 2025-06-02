import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Navbar from "../../Components/navbar/Navbar";
import { Toast } from "../../Components/Toast/Toast";
import SectionHeader from "../../Components/SectionHeader/SectionHeader";
import { getProjectById } from "../../services/api";
import { addToast } from "../../store/slices/toastSlice";
import { useAppDispatch } from "../../hooks/useAppDispatch";

interface ProjectFile {
  id: string;
  name: string;
  size?: number;
  upload_date?: string;
  file_type?: string;
}

interface Project {
  id: string;
  name: string;
  records?: any[];
  additional_files?: ProjectFile[];
}

const DataManagementPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchProject();
  }, [projectId]);

  const fetchProject = async () => {
    if (!projectId) return;
    
    setLoading(true);
    try {
      const data = await getProjectById(projectId);
      setProject(data);
    } catch (error) {
      console.error("Error fetching project:", error);
      dispatch(addToast({
        message: "Failed to load project data",
        type: "error",
        duration: 5000
      }));
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      // TODO: Implement file upload API call
      dispatch(addToast({
        message: "File upload functionality will be implemented soon",
        type: "info",
        duration: 3000
      }));
    } catch (error) {
      console.error("Error uploading file:", error);
      dispatch(addToast({
        message: "Failed to upload file",
        type: "error",
        duration: 5000
      }));
    } finally {
      setUploading(false);
      // Reset file input
      event.target.value = '';
    }
  };

  const handleFileDownload = async (file: ProjectFile) => {
    try {
      // TODO: Implement file download API call
      dispatch(addToast({
        message: "File download functionality will be implemented soon",
        type: "info",
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

          {/* File Upload Section */}
          <div className="row mb-4">
            <div className="col-12">
              <div className="card shadow-sm">
                <div className="card-header">
                  <h5 className="card-title mb-0">Upload New File</h5>
                </div>
                <div className="card-body">
                  <div className="row align-items-center">
                    <div className="col-md-8">
                      <input
                        type="file"
                        className="form-control"
                        onChange={handleFileUpload}
                        disabled={uploading}
                        accept=".sgy,.segy,.txt,.csv,.pdf,.doc,.docx,.xls,.xlsx"
                      />
                    </div>
                    <div className="col-md-4">
                      {uploading && (
                        <div className="d-flex align-items-center">
                          <div className="spinner-border spinner-border-sm me-2" role="status">
                            <span className="visually-hidden">Uploading...</span>
                          </div>
                          <span>Uploading...</span>
                        </div>
                      )}
                    </div>
                  </div>
                  <small className="text-muted">
                    Supported formats: SGY, SEGY, TXT, CSV, PDF, DOC, DOCX, XLS, XLSX
                  </small>
                </div>
              </div>
            </div>
          </div>

          {/* SGY Files Section */}
          <div className="row mb-4">
            <div className="col-12">
              <div className="card shadow-sm">
                <div className="card-header">
                  <h5 className="card-title mb-0">SGY Files ({project?.records?.length || 0})</h5>
                </div>
                <div className="card-body">
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
                          {project.records.map((record: any, index: number) => (
                            <tr key={record.id || index}>
                              <td>{record.file_name || `SGY File ${index + 1}`}</td>
                              <td>{formatFileSize(record.file_size)}</td>
                              <td>{formatDate(record.created_at)}</td>
                              <td>
                                <button
                                  className="btn btn-sm btn-outline-primary"
                                  onClick={() => handleFileDownload(record)}
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
                    <p className="text-muted mb-0">No SGY files found for this project.</p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Additional Files Section */}
          <div className="row mb-4">
            <div className="col-12">
              <div className="card shadow-sm">
                <div className="card-header">
                  <h5 className="card-title mb-0">Additional Files ({project?.additional_files?.length || 0})</h5>
                </div>
                <div className="card-body">
                  {project?.additional_files && project.additional_files.length > 0 ? (
                    <div className="table-responsive">
                      <table className="table table-hover">
                        <thead>
                          <tr>
                            <th>File Name</th>
                            <th>Type</th>
                            <th>Size</th>
                            <th>Date Added</th>
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {project.additional_files.map((file: ProjectFile) => (
                            <tr key={file.id}>
                              <td>{file.name}</td>
                              <td>
                                <span className="badge bg-secondary">
                                  {file.file_type || 'Unknown'}
                                </span>
                              </td>
                              <td>{formatFileSize(file.size)}</td>
                              <td>{formatDate(file.upload_date)}</td>
                              <td>
                                <button
                                  className="btn btn-sm btn-outline-primary"
                                  onClick={() => handleFileDownload(file)}
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
                    <p className="text-muted mb-0">No additional files found for this project.</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default DataManagementPage; 