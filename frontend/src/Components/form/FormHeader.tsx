//formHeader to use when doing some more tidying of forms

import React from 'react';
import { useDialog } from '../../Contexts/InfoDialogContext';

interface FormHeaderProps {
    formTitle: string;
}

const FormHeader: React.FC<FormHeaderProps> = ({ formTitle }) => {
    // Access the openDialog function from context
    const { openDialog } = useDialog();
  
    return (
      <div className="title-div container-fluid">
        <div className="row align-items-baseline">
          <div className="col"></div>
          <div className="col">
            <h2 className="text-light fs-1">{formTitle}</h2>
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
    );
  };

  export default FormHeader