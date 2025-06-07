import { useNavigate } from "react-router-dom";

const ViewAllProjectsButton: React.FC = () => {
  const navigate = useNavigate();

  return (
    <>
      <button
        className="btn btn-outline-secondary btn-sm"
        onClick={() => navigate('/projects')}
      >
        View All Projects
      </button>
    </>
  )
}

export default ViewAllProjectsButton
