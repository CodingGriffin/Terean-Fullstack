from datetime import datetime, timedelta

import randomname, random

from schemas import project_schema
from utils.custom_types.Priority import Priority
from utils.custom_types.ProjectStatus import ProjectStatus

random_client_list = [
    "Anglo Gold",
    "DoE",
    "UES",
    "Stanford",
    "Intertek",
    "PSI",
    "ECS",
    "Earth Tech",
    "MSTS",
    "Southwest Geo",
    "Westex",
    "Aurecon",
    "Wood Rogers",
    "Kiewitt",
]


def random_date(start, end):
    """Generate a random datetime between `start` and `end`"""
    return start + timedelta(
        # Get a random amount of seconds between `start` and `end`
        seconds=random.randint(0, int((end - start).total_seconds())),
    )


def create_dummy_project() -> project_schema.ProjectCreate:
    name = randomname.get_name()
    client = random.choice(random_client_list)
    status = random.choice(list(ProjectStatus))
    priority = random.choice(list(Priority))
    velocity = random.uniform(299.0, 7000.0)
    geophone_count = random.choice([6, 12, 24, 36, 48, 72, 96])
    geophone_spacing = random.choice([3.6576, 4.0, 7.3152, 8.0, 16.0])
    survey_date = random_date(datetime(2000, 1, 1), datetime(2025, 1, 1))
    received_date = survey_date + timedelta(hours=random.uniform(4.0, 24.0 * 10.0))
    new_project = project_schema.ProjectCreate(
        name=name,
        client=client,
        status=status,
        priority=priority,
        velocity=velocity,
        geophone_count=geophone_count,
        geophone_spacing=geophone_spacing,
        survey_date=survey_date,
        received_date=received_date,
    )
    return new_project
