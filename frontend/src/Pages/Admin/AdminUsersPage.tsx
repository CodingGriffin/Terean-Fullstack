import { backendUrl } from "../../utils/utils";
import { useEffect, useState } from "react";
import { UserData } from "../../types";

const AdminUsers = () => {
  const [users, setUsers] = useState<UserData[]>([]);

  useEffect(() => {

    const fetchUsers = async () => {
      const token = localStorage.getItem("token");  

      if (!token) {
        console.log("No token found");
        return;
      }

      //once again i am using a clean url, this is annoying and i dont know how to permafix quite yet
      const cleanUrl = `${backendUrl.replace(/\/+$/, "")}/admin/register_user`;
      console.log(cleanUrl)
      const response = await fetch(cleanUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data: UserData[] = await response.json();
        setUsers(data); 
      } else {
        console.error("Failed to fetch users", response.status);
      }
    };

    fetchUsers();
  }, []);

  return (
    <>
      
      <div>
        <h2>Admin Users</h2>
        <ul>
          {users.map((user, index) => (
            <li key={index}>
              {user.username} - {user.full_name} - {user.email} (Auth Level: {user.auth_level})
              {user.expiration && <p>Expires: {user.expiration}</p>}
            </li>
          ))}
        </ul>
      </div>
    </>
    
  );
};

export default AdminUsers;
