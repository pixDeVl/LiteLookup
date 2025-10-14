from fastapi import FastAPI
from typing import Union
import lookup
from fastapi import HTTPException
from models import Punishment, DataResponse, Username

app = FastAPI()




@app.get(
    "/punishments/username/{username}",
    responses={
        404: {
            "description": "Record Not Found",
            "content": {
                "application/json": {
                    "examples": {
                        "No UUID found": {
                            "value": {"detail": "ERR_PLAYER_NO_UUID"},
                            "description": "No UUID could be found for this username.",
                        },
                        "Player hasn't joined": {
                            "value": {"detail": "ERR_PLAYER_NEVER_JOIN"},
                            "description": "This player has never joined the server.",
                        },
                    }
                }
            },
        }
    },
)
def read_item(username: Username) -> DataResponse:
    """
    Retrieves punishment data for a given username. 
    Returns an overview with the current punishment `status` of the account, and the full known `history` of moderations.
    """
    data = lookup.getPunishments(username=username)
    if isinstance(data, Exception):
        raise HTTPException(status_code=500, detail=data)
    return DataResponse(
        username=username,
        uuid=data["uuid"],
        status=data["status"],
        history=data["history"],
    )
