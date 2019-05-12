from typing import TYPE_CHECKING, Union, cast
from . import entityrequirement
from enum import Enum, auto
import json

if TYPE_CHECKING:
    import sqlite3


class RequirementType(Enum):
    BASE = auto()

    TIMEFRAME = auto()
    RELATIVE = auto()
    TOTALS = auto()


def rebuild_requirement_from_requirement_id(requirement_id: int,
                                            db_connection: 'sqlite3.Connection') -> \
                                                                    Union['entityrequirement.EntityRequirement', None]:

    data = db_connection.execute("SELECT type,json_data FROM requirement WHERE id=?;",
                                 (requirement_id,)).fetchone()

    if data is None:
        return None

    req_type = data[0]
    data = data[1]

    return rebuild_from_data(req_type, data, requirement_id)


def rebuild_from_data(req_type: str, json_data: str, requirement_id: int = -1) -> Union['entityrequirement.EntityRequirement', None]:
    data = json.loads(json_data)

    created_requirement = None

    if req_type == RequirementType.BASE.name:
        created_requirement = entityrequirement.EntityRequirement.unserialize(data)
    elif req_type == RequirementType.TIMEFRAME.name:
        created_requirement = entityrequirement.TimeFrameRequirement.unserialize(data)
    elif req_type == RequirementType.TOTALS.name:
        created_requirement = entityrequirement.TotalsRequirement.unserialize(data)
    elif req_type == RequirementType.RELATIVE.name:
        created_requirement = entityrequirement.RelativeRequirement.unserialize(data)

    if created_requirement is not None:
        created_requirement.requirement_id = requirement_id

    return created_requirement


def store_requirement(db_connection: 'sqlite3.Connection',
                      entity_id: int,
                      requirement: entityrequirement.EntityRequirement) -> int:

    requirement_type = RequirementType.BASE

    if isinstance(requirement, entityrequirement.TimeFrameRequirement):
        requirement_type = RequirementType.TIMEFRAME
        data = cast(entityrequirement.TimeFrameRequirement, requirement).serialize()
    elif isinstance(requirement, entityrequirement.RelativeRequirement):
        requirement_type = RequirementType.RELATIVE
        data = cast(entityrequirement.RelativeRequirement, requirement).serialize()
    elif isinstance(requirement, entityrequirement.TotalsRequirement):
        requirement_type = RequirementType.TOTALS
        data = cast(entityrequirement.RelativeRequirement, requirement).serialize()
    else:
        data = requirement.serialize()

    updated_row = db_connection.execute("INSERT INTO requirement(entity_id, type, json_data) VALUES (?, ?, ?);",
                                        (entity_id, requirement_type.name, json.dumps(data))).lastrowid

    db_connection.commit()

    return updated_row

