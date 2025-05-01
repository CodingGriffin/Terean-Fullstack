import { DisperCurveManager } from '../../Features/DisperCurveManager/DisperCurveManager';
import { DisperModelManager } from '../../Features/DisperModelManager/DisperModelManager';
import { DisperProvider } from '../../Contexts/DisperContext';
import UnitsSelector from '../../Features/DisperUnitSelector/DisperUnitSelector';
import SectionHeader from '../../Components/SectionHeader/SectionHeader';
import DisperSettingsSave from '../../Features/DisperSettingsSave/DisperSettingsSave';
import { Toast } from '../../Components/Toast/Toast';
import Navbar from '../../Components/navbar/Navbar';

export default function DisperPage() {

    return (
        <>
        <Navbar/>
        <div className="w-full">
            <Toast/>
            <DisperProvider>
                <div className="container-fluid py-4">
                    <div className="row mb-4">
                        <div className="col-12">
                            <SectionHeader title="Dispersion Analysis">
                                <div className='d-flex gap-2'>
                                    <UnitsSelector />
                                    <DisperSettingsSave />
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
            </DisperProvider>
        </div>
        </>
    );
}