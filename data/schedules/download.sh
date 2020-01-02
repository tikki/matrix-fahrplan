#!/bin/sh

echo Downloading schedules for 36c3.
curl --progress-bar -o 36c3-main.json https://fahrplan.events.ccc.de/congress/2019/Fahrplan/schedule.json
curl --progress-bar -o 36c3-chaos-west.json https://fahrplan.chaos-west.de/36c3/schedule/export/schedule.json
