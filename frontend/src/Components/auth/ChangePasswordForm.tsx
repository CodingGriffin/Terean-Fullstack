import React, { useState } from "react";
import { useAuth } from "../../Contexts/authContext";
import { backendUrl } from "../../utils/utils";

export default function PasswordChangeForm() {
  const { userData } = useAuth(); // Access user data from AuthContext
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const token = localStorage.getItem("token");

  // Check if user is logged in using the context
  if (!userData) {
    return <div>Please log in to reset your password.</div>;
  }

  const handlePasswordReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage(""); // Clear previous error messages
    setSuccessMessage(""); // Clear previous success messages

    try {
      const response = await fetch(
        `${backendUrl.replace(/\/$/, "")}/change-password`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            current_password: currentPassword,
            new_password: newPassword,
          }),
        }
      );

      if (response.ok) {
        setSuccessMessage("Your password has been successfully reset.");
      } else {
        const data = await response.json();
        setErrorMessage(
          data.message || "Error resetting password. Please try again."
        );
      }
    } catch (err) {
      setErrorMessage("Something went wrong. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="row justify-content-center pt-5">
      <div className="col-12 col-md-6 col-lg-5">
        <div className="card shadow-sm rounded-3">
          <div className="card-body">
            <h2 className="card-title text-center">Change your password</h2>

            <form onSubmit={handlePasswordReset}>
              <div className="mb-3">
                <label htmlFor="currentPassword" className="form-label">
                  Current Password
                </label>
                <input
                  type="password"
                  id="oldPassword"
                  className="form-control"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  required
                />
              </div>

              <div className="mb-3">
                <label htmlFor="newPassword" className="form-label">
                  New Password
                </label>
                <input
                  type="password"
                  id="newPassword"
                  className="form-control"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                />
              </div>

              {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}
              {successMessage && (
                <p style={{ color: "green" }}>{successMessage}</p>
              )}

              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading}
              >
                {loading ? "Resetting..." : "Reset Password"}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
