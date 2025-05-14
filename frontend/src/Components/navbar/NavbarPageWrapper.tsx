// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import React, { ReactNode } from "react";
import Navbar from "./Navbar";

interface NavbarPageWrapperProps {
  children: ReactNode;
}

export default function NavbarPageWrapper({
  children,
}: NavbarPageWrapperProps) {
  return (
    <>
      <Navbar />
      {children}
    </>
  );
}
