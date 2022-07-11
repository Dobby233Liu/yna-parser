import ynaparser
import ynaparser.fake_discord
y = ynaparser.YnaRootContext(ynaparser.fake_discord.Context(ynaparser.fake_discord.Guild({})))
yn = ynaparser.YnaFunctionContext(y)
async def a(): print(await ynaparser.functions.slice(yn, "", "!"))               
import asyncio
asyncio.run(a())