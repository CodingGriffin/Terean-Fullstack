import Navbar from "../../Components/navbar/Navbar.tsx";
import {ProjectProvider} from "../../Contexts/ProjectContext.tsx";
import {Toast} from "../../Components/Toast/Toast.tsx";

interface ProjectTemplateProps {
  children: React.ReactNode;
}

const ProjectTemplate: React.FC<ProjectTemplateProps> = ({children}) => {
  const loading: boolean = false

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
  
  return (
    <>
      <Navbar/>
      <div className="w-full">
        <Toast/>
        <div className="container-fluid">
          <ProjectProvider>
            {children}
          </ProjectProvider>
        </div>
      </div>
    </>
  );
}

export default ProjectTemplate;
