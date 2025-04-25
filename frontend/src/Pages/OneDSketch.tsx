import { useEffect, useState } from "react";
import Navbar from "../Components/navbar/Navbar.tsx";
import RecordManager from "../Components/RecordManager.js";
import VelModel from "../Components/VelModel.tsx";
import { useAuth } from "../Contexts/authContext.tsx";
import { useNavigate } from "react-router-dom";

/**
 *
 * @param period_vals Array of periods to calculate velocity for
 * @param num_layers Number of layers
 * @param layer_thicknesses Thicknesses of each layer. Calculate using end_depth - start_depth
 * @param vels_shear
 * @param phase_vel_min
 * @param phase_vel_max
 * @return Array of velocities for each period
 *         if a value would be outside the range of phase_vel_min-phase_vel_max, then null is returned for that value instead
 */
function CalcCurve(
  period_vals: number[],
  num_layers: number,
  layer_thicknesses: number[], //
  vels_shear: number[], // The velocities from the model
  phase_vel_min: number, // The min value on the left plot
  phase_vel_max: number // The max value on the left plot
) {
  // Create Array of densities the same size as the number of layers
  const densities = Array(num_layers).fill(2.0);
  // Calculate Vc as 3*Vs
  const vels_compression = vels_shear.map((x) => {
    return x * 3; //Math.sqrt(3)
  });

  // Create Vel Model object from parameters
  const model = new VelModel(
    num_layers,
    layer_thicknesses,
    densities,
    vels_compression,
    vels_shear,
    phase_vel_min,
    phase_vel_max,
    2.0
  );
  return period_vals.map((x) => model.getc_period(x));
}

export default function OneDSketch() {
  const { userData } = useAuth();
  const navigate = useNavigate();

  // Define *ALL* the state
  const [records, setRecords] = useState([]);
  const vels = CalcCurve(
    [0.02, 0.04526316],
    3,
    [30, 14, 100],
    [760, 1061, 1235],
    50,
    2500
  );
  console.log(vels);

  useEffect(() => {
    if (!userData) {
      navigate("/403");
    }
  }, [userData, navigate]);

  return (
    <div className="vh-100">
      <Navbar />
      <div
        className=".container-fluid pb-0 mx-0"
        style={{ height: "100%", minHeight: "300px" }}
      >
        <div className="one-d-main pb-0 mx-0 bg-light border border-1 col-xxl-6">
          <h1>Home</h1>
          <p>Welcome Text</p>
          <RecordManager records={records} setRecords={setRecords} />
        </div>
      </div>
    </div>
  );
}
