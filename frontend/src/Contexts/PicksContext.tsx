import { createContext, useContext, useReducer, useCallback, ReactNode, useEffect, useRef } from 'react';
import { useAppDispatch } from '../hooks/useAppDispatch';
import { addToast } from '../store/slices/toastSlice';
import { useParams } from 'react-router-dom';
import { PickData } from '../types/data';
import { savePicksByProjectId, fetchPicksByProjectId, processGridsForPreview, uploadSgyFilesWithIdsThunk, fetchOptionsByProjectId } from '../store/thunks/cacheThunks';
import { GeometryItem } from '../types/geometry';
import { RecordOption, RecordUploadFile } from '../types/record';
import { setGeometrySlice } from '../store/slices/geometrySlice';
import { setNumFreq, updateMaxFreq } from '../store/slices/freqSlice';
import { setNumSlow, updateMaxSlow } from '../store/slices/slowSlice';
import { setOptions } from '../store/slices/recordSlice';
import { setInitialized } from '../store/slices/initializationSlice';

const initialState = {
    points: [] as PickData[],
    hoveredPoint: null as PickData | null,
    isDragging: false,
    draggedPoint: null as PickData | null,
    plotDimensions: {
        width: 0,
        height: 0
    },
    isLoading: false,
    coordinateMatrix: [] as number[][],
    transformations: [] as string[],
    dataLimits: {
        minFrequency: 0.0001,
        maxFrequency: 100,
        minSlowness: 0.0001,
        maxSlowness: 100,
    },
    plotLimits: {
        xmin: 0.001,
        xmax: 10,
        ymin: 0,
        ymax: 1000
    },
    showDataManager: false,
    geometry: [] as GeometryItem[],
    savedGeometry: [] as GeometryItem[],
    freqSettings: {
        numFreq: 50,
        maxFreq: 50
    },
    savedFreqSettings: {
        numFreq: 50,
        maxFreq: 50
    },
    slowSettings: {
        numSlow: 50,
        maxSlow: 0.015
    },
    savedSlowSettings: {
        numSlow: 50,
        maxSlow: 0.015
    },
    recordOptions: [] as RecordOption[],
    savedRecordOptions: [] as RecordOption[],
    uploadFiles: {} as { [key: string]: File | null }
};

type PicksAction = 
    | { type: 'ADD_POINT'; payload: PickData }
    | { type: 'REMOVE_POINT'; payload: PickData }
    | { type: 'SET_POINTS'; payload: PickData[] }
    | { type: 'SET_HOVERED_POINT'; payload: PickData | null }
    | { type: 'SET_IS_DRAGGING'; payload: boolean }
    | { type: 'SET_DRAGGED_POINT'; payload: PickData | null }
    | { type: 'SET_PLOT_DIMENSIONS'; payload: { width: number; height: number } }
    | { type: 'SET_IS_LOADING'; payload: boolean }
    | { type: 'SET_COORDINATE_MATRIX'; payload: number[][] }
    | { type: 'ADD_TRANSFORMATION'; payload: string }
    | { type: 'EMPTY_TRANSFORMATIONS' }
    | { type: 'SET_PLOT_LIMITS'; payload: { xmin: number; xmax: number; ymin: number; ymax: number } }
    | { type: 'SET_DATA_LIMITS'; payload: { minFrequency: number; maxFrequency: number; minSlowness: number; maxSlowness: number } }
    | { type: 'SET_SHOW_DATA_MANAGER'; payload: boolean }
    | { type: 'SET_GEOMETRY'; payload: GeometryItem[] }
    | { type: 'SET_SAVED_GEOMETRY'; payload: GeometryItem[] }
    | { type: 'SET_FREQ_SETTINGS'; payload: { numFreq: number; maxFreq: number } }
    | { type: 'SET_SAVED_FREQ_SETTINGS'; payload: { numFreq: number; maxFreq: number } }
    | { type: 'SET_SLOW_SETTINGS'; payload: { numSlow: number; maxSlow: number } }
    | { type: 'SET_SAVED_SLOW_SETTINGS'; payload: { numSlow: number; maxSlow: number } }
    | { type: 'SET_RECORD_OPTIONS'; payload: RecordOption[] }
    | { type: 'SET_SAVED_RECORD_OPTIONS'; payload: RecordOption[] }
    | { type: 'SET_UPLOAD_FILES'; payload: { [key: string]: File | null } };

