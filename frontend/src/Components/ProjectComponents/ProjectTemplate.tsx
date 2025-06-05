import Navbar from "../../Components/navbar/Navbar.tsx";
import {Toast} from "../Toast/Toast.tsx";
import { useProject } from "../../Contexts/ProjectContext.tsx";

interface ProjectTemplateProps {
  children: React.ReactNode;
}

const ProjectTemplate: React.FC<ProjectTemplateProps> = ({children}) => {
  const { loading, error } = useProject();

  if (loading) {
    return (
      <>
        <Navbar/>
        <div className="container-fluid">
          <div className="d-flex justify-content-center align-items-center" style={{minHeight: "60vh"}}>
            <div className="spinner-border text-primary" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
          </div>
        </div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Navbar/>
        <div className="container-fluid">
          <div className="d-flex justify-content-center align-items-center" style={{minHeight: "60vh"}}>
            <div className="alert alert-danger" role="alert">
              <i className="bi bi-exclamation-triangle me-2"></i>
              Error loading project: {error}
            </div>
          </div>
        </div>
      </>
    );
  }
  
  return (
    <>
      <Navbar/>
      <div className="w-full">
        <Toast/>
        <div className="container-fluid">
          {children}
        </div>
      </div>
    </>
  );
}

export default ProjectTemplate;
