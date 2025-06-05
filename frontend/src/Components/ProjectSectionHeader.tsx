import SectionHeader from "./SectionHeader/SectionHeader.tsx";
import { useProject } from "../Contexts/ProjectContext.tsx";

interface ProjectSectionHeaderProps {
  buttons?: React.ReactNode;
}

const ProjectSectionHeader: React.FC<ProjectSectionHeaderProps> =
  ({
     buttons,
   }) => {
    const { project } = useProject();

    return (
      <SectionHeader
        title={`Project Main Page - ${project?.name || "Unknown Project"}`}
        actions={
          <div className="d-flex gap-2">
            {buttons}
          </div>
        }
      />
    );
  }

export default ProjectSectionHeader;
