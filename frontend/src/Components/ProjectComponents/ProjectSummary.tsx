import { useState } from "react";
import {useProject} from "../../Contexts/ProjectContext.tsx";
import {addToast} from "../../store/slices/toastSlice.ts";
import { useAppDispatch } from "../../hooks/useAppDispatch";
import { ProjectUpdate } from "../../types/project.ts";

interface EditFormData {
  name: string;
  status: string;
  priority: string;
  survey_date?: string;
  received_date?: string;
  display_units: string;
  asce_version: string;
}

const ProjectSummary: React.FC = () => {
  const {project, updateProject} = useProject();
  const dispatch = useAppDispatch();
  const [updating, setUpdating] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editForm, setEditForm] = useState<EditFormData>({
    name: '',
    status: '',
    priority: '',
    survey_date: '',
    received_date: '',
    display_units: '',
    asce_version: ''
  });
  const [originalForm, setOriginalForm] = useState<EditFormData>({
    name: '',
    status: '',
    priority: '',
    survey_date: '',
    received_date: '',
    display_units: '',
    asce_version: ''
  });

  const hasChanges = () => {
    return JSON.stringify(editForm) !== JSON.stringify(originalForm);
  };

  const initializeForm = () => {
    if (project) {
      const formData: EditFormData = {
        name: project.name || '',
        status: project.status || 'not_started',
        priority: project.priority || 'medium',
        survey_date: project.survey_date ? project.survey_date.split('T')[0] : '',
        received_date: project.received_date ? project.received_date.split('T')[0] : '',
        display_units: project.display_units || 'meters',
        asce_version: project.asce_version || 'asce_722'
      };
      setEditForm(formData);
      setOriginalForm(formData);
    }
  };

  const handleSaveChanges = async () => {
    if (!project || updating || !hasChanges()) {
      if (!hasChanges()) {
        setShowEditModal(false);
        return;
      }
      return;
    }

    // Validate required fields
    if (!editForm.name.trim()) {
      dispatch(addToast({
        message: "Project name is required",
        type: "error",
        duration: 3000
      }));
      return;
    }

    setUpdating(true);
    try {
      // Prepare the update payload, converting empty date strings to null
      // Ensure that data is only included in the payload if it has been changed!
      const updatePayload: ProjectUpdate = {};
      
      if (editForm.name !== originalForm.name) {
        updatePayload.name = editForm.name.trim();
      }
      
      if (editForm.status !== originalForm.status) {
        updatePayload.status = editForm.status;
      }
      
      if (editForm.priority !== originalForm.priority) {
        updatePayload.priority = editForm.priority;
      }
      
      if (editForm.survey_date !== originalForm.survey_date) {
        updatePayload.survey_date = editForm.survey_date || null;
      }
      
      if (editForm.received_date !== originalForm.received_date) {
        updatePayload.received_date = editForm.received_date || null;
      }
      
      if (editForm.display_units !== originalForm.display_units) {
        updatePayload.display_units = editForm.display_units as 'meters' | 'feet';
      }
      
      if (editForm.asce_version !== originalForm.asce_version) {
        updatePayload.asce_version = editForm.asce_version as 'asce_716' | 'asce_722';
      }

      // Send the API request, and only update the UI on confirmation from the backend 
      // (API First / Pessimistic updating)
      await updateProject(updatePayload);

      // Update the form values after successful save
      setOriginalForm(editForm);
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

  const getStatusBadgeColor = (status?: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'primary';
      case 'blocked':
        return 'danger';
      case 'on_hold':
        return 'warning';
      case 'not_started':
        return 'secondary';
      default:
        return 'secondary';
    }
  };

  const getPriorityBadgeColor = (priority?: string) => {
    switch (priority) {
      case 'very_high':
        return 'danger';
      case 'high':
        return 'warning';
      case 'medium':
        return 'secondary';
      case 'low':
        return 'info';
      case 'very_low':
        return 'light';
      default:
        return 'secondary';
    }
  };

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
    <>
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
                          <span
                            className="ms-2">{project.asce_version?.replace('_', ' ').toUpperCase() || 'ASCE 7-22'}</span>
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
              </div>
              <button
                className="btn btn-primary btn-sm position-absolute top-0 end-0 m-3"
                onClick={() => {
                  initializeForm();
                  setShowEditModal(true)
                }}
              >
                <i className="bi bi-pencil me-1"></i>
                Edit
              </button>
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
                    initializeForm();
                    setShowEditModal(false);
                  }}
                  disabled={updating}
                ></button>
              </div>
              <div className="modal-body">
                <div className="mb-3">
                  <label htmlFor="edit-name" className="form-label">Name</label>
                  <input
                    id="edit-name"
                    type="text"
                    className="form-control"
                    value={editForm.name}
                    onChange={(e) => setEditForm({...editForm, name: e.target.value})}
                    disabled={updating}
                  />
                </div>
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
                <div className="mb-3">
                  <label htmlFor="edit-display-units" className="form-label">Display Units</label>
                  <select
                    id="edit-display-units"
                    className="form-select"
                    value={editForm.display_units}
                    onChange={(e) => setEditForm({...editForm, display_units: e.target.value})}
                    disabled={updating}
                  >
                    <option value="m">Meters</option>
                    <option value="ft">Feet</option>
                  </select>
                </div>
                <div className="mb-3">
                  <label htmlFor="edit-asce-version" className="form-label">ASCE Version</label>
                  <select
                    id="edit-asce-version"
                    className="form-select"
                    value={editForm.asce_version}
                    onChange={(e) => setEditForm({...editForm, asce_version: e.target.value})}
                    disabled={updating}
                  >
                    <option value="ASCE 7-16">ASCE 7-16</option>
                    <option value="ASCE 7-22">ASCE 7-22</option>
                  </select>
                </div>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    initializeForm();
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
}

export default ProjectSummary;
