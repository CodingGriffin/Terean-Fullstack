import re
from enum import Enum
from fastapi import HTTPException
from tereancore.utils import RE_COMBINE_WHITESPACE


class AsceVersion(str, Enum):
    asce_716 = "ASCE 7-16"
    asce_722 = "ASCE 7-22"
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            try:
                return AsceVersion.from_str(value)
            except ValueError:
                return None
        return None

    @classmethod
    def list_values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))

    @classmethod
    def list_values_as_string(cls, join_str=", ") -> str:

        return join_str.join([f"{x}" for x in AsceVersion.list_values()])

    @staticmethod
    def from_str(s: str) -> 'AsceVersion':
        # Use regex to extract the year number
        match_regex = re.compile(r'(?i)^\s*(?:asce)*[-_\s]*7[-_\s]*([0-9]+)\s*')
        match_object = match_regex.match(s)
        try:
            if match_object is None:
                raise ValueError(f"{s} is not valid.")
            year_number = int(match_object.group(1))
            if year_number == 22:
                return AsceVersion("ASCE 7-22")
            elif year_number == 16:
                return AsceVersion("ASCE 7-16")
            else:
                raise ValueError(f"{s} is not a valid ASCE year.")
        except ValueError:
            raise HTTPException(status_code=400, detail=f"{s} is not a valid option for AsceVersion. Valid options "
                                                        f"are: {AsceVersion.list_values_as_string()}")
