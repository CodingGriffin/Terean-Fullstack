// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../Contexts/authContext.tsx";
import { backendUrl } from "../utils/utils.tsx";

const ProfileCard = () => {
  const { userData, setUserData } = useAuth();
  const [fullName, setFullName] = useState(userData?.full_name || "");
  const [email, setEmail] = useState(userData?.email || "");
  const [message, setMessage] = useState("");
  const [isEditing, setIsEditing] = useState(false);

  if (!userData) {
    return <p>You are not logged in.</p>;
  }

  const handleUpdate = async () => {
    const cleanUrl = `${backendUrl.replace(/\/+$/, "")}/admin/users/${
      userData.username
    }`;

    try {
      const res = await fetch(cleanUrl, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          full_name: fullName,
          email: email,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || "Failed to update user");
      }

      const updatedUser = await res.json();
      setUserData(updatedUser);
      setMessage("Profile updated successfully!");
      setIsEditing(false);
    } catch (err) {
      setMessage(err.message || "Something went wrong.");
    }
  };

  const handleDiscard = () => {
    setFullName(userData.full_name);
    setEmail(userData.email);
    setIsEditing(false);
    setMessage("");
  };

  return (
    <div className="row justify-content-center pt-5">
      <div className="col-12 col-md-8 col-lg-6">
        <div className="card shadow-lg rounded-3 position-relative">
          <div className="card-body">
            <div className="d-flex align-items-center mb-4 w-100">
              <h1 className="card-title mb-0 mx-auto">{userData.username}</h1>
              {!isEditing && (
                <button
                  className="btn btn-outline-secondary btn-sm"
                  onClick={() => setIsEditing(true)}
                >
                  Edit
                </button>
              )}
            </div>

            <div className="mb-4">
              {isEditing ? (
                <>
                  <label className="form-label">Full Name</label>
                  <input
                    type="text"
                    className="form-control mb-3"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                  />
                  <label className="form-label">Email</label>
                  <input
                    type="email"
                    className="form-control"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </>
              ) : (
                <ul className="list-group">
                  <li className="list-group-item">
                    <strong>Full Name:</strong> {userData.full_name}
                  </li>
                  <li className="list-group-item">
                    <strong>Email:</strong> {userData.email}
                  </li>
                </ul>
              )}
            </div>

            {message && <div className="alert alert-info mt-3">{message}</div>}

            <div className="d-flex justify-content-center mt-4">
              {isEditing ? (
                <>
                  <button
                    className="btn btn-success me-2"
                    onClick={handleUpdate}
                  >
                    Save Changes
                  </button>
                  <button className="btn btn-secondary" onClick={handleDiscard}>
                    Discard Changes
                  </button>
                </>
              ) : (
                <Link to="/password_change" className="btn btn-primary btn-sm">
                  Change Password?
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileCard;
