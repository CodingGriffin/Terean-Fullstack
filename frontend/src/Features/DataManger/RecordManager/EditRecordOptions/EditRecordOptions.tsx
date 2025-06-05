import React from "react";
import { RecordOption, RecordUploadFile } from "../../../../types/record";
import { DndContext, closestCenter, KeyboardSensor, PointerSensor, useSensor, useSensors, DragEndEvent } from "@dnd-kit/core";
import { arrayMove, SortableContext, sortableKeyboardCoordinates, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { SortableRecordOptionRow } from "./SortableRecordOptionRow";
import { Button } from "../../../../Components/Button/Button";
import { useState } from "react";
import ConfirmationModal from "../../../../Components/ConfirmationModal/ConfirmationModal";
import AddRecordOptions from "../AddRecordOptions/AddRecordOptions";
import { Modal } from "../../../../Components/Modal/Modal";

interface EditRecordOptionsProps {
  initialRecordOptions: RecordOption[];
  initialRecordUploadFiles:{[key:string]:File|null};
  onRecordOptionsChange?: (options: RecordOption[]) => void;
  onFilesChange: (data:{[key:string]:File|null}) => void;
  onClose?: () => void;
}

const EditRecordOptions: React.FC<EditRecordOptionsProps> = ({
  initialRecordOptions,
  initialRecordUploadFiles,
  onFilesChange,
  onRecordOptionsChange,
  onClose
}) => {
  const [recordOptions, setRecordOptions] = useState<RecordOption[]>(initialRecordOptions);
  const [recordUploadFiles, setRecordUploadFiles] = useState<{[key:string]:File|null}>(initialRecordUploadFiles);
  const [selectedRecordId, setSelectedRecordId] = useState<string | null>(null);
  const [addMode, setAddMode] = useState<"add" | "edit" | null>(null);
  const [showDeleteConfirmation, setShowDeleteConfirmation] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    }),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  );

  const handleUploadFiles = (files: RecordUploadFile[]|null) => {
    console.log('=== EditRecordOptions handleUploadFiles ===');
    console.log('Files:', JSON.stringify(files, null, 2));
    console.log('Current recordUploadFiles:', JSON.stringify(recordUploadFiles, null, 2));
    
    let newUploadFiles:{[key:string]:File|null} = {...recordUploadFiles};
    if (files === null) {
      console.log('Clearing all upload files');
      setRecordUploadFiles({});
      return;
    } else if (files.length === 1 && files[0].file === null) {
      console.log('Deleting single file with ID:', files[0].id);
      delete newUploadFiles[files[0].id];
    } else {
      console.log('Adding/updating files:');
      files.forEach((uploadFile) => {
        console.log(`  - ID: ${uploadFile.id}, File: ${uploadFile.file?.name}`);
        newUploadFiles[uploadFile.id] = uploadFile.file;
      });
    }
    console.log('New upload files keys:', Object.keys(newUploadFiles));
    setRecordUploadFiles(newUploadFiles);
  }

  const handleRecordOptionsChange = (updatedOptions: RecordOption[]) => {
    console.log('=== EditRecordOptions handleRecordOptionsChange ===');
    console.log('Updated options:', JSON.stringify(updatedOptions, null, 2));
    console.log('Previous options:', JSON.stringify(recordOptions, null, 2));
    setRecordOptions(updatedOptions);
    setHasChanges(true);
  };

  const onRecordOptionsUpdate = (id: string, data: Partial<RecordOption> | null) => {
    if (data === null) {
      setSelectedRecordId(id);
      setAddMode("edit");
    } else {
      const updatedOptions = recordOptions.map(option => {
        if (option.id === id) {
          return { ...option, ...data };
        }
        return option;
      });
      handleRecordOptionsChange(updatedOptions);
    }
  };

  const onRecordOptionsDelete = (id: string) => {
    setSelectedRecordId(id);
    setShowDeleteConfirmation(true);
  };

  const handleDeleteRecord = () => {
    if (selectedRecordId) {
      const updatedOptions = recordOptions.filter(option => option.id !== selectedRecordId);
      handleRecordOptionsChange(updatedOptions);
      handleUploadFiles([{id: selectedRecordId, file:null}])
      setSelectedRecordId(null);
      setShowDeleteConfirmation(false);
    }
  };

  const onRecordOptionsReorder = (orderedIds: string[]) => {
    const updatedOptions = orderedIds.map(id => recordOptions.find(option => option.id === id)!);
    handleRecordOptionsChange(updatedOptions);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;

    const oldIndex = recordOptions.findIndex(record => record.id === active.id);
    const newIndex = recordOptions.findIndex(record => record.id === over.id);

    if (oldIndex !== -1 && newIndex !== -1) {
      const newItems = arrayMove(recordOptions, oldIndex, newIndex);
      onRecordOptionsReorder(newItems.map(item => item.id));
    }
  };

  const handleAddRecordOptions = (newOptions: RecordOption[]) => {
    console.log('=== EditRecordOptions handleAddRecordOptions ===');
    console.log('Mode:', addMode);
    console.log('New options:', JSON.stringify(newOptions, null, 2));
    console.log('Current record options:', JSON.stringify(recordOptions, null, 2));
    
    let updatedOptions: RecordOption[] = [];

    if (addMode === 'edit' && newOptions.length === 1) {
      updatedOptions = recordOptions.map((option) => {
        if (option.id === newOptions[0].id) {
          return newOptions[0];
        } else {
          return option;
        }
      })
    } else {
      updatedOptions = [...recordOptions, ...newOptions];
    }
    
    console.log('Updated options after merge:', JSON.stringify(updatedOptions, null, 2));
    handleRecordOptionsChange(updatedOptions);
    setAddMode(null);
  };

  const handleDeleteAll = () => {
    setRecordOptions([]);
    handleUploadFiles(null);
    setHasChanges(true);
    setShowDeleteConfirmation(false);
  };

  const handleApplyChanges = () => {
    console.log('=== EditRecordOptions handleApplyChanges ===');
    console.log('Record options to apply:', JSON.stringify(recordOptions, null, 2));
    console.log('Upload files to apply keys:', Object.keys(recordUploadFiles));
    onRecordOptionsChange?.(recordOptions);
    onFilesChange(recordUploadFiles);
    setHasChanges(false);
    onClose?.();
  };

  return (
    <div className="modal-content">
      <div className="modal-header">
        <h5 className="modal-title">View / Edit Record</h5>
        <Button variant="secondary" className="btn-close" onClick={onClose} aria-label="Close" />
      </div>
      <div className="modal-body">
        <div className="d-flex flex-column h-100">
          <div className="flex-grow-1 overflow-auto mb-3">
            {recordOptions.length ? <DndContext
              sensors={sensors}
              collisionDetection={closestCenter}
              onDragEnd={handleDragEnd}
            >
              <SortableContext
                items={recordOptions.map(record => record.id)}
                strategy={verticalListSortingStrategy}
              >
                <div className="list-group">
                  {recordOptions.map((record, index) => (
                    <SortableRecordOptionRow
                      key={record.id}
                      record={record}
                      index={index}
                      onToggleEnabled={(enabled) => onRecordOptionsUpdate(record.id, { enabled: !enabled })}
                      onWeightChange={(weight) => onRecordOptionsUpdate(record.id, { weight })}
                      onEdit={() => onRecordOptionsUpdate(record.id, null)}
                      onDelete={() => onRecordOptionsDelete(record.id)}
                    />
                  ))}
                </div>
              </SortableContext>
            </DndContext> : <div className="alert alert-info">
              No recordOptions available. Add recordOptions to get started.
            </div>}
          </div>
        </div>
      </div>
      <div className="modal-footer">
        <div className="d-flex gap-2 flex-grow-1">
          <Button
            variant="primary"
            onClick={() => setAddMode("add")}
          >
            Add Record
          </Button>
          <Button
            variant="danger"
            onClick={() => setShowDeleteConfirmation(true)}
            disabled={recordOptions.length === 0}
          >
            Delete All
          </Button>
        </div>
        <div className="d-flex gap-2">
          <Button
            variant="success"
            onClick={handleApplyChanges}
            disabled={!hasChanges}
          >
            Apply Changes
          </Button>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
        </div>
      </div>

      <ConfirmationModal
        isOpen={showDeleteConfirmation}
        title="Confirm Deletion"
        message={selectedRecordId ? "Are you sure you want to delete this record?" : "Are you sure you want to delete all records?"}
        onConfirm={selectedRecordId ? handleDeleteRecord : handleDeleteAll}
        onCancel={() => setShowDeleteConfirmation(false)}
        confirmText="Delete"
        cancelText="Cancel"
        confirmVariant="danger"
      />

      <Modal
        isOpen={addMode !== null}
        onClose={() => setAddMode(null)}
      >
        <AddRecordOptions
          mode={addMode || "add"}
          onUploadFiles={handleUploadFiles}
          selectedRecord={selectedRecordId ? recordOptions.find(r => r.id === selectedRecordId) : undefined}
          onAddRecordOptions={handleAddRecordOptions}
          onClose={() => setAddMode(null)}
        />
      </Modal>
    </div>
  );
};

export default EditRecordOptions;
