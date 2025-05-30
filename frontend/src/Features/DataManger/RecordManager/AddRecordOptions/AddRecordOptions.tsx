import React, { useState, useEffect, ChangeEvent } from "react";
import { RecordOption, RecordUploadFile } from "../../../../types/record";
import { Button } from "../../../../Components/Button/Button";
import { FileControls } from "../../../../Components/FileControls/FileControls";

interface AddRecordOptionsProps {
  selectedRecord?: RecordOption;
  mode: "add" | "edit";
  onUploadFiles:(files:RecordUploadFile[]) => void;
  onAddRecordOptions: (data: RecordOption[]) => void;
  onClose: () => void;
}

const AddRecordOptions: React.FC<AddRecordOptionsProps> = ({
  selectedRecord,
  mode,
  onAddRecordOptions,
  onUploadFiles,
  onClose,
}) => {

  const [previewData, setPreviewData] = useState<RecordOption[]>([]);
  const [uploadfiles, setUploadFiles] = useState<RecordUploadFile[]>([]);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  useEffect(() => {
    if (selectedRecord) {
      setPreviewData([selectedRecord]);
    }
  }, [selectedRecord]);

  const handleFileUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;
    
    console.log('=== AddRecordOptions File Upload ===');
    console.log("Files selected:", files);
    console.log("File Attributes:", files[0]);
    
    const filesArray = Array.from(files);
    setSelectedFiles(filesArray);
    
    // Create preview data without IDs (will be added by backend)
    const newRecordOptions = filesArray.map(file => ({
      id: '', // Temporary empty ID, will be filled by backend
      enabled: false,
      weight: 100,
      fileName: file.name,
    }));
    
    console.log('Preview record options:', newRecordOptions);
    setPreviewData(newRecordOptions);
    
    // Store files for upload
    const newUploadFiles = filesArray.map(file => ({
      id: '', // Temporary empty ID
      file
    }));
    setUploadFiles(newUploadFiles);
  };

  return (
    <div className="modal-content">
      <div className="modal-header">
        <h5 className="modal-title">
          {mode === "add" ? "Add New Record" : "Edit Record"}
        </h5>
        <button
          type="button"
          className="btn-close"
          onClick={onClose}
          aria-label="Close" />
      </div>
      <div className="modal-body">
        <FileControls
          onFileSelect={handleFileUpload}
          accept=".sgy"
          showDownload={false}
          multiple={mode === "add" ? true : false}
        />
        <>
          {previewData.length > 0 && (
            <div className="border rounded p-3 mb-3 overflow-auto" style={{ maxHeight: "200px" }}>
              <h6 className="mb-3">Preview Information:</h6>
              {previewData.map((data, index) => (
                <div key={`${data.fileName}-${index}`} className="card mb-2 p-2">
                  <div className="d-flex justify-content-between">
                    <strong>{data.fileName}</strong>
                    <span className="badge bg-primary">{index + 1}/{previewData.length}</span>
                  </div>
                  <div className="small text-muted">
                    <div>Weight: {data.weight}</div>
                    <div>Enabled: {data.enabled ? "Yes" : "No"}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      </div>

      <div className="modal-footer">
        <Button variant="secondary" onClick={onClose}>
          Cancel
        </Button>
        <Button variant="primary" onClick={() => {
          console.log('=== AddRecordOptions Submit ===');
          console.log('Upload files:', uploadfiles);
          console.log('Selected files:', selectedFiles);
          
          // Pass the actual files for upload
          onUploadFiles(uploadfiles);
          // Pass empty record options that will be populated with backend IDs
          onAddRecordOptions(previewData);
          onClose();
        }}>
          {mode === "add" ? "Add" : "Save Changes"}
        </Button>
      </div>
    </div>
  );
};

export default AddRecordOptions;