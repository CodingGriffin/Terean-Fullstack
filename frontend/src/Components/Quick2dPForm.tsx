// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import React, { useState } from "react";
import { Dialog } from "primereact/dialog";
import { Button } from "primereact/button";
import axios from "axios";
import { ProgressSpinner } from "primereact/progressspinner";
import { useDialog } from "../Contexts/InfoDialogContext.tsx";
import { useSimpleFieldValidation } from "./SimpleValidationContext.js";
import validateSingleField from "../utils/validateSingleField.tsx";
import { backendUrl } from "../utils/utils.tsx";
import { State2dP } from "../types";

const Quick2dPForm = () => {
  const { dialogs, openDialog, closeDialog } = useDialog();
  const { errors, setErrors } = useSimpleFieldValidation();
  const [isFormSubmitting, setIsFormSubmitting] = useState(false);
  const [imageSrc, setImageSrc] = useState(null); //state to hold response logo
  const [travelTimeFile, setTravelTimeFile] = useState<File | null>(null);
  const [geoCtModelFile, setGeoCtModelFile] = useState<File | null>(null);
  const [formValues, setFormValues] = useState<State2dP>({
    title: "VsSurf ReMi 2dP™ - ",
    min_depth: "",
    max_depth: "",
    vel_min: "",
    vel_max: "",
    smoothing: "10",
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
      rawInput: "",
    },
    invert_colorbar_axis: true,
    enable_colorbar: true,
    shift_elevation: true,
    display_as_depth: false,
    cbar_ticks: [],
    reverse_elevation: false,
    reverse_data: false,
    unit_override: "feet",
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
  });

  const handleGeoCTFileUpload = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    if (e.target.files == null || e.target.files.length === 0) {
      console.log("Error: No file present.");
    } else if (e.target.files.length > 1) {
      console.log("Error: Too many files present. There should only be one!");
    } else {
      const file = e.target.files[0];
      setGeoCtModelFile(file);
    }
  };

  const handleExcelUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files == null || e.target.files.length === 0) {
      console.log("Error: No file present.");
    } else if (e.target.files.length > 1) {
      console.log("Error: Too many files present. There should only be one!");
    } else {
      const file = e.target.files[0];
      setTravelTimeFile(file);
    }
  };

  const handleContoursInput = (value: string) => {
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
      setErrors((prev: any) => ({
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
      setErrors((prev: Object) => ({
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
        setErrors((prev: Object) => ({
          ...prev,
          contours:
            "Invalid input. Use 'none', an integer, or a comma-separated list of positive floats.",
        }));
      } else {
        setErrors((prev: Object) => ({
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
      setErrors((prev: Object) => ({
        ...prev,
        cbar_ticks: "Cbar Ticks must be a list of positive floats.",
      }));
    } else {
      setErrors((prev: Object) => ({
        ...prev,
        cbar_ticks: "", // Clear any errors if valid
      }));
    }
  };

  const handleStringInput = (e) => {
    const { name, value } = e.target;

    setFormValues((prev) => ({
      ...prev,
      [name]: value,
    }));

    const fieldErrors = validateSingleField(name, value);

    setErrors((prev: Object) => ({
      ...prev,
      [name]: fieldErrors[name] || "", // Clear error if validation passes
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

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    const token = localStorage.getItem("token");
    setIsFormSubmitting(true);

    if (geoCtModelFile == null) {
      setErrors((prev) => ({
        ...prev,
        geoct_files: "Must submit a GeoCT Model File",
      }));
    } else {
      setErrors((prev) => ({ ...prev, geoct_files: "" })); //clear out errors for geoct files
    }

    console.log("Form Files before submission:", geoCtModelFile);
    console.log(formValues);
    const config = {
      headers: {
        Accept: "application/json",
        "Content-Type": "multipart/form-data",
        Authorization: `Bearer ${token}`,
      },
      responseType: "arraybuffer",
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

    if (geoCtModelFile != null) {
      formData.append("geoct_model_file", geoCtModelFile);
    }

    if (travelTimeFile !== null && travelTimeFile !== undefined) {
      formData.append("travel_time_file", travelTimeFile);
    }

    try {
      console.log(formData);
      axios
        .post(`${backendUrl}process2dP`, formData, config)
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
      {/* Header Section */}
      <div className="title-div px-4 pt-4 pb-2">
        <div className="row align-items-center">
          <div className="col"></div>
          <div className="col text-center">
            <h2 className="text-light fs-1"> Quick 2dP Form</h2>
          </div>
          <div className="col text-end">
            <button
              className="advancedfilters-button border border-1 border-white dropdown text-light"
              type="button"
              onClick={() => openDialog("advancedfilters")}
            >
              Advanced Filters <i className="pi pi-arrow-down"></i>
            </button>
          </div>
        </div>
      </div>

      {/* form content */}
      <form className="px-4 pb-4" onSubmit={handleFormSubmit}>
        <div className="container p-4">
          {/* title */}
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
                      onClick={() => openDialog("title")}
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
                      visible={!!dialogs.title}
                      onHide={() => closeDialog("title")}
                    >
                      <div className="card">
                        <p>The title is displayed above the plot</p>
                      </div>
                    </Dialog>
                  </div>
                </div>
              </div>
              {/* geomodel and elevation section */}
              <div className="container">
                <div className="row mb-3 bg-white border border-1">
                  <div className="col-6 d-flex flex-column align-items-center">
                    <h4 className="mb-0 text-center">GeoCT Model</h4>

                    {/* Need to add in custom label, input, and span to get it dynamically updating */}
                    <div className="custom-file-wrapper d-flex flex-column align-items-center">
                      <span className="mt-1 text-secondary">
                        {geoCtModelFile != null ? (
                          `${geoCtModelFile.name} selected`
                        ) : (
                          <>
                            Please select a file{" "}
                            <span className="text-danger">*</span>
                          </>
                        )}
                      </span>

                      <label
                        htmlFor="geoct-files"
                        className="btn btn-primary w-auto ms-2 mb-2"
                        style={{ cursor: "pointer" }}
                      >
                        {geoCtModelFile != null ? "Change File" : "Select File"}
                      </label>

                      <input
                        type="file"
                        className={`form-control-file w-75 mt-2 ${
                          errors.geoct_files ? "is-invalid" : ""
                        }`}
                        name="geoct_files"
                        id="geoct-files"
                        accept=".mdl"
                        onChange={handleGeoCTFileUpload}
                        style={{ display: "none" }} //need to hide default file input button to do required styling
                      />

                      {errors.geoct_files && (
                        <span className="text-danger">
                          {errors.geoct_files}
                        </span>
                      )}
                    </div>
                  </div>
                  {/* NEED TO ADD VERTICAL DIVIDER HERE or BORDER_RIGHT AND BORDER_LEFT */}

                  <div className="col-6 d-flex flex-column align-items-center">
                    <h4 className="mb-0 text-center">TT File</h4>

                    <div className="custom-file-wrapper d-flex flex-column align-items-center">
                      <span className="mt-1 text-secondary">
                        {travelTimeFile !== null && travelTimeFile !== undefined
                          ? travelTimeFile.name
                          : "Click below to select a TT file."}
                      </span>

                      <div className="custom-file-wrapper d-flex flex-row align-items-center gap-2">
                        <label
                          htmlFor="traveltime-upload"
                          className="btn btn-primary w-auto mb-0"
                          style={{ cursor: "pointer" }}
                        >
                          {travelTimeFile !== null &&
                          travelTimeFile !== undefined
                            ? "Change"
                            : "Select File"}
                        </label>
                        <input
                          type="file"
                          className={`form-control-file w-75 mt-2`}
                          name="excel_file_input"
                          id="traveltime-upload"
                          accept=".tt"
                          onChange={handleExcelUpload}
                          style={{ display: "none" }} //need to hide default file input button to do required styling
                        />
                        {travelTimeFile !== null &&
                        travelTimeFile !== undefined ? (
                          <Button
                            type="button"
                            className="btn btn-danger"
                            onClick={() => setTravelTimeFile(null)}
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

          {/* Max Depth, vMin, Smoothing, vMax Section */}
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
                      onClick={() => openDialog("maxdepth")}
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
                      placeholder="0.00"
                    />
                    {errors.max_depth && (
                      <span className="error">{errors.max_depth}</span>
                    )}

                    <Dialog
                      header="Max Depth Information"
                      visible={!!dialogs.maxdepth}
                      onHide={() => closeDialog("maxdepth")}
                    >
                      <div className="card">
                        <p>Max depth to plot to.</p>
                      </div>
                    </Dialog>
                  </div>

                  <div className="mb-3">
                    <label htmlFor="smoothing" className="form-label">
                      Smoothing
                    </label>
                    <button
                      type="button"
                      onClick={() => openDialog("smoothing")}
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
                      placeholder="1"
                    />
                    {errors.smoothing && (
                      <span className="error">{errors.smoothing}</span>
                    )}

                    <Dialog
                      header="Smoothing Information"
                      visible={!!dialogs.smoothing}
                      onHide={() => closeDialog("smoothing")}
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
                      onClick={() => openDialog("vmin")}
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
                      placeholder="0.00"
                    />
                    {errors.vel_min && (
                      <span className="error">{errors.vel_min}</span>
                    )}

                    <Dialog
                      header="Minimum Velocity Information"
                      visible={!!dialogs.vmin}
                      onHide={() => closeDialog("vmin")}
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
                      onClick={() => openDialog("vmax")}
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
                      placeholder="0.00"
                    />
                    {errors.vel_max && (
                      <span className="error">{errors.vel_max}</span>
                    )}

                    <Dialog
                      header="Maximum Velocity Information"
                      visible={!!dialogs.vmax}
                      onHide={() => closeDialog("vmax")}
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
          {/* Contours Section */}
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
                      onClick={() => openDialog("contours")}
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
              </div>
            </div>

            <Dialog
              header={contourHeader}
              visible={!!dialogs.contours}
              onHide={() => closeDialog("contours")}
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
        <div className="container col-3 pt-4">
          <button
            className="btn btn-primary w-100 px-5 py-3 fw-bold"
            type="submit"
          >
            Submit
          </button> 
        </div>
        <div className="row align-items-center justify-content-center">
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
        visible={!!dialogs.advancedfilters}
        onHide={() => closeDialog("advancedfilters")}
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
                    onClick={() => openDialog("ymin")}
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
                  />
                  {errors.min_depth && (
                    <span className="error">{errors.min_depth}</span>
                  )}

                  <Dialog
                    header="Ymin Information"
                    visible={!!dialogs.ymin}
                    onHide={() => closeDialog("ymin")}
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
                    <option value="feet">Feet</option>
                    <option value="meters">Meters</option>
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
                      onClick={() => openDialog("colorbars")}
                      aria-label="Toggle information dialog"
                      className="icon-button"
                    >
                      <i className="pi pi-question-circle" />
                    </button>
                  </div>

                  <Dialog
                    header="Enable Colorbar Information"
                    visible={!!dialogs.colorbars}
                    onHide={() => closeDialog("colorbars")}
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
                />
                {errors.contour_width && (
                  <span className="error">{errors.contour_width}</span>
                )}
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
            <button
              type="button"
              onClick={() => closeDialog("advancedfilters")}
            >
              Save
            </button>
            <button type="button">Reset</button>
          </div>
        </form>
      </Dialog>
    </div>
  );
};

export default Quick2dPForm;
