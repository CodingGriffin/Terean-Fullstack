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

const ProjectSummary: React.FC = () => {
  const project: Project = {
    id: "asdfg",
    name: "testName",
    status: undefined,
    priority: undefined,
    survey_date: undefined,
    received_date: undefined,
    records: undefined,
    additional_files: undefined,
  }

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

  return (
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
                console.log("Need to implement this!")
                // setEditForm(originalForm);
                // setShowEditModal(true);
              }}
            >
              <i className="bi bi-pencil me-1"></i>
              Edit
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ProjectSummary
