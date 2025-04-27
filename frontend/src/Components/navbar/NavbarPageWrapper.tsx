// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import React, { ReactNode } from "react";
import { useAuth } from "../../Contexts/authContext";
import Navbar from "./Navbar";
import { useNavigate } from "react-router-dom";

interface NavbarPageWrapperProps {
  redirectOnFail: boolean;
  children: ReactNode;
}

export default function NavbarPageWrapper({
  redirectOnFail,
  children,
}: NavbarPageWrapperProps) {
  const { userData } = useAuth();
  const navigate = useNavigate();
  if (userData === null) {
    if (redirectOnFail) {
      navigate("/login");
    }
  }

  return (
    <>
      <Navbar />
      {children}
    </>
  );
}
