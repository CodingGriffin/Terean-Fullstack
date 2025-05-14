import React, { createContext, useContext, ReactNode } from "react";
import useSWR from "swr";
import { CurrentUser } from "../types";
import { jwtDecode } from "jwt-decode";
import { backendUrl } from "../utils/utils.tsx"; 

interface AuthContextType {
  userData: CurrentUser | null;
  mutateUser: () => Promise<CurrentUser>;
  refreshToken: () => Promise<boolean>;
  logout: () => void;
}

// This is the initial value the user is set to.  It's important
// to note I'm using an auth_level of -1 (negative one) to indicate
// no user data has been attempted to be loaded from the system.
// Once the request to validate the user is complete this will be
// replaced with either a real user from the database or a Guest user (see next var)
const undefinedGuestUser: CurrentUser = {
  id: 0,
  username: '',
  disabled: false,
  // Very important to notice this is set to -1 (negative one)
  // this is how you know the authorization process has not completed
  // on a page refresh. (see ProtectedAdminRoute or ProtectedRoute) for how
  // to utilize this.
  auth_level: -1,
  email: '',
  full_name: 'Undefined Guest',
  expiration: null,
}

// This is the user data that will be assigned if a user
// does not have a valid token.  It has an id of 0 and
// an auth_level of 0 to indicate it is not a real user.
// You can use the id field to determine if someone is or
// isn't logged in. For instance the login/logout button checks
// id to determine which to show.
const guestUser: CurrentUser = {
  id: 0,
  username: '',
  disabled: false,
  auth_level: 0,
  email: '',
  full_name: 'Guest',
  expiration: null,
}

const defaultAuthContext: AuthContextType = {
  userData: null,
  mutateUser: async () => guestUser,
  refreshToken: async () => false,
  logout: async () => {},
};

const AuthContext = createContext<AuthContextType>(defaultAuthContext);

/**
 * Decodes a JWT token and returns the payload
 * @param {string} token - The JWT token to decode
 * @returns {object|null} The decoded token payload or null if invalid
 */
export function decodeToken(token: string) {
  try {
    return jwtDecode(token);
  } catch (error) {
    console.error('Error decoding token:', error);
    return null;
  }
}

/**
 * Checks if a token is expired
 * @param {string} token - The JWT token to check
 * @returns {boolean} True if token is expired or invalid, false otherwise
 */
export function isTokenExpired(token: string) {
  const decoded = decodeToken(token);
  if (!decoded || !decoded.exp) return true;
  
  const currentTime = Date.now() / 1000;
  return decoded.exp < currentTime;
}

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  async function refreshToken() {
    try {
      console.log("Renewing token...");
      const refresh_token = localStorage.getItem("refresh_token");

      const response = await fetch(`${backendUrl.replace(/\/+$/, '')}/refresh-token`, { 
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ token: refresh_token })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      localStorage.setItem("token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);

      return true;
    } catch (error) {
      console.error("Error renewing token:", error);
      return false;
    }
  }

  async function fetchUser(url: string) {
    const token = localStorage.getItem("token");

    if (!token) {
      return guestUser;
    }

    if (isTokenExpired(token)) {
      console.log("Token expired. Refreshing...");
      await refreshToken();
    }

    let response;
    try {
      console.log("Fetching user data...");
      response = await fetch(url, { 
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      })
      console.log(response);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const userData = response.json();

      if (userData) {
        return userData;
      }
    } catch (error) {
      console.error("Error fetching user data:", error);
      // Handle an expired token.
      // Try to renew it. If successful requery the user.
      if (response && response.status === 401) {
        const renewed = await refreshToken();
        if (renewed) {
          return fetchUser(url);
        }

        logout();
        window.location.href = "/";
      }

      if (response && response.status === 403) {
        logout();
        window.location.href = "/";
      }

      if (response && response.status === 404) {
        logout();
        window.location.href = "/";
      }

      console.error("Error fetching user data:", error);
    }

    return guestUser;
  }

  const {
    data: userData,
    // error: authErrorResp,
    mutate: mutateUser,
  } = useSWR(`${backendUrl.replace(/\/+$/, '')}/users/me`, fetchUser, { fallbackData: undefinedGuestUser });

  async function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("refresh_token");
    await mutateUser();
  }

  return (
    <AuthContext.Provider value={{ userData, mutateUser, refreshToken, logout }}>
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
