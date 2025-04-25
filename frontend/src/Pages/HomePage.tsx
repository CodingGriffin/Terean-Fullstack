import React from "react";
import Navbar from "../Components/navbar/Navbar";

export default function HomePage() {
  return (
    <>
      <Navbar />
      <div className="container-lg">
        <h1>Home</h1>
        <p>Welcome Text</p>
      </div>
    </>
  );
}
