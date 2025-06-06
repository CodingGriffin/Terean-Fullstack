import SectionHeader from "./SectionHeader/SectionHeader.tsx";
import {useProject} from "../Contexts/ProjectContext.tsx";

interface ProjectSectionHeaderProps {
  pageName: string;
  buttons?: React.ReactNode;
}

const ProjectSectionHeader: React.FC<ProjectSectionHeaderProps> =
  ({
     pageName,
     buttons,
   }) => {
    const {project} = useProject();

    return (
      <SectionHeader
        title={`${pageName} - ${project?.name || "Unknown Project"}`}
        actions={
          <div className="d-flex gap-2">
            {buttons}
          </div>
        }
      />
    );
  }

export default ProjectSectionHeader;
