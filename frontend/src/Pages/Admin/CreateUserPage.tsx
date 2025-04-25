import { useNavigate } from "react-router-dom";
import UserForm, { UserFormData } from "../../Components/admin/UserForm";
import { backendUrl } from "../../utils/utils";
import Navbar from "../../Components/navbar/Navbar";

export default function CreateUser() {
  const navigate = useNavigate();

  // Handle the creation of a new user
  const handleCreate = async (data: UserFormData) => {
    const token = localStorage.getItem("token");  

    const cleanUrl = `${backendUrl.replace(/\/+$/, "")}/admin/register_user`;
    const response = await fetch(cleanUrl, { 
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
    <>
      <Navbar />
      <div className="d-flex flex-column align-items-center mt-5">
        <h2 className="text-center mb-4">Create New User</h2>
        <UserForm onSubmit={handleCreate} />
      </div>
    </>
  );
}
