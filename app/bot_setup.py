from discord.ext.commands import Bot
from discord import Intents
from discord.ui import View

intents = Intents.default()
intents.members = True
# intents.message_content = True #Likely not needed
bot = Bot(command_prefix='!', intents=intents)

def create_bot(views : list[View] = []) -> Bot:
    intents = Intents.default()
    intents.members = True
    intents.message_content = True #Likely not needed
    bot = Bot(command_prefix='!', intents=intents)

    for view in views:
        bot.add_view(view)
    return bot
class testing():
    def __init__():
        return