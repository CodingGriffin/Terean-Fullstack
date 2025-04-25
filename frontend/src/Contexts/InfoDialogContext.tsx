//Comments featured here are to help me solidify my understanding of useContext so please dont delete them yet.
import React, { createContext, useContext, useState } from "react";

interface DialogsState {
  [key: string]: boolean;
}
interface DialogContextType {
  dialogs: DialogsState;
  openDialog: (name: string) => void;
  closeDialog: (name: string) => void;
}

const DialogContext = createContext<DialogContextType | null>(null);

//children represents ANY component inside the provider
export const InfoDialogProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  //can update with additional filters info dialogs too later
  const [dialogs, setDialogs] = useState<DialogsState>({});

  const openDialog = (name: string) => {
    setDialogs((prev) => ({ ...prev, [name]: true })); //set dialog to open, while keeping previous state of other dialogs
  };

  const closeDialog = (name: string) => {
    setDialogs((prev) => ({ ...prev, [name]: false })); //set dialog to close, while keeping previous state of other dialogs
  };

  //children are essentially child components of the provider and inherent dialogs, openDialog, closeDialog.
  return (
    <DialogContext.Provider value={{ dialogs, openDialog, closeDialog }}>
      {children}
    </DialogContext.Provider>
  );
};

export const useDialog = () => {
  const context = useContext(DialogContext);
  if (!context) {
    throw new Error("useDialog must be used within an InfoDialogProvider");
  }
  return context;
};
