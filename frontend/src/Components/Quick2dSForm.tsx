// @ts-nocheck
import React, { useRef, useState } from "react";
import { Dialog } from "primereact/dialog";
import { Button } from "primereact/button";
import axios from "axios";
import { ProgressSpinner } from "primereact/progressspinner";
import { backendUrl } from "../utils/utils.tsx";
import { useSimpleFieldValidation } from "./SimpleValidationContext.tsx";
import FormHeader from "./form/FormHeader.tsx";

const Quick2dSForm = () => {
  const [showFiltersDialog, setShowFiltersDialog] = useState(false); //the popup window for advanced filters
  const [showVelocityModelsFilesDialog, setShowVelocityModelsFilesDialog] =
    useState(false);
  const [showContoursDialog, setShowContoursDialog] = useState(false); //the popup info window for contours
  const [showTitleDialog, setShowTitleDialog] = useState(false); //popup window for title
  const [showMaxDepthDialog, setShowMaxDepthDialog] = useState(false); //popup window for maxdepth/y-max
  const [showResolutionDialog, setShowResolutionDialog] = useState(false); //the popup window for Resolution
  const [showSmoothingDialog, setShowSmoothingDialog] = useState(false); //the popup window for Smoothing
  const [showVminDialog, setShowVminDialog] = useState(false); //the popup window for vMin
  const [showVmaxDialog, setShowVmaxDialog] = useState(false); //the popup window for vMax
  const [showColorbarDialog, setShowColorbarDialog] = useState(false); //the popup window for enable colorbar
  const [showYminDialog, setShowYminDialog] = useState(false); //the popup windown for ymin

  const [showElevationTickSizeDialog, setShowElevationTickSizeDialog] =
    useState(false); //temp use state for dialog until context is updated
  const [showColorbarFractionDialog, setShowColorbarFractionDialog] =
    useState(false); //temp use state for dialog until context is updated
  const [showColorbarOrientationDialog, setShowColorbarOrientationDialog] =
    useState(false); //temp use state for dialog until context is updated
  const [showAspectRatioDialog, setShowAspectRatioDialog] = useState(false); //temp use state for dialog until context is updated

  const fileInputRef = useRef(null);
  const [showDeletePrompt, setShowDeletePrompt] = useState(false);
  //   const [errors, setErrors] = useState({});

  const { errors, setErrors } = useSimpleFieldValidation();
  let duplicateErrorTimeout: NodeJS.Timeout | null = null;
  const [isFormSubmitting, setIsFormSubmitting] = useState(false);
  const [imageSrc, setImageSrc] = useState(null); //state to hold response logo
  const [excelFile, setExcelFile] = useState(null);
  const [formFiles, setFormFiles] = useState([]); //array to store values for formData, for some reason velocity files only work in array and not object
  const [formValues, setFormValues] = useState({
    title: "VsSurf ReMi 2dS™ - ",
    min_depth: "",
    max_depth: "",
    vel_min: "",
    vel_max: "",
    resolution: "0.2",
    smoothing: "20",
    x_min: "",
    x_max: "",
    y_label: "",
    x_label: "",
    cbar_label: "",
    label_pad_size: "-68",
    elevation_tick_increment: "50",
    cbar_pad_size: "0.05",
    contour_color: "k",
    contour_width: "0.8",
    aboveground_color: "w",
    aboveground_border_color: "",
    contours: {
      type: "",
      data: [],
    },
    invert_colorbar_axis: true,
    enable_colorbar: true,
    shift_elevation: true,
    display_as_depth: false,
    cbar_ticks: [],
    reverse_elevation: false,
    reverse_data: false,
    unit_override: "none",
    tick_right: false,
    tick_left: true,
    tick_top: true,
    tick_bottom: false,
    ticklabel_right: false,
    ticklabel_left: true,
    ticklabel_top: true,
    ticklabel_bottom: false,
    x_axis_label_pos: "top",
    y_axis_label_pos: "left",
    elevation_tick_size: 50,
    cbar_fraction: 0.05,
    cbar_orientation: "Vertical",
    aspect_ratio: "",
  });

  const toggleDialog = () => {
    setShowFiltersDialog((prev) => !prev);
  };

  const toggleInfoDialog = () => {
    setShowContoursDialog((prev) => !prev);
  };

  const toggleVelocityModelsFilesDialog = () => {
    setShowVelocityModelsFilesDialog((prev) => !prev);
  };

  const toggleTitleDialog = () => {
    setShowTitleDialog((prev) => !prev);
  };

  const toggleMaxDepthDialog = () => {
    setShowMaxDepthDialog((prev) => !prev);
  };

  const toggleResolutionDialog = () => {
    setShowResolutionDialog((prev) => !prev);
  };

  const toggleSmoothingDialog = () => {
    setShowSmoothingDialog((prev) => !prev);
  };

  const toggleVminDialog = () => {
    setShowVminDialog((prev) => !prev);
  };

  const toggleVmaxDialog = () => {
    setShowVmaxDialog((prev) => !prev);
  };

  const toggleColorBarDialog = () => {
    setShowColorbarDialog((prev) => !prev);
  };

  const toggleYminDialog = () => {
    setShowYminDialog((prev) => !prev);
  };

  const toggleElevationTickSizeDialog = () => {
    setShowElevationTickSizeDialog((prev) => !prev);
  };

  const toggleColorbarFractionDialog = () => {
    setShowColorbarFractionDialog((prev) => !prev);
  };

  const toggleColorbarOrientationDialog = () => {
    setShowColorbarOrientationDialog((prev) => !prev);
  };

  const toggleAspectRatioDialog = () => {
    setShowAspectRatioDialog((prev) => !prev);
  };

  const handleVelocityFileUpload = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    // Clear any previous errors
    setErrors((prevErrors) => ({
      ...prevErrors,
      invalid_files: "",
      duplicate_files: "",
    }));

    const filesArray = Array.from(e.target.files);

    // Your updated regex for filename validation
    const regex = /.*-(\d+\.?\d*)([mM]|[fF][tT])-[mM]odel\.txt/;

    const invalidFiles = [];
    const validFiles = [];
    const duplicateFiles = [];

    //track what file names we already have in a Set which is like array but automatically gets rid of duplicates
    const existingFileNames = new Set(formFiles.map((file) => file.name));

    // Process files asynchronously
    const fileReadPromises = filesArray.map((file) => {
      return new Promise((resolve, reject) => {
        if (regex.test(file.name) && !existingFileNames.has(file.name)) {
          const reader = new FileReader();
          reader.onload = (event) => {
            resolve({
              name: file.name,
              content: event.target.result,
              fileData: file,
            });
          };
          reader.onerror = () => {
            reject(`Failed to read file: ${file.name}`);
          };
          reader.readAsText(file);
        } else {
          if (!regex.test(file.name)) {
            invalidFiles.push(file.name);
          } else if (existingFileNames.has(file.name)) {
            duplicateFiles.push(file.name);
          }
          resolve(null); // Resolve null for invalid files
        }
      });
    });

    try {
      const processedFiles = await Promise.all(fileReadPromises);

      // Filter out null (invalid files) and add valid files to formFiles
      const validFileList = processedFiles.filter((file) => file !== null);
      validFiles.push(...validFileList);
      // processedFiles.forEach((file) => {
      //     if (file) validFiles.push(file);
      // });

      console.log("Valid Files Before Sorting:", validFiles);

      const sortedValidFiles = [...validFiles].sort((a, b) => {
        const regexMatchA = a.name.match(regex);
        const regexMatchB = b.name.match(regex);

        if (regexMatchA && regexMatchB) {
          const numberA = parseFloat(regexMatchA[1]);
          const numberB = parseFloat(regexMatchB[1]);
          return numberA - numberB;
        }

        return 0;
      });

      console.log("Sorted Valid Files:", sortedValidFiles);
      setFormFiles((prevFiles) => [...prevFiles, ...sortedValidFiles]);

      if (invalidFiles.length > 0) {
        setErrors((prevErrors) => ({
          ...prevErrors,
          invalid_files: `Invalid file(s): ${invalidFiles.join(
            ", "
          )}. Please select files with the correct naming convention.`,
        }));
      }

      if (duplicateFiles.length > 0) {
        setErrors((prevErrors) => ({
          ...prevErrors,
          duplicate_files: `Duplicate file(s): ${duplicateFiles.join(
            ", "
          )}. Please choose unique files.`,
        }));
        clearTimeout(duplicateErrorTimeout);
        duplicateErrorTimeout = setTimeout(() => {
          setErrors((prevErrors) => ({
            ...prevErrors,
            duplicate_files: "",
          }));
        }, 2000); // 2 seconds timeout
      }

      console.log("Valid files:", validFiles);
      console.log("Invalid files:", invalidFiles);
    } catch (error) {
      console.error("Error reading files:", error);
      setErrors((prevErrors) => ({
        ...prevErrors,
        velocity_files: "An error occurred while reading the files.",
      }));
    }
  };

  const handleAddMoreVelocityFiles = () => {
    fileInputRef.current.click();
  };

  const handleDeleteVelocityFile = (fileIndexToDelete) => {
    setFormFiles((prevFiles) => {
      return prevFiles.filter((file, index) => index !== fileIndexToDelete);
    });
  };

  const handleDeleteAllClick = () => {
    setShowDeletePrompt(true);
  };

  const handleDeleteAllVelocityFiles = () => {
    setFormFiles([]);

    setShowDeletePrompt(false);
  };

  const handleCancelDelete = () => {
    setShowDeletePrompt(false);
  };

  const handleExcelUpload = (e) => {
    if (e.target.files.length !== 1) {
      return;
    }
    const file = e.target.files[0];
    setExcelFile(file);
  };

  const validateSingleField = (id, value) => {
    const errors = {};

    const isFloat = (val) => {
      const floatRegex = /^-?\d+(?:[.,]\d*?)?$/;
      if (!floatRegex.test(val)) return false;
      val = parseFloat(val);
      return !isNaN(val);
    };

    const isPositiveInteger = (val) =>
      !isNaN(val) && Number.isInteger(parseFloat(val)) && parseFloat(val) > 0;

    const isPositiveIntegerOrZero = (val) =>
      !isNaN(val) && Number.isInteger(parseFloat(val)) && parseFloat(val) >= 0;

    const isPositiveFloat = (val) => {
      // Allow intermediate negative values or empty strings
      if (val === "" || val === "-" || val === "-.") {
        return true;
      }
      return !isNaN(val) && parseFloat(val) > 0;
    };

    if (id === "max_depth" && !isPositiveFloat(value)) {
      errors.max_depth = "Max Depth must be a positive float.";
    }

    if (id === "resolution" && !isPositiveFloat(value)) {
      errors.resolution = "Resolution must be a positive float.";
    }

    if (id === "smoothing" && value !== "" && !isPositiveIntegerOrZero(value)) {
      errors.smoothing =
        "Smoothing must be an integer greater than or equal to 0.";
    }

    if (id === "vel_min" && !isPositiveFloat(value)) {
      errors.vel_min = "vMin must be a positive float.";
    }

    if (id === "vel_max" && !isPositiveFloat(value)) {
      errors.vel_max = "vMax must be a positive float.";
    }

    if (id === "min_depth" && !isPositiveFloat(value)) {
      errors.min_depth = "Y-Min must be a positive float.";
    }

    if (id === "x_min" && !isPositiveFloat(value)) {
      errors.x_min = "X-Min must be a positive float.";
    }

    if (id === "x_max" && !isPositiveFloat(value)) {
      errors.x_max = "X-Max must be a positive float.";
    }

    if (id === "contour_width" && !isPositiveFloat(value)) {
      errors.contour_width = "Contour width must be a positive float.";
    }

    if (id === "elevation_tick_size" && !isFloat(value)) {
      errors.elevation_tick_size =
        "Elevation Tick Size must be a positive float.";
    }

    if (id === "cbar_fraction" && !isFloat(value)) {
      errors.cbar_fraction = "Colobar Fraction must be a positive float.";
    }

    if (id === "aspect_ratio" && !isFloat(value)) {
      errors.aspect_ratio = "Aspect Ratio must be a positive float.";
    }

    if (id === "label_pad_size" && !isFloat(value)) {
      errors.label_pad_size = "Label Pad Size must be a positive float.";
    }

    if (id === "elevation_tick_increment" && !isFloat(value)) {
      errors.elevation_tick_increment =
        "Elevation Increment must be a positive float.";
    }

    if (id === "cbar_pad_size" && !isFloat(value)) {
      errors.cbar_pad_size = "Cbar Pad Size must be a positive float.";
    }

    return errors;
  };

  const handleContoursInput = (value) => {
    setFormValues((prev) => ({
      ...prev,
      contours: {
        ...prev.contours,
        rawInput: value, // Update raw input freely
      },
    }));
  };

  //have to have it validate when the user leaves the field due to it being a more complicated field, can refine later
  const validateContours = () => {
    const rawInput = formValues.contours.rawInput.trim().toLowerCase();

    if (rawInput === "none") {
      setErrors((prev) => ({
        ...prev,
        contours: "", // Clear errors
      }));

      setFormValues((prev) => ({
        ...prev,
        contours: {
          rawInput, // Preserve raw input
          type: "none",
          data: [], // Empty array for 'none'
        },
      }));
    } else if (rawInput === "") {
      setErrors((prev) => ({
        ...prev,
        contours: "", // No error for empty input
      }));

      setFormValues((prev) => ({
        ...prev,
        contours: {
          rawInput, // Preserve raw input
          type: "",
          data: [], // Clear data
        },
      }));
    } else {
      const segments = rawInput
        .split(",")
        .map((segment) => {
          return segment.trim();
        })
        .filter((segment) => {
          console.log("Segment is:", segment);
          console.log("Segment type is:", typeof segment);
          let validSegment = segment != null && segment.length > 0;
          console.log("Segment bool is", validSegment);
          return validSegment;
        });
      const invalidSegments = segments.filter((segment) => {
        const parsed = parseFloat(segment);
        return segment !== "" && (isNaN(parsed) || parsed <= 0);
      });

      if (invalidSegments.length > 0) {
        setErrors((prev) => ({
          ...prev,
          contours:
            "Invalid input. Use 'none', an integer, or a comma-separated list of positive floats.",
        }));
      } else {
        setErrors((prev) => ({
          ...prev,
          contours: "", // Clear errors
        }));

        // If more than one segment, it's type list
        if (segments.length > 1) {
          setFormValues((prev) => ({
            ...prev,
            contours: {
              rawInput, // Preserve raw input
              type: "list",
              data: segments.map((segment) => parseFloat(segment)), // Convert to floats
            },
          }));
        } else if (segments.length === 1) {
          // It's either a single int, or a float
          // Check if segment contains "." as a shorthand
          // This lets us submit "X.0" if we want a single float processed, so it doesn't set as an int
          let segment = segments[0];
          console.log("Parsing single segment, of value", segment);
          if (segment.includes(".")) {
            setFormValues((prev) => ({
              ...prev,
              contours: {
                rawInput, // Preserve raw input
                type: "list",
                data: segments.map((segment) => {
                  return parseFloat(segment);
                }), // Convert to floats
              },
            }));
          } else {
            setFormValues((prev) => ({
              ...prev,
              contours: {
                rawInput, // Preserve raw input
                type: "integer",
                data: parseInt(segment),
              },
            }));
          }
        }
      }
    }
  };

  //have to have it validate when the user leaves the field for right now due to it being a more complicated field, can refine later
  const validateCbarTicks = () => {
    const values = formValues.cbar_ticks;

    const invalidValues = values.filter((val) => {
      const parsedValue = parseFloat(val);
      return isNaN(parsedValue) || parsedValue <= 0;
    });

    if (invalidValues.length > 0) {
      setErrors((prev) => ({
        ...prev,
        cbar_ticks: "Cbar Ticks must be a list of positive floats.",
      }));
    } else {
      setErrors((prev) => ({
        ...prev,
        cbar_ticks: "", // Clear any errors if valid
      }));
    }
  };

  const handleStringInput = (e) => {
    const { name, value } = e.target;

    // Validate field
    const fieldErrors = validateSingleField(name, value);

    // Update errors state for invalid inputs
    setErrors((prev) => ({
      ...prev,
      [name]: fieldErrors[name] || "", // Clear error if validation passes
    }));

    // Always update formValues to reflect user's input
    setFormValues((prev) => ({
      ...prev,
      [name]: value, // Allow intermediate values, even if temporarily invalid
    }));
  };

  const handleBooleanInput = (e) => {
    const { name, checked } = e.target;

    setFormValues((prev) => ({
      ...prev,
      [name]: checked,
    }));
  };

  const handleSelectInput = (e) => {
    const { name, value } = e.target;

    setFormValues((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const contourHeader = () => {
    return (
      <>
        <div
          id="pr_id_7_header"
          className="p-dialog-title"
          data-pc-section="headertitle"
        >
          <i className="pi pi-info-circle"></i>Valid Contour Inputs
        </div>
      </>
    );
  };

  const handleAdvancedFiltersSave = () => {
    toggleDialog();
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    setIsFormSubmitting(true);

    console.log("Form Files before submission:", formFiles);
    console.log(formValues);
    const config = {
      headers: {
        Accept: "application/json",
        "Content-Type": "multipart/form-data",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET,PUT,POST,DELETE,PATCH,OPTIONS",
        "Access-Control-Allow-Headers": "X-Requested-With",
      },
    };
    const formData = new FormData();

    if (formValues.contours && formValues.contours.type) {
      if (
        formValues.contours.type === "integer" ||
        formValues.contours.type === "list"
      ) {
        formData.append(
          "contours",
          JSON.stringify({
            type: formValues.contours.type,
            data: formValues.contours.data || [],
          })
        );
      } else {
        console.error("Invalid contours type:", formValues.contours);
      }
    }

    if (formValues.cbar_ticks && formValues.cbar_ticks.length > 0) {
      // If cbar_ticks has values, append them to formData
      for (let i = 0; i < formValues.cbar_ticks.length; i++) {
        formData.append("cbar_ticks", formValues.cbar_ticks[i]);
      }
    } else {
      // I tried formData.append("cbar_ticks",[]), formData.append("cbar_ticks","", amd formData.append("cbar_ticks", JSON.stringify([]))
      console.log(
        "cbar_ticks is empty, not appending to formData.Can't force it to accept an empty array even when i try doing JSON.stringify()"
      );
    }

    for (const key in formValues) {
      const value = formValues[key];
      console.log(key, value, typeof value);
      // If formValues is null, undefined, or an empty string simply don't include it
      if (value === undefined || value === null || /^\s*$/.test(value)) {
        console.log(`Skipping key ${key}`);
        continue;
      }
      if (key !== "contours" && key !== "cbar_ticks") {
        // Exclude contours from the loop
        if (typeof formValues[key] === "boolean") {
          formData.append(key, formValues[key]);
        } else {
          formData.append(key, formValues[key] || "");
        }
      }
    }

    if (formFiles && formFiles.length > 0) {
      formFiles.forEach((fileObj) => {
        if (fileObj && fileObj.fileData) {
          formData.append("velocity_models", fileObj.fileData); // Append the fileData to the formData
        }
      });
    }

    if (excelFile !== null && excelFile !== undefined) {
      formData.append("elevation_data", excelFile);
    }

    try {
      console.log(formData);
      axios
        .post(
          `${backendUrl}process2dS`,
          formData,
          { responseType: "arraybuffer" }, //may need this for response binary of png
          config
        )
        .catch((error) => {
          console.log("Error occurred on form post.");
          console.log(error);
        })
        .then((response) => {
          console.log("response is ", response);
          if (response === undefined || response === null) {
            console.log(
              "Error occurred on form post - Response is null or undefined"
            );
          } else if (response.status < 200 || response.status > 299) {
            console.log("Error occurred on form post - Status is not 2XX.");
            console.log(response);
          } else {
            console.log(response.data); // Log the raw response data
            console.log("Response Headers:", response.headers);
            console.log("Response Data Type:", typeof response.data);

            if (response.data.constructor.name === "ArrayBuffer") {
              console.log(
                "ArrayBuffer received, size:",
                response.data.byteLength
              );

              // Create a Blob from the ArrayBuffer
              const blob = new Blob([response.data], { type: "image/png" });

              // Create an Object URL for the Blob
              const imageUrl = URL.createObjectURL(blob);

              // Set the image source (imageSrc)
              setImageSrc(imageUrl);
            } else {
              console.error("Expected ArrayBuffer, but got:", response.data);
            }
          }
        })
        .finally(() => {
          setIsFormSubmitting(false);
        });
    } catch (err) {
      console.error("Error occurred in form submission callback:", err);
    }
  };

  return (
    <div
      className="form-div mx-auto bg-light border border-1 col-xxl-6 mt-4"
      style={{ position: "relative", minHeight: "300px" }}
    >
      {/* Header Section*/}
      <div className="title-div px-4 pt-4 pb-2">
        <div className="row align-items-center">
          <div className="col"></div>
          <div className="col text-center">
            <h2 className="text-light fs-1">2dS Form</h2>
          </div>
          <div className="col text-end">
            <button
              className="advancedfilters-button border border-1 border-white dropdown text-light"
              type="button"
              onClick={toggleDialog}
            >
              Advanced Filters <i className="pi pi-arrow-down"></i>
            </button>
          </div>
        </div>
      </div>

       {/* form content */}
      <form className="px-4 pb-4" onSubmit={handleFormSubmit}>
        <div className="container p-4">

          {/* title, velocity, and elevation section */}
          <div className="mb-4">
            <div className="bg-white rounded-1 border border-1 p-2">
              <div className="container p-1">
                <div className="row justify-content-center align-items-center">
                  <div className="mb-3 col-6">
                    <label htmlFor="title" className="form-label">
                      Title
                    </label>
                    <button
                      type="button"
                      onClick={toggleTitleDialog}
                      aria-label="Toggle information dialog"
                      className="icon-button"
                    >
                      <i className="pi pi-question-circle" />
                    </button>

                    <input
                      type="text"
                      className="form-control px-1 py-1 bg-white rounded-3 border border-1"
                      name="title"
                      id="title"
                      value={formValues.title || ""}
                      onChange={handleStringInput}
                      placeholder="Example"
                    />
                    <Dialog
                      header="Title Information"
                      visible={showTitleDialog}
                      onHide={toggleTitleDialog}
                    >
                      <div className="card">
                        <p>The title is displayed above the plot</p>
                      </div>
                    </Dialog>
                  </div>
                </div>
              </div>

              {/* velocity and elevation content */}
              <div className="container">
                <div className="row mb-3 bg-white border border-1">
                  <div className="col-6 d-flex flex-column align-items-center">
                    <h4 className="mb-0 text-center">Velocity Models</h4>

                    {/* Need to add in custom label, input, and span to get it dynamically updating */}
                    <div className="custom-file-wrapper d-flex flex-column align-items-center">
                      <span className="mt-1 text-secondary">
                        {formFiles.length > 0
                          ? `${formFiles.length} file(s) selected`
                          : "Please select at least one .txt file"}
                      </span>

                      <label
                        htmlFor="velocity-files"
                        className="btn btn-primary w-auto ms-2 mb-2"
                        style={{ cursor: "pointer" }}
                        onClick={(e) => {
                          if (formFiles.length > 0) {
                            e.preventDefault(); //necessary to include since we dont want the file explorer to pop up over the dialog every time
                            toggleVelocityModelsFilesDialog(); // Open dialog only if files are selected
                          }
                        }}
                      >
                        {formFiles.length > 0 ? "View/Edit Files" : "Choose Files"}
                      </label>

                      <input
                        type="file"
                        className={`form-control-file w-75 mt-2 ${
                          errors.velocity_files ? "is-invalid" : ""
                        }`}
                        name="velocity_models"
                        id="velocity-files"
                        accept=".txt"
                        multiple
                        required
                        onChange={handleVelocityFileUpload}
                        style={{ display: "none" }} //need to hide default file input button to do required styling
                      />

                      {errors.velocity_files && (
                        <span className="text-danger">{errors.velocity_files}</span>
                      )}

                      <Dialog
                        header="Velocity Models Files Selected"
                        visible={showVelocityModelsFilesDialog}
                        onHide={toggleVelocityModelsFilesDialog}
                      >
                        <ul
                          className="velocity-files-list"
                          style={{ listStyleType: "none" }}
                        >
                          {formFiles.map((file, index) => (
                            <li key={index} className="m-1">
                              <span className="me-1">{file.name}</span>
                              <Button type="button" className="btn btn-secondary m-1">
                                Edit
                              </Button>
                              <Button
                                type="button"
                                className="btn btn-danger m-1"
                                onClick={() => handleDeleteVelocityFile(index)}
                              >
                                Delete
                              </Button>
                            </li>
                          ))}
                          <li className="bg-white">
                            <Button
                              type="button"
                              className={`btn btn-primary mt-3 ${
                                errors.length === 0 && formFiles.length === 0
                                  ? "is-invalid"
                                  : ""
                              }`}
                              onClick={handleAddMoreVelocityFiles}
                            >
                              Add More File(s)
                            </Button>

                            {formFiles.length > 0 && (
                              <button
                                className="btn btn-danger mt-3"
                                onClick={handleDeleteAllClick}
                              >
                                Delete All Files
                              </button>
                            )}

                            <input
                              type="file"
                              ref={fileInputRef}
                              className="d-none"
                              multiple
                              accept=".txt"
                              onChange={handleVelocityFileUpload}
                            />
                          </li>

                          <li>
                            {showDeletePrompt && (
                              <div className="delete-prompt-container container text-center w-100">
                                <span className="d-block">
                                  Are you sure you want to delete all files?
                                </span>
                                <button
                                  className="btn btn-danger"
                                  onClick={handleDeleteAllVelocityFiles}
                                >
                                  Yes, Delete All
                                </button>
                                <button
                                  className="btn btn-secondary"
                                  onClick={handleCancelDelete}
                                >
                                  Cancel
                                </button>
                              </div>
                            )}
                          </li>

                          <li>
                            {errors.invalid_files && (
                              <span className="text-danger">
                                {errors.invalid_files}
                              </span>
                            )}
                            {errors.duplicate_files && (
                              <span className="text-danger">
                                {errors.duplicate_files}
                              </span>
                            )}
                          </li>
                        </ul>
                      </Dialog>
                    </div>
                  </div>

                  {/* NEED TO ADD VERTICAL DIVIDER HERE or BORDER_RIGHT AND BORDER_LEFT */}

                  <div className="col-6 d-flex flex-column align-items-center">
                    <h4 className="mb-0 text-center">Elevation</h4>

                    <div className="custom-file-wrapper d-flex flex-column align-items-center">
                      <span className="mt-1 text-secondary">
                        {excelFile !== null && excelFile !== undefined
                          ? excelFile.name
                          : "Click below to select an elevation spreadsheet."}
                      </span>

                      <div className="custom-file-wrapper d-flex flex-row align-items-center gap-2">
                        <label
                          htmlFor="elevation-upload"
                          className="btn btn-primary w-auto mb-0"
                          style={{ cursor: "pointer" }}
                        >
                          {excelFile !== null && excelFile !== undefined
                            ? "Change"
                            : "Select File"}
                        </label>
                        <input
                          type="file"
                          className={`form-control-file w-75 mt-2`}
                          name="excel_file_input"
                          id="elevation-upload"
                          accept=".xls, .xlsx"
                          onChange={handleExcelUpload}
                          style={{ display: "none" }} //need to hide default file input button to do required styling
                        />
                        {excelFile !== null && excelFile !== undefined ? (
                          <Button
                            type="button"
                            className="btn btn-danger"
                            onClick={() => setExcelFile(null)}
                          >
                            Delete
                          </Button>
                        ) : null}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Max Depth, Resolution, vMin, vMax, and smoothing content */}
          <div className="mb-4">
            <div className="container bg-white rounded-1 border border-1 p-2">
              <div className="row">
                <div className="col-6">
                  <div className="mb-3">
                    <label htmlFor="max_depth" className="form-label">
                      Max Depth (Y-Max)
                    </label>
                    <button
                      type="button"
                      onClick={toggleMaxDepthDialog}
                      aria-label="Toggle information dialog"
                      className="icon-button"
                    >
                      <i className="pi pi-question-circle" />
                    </button>

                    <input
                      type="text"
                      className={`form-control ${
                        errors.max_depth ? "is-invalid" : ""
                      }`}
                      name="max_depth"
                      id="max_depth"
                      value={formValues.max_depth || ""}
                      onChange={handleStringInput}
                      // onBlur={(e) => handleChange(e, "main", true)}
                      placeholder="0.00"
                    />
                    {errors.max_depth && (
                      <span className="error">{errors.max_depth}</span>
                    )}

                    <Dialog
                      header="Max Depth Information"
                      visible={showMaxDepthDialog}
                      onHide={toggleMaxDepthDialog}
                    >
                      <div className="card">
                        <p>
                          Max depth to plot to - uses units parsed from the velocity
                          model, or from unit override if it's provided.
                        </p>
                      </div>
                    </Dialog>
                  </div>

                  <div className="mb-3">
                    <label htmlFor="resolution" className="form-label">
                      Resolution
                    </label>
                    <button
                      type="button"
                      onClick={toggleResolutionDialog}
                      aria-label="Toggle information dialog"
                      className="icon-button"
                    >
                      <i className="pi pi-question-circle" />
                    </button>

                    <input
                      type="text"
                      className={`form-control ${
                        errors.resolution ? "is-invalid" : ""
                      }`}
                      name="resolution"
                      id="resolution"
                      value={formValues.resolution || ""}
                      onChange={handleStringInput}
                      // onBlur={(e) => handleChange(e, "main", true)}
                      placeholder="0.00"
                    />
                    {errors.resolution && (
                      <span className="error">{errors.resolution}</span>
                    )}

                    <Dialog
                      header="Resolution Information"
                      visible={showResolutionDialog}
                      onHide={toggleResolutionDialog}
                    >
                      <div className="card">
                        <p>
                          The number of units/pixel, e.g, if 0.1 is chosen and the
                          units are feet there will be 10 pixels/foot
                        </p>
                      </div>
                    </Dialog>
                  </div>

                  <div className="mb-3">
                    <label htmlFor="smoothing" className="form-label">
                      Smoothing
                    </label>
                    <button
                      type="button"
                      onClick={toggleSmoothingDialog}
                      aria-label="Toggle information dialog"
                      className="icon-button"
                    >
                      <i className="pi pi-question-circle" />
                    </button>

                    <input
                      type="text"
                      className={`form-control ${
                        errors.smoothing ? "is-invalid" : ""
                      }`}
                      name="smoothing"
                      id="smoothing"
                      value={formValues.smoothing || ""}
                      onChange={handleStringInput}
                      // onBlur={(e) => handleChange(e, "main", true)}
                      placeholder="1"
                    />
                    {errors.smoothing && (
                      <span className="error">{errors.smoothing}</span>
                    )}

                    <Dialog
                      header="Smoothing Information"
                      visible={showSmoothingDialog}
                      onHide={toggleSmoothingDialog}
                    >
                      <div className="card">
                        <p>
                          Size of the smoothing gaussian, in pixels. 0 disables
                          smoothing entirely.
                        </p>
                      </div>
                    </Dialog>
                  </div>
                </div>

                <div className="col-6">
                  <div className="mb-3">
                    <label htmlFor="vel_min" className="form-label">
                      vMin
                    </label>
                    <button
                      type="button"
                      onClick={toggleVminDialog}
                      aria-label="Toggle information dialog"
                      className="icon-button"
                    >
                      <i className="pi pi-question-circle" />
                    </button>

                    <input
                      type="text"
                      className={`form-control ${
                        errors.vel_min ? "is-invalid" : ""
                      }`}
                      name="vel_min"
                      id="vel_min"
                      value={formValues.vel_min || ""}
                      onChange={handleStringInput}
                      // onBlur={(e) => handleChange(e, "main", true)}
                      placeholder="0.00"
                    />
                    {errors.vel_min && (
                      <span className="error">{errors.vel_min}</span>
                    )}

                    <Dialog
                      header="Minimum Velocity Information"
                      visible={showVminDialog}
                      onHide={toggleVminDialog}
                    >
                      <div className="card">
                        <p>Minimum velocity when generating the colormap.</p>
                      </div>
                    </Dialog>
                  </div>

                  <div className="mb-3">
                    <label htmlFor="vel_max" className="form-label">
                      vMax
                    </label>
                    <button
                      type="button"
                      onClick={toggleVmaxDialog}
                      aria-label="Toggle information dialog"
                      className="icon-button"
                    >
                      <i className="pi pi-question-circle" />
                    </button>

                    <input
                      type="text"
                      className={`form-control ${
                        errors.vel_max ? "is-invalid" : ""
                      }`}
                      name="vel_max"
                      id="vel_max"
                      value={formValues.vel_max || ""}
                      onChange={handleStringInput}
                      // onBlur={(e) => handleChange(e, "main", true)}
                      placeholder="0.00"
                    />
                    {errors.vel_max && (
                      <span className="error">{errors.vel_max}</span>
                    )}

                    <Dialog
                      header="Maximum Velocity Information"
                      visible={showVmaxDialog}
                      onHide={toggleVmaxDialog}
                    >
                      <div className="card">
                        <p>Maximum velocity when generating the colormap.</p>
                      </div>
                    </Dialog>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* contours section */}
          <div className="container bg-white rounded-1 border border-1 p-4">
            <div className="row justify-content-center">
              <h3>
                <u>Contours</u>
              </h3>

              <div className="col-6 pb-1 border">
                <div className="row ps-3 pe-3 pt-3">
                  <div className="col-1">
                    <label htmlFor="contours" className="form-label col-1">
                      Contours
                    </label>
                  </div>

                  <div className="col-auto ms-auto">
                    <button
                      type="button"
                      onClick={toggleInfoDialog}
                      aria-label="Toggle information dialog"
                      className="icon-button"
                    >
                      <i className="pi pi-question-circle" />
                    </button>
                  </div>
                </div>

                <div className="row align-items-center justify-content-center pb-3">
                  <div className="col-11">
                    <input
                      type="text"
                      className={`form-control ${
                        errors.contours ? "is-invalid" : ""
                      }`}
                      name="contours"
                      id="contours"
                      value={formValues.contours.rawInput || ""}
                      onChange={(e) => handleContoursInput(e.target.value)}
                      onBlur={validateContours} //some tricky timing im trying to get to work ideally in realtime but for now we are doing it once the user leaves the focus of the input
                      placeholder="Please enter contours as specified by info circle"
                    />

                    {errors.contours && (
                      <span className="error">{errors.contours}</span>
                    )}
                  </div>
                </div>
                <Dialog
                  header={contourHeader}
                  visible={showContoursDialog}
                  onHide={toggleInfoDialog}
                >
                  <div className="card">
                    <p>
                      Please enter either <span className="bold">none</span>, a
                      single integer greater than zero, or a list of float numbers
                      all greater than zero separated by commas. To enter a single,
                      specific contour use a decimal.
                    </p>
                    <p>
                      eg: 1750.0 will generate a single contour at 1750, however
                      1750 will generate 1,750 contours.
                    </p>
                  </div>
                </Dialog>
            </div>
          </div>
        </div>
            
        <div className="container col-3 pt-4">
          <button
              className="btn btn-primary w-100 px-5 py-3 fw-bold"
              type="submit"
            >
              Submit
            </button>
            <div className="row">
              {imageSrc && (
                <div style={{ marginTop: "20px" }}>
                  <img
                    src={imageSrc}
                    alt="Form Successful return"
                    style={{ width: "auto", height: "auto" }}
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      </form>
      {isFormSubmitting && (
        <div
          style={{
            position: "absolute", // Position relative to form-div
            top: 0, // Align to the top of the form-div
            left: 0, // Align to the left of the form-div
            width: "100%", // Take up full width of the form-div
            height: "100%", // Take up full height of the form-div
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            backgroundColor: "rgba(255, 255, 255, 0.8)",
            zIndex: 1000, // Ensure spinner is above other content
          }}
        >
          <ProgressSpinner
            style={{
              borderTopColor: "red",
              borderRightColor: "blue",
              borderBottomColor: "green",
              borderLeftColor: "yellow",
              width: "50px",
              height: "50px",
            }}
          />
        </div>
      )}

      <Dialog
        header="Advanced Filters"
        visible={showFiltersDialog}
        onHide={toggleDialog}
      >
        <form className="container">
          <div className="container">
            <div className="row">
              <div className="col-6">
                <div className="mb-3">
                  <label htmlFor="min_depth" className="form-label">
                    Y-Min
                  </label>
                  <button
                    type="button"
                    onClick={toggleYminDialog}
                    aria-label="Toggle information dialog"
                    className="icon-button"
                  >
                    <i className="pi pi-question-circle" />
                  </button>

                  <input
                    type="text"
                    className={`form-control ${
                      errors.min_depth ? "is-invalid" : ""
                    }`}
                    name="min_depth"
                    id="min_depth"
                    value={formValues.min_depth || ""}
                    onChange={handleStringInput}
                    // onBlur={(e) => handleChange(e, "dialog", true)}
                  />
                  {errors.min_depth && (
                    <span className="error">{errors.min_depth}</span>
                  )}

                  <Dialog
                    header="Ymin Information"
                    visible={showYminDialog}
                    onHide={toggleYminDialog}
                  >
                    <div className="card">
                      <p>
                        Minimum height value. May be adjusted to better display
                        elevation.
                      </p>
                      <p>
                        If a value is present here, it overwrites{" "}
                        <strong>any</strong> behavior from shift elevation.
                      </p>
                    </div>
                  </Dialog>
                </div>

                <div className="mb-3">
                  <label htmlFor="x_min" className="form-label">
                    X-Min
                  </label>
                  <input
                    type="text"
                    className={`form-control ${
                      errors.x_min ? "is-invalid" : ""
                    }`}
                    name="x_min"
                    id="x_min"
                    value={formValues.x_min || ""}
                    onChange={handleStringInput}
                    // onBlur={(e) => handleChange(e, "dialog", true)}
                  />
                  {errors.x_min && (
                    <span className="error">{errors.x_min}</span>
                  )}
                </div>

                <div className="mb-3">
                  <label htmlFor="x_max" className="form-label">
                    X-Max
                  </label>
                  <input
                    type="text"
                    className={`form-control ${
                      errors.x_max ? "is-invalid" : ""
                    }`}
                    name="x_max"
                    id="x_max"
                    value={formValues.x_max || ""}
                    onChange={handleStringInput}
                    // onBlur={(e) => handleChange(e, "dialog", true)}
                  />
                  {errors.x_max && (
                    <span className="error">{errors.x_max}</span>
                  )}
                </div>
              </div>

              <div className="col-6">
                <div className="mb-3">
                  <label htmlFor="unit_override" className="form-label">
                    Unit Override
                  </label>
                  <select
                    className="form-control"
                    name="unit_override"
                    id="unit_override"
                    value={formValues.unit_override}
                    onChange={handleSelectInput}
                  >
                    <option value="none">None</option>
                    <option value="meters">Meters</option>
                    <option value="feet">Feet</option>
                  </select>
                </div>

                <div className="mb-3">
                  <label htmlFor="x_axis_label_pos" className="form-label">
                    X-Axis Label
                  </label>
                  <select
                    className="form-control"
                    name="x_axis_label_pos"
                    id="x_axis_label_pos"
                    value={formValues.x_axis_label_pos}
                    onChange={handleSelectInput}
                  >
                    <option value="top">Top</option>
                    <option value="bottom">Bottom</option>
                  </select>
                </div>

                <div className="mb-3">
                  <label htmlFor="y_axis_label_pos" className="form-label">
                    Y-Axis Label
                  </label>
                  <select
                    className="form-control"
                    name="y_axis_label_pos"
                    id="y_axis_label_pos"
                    value={formValues.y_axis_label_pos}
                    onChange={handleSelectInput}
                  >
                    <option value="left">Left</option>
                    <option value="right">Right</option>
                  </select>
                </div>

                <div className="container mb-3 px-0">
                  <div className="form-check d-flex justify-content-start">
                    <input
                      type="checkbox"
                      className="form-check-input me-2"
                      name="enable_colorbar"
                      id="enable_colorbar"
                      checked={formValues.enable_colorbar}
                      onChange={handleBooleanInput}
                      aria-describedby="enableColorbarHelp"
                    />
                    <label
                      className="form-check-label"
                      htmlFor="enable_colorbar"
                    >
                      Enable Colorbar
                    </label>

                    <button
                      type="button"
                      onClick={toggleColorBarDialog}
                      aria-label="Toggle information dialog"
                      className="icon-button"
                    >
                      <i className="pi pi-question-circle" />
                    </button>
                  </div>

                  <Dialog
                    header="Enable Colorbar Information"
                    visible={showColorbarDialog}
                    onHide={toggleColorBarDialog}
                  >
                    <div className="card">
                      <p>
                        Can include a colorbar that will display on the right
                        side of the plot.
                      </p>
                    </div>
                  </Dialog>
                </div>
              </div>
            </div>
          </div>

          <div className="row mb-3">
            <div className="col-4 border p-3">
              <div className="mb-3">
                <label htmlFor="y_label" className="form-label">
                  Y-Label
                </label>
                <input
                  type="text"
                  className="form-control"
                  name="y_label"
                  id="y_label"
                  value={formValues.y_label || ""}
                  onChange={handleStringInput}
                  // onBlur={(e) => handleChange(e, "dialog", true)}
                />
              </div>

              <div className="mb-3">
                <label htmlFor="x_label" className="form-label">
                  X-Label
                </label>
                <input
                  type="text"
                  className="form-control"
                  name="x_label"
                  id="x_label"
                  value={formValues.x_label || ""}
                  onChange={handleStringInput}
                  // onBlur={(e) => handleChange(e, "dialog", true)}
                />
              </div>

              <div className="mb-3">
                <label htmlFor="cbar_label" className="form-label">
                  Colorbar Label
                </label>
                <input
                  type="text"
                  className="form-control"
                  name="cbar_label"
                  id="cbar_label"
                  value={formValues.cbar_label || ""}
                  onChange={handleStringInput}
                  // onBlur={(e) => handleChange(e, "dialog", true)}
                />
              </div>

              <div className="mb-3">
                <label htmlFor="contour_color" className="form-label">
                  Contour Color
                </label>
                <input
                  type="text"
                  className="form-control"
                  name="contour_color"
                  id="contour_color"
                  value={formValues.contour_color || ""}
                  onChange={handleStringInput}
                  // onBlur={(e) => handleChange(e, "dialog", true)}
                />
              </div>

              <div className="mb-3">
                <label htmlFor="contour_width" className="form-label">
                  Contour Width
                </label>
                <input
                  type="text"
                  className={`form-control ${
                    errors.contour_width ? "is-invalid" : ""
                  }`}
                  name="contour_width"
                  id="contour_width"
                  value={formValues.contour_width || ""}
                  onChange={handleStringInput}
                  // onBlur={(e) => handleChange(e, "dialog", true)}
                />
                {errors.contour_width && (
                  <span className="error">{errors.contour_width}</span>
                )}
              </div>

              <div className="mb-3">
                <label htmlFor="elevation_tick_size" className="form-label">
                  Elevation Tick Size
                </label>
                <button
                  type="button"
                  onClick={toggleElevationTickSizeDialog}
                  aria-label="Toggle information dialog"
                  className="icon-button"
                >
                  <i className="pi pi-question-circle" />
                </button>
                <input
                  type="text"
                  className={`form-control ${
                    errors.elevation_tick_size ? "is-invalid" : ""
                  }`}
                  name="elevation_tick_size"
                  id="elevation_tick_size"
                  value={formValues.elevation_tick_size || ""}
                  onChange={handleStringInput}
                  // onBlur={(e) => handleChange(e, "dialog", true)}
                />
                {errors.elevation_tick_size && (
                  <span className="error">{errors.elevation_tick_size}</span>
                )}

                <Dialog
                  header="Elevation Tick Size Information"
                  visible={showElevationTickSizeDialog}
                  onHide={toggleElevationTickSizeDialog}
                >
                  <div className="card">
                    <p>
                      Number of feet between ticks on the plot when plotting
                      with elevation.
                    </p>
                  </div>
                </Dialog>
              </div>

              <div className="mb-3">
                <label htmlFor="cbar_fraction" className="form-label">
                  Colorbar Fraction
                </label>
                <button
                  type="button"
                  onClick={toggleColorbarFractionDialog}
                  aria-label="Toggle information dialog"
                  className="icon-button"
                >
                  <i className="pi pi-question-circle" />
                </button>

                <input
                  type="text"
                  className={`form-control ${
                    errors.cbar_fraction ? "is-invalid" : ""
                  }`}
                  name="cbar_fraction"
                  id="cbar_fraction"
                  value={formValues.cbar_fraction || ""}
                  onChange={handleStringInput}
                  // onBlur={(e) => handleChange(e, "dialog", true)}
                />
                {errors.cbar_fraction && (
                  <span className="error">{errors.cbar_fraction}</span>
                )}

                <Dialog
                  header="Colorbar Fraction Information"
                  visible={showColorbarFractionDialog}
                  onHide={toggleColorbarFractionDialog}
                >
                  <div className="card">
                    <p>TODO</p>
                  </div>
                </Dialog>
              </div>

              <div className="mb-3">
                <label htmlFor="cbar_orientation" className="form-label">
                  Colorbar Orientation
                </label>
                <button
                  type="button"
                  onClick={toggleColorbarOrientationDialog}
                  aria-label="Toggle information dialog"
                  className="icon-button"
                >
                  <i className="pi pi-question-circle" />
                </button>

                <input
                  type="text"
                  className={`form-control ${
                    errors.cbar_orientation ? "is-invalid" : ""
                  }`}
                  name="cbar_orientation"
                  id="cbar_orientation"
                  value={formValues.cbar_orientation || ""}
                  onChange={handleStringInput}
                  // onBlur={(e) => handleChange(e, "dialog", true)}
                />
                {errors.cbar_orientation && (
                  <span className="error">{errors.cbar_orientation}</span>
                )}

                <Dialog
                  header="Colorbar Orientation Information"
                  visible={showColorbarOrientationDialog}
                  onHide={toggleColorbarOrientationDialog}
                >
                  <div className="card">
                    <p>TODO</p>
                  </div>
                </Dialog>
              </div>

              <div className="mb-3">
                <label htmlFor="aspect_ratio" className="form-label">
                  Aspect Ratio
                </label>
                <button
                  type="button"
                  onClick={toggleAspectRatioDialog}
                  aria-label="Toggle information dialog"
                  className="icon-button"
                >
                  <i className="pi pi-question-circle" />
                </button>

                <input
                  type="text"
                  className={`form-control ${
                    errors.aspect_ratio ? "is-invalid" : ""
                  }`}
                  name="aspect_ratio"
                  id="aspect_ratio"
                  value={formValues.aspect_ratio || ""}
                  onChange={handleStringInput}
                  // onBlur={(e) => handleChange(e, "dialog", true)}
                />
                {errors.aspect_ratio && (
                  <span className="error">{errors.aspect_ratio}</span>
                )}

                <Dialog
                  header="Aspect Ratop Information"
                  visible={showAspectRatioDialog}
                  onHide={toggleAspectRatioDialog}
                >
                  <div className="card">
                    <p>TODO</p>
                  </div>
                </Dialog>
              </div>
            </div>
            <div className="col-4 border p-3">
              <div className="mb-3">
                <label
                  htmlFor="elevation_tick_increment"
                  className="form-label"
                >
                  Elevation Tick Increment
                </label>
                <input
                  type="text"
                  className={`form-control ${
                    errors.elevation_tick_increment ? "is-invalid" : ""
                  }`}
                  name="elevation_tick_increment"
                  id="elevation_tick_increment"
                  value={formValues.elevation_tick_increment || ""}
                  onChange={handleStringInput}
                  // onBlur={(e) => handleChange(e, "dialog", true)}
                />
                {errors.elevation_tick_increment && (
                  <span className="error">
                    {errors.elevation_tick_increment}
                  </span>
                )}
              </div>

              <div className="mb-3">
                <label htmlFor="label_pad_size" className="form-label">
                  Label Pad Size
                </label>
                <input
                  type="text"
                  className={`form-control ${
                    errors.label_pad_size ? "is-invalid" : ""
                  }`}
                  name="label_pad_size"
                  id="label_pad_size"
                  value={formValues.label_pad_size || ""}
                  onChange={handleStringInput}
                  // onBlur={(e) => handleChange(e, "dialog", true)}
                />
                {errors.label_pad_size && (
                  <span className="error">{errors.label_pad_size}</span>
                )}
              </div>

              <div className="mb-3">
                <label htmlFor="cbar_pad_size" className="form-label">
                  Cbar Pad Size
                </label>
                <input
                  type="text"
                  className={`form-control ${
                    errors.cbar_pad_size ? "is-invalid" : ""
                  }`}
                  name="cbar_pad_size"
                  id="cbar_pad_size"
                  value={formValues.cbar_pad_size || ""}
                  onChange={handleStringInput}
                  // onBlur={(e) => handleChange(e, "dialog", true)}
                />
                {errors.cbar_pad_size && (
                  <span className="error">{errors.cbar_pad_size}</span>
                )}
              </div>

              <div className="form-check form-switch">
                <label
                  className="form-check-label"
                  htmlFor="invert_colorbar_axis"
                >
                  Invert Colorbar Axis
                </label>
                <input
                  type="checkbox"
                  className="form-check-input"
                  role="switch"
                  name="invert_colorbar_axis"
                  id="invert_colorbar_axis"
                  checked={formValues.invert_colorbar_axis}
                  onChange={handleBooleanInput}
                />
              </div>

              <div className="mb-3">
                <label htmlFor="aboveground_color" className="form-label">
                  Aboveground Color
                </label>
                <input
                  type="text"
                  className="form-control"
                  name="aboveground_color"
                  id="aboveground_color"
                  value={formValues.aboveground_color || ""}
                  onChange={handleStringInput}
                />
              </div>

              <div className="mb-3">
                <label
                  htmlFor="aboveground_border_color"
                  className="form-label"
                >
                  Aboveground Border Color
                </label>
                <input
                  type="text"
                  className="form-control"
                  name="aboveground_border_color"
                  id="aboveground_border_color"
                  value={formValues.aboveground_border_color || ""}
                  onChange={handleStringInput}
                />
              </div>
            </div>
            <div className="col-4 border p-3">
              <div className="mb-3">
                <div className="form-check form-switch">
                  <label className="form-check-label" htmlFor="shift_elevation">
                    Shift Elevation
                  </label>
                  <input
                    type="checkbox"
                    className="form-check-input"
                    role="switch"
                    name="shift_elevation"
                    id="shift_elevation"
                    checked={formValues.shift_elevation}
                    onChange={handleBooleanInput}
                  />
                </div>
              </div>

              <div className="mb-3">
                <div className="form-check form-switch">
                  <label
                    className="form-check-label"
                    htmlFor="display_as_depth"
                  >
                    Display As Depth
                  </label>
                  <input
                    type="checkbox"
                    className="form-check-input"
                    role="switch"
                    name="display_as_depth"
                    id="display_as_depth"
                    checked={formValues.display_as_depth}
                    onChange={handleBooleanInput}
                  />
                </div>
              </div>

              <div className="mb-3">
                <label htmlFor="cbar_ticks" className="form-label">
                  Cbar Ticks
                </label>
                <input
                  type="text"
                  className={`form-control ${
                    errors.cbar_ticks ? "is-invalid" : ""
                  }`}
                  name="cbar_ticks"
                  id="cbar_ticks"
                  value={formValues.cbar_ticks.join(", ") || ""} // Display array as comma-separated values
                  onChange={(e) => {
                    // Handle changes and update the cbar_ticks array
                    const value = e.target.value;
                    const newValues = value.split(",").map((val) => val.trim()); // Split by comma and trim each value
                    setFormValues((prev) => ({
                      ...prev,
                      cbar_ticks: newValues, // Store as an array
                    }));
                  }}
                  onBlur={validateCbarTicks} // Trigger validation onBlur
                  placeholder="Enter Cbar Ticks as a list of positive floats, separated by commas"
                />

                {errors.cbar_ticks && (
                  <span className="error">{errors.cbar_ticks}</span>
                )}
              </div>

              <div className="mb-3">
                <div className="form-check form-switch">
                  <label className="form-check-label" htmlFor="tick_right">
                    Right Tick
                  </label>
                  <input
                    type="checkbox"
                    className="form-check-input"
                    role="switch"
                    name="tick_right"
                    id="tick_right"
                    checked={formValues.tick_right}
                    onChange={handleBooleanInput}
                  />
                </div>
              </div>

              <div className="mb-3">
                <div className="form-check form-switch">
                  <label className="form-check-label" htmlFor="tick_left">
                    Left Tick
                  </label>
                  <input
                    type="checkbox"
                    className="form-check-input"
                    role="switch"
                    name="tick_left"
                    id="tick_left"
                    checked={formValues.tick_left}
                    onChange={handleBooleanInput}
                  />
                </div>
              </div>

              <div className="mb-3">
                <div className="form-check form-switch">
                  <label className="form-check-label" htmlFor="tick_top">
                    Top Tick
                  </label>
                  <input
                    type="checkbox"
                    className="form-check-input"
                    role="switch"
                    name="tick_top"
                    id="tick_top"
                    checked={formValues.tick_top}
                    onChange={handleBooleanInput}
                  />
                </div>
              </div>

              <div className="mb-3">
                <div className="form-check form-switch">
                  <label className="form-check-label" htmlFor="tick_bottom">
                    Bottom Tick
                  </label>
                  <input
                    type="checkbox"
                    className="form-check-input"
                    role="switch"
                    name="tick_bottom"
                    id="tick_bottom"
                    checked={formValues.tick_bottom}
                    onChange={handleBooleanInput}
                  />
                </div>
              </div>

              <div className="mb-3">
                <div className="form-check form-switch">
                  <label className="form-check-label" htmlFor="ticklabel_right">
                    Right Tick Label
                  </label>
                  <input
                    type="checkbox"
                    className="form-check-input"
                    role="switch"
                    name="ticklabel_right"
                    id="ticklabel_right"
                    checked={formValues.ticklabel_right}
                    onChange={handleBooleanInput}
                  />
                </div>
              </div>

              <div className="mb-3">
                <div className="form-check form-switch">
                  <label className="form-check-label" htmlFor="ticklabel_top">
                    Left Tick Label
                  </label>
                  <input
                    type="checkbox"
                    className="form-check-input"
                    role="switch"
                    name="ticklabel_left"
                    id="ticklabel_left"
                    checked={formValues.ticklabel_left}
                    onChange={handleBooleanInput}
                  />
                </div>
              </div>

              <div className="mb-3">
                <div className="form-check form-switch">
                  <label className="form-check-label" htmlFor="ticklabel_top">
                    Top Tick Label
                  </label>
                  <input
                    type="checkbox"
                    className="form-check-input"
                    role="switch"
                    name="ticklabel_top"
                    id="ticklabel_top"
                    checked={formValues.ticklabel_top}
                    onChange={handleBooleanInput}
                  />
                </div>
              </div>

              <div className="mb-3">
                <div className="form-check form-switch">
                  <label className="form-check-label" htmlFor="ticklabel_right">
                    Bottom Tick Label
                  </label>
                  <input
                    type="checkbox"
                    className="form-check-input"
                    role="switch"
                    name="ticklabel_bottom"
                    id="ticklabel_bottom"
                    checked={formValues.ticklabel_bottom}
                    onChange={handleBooleanInput}
                  />
                </div>
              </div>
              <div className="mb-3">
                <div className="form-check form-switch">
                  <label
                    className="form-check-label"
                    htmlFor="reverse_elevation"
                  >
                    Reverse Elevation
                  </label>
                  <input
                    type="checkbox"
                    className="form-check-input"
                    role="switch"
                    name="reverse_elevation"
                    id="reverse_elevation"
                    checked={formValues.reverse_elevation}
                    onChange={handleBooleanInput}
                  />
                </div>
              </div>

              <div className="mb-3">
                <div className="form-check form-switch">
                  <label className="form-check-label" htmlFor="reverse_data">
                    Reverse Data
                  </label>
                  <input
                    type="checkbox"
                    className="form-check-input"
                    role="switch"
                    name="reverse_data"
                    id="reverse_data"
                    checked={formValues.reverse_data}
                    onChange={handleBooleanInput}
                  />
                </div>
              </div>
            </div>
          </div>

          <div className="mb-3">
            <button type="button" onClick={handleAdvancedFiltersSave}>
              Save
            </button>
            <button type="button">Reset</button>
          </div>
        </form>
      </Dialog>
    </div>
  );
};

export default Quick2dSForm;
