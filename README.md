# Congress Fahrplan Bot for Matrix

A very simple [matrix] bot to announce and query current [congress events][fahrplan].  
Should be compatible with any [frab] JSON export.

[matrix]: https://matrix.org/
[fahrplan]: https://fahrplan.events.ccc.de/
[frab]: https://github.com/frab/frab

# How to install

`pipenv install`

# How to configure

Set these environment vars:

- `BOT_HOMESERVER`, e.g. `https://matrix.example.org`
- `BOT_PASSWORD`, e.g. `you'll never gonna guess this one`
- `BOT_ROOMS`, e.g. `#spam:matrix.example.org #congress:matrix.example.org`
- `BOT_SCHEDULES`, e.g. `data/schedules/36c3-main.json data/schedules/36c3-chaos-west.json`
- `BOT_USERID`, e.g. `@fahrplan:matrix.example.org`

Best practive is to put all of these into a local `.env` file which you load whenever the bot is started.

# How to run

To run the bot, run `python main.py`.  
To run the bot with a local env file like suggested above, use something like `(. ./.env; python main.py)`.

# Where to get schedules

You'll have to look for links to schedules yourself.  Any [frab] compatible JSON export should do.  
For convenience a script to download the schedules for 36c3 is included at `data/schedules/download.sh`.  
To download and use these schedules, `cd data/schedules && ./download.sh`.
