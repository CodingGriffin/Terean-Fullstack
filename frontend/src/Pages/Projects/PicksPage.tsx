import type React from "react";
import RecordCarousel from "../../Features/RecordCarosel/RecordCarosel";
import SelectedRecordsSummary from "../../Features/RecordSummary/RecordSummary";
import MainPlot from "../../Features/MainRecord/MainPlot";
import { DataManager } from "../../Features/DataManger/DataManager";
import SectionHeader from "../../Components/SectionHeader/SectionHeader";
import PicksSettingsSave from "../../Features/PicksSettingsSave/PicksSettingsSave";
import Navbar from "../../Components/navbar/Navbar";
import { Toast } from "../../Components/Toast/Toast";

const PicksPage: React.FC = () => {

  return (
    <>
    <Navbar/>
    <div className="w-full">
        <Toast/>
      <div className="container-fluid py-4">
        <div className="row mb-4">
            <div className="col-12">
                <SectionHeader title="Picks Analysis">
                    <div className='d-flex gap-2'>
                        <PicksSettingsSave/>
                    </div>
                </SectionHeader>
            </div>
        </div>
        <div className="row g-3 mb-3">
          <div className="col-12 col-md-2">
            <DataManager/>
          </div>

          <div className="col-12 col-md-7">
            <RecordCarousel />
          </div>

          <div className="col-12 col-md-3">
            <SelectedRecordsSummary />
          </div>
        </div>
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

export default PicksPage;