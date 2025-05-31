import { useNavigate } from "react-router-dom";
import { useAuth } from "../../Contexts/authContext"; 
import UserForm, { UserFormData } from "./UserForm";
import { backendUrl } from "../../utils/utils";

export default function CreateUser() {
  const { userData } = useAuth();
  const navigate = useNavigate();

  const handleCreate = async (data: UserFormData) => {
    
    
    if (!userData || userData.auth_level < 4) {
      console.log("You do not have permission to create users.");
      return;
    }

    const token = localStorage.getItem("token");

    const response = await fetch(`${backendUrl}/admin/register_user`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (response.ok) {
      navigate("/admin");
    } else {
      console.error("Failed to create user");
    }
  };

  return (
    <div>
      <h2>Create New User</h2>
      <UserForm onSubmit={handleCreate} />
    </div>
  );
}
