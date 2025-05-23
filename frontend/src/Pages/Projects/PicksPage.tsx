import type React from "react";
import { useState, useEffect } from "react";
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

  useEffect(() => {
    if (isLoading) {
      setShowOptions(false);
    } else {
      window.addEventListener("resize", function () {
        if (window.innerHeight < 768) {
          setShowOptions(false);
        }
      });
    }
  }, [isLoading]);

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
      <div className="w-100">
        <Toast />
        <div className="w-100 h-100 d-flex flex-column">
          <div className="row m-2">
            <SectionHeader title="Picks Analysis">
              <div className="d-flex gap-2">
                <button 
                  className={`btn btn-sm ${showOptions ? "btn-outline-primary" : "btn-outline-secondary"}`}
                  onClick={() => setShowOptions(!showOptions)}
                >
                  {showOptions ? "Hide Options" : "Show Options"}
                </button>
                <PicksSettingsSave />
              </div>
            </SectionHeader>
          </div>
          
          {/* Conditional rendering for DataManager and RecordCarousel */}
          {(showOptions) && (
            <div className="row g-3 m-2">
              
                <div className="col-12 col-md-2 m-0">
                  <DataManager />
                </div>
             
                <div className="col-12 col-md-10 m-0">
                  <RecordCarousel />
                </div>
            </div>
          )}
        
          {showOptions ?
            (<div className="row m-2" style={{height:"calc(100vh - 70px - 42px - 251px - 2rem - 2rem)"}}>
              <MainPlot />
            </div>):(
              <div className="row m-2" style={{height:"calc(100vh - 70px - 42px - 2rem)"}}>
                <MainPlot />
              </div>)
          }
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
