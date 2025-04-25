import React from "react";
import PasswordChangeForm from "../Components/auth/ChangePasswordForm.tsx";
import Navbar from "../Components/navbar/Navbar.tsx";

export default function PasswordChangePage() {
  return (
    <>
      <Navbar />
      <PasswordChangeForm />
    </>
  );
}
