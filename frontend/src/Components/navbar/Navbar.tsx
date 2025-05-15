// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import React from "react";
import ProfileIcon from "../Icons/ProfileIcon";
import { Link, useNavigate } from "react-router-dom";
import NavbarItem from "./NavbarItem";
import { useAuth } from "../../Contexts/authContext";

export default function Navbar() {
  const { userData, logout } = useAuth();
  const navigate = useNavigate();

  const hasProfileAccess = userData && userData.auth_level >= 1; // Can change later to string roles if needed

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <nav className="navbar navbar px-3 py-2">
      <button
        className="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarSupportedContent"
        aria-controls="navbarSupportedContent"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span className="navbar-toggler-icon"></span>
      </button>

      <Link className="navbar-brand mx-auto" to="/">
        Ter<span className="eStyle">e&#772;</span>an&trade;
      </Link>

      <div className="d-flex align-items-center">
        {userData && userData.id ? (
          <>
            <Link
              to={hasProfileAccess ? "/profile" : "#"}
              className="nav-link"
              style={{
                opacity: hasProfileAccess ? 1 : 0.5,
                cursor: hasProfileAccess ? "pointer" : "not-allowed",
              }}
            >
              <ProfileIcon />
            </Link>

            <button
              className="btn btn-outline-danger ms-2"
              onClick={handleLogout}
            >
              Logout
            </button>
          </>
        ) : (
          <Link to="/login" className="btn btn-outline-primary">
            Login
          </Link>
        )}
      </div>

      <div className="collapse navbar-collapse" id="navbarSupportedContent">
        <ul className="navbar-nav col-6 align-items-start">
          {/* Public home link, always accessible */}
          <NavbarItem
            url={"/"}
            name={"Home"}
            authRequired={0}
            userData={userData}
          />

          {/* Quick 2dS link, accessible if user has auth level 1 or higher */}
          <NavbarItem
            url={"/Quick2dS"}
            name={"Quick 2dS"}
            authRequired={1}
            userData={userData}
          />

          {/* Quick 2dP link, accessible if user has auth level 2 or higher */}
          <NavbarItem
            url={"/Quick2dP"}
            name={"Quick 2dP"}
            authRequired={2}
            userData={userData}
          />

          {/* Admin Dashboard link, accessible to admin users with auth level of 3 or higher */}
          <NavbarItem
            url={"/admin"}
            name={"Admin"}
            authRequired={3}
            userData={userData}
          />
          <NavbarItem
            url={"/projects/1/picks"}
            name={"Picks"}
            authRequired={2}
            userData={userData}
          />
          <NavbarItem
            url={"/projects/1/disper"}
            name={"Disper"}
            authRequired={2}
            userData={userData}
          />
        </ul>
      </div>
    </nav>
  );
}
