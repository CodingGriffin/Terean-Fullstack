import {useNavigate} from "react-router-dom";
import {useProject} from "../../../Contexts/ProjectContext.tsx";

const ViewAllProjectsButton: React.FC = () => {
  const navigate = useNavigate();
  const {project} = useProject();

  return (
    <>
      <button
        className="btn btn-outline-secondary btn-sm"
        onClick={() => navigate(`/projects/${project!.id}`)}
      >
        Back to Project
      </button>
    </>
  )
}

export default ViewAllProjectsButton
