// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import React from "react";
import { Link } from "react-router-dom";
import { UserData } from "../../types";

interface NavbarItemProps {
  url: string;
  name: string;
  authRequired: number;
  userData: UserData | null;
}

const NavbarItem: React.FC<NavbarItemProps> = ({
  url,
  name,
  authRequired,
  userData,
}) => {
  
  if (name === "Home" || (userData && userData.auth_level >= authRequired)) {
    return (
      <li className="nav-item">
        <Link to={url} className="nav-link">
          {name}
        </Link>
      </li>
    );
  }

  return null; 
};

export default NavbarItem;
