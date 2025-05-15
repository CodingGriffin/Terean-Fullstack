import {FreqSlowManger} from "./FreqSlowManager/FreqSlowManager";
import {GeometryManager} from "./GeometryManager/GeometryManager";
import RecordManager from "./RecordManager/RecordManger";
import {Button} from "../../Components/Button/Button";
import {useState} from "react";
import SectionHeader from "../../Components/SectionHeader/SectionHeader";
import {Modal} from "../../Components/Modal/Modal";
import {usePicks} from "../../Contexts/PicksContext";

export const DataManager = () => {
  const [showDataManager, setShowDataManager] = useState<boolean>(false);
  const {
    state,
    handleUploadFiles,
    handleApplyChanges,
    handleDiscardChanges,
    setSavedGeometry,
    setSavedRecordOptions,
    setUploadFiles,
    setSavedFreqSettings,
    setSavedSlowSettings
  } = usePicks();

  const handleClose = () => {
    handleDiscardChanges();
    setShowDataManager(false);
  };

  const handleApply = () => {
    handleApplyChanges();
    setShowDataManager(false);
  };

  return (
    <>
      <div className="d-flex flex-column border rounded">
        <SectionHeader
          title="Controls"
        />
        <div className="d-flex justify-content-between flex-column gap-3 pt-1" style={{height: "210px", margin: "8px"}}>
          <Button
            variant="primary"
            onClick={() => setShowDataManager(true)}
            className="w-100"
          >
            Manage Data
          </Button>
          <Button variant="primary" className="w-100">Update Plots</Button>
          <Button variant="primary" className="w-100">Download</Button>
        </div>
      </div>

      <Modal
        isOpen={showDataManager}
        onClose={handleClose}
        className="modal-lg"
      >
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Manage Data</h5>
            <Button
              variant="secondary"
              className="btn-close"
              onClick={handleClose}
              aria-label="Close"
            />
          </div>
          <div className="modal-body">
            <div className="container p-3">
              <div className="row mt-3 gy-5">
                <div className="col border m-3 p-3">
                  <GeometryManager
                    geometry={state.savedGeometry}
                    onGeometryChange={(geometry) => setSavedGeometry(geometry)}
                  />
                </div>
                <div className="col border m-3 p-3">
                  <RecordManager
                    onUploadFiles={handleUploadFiles}
                    onFilesChange={(data) => setUploadFiles(data)}
                    recordOptions={state.savedRecordOptions}
                    recordUploadFiles={state.uploadFiles}
                    onRecordOptionsChange={(recordOptions) => setSavedRecordOptions(recordOptions)}
                  />
                </div>
              </div>
              <div className="row">
                <div className="col border m-3">
                  <FreqSlowManger
                    numFreq={state.savedFreqSettings.numFreq}
                    maxFreq={state.savedFreqSettings.maxFreq}
                    numSlow={state.savedSlowSettings.numSlow}
                    maxSlow={state.savedSlowSettings.maxSlow}
                    onNumFreqChange={(value) => setSavedFreqSettings({...state.savedFreqSettings, numFreq: value})}
                    onMaxFreqChange={(value) => setSavedFreqSettings({...state.savedFreqSettings, maxFreq: value})}
                    onNumSlowChange={(value) => setSavedSlowSettings({...state.savedSlowSettings, numSlow: value})}
                    onMaxSlowChange={(value) => setSavedSlowSettings({...state.savedSlowSettings, maxSlow: value})}
                  />
                </div>
              </div>
            </div>
          </div>
          <div className="modal-footer">
            <Button variant="secondary" onClick={handleClose}>
              Discard Changes
            </Button>
            <Button variant="primary" onClick={handleApply}>
              Apply Changes
            </Button>
          </div>
        </div>
      </Modal>
    </>
  );
};
