from app import bot_setup as bsp, config as cfg
from discord.ext.commands import Bot
from discord.ext import commands
from discord import Embed, Colour, Interaction
from discord.app_commands.errors import MissingRole
from discord.member import Member
from app.views.explain_embed_view import ExplainEmbedView
import discord

bot = bsp.create_bot()

guilds = []
for guild_id in cfg.GUILD_IDS:
    guild = discord.Object(id = guild_id)
    guilds.append(guild)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.add_view(ExplainEmbedView())
    try:
        guild = discord.Object(id = cfg.GUILD_IDS[0])
        synced = await bot.tree.sync(guild=guild)
        print(f'Synced {len(synced)} cmds')
    except Exception as e:
        print(e)
        pass

@bot.event
async def on_member_update(before: Member, after: Member) -> None:
    #TODO update player
    return

@bot.event
async def on_member_remove(member: Member) -> None:
    #TODO update player
    return

@bot.tree.command(name="testing", guilds=guilds)
async def testing(inter):
    await inter.response.send_message("button", view=ExplainEmbedView())

@bot.tree.command(name= "hello", description='Say Hello!',  guilds=guilds)
async def sayHello(inter):
    await inter.response.send_message('Hello')

@bot.tree.command(description="Dont worry, don't touch unless you're called Leon.", guilds=guilds)
@discord.app_commands.checks.has_role(cfg.EXPLAIN_EMBED_ROLE)
async def explain_embed_setup(inter):
    await inter.response.defer()
    embed = Embed(title=f'The {cfg.BOTNAME} whitelist bot',
                  colour=Colour.orange())
    embed.add_field(name='Patreon', value=f'Get your whitelist at {cfg.WHITELIST_LINK}')
    embed.add_field(name='Register', value='''
        Use this button to register yourself with the bot, it will ask you for your steam64 ID. Getting registered is required to activate your whitelist or to get whitelisted by a friend. \n
        - Note: To find your Steam64 ID go to the settings page on your steam account and click on the "View Account Details" option. A new page will open in steam, at the top it will state "Steam64 ID: 7656119xxxxxxxxxx" (with the x's being unique to your account). This is your steam64ID that you need to use when registering. \n
        - Important: Once you are registered and have an active whitelist it will only take effect once a new round has started on the server (maximum 2 hours).\n
        ''', inline=False)
    embed.add_field(name='Add a Friend', value='''
        If you have a higher tier patreon subscription you have the abilitty to add friends, make sure they register and then get their steam64 ID.\n
        - Note: You can only add one friend at a time.\n
        - Important: Once you added your friend their whitelist will only take effect once a new round has started (maximum 2 hours).\n
        ''', inline=False)
    embed.add_field(name='Change My Steam64ID', value='''
        If you used the wrong steam64 ID when you registered you can change it by entering the correct one.
        ''', inline=False)
    embed.add_field(name='Get My Info', value=f'''
        To check if everything should be working you can use this button, it will show you your:\n
        - Currently listed steam64 ID\n
        - Discord ID\n
        - "{cfg.BOTNAME}" ID (this is a unique ID for you within the database, you can ignore this)\n
        - Whitelist status (it will show whether your whitelist is "Active" or "Inactive")\n
        - Who you are whitelisted by (only visible if your whitelist status is "Active")\n
        - Whitelist subscription tier (only visible if you have any of those roles)\n
        ''', inline=False)
    embed.add_field(name='Get My Whitelist Info', value='''
        To see who you have added to your whitelist you can use this button, it will show you your:\n
        - Whitelist subscription tier\n
        - Whitelist status (it will show whether your whitelist is "Active" or "Inactive")\n
        - Whitelists (a list of everyone whitelisted under your subscription including yourself)\n
        - Note: Only works if you have a whitelist role in this discord.\n
        ''', inline=False)
    embed.add_field(name='Update My Data', value='''
        If something related to your whitelist is supposed to be working but isnt you can click this button first to force the bot to update. If that has no effect you can #create-ticekt with the admin team and we can take a better look.\n
        - Important: Whitelist it will only take effect once a new round has started on the server (maximum 2 hours).\n
        ''', inline=False)
    embed.add_field(name='Remove a Friend', value='''
        If you want to remove a friend from your whitelist you can do that here. To remove them enter their steam64 ID in the provided form.\n
        - Note: Dont worry, using this button wont remove them as your friend in real life. It just means that they are no longer whitelisted under your subscription.
        ''', inline=False)
    embed.add_field(name='Delete My Data', value='''
        If you want to remove all your info from the database for whatever reason you can do this with this button, it will ask you to confirm by having you type in "DELETE" so you cant do it on accident.\n
        - Note: This means that you will not be whitelisted anymore (even if you are whitelisted through a friend).
        ''', inline=False)
    
    await inter.followup.send(embed=embed, view=ExplainEmbedView())
    return

@explain_embed_setup.error
async def explain_embed_setup_error(inter: Interaction, error):
    if isinstance(error, MissingRole):
        await inter.response.send_message(embed=Embed(title='You do not have the required roles to use this command'), ephemeral=True)
    else:
        raise error

if __name__ == "__main__":
    bot.run(cfg.TOKEN)