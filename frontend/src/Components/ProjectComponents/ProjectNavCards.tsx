import { useNavigate } from "react-router-dom";
import {useProject} from "../../Contexts/ProjectContext.tsx";


const ProjectNavCards: React.FC = () => {
  const navigate = useNavigate();
  const {project} = useProject();
  const projectId = project?.id
  
  return (
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
  )
}

export default ProjectNavCards
