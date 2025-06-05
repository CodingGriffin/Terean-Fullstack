import SectionHeader from "./SectionHeader/SectionHeader.tsx";

interface ProjectData {
  id?: string;
  name?: string;
}

interface ProjectSectionHeaderProps {
  buttons?: React.ReactNode;
}

const ProjectSectionHeader: React.FC<ProjectSectionHeaderProps> =
  ({
     buttons,
   }) => {
    const projectData: ProjectData = {
      id: "testID",
      name: "testName",
    }

    return (
      <>
        <SectionHeader
          title={`Project Main Page - ${projectData.name || "Unknown Project"}`}
          actions={
            <div className="d-flex gap-2">
              {buttons}
            </div>
          }
        />
      </>
    )
  }

export default ProjectSectionHeader;
