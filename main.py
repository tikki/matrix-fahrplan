import asyncio

import bot
import commands


async def main():
    bot.commands.update(
        {
            "help": commands.reply_help,
            "next": commands.reply_next_up,
            "now": commands.reply_now_playing,
            "room": commands.reply_room_details,
        }
    )
    bot.live.add(commands.announce_soon)
    await bot.run()
    # print(commands.current_events(format=commands.html))
    # print(commands.next_events(format=commands.html))
    # print(commands.pretty_room_details(commands.html, "ada"))


asyncio.run(main())
