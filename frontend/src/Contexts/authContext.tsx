import React, { createContext, useState, useContext, ReactNode, useEffect } from "react";
import { UserData } from "../types"; 
import { backendUrl } from "../utils/utils.tsx"; 

interface AuthContextType {
  userData: UserData | null;
  setUserData: React.Dispatch<React.SetStateAction<UserData | null>>;
  logout: () => void;
  loading: boolean; 
}

const defaultAuthContext: AuthContextType = {
  userData: null,
  setUserData: () => {},
  logout: () => {},
  loading: true, 
};

const AuthContext = createContext<AuthContextType>(defaultAuthContext);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [userData, setUserData] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true); 

  const logout = () => {
    setUserData(null);
    localStorage.removeItem("token");
  };

  useEffect(() => {
    const token = localStorage.getItem("token");
    const cleanUrl = `${backendUrl.replace(/\/+$/, '')}/verify-token/${token}`;

    if (token) {
      fetch(cleanUrl, { 
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
        .then(response => {
          if (response.ok) {
            return response.json();
          } else {
            throw new Error('Invalid token');
          }
        })
        .then(data => {
          setUserData(data); 
        })
        .catch(() => {
          logout(); 
        })
        .finally(() => {
          setLoading(false); 
        });
    } else {
      setLoading(false); 
    }
  }, []); 
  return (
    <AuthContext.Provider value={{ userData, setUserData, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
