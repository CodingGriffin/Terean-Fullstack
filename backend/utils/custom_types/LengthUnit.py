from enum import Enum
from fastapi import HTTPException
from tereancore.utils import RE_COMBINE_WHITESPACE


class LengthUnit(str, Enum):
    meters = "m"
    feet = "ft"

    @classmethod
    def list_values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))

    @classmethod
    def list_values_as_string(cls, join_char=" ") -> str:
        return join_char.join([f"{x}" for x in LengthUnit.list_values()])

    @staticmethod
    def from_str(s: str) -> 'LengthUnit':
        # Trim outer whitespace, replace inner spaces with _, and convert to lowercase
        s = RE_COMBINE_WHITESPACE.sub(" ", s).strip().replace(" ", "_").lower()
        try:
            return LengthUnit(s)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"{s} is not a valid option for ProjectStatus. Valid options "
                                                        f"are: {LengthUnit.list_values_as_string()}")
