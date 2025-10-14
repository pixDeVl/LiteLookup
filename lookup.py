import requests
from bs4 import BeautifulSoup
import re
from dataclasses import dataclass
from datetime import datetime
from models import Punishment, PunishTypes
import time
from fastapi import HTTPException



def getPunishments(username) -> list | str | tuple:
    APIENDPOINT = f"https://api.mojang.com/users/profiles/minecraft/"
    try:
        uuid = requests.get(f"{APIENDPOINT}{username}").json()["id"]

    except KeyError:
        raise HTTPException(
            detail="ERR_PLAYER_NO_UUID",
            status_code=404,
        )
    except Exception as e:
        raise HTTPException(detail="ERR_UUID_REQUEST_FAIL", status_code=500)

    start_time = time.time()
    html = requests.get(f"https://stoneworks.gg/bans/history.php?uuid={uuid}").text
    elapsed_time = time.time() - start_time
    soup = BeautifulSoup(html, "html.parser")
    punishments = []
    if "No punishments found." in soup.text:
        pass
    elif "has not joined before." in soup.text:
        raise HTTPException(detail="ERR_PLAYER_NEVER_JOIN", status_code=404)
    else:
        for row in soup.find("table").find("tbody").find_all("tr"):
            # print(row.prettify())
            row_list = []
            for i in row.find_all("td"):
                row_list.append(i.find("a").text)
            punishments.append(row_list)
        profile = soup.find("table").find("tbody").find("tr").find("img")["src"]
        href = soup.find("table").find("tbody").find("tr").find("a")["href"]
        match = re.search(r"id=(\d+)", href)
        id = match.group(1) if match else None
    punishment_classes = []
    for entry in punishments:
        # Parse the date string to a datetime object (UTC)
        punish_time = datetime.strptime(entry[4], "%B %d, %Y, %H:%M")
        pardoner_search = re.search(r"Unbanned by (.{3,16})\)", entry[5])
        pardoner = pardoner_search.group(1) if pardoner_search else None
        print(entry[5].split("(")[0])
        expiry = (
            None  # TODO: proper True False and None for expiry
            if entry[5].startswith("Permanent Ban")
            else (datetime.strptime(entry[5].split("(")[0].strip(), "%B %d, %Y, %H:%M"))
        )
        punishment_classes.append(
            Punishment(
                type=entry[0],
                id=id,
                username=entry[1],
                moderator=entry[2],
                reason=entry[3],
                time=punish_time,
                pardoner=pardoner,
                expired=(
                    True if expiry and expiry < datetime.now() else None
                ),  # Is this needed? Do we need expired for pardoned punishments? If not just look for (Expired)
                expiry=expiry,
            )
        )
    bans = list(filter(lambda obj: obj.type == PunishTypes.Ban, punishment_classes))
    status = None

    if bans.__len__() == 0:
        status = "UNBANNED"
    elif bans[0].expiry and bans[0].expiry > datetime.now():
        status = "TEMP_BANNED"
    elif bans[0].expiry and bans[0].expiry <= datetime.now():
        status = "UNBANNED"
    elif bans[0].expiry is None and bans[0].pardoner:
        status = "UNBANNED"
    else:
        status = "PERMA_BANNED"

    return {"history": punishment_classes, "status": status, "uuid": uuid}
