from enum import Enum
from fastapi import HTTPException
from tereancore.utils import RE_COMBINE_WHITESPACE
from LengthUnit import LengthUnit


class Asce722(str, Enum):
    A = "A"
    B = "B"
    BC = "BC"
    C = "C"
    CD = "CD"
    D = "D"
    DE = "DE"
    E = "E"

    @classmethod
    def from_vel(cls, velocity: float, unit: LengthUnit | None = None) -> 'Asce722':
        if unit is None or unit is LengthUnit.meters:
            return Asce722.from_vel_meters(velocity)
        elif unit is LengthUnit.feet:
            return Asce722.from_vel_feet(velocity)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported unit {unit}")

    @classmethod
    def from_vel_meters(cls, velocity: float) -> 'Asce722':
        return Asce722.from_vel_feet(velocity)

    @classmethod
    def from_vel_feet(cls, velocity: float) -> 'Asce722':
        if velocity > 5000:
            return Asce722.A  # 5000 < A
        elif velocity > 3000:
            return Asce722.B  # 3000 < B <= 5000
        elif velocity > 2100:
            return Asce722.BC  # 2100 < BC <= 3000
        elif velocity > 1450:
            return Asce722.C  # 1450 < C <= 2100
        elif velocity > 1000:
            return Asce722.CD  # 1000 < CD <= 1450
        elif velocity > 700:
            return Asce722.D  # 700 < D <= 1000
        elif velocity > 500:
            return Asce722.DE  # 500 < DE <= 700
        else:
            return Asce722.E  # E <= 500

    @classmethod
    def list_values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))

    @classmethod
    def list_values_as_string(cls, join_char: str = " ") -> str:
        return join_char.join([f"{x}" for x in Asce722.list_values()])

    @staticmethod
    def from_str(s: str) -> 'Asce722':
        # Trim all whitespace, convert to uppercase.
        s = RE_COMBINE_WHITESPACE.sub("", s).upper()
        try:
            return Asce722(s)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"{s} is not a valid option for ProjectStatus. Valid options "
                                                        f"are: {Asce722.list_values_as_string()}")
