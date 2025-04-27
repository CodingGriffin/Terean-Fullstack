// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import React from "react";
import Navbar from "../../Components/navbar/Navbar";
import AdminDashboard from "../../Components/admin/AdminDashboard";

const AdminDashboardPage = () => {
  return ( 
    <>
      <Navbar />
      <div className="container mt-4">
        <div className="row">
          <div className="col-12 text-center mb-4">
            <h1>Admin Dashboard</h1>
            <p className="lead">Welcome to the admin dashboard!</p>
          </div>
        </div>
        <div className="row">
          <div className="col-12">
            <AdminDashboard />
          </div>
        </div>
    </div>
    </> 
  );
};

export default AdminDashboardPage;