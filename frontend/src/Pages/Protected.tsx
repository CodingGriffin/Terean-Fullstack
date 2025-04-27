// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import React, { useEffect, useState } from "react";
import { useAuth } from "../Contexts/authContext.tsx"; 
import { Navigate } from "react-router-dom";

function ProtectedPage() {
  const { userData } = useAuth();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (userData !== null) {
      setLoading(false);
    }
  }, [userData]);

  if (loading) {
    return (
      <div>
        <h2>Loading page...</h2>
      </div>
    );
  }

  if (!userData) {
    return <Navigate to="/login" />; 
  }

  return (
    <div>This is a protected page. Only visible to authenticated users.</div>
  );
}

export default ProtectedPage;
