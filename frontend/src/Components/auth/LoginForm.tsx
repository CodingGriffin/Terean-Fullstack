import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { backendUrl } from "../../utils/utils";
import { useAuth } from "../../Contexts/authContext";

const LoginForm = () => {
  const { mutateUser } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const validateForm = () => {
    if (!username || !password) {
      setError("Username and password are required");
      return false;
    }
    setError("");
    return true;
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!validateForm()) return;
    setLoading(true);

    const formDetails = new URLSearchParams();
    formDetails.append("username", username);
    formDetails.append("password", password);

    try {
      const response = await fetch(`${backendUrl}token`, {
        mode: "cors",
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formDetails,
      });

      setLoading(false);

      if (response.ok) {
        const data = await response.json();

        const token = data.access_token;
        localStorage.setItem("token", token);

        const refresh_token = data.refresh_token;
        localStorage.setItem("refresh_token", refresh_token);

        await mutateUser();
        navigate("/");
      } else {
        const errorData = await response.json();
        setError(errorData.detail || "Authentication failed!");
      }
    } catch (error) {
      setLoading(false);
      setError("An error occurred. Please try again later.");
    }
  };

  return (
    <div className="row justify-content-center pt-5">
      <div className="col-12 col-md-6 col-lg-5">
        <div className="card shadow-sm rounded-3">
          <div className="card-body">
            <h2 className="card-title text-center mb-4">Login</h2>
            <p className="text-center text-muted mb-4">
              Please enter your credentials to access your account
            </p>

            <form onSubmit={handleSubmit}>
              <div className="mb-3">
                <label htmlFor="username" className="form-label">
                  Username:
                </label>
                <input
                  type="text"
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="form-control"
                />
              </div>
              <div className="mb-3">
                <label htmlFor="password" className="form-label">
                  Password:
                </label>
                <input
                  type="password"
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="form-control"
                />
              </div>
              <div className="row justify-content-center mt-4">
                <div className="col-12 col-md-6 col-lg-4">
                  <button
                    type="submit"
                    disabled={loading}
                    className="btn btn-primary w-100"
                  >
                    {loading ? "Logging in..." : "Login"}
                  </button>
                </div>
              </div>

              <div className="d-flex justify-content-center mt-3">
                <Link to="/forgot_password" className="btn btn-link">
                  Forgot your password?
                </Link>
              </div>

              {error && <p className="text-danger mt-3">{error}</p>}
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;
