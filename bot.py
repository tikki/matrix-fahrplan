from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Collection, Dict, NoReturn, Optional
import asyncio
import platform

from nio import AsyncClient, RoomMessageText, MatrixRoom, SyncResponse

from config import config


client = AsyncClient(config.homeserver, config.userid, device_id=config.devicename)

commands = {}
live = set()
rooms = {}


async def command_dispatcher(room: MatrixRoom, event: RoomMessageText):
    if not event.body.startswith(config.trigger):
        return
    command_line: str = event.body[len(config.trigger) :]
    command, *args = command_line.split()
    if command in commands:
        print(f"{room.user_name(event.sender)}@{room.display_name} > '{command_line}'")
        await commands[command](room, event, *args)


async def store_sync_token(event: SyncResponse):
    config.sync_token_store.write_text(event.next_batch)


def sync_token() -> Optional[str]:
    try:
        return config.sync_token_store.read_text()
    except FileNotFoundError:
        return None


async def live_forever() -> NoReturn:
    while True:
        await asyncio.gather(*[func(client) for func in live])
        await asyncio.sleep(1)


async def run() -> NoReturn:
    client.add_event_callback(command_dispatcher, RoomMessageText)
    client.add_response_callback(store_sync_token, SyncResponse)

    r = await client.login(config.passwd)
    print(r)
    r = await asyncio.gather(*[client.join(room) for room in config.rooms])
    rooms.update({room: resp.room_id for room, resp in zip(config.rooms, r)})
    # print(r)
    try:
        await asyncio.gather(
            live_forever(),
            client.sync_forever(
                timeout=30_000,
                since=sync_token(),
                sync_filter={"room": {"timeline": {"limit": 1}}},
                full_state=True,
            ),
        )
    except:
        await client.close()
        raise
