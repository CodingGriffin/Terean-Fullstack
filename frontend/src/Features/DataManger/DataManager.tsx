import {FreqSlowManger} from "./FreqSlowManager/FreqSlowManager";
import {GeometryManager} from "./GeometryManager/GeometryManager";
import RecordManager from "./RecordManager/RecordManger";
import {Button} from "../../Components/Button/Button";
import {useState} from "react";
import SectionHeader from "../../Components/SectionHeader/SectionHeader";
import {Modal} from "../../Components/Modal/Modal";
import {usePicks} from "../../Contexts/PicksContext";
import { useAppSelector } from "../../hooks/useAppSelector";
import { ColorMapManager } from "../MainRecord/ColorMapManager/ColorMapManager";
import { useAppDispatch } from "../../hooks/useAppDispatch";
import { addTransformation } from "../../store/slices/plotSlice";
import { Matrix } from "../../types/record";
import { PickData } from "../../types/data";

export const DataManager = () => {
  const dispatch = useAppDispatch();

  const { 
    points, 
    coordinateMatrix,
    isLoading
  } = useAppSelector((state: { plot: { 
    points: PickData[];
    coordinateMatrix: Matrix;
    isLoading: boolean;
  } }) => state.plot);

  const isAxisSwapped = () => coordinateMatrix[1][0] < 0;

  const [showDataManager, setShowDataManager] = useState<boolean>(false);
  const [showPlotControls, setShowPlotControls] = useState<boolean>(false);

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
        <div className="d-flex justify-content-space-between flex-column gap-3 pt-1" style={{height: "210px", margin: "8px"}}>
          <Button
            variant="primary"
            onClick={() => setShowDataManager(true)}
            className="w-100"
          >
            Manage Data
          </Button>
          <Button 
            variant="primary" 
            onClick={() => setShowPlotControls(true)}
            className="w-100"
          >
            Plot Controls
          </Button>
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
      <Modal
        isOpen={showPlotControls}
        onClose={() => setShowPlotControls(false)}
      >
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Plot Controls</h5>
            <Button
              variant="secondary"
              className="btn-close"
              onClick={() => setShowPlotControls(false)}
              aria-label="Close"
            />
          </div>
          <div className="modal-body">
            {/* Controls Panel */}
            <div className="container">
              <div className="p-3">
                
                {/* ColorMap Controls */}
                <div className="m-3 p-5 border">
                  <h1 className="m-3 text-center ">Color Map</h1>
                  <ColorMapManager/>
                </div>

                {/* Transform Controls */}
                <div className="m-3 p-5 border">
                  <h1 className="m-3 text-center ">Transform</h1>
                  <div className="d-flex flex-wrap gap-2 justify-content-between">
                  <button
                    onClick={() => {
                      dispatch(addTransformation("rotateCounterClockwise"));
                    }}
                    className="btn btn-outline-primary btn-sm"
                    title="Rotate Counter-clockwise"
                    disabled={isLoading}
                  >
                    <span>↺</span>
                  </button>
                  <button
                    onClick={() => {
                      dispatch(addTransformation("rotateClockwise"));
                    }}
                    className="btn btn-outline-primary btn-sm"
                    title="Rotate Clockwise"
                    disabled={isLoading}
                  >
                    <span>↻</span>
                  </button>
                  <button
                    onClick={() => {
                      isAxisSwapped()? dispatch(addTransformation("flipHorizontal")):dispatch(addTransformation("flipVertical"));
                    }}
                    className="btn btn-outline-primary btn-sm"
                    title="Flip Horizontal"
                    disabled={isLoading}
                  >
                    <span>↔</span>
                  </button>
                  <button
                    onClick={() => {
                      isAxisSwapped()? dispatch(addTransformation("flipVertical")):dispatch(addTransformation("flipHorizontal"));
                    }}
                    className="btn btn-outline-primary btn-sm"
                    title="Flip Vertical"
                    disabled={isLoading}
                  >
                    <span>↕</span>
                  </button>
                  </div>
                </div>
                
                {/* Points Info */}
                {points.length > 0 && (
                  <div className="mt-3">
                    <small className="text-muted d-block mb-1">
                      {points.length} point{points.length !== 1 ? 's' : ''} added
                    </small>
                    <small className="text-muted d-block">
                      Shift+Click: Add point<br/>
                      Alt+Click: Remove point
                    </small>
                  </div>
                )}
              </div>
            </div>
          </div>
          <div className="modal-footer">
            <Button
              variant="primary"
              onClick={() => setShowPlotControls(false)}
            >
              Close
            </Button>
          </div>
        </div>
      </Modal>
    </>
  );
};
