import re
from enum import Enum
from fastapi import HTTPException
from tereancore.utils import RE_COMBINE_WHITESPACE


class LengthUnit(str, Enum):
    meters = "m"
    feet = "ft"

    @classmethod
    def _missing_(cls, value):
        print(f"MISSING CALLED with value {value}")
        if isinstance(value, str):
            try:
                return LengthUnit.from_str(value)
            except ValueError:
                return None
        return None
    
    @classmethod
    def list_values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))

    @classmethod
    def list_values_as_string(cls, join_char=" ") -> str:
        return join_char.join([f"{x}" for x in LengthUnit.list_values()])

    @staticmethod
    def from_str(s: str) -> 'LengthUnit':
        print(f"FROM STR CALLED with value {s}")
        s = RE_COMBINE_WHITESPACE.sub(" ", s).strip().replace(" ", "_").lower()
        print(f"After update: {s}")
        foot_matcher = re.compile(r'(?i)^f(?:ee)*t')
        meter_matcher = re.compile(r'(?i)m(?:eter)*s*')
        if foot_matcher.match(s) is not None:
            print("MATCHED FOOT")
            return LengthUnit.feet
        elif meter_matcher.match(s) is not None:
            print("MATCHED METER")
            return LengthUnit.meters
        else:
            raise HTTPException(status_code=400, detail=f"{s} is not a valid option for ProjectStatus. Valid options "
                                                        f"are: {LengthUnit.list_values_as_string()}")
