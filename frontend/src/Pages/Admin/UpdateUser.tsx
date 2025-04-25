import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { backendUrl } from "../../utils/utils";
import UserForm, {UserFormData } from "../../Components/admin/UserForm";
import Navbar from "../../Components/navbar/Navbar";

export default function UpdateUser() {
  const { username } = useParams();  
  const navigate = useNavigate();
  const [userData, setUserData] = useState<UserFormData | null>(null);  

  useEffect(() => {
    
    const fetchUser = async () => {
      const token = localStorage.getItem("token"); 
      if (!token) {
        console.error("No token found");
        return;
      }

      const cleanUrl = `${backendUrl.replace(/\/+$/, "")}/admin/users`;
      const res = await fetch(cleanUrl, {
        headers: { Authorization: `Bearer ${token}` },  
      });

      if (res.ok) {
        const users: UserFormData[] = await res.json();  
        const target = users.find((u) => u.username === username);  
        if (target) {
          setUserData(target);
        } else {
          console.error("User not found");
        }
      } else {
        console.error("Failed to fetch users");
      }
    };

    fetchUser();
  }, [username]); 

  const handleUpdate = async (data: UserFormData) => {
    const token = localStorage.getItem("token"); 
    if (!token) {
      console.error("No token found");
      return;
    }

    const response = await fetch(
        `${backendUrl.replace(/\/+$/, "")}/admin/users/${username}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(data),
        }
      );

    if (response.ok) {
      navigate("/admin");  // Redirect to the admin dashboard after successful update
    } else {
      console.error("Failed to update user");
    }
  };

  return (
    <>
    <Navbar />
    <div className="d-flex flex-column align-items-center mt-4">
      <h2>Update User</h2>
      {userData ? (
        <UserForm initialData={userData} onSubmit={handleUpdate} isUpdate />
      ) : (
        <p>Loading user data...</p>
      )}
    </div>
    </>
  );
}
