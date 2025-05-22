import type React from "react";
import { useState } from "react";
import RecordCarousel from "../../Features/RecordCarosel/RecordCarosel";
import MainPlot from "../../Features/MainRecord/MainPlot";
import { DataManager } from "../../Features/DataManger/DataManager";
import SectionHeader from "../../Components/SectionHeader/SectionHeader";
import PicksSettingsSave from "../../Features/PicksSettingsSave/PicksSettingsSave";
import Navbar from "../../Components/navbar/Navbar";
import { Toast } from "../../Components/Toast/Toast";
import { PicksProvider, usePicks } from "../../Contexts/PicksContext";
const PicksPageContent: React.FC = () => {
  const { state: { isLoading } } = usePicks();
  const [showOptions, setShowOptions] = useState(true);

  if (isLoading) {
    return (
      <>
        <Navbar />
        <div className="w-full">
          <Toast />
          <div className="container-fluid py-4">
            <div className="d-flex justify-content-center align-items-center" style={{ minHeight: "60vh" }}>
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="w-full">
        <Toast />
        <div className="container-fluid py-4">
          <div className="row mb-4">
            <div className="col-12">
              <SectionHeader title="Picks Analysis">
                <div className="d-flex gap-2 mb-2">
                  <button 
                    className={`btn ${showOptions ? "btn-outline-primary" : "btn-outline-secondary"}`}
                    onClick={() => setShowOptions(!showOptions)}
                  >
                    {showOptions ? "Hide Options" : "Show Options"}
                  </button>
                  <PicksSettingsSave />
                </div>
              </SectionHeader>
            </div>
          </div>
          
          {/* Conditional rendering for DataManager and RecordCarousel */}
          {(showOptions) && (
            <div className="row g-3 mb-3">
              
                <div className="col-12  col-md-2">
                  <DataManager />
                </div>
             
                <div className="col-12 col-md-10">
                  <RecordCarousel />
                </div>
            </div>
          )}
          
          <div className="row mb-3">
            <div className="col-12">
              <MainPlot />
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

const PicksPage: React.FC = () => {
  return (
    <PicksProvider>
      <PicksPageContent />
    </PicksProvider>
  );
};

export default PicksPage;
