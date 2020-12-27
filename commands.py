from typing import Callable
import asyncio

from nio import RoomMessageText, MatrixRoom
from pendulum import duration

from config import config
from schedule import fahrplan, current, next_up, daterange
import bot

timetable = sum((fahrplan(p) for p in config.timetables), [])
timetable.sort(key=lambda e: e["date"])

announced = set()


async def announce_soon(client: bot.AsyncClient) -> None:
    news = [
        event
        for events in next_up(timetable, within=duration(minutes=10)).values()
        for event in events
        if event["id"] not in announced
    ]
    if news:
        await asyncio.gather(
            *[
                client.room_send(
                    room_id=room_id,
                    message_type="m.room.message",
                    content={
                        "msgtype": "m.text",
                        "body": "Soon: "
                        + " // ".join(pretty_event(plain, event) for event in news),
                        "format": "org.matrix.custom.html",
                        "formatted_body": "Soon: "
                        + " // ".join(pretty_event(html, event) for event in news),
                    },
                )
                for room_id in bot.rooms.values()
            ]
        )
        announced.update(event["id"] for event in news)


async def reply_now_playing(
    room: MatrixRoom, event: RoomMessageText, *args: str
) -> None:
    await bot.client.room_send(
        room_id=room.room_id,
        message_type="m.room.message",
        content={
            "msgtype": "m.text",
            "body": current_events(),
            "format": "org.matrix.custom.html",
            "formatted_body": current_events(format=html),
        },
    )


async def reply_next_up(room: MatrixRoom, event: RoomMessageText, *args: str) -> None:
    await bot.client.room_send(
        room_id=room.room_id,
        message_type="m.room.message",
        content={
            "msgtype": "m.text",
            "body": next_events(),
            "format": "org.matrix.custom.html",
            "formatted_body": next_events(format=html),
        },
    )


async def reply_room_details(
    room: MatrixRoom, event: RoomMessageText, *args: str
) -> None:
    if not args:
        return
    ttroom, *_ = args
    await bot.client.room_send(
        room_id=room.room_id,
        message_type="m.room.message",
        content={
            "msgtype": "m.text",
            "body": pretty_room_details(plain, ttroom),
            "format": "org.matrix.custom.html",
            "formatted_body": pretty_room_details(html, ttroom),
        },
    )


async def reply_help(room: MatrixRoom, event: RoomMessageText, *args: str) -> None:
    await bot.client.room_send(
        room_id=room.room_id,
        message_type="m.room.message",
        content={
            "msgtype": "m.text",
            "body": "Available commands: "
            + ", ".join(f"{config.trigger}{k}" for k in bot.commands),
        },
    )


def b(s: str) -> str:
    return f"<strong>{s}</strong>"


def i(s: str) -> str:
    return f"<i>{s}</i>"


def br(s: str) -> str:
    return "<br/>"


def link(text: str, href: str) -> str:
    if href is None:
        return text
    return f'<a href="{href}">{text}</a>'


def img(src: str) -> str:
    return f'<img src="{src}"/>'


def html(type, content: str, *args) -> str:
    return type(content, *args)


def plain(type, content: str, *args) -> str:
    return content


def pretty_person(format: Callable, person) -> str:
    return format(link, person["public_name"], person["url"])


def pretty_event_details(format: Callable, event) -> str:
    start, end = [d.format("HH:mm") for d in daterange(event)]
    return (
        format(
            link,
            format(b, f'{event["title"].strip()}') + f': {event["subtitle"].strip()}',
            event["url"],
        )
        + (format(br, "\n") + format(i, event["abstract"]))
        + format(br, "\n")
        + (
            format(br, "\n")
            + f"From {start} until {end}, in room {format(link, event['room'], event['stream_url'])}."
        )
        + (
            format(br, "\n")
            + "Speakers: "
            + ", and ".join(pretty_person(format, p) for p in event["persons"])
        )
        + (
            (format(br, "\n") + img(event["logo"]))
            if format is html and event["logo"]
            else ""
        )
        + (
            (format(br, "\n") + b("This talk will not be broadcast!"))
            if event["do_not_record"]
            else ""
        )
    )


def pretty_room_details(format: Callable, room: str) -> str:
    event = current(timetable).get(room.capitalize())
    if event is None:
        events = next_up(timetable, within=duration(hours=2)).get(
            room.capitalize(), [None]
        )
        event = events[0]
    if event is None:
        return f"Unknown room name (or no upcoming event in): {room}"
    return pretty_event_details(format, event)


def pretty_event(format: Callable, event) -> str:
    start, end = [d.format("HH:mm") for d in daterange(event)]
    return (
        format(link, format(b, event["title"].strip()), event["url"])
        + f" ({start} ⇥ {end}, {format(link, event['room'], event['stream_url'])})"
    )


def current_events(format: Callable = plain) -> str:
    return "Now playing: " + " // ".join(
        pretty_event(format, event)
        for _, event in sorted(current(timetable).items())
        if event is not None
    )


def next_events(format: Callable = plain) -> str:
    return "Coming next: " + " // ".join(
        pretty_event(format, events[0])
        for _, events in sorted(next_up(timetable, within=duration(hours=2)).items())
    )
