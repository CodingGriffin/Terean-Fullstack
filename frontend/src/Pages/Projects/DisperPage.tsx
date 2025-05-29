import { DisperCurveManager } from '../../Features/DisperCurveManager/DisperCurveManager';
import { DisperModelManager } from '../../Features/DisperModelManager/DisperModelManager';
import { DisperProvider, useDisper } from '../../Contexts/DisperContext';
import UnitsSelector from '../../Features/DisperUnitSelector/DisperUnitSelector';
import SectionHeader from '../../Components/SectionHeader/SectionHeader';
import DisperSettingsSave from '../../Features/DisperSettingsSave/DisperSettingsSave';
import { Toast } from '../../Components/Toast/Toast';
import Navbar from '../../Components/navbar/Navbar';
import { useNavigate, useParams } from 'react-router-dom';

const DisperPageContent = () => {
    const { state: { isLoading } } = useDisper();

    const navigate = useNavigate();
    const { projectId } = useParams();

    if (isLoading) {
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
                            <SectionHeader title="Dispersion Analysis">
                                <div className='d-flex gap-2'>
                                    <UnitsSelector />
                                    <DisperSettingsSave />
                                    <button 
                                    className="btn btn-sm btn-outline-info"
                                    onClick={() => navigate(`/projects/${projectId}/picks`)}
                                    >
                                        Go to Picks
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

                    <div className="row g-4">
                        <div className="col-lg-6">
                            <DisperCurveManager />
                        </div>
                        <div className="col-lg-6">
                            <DisperModelManager />
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
};

export default function DisperPage() {
    return (
        <DisperProvider>
            <DisperPageContent />
        </DisperProvider>
    );
}
