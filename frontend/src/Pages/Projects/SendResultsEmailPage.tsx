import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Navbar from "../../Components/navbar/Navbar";
import { Toast } from "../../Components/Toast/Toast";
import SectionHeader from "../../Components/SectionHeader/SectionHeader";
import { getProjectById, generateResultsEmail, getAdditionalFileContent } from "../../services/api";
import { addToast } from "../../store/slices/toastSlice";
import { useAppDispatch } from "../../hooks/useAppDispatch";

interface Project {
  id: string;
  name: string;
  status?: string;
  priority?: string;
  client?: {
    id: number;
    name: string;
    contacts: Array<{
      id: number;
      name: string;
      email: string;
      phone_number?: string;
    }>;
  };
  additional_files?: Array<{
    id: string;
    original_name: string;
    name: string;
  }>;
}

interface ContactOption {
  name: string;
  email: string;
  source: 'user_cfg' | 'client_contact';
}

const SendResultsEmailPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  
  // Dropdown options
  const [contactOptions, setContactOptions] = useState<ContactOption[]>([]);
  const [hasProjectVelocityModel, setHasProjectVelocityModel] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    velocityModelOption: '',
    velocityModelFile: null as File | null,
    clientContactOption: '',
    manualClientName: '',
    manualClientEmail: ''
  });
  
  // Validation errors
  const [errors, setErrors] = useState({
    velocityModelOption: '',
    velocityModelFile: '',
    clientContactOption: '',
    manualClientName: '',
    manualClientEmail: ''
  });

  useEffect(() => {
    fetchProjectData();
  }, [projectId]);

  const fetchProjectData = async () => {
    if (!projectId) return;
    
    setLoading(true);
    try {
      const data = await getProjectById(projectId);
      setProject(data);
      
      // Check for project velocity model (you may need to adjust this logic based on your data structure)
      setHasProjectVelocityModel(true); // Assume all projects have velocity models for now
      
      // Set default velocity model option to project
      setFormData(prev => ({
        ...prev,
        velocityModelOption: 'project'
      }));
      
      // Parse contact options and set defaults
      await parseContactOptions(data);
      
    } catch (error) {
      console.error("Error fetching project:", error);
      dispatch(addToast({
        message: "Failed to load project data",
        type: "error",
        duration: 5000
      }));
    } finally {
      setLoading(false);
    }
  };

  const parseContactOptions = async (projectData: Project) => {
    const userCfgOptions: ContactOption[] = [];
    const clientContactOptions: ContactOption[] = [];
    
    // Parse user.cfg if it exists (highest priority)
    const userCfgFile = projectData.additional_files?.find(
      file => {
        return file.original_name.toLowerCase() === 'user.cfg'
      }
    );
    
    if (userCfgFile) {
      try {
        const fileContent = await getAdditionalFileContent(projectId!, userCfgFile.id);
        const userCfgData = parseUserCfg(fileContent);
        if (userCfgData.name && userCfgData.email) {
          userCfgOptions.push({
            name: userCfgData.name,
            email: userCfgData.email,
            source: 'user_cfg'
          });
        }
      } catch (error) {
        console.error("Error parsing user.cfg:", error);
      }
    }
    
    // Add client contacts if available (second priority)
    if (projectData.client?.contacts) {
      projectData.client.contacts.forEach(contact => {
        clientContactOptions.push({
          name: contact.name,
          email: contact.email,
          source: 'client_contact'
        });
      });
    }
    
    // Combine options with user.cfg first, then client contacts
    const allOptions = [...userCfgOptions, ...clientContactOptions];
    setContactOptions(allOptions);
    
    // Set default selection based on priority: user.cfg > client contacts > manual
    if (userCfgOptions.length > 0) {
      // Use first user.cfg option (highest priority)
      setFormData(prev => ({
        ...prev,
        clientContactOption: `${userCfgOptions[0].name}|${userCfgOptions[0].email}`
      }));
    } else if (clientContactOptions.length > 0) {
      // Use first client contact (second priority)
      setFormData(prev => ({
        ...prev,
        clientContactOption: `${clientContactOptions[0].name}|${clientContactOptions[0].email}`
      }));
    } else {
      // Default to manual entry (lowest priority)
      setFormData(prev => ({
        ...prev,
        clientContactOption: 'manual'
      }));
    }
  };

  const parseUserCfg = (content: string) => {
    const lines = content.split('\n');
    const data: { name?: string; email?: string; phone?: string } = {};
    
    lines.forEach(line => {
      const trimmedLine = line.trim();
      if (trimmedLine.startsWith('name=')) {
        data.name = trimmedLine.substring(5).trim();
      } else if (trimmedLine.startsWith('email=')) {
        data.email = trimmedLine.substring(6).trim();
      } else if (trimmedLine.startsWith('phone=')) {
        data.phone = trimmedLine.substring(6).trim();
      }
    });
    
    return data;
  };

  const getDefaultClientContactOption = () => {
    // Priority: user.cfg > client contacts > manual
    const userCfgOptions = contactOptions.filter(opt => opt.source === 'user_cfg');
    const clientContactOptions = contactOptions.filter(opt => opt.source === 'client_contact');
    
    if (userCfgOptions.length > 0) {
      return `${userCfgOptions[0].name}|${userCfgOptions[0].email}`;
    } else if (clientContactOptions.length > 0) {
      return `${clientContactOptions[0].name}|${clientContactOptions[0].email}`;
    } else {
      return 'manual';
    }
  };

  const validateForm = () => {
    const newErrors = {
      velocityModelOption: '',
      velocityModelFile: '',
      clientContactOption: '',
      manualClientName: '',
      manualClientEmail: ''
    };

    // Validate velocity model selection
    if (!formData.velocityModelOption) {
      newErrors.velocityModelOption = 'Please select a velocity model option';
    } else if (formData.velocityModelOption === 'upload' && !formData.velocityModelFile) {
      newErrors.velocityModelFile = 'Please select a velocity model file';
    } else if (formData.velocityModelFile && !formData.velocityModelFile.name.toLowerCase().endsWith('.txt')) {
      newErrors.velocityModelFile = 'Please select a .txt file';
    }

    // Validate client contact selection
    if (!formData.clientContactOption) {
      newErrors.clientContactOption = 'Please select a client contact option';
    } else if (formData.clientContactOption === 'manual') {
      if (!formData.manualClientName.trim()) {
        newErrors.manualClientName = 'Client name is required';
      }
      if (!formData.manualClientEmail.trim()) {
        newErrors.manualClientEmail = 'Client email is required';
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.manualClientEmail)) {
        newErrors.manualClientEmail = 'Please enter a valid email address';
      }
    }

    setErrors(newErrors);
    return !Object.values(newErrors).some(error => error !== '');
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user makes changes
    if (errors[field as keyof typeof errors]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null;
    setFormData(prev => ({ ...prev, velocityModelFile: file }));
    
    // Clear error when file is selected
    if (errors.velocityModelFile) {
      setErrors(prev => ({ ...prev, velocityModelFile: '' }));
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!validateForm() || !projectId) {
      return;
    }

    setSubmitting(true);
    try {
      let clientName = '';
      let clientEmail = '';
      let velocityFile: File | null = null;

      // Extract client information
      if (formData.clientContactOption === 'manual') {
        clientName = formData.manualClientName;
        clientEmail = formData.manualClientEmail;
      } else {
        const [name, email] = formData.clientContactOption.split('|');
        clientName = name;
        clientEmail = email;
      }

      // Handle velocity model
      if (formData.velocityModelOption === 'upload' && formData.velocityModelFile) {
        velocityFile = formData.velocityModelFile;
      } else if (formData.velocityModelOption === 'project') {
        // Create a placeholder file for project velocity model
        // The backend should handle this case differently
        const blob = new Blob(['USE_PROJECT_VELOCITY_MODEL'], { type: 'text/plain' });
        velocityFile = new File([blob], 'project_velocity_model.txt', { type: 'text/plain' });
      }

      if (!velocityFile) {
        throw new Error('No velocity model specified');
      }

      await generateResultsEmail(
        projectId,
        velocityFile,
        clientName,
        clientEmail
      );
      
      dispatch(addToast({
        message: "Results email generated and sent successfully",
        type: "success",
        duration: 5000
      }));

      // Reset form
      setFormData({
        velocityModelOption: 'project',
        velocityModelFile: null,
        clientContactOption: getDefaultClientContactOption(),
        manualClientName: '',
        manualClientEmail: ''
      });
      
      // Reset file input
      const fileInput = document.getElementById('velocity-model-file') as HTMLInputElement;
      if (fileInput) {
        fileInput.value = '';
      }

    } catch (error) {
      console.error("Error generating results email:", error);
      dispatch(addToast({
        message: "Failed to generate and send results email",
        type: "error",
        duration: 5000
      }));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <>
        <Navbar />
        <div className="w-full">
          <Toast />
          <div className="container-fluid py-4">
            <div className="d-flex justify-content-center align-items-center" style={{ minHeight: "60vh" }}>
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Navbar />
      <div className="w-full">
        <Toast />
        <div className="container-fluid">
          <div className="row mb-4">
            <div className="col-12">
              <SectionHeader title={`Send Results Email - ${project?.name || projectId}`}>
                <div className="d-flex gap-2">
                  <button 
                    className="btn btn-sm btn-outline-info"
                    onClick={() => navigate(`/projects/${projectId}/picks`)}
                  >
                    Go to Picks
                  </button>
                  <button 
                    className="btn btn-sm btn-outline-info"
                    onClick={() => navigate(`/projects/${projectId}/disper`)}
                  >
                    Go to Disper
                  </button>
                  <button 
                    className="btn btn-sm btn-outline-secondary"
                    onClick={() => navigate(`/projects/${projectId}`)}
                  >
                    Back to Project
                  </button>
                </div>
              </SectionHeader>
            </div>
          </div>

          {/* Main Form */}
          <div className="row justify-content-center">
            <div className="col-md-8 col-lg-6">
              <div className="card shadow-sm">
                <div className="card-body">
                  <h5 className="card-title mb-4">
                    <i className="bi bi-envelope-paper me-2"></i>
                    Generate Results Email
                  </h5>
                  <form onSubmit={handleSubmit}>
                    {/* Velocity Model Selection */}
                    <div className="mb-3">
                      <label htmlFor="velocity-model-option" className="form-label">
                        Velocity Model <span className="text-danger">*</span>
                      </label>
                      <select
                        className={`form-select ${errors.velocityModelOption ? 'is-invalid' : ''}`}
                        id="velocity-model-option"
                        value={formData.velocityModelOption}
                        onChange={(e) => handleInputChange('velocityModelOption', e.target.value)}
                        disabled={submitting}
                      >
                        <option value="">Select velocity model option...</option>
                        {hasProjectVelocityModel && (
                          <option value="project">Use project velocity model</option>
                        )}
                        <option value="upload">Upload velocity model</option>
                      </select>
                      {errors.velocityModelOption && (
                        <div className="invalid-feedback">
                          {errors.velocityModelOption}
                        </div>
                      )}
                    </div>

                    {/* File Upload (shown only when upload is selected) */}
                    {formData.velocityModelOption === 'upload' && (
                      <div className="mb-3">
                        <label htmlFor="velocity-model-file" className="form-label">
                          Upload Velocity Model File <span className="text-danger">*</span>
                        </label>
                        <input
                          type="file"
                          className={`form-control ${errors.velocityModelFile ? 'is-invalid' : ''}`}
                          id="velocity-model-file"
                          accept=".txt"
                          onChange={handleFileChange}
                          disabled={submitting}
                        />
                        <div className="form-text">
                          Please select a .txt file containing the velocity model data.
                        </div>
                        {errors.velocityModelFile && (
                          <div className="invalid-feedback">
                            {errors.velocityModelFile}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Client Contact Selection */}
                    <div className="mb-3">
                      <label htmlFor="client-contact-option" className="form-label">
                        Client Contact <span className="text-danger">*</span>
                      </label>
                      <select
                        className={`form-select ${errors.clientContactOption ? 'is-invalid' : ''}`}
                        id="client-contact-option"
                        value={formData.clientContactOption}
                        onChange={(e) => handleInputChange('clientContactOption', e.target.value)}
                        disabled={submitting}
                      >
                        <option value="">Select client contact...</option>
                        {contactOptions.map((contact, index) => (
                          <option key={index} value={`${contact.name}|${contact.email}`}>
                            {contact.name} ({contact.email}) - {contact.source === 'user_cfg' ? 'from user.cfg' : 'client contact'}
                          </option>
                        ))}
                        <option value="manual">Enter manually</option>
                      </select>
                      {errors.clientContactOption && (
                        <div className="invalid-feedback">
                          {errors.clientContactOption}
                        </div>
                      )}
                    </div>

                    {/* Manual Client Entry (shown only when manual is selected) */}
                    {formData.clientContactOption === 'manual' && (
                      <>
                        <div className="mb-3">
                          <label htmlFor="manual-client-name" className="form-label">
                            Client Name <span className="text-danger">*</span>
                          </label>
                          <input
                            type="text"
                            className={`form-control ${errors.manualClientName ? 'is-invalid' : ''}`}
                            id="manual-client-name"
                            value={formData.manualClientName}
                            onChange={(e) => handleInputChange('manualClientName', e.target.value)}
                            placeholder="Enter client name"
                            disabled={submitting}
                          />
                          {errors.manualClientName && (
                            <div className="invalid-feedback">
                              {errors.manualClientName}
                            </div>
                          )}
                        </div>

                        <div className="mb-4">
                          <label htmlFor="manual-client-email" className="form-label">
                            Client Email <span className="text-danger">*</span>
                          </label>
                          <input
                            type="email"
                            className={`form-control ${errors.manualClientEmail ? 'is-invalid' : ''}`}
                            id="manual-client-email"
                            value={formData.manualClientEmail}
                            onChange={(e) => handleInputChange('manualClientEmail', e.target.value)}
                            placeholder="Enter client email address"
                            disabled={submitting}
                          />
                          {errors.manualClientEmail && (
                            <div className="invalid-feedback">
                              {errors.manualClientEmail}
                            </div>
                          )}
                        </div>
                      </>
                    )}

                    {/* Submit Button */}
                    <div className="d-grid">
                      <button
                        type="submit"
                        className="btn btn-primary"
                        disabled={submitting}
                      >
                        {submitting ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                            Generating Email...
                          </>
                        ) : (
                          <>
                            <i className="bi bi-envelope-paper me-2"></i>
                            Generate & Send Email
                          </>
                        )}
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default SendResultsEmailPage; 
