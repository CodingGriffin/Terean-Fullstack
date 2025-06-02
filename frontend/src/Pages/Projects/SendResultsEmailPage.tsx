import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import Navbar from "../../Components/navbar/Navbar";
import { Toast } from "../../Components/Toast/Toast";
import SectionHeader from "../../Components/SectionHeader/SectionHeader";
import { getProjectById, generateResultsEmail } from "../../services/api";
import { addToast } from "../../store/slices/toastSlice";
import { useAppDispatch } from "../../hooks/useAppDispatch";

interface Project {
  id: string;
  name: string;
  status?: string;
  priority?: string;
}

const SendResultsEmailPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    clientName: '',
    clientEmail: '',
    velocityModelFile: null as File | null
  });
  
  // Validation errors
  const [errors, setErrors] = useState({
    clientName: '',
    clientEmail: '',
    velocityModelFile: ''
  });

  useEffect(() => {
    fetchProject();
  }, [projectId]);

  const fetchProject = async () => {
    if (!projectId) return;
    
    setLoading(true);
    try {
      const data = await getProjectById(projectId);
      setProject(data);
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

  const validateForm = () => {
    const newErrors = {
      clientName: '',
      clientEmail: '',
      velocityModelFile: ''
    };

    // Validate client name
    if (!formData.clientName.trim()) {
      newErrors.clientName = 'Client name is required';
    }

    // Validate client email
    if (!formData.clientEmail.trim()) {
      newErrors.clientEmail = 'Client email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.clientEmail)) {
      newErrors.clientEmail = 'Please enter a valid email address';
    }

    // Validate velocity model file
    if (!formData.velocityModelFile) {
      newErrors.velocityModelFile = 'Velocity model file is required';
    } else if (!formData.velocityModelFile.name.toLowerCase().endsWith('.txt')) {
      newErrors.velocityModelFile = 'Please select a .txt file';
    }

    setErrors(newErrors);
    return !Object.values(newErrors).some(error => error !== '');
  };

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
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
    
    if (!validateForm() || !projectId || !formData.velocityModelFile) {
      return;
    }

    setSubmitting(true);
    try {
      await generateResultsEmail(
        projectId,
        formData.velocityModelFile,
        formData.clientName,
        formData.clientEmail
      );
      
      dispatch(addToast({
        message: "Results email generated and sent successfully",
        type: "success",
        duration: 5000
      }));

      // Reset form
      setFormData({
        clientName: '',
        clientEmail: '',
        velocityModelFile: null
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
                    {/* Velocity Model File */}
                    <div className="mb-3">
                      <label htmlFor="velocity-model-file" className="form-label">
                        Velocity Model <span className="text-danger">*</span>
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

                    {/* Client Name */}
                    <div className="mb-3">
                      <label htmlFor="client-name" className="form-label">
                        Client Name <span className="text-danger">*</span>
                      </label>
                      <input
                        type="text"
                        className={`form-control ${errors.clientName ? 'is-invalid' : ''}`}
                        id="client-name"
                        value={formData.clientName}
                        onChange={(e) => handleInputChange('clientName', e.target.value)}
                        placeholder="Enter client name"
                        disabled={submitting}
                      />
                      {errors.clientName && (
                        <div className="invalid-feedback">
                          {errors.clientName}
                        </div>
                      )}
                    </div>

                    {/* Client Email */}
                    <div className="mb-4">
                      <label htmlFor="client-email" className="form-label">
                        Client Email <span className="text-danger">*</span>
                      </label>
                      <input
                        type="email"
                        className={`form-control ${errors.clientEmail ? 'is-invalid' : ''}`}
                        id="client-email"
                        value={formData.clientEmail}
                        onChange={(e) => handleInputChange('clientEmail', e.target.value)}
                        placeholder="Enter client email address"
                        disabled={submitting}
                      />
                      {errors.clientEmail && (
                        <div className="invalid-feedback">
                          {errors.clientEmail}
                        </div>
                      )}
                    </div>

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
