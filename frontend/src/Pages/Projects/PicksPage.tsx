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
import { Button } from "../../Components/Button/Button";

const PicksPageContent: React.FC = () => {
  const { state: { isLoading } } = usePicks();
  const [showDataManager, setShowDataManager] = useState(true);
  const [showRecordCarousel, setShowRecordCarousel] = useState(true);

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
                    className={`btn ${showDataManager ? "btn-outline-primary" : "btn-outline-secondary"}`}
                    onClick={() => setShowDataManager(!showDataManager)}
                  >
                    {showDataManager ? "Hide Data Manager" : "Show Data Manager"}
                  </button>
                  <button 
                    className={`btn ${showRecordCarousel ? "btn-outline-primary" : "btn-outline-secondary"}`}
                    onClick={() => setShowRecordCarousel(!showRecordCarousel)}
                  >
                    {showRecordCarousel ? "Hide Record Carousel" : "Show Record Carousel"}
                  </button>
                  <PicksSettingsSave />
                </div>
              </SectionHeader>
            </div>
          </div>
          
          {/* Conditional rendering for DataManager and RecordCarousel */}
          {(showDataManager || showRecordCarousel) && (
            <div className="row g-3 mb-3">
              {showDataManager && (
                <div className={`col-12 ${showRecordCarousel ? 'col-md-2' : 'col-md-3'}`}>
                  <DataManager />
                </div>
              )}
              {showRecordCarousel && (
                <div className={`col-12 ${showDataManager ? 'col-md-10' : 'col-md-12'}`}>
                  <RecordCarousel />
                </div>
              )}
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
