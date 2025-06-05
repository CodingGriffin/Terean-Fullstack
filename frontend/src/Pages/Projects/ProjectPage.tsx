import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Navbar from "../../Components/navbar/Navbar";
import { Toast } from "../../Components/Toast/Toast";
import SectionHeader from "../../Components/SectionHeader/SectionHeader";
import { getProjectById, updateProject } from "../../services/api";
import { addToast } from "../../store/slices/toastSlice";
import { useAppDispatch } from "../../hooks/useAppDispatch";

interface Project {
  id: string;
  name: string;
  status?: string;
  priority?: string;
  survey_date?: string;
  received_date?: string;
  records?: any[];
  additional_files?: any[];
}

const ProjectPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editForm, setEditForm] = useState({
    status: '',
    priority: '',
    survey_date: '',
    received_date: ''
  });
  const [originalForm, setOriginalForm] = useState({
    status: '',
    priority: '',
    survey_date: '',
    received_date: ''
  });


  useEffect(() => {
    fetchProject();
  }, [projectId]);

  const fetchProject = async () => {
    if (!projectId) return;
    
    setLoading(true);
    try {
      const data = await getProjectById(projectId);
      setProject(data);
      const formData = {
        status: data.status || 'not_started',
        priority: data.priority || 'medium',
        survey_date: data.survey_date ? data.survey_date.split('T')[0] : '',
        received_date: data.received_date ? data.received_date.split('T')[0] : ''
      };
      setEditForm(formData);
      setOriginalForm(formData);
    } catch (error) {
      console.error("Error fetching project:", error);
      dispatch(addToast({
        message: "Failed to load project",
        type: "error",
        duration: 5000
      }));
    } finally {
      setLoading(false);
    }
  };

  const hasChanges = () => {
    return JSON.stringify(editForm) !== JSON.stringify(originalForm);
  };

  const handleSaveChanges = async () => {
    if (!project || updating || !hasChanges()) {
      if (!hasChanges()) {
        setShowEditModal(false);
        return;
      }
      return;
    }

    setUpdating(true);
    try {
      // Prepare the update payload, converting empty date strings to null
      const updatePayload: any = {
        status: editForm.status,
        priority: editForm.priority
      };

      // Only include dates if they have changed
      if (editForm.survey_date !== originalForm.survey_date) {
        updatePayload.survey_date = editForm.survey_date || null;
      }
      if (editForm.received_date !== originalForm.received_date) {
        updatePayload.received_date = editForm.received_date || null;
      }

      const updated = await updateProject(projectId!, updatePayload);
      setProject(updated);

      // Update the original form values after successful save
      const newFormData = {
        status: updated.status || 'not_started',
        priority: updated.priority || 'medium',
        survey_date: updated.survey_date ? updated.survey_date.split('T')[0] : '',
        received_date: updated.received_date ? updated.received_date.split('T')[0] : ''
      };
      setEditForm(newFormData);
      setOriginalForm(newFormData);

      setShowEditModal(false);
      dispatch(addToast({
        message: "Project updated successfully",
        type: "success",
        duration: 3000
      }));
    } catch (error) {
      console.error("Error updating project:", error);
      dispatch(addToast({
        message: "Failed to update project",
        type: "error",
        duration: 5000
      }));
    } finally {
      setUpdating(false);
    }
  };

  const formatStatus = (status?: string) => {
    if (!status) return "Not Started";
    return status.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const formatPriority = (priority?: string) => {
    if (!priority) return "Medium";
    return priority.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return "Not set";
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };
  
  if (loading) {
    return (
      <>
        <Navbar />
        <div className="container-fluid">
          <div className="d-flex justify-content-center align-items-center" style={{ minHeight: "60vh" }}>
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Loading...</span>
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
              <SectionHeader title={project?.name || `Project: ${projectId}`}>
                <div className="d-flex gap-2">
                  <button 
                    className="btn btn-outline-secondary btn-sm"
                    onClick={() => navigate('/projects')}
                  >
                    View All Projects
                  </button>
                </div>
              </SectionHeader>
            </div>
          </div>
          
          <div className="row mb-4">
            <div className="col-12">
              <div className="card shadow-sm p-4">
                <div className="d-flex justify-content-between align-items-start">
                  <div className="w-100">
                    <h5 className="card-title mb-3 text-center">Project Summary</h5>
                    <div className="row justify-content-center">
                      <div className="col-md-10">
                        <div className="row text-center">
                          <div className="col-md-3">
                            <p className="mb-2">
                              <strong>Status:</strong>
                              <span className={`ms-2 badge bg-${
                                project?.status === 'completed' ? 'success' :
                                  project?.status === 'in_progress' ? 'primary' :
                                    project?.status === 'blocked' ? 'danger' : 'secondary'
                              }`}>
                                {formatStatus(project?.status)}
                              </span>
                            </p>
                          </div>
                          <div className="col-md-3">
                            <p className="mb-2">
                              <strong>Priority:</strong>
                              <span className={`ms-2 badge bg-${
                                project?.priority === 'very_high' ? 'danger' :
                                  project?.priority === 'high' ? 'warning' :
                                    project?.priority === 'low' || project?.priority === 'very_low' ? 'info' : 'secondary'
                              }`}>
                                {formatPriority(project?.priority)}
                              </span>
                            </p>
                          </div>
                          <div className="col-md-3">
                            <p className="mb-2">
                              <strong>SGY Files:</strong>
                              <span className="ms-2">{project?.records?.length || 0}</span>
                            </p>
                          </div>
                          <div className="col-md-3">
                            <p className="mb-2">
                              <strong>Additional Files:</strong>
                              <span className="ms-2">{project?.additional_files?.length || 0}</span>
                            </p>
                          </div>
                        </div>
                        <div className="row text-center mt-3">
                          <div className="col-md-6">
                            <p className="mb-2">
                              <strong>Survey Date:</strong>
                              <span className="ms-2">{formatDate(project?.survey_date)}</span>
                            </p>
                          </div>
                          <div className="col-md-6">
                            <p className="mb-2">
                              <strong>Received Date:</strong>
                              <span className="ms-2">{formatDate(project?.received_date)}</span>
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <button
                    className="btn btn-primary btn-sm position-absolute top-0 end-0 m-3"
                    onClick={() => {
                      setEditForm(originalForm);
                      setShowEditModal(true);
                    }}
                  >
                    <i className="bi bi-pencil me-1"></i>
                    Edit
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="row g-4">
            <div className="col-md-6 col-lg-4">
              <div className="card shadow-sm p-4">
                <h3>Picks Analysis</h3>
                <p>Manage and analyze picks data for this project.</p>
                <button 
                  className="btn btn-primary mt-3"
                  onClick={() => navigate(`/projects/${projectId}/picks`)}
                >
                  Go to Picks
                </button>
              </div>
            </div>
            <div className="col-md-6 col-lg-4">
              <div className="card shadow-sm p-4">
                <h3>Dispersion Analysis</h3>
                <p>Perform dispersion analysis for this project.</p>
                <button 
                  className="btn btn-primary mt-3"
                  onClick={() => navigate(`/projects/${projectId}/disper`)}
                >
                  Go to Disper
                </button>
              </div>
            </div>
            <div className="col-md-6 col-lg-4">
              <div className="card shadow-sm p-4">
                <h3>Data Management</h3>
                <p>View, upload, and manage project files and data.</p>
                <button 
                  className="btn btn-primary mt-3"
                  onClick={() => navigate(`/projects/${projectId}/data`)}
                >
                  Manage Data
                </button>
              </div>
            </div>
            <div className="col-md-6 col-lg-4">
              <div className="card shadow-sm p-4">
                <h3>Send Results Email</h3>
                <p>Send analysis results and reports to clients.</p>
                <button 
                  className="btn btn-primary mt-3"
                  onClick={() => navigate(`/projects/${projectId}/email`)}
                >
                  Send Email
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Edit Modal */}
      {showEditModal && (
        <div className="modal d-block" tabIndex={-1} style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Edit Project</h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => {
                    setEditForm(originalForm);
                    setShowEditModal(false);
                  }}
                  disabled={updating}
                ></button>
              </div>
              <div className="modal-body">
                <div className="mb-3">
                  <label htmlFor="edit-status" className="form-label">Status</label>
                  <select
                    id="edit-status"
                    className="form-select"
                    value={editForm.status}
                    onChange={(e) => setEditForm({...editForm, status: e.target.value})}
                    disabled={updating}
                  >
                    <option value="not_started">Not Started</option>
                    <option value="in_progress">In Progress</option>
                    <option value="completed">Completed</option>
                    <option value="blocked">Blocked</option>
                  </select>
                </div>
                <div className="mb-3">
                  <label htmlFor="edit-priority" className="form-label">Priority</label>
                  <select
                    id="edit-priority"
                    className="form-select"
                    value={editForm.priority}
                    onChange={(e) => setEditForm({...editForm, priority: e.target.value})}
                    disabled={updating}
                  >
                    <option value="very_high">Very High</option>
                    <option value="high">High</option>
                    <option value="medium">Medium</option>
                    <option value="low">Low</option>
                    <option value="very_low">Very Low</option>
                  </select>
                </div>
                <div className="mb-3">
                  <label htmlFor="edit-survey-date" className="form-label">Survey Date</label>
                  <input
                    id="edit-survey-date"
                    type="date"
                    className="form-control"
                    value={editForm.survey_date}
                    onChange={(e) => setEditForm({...editForm, survey_date: e.target.value})}
                    disabled={updating}
                  />
                </div>
                <div className="mb-3">
                  <label htmlFor="edit-received-date" className="form-label">Received Date</label>
                  <input
                    id="edit-received-date"
                    type="date"
                    className="form-control"
                    value={editForm.received_date}
                    onChange={(e) => setEditForm({...editForm, received_date: e.target.value})}
                    disabled={updating}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setEditForm(originalForm);
                    setShowEditModal(false);
                  }}
                  disabled={updating}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={handleSaveChanges}
                  disabled={updating || !hasChanges()}
                >
                  {updating ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Saving...
                    </>
                  ) : 'Save Changes'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default ProjectPage;

