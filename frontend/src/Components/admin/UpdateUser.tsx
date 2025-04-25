import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { backendUrl } from "../../utils/utils";
import UserForm, { UserFormData } from "./UserForm";

export default function UpdateUser() {
  const { username } = useParams();
  const navigate = useNavigate();
  const [userData, setUserData] = useState<UserFormData | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem("token");
      const res = await fetch(`${backendUrl}/admin/users`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (res.ok) {
        const users: UserFormData[] = await res.json();
        const target = users.find((u) => u.username === username);
        if (target) setUserData(target);
      }
    };
    fetchUser();
  }, [username]);

  const handleUpdate = async (data: UserFormData) => {
    const token = localStorage.getItem("token");

    const cleanUrl = `${backendUrl.replace(/\/+$/, "")}/admin/users/${username}`;
    const response = await fetch(cleanUrl, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (response.ok) {
      navigate("/admin");
    } else {
      console.error("Failed to update user");
    }
  };

  return (
    <div>
      <h2>Update User</h2>
      {userData ? (
        <UserForm initialData={userData} onSubmit={handleUpdate} isUpdate />
      ) : (
        <p>Loading user data...</p>
      )}
    </div>
  );
}
