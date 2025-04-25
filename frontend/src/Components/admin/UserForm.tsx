import { useState } from "react";
import type { AdminUser } from "../../types";
interface UserFormProps {
  initialData?: Partial<AdminUser>;
  onSubmit: (data: UserFormData) => void;
  isUpdate?: boolean;
}

export interface UserFormData {
  username: string;
  email: string;
  full_name: string;
  auth_level: number;
  password?: string;
  disabled: boolean;
}

export default function UserForm({ initialData = {}, onSubmit, isUpdate = false }: UserFormProps) {
  const [formData, setFormData] = useState<UserFormData>({
    username: initialData.username || "",
    email: initialData.email || "",
    full_name: initialData.full_name || "",
    auth_level: initialData.auth_level ?? 1,
    password: "",
    disabled: initialData.disabled ?? false,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form className="form container" onSubmit={handleSubmit}>

      <div className="row col-6 mx-auto">
        <div className="mb-3">
          <label htmlFor="username" className="form-label">Username</label>
          <input name="username" className="form-control" id="username" type="text" value={formData.username} onChange={handleChange} required={!isUpdate} disabled={isUpdate} />
        </div>
      </div>
      
      <div className="row col-6 mx-auto">
        <div className="mb-3">
          <label htmlFor="email" className="form-email">Email</label>
          <input name="email" className="form-control" id="email" type="email" value={formData.email} onChange={handleChange} />
        </div>
      </div>

      <div className="row col-6 mx-auto">
        <div className="mb-3">
          <label htmlFor="full_name" className="form-label">Full Name</label>
          <input name="full_name" className="form-control" id="full_name" type="text" value={formData.full_name} onChange={handleChange} />
        </div>
      </div>

      <div className="row col-6 mx-auto">
        <div className="mb-3">
          <label>Auth Level</label>
          <input name="auth_level" className="form-control" id="auth_level" type="number" value={formData.auth_level} onChange={handleChange} required />
        </div>
      </div>

      <div className="row col-6 mx-auto">
        {!isUpdate && (
          <div className="mb-3">
            <label>Password</label>
            <input name="password" className="form-control" id="password" type="password" value={formData.password} onChange={handleChange} required />
          </div>
        )}
      </div>

      <div className="row col-6 mx-auto">
        <div className="mb-3">
          <label className="form-check-label" htmlFor="disabled">Disabled</label>
          <input name="disabled" className="form-check-input" id="disabled" type="checkbox" checked={formData.disabled} onChange={handleChange} />
        </div>
      </div>

      <div className="row col-6 mx-auto">
        <button type="submit" className="btn btn-primary">{isUpdate ? "Update User" : "Create User"}</button>
      </div>
      
    </form>
  );
}
