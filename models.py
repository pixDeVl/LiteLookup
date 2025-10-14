from typing import Annotated, Optional
from pydantic import BaseModel, StringConstraints
from datetime import datetime
from uuid import UUID
from enum import Enum
Username = Annotated[str, StringConstraints(pattern=r'^[a-zA-Z0-9_]{3,16}$')]
class PunishTypes(Enum):
    Ban = "Ban"
    Mute = "Mute"
    Warn = "Warn"
    Kick = "Kick"

class PlayerStatus(Enum):
    FREE = "UNBANNED"
    TEMP_BANNED = "TEMP_BANNED"
    PERMA_BAN = "PERMA_BANNED"
class Punishment(BaseModel):
    type: PunishTypes
    id: int
    username: Username
    moderator: Username
    reason: str
    time: datetime
    expiry: datetime | bool | None = None # datetime = temp ban, bool(False) = perma, None for N/A ie Kick
    pardoner: Username | None = None
    expired: bool | None = None


class DataResponse(BaseModel):
    username: Username
    uuid: UUID
    status: PlayerStatus
    history: list[Punishment]