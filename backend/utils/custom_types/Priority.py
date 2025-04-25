from enum import Enum

from fastapi import HTTPException

from utils.utils import _RE_COMBINE_WHITESPACE


class Priority(str, Enum):
    very_high = "very_high"
    high = "high"
    medium = "medium"
    low = "low"
    very_low = "very_low"

    @classmethod
    def list_values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))

    @classmethod
    def list_values_as_string(cls, join_char=" ") -> str:
        return join_char.join([f"{x}" for x in Priority.list_values()])

    @staticmethod
    def from_str(s: str) -> 'Priority':
        # Trim outer whitespace, replace inner spaces with _, and convert to lowercase
        s = _RE_COMBINE_WHITESPACE.sub(" ", s).strip().replace(" ", "_").lower()
        try:
            return Priority(s)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"{s} is not a valid option for ProjectStatus. Valid options "
                                                        f"are: {Priority.list_values_as_string()}")
