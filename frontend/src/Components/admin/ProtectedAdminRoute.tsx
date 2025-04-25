import React, { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../../Contexts/authContext";

interface ProtectedAdminRouteProps {
  children: React.ReactNode;
}

const ProtectedAdminRoute = ({ children }: ProtectedAdminRouteProps) => {
  const { userData } = useAuth();
  const [shouldRedirect, setShouldRedirect] = useState(false);

  useEffect(() => {
    if (userData === null) {
    
      setShouldRedirect(true);
    }
  }, [userData]);

  if (shouldRedirect || userData === null) {
    return <Navigate to="/403" />;
  }

  if (userData.auth_level < 3) {
    return <Navigate to="/403" />;
  }

  return <>{children}</>;
};

export default ProtectedAdminRoute;
