from enum import Enum
from fastapi import HTTPException
from tereancore.utils import RE_COMBINE_WHITESPACE


class ProjectStatus(str, Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    blocked = "blocked"


    @classmethod
    def list_values(cls) -> list[str]:
        return list(map(lambda c: c.value, cls))

    @classmethod
    def list_values_as_string(cls, join_char=" ") -> str:
        return join_char.join([f"{x}" for x in ProjectStatus.list_values()])

    @staticmethod
    def from_str(s: str) -> 'ProjectStatus':
        # Trim outer whitespace, replace inner spaces with _, and convert to lowercase
        s = RE_COMBINE_WHITESPACE.sub(" ", s).strip().replace(" ", "_").lower()
        try:
            return ProjectStatus(s)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"{s} is not a valid option for ProjectStatus. Valid options "
                                                        f"are: {ProjectStatus.list_values_as_string()}")
