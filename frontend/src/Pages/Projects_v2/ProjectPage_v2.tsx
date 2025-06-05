import ProjectSectionHeader from "../../Components/ProjectSectionHeader.tsx";
import ViewAllProjectsButton from "../../Components/ProjectComponents/ProjectButtons/ViewAllProjectsButton.tsx";
import ProjectSummary from "../../Components/ProjectComponents/ProjectSummary.tsx";
import ProjectTemplate from "../../Components/ProjectComponents/ProjectTemplate.tsx";
import { ProjectProvider } from "../../Contexts/ProjectContext.tsx";

const ProjectPage_v2: React.FC = () => {
  return (
    <ProjectProvider>
      <ProjectTemplate>
        <ProjectSectionHeader
          buttons={
            <ViewAllProjectsButton/>
          }
        />
        <ProjectSummary/>
      </ProjectTemplate>
    </ProjectProvider>
  );
}

export default ProjectPage_v2;
