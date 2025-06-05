import { useState } from "react";
import {useProject} from "../../Contexts/ProjectContext.tsx";
import {updateProject} from "../../services/api.ts";
import {addToast} from "../../store/slices/toastSlice.ts";
import { ProjectUpdate } from "../../types/project.ts";

const ProjectSummary: React.FC = () => {
  const { project, loading, error, updateProject, isUpdating } = useProject();
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState<ProjectUpdate>({});

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

  const getStatusBadgeColor = (status?: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'primary';
      case 'blocked': return 'danger';
      case 'on_hold': return 'warning';
      case 'not_started': return 'secondary';
      default: return 'secondary';
    }
  };

  const getPriorityBadgeColor = (priority?: string) => {
    switch (priority) {
      case 'very_high': return 'danger';
      case 'high': return 'warning';
      case 'medium': return 'secondary';
      case 'low': return 'info';
      case 'very_low': return 'light';
      default: return 'secondary';
    }
  };

  const handleEditClick = () => {
    if (project) {
      setEditForm({
        name: project.name,
        status: project.status,
        priority: project.priority,
        survey_date: project.survey_date,
        received_date: project.received_date,
        display_units: project.display_units,
        asce_version: project.asce_version,
        client_id: project.client_id,
      });
      setIsEditing(true);
    }
  };

  const handleSaveEdit = async () => {
    try {
      await updateProject(editForm);
      setIsEditing(false);
      setEditForm({});
    } catch (err) {
      console.error("Failed to update project:", err);
      // Error is handled by the context and displayed in the UI
    }
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditForm({});
  };

  if (loading) {
    return (
      <div className="row mb-4">
        <div className="col-12">
          <div className="card shadow-sm p-4">
            <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '200px' }}>
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="row mb-4">
        <div className="col-12">
          <div className="card shadow-sm p-4">
            <div className="alert alert-danger" role="alert">
              <i className="bi bi-exclamation-triangle me-2"></i>
              Error loading project data: {error}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="row mb-4">
        <div className="col-12">
          <div className="card shadow-sm p-4">
            <div className="alert alert-warning" role="alert">
              <i className="bi bi-info-circle me-2"></i>
              No project data available
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="row mb-4">
      <div className="col-12">
        <div className="card shadow-sm p-4">
          <div className="d-flex justify-content-between align-items-start">
            <div className="w-100">
              <h5 className="card-title mb-3 text-center">Project Summary</h5>
              
              {isEditing ? (
                // Edit Form
                <div className="row justify-content-center">
                  <div className="col-md-8">
                    <div className="mb-3">
                      <label className="form-label">Project Name</label>
                      <input
                        type="text"
                        className="form-control"
                        value={editForm.name || ''}
                        onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                      />
                    </div>
                    <div className="row">
                      <div className="col-md-6 mb-3">
                        <label className="form-label">Status</label>
                        <select
                          className="form-select"
                          value={editForm.status || ''}
                          onChange={(e) => setEditForm({ ...editForm, status: e.target.value as any })}
                        >
                          <option value="">Select Status</option>
                          <option value="not_started">Not Started</option>
                          <option value="in_progress">In Progress</option>
                          <option value="completed">Completed</option>
                          <option value="blocked">Blocked</option>
                          <option value="on_hold">On Hold</option>
                        </select>
                      </div>
                      <div className="col-md-6 mb-3">
                        <label className="form-label">Priority</label>
                        <select
                          className="form-select"
                          value={editForm.priority || ''}
                          onChange={(e) => setEditForm({ ...editForm, priority: e.target.value as any })}
                        >
                          <option value="">Select Priority</option>
                          <option value="very_low">Very Low</option>
                          <option value="low">Low</option>
                          <option value="medium">Medium</option>
                          <option value="high">High</option>
                          <option value="very_high">Very High</option>
                        </select>
                      </div>
                    </div>
                    <div className="row">
                      <div className="col-md-6 mb-3">
                        <label className="form-label">Survey Date</label>
                        <input
                          type="date"
                          className="form-control"
                          value={editForm.survey_date ? editForm.survey_date.split('T')[0] : ''}
                          onChange={(e) => setEditForm({ ...editForm, survey_date: e.target.value || null })}
                        />
                      </div>
                      <div className="col-md-6 mb-3">
                        <label className="form-label">Received Date</label>
                        <input
                          type="date"
                          className="form-control"
                          value={editForm.received_date ? editForm.received_date.split('T')[0] : ''}
                          onChange={(e) => setEditForm({ ...editForm, received_date: e.target.value || null })}
                        />
                      </div>
                    </div>
                    <div className="d-flex justify-content-end gap-2">
                      <button
                        className="btn btn-secondary"
                        onClick={handleCancelEdit}
                        disabled={isUpdating}
                      >
                        Cancel
                      </button>
                      <button
                        className="btn btn-primary"
                        onClick={handleSaveEdit}
                        disabled={isUpdating || !editForm.name?.trim()}
                      >
                        {isUpdating ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                            Saving...
                          </>
                        ) : (
                          'Save Changes'
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              ) : (
                // Display Mode
                <div className="row justify-content-center">
                  <div className="col-md-10">
                    <div className="row text-center">
                      <div className="col-md-3">
                        <p className="mb-2">
                          <strong>Status:</strong>
                          <span className={`ms-2 badge bg-${getStatusBadgeColor(project.status)}`}>
                            {formatStatus(project.status)}
                          </span>
                        </p>
                      </div>
                      <div className="col-md-3">
                        <p className="mb-2">
                          <strong>Priority:</strong>
                          <span className={`ms-2 badge bg-${getPriorityBadgeColor(project.priority)}`}>
                            {formatPriority(project.priority)}
                          </span>
                        </p>
                      </div>
                      <div className="col-md-3">
                        <p className="mb-2">
                          <strong>SGY Files:</strong>
                          <span className="ms-2">{project.records?.length || 0}</span>
                        </p>
                      </div>
                      <div className="col-md-3">
                        <p className="mb-2">
                          <strong>Additional Files:</strong>
                          <span className="ms-2">{project.additional_files?.length || 0}</span>
                        </p>
                      </div>
                    </div>
                    <div className="row text-center mt-3">
                      <div className="col-md-6">
                        <p className="mb-2">
                          <strong>Survey Date:</strong>
                          <span className="ms-2">{formatDate(project.survey_date)}</span>
                        </p>
                      </div>
                      <div className="col-md-6">
                        <p className="mb-2">
                          <strong>Received Date:</strong>
                          <span className="ms-2">{formatDate(project.received_date)}</span>
                        </p>
                      </div>
                    </div>
                    {project.client && (
                      <div className="row text-center mt-3">
                        <div className="col-12">
                          <p className="mb-2">
                            <strong>Client:</strong>
                            <span className="ms-2">{project.client.name}</span>
                            {project.client.company && (
                              <span className="text-muted ms-1">({project.client.company})</span>
                            )}
                          </p>
                        </div>
                      </div>
                    )}
                    <div className="row text-center mt-3">
                      <div className="col-md-6">
                        <p className="mb-2">
                          <strong>Display Units:</strong>
                          <span className="ms-2 text-capitalize">{project.display_units || 'meters'}</span>
                        </p>
                      </div>
                      <div className="col-md-6">
                        <p className="mb-2">
                          <strong>ASCE Version:</strong>
                          <span className="ms-2">{project.asce_version?.replace('_', ' ').toUpperCase() || 'ASCE 7-22'}</span>
                        </p>
                      </div>
                    </div>
                    {(project.created_at || project.updated_at) && (
                      <div className="row text-center mt-3">
                        {project.created_at && (
                          <div className="col-md-6">
                            <p className="mb-2 text-muted">
                              <small>
                                <strong>Created:</strong>
                                <span className="ms-2">{formatDate(project.created_at)}</span>
                              </small>
                            </p>
                          </div>
                        )}
                        {project.updated_at && (
                          <div className="col-md-6">
                            <p className="mb-2 text-muted">
                              <small>
                                <strong>Last Updated:</strong>
                                <span className="ms-2">{formatDate(project.updated_at)}</span>
                              </small>
                            </p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
            
            {!isEditing && (
              <button
                className="btn btn-primary btn-sm position-absolute top-0 end-0 m-3"
                onClick={handleEditClick}
                disabled={isUpdating}
              >
                <i className="bi bi-pencil me-1"></i>
                Edit
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProjectSummary;
