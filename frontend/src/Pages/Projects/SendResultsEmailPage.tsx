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
  status?: string;
  priority?: string;
}

const SendResultsEmailPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);

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
              <SectionHeader title={`Send Results Email - ${project?.name || projectId}`}>
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

          {/* Coming Soon Section */}
          <div className="row">
            <div className="col-12">
              <div className="card shadow-sm">
                <div className="card-body text-center py-5">
                  <div className="mb-4">
                    <i className="bi bi-envelope-paper display-1 text-muted"></i>
                  </div>
                  <h2 className="card-title text-muted mb-4">Email Results Feature</h2>
                  <p className="card-text lead text-muted mb-4">
                    This feature is currently under development and will be available soon.
                  </p>
                  
                  <div className="row justify-content-center">
                    <div className="col-md-8 col-lg-6">
                      <div className="card bg-light">
                        <div className="card-body">
                          <h5 className="card-title">Planned Features</h5>
                          <ul className="list-unstyled text-start">
                            <li className="mb-2">
                              <i className="bi bi-check-circle text-success me-2"></i>
                              Email analysis results to clients
                            </li>
                            <li className="mb-2">
                              <i className="bi bi-check-circle text-success me-2"></i>
                              Attach project reports and data
                            </li>
                            <li className="mb-2">
                              <i className="bi bi-check-circle text-success me-2"></i>
                              Customizable email templates
                            </li>
                            <li className="mb-2">
                              <i className="bi bi-check-circle text-success me-2"></i>
                              Multiple recipient support
                            </li>
                            <li className="mb-2">
                              <i className="bi bi-check-circle text-success me-2"></i>
                              Email history and tracking
                            </li>
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4">
                    <p className="text-muted">
                      In the meantime, you can use the Download Links page to get project files 
                      and manually send them to your clients.
                    </p>
                    <div className="d-flex gap-2 justify-content-center flex-wrap">
                      <button
                        className="btn btn-outline-secondary"
                        onClick={() => navigate(`/projects/${projectId}/data`)}
                      >
                        <i className="bi bi-folder2-open me-2"></i>
                        Manage Project Files
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Contact Section */}
          <div className="row mt-4">
            <div className="col-12">
              <div className="card shadow-sm">
                <div className="card-body">
                  <h6 className="card-title">Need to Send Results Now?</h6>
                  <p className="card-text text-muted">
                    While this feature is in development, you can download project files and results 
                    using the other available tools and send them manually via your preferred email client.
                  </p>
                  <div className="d-flex gap-2 flex-wrap">
                    <button
                      className="btn btn-outline-primary btn-sm"
                      onClick={() => navigate(`/projects/${projectId}/data`)}
                    >
                      <i className="bi bi-files me-1"></i>
                      View All Files
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

export default SendResultsEmailPage; 
