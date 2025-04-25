import React, { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../../Contexts/authContext.tsx";

interface ProtectedRouteProps {
  children: React.ReactNode;
  minAuthLevel: number;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  minAuthLevel,
}) => {
  const { userData } = useAuth();
  const [shouldRedirect, setShouldRedirect] = useState(false);

  useEffect(() => {
    if (!userData) {
      setShouldRedirect(true);
    }
  }, [userData]);

  if (shouldRedirect) {
    return <Navigate to="/403" />;
  }

  if (!userData || userData.auth_level < minAuthLevel) {
    return <Navigate to="/403" />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
