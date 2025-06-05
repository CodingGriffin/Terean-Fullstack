

@app.post("/process/auto-velocity-model")
async def auto_velocity_model(
    picks: Annotated[str, Form(...)],
    current_user: User = Depends(get_current_user)
):
    check_permissions(current_user, 1)
    
    default_model = {
        "layers": [
            {"startDepth": 0.0, "endDepth": 30.0, "velocity": 760.0, "density": 2.0, "ignore": 0},
            {"startDepth": 30.0, "endDepth": 44.0, "velocity": 1061.0, "density": 2.0, "ignore": 0},
            {"startDepth": 44.0, "endDepth": 144.0, "velocity": 1270.657, "density": 2.0, "ignore": 0},
        ],
        "modelAxisLimits": {
            "xmin": 50,
            "xmax": 1400,
            "ymin": 0,
            "ymax": 150
        }
    }
    
    return default_model


@app.post("/process/auto-limit")
async def auto_limit(
    project_id: Annotated[str, Form(...)],
    current_user: User = Depends(get_current_user)
):
    check_permissions(current_user, 1)
    
    # For now, just return default values
    # In a real implementation, you would:
    # 1. Get all SGY files for the project
    try:
        # Find all SGY files associated with this project
        project_sgy_dir = os.path.join(GLOBAL_SGY_FILES_DIR, project_id)
        if os.path.exists(project_sgy_dir):
            sgy_files = glob.glob(os.path.join(project_sgy_dir, "*.sgy"))
            logger.info(f"Found {len(sgy_files)} SGY files for project {project_id}")
        else:
            logger.warning(f"No SGY directory found for project {project_id}")
            sgy_files = []
            
        # 2. Analyze them to determine optimal frequency and slowness limits
        if sgy_files:
            # This is where you would analyze the files
            # For now, we'll just return different defaults based on file count
            if len(sgy_files) > 5:
                # More files might need higher frequency resolution
                return {
                    "maxFreq": 60.0,
                    "maxSlow": 0.012
                }
            elif len(sgy_files) > 0:
                # Some files found, use moderate settings
                return {
                    "maxFreq": 55.0,
                    "maxSlow": 0.014
                }
    except Exception as e:
        logger.error(f"Error analyzing SGY files: {str(e)}")
        # Continue to default values on error
    
    # 3. Return those values (or defaults if analysis failed)
    default_limits = {
        "maxFreq": 50.0,
        "maxSlow": 0.015
    }
    
    return default_limits


@app.post("/process/auto-pick")
async def auto_pick(
    project_id: Annotated[str, Form(...)],
    current_user: User = Depends(get_current_user)
):
    check_permissions(current_user, 1)
    
    default_picks = [
        {"d1": 0, "d2": 0, "frequency": 5.0, "d3": 0, "slowness": 0.0015, "d4": 0, "d5": 0},
        {"d1": 0, "d2": 0, "frequency": 10.0, "d3": 0, "slowness": 0.0012, "d4": 0, "d5": 0},
        {"d1": 0, "d2": 0, "frequency": 15.0, "d3": 0, "slowness": 0.0010, "d4": 0, "d5": 0},
        {"d1": 0, "d2": 0, "frequency": 20.0, "d3": 0, "slowness": 0.0008, "d4": 0, "d5": 0},
        {"d1": 0, "d2": 0, "frequency": 25.0, "d3": 0, "slowness": 0.0007, "d4": 0, "d5": 0},
        {"d1": 0, "d2": 0, "frequency": 30.0, "d3": 0, "slowness": 0.0006, "d4": 0, "d5": 0},
        {"d1": 0, "d2": 0, "frequency": 35.0, "d3": 0, "slowness": 0.0005, "d4": 0, "d5": 0},
        {"d1": 0, "d2": 0, "frequency": 40.0, "d3": 0, "slowness": 0.0004, "d4": 0, "d5": 0}
    ]
    
    return default_picks
