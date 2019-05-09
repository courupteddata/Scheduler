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


def rebuild_requirement_from_id(requirement_id: int,
                                db_connection: 'sqlite3.Connection') -> \
        Union['entityrequirement.EntityRequirement', None]:

    data = db_connection.execute("SELECT type,json_data FROM requirement WHERE id=?;",
                                 (requirement_id,)).fetchone()

    if data is None:
        return None

    req_type = data[0]
    data = data[1]

    if req_type == RequirementType.BASE.name:
        return entityrequirement.EntityRequirement.unserialize(data)
    elif req_type == RequirementType.TIMEFRAME.name:
        return entityrequirement.TimeFrameRequirement.unserialize(data)
    elif req_type == RequirementType.TOTALS.name:
        return entityrequirement.TotalsRequirement.unserialize(data)
    elif req_type == RequirementType.RELATIVE.name:
        return entityrequirement.RelativeRequirement.unserialize(data)

    return None


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

