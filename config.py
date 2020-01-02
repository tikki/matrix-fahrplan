from dataclasses import dataclass, field
from pathlib import Path
from typing import Collection
import os
import platform


@dataclass
class _Config:
    devicename: str = f"fahrplanbot/{platform.node()}"
    homeserver: str = ""
    passwd: str = ""
    rooms: Collection[str] = field(default_factory=tuple)
    sync_token_store: Path = Path("data/sync-token")
    timetables: Collection[str] = field(default_factory=tuple)
    trigger: str = "."
    userid: str = ""


def _env():
    return {
        "homeserver": os.getenv("BOT_HOMESERVER", ""),
        "passwd": os.getenv("BOT_PASSWORD", ""),
        "rooms": os.getenv("BOT_ROOMS", "").split(" "),
        "timetables": os.getenv("BOT_SCHEDULES", "").split(" "),
        "userid": os.getenv("BOT_USERID", ""),
    }


config = _Config(**_env())
