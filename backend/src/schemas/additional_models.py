from typing import List, Union

from pydantic import BaseModel


class GeometryItem(BaseModel):
    x: float
    y: float
    z: float
    index: Union[str, int]  # Accept either string or integer

    def __json__(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "index": self.index
        }


class PlotLimits(BaseModel):
    numFreq: int
    maxFreq: float
    numSlow: int
    maxSlow: float

    def __json__(self):
        return {
            "numFreq": self.numFreq,
            "maxFreq": self.maxFreq,
            "numSlow": self.numSlow,
            "maxSlow": self.maxSlow
        }


class Layer(BaseModel):
    startDepth: float
    endDepth: float
    velocity: float
    density: float
    ignore: int

    def __json__(self):
        return {
            "startDepth": self.startDepth,
            "endDepth": self.endDepth,
            "velocity": self.velocity,
            "density": self.density,
            "ignore": self.ignore
        }


class DisperSettingsModel(BaseModel):
    displayUnits: str
    # model settings
    layers: List[Layer]
    asceVersion: str
    modelAxisLimits: dict = {
        "xmin": float,
        "xmax": float,
        "ymin": float,
        "ymax": float
    }
    # curve settings
    curveAxisLimits: dict = {
        "xmin": float,
        "xmax": float,
        "ymin": float,
        "ymax": float
    }
    numPoints: int
    velocityUnit: str
    periodUnit: str
    velocityReversed: bool
    periodReversed: bool
    axesSwapped: bool

    def __json__(self):
        return {
            "displayUnits": self.displayUnits,
            "layers": [layer.__json__() for layer in self.layers],
            "asceVersion": self.asceVersion,
            "modelAxisLimits": self.modelAxisLimits,
            "curveAxisLimits": self.curveAxisLimits,
            "numPoints": self.numPoints,
            "velocityUnit": self.velocityUnit,
            "periodUnit": self.periodUnit,
            "velocityReversed": self.velocityReversed,
            "periodReversed": self.periodReversed,
            "axesSwapped": self.axesSwapped
        }


class RecordOption(BaseModel):
    id: str
    enabled: bool
    weight: float
    fileName: str

    def __json__(self):
        return {
            "id": self.id,
            "enabled": self.enabled,
            "weight": self.weight,
            "fileName": self.fileName
        }


class PickData(BaseModel):
    d1: float
    d2: float
    frequency: float
    d3: float
    slowness: float
    d4: float
    d5: float

    def __json__(self):
        return {
            "d1": self.d1,
            "d2": self.d2,
            "frequency": self.frequency,
            "d3": self.d3,
            "slowness": self.slowness,
            "d4": self.d4,
            "d5": self.d5
        }


class Grid(BaseModel):
    name: str
    data: list
    shape: list

    def __json__(self):
        return {
            "name": self.name,
            "data": self.data,
            "shape": self.shape
        }


class OptionsModel(BaseModel):
    geometry: List[GeometryItem]
    records: List[RecordOption]
    plotLimits: PlotLimits

    def __json__(self):
        return {
            "geometry": [item.__json__() for item in self.geometry],
            "records": [record.__json__() for record in self.records],
            "plotLimits": self.plotLimits.__json__()
        } 