type PicksContextType = {
    state: typeof initialState;
    addPoint: (point: PickData) => void;
    removePoint: (point: PickData) => void;
    setPoints: (points: PickData[]) => void;
    setHoveredPoint: (point: PickData | null) => void;
    setIsDragging: (isDragging: boolean) => void;
    setDraggedPoint: (point: PickData | null) => void;
    setPlotDimensions: (dimensions: { width: number; height: number }) => void;
    setIsLoading: (isLoading: boolean) => void;
    setCoordinateMatrix: (matrix: number[][]) => void;
    addTransformation: (transformation: string) => void;
    emptyTransformations: () => void;
    setPlotLimits: (limits: { xmin: number; xmax: number; ymin: number; ymax: number }) => void;
    saveSettings: (projectId: string) => Promise<void>;
    loadSettings: (projectId: string) => Promise<void>;
    setShowDataManager: (show: boolean) => void;
    setGeometry: (geometry: GeometryItem[]) => void;
    setSavedGeometry: (geometry: GeometryItem[]) => void;
    setFreqSettings: (settings: { numFreq: number; maxFreq: number }) => void;
    setSavedFreqSettings: (settings: { numFreq: number; maxFreq: number }) => void;
    setSlowSettings: (settings: { numSlow: number; maxSlow: number }) => void;
    setSavedSlowSettings: (settings: { numSlow: number; maxSlow: number }) => void;
    setRecordOptions: (options: RecordOption[]) => void;
    setSavedRecordOptions: (options: RecordOption[]) => void;
    setUploadFiles: (files: { [key: string]: File | null }) => void;
    handleUploadFiles: (files: RecordUploadFile[] | null) => void;
    handleApplyChanges: () => void;
    handleDiscardChanges: () => void;
};

function reducer(state: typeof initialState, action: PicksAction): typeof initialState {
    switch (action.type) {
        case 'ADD_POINT':
            return {
                ...state,
                points: [...state.points, action.payload]
            };
        case 'REMOVE_POINT':
            return {
                ...state,
                points: state.points.filter(point => 
                    point.frequency !== action.payload.frequency || 
                    point.slowness !== action.payload.slowness
                )
            };
        case 'SET_POINTS':
            return {
                ...state,
                points: action.payload
            };
        case 'SET_HOVERED_POINT':
            return {
                ...state,
                hoveredPoint: action.payload
            };
        case 'SET_IS_DRAGGING':
            return {
                ...state,
                isDragging: action.payload
            };
        case 'SET_DRAGGED_POINT':
            return {
                ...state,
                draggedPoint: action.payload
            };
        case 'SET_PLOT_DIMENSIONS':
            return {
                ...state,
                plotDimensions: action.payload
            };
        case 'SET_IS_LOADING':
            return {
                ...state,
                isLoading: action.payload
            };
        case 'SET_COORDINATE_MATRIX':
            return {
                ...state,
                coordinateMatrix: action.payload
            };
        case 'ADD_TRANSFORMATION':
            return {
                ...state,
                transformations: [...state.transformations, action.payload]
            };
        case 'EMPTY_TRANSFORMATIONS':
            return {
                ...state,
                transformations: []
            };
        case 'SET_PLOT_LIMITS':
            return {
                ...state,
                plotLimits: action.payload
            };
        case 'SET_DATA_LIMITS':
            return {
                ...state,
                dataLimits: action.payload
            };
        case 'SET_SHOW_DATA_MANAGER':
            return {
                ...state,
                showDataManager: action.payload
            };
        case 'SET_GEOMETRY':
            return {
                ...state,
                geometry: action.payload
            };
        case 'SET_SAVED_GEOMETRY':
            return {
                ...state,
                savedGeometry: action.payload
            };
        case 'SET_FREQ_SETTINGS':
            return {
                ...state,
                freqSettings: action.payload
            };
        case 'SET_SAVED_FREQ_SETTINGS':
            return {
                ...state,
                savedFreqSettings: action.payload
            };
        case 'SET_SLOW_SETTINGS':
            return {
                ...state,
                slowSettings: action.payload
            };
        case 'SET_SAVED_SLOW_SETTINGS':
            return {
                ...state,
                savedSlowSettings: action.payload
            };
        case 'SET_RECORD_OPTIONS':
            return {
                ...state,
                recordOptions: action.payload
            };
        case 'SET_SAVED_RECORD_OPTIONS':
            return {
                ...state,
                savedRecordOptions: action.payload
            };
        case 'SET_UPLOAD_FILES':
            return {
                ...state,
                uploadFiles: action.payload
            };
        default:
            return state;
    }
}

