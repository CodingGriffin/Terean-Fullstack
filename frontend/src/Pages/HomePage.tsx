import React from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../Components/navbar/Navbar";

export default function HomePage() {
  const navigate = useNavigate();
  
  return (
    <>
      <Navbar />
      <div className="container-lg py-5">
        <div className="row">
          <div className="col-12 text-center mb-5">
            <h1>Welcome to Terean</h1>
            <p className="lead">Seismic data analysis and visualization platform</p>
          </div>
        </div>
        
        <div className="row justify-content-center g-4">
          <div className="col-md-6 col-lg-4">
            <div className="card shadow-sm p-4 text-center h-100">
              <h3>Projects</h3>
              <p>Manage your seismic analysis projects</p>
              <button 
                className="btn btn-primary mt-auto"
                onClick={() => navigate('/projects')}
              >
                Browse Projects
              </button>
            </div>
          </div>
          
          <div className="col-md-6 col-lg-4">
            <div className="card shadow-sm p-4 text-center h-100">
              <h3>Quick Analysis</h3>
              <p>Perform quick analysis without creating a project</p>
              <div className="d-flex gap-2 justify-content-center mt-auto">
                <button 
                  className="btn btn-outline-primary"
                  onClick={() => navigate('/quick2ds')}
                >
                  Quick 2dS
                </button>
                <button 
                  className="btn btn-outline-primary"
                  onClick={() => navigate('/quick2dp')}
                >
                  Quick 2dP
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
