// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import React, { createContext, useContext, useState } from "react";

const SimpleFieldValidationContext: React.Context<any> = createContext(null);

export const SimpleFieldValidationProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const [errors, setErrors] = useState({});

  return (
    <SimpleFieldValidationContext.Provider value={{ errors, setErrors }}>
      {children}
    </SimpleFieldValidationContext.Provider>
  );
};

export const useSimpleFieldValidation = () => {
  const context = useContext(SimpleFieldValidationContext);

  if (!context) {
    throw new Error(
      "useSimpleFieldValidation must be used within a a SimpleFieldValidationProvider"
    );
  }

  return context;
};
