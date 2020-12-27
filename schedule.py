from bisect import bisect_left, bisect_right
from collections import defaultdict
from functools import lru_cache
from typing import Sequence, Mapping, Optional, Tuple
from urllib.parse import urljoin
import json

import pendulum

Event = Mapping
Timetable = Sequence[Event]


@lru_cache()
def fahrplan(filepath) -> Timetable:
    with open(filepath) as fp:
        schedule = json.load(fp)

    timetable = [
        event
        for day in schedule["schedule"]["conference"]["days"]
        for room in day["rooms"].values()
        for event in room
    ]
    timetable.sort(key=lambda e: e["date"])

    # fix URLs
    base_url = schedule["schedule"]["base_url"]
    confid = schedule["schedule"]["conference"]["acronym"]
    roomstreamurls = {
        "Ada": f"https://streaming.media.ccc.de/{confid}/halla",
        "Borg": f"https://streaming.media.ccc.de/{confid}/hallb",
        "Clarke": f"https://streaming.media.ccc.de/{confid}/hallc",
        "Dijkstra": f"https://streaming.media.ccc.de/{confid}/halld",
        "Eliza": f"https://streaming.media.ccc.de/{confid}/halle",
        "Chaos-West Bühne": f"https://streaming.media.ccc.de/{confid}/chaoswest",
        # rC3
        "rC1": f"https://streaming.media.ccc.de/{confid}/one",
        "rC2": f"https://streaming.media.ccc.de/{confid}/two",
        "restrealitaet": f"https://streaming.media.ccc.de/{confid}/restrealitaet",
        "chaosstudio-hamburg": f"https://streaming.media.ccc.de/{confid}/chaosstudio-hamburg",
        "ChaosTrawler": f"https://streaming.media.ccc.de/{confid}/chaostrawler",
        "r3s - Monheim/Rhein": f"https://streaming.media.ccc.de/{confid}/r3s",
        "franconian.net": f"https://streaming.media.ccc.de/{confid}/franconiannet",
        "Chaos-West TV": f"https://streaming.media.ccc.de/{confid}/cwtv",
        "hacc München / about:future": f"https://streaming.media.ccc.de/{confid}/hacc",
        "xHain Berlin": f"https://streaming.media.ccc.de/{confid}/xhain",
        "c-base Berlin": f"https://streaming.media.ccc.de/{confid}/cbase",
        "Bitwäscherei Zürich": f"https://streaming.media.ccc.de/{confid}/bitwaescherei",
        "KreaturWorks": f"https://streaming.media.ccc.de/{confid}/kreaturworks",
        "ChaosZone TV Stream": f"https://streaming.media.ccc.de/{confid}/chaoszone",
        "OIO/A:F Bühne": f"https://streaming.media.ccc.de/{confid}/oio",
        "SZ Bühne": f"https://streaming.media.ccc.de/{confid}/sendezentrum",
        "Wikipaka": f"https://streaming.media.ccc.de/{confid}/wikipaka",
    }
    for event in timetable:
        for field in "url", "logo":
            event[field] = urljoin(base_url, event[field]) if event.get(field) else None
        for link in event.get("links", []):
            link["url"] = urljoin(base_url, link["url"]) if link["url"] else None
        for attachment in event.get("attachments", []):
            attachment["url"] = (
                urljoin(base_url, attachment["url"]) if attachment["url"] else None
            )
        for person in event.get("persons", []):
            if "code" in person:
                # support for chaos-west
                personurl = f'../speaker/{person["code"]}/'
            else:
                personurl = f'speakers/{person["id"]}.html'
            person["url"] = urljoin(base_url, personurl)
        event["stream_url"] = roomstreamurls.get(event["room"])

    return timetable


def rooms(timetable: Timetable):
    return set(event["room"] for event in timetable)


def now() -> pendulum.DateTime:
    return pendulum.now("Europe/Berlin")


def ttindex(timetable, at_time=None):
    if at_time is None:
        at_time = now()
    timestring = at_time.isoformat(timespec="seconds")
    # print(timestring)
    keys = [event["date"] for event in timetable]
    return bisect_left(keys, timestring)


def next_up(
    timetable: Timetable, within: Optional[pendulum.Duration] = None
) -> Mapping[str, Sequence[Event]]:
    now_ = now()
    in_one_hour = now_.add(hours=1) if within is None else now_ + within
    found = defaultdict(list)
    for event in timetable[ttindex(timetable, now_) : ttindex(timetable, in_one_hour)]:
        found[event["room"]].append(event)
    return found


Offline = object()


def duration(s: str) -> pendulum.Duration:
    t = pendulum.from_format(s, "H:m")
    return pendulum.duration(hours=t.hour, minutes=t.minute)


def daterange(event: Event) -> Tuple[pendulum.DateTime, pendulum.DateTime]:
    start = pendulum.parse(event["date"])
    end = start + duration(event["duration"])
    return start, end


def current(timetable: Timetable) -> Mapping[str, Event]:
    now_ = now()
    unknown = None
    found = {r: unknown for r in rooms(timetable)}
    for event in timetable[ttindex(timetable, now_) - 1 :: -1]:
        if found[event["room"]] is unknown:
            _, eventend = daterange(event)
            found[event["room"]] = event if now_ < eventend else Offline
        elif not any(r is unknown for r in found.values()):
            break
    return {r: e for r, e in found.items() if e is not Offline}
