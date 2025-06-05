from enum import Enum
from fastapi import HTTPException
from tereancore.utils import RE_COMBINE_WHITESPACE
from LengthUnit import LengthUnit


class Asce716(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"

    @classmethod
    def from_vel(cls, velocity: float, unit: LengthUnit | None = None) -> 'Asce716':
        if unit is None or unit is LengthUnit.meters:
            return Asce716.from_vel_meters(velocity)
        elif unit is LengthUnit.feet:
            return Asce716.from_vel_feet(velocity)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported unit {unit}")

    @classmethod
    def from_vel_meters(cls, velocity: float) -> 'Asce716':
        return Asce716.from_vel_feet(velocity)

    @classmethod
    def from_vel_feet(cls, velocity: float) -> 'Asce716':
        if velocity > 5000:
            return Asce716.A  # 5000 < A
        elif velocity > 2500:
            return Asce716.B  # 2500 < B <= 5000
        elif velocity > 1200:
            return Asce716.C  # 1200 < C <= 2500
        elif velocity > 600:
            return Asce716.D  # 600 < D <= 1200
        else:
            return Asce716.E  # E <= 600

    @classmethod
    def list_values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))

    @classmethod
    def list_values_as_string(cls, join_char: str = " ") -> str:
        return join_char.join([f"{x}" for x in Asce716.list_values()])

    @staticmethod
    def from_str(s: str) -> 'Asce716':
        # Trim all whitespace, convert to uppercase.
        s = RE_COMBINE_WHITESPACE.sub("", s).upper()
        try:
            return Asce716(s)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"{s} is not a valid option for ProjectStatus. Valid options "
                                                        f"are: {Asce716.list_values_as_string()}")
