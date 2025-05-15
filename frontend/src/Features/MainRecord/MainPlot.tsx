import { Container, Sprite, Graphics, Text, Texture } from "pixi.js";
import { useCallback, useRef, useEffect, useMemo, useState } from "react";
import { extend } from "@pixi/react";
import { BasePlot } from "../../Components/BasePlot/BasePlot";
import { useAppSelector } from "../../hooks/useAppSelector";
import { selectEnabledRecordCount, selectEnabledRecords } from "../../store/selectors/recordSelectors";
import { Matrix } from "../../types/record";
import { useAppDispatch } from "../../hooks/useAppDispatch";
import { addToast } from "../../store/slices/toastSlice";
import SectionHeader from "../../Components/SectionHeader/SectionHeader";
import { ColorMapManager } from "./ColorMapManager/ColorMapManager";
import ConfirmationModal from "../../Components/ConfirmationModal/ConfirmationModal";

import { 
  addPoint, 
  removePoint,
  setHoveredPoint, 
  setIsDragging, 
  setDraggedPoint,
  setPlotDimensions,
  setIsLoading,
  addTransformation,
  setCoordinateMatrix,
  emptyTransformations,
  setPoints,
} from "../../store/slices/plotSlice";
import { getMatrixShape } from "../../utils/matrix-util";
import { createTexture } from "../../utils/plot-util";
import { applyTransformation, areMatricesEqual } from "../../utils/matrix-util";
import { ORIGINAL_COORDINATE_MATRIX } from "../../utils/plot-util";
import { PickData } from "../../types/data";
import { useParams } from "react-router";
import { savePicksByProjectId } from "../../store/thunks/cacheThunks";

extend({ Container, Sprite, Graphics, Text });

interface PlotDimensions {
  width: number;
  height: number;
}

interface DataLimits {
  slowMin: number;
  slowMax: number;
  freqMin: number;
  freqMax: number;
}

interface CoordinateHelpers {
  toScreenX: (value: number) => number;
  fromScreenX: (x: number) => number;
  toScreenY: (value: number) => number;
  fromScreenY: (y: number) => number;
}

interface PointerEvent {
  data?: {
    global: {
      x: number;
      y: number;
    };
  };
  clientX?: number;
  clientY?: number;
  nativeEvent?: {
    shiftKey?: boolean;
    altKey?: boolean;
  };
  shiftKey?: boolean;
  altKey?: boolean;
}

interface FileHandle {
  getFile: () => Promise<File>;
}

interface FilePickerOptions {
  types: Array<{
    description: string;
    accept: {
      [key: string]: string[];
    };
  }>;
  multiple: boolean;
}

interface SaveFilePickerOptions {
  suggestedName: string;
  types: Array<{
    description: string;
    accept: {
      [key: string]: string[];
    };
  }>;
}

interface FileSystemWritable {
  write: (data: Blob) => Promise<void>;
  close: () => Promise<void>;
}

interface FileSystemFileHandle {
  createWritable: () => Promise<FileSystemWritable>;
}

