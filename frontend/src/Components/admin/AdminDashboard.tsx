import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../Contexts/authContext";
import { backendUrl } from "../../utils/utils";
import { AdminUser } from "../../types";

export default function AdminDashboard() {
  const { userData } = useAuth();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUsers = async () => {
      if (!userData || userData.auth_level < 3) {
        navigate("/login");
        return;
      }

      const token = localStorage.getItem("token");
      if (!token) {
        console.log("No token found");
        return;
      }

      const cleanUrl = `${backendUrl.replace(/\/+$/, "")}/admin/users`;

      const response = await fetch(cleanUrl, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUsers(data);
      } else {
        console.error("Failed to fetch users");
      }
    };

    fetchUsers();
  }, [navigate, userData]);

  const handleToggleUserDisabled = async (
    username: string,
    currentDisabled: boolean
  ) => {
    const token = localStorage.getItem("token");
    if (!token) return;

    const cleanUrl = `${backendUrl.replace(
      /\/+$/,
      ""
    )}/admin/disable_user/${username}`;
    const response = await fetch(cleanUrl, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ disabled: !currentDisabled }),
    });

    if (response.ok) {
      setUsers((prevUsers) =>
        prevUsers.map((user) =>
          user.username === username
            ? { ...user, disabled: !currentDisabled }
            : user
        )
      );
    } else {
      console.error("Failed to update user");
    }
  };

  const activeUsers = users.filter((user) => !user.disabled);
  const disabledUsers = users.filter((user) => user.disabled);

  const renderUserRow = (user: AdminUser) => (
    <tr key={user.username} className={user.disabled ? "table-secondary" : ""}>
      <td>{user.username}</td>
      <td>{user.email}</td>
      <td>{user.full_name}</td>
      <td>{user.auth_level}</td>
      <td>
        <button onClick={() => navigate(`/admin/users/${user.username}`)}>
          Update
        </button>
        <button
          onClick={() => handleToggleUserDisabled(user.username, user.disabled)}
        >
          {user.disabled ? "Reactivate" : "Deactivate"}
        </button>
      </td>
    </tr>
  );

  return (
    <div>
      <h2>Admin Dashboard</h2>
      <button onClick={() => navigate("/admin/register_user")}>
        Create New User
      </button>

      {activeUsers.length > 0 && (
        <>
          <h3 style={{ marginTop: "1.5rem" }}>Active Users</h3>
          <table className="table table-hover table-bordered border-primary">
            <thead>
              <tr>
                <th scope="col">Username</th>
                <th scope="col">Email</th>
                <th scope="col">Full Name</th>
                <th scope="col">Auth Level</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>{activeUsers.map(renderUserRow)}</tbody>
          </table>
        </>
      )}

      {disabledUsers.length > 0 && (
        <>
          <h3 style={{ marginTop: "2rem" }}>Deactivated Users</h3>
          <table className="table table-bordered border-secondary">
            <thead>
              <tr>
                <th scope="col">Username</th>
                <th scope="col">Email</th>
                <th scope="col">Full Name</th>
                <th scope="col">Auth Level</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>{disabledUsers.map(renderUserRow)}</tbody>
          </table>
        </>
      )}
    </div>
  );
}
