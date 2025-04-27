// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import React from "react";
import Navbar from "../Components/navbar/Navbar";
import LoginForm from "../Components/auth/LoginForm";

export default function Login() {
  return (
    <>
      <Navbar />
      <LoginForm />
    </>
  )
}