import ProjectSectionHeader from "../../Components/ProjectSectionHeader.tsx";
import ViewAllProjectsButton from "../../Components/ProjectComponents/ProjectButtons/ViewAllProjectsButton.tsx";
import ProjectSummary from "../../Components/ProjectComponents/ProjectSummary.tsx";
import ProjectTemplate from "../../Components/ProjectComponents/ProjectTemplate.tsx";

const ProjectPage_v2: React.FC = () => {
  return (
    <>
      <ProjectTemplate>
        <ProjectSectionHeader
          buttons={
            <ViewAllProjectsButton/>
          }
        />
        <ProjectSummary/>
      </ProjectTemplate>
    </>
  );
}

export default ProjectPage_v2;