export default function MainPlot() {
  const dispatch = useAppDispatch();
  const enabledRecords = useAppSelector(selectEnabledRecords);
  const enabledRecordCount = useAppSelector(selectEnabledRecordCount);
  const isInitialized = useAppSelector((state) => state.initialization.isInitialized);

  const { 
    selectedColorMap, 
    colorMaps,
    isLoading, 
    points, 
    hoveredPoint, 
    isDragging, 
    draggedPoint, 
    plotDimensions,
    coordinateMatrix,
    dataLimits,
    transformations
  } = useAppSelector((state: { plot: { 
    selectedColorMap: string;
    colorMaps: Record<string, any>;
    isLoading: boolean;
    points: PickData[];
    hoveredPoint: PickData | null;
    isDragging: boolean;
    draggedPoint: PickData | null;
    plotDimensions: PlotDimensions;
    coordinateMatrix: Matrix;
    dataLimits: DataLimits;
    transformations: string[];
  } }) => state.plot);
  
  const { projectId } = useParams();

  const plotRef = useRef<HTMLDivElement>(null);
  
  const [texture, setTexture] = useState<Texture | null>(null);
  const [tooltipContent, setTooltipContent] = useState<string>('');
  const [showUploadConfirmation, setShowUploadConfirmation] = useState<boolean>(false);
  const [pendingNewPoints, setPendingNewPoints] = useState<PickData[]>([]);

  const selectAxisValue = useCallback((axisKey:number): number => {
    switch(axisKey) {
      case 1:
        return dataLimits.slowMin;
      case 2:
        return dataLimits.slowMax;
      case -2:
        return dataLimits.freqMin;
      case -1:
        return dataLimits.freqMax;
      default:
        return 0;
    }
  }, [dataLimits]);
  
  const left = useCallback(() => selectAxisValue(coordinateMatrix[1][0]), [dataLimits, coordinateMatrix]);
  const right = useCallback(() => selectAxisValue(coordinateMatrix[1][2]), [dataLimits, coordinateMatrix]);
  const bottom = useCallback(() => selectAxisValue(coordinateMatrix[2][1]), [dataLimits, coordinateMatrix]);
  const top = useCallback(() => selectAxisValue(coordinateMatrix[0][1]), [dataLimits, coordinateMatrix]);
  const isAxisSwapped = useCallback(() => coordinateMatrix[1][0] < 0, [dataLimits, coordinateMatrix]);

  const isFlippedHorizontal = useCallback(() => coordinateMatrix[1][0] < coordinateMatrix[1][2], [coordinateMatrix]);
  const isFlippedVertical = useCallback(() => coordinateMatrix[0][1] < coordinateMatrix[2][1], [coordinateMatrix]);
  
  const coordinateHelpers : CoordinateHelpers = useMemo(
    () => ({
      toScreenX: (value: number) => {
        if (isAxisSwapped()) {
          return !isFlippedHorizontal()
            ? plotDimensions.width - 
              ((value - dataLimits.freqMin) / (dataLimits.freqMax - dataLimits.freqMin)) * 
              plotDimensions.width
            : ((value - dataLimits.freqMin) / (dataLimits.freqMax - dataLimits.freqMin)) * 
              plotDimensions.width;
        } else {
          return !isFlippedHorizontal()
            ? plotDimensions.width - 
              ((value - dataLimits.slowMin) / (dataLimits.slowMax - dataLimits.slowMin)) * 
              plotDimensions.width
            : ((value - dataLimits.slowMin) / (dataLimits.slowMax - dataLimits.slowMin)) * 
              plotDimensions.width;
        }
      },
      fromScreenX: (x: number) => {
        const value =
          isFlippedHorizontal()
            ? right() +
              ((plotDimensions.width - x) / plotDimensions.width) *
                (left() - right())
            : left() + (x / plotDimensions.width) * (right() - left());

        return Math.round(value * 1000000) / 1000000;
      },
      toScreenY: (value: number) => {
        if (isAxisSwapped()) {
          return !isFlippedVertical()
            ? plotDimensions.height - 
              ((value - dataLimits.slowMin) / (dataLimits.slowMax - dataLimits.slowMin)) * 
              plotDimensions.height
            : ((value - dataLimits.slowMin) / (dataLimits.slowMax - dataLimits.slowMin)) * 
              plotDimensions.height;
        } else {
          return !isFlippedVertical()
            ? plotDimensions.height - 
              ((value - dataLimits.freqMin) / (dataLimits.freqMax - dataLimits.freqMin)) * 
              plotDimensions.height
            : ((value - dataLimits.freqMin) / (dataLimits.freqMax - dataLimits.freqMin)) * 
              plotDimensions.height;
        }
      },
      fromScreenY: (y: number) => {
        const value =
          isFlippedVertical()
            ? bottom() +
              ((plotDimensions.height - y) / plotDimensions.height) *
                (top() - bottom())
            : top() + (y / plotDimensions.height) * (bottom() - top());

        return Math.round(value * 1000000) / 1000000;
      },
    }),
    [dataLimits, plotDimensions, coordinateMatrix, isAxisSwapped, isFlippedHorizontal, isFlippedVertical]
  );

  const handleDimensionChange = useCallback(
    (dimensions: PlotDimensions) => {
      dispatch(setPlotDimensions(dimensions));
    },
    [dispatch]
  );

  const handlePointerDown = useCallback((event: PointerEvent) => {
    console.log("PointerDown event:", event);
    
    let x: number, y: number;
    
    if (event.data && event.data.global) {
      // PixiJS event
      x = event.data.global.x;
      y = event.data.global.y;
      
    } else if (event.clientX !== undefined && event.clientY !== undefined) {
      // DOM event
      const rect = plotRef.current?.getBoundingClientRect();
      if (!rect) return;
      
      x = event.clientX - rect.left;
      y = event.clientY - rect.top;
    } else {
      console.error("Unknown event format:", event);
      return;
    }

    if ((event.nativeEvent && event.nativeEvent.shiftKey) || event.shiftKey) {
      const slow = isAxisSwapped() 
        ? coordinateHelpers.fromScreenY(y) 
        : coordinateHelpers.fromScreenX(x);
      const freq = isAxisSwapped() 
        ? coordinateHelpers.fromScreenX(x) 
        : coordinateHelpers.fromScreenY(y);
      
      console.log("Adding new point at coordinates:", { slow, freq });
      const newPoint:PickData = {
        d1: 0,
        d2: 0,
        frequency: freq,
        d3: 0,
        slowness: slow,
        d4: 0,
        d5: 0
      }
      dispatch(addPoint(newPoint));
      return;
    }
    
    const clickedPointIndex = points.findIndex(point => {
      // Convert slow/freq to screen coordinates for comparison
      const screenX = isAxisSwapped() 
        ? coordinateHelpers.toScreenX(point.frequency) 
        : coordinateHelpers.toScreenX(point.slowness);
      const screenY = isAxisSwapped() 
        ? coordinateHelpers.toScreenY(point.slowness) 
        : coordinateHelpers.toScreenY(point.frequency);
      
      const distance = Math.sqrt(
        Math.pow(screenX - x, 2) + Math.pow(screenY - y, 2)
      );
      return distance < 10;
    });
    
    if (clickedPointIndex !== -1) {
      const clickedPoint = points[clickedPointIndex];
      
      if ((event.nativeEvent && event.nativeEvent.altKey) || event.altKey) {
        console.log("Removing point:", clickedPoint);
        dispatch(removePoint(clickedPoint));
      } else {
        console.log("Starting drag on point:", clickedPoint);
        dispatch(setDraggedPoint(clickedPoint));
        dispatch(setIsDragging(true));
      }
    }
  }, [points, dispatch, plotRef, coordinateHelpers]);
  
  const handlePointerMove = useCallback((event: PointerEvent) => {
    let x: number, y: number;
    
    if (event.data && event.data.global) {
      // PixiJS event
      x = event.data.global.x;
      y = event.data.global.y;
    } else if (event.clientX !== undefined && event.clientY !== undefined) {
      // DOM event
      const rect = plotRef.current?.getBoundingClientRect();
      if (!rect) return;
      
      x = event.clientX - rect.left;
      y = event.clientY - rect.top;
    } else {
      return; // Unknown event format
    }
    
    if (isDragging && draggedPoint) {
      // Convert screen coordinates to slow/freq values
      const slow = isAxisSwapped() 
        ? coordinateHelpers.fromScreenY(y) 
        : coordinateHelpers.fromScreenX(x);
      const freq = isAxisSwapped() 
        ? coordinateHelpers.fromScreenX(x) 
        : coordinateHelpers.fromScreenY(y);
      
      // Update the dragged point position
      dispatch(removePoint(draggedPoint));
      const newPoint:PickData = {
        d1: 0,
        d2: 0,
        frequency: freq,
        d3: 0,
        slowness: slow,
        d4: 0,
        d5: 0
      };
      dispatch(addPoint(newPoint));
      dispatch(setDraggedPoint(newPoint));
      
      // Update tooltip content for dragged point
      setTooltipContent(`(Slow:${slow.toFixed(6)}, Freq:${freq.toFixed(6)})`);
    } else {
      // Check for hovering over points
      const hovered = points.find(point => {
        // Convert slow/freq to screen coordinates for comparison
        const screenX = isAxisSwapped() 
          ? coordinateHelpers.toScreenX(point.frequency) 
          : coordinateHelpers.toScreenX(point.slowness);
        const screenY = isAxisSwapped() 
          ? coordinateHelpers.toScreenY(point.slowness) 
          : coordinateHelpers.toScreenY(point.frequency);
        
        const distance = Math.sqrt(
          Math.pow(screenX - x, 2) + Math.pow(screenY - y, 2)
        );
        return distance < 10;
      });
      
      dispatch(setHoveredPoint(hovered || null));
      
      // Update tooltip content for hovered point
      if (hovered) {
        setTooltipContent(`(Slow:${hovered.slowness.toFixed(6)}, Freq:${hovered.frequency.toFixed(6)})`);
      } else {
        setTooltipContent('');
      }
    }
  }, [isDragging, draggedPoint, points, dispatch, plotRef, coordinateHelpers, isAxisSwapped]);
  
  const handlePointerUp = useCallback(() => {
    dispatch(setIsDragging(false));
    dispatch(setDraggedPoint(null));
  }, [dispatch]);

  const handleDownloadPoints = useCallback(() => {
    if (points.length === 0) {
      dispatch(addToast({
        message: "No points to save",
        type: "warning",
        duration: 5000
      }));
      return;
    }
    
    const pointsData = points.map(p => `${p.d1.toFixed(6)} ${p.d2.toFixed(6)} ${p.frequency.toFixed(6)} ${p.d3.toFixed(6)} ${p.slowness.toFixed(6)} ${p.d4.toFixed(6)} ${p.d5.toFixed(6)}`).join('\n');
    const blob = new Blob([pointsData], { type: 'text/plain' });
    
    // Use showSaveFilePicker API for native file save dialog
    try {
      (window as unknown as { showSaveFilePicker: (options: SaveFilePickerOptions) => Promise<FileSystemFileHandle> })
        .showSaveFilePicker({
          suggestedName: "plotted_points.pck",
          types: [
            {
              description: "Picked Points",
              accept: {
                "text/plain": [".pck"],
              },
            },
          ],
        })
        .then(async (handle: FileSystemFileHandle) => {
          const writable = await handle.createWritable();
          await writable.write(blob);
          await writable.close();
        });
    } catch (err) {
      console.error("Error saving file:", err);
      dispatch(addToast({
        message: "Failed to save file. Please try again.",
        type: "error",
        duration: 5000
      }));
      
      // Fallback to download link if native file picker fails
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "plotted_points.pck";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    }
  }, [points, dispatch]);

  const handleUploadPoints = useCallback(async () => {
    try {
      const [fileHandle] = await (window as unknown as { showOpenFilePicker: (options: FilePickerOptions) => Promise<FileHandle[]> })
        .showOpenFilePicker({
          types: [
            {
              description: "Picked Points",
              accept: {
                "text/plain": [".pck"],
              },
            },
          ],
          multiple: false,
        });
      
      const file = await fileHandle.getFile();
      const content = await file.text();
      
      const lines = content.trim().split('\n');
      const newPoints: PickData[] = [];
      
      for (const line of lines) {
        const values = line.split(' ').map((val) => parseFloat(val.trim()));
        
        if (values.length >= 7) {
          const point: PickData = {
            d1: values[0],
            d2: values[1],
            frequency: values[2],
            d3: values[3],
            slowness: values[4],
            d4: values[5],
            d5: values[6]
          };
          newPoints.push(point);
        }
      }
      
      if (newPoints.length === 0) {
        dispatch(addToast({
          message: "No valid points found in file",
          type: "warning",
          duration: 5000
        }));
        return;
      }
      
      if (points.length > 0) {
        setPendingNewPoints(newPoints);
        setShowUploadConfirmation(true);
      } else {
        dispatch(setPoints(newPoints));
        dispatch(addToast({
          message: `Successfully loaded ${newPoints.length} points`,
          type: "success",
          duration: 5000
        }));
      }
      
    } catch (err) {
      console.error("Error uploading file:", err);
      
      if ((err as Error).name !== 'AbortError') {
        dispatch(addToast({
          message: "Failed to upload file. Please try again.",
          type: "error",
          duration: 5000
        }));
      }
      
      try {
        const input = document.createElement('input');
        input.type = 'file';
        input.accept = '.pck';
        
        input.onchange = async (e) => {
          const target = e.target as HTMLInputElement;
          if (!target.files || target.files.length === 0) return;
          
          const file = target.files[0];
          const reader = new FileReader();
          
          reader.onload = (event) => {
            const content = event.target?.result as string;
            const lines = content.trim().split('\n');
            const newPoints: PickData[] = [];
            
            for (const line of lines) {
              const values = line.split(',').map(val => parseFloat(val.trim()));
              
              if (values.length >= 7) {
                const point: PickData = {
                  d1: values[0],
                  d2: values[1],
                  frequency: values[2],
                  d3: values[3],
                  slowness: values[4],
                  d4: values[5],
                  d5: values[6]
                };
                newPoints.push(point);
              }
            }
            
            if (newPoints.length === 0) {
              dispatch(addToast({
                message: "No valid points found in file",
                type: "warning",
                duration: 5000
              }));
              return;
            }

            dispatch(setPoints(newPoints))

            dispatch(addToast({
              message: `Successfully loaded ${newPoints.length} points`,
              type: "success",
              duration: 5000
            }));
          };
          
          reader.readAsText(file);
        };
        
        input.click();
      } catch (fallbackErr) {
        console.error("Fallback upload method failed:", fallbackErr);
      }
    }
  }, [dispatch, points]);

  const handleMergePoints = useCallback(() => {
    if (pendingNewPoints.length > 0) {
      const mergedPoints = [...points, ...pendingNewPoints];
      dispatch(setPoints(mergedPoints));
      dispatch(addToast({
        message: `Added ${pendingNewPoints.length} points to existing ${points.length} points`,
        type: "success",
        duration: 5000
      }));
      setPendingNewPoints([]);
      setShowUploadConfirmation(false);
    }
  }, [dispatch, points, pendingNewPoints]);

  const handleReplacePoints = useCallback(() => {
    if (pendingNewPoints.length > 0) {
      dispatch(setPoints(pendingNewPoints));
      dispatch(addToast({
        message: `Replaced existing points with ${pendingNewPoints.length} new points`,
        type: "success",
        duration: 5000
      }));
      setPendingNewPoints([]);
      setShowUploadConfirmation(false);
    }
  }, [dispatch, pendingNewPoints]);

  const handleSavePoints = () => {
    dispatch(savePicksByProjectId(projectId))
  }

  // Add a new handler function for clearing all points
  const handleClearPoints = useCallback(() => {
    if (points.length === 0) {
      dispatch(addToast({
        message: "No points to clear",
        type: "info",
        duration: 3000
      }));
      return;
    }
    
    dispatch(setPoints([]));
    dispatch(addToast({
      message: "All points cleared",
      type: "success",
      duration: 3000
    }));
  }, [dispatch, points.length]);

  useEffect(() => {
    if (!isInitialized) return;
    
    if (enabledRecordCount === 0) {
      setTexture(null);
      dispatch(setIsLoading(false));
      return;
    }
    
    dispatch(setIsLoading(true));
    
    console.log("Transformations Changed", transformations);
    console.log("Before:", coordinateMatrix);
    const newCoordinate = applyTransformation(ORIGINAL_COORDINATE_MATRIX, transformations);
    if (transformations.length !== 0 && areMatricesEqual(newCoordinate, ORIGINAL_COORDINATE_MATRIX)) {
      dispatch(emptyTransformations());
      console.log("The transforms is reset");
    }
    console.log("New:", newCoordinate);
    dispatch(setCoordinateMatrix(newCoordinate));
    // Create weighted texture from selected records
    const createWeightedTexture = async () => {
      try {
        const totalWeight = enabledRecords.reduce(
          (total: number, item) => total + item.weight,
          0
        );
        if (totalWeight === 0) {
          dispatch(addToast({ message: "Total weight is 0, cannot create weighted texture", type: "warning", duration: 5000 }));
          return;
        }
        // Get the dimensions from the first record
        const shape = getMatrixShape(enabledRecords[0].data as Matrix);
        const width = shape[1];
        const height = shape[0];
       
        // Create empty matrix with proper dimensions
        let mainMatrix: Matrix = Array.from(
          { length: height }, 
          () => Array(width).fill(0)
        );

        // Properly accumulate weighted values
        for (const record of enabledRecords) {
          const recordMatrix = record.data as Matrix;
          
          for (let i = 0; i < height; i++) {
            for (let j = 0; j < width; j++) {
              mainMatrix[i][j] += recordMatrix[i][j] * record.weight / totalWeight;
            }
          }
        }
        if (mainMatrix.length === 0) {
          dispatch(addToast({ message: "No data to create texture", type: "warning", duration: 5000 }));
          return;
        }
        if (transformations.length !== 0) {
          mainMatrix = applyTransformation(mainMatrix, transformations);
        }
        // Calculate min/max from the weighted data for better visualization
        const flatMatrix = mainMatrix.flat();
        const min = Math.min(...flatMatrix);
        const max = Math.max(...flatMatrix);
        // Convert back to flat array for texture creation
        const mainRecord = flatMatrix;
        const newTexture = createTexture(
          mainRecord,
          enabledRecords[0].dimensions,
          { min, max }, // Use calculated min/max instead of from first record
          colorMaps[selectedColorMap]
        );
        
        setTexture(newTexture);
      } catch (error) {
        console.error("Error creating texture:", error);
        dispatch(addToast({
          message: "Failed to create texture from data",
          type: "error",
          duration: 7000
        }));
      } finally {
        dispatch(setIsLoading(false));
      }
    };
    
    createWeightedTexture();
  }, [enabledRecords, selectedColorMap, colorMaps, dispatch, transformations]);

  useEffect(() => {
    console.log("Coordinates:", coordinateMatrix)
    console.log("Points:", points)
    console.log("Tooltip:", tooltipContent)
  }, [coordinateMatrix, points, tooltipContent])

  // Return loading state if not initialized
  if (!isInitialized) {
    return (
      <div className="d-flex flex-column border rounded h-100 justify-content-center align-items-center">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <div className="mt-2">Initializing data...</div>
      </div>
    );
  }

  return (
    <div className="card shadow-sm mb-4">
      <SectionHeader title="Main Plot">
        <div className="d-flex gap-2">
          <button 
            className="btn btn-outline-secondary btn-sm"
            onClick={handleSavePoints}
          >
            Save Picks
          </button>
          <button 
            className="btn btn-outline-secondary btn-sm"
            onClick={handleUploadPoints}
          >
            Upload Picks
          </button>
          <button 
            className="btn btn-outline-secondary btn-sm"
            onClick={handleDownloadPoints}
            disabled={points.length === 0}
          >
            Download Picks
          </button>
        </div>
      </SectionHeader>
      <div className="card-body p-0">
        <div className="row g-0">
          <div className="col-lg-9">
            <div className="aspect-ratio-container">
              <div className="plot-container">
                {isLoading ? (
                  <div className="d-flex align-items-center justify-content-center h-100">
                    <div className="spinner-border text-primary" role="status">
                      <span className="visually-hidden">Loading...</span>
                    </div>
                  </div>
                ) : texture ? (
                  <BasePlot
                    ref={plotRef}
                    xLabel={isAxisSwapped() ? "Frequency" : "Slowness"}
                    yLabel={isAxisSwapped() ? "Slowness" : "Frequency"}
                    xMax={right()}
                    xMin={left()}
                    yMin={bottom()}
                    yMax={top()}
                    display={(value) => value.toFixed(3)}
                    onPointerMove={handlePointerMove}
                    onPointerUp={handlePointerUp}
                    onPointerDown={handlePointerDown}
                    onDimensionChange={handleDimensionChange}
                    tooltipContent={tooltipContent}
                  >
                    <pixiContainer>
                      {texture && (
                        <pixiSprite
                          texture={texture}
                          width={plotDimensions.width}
                          height={plotDimensions.height}
                          anchor={0}
                        />
                      )}
                      <pixiGraphics
                        draw={(g) => {
                          g.clear();

                          points.forEach((point) => {
                            const isHovered = hoveredPoint === point;
                            const isDragged = draggedPoint === point;
                            
                            const screenX = isAxisSwapped() 
                              ? coordinateHelpers.toScreenX(point.frequency) 
                              : coordinateHelpers.toScreenX(point.slowness);
                            const screenY = isAxisSwapped() 
                              ? coordinateHelpers.toScreenY(point.slowness) 
                              : coordinateHelpers.toScreenY(point.frequency);
                            
                            g.setFillStyle({
                              color: isHovered || isDragged ? 0x00ff00 : 0xff0000,
                              alpha: 0.8,
                            });
                            
                            g.circle(
                              screenX,
                              screenY,
                              isHovered || isDragged ? 6 : 4
                            );
                            g.fill();
                          });
                        }}
                      />
                    </pixiContainer>
                  </BasePlot>
                ) : (
                  <div className="d-flex align-items-center justify-content-center h-100">
                    <p className="text-muted">No data selected</p>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          {/* Controls Panel */}
          <div className="col-lg-3 border-start">
            <div className="p-3">
              <h6 className="mb-3">Plot Controls</h6>
              
              {/* ColorMap Controls */}
              <div className="mb-3">
                <label className="form-label">Color Map</label>
                <ColorMapManager/>
              </div>

              {/* Transform Controls */}
              <div className="mb-3">
                <label className="form-label">Transform</label>
                <div className="d-flex flex-wrap gap-2 justify-content-between">
                <button
                  onClick={() => {
                    dispatch(addTransformation("rotateCounterClockwise"));
                  }}
                  className="btn btn-outline-primary btn-sm"
                  title="Rotate Counter-clockwise"
                  disabled={isLoading || !texture}
                >
                  <span>↺</span>
                </button>
                <button
                  onClick={() => {
                    dispatch(addTransformation("rotateClockwise"));
                  }}
                  className="btn btn-outline-primary btn-sm"
                  title="Rotate Clockwise"
                  disabled={isLoading || !texture}
                >
                  <span>↻</span>
                </button>
                <button
                  onClick={() => {
                    // eslint-disable-next-line @typescript-eslint/no-unused-expressions
                    isAxisSwapped()? dispatch(addTransformation("flipHorizontal")):dispatch(addTransformation("flipVertical"));
                  }}
                  className="btn btn-outline-primary btn-sm"
                  title="Flip Horizontal"
                  disabled={isLoading || !texture}
                >
                  <span>↔</span>
                </button>
                <button
                  onClick={() => {
                    // eslint-disable-next-line @typescript-eslint/no-unused-expressions
                    isAxisSwapped()? dispatch(addTransformation("flipVertical")):dispatch(addTransformation("flipHorizontal"));
                  }}
                  className="btn btn-outline-primary btn-sm"
                  title="Flip Vertical"
                  disabled={isLoading || !texture}
                >
                  <span>↕</span>
                </button>
                </div>
              </div>
              
              {/* Action Buttons */}
              <div className="d-grid gap-2 mt-4">
                <button 
                  className="btn btn-outline-danger btn-sm"
                  onClick={handleClearPoints}
                  disabled={points.length === 0}
                >
                  Clear All Picks
                </button>
              </div>
              
              {/* Points Info */}
              {points.length > 0 && (
                <div className="mt-3">
                  <small className="text-muted d-block mb-1">
                    {points.length} point{points.length !== 1 ? 's' : ''} added
                  </small>
                  <small className="text-muted d-block">
                    Shift+Click: Add point<br/>
                    Alt+Click: Remove point
                  </small>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      <ConfirmationModal
        isOpen={showUploadConfirmation}
        title="Upload Points"
        message={`You have ${points.length} existing points. Do you want to add the ${pendingNewPoints.length} new points to them or replace them?`}
        onConfirm={handleMergePoints}
        onCancel={() => setShowUploadConfirmation(false)}
        onAlternative={handleReplacePoints}
        confirmText="Add to Existing"
        cancelText="Cancel"
        alternativeText="Replace Existing"
      />
    </div>
  );
}
