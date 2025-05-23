import { Application } from "@pixi/react";
import { ReactNode, useEffect, useState, forwardRef, useCallback, useMemo } from "react";
import { Tooltip } from "../ToolTip/ToolTip";

interface BasePlotProps {
  children: ReactNode;
  xLabel?: string;
  yLabel?: string;
  xMin?: number;
  xMax?: number;
  yMin?: number;
  yMax?: number;
  display?: (value:number) => string;
  tooltipContent?: string;
  axesSwapped?: boolean;
  xAxisReversed?: boolean;
  yAxisReversed?: boolean;
  onPointerMove?: (event: React.PointerEvent) => void;
  onPointerUp?: () => void;
  onPointerDown?: (event: React.PointerEvent) => void;
  plotDimensions?: { width: number; height: number };
}

export const BasePlot = forwardRef<HTMLDivElement, BasePlotProps>(({
  children,
  xLabel,
  yLabel,
  xMin,
  xMax,
  yMin,
  yMax,
  display,
  tooltipContent,
  onPointerMove,
  onPointerUp,
  onPointerDown,
  axesSwapped = false,
  xAxisReversed = false,
  yAxisReversed = false,
  plotDimensions = { width: 640, height: 480 },
}, ref) => {

  const [isFullyMounted, SetIsFullyMounted] = useState(false);
  const [cursorPosition, setCursorPosition] = useState<{ x: number; y: number } | null>(null);

  const handlePointerMove = useCallback((event: React.PointerEvent) => {
    if (!ref || !('current' in ref) || !ref.current) return;
    
    const rect = ref.current.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    setCursorPosition({ x, y });
    if (onPointerMove) {
      onPointerMove(event);
    }
  }, [ref, onPointerMove]);

  const getDisplayedXLabel = useCallback(() => {
    return axesSwapped ? yLabel : xLabel;
  }, [axesSwapped, xLabel, yLabel]);

  const getDisplayedYLabel = useCallback(() => {
    return axesSwapped ? xLabel : yLabel;
  }, [axesSwapped, xLabel, yLabel]);

  const getDisplayedXMin = useCallback(() => {
    if (axesSwapped) {
      return yAxisReversed ? yMax : yMin;
    } else {
      return xAxisReversed ? xMax : xMin;
    }
  }, [axesSwapped, xMin, xMax, yMin, yMax, xAxisReversed, yAxisReversed]);

  const getDisplayedXMax = useCallback(() => {
    if (axesSwapped) {
      return yAxisReversed ? yMin : yMax;
    } else {
      return xAxisReversed ? xMin : xMax;
    }
  }, [axesSwapped, xMin, xMax, yMin, yMax, xAxisReversed, yAxisReversed]);

  const getDisplayedYMin = useCallback(() => {
    if (axesSwapped) {
      return xAxisReversed ? xMax : xMin;
    } else {
      return yAxisReversed ? yMax : yMin;
    }
  }, [axesSwapped, xMin, xMax, yMin, yMax, xAxisReversed, yAxisReversed]);

  const getDisplayedYMax = useCallback(() => {
    if (axesSwapped) {
      return xAxisReversed ? xMin : xMax;
    } else {
      return yAxisReversed ? yMin : yMax;
    }
  }, [axesSwapped, xMin, xMax, yMin, yMax, xAxisReversed, yAxisReversed]);

  const displayedValues = useMemo(() => ({
    xLabel: getDisplayedXLabel(),
    yLabel: getDisplayedYLabel(),
    xMin: getDisplayedXMin(),
    xMax: getDisplayedXMax(),
    yMin: getDisplayedYMin(),
    yMax: getDisplayedYMax()
  }), [
    getDisplayedXLabel, getDisplayedYLabel,
    getDisplayedXMin, getDisplayedXMax,
    getDisplayedYMin, getDisplayedYMax
  ]);

  useEffect(() => {
    SetIsFullyMounted(true);
  }, [plotDimensions]);

  return (
    <div
      className="position-relative border"
      style={{width: plotDimensions.width, height:plotDimensions.height}}
    >
      <div 
        className="position-absolute small" 
        style={{
          right: plotDimensions.width - 25,
          top: '50%',
          transform: 'translateY(-50%) rotate(-90deg)',
          width: '100px'
        }}
      >
        {displayedValues.yLabel}
      </div>
      
      {/* Y-axis values */}
      <div className="position-absolute h-100 d-flex flex-column justify-content-between align-items-center" 
           style={{ right: plotDimensions.width + 5, top: '0' }}>
        <div className="small">{displayedValues.yMax !== undefined && display ? display(displayedValues.yMax) : ''}</div>
        <div className="small">{displayedValues.yMin !== undefined && display ? display(displayedValues.yMin) : ''}</div>
      </div>
      
      {/* X-axis label */}
      <div className="position-absolute small text-center w-100" style={{ bottom: '-25px' }}>
        {displayedValues.xLabel}
      </div>
      
      {/* X-axis values */}
      <div className="position-absolute w-100 d-flex justify-content-between" 
           style={{ bottom: '-25px'}}>
        <div className="small">{displayedValues.xMin !== undefined && display ? display(displayedValues.xMin) : ''}</div>
        <div className="small">{displayedValues.xMax !== undefined && display ? display(displayedValues.xMax) : ''}</div>
      </div>
      
      <div 
        style={{width: plotDimensions.width, height:plotDimensions.height}}
        onPointerMove={handlePointerMove}
        onPointerUp={onPointerUp}
        onPointerDown={onPointerDown}
        ref={ref}
      >
        {isFullyMounted && ref && 'current' in ref && ref.current ? (
          <Application
            // width={ref.current.getBoundingClientRect().width}
            // height={ref.current.getBoundingClientRect().height}
            width={plotDimensions.width}
            height={plotDimensions.height}
            background="white"
            resizeTo={ref.current}
            autoDensity={true}
            resolution={window.devicePixelRatio || 1}
            antialias={false}
          >
            {children}
          </Application>
        ): <div className="flex-1 spinner-border spinner-border-sm text-primary"></div>}

        <Tooltip
          x={cursorPosition?.x ?? 0}
          y={cursorPosition?.y ?? 0}
          content={tooltipContent ?? ''}
          visible={!!cursorPosition && !!tooltipContent}
        />
      </div>
    </div>
  );
});
