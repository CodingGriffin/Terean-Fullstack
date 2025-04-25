import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { backendUrl } from "../../utils/utils";

export default function UpdateUser() {
  const { userId } = useParams();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [authLevel, setAuthLevel] = useState(1);
  const [disabled, setDisabled] = useState(false);
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUser = async () => {
      const response = await fetch(`${backendUrl}/admin/get_user/${userId}`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setUsername(data.username);
        setEmail(data.email);
        setFullName(data.full_name);
        setAuthLevel(data.auth_level);
        setDisabled(data.disabled);
      }
    };

    fetchUser();
  }, [userId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const response = await fetch(`${backendUrl}/admin/update_user`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: JSON.stringify({
        username,
        email,
        full_name: fullName,
        auth_level: authLevel,
        disabled,
        password,
      }),
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
      <form onSubmit={handleSubmit}>
        <label>Username</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <label>Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <label>Full Name</label>
        <input
          type="text"
          value={fullName}
          onChange={(e) => setFullName(e.target.value)}
          required
        />
        <label>Auth Level</label>
        <input
          type="number"
          value={authLevel}
          onChange={(e) => setAuthLevel(Number(e.target.value))}
          required
        />
        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <label>Disabled</label>
        <input
          type="checkbox"
          checked={disabled}
          onChange={() => setDisabled(!disabled)}
        />
        <button type="submit">Update User</button>
      </form>
    </div>
  );
}
