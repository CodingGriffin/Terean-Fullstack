import React from "react";
import { useNavigate, useParams } from "react-router-dom";
import Navbar from "../../Components/navbar/Navbar";
import { Toast } from "../../Components/Toast/Toast";
import SectionHeader from "../../Components/SectionHeader/SectionHeader";

const ProjectPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  return (
    <>
      <Navbar />
      <div className="w-full">
        <Toast />
        <div className="container-fluid">
          <div className="row mb-4">
            <div className="col-12">
              <SectionHeader title={`Project: ${projectId}`}>
                <div className="d-flex gap-2">
                  <button 
                    className="btn btn-outline-secondary btn-sm"
                    onClick={() => navigate('/projects')}
                  >
                    View All Projects
                  </button>
                </div>
              </SectionHeader>
            </div>
          </div>

          <div className="row g-4">
            <div className="col-md-6">
              <div className="card shadow-sm p-4">
                <h3>Picks Analysis</h3>
                <p>Manage and analyze picks data for this project.</p>
                <button 
                  className="btn btn-primary mt-3"
                  onClick={() => navigate(`/projects/${projectId}/picks`)}
                >
                  Go to Picks
                </button>
              </div>
            </div>
            <div className="col-md-6">
              <div className="card shadow-sm p-4">
                <h3>Dispersion Analysis</h3>
                <p>Perform dispersion analysis for this project.</p>
                <button 
                  className="btn btn-primary mt-3"
                  onClick={() => navigate(`/projects/${projectId}/disper`)}
                >
                  Go to Disper
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default ProjectPage;
