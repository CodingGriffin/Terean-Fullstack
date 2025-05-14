import React from "react";
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

  // Wait until the user has loaded and auth_level is not -1.
  // I'm using -1 to indicate the user data has not been looked up
  // at all.  Upon loading a page the user will either be populated
  // by their real user data (if they have a valid token), or will be
  // set to guest user info that has an auth_level of 0.
  //
  // So here we wait until the user data is not null and auth_level is not -1
  // to be sure that the user data has been loaded. If we didn't do this everyone
  // would be redirected to the 403 page if they refreshed the page.
  if (!userData || userData.auth_level === -1) {
    return (
      <div>Loading</div>
    )
  }

  if (userData.auth_level < minAuthLevel) {
    return <Navigate to="/403" />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