export const PicksContext = createContext<PicksContextType | null>(null);

export function usePicks() {
    const context = useContext(PicksContext);
    if (!context) throw new Error('usePicks must be used within a PicksProvider');
    return context;
}

export function PicksProvider({ children }: { children: ReactNode }) {
    const [state, dispatch] = useReducer(reducer, initialState);
    const reduxDispatch = useAppDispatch();
    const { projectId } = useParams<{ projectId: string }>();
    const initialFetchDone = useRef(false);

    const addPoint = useCallback((point: PickData) => {
        dispatch({ type: 'ADD_POINT', payload: point });
    }, []);

    const removePoint = useCallback((point: PickData) => {
        dispatch({ type: 'REMOVE_POINT', payload: point });
    }, []);

    const setPoints = useCallback((points: PickData[]) => {
        dispatch({ type: 'SET_POINTS', payload: points });
    }, []);

    const setHoveredPoint = useCallback((point: PickData | null) => {
        dispatch({ type: 'SET_HOVERED_POINT', payload: point });
    }, []);

    const setIsDragging = useCallback((isDragging: boolean) => {
        dispatch({ type: 'SET_IS_DRAGGING', payload: isDragging });
    }, []);

    const setDraggedPoint = useCallback((point: PickData | null) => {
        dispatch({ type: 'SET_DRAGGED_POINT', payload: point });
    }, []);

    const setPlotDimensions = useCallback((dimensions: { width: number; height: number }) => {
        dispatch({ type: 'SET_PLOT_DIMENSIONS', payload: dimensions });
    }, []);

    const setIsLoading = useCallback((isLoading: boolean) => {
        dispatch({ type: 'SET_IS_LOADING', payload: isLoading });
    }, []);

    const setCoordinateMatrix = useCallback((matrix: number[][]) => {
        dispatch({ type: 'SET_COORDINATE_MATRIX', payload: matrix });
    }, []);

    const addTransformation = useCallback((transformation: string) => {
        dispatch({ type: 'ADD_TRANSFORMATION', payload: transformation });
    }, []);

    const emptyTransformations = useCallback(() => {
        dispatch({ type: 'EMPTY_TRANSFORMATIONS' });
    }, []);

    const setPlotLimits = useCallback((limits: { xmin: number; xmax: number; ymin: number; ymax: number }) => {
        dispatch({ type: 'SET_PLOT_LIMITS', payload: limits });
    }, []);

    const setShowDataManager = useCallback((show: boolean) => {
        dispatch({ type: 'SET_SHOW_DATA_MANAGER', payload: show });
    }, []);

    const setGeometry = useCallback((geometry: GeometryItem[]) => {
        dispatch({ type: 'SET_GEOMETRY', payload: geometry });
    }, []);

    const setSavedGeometry = useCallback((geometry: GeometryItem[]) => {
        dispatch({ type: 'SET_SAVED_GEOMETRY', payload: geometry });
    }, []);

    const setFreqSettings = useCallback((settings: { numFreq: number; maxFreq: number }) => {
        dispatch({ type: 'SET_FREQ_SETTINGS', payload: settings });
    }, []);

    const setSavedFreqSettings = useCallback((settings: { numFreq: number; maxFreq: number }) => {
        dispatch({ type: 'SET_SAVED_FREQ_SETTINGS', payload: settings });
    }, []);

    const setSlowSettings = useCallback((settings: { numSlow: number; maxSlow: number }) => {
        dispatch({ type: 'SET_SLOW_SETTINGS', payload: settings });
    }, []);

    const setSavedSlowSettings = useCallback((settings: { numSlow: number; maxSlow: number }) => {
        dispatch({ type: 'SET_SAVED_SLOW_SETTINGS', payload: settings });
    }, []);

    const setRecordOptions = useCallback((options: RecordOption[]) => {
        dispatch({ type: 'SET_RECORD_OPTIONS', payload: options });
    }, []);

    const setSavedRecordOptions = useCallback((options: RecordOption[]) => {
        dispatch({ type: 'SET_SAVED_RECORD_OPTIONS', payload: options });
    }, []);

    const setUploadFiles = useCallback((files: { [key: string]: File | null }) => {
        dispatch({ type: 'SET_UPLOAD_FILES', payload: files });
    }, []);

    const handleUploadFiles = useCallback((files: RecordUploadFile[] | null) => {
        const newUploadFiles = { ...state.uploadFiles };
        if (files === null) {
            setUploadFiles({});
        } else if (files.length === 1 && files[0].file === null) {
            delete newUploadFiles[files[0].id];
            setUploadFiles(newUploadFiles);
        } else {
            files.forEach((uploadFile) => newUploadFiles[uploadFile.id] = uploadFile.file);
            setUploadFiles(newUploadFiles);
        }
    }, [state.uploadFiles, setUploadFiles]);

    const handleApplyChanges = useCallback(async () => {
        const validationErrors = [];

        if (state.savedRecordOptions.length === 0) {
            validationErrors.push("No RecordOption is provided");
        }

        if (state.savedGeometry.length === 0) {
            validationErrors.push("No geometry data provided");
        }

        if (state.savedFreqSettings.numFreq <= 0 || state.savedFreqSettings.maxFreq <= 0) {
            validationErrors.push("Invalid frequency settings");
        }

        if (state.savedSlowSettings.numSlow <= 0 || state.savedSlowSettings.maxSlow <= 0) {
            validationErrors.push("Invalid slowness settings");
        }

        if (validationErrors.length > 0) {
            reduxDispatch(addToast({
                message: `Validation failed: ${validationErrors.join(", ")}`,
                type: "error",
                duration: 5000
            }));
            return;
        }

        reduxDispatch(setGeometrySlice(state.savedGeometry));
        reduxDispatch(setNumFreq(state.savedFreqSettings.numFreq));
        reduxDispatch(updateMaxFreq(state.savedFreqSettings.maxFreq));
        reduxDispatch(setNumSlow(state.savedSlowSettings.numSlow));
        reduxDispatch(updateMaxSlow(state.savedSlowSettings.maxSlow));
        reduxDispatch(setOptions(state.savedRecordOptions));

        if (projectId && state.savedRecordOptions.length > 0 && state.savedGeometry.length > 0) {
            try {
                await reduxDispatch(processGridsForPreview({
                    projectId,
                    recordOptions: JSON.stringify(state.savedRecordOptions),
                    geometryData: JSON.stringify(state.savedGeometry),
                    maxSlowness: state.savedSlowSettings.maxSlow,
                    maxFrequency: state.savedFreqSettings.maxFreq,
                    numSlowPoints: state.savedSlowSettings.numSlow,
                    numFreqPoints: state.savedFreqSettings.numFreq,
                    returnFreqAndSlow: true
                })).unwrap();

                reduxDispatch(addToast({
                    message: `Processing ${state.savedRecordOptions.length} files with ${state.savedGeometry.length} geometry points`,
                    type: "info",
                    duration: 3000
                }));
            } catch (error) {
                console.error("Error processing grids:", error);
                reduxDispatch(addToast({
                    message: "Failed to process grids",
                    type: "error",
                    duration: 5000
                }));
            }
        }

        setShowDataManager(false);
    }, [
        state.savedRecordOptions,
        state.savedGeometry,
        state.savedFreqSettings,
        state.savedSlowSettings,
        projectId,
        reduxDispatch,
        setShowDataManager
    ]);

    const handleDiscardChanges = useCallback(() => {
        console.log("Discarding changes");
        setSavedGeometry(state.geometry);
        setSavedFreqSettings(state.freqSettings);
        setSavedSlowSettings(state.slowSettings);
        setSavedRecordOptions(state.recordOptions);
        setUploadFiles({});

        reduxDispatch(addToast({
            message: "Changes discarded",
            type: "info",
            duration: 3000
        }));

        setShowDataManager(false);
    }, [
        state.geometry,
        state.freqSettings,
        state.slowSettings,
        state.recordOptions,
        reduxDispatch,
        setSavedGeometry,
        setSavedFreqSettings,
        setSavedSlowSettings,
        setSavedRecordOptions,
        setUploadFiles,
        setShowDataManager
    ]);

    const saveSettings = useCallback(async (projectId: string) => {
        if (!projectId) {
            reduxDispatch(addToast({
                message: "No project ID available",
                type: "error",
                duration: 5000
            }));
            return;
        }

        try {
            await reduxDispatch(savePicksByProjectId(projectId)).unwrap();
            reduxDispatch(addToast({
                message: "Picks settings saved successfully",
                type: "success",
                duration: 3000
            }));
        } catch (error) {
            console.error("Error saving picks settings:", error);
            reduxDispatch(addToast({
                message: "Failed to save picks settings",
                type: "error",
                duration: 5000
            }));
        }
    }, [reduxDispatch]);

    const loadSettings = useCallback(async (projectId: string) => {
        if (!projectId) {
            console.warn("No project ID available to load settings");
            return;
        }

        try {
            setIsLoading(true);
            
            // Fetch both picks and options data
            const [picksResult, optionsResult] = await Promise.all([
                reduxDispatch(fetchPicksByProjectId(projectId)).unwrap(),
                reduxDispatch(fetchOptionsByProjectId(projectId)).unwrap()
            ]);
            
            // Initialize picks if available
            if (picksResult?.picks) {
                setPoints(picksResult.picks);
            }

            // Initialize settings from options
            if (optionsResult?.options) {
                const { geometry, records, plotLimits } = optionsResult.options;

                // Initialize geometry
                setGeometry(geometry);
                setSavedGeometry(geometry);

                // Initialize frequency settings
                const freqSettings = {
                    numFreq: plotLimits.numFreq,
                    maxFreq: plotLimits.maxFreq
                };
                setFreqSettings(freqSettings);
                setSavedFreqSettings(freqSettings);

                // Initialize slowness settings
                const slowSettings = {
                    numSlow: plotLimits.numSlow,
                    maxSlow: plotLimits.maxSlow
                };
                setSlowSettings(slowSettings);
                setSavedSlowSettings(slowSettings);

                // Initialize record options
                setRecordOptions(records);
                setSavedRecordOptions(records);

                // Process grids for preview with initialized settings
                await reduxDispatch(processGridsForPreview({
                    projectId,
                    recordOptions: JSON.stringify(records),
                    geometryData: JSON.stringify(geometry),
                    maxSlowness: plotLimits.maxSlow,
                    maxFrequency: plotLimits.maxFreq,
                    numSlowPoints: plotLimits.numSlow,
                    numFreqPoints: plotLimits.numFreq,
                    returnFreqAndSlow: true
                })).unwrap();

                reduxDispatch(setInitialized(true));
                reduxDispatch(addToast({
                    message: "Data initialized successfully",
                    type: "success",
                    duration: 3000
                }));
            }
        } catch (error) {
            console.error("Error loading settings:", error);
            reduxDispatch(addToast({
                message: "Failed to load settings",
                type: "error",
                duration: 5000
            }));
        } finally {
            setIsLoading(false);
        }
    }, [
        reduxDispatch,
        setPoints,
        setIsLoading,
        setGeometry,
        setSavedGeometry,
        setFreqSettings,
        setSavedFreqSettings,
        setSlowSettings,
        setSavedSlowSettings,
        setRecordOptions,
        setSavedRecordOptions
    ]);

    const updateDataLimits = useCallback(() => {
        if (state.points.length > 0) {
            const minFrequency = Math.min(...state.points.map(point => point.frequency));
            const maxFrequency = Math.max(...state.points.map(point => point.frequency));
            const minSlowness = Math.min(...state.points.map(point => point.slowness));
            const maxSlowness = Math.max(...state.points.map(point => point.slowness));

            dispatch({
                type: 'SET_DATA_LIMITS',
                payload: { minFrequency, maxFrequency, minSlowness, maxSlowness }
            });
        }
    }, [state.points, dispatch]);

    useEffect(() => {
        updateDataLimits();
    }, [updateDataLimits]);

    useEffect(() => {
        if (projectId && !initialFetchDone.current) {
            console.log("Loading settings for project", projectId);
            loadSettings(projectId);
            initialFetchDone.current = true;
        }
    }, [projectId, loadSettings]);

    useEffect(() => {
        if (Object.values(state.uploadFiles).length > 0) {
            reduxDispatch(uploadSgyFilesWithIdsThunk(state.uploadFiles));
        }
    }, [state.uploadFiles, reduxDispatch]);

    return (
        <PicksContext.Provider
            value={{
                state,
                addPoint,
                removePoint,
                setPoints,
                setHoveredPoint,
                setIsDragging,
                setDraggedPoint,
                setPlotDimensions,
                setIsLoading,
                setCoordinateMatrix,
                addTransformation,
                emptyTransformations,
                setPlotLimits,
                saveSettings,
                loadSettings,
                setShowDataManager,
                setGeometry,
                setSavedGeometry,
                setFreqSettings,
                setSavedFreqSettings,
                setSlowSettings,
                setSavedSlowSettings,
                setRecordOptions,
                setSavedRecordOptions,
                setUploadFiles,
                handleUploadFiles,
                handleApplyChanges,
                handleDiscardChanges
            }}
        >
            {children}
        </PicksContext.Provider>
    );
} 
