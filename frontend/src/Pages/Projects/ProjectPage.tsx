import ProjectSectionHeader from "../../Components/ProjectSectionHeader.tsx";
import ViewAllProjectsButton from "../../Components/ProjectComponents/ProjectButtons/ViewAllProjectsButton.tsx";
import ProjectSummary from "../../Components/ProjectComponents/ProjectSummary.tsx";
import ProjectTemplate from "../../Components/ProjectComponents/ProjectTemplate.tsx";
import {ProjectProvider} from "../../Contexts/ProjectContext.tsx";
import ProjectNavCards from "../../Components/ProjectComponents/ProjectNavCards.tsx";

const ProjectPage: React.FC = () => {
  return (
    <ProjectProvider>
      <ProjectTemplate>
        <ProjectSectionHeader
          pageName={"Project Main Page"}
          buttons={
            <>
              <ViewAllProjectsButton/>
            </>
          }
        />
        <ProjectSummary/>
        <ProjectNavCards/>
      </ProjectTemplate>
    </ProjectProvider>
  );
}

export default ProjectPage;
