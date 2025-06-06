import {useNavigate} from "react-router-dom";
import {useProject} from "../../../Contexts/ProjectContext.tsx";

const ToDisperButton: React.FC = () => {
  const navigate = useNavigate();
  const {project} = useProject();

  return (
    <>
      <button
        className="btn btn-outline-info btn-sm"
        onClick={() => navigate(`/projects/${project!.id}/disper`)}
      >
        Disper
      </button>
    </>
  )
}

export default ToDisperButton
