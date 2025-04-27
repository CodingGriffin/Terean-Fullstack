// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import { useState } from "react";
import validateSingleField from "../utils/validateSingleField";

// Type for form values
interface FormValues {
  [key: string]: string | undefined;
}

// Type for errors
interface FormErrors {
  [key: string]: string;
}

// Type for FieldId (your existing FieldId union type)
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

// Type guard to check if a string is a valid FieldId
const isFieldId = (name: string): name is FieldId => {
  const validFieldIds: FieldId[] = [
    "max_depth", "smoothing", "vel_min", "vel_max", "min_depth", "x_max", 
    "contour_width", "elevation_tick_size", "cbar_fraction", "aspect_ratio", 
    "label_pad_size", "elevation_tick_increment", "cbar_pad_size"
  ];
  return validFieldIds.includes(name as FieldId);
};

export const useFormValidation = () => {
  const [formValues, setFormValues] = useState<FormValues>({});
  const [errors, setErrors] = useState<FormErrors>({});

  const handleStringInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;

    // Ensure `name` is a valid FieldId before proceeding
    if (isFieldId(name)) {
      // Validate the field and set the error (if any)
      const fieldErrors = validateSingleField(name, value);

      // Update form values and errors state
      setFormValues((prev) => ({
        ...prev,
        [name]: value,
      }));

      setErrors((prev) => ({
        ...prev,
        [name]: fieldErrors[name] || "", // Clear error if validation passes
      }));
    }
  };

  return { formValues, errors, handleStringInput };
};
