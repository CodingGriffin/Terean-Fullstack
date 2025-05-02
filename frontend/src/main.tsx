import React from "react";
import { createRoot } from "react-dom/client";
import { InfoDialogProvider } from "./Contexts/InfoDialogContext.js";
import { SimpleFieldValidationProvider } from "./Components/SimpleValidationContext.js";
import { AuthProvider } from "./Contexts/authContext.js";
import App from "./App";
import "./App.scss";
import "./index.scss";
import "./styles.scss";
import "primeicons/primeicons.css";
import "primereact/resources/primereact.css";
import "primereact/resources/themes/bootstrap4-light-blue/theme.css";

import { PrimeReactProvider } from "primereact/api";
import { BrowserRouter } from "react-router-dom";

import { Provider } from "react-redux";
import { store } from "./store/index.js";

createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <Provider store={store}>
      <PrimeReactProvider>
        <BrowserRouter>
          <SimpleFieldValidationProvider>
            <InfoDialogProvider>
              <AuthProvider>
                <App />
              </AuthProvider>
            </InfoDialogProvider>
          </SimpleFieldValidationProvider>
        </BrowserRouter>
      </PrimeReactProvider>
    </Provider>
  </React.StrictMode>
);
