type FieldId =
  | "max_depth"
  | "smoothing"
  | "vel_min"
  | "vel_max"
  | "min_depth"
  | "x_max"
  | "contour_width"
  | "elevation_tick_size"
  | "cbar_fraction"
  | "aspect_ratio"
  | "label_pad_size"
  | "elevation_tick_increment"
  | "cbar_pad_size";

interface ValidationErrors {
  [key: string]: string;
}

const validateSingleField = (
  id: FieldId,
  value: string | undefined
): ValidationErrors => {
  const newErrors: ValidationErrors = {};

  if (value === "" || value === null || value === undefined) {
    return newErrors; // No errors if the field is empty
  }

  // Convert value to a number
  const numericValue = parseFloat(value);

  // Validate if value is a valid float
  const isFloat = (val: string): boolean => {
    val = val.replace(/,/g, ""); // Remove commas for numeric input like "1,000"
    const floatRegex = /^\d+(\.\d+)?$/; // Validates positive float
    return floatRegex.test(val) && parseFloat(val) > 0;
  };

  // Validate if value is a positive integer or zero
  const isPositiveIntegerOrZero = (val: string): boolean => {
    const number = parseFloat(val);
    return !isNaN(number) && Number.isInteger(number) && number >= 0;
  };

  // Validation based on field ID
  switch (id) {
    case "max_depth":
      if (!isFloat(value)) {
        newErrors.max_depth = "Max Depth must be a positive float.";
      }
      break;

    case "smoothing":
      if (value !== "" && !isPositiveIntegerOrZero(numericValue.toString())) {
        newErrors.smoothing =
          "Smoothing must be an integer greater than or equal to 0.";
      }
      break;

    case "vel_min":
      if (!isFloat(value)) {
        newErrors.vel_min = "vMin must be a positive float.";
      }
      break;

    case "vel_max":
      if (!isFloat(value)) {
        newErrors.vel_max = "vMax must be a positive float.";
      }
      break;

    case "min_depth":
      if (!isFloat(value)) {
        newErrors.min_depth = "Min Depth must be a positive float.";
      }
      break;

    case "x_max":
      if (!isFloat(value)) {
        newErrors.x_max = "X-Max must be a positive float.";
      }
      break;

    case "contour_width":
      if (!isFloat(value)) {
        newErrors.contour_width = "Contour Width must be a positive float.";
      }
      break;

    case "elevation_tick_size":
      if (!isFloat(value)) {
        newErrors.elevation_tick_size =
          "Elevation Tick Size must be a positive float.";
      }
      break;

    case "cbar_fraction":
      if (!isFloat(value)) {
        newErrors.cbar_fraction = "Colorbar Fraction must be a positive float.";
      }
      break;

    case "aspect_ratio":
      if (!isFloat(value)) {
        newErrors.aspect_ratio = "Aspect Ratio must be a positive float.";
      }
      break;

    case "label_pad_size":
      if (!isFloat(value)) {
        newErrors.label_pad_size = "Label Pad Size must be a positive float.";
      }
      break;

    case "elevation_tick_increment":
      if (!isFloat(value)) {
        newErrors.elevation_tick_increment =
          "Elevation Increment must be a positive float.";
      }
      break;

    case "cbar_pad_size":
      if (!isFloat(value)) {
        newErrors.cbar_pad_size = "Colorbar Pad Size must be a positive float.";
      }
      break;

    default:
      break;
  }

  return newErrors;
};

export default validateSingleField;
