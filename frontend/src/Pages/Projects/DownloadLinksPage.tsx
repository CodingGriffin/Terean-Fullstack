import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Navbar from "../../Components/navbar/Navbar";
import { Toast } from "../../Components/Toast/Toast";
import SectionHeader from "../../Components/SectionHeader/SectionHeader";
import { getProjectById } from "../../services/api";
import { addToast } from "../../store/slices/toastSlice";
import { useAppDispatch } from "../../hooks/useAppDispatch";

interface Project {
  id: string;
  name: string;
  records?: any[];
  additional_files?: any[];
}

const DownloadLinksPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [downloading, setDownloading] = useState<string | null>(null);

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

  const handleDownloadAllSGY = async () => {
    if (!project?.records || project.records.length === 0) {
      dispatch(addToast({
        message: "No SGY files available for download",
        type: "warning",
        duration: 3000
      }));
      return;
    }

    setDownloading('sgy');
    try {
      // TODO: Implement bulk SGY download API call
      dispatch(addToast({
        message: "SGY files download functionality will be implemented soon",
        type: "info",
        duration: 3000
      }));
    } catch (error) {
      console.error("Error downloading SGY files:", error);
      dispatch(addToast({
        message: "Failed to download SGY files",
        type: "error",
        duration: 5000
      }));
    } finally {
      setDownloading(null);
    }
  };

  const handleDownloadAllAdditional = async () => {
    if (!project?.additional_files || project.additional_files.length === 0) {
      dispatch(addToast({
        message: "No additional files available for download",
        type: "warning",
        duration: 3000
      }));
      return;
    }

    setDownloading('additional');
    try {
      // TODO: Implement bulk additional files download API call
      dispatch(addToast({
        message: "Additional files download functionality will be implemented soon",
        type: "info",
        duration: 3000
      }));
    } catch (error) {
      console.error("Error downloading additional files:", error);
      dispatch(addToast({
        message: "Failed to download additional files",
        type: "error",
        duration: 5000
      }));
    } finally {
      setDownloading(null);
    }
  };

  const handleDownloadProjectData = async () => {
    setDownloading('project');
    try {
      // TODO: Implement project data export (metadata, analysis results, etc.)
      dispatch(addToast({
        message: "Project data export functionality will be implemented soon",
        type: "info",
        duration: 3000
      }));
    } catch (error) {
      console.error("Error downloading project data:", error);
      dispatch(addToast({
        message: "Failed to download project data",
        type: "error",
        duration: 5000
      }));
    } finally {
      setDownloading(null);
    }
  };

  const formatFileCount = (count?: number) => {
    return count ? `${count} file${count === 1 ? '' : 's'}` : 'No files';
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
              <SectionHeader title={`Download Links - ${project?.name || projectId}`}>
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

          {/* Project Overview */}
          <div className="row mb-4">
            <div className="col-12">
              <div className="card shadow-sm">
                <div className="card-body">
                  <h5 className="card-title">Project Download Overview</h5>
                  <div className="row text-center">
                    <div className="col-md-4">
                      <div className="border rounded p-3">
                        <h6 className="text-muted">SGY Files</h6>
                        <h4 className="text-primary">{project?.records?.length || 0}</h4>
                        <small className="text-muted">Seismic data files</small>
                      </div>
                    </div>
                    <div className="col-md-4">
                      <div className="border rounded p-3">
                        <h6 className="text-muted">Additional Files</h6>
                        <h4 className="text-info">{project?.additional_files?.length || 0}</h4>
                        <small className="text-muted">Support documents</small>
                      </div>
                    </div>
                    <div className="col-md-4">
                      <div className="border rounded p-3">
                        <h6 className="text-muted">Total Files</h6>
                        <h4 className="text-success">
                          {(project?.records?.length || 0) + (project?.additional_files?.length || 0)}
                        </h4>
                        <small className="text-muted">All project files</small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Download Options */}
          <div className="row g-4">
            {/* SGY Files Download */}
            <div className="col-md-6 col-lg-4">
              <div className="card shadow-sm h-100">
                <div className="card-body d-flex flex-column">
                  <div className="text-center mb-3">
                    <i className="bi bi-file-earmark-zip display-1 text-primary"></i>
                  </div>
                  <h5 className="card-title text-center">Download All SGY Files</h5>
                  <p className="card-text text-center text-muted">
                    Download all seismic data files as a compressed archive.
                  </p>
                  <div className="text-center mb-3">
                    <span className="badge bg-primary fs-6">
                      {formatFileCount(project?.records?.length)}
                    </span>
                  </div>
                  <div className="mt-auto">
                    <button
                      className="btn btn-primary w-100"
                      onClick={handleDownloadAllSGY}
                      disabled={downloading === 'sgy' || !project?.records?.length}
                    >
                      {downloading === 'sgy' ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          Preparing Download...
                        </>
                      ) : (
                        <>
                          <i className="bi bi-download me-2"></i>
                          Download SGY Files
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Additional Files Download */}
            <div className="col-md-6 col-lg-4">
              <div className="card shadow-sm h-100">
                <div className="card-body d-flex flex-column">
                  <div className="text-center mb-3">
                    <i className="bi bi-file-earmark-text display-1 text-info"></i>
                  </div>
                  <h5 className="card-title text-center">Download Additional Files</h5>
                  <p className="card-text text-center text-muted">
                    Download all additional project files and documents.
                  </p>
                  <div className="text-center mb-3">
                    <span className="badge bg-info fs-6">
                      {formatFileCount(project?.additional_files?.length)}
                    </span>
                  </div>
                  <div className="mt-auto">
                    <button
                      className="btn btn-info w-100"
                      onClick={handleDownloadAllAdditional}
                      disabled={downloading === 'additional' || !project?.additional_files?.length}
                    >
                      {downloading === 'additional' ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          Preparing Download...
                        </>
                      ) : (
                        <>
                          <i className="bi bi-download me-2"></i>
                          Download Additional Files
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Project Data Export */}
            <div className="col-md-6 col-lg-4">
              <div className="card shadow-sm h-100">
                <div className="card-body d-flex flex-column">
                  <div className="text-center mb-3">
                    <i className="bi bi-file-earmark-spreadsheet display-1 text-success"></i>
                  </div>
                  <h5 className="card-title text-center">Export Project Data</h5>
                  <p className="card-text text-center text-muted">
                    Export project metadata, analysis results, and reports.
                  </p>
                  <div className="text-center mb-3">
                    <span className="badge bg-success fs-6">
                      Project Summary
                    </span>
                  </div>
                  <div className="mt-auto">
                    <button
                      className="btn btn-success w-100"
                      onClick={handleDownloadProjectData}
                      disabled={downloading === 'project'}
                    >
                      {downloading === 'project' ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          Preparing Export...
                        </>
                      ) : (
                        <>
                          <i className="bi bi-file-earmark-arrow-down me-2"></i>
                          Export Project Data
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="row mt-4">
            <div className="col-12">
              <div className="card shadow-sm">
                <div className="card-header">
                  <h6 className="card-title mb-0">Quick Actions</h6>
                </div>
                <div className="card-body">
                  <div className="d-flex gap-2 flex-wrap">
                    <button
                      className="btn btn-outline-primary btn-sm"
                      onClick={() => navigate(`/projects/${projectId}/data`)}
                    >
                      <i className="bi bi-folder2-open me-1"></i>
                      Manage Files
                    </button>
                    <button
                      className="btn btn-outline-secondary btn-sm"
                      onClick={() => window.print()}
                    >
                      <i className="bi bi-printer me-1"></i>
                      Print Page
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default DownloadLinksPage; 