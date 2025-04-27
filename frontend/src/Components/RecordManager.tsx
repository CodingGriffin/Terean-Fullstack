// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import React, {useRef, useState} from "react";
import {nanoid} from 'nanoid'
import {Dialog} from "primereact/dialog";
import {Button} from "primereact/button";
import RecordStatusComponent from "./FileStatusComponent.js";
import axios from "axios";
import {backendUrl} from "../utils/utils.tsx";

export default function RecordManager({records, setRecords}) {
    const recordInputRef = useRef(null)
    const [showRecordsDialog, setShowRecordsDialog] = useState(false);
    const toggleRecordsDialog = () => {
        setShowRecordsDialog(!showRecordsDialog)
    }
    const handleAddMoreRecords = () => {
        recordInputRef.current.click();
    }
    const handleDeleteRecord = (idToDelete) => {
        setRecords((prevRecords) => {
            return prevRecords.filter((record) => record.id !== idToDelete)
        })
    }
    const handleRecordUpload = async (e) => {
        const filesArray = Array.from(e.target.files);
        const config = {
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'multipart/form-data',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,PATCH,OPTIONS',
                "Access-Control-Allow-Headers": "X-Requested-With",
            }
        }
        filesArray.forEach(
            (file) => {
                const newId = nanoid()
                setRecords(prevRecords => [...prevRecords, {
                    "id": newId,
                    "status": "Validating",
                    "errors": [],
                    "active": false,
                    "weight": 1.0,
                    "fileName": file.name,
                    "file": file,
                }])
                setTimeout(() => {
                    const formData = new FormData();
                    formData.append("file_data", file)
                    axios.post(
                        `${backendUrl}checkRecord`,
                        formData,
                        config
                    ).catch(error => {
                        console.log("Error occurred checking record.")
                        console.log(error)
                    }).then(response => {
                        const newErrors = [];
                        let newStatus;
                        if (response === undefined || response === null) {
                            newStatus = "Error"
                            newErrors.push("Error occurred checking record - response is null or undefined")
                        } else if (response.status < 200 || response.status > 299) {
                            newStatus = "Error"
                            newErrors.push("Error occurred checking record - response is null or undefined")
                        } else {
                            newStatus = "Complete"
                        }
                        setRecords((oldRecords) => {
                            return oldRecords.map((record) => {
                                    if (record.id === newId) {
                                        record['status'] = newStatus
                                        record['errors'] = newErrors
                                    }
                                    return record
                                }
                            )
                        })
                    })
                }, 500)
            }
        )
    }

    return (
        <div className="d-flex flex-column align-items-center">
            <h4 className="mb-0 text-center">Records</h4>
            <span className="mb-0 text-secondary">
                {records.length > 0
                    ? `${records.length} record(s) selected`
                    : "No records selected."
                }
            </span>
            <label
                htmlFor="record-files"
                className="btn btn-primary w-auto ms-2 mb-0"
                style={{cursor: "pointer"}}
                onClick={(e) => {
                    if (records.length > 0) {
                        e.preventDefault(); //necessary to include since we don't want the file explorer to pop up over the dialog every time
                        toggleRecordsDialog()
                    }
                }}
            >
                {records.length > 0 ? "Manage Records" : "Select Records"}
            </label>
            <input
                type="file"
                className={`form-control-file w-75 mt-2`}
                name="record_file_input"
                id="record-files"
                accept=".sgy,.seg2"
                multiple
                required
                onChange={handleRecordUpload}
                style={{display: "none"}} //need to hide default file input button to do required styling
            />
            <Dialog
                header="Velocity Models Files Selected"
                visible={showRecordsDialog}
                onHide={toggleRecordsDialog}
            >
                <ul style={{listStyleType: 'none'}}>
                    {records.map((record) => (
                        <li key={record.id} className="m-1">
                            <span className="me-1">{record.fileName}</span>
                            <RecordStatusComponent recordObj={record} height={30} width={30}/>
                            <Button type="button" className="btn btn-danger"
                                    onClick={() => handleDeleteRecord(record.id)}>Delete</Button>
                        </li>
                    ))}
                    <li>
                        <Button
                            type="button"
                            className={`btn btn-primary mt-3`}
                            onClick={handleAddMoreRecords}
                        >
                            Add More File(s)
                        </Button>
                        <input
                            type="file"
                            ref={recordInputRef}
                            className="d-none"
                            multiple
                            accept=".sgy,.seg2"
                            onChange={handleRecordUpload}
                        />
                    </li>
                </ul>
            </Dialog>
        </div>
    );
}