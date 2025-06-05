import React, {createContext, useContext, ReactNode} from "react";


interface ProjectContextType {
  id?: string;
  name?: string;
  loading: boolean;
}

const defaultProjectContext: ProjectContextType = {
  id: undefined,
  name: undefined,
  loading: true,
}

const ProjectContext = createContext<ProjectContextType>(defaultProjectContext);

export const ProjectProvider: React.FC<{ children: ReactNode }> = ({children}) => {


  // <ProjectContext.Provider value={}>
  //   {children}
  // </ProjectContext.Provider>
  return (
    <>
      {children}
    </>
  );
}


export const useProject = (): ProjectContextType => {
  const context = useContext(ProjectContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
