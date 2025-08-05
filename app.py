"""Main entry into the discordbot
    Defines all commands and events"""
import discord

from discord import Embed, Colour, Interaction
from discord.member import Member

from app import config as cfg
from app.views.explain_embed_view import ExplainEmbedView
import app.command_logic as cl
from app.util import command_error_embed_gen, get_player, connect_database, create_bot


bot = create_bot()

guilds = []
for guild_id in cfg.GUILD_IDS:
    guilds.append(discord.Object(id = guild_id))

#############################
########   Events    ########
#############################

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.add_view(ExplainEmbedView())
    try:
        for guild in guilds:
            synced = await bot.tree.sync(guild=guild)
            print(f'Synced {len(synced)} cmds, in guildID: {guild.id}')
    except Exception as e:
        print(e)
    return

@bot.event
async def on_member_update(before: Member, after: Member) -> None:
    with connect_database() as connection:
        cl.update_player_from_member(connection, member=after)
        connection.commit()
    return

@bot.event
async def on_raw_member_remove(payload) -> None:
    with connect_database() as connection:
        cl.deactivate_whitelist_order(connection, member = payload.user)
        connection.commit()
    return

@bot.event
async def on_member_join(member: Member):
    with connect_database() as connection:
        cl.update_player_from_member(connection, member)
        connection.commit()
    return

#######################################
########   TESTING Commands    ########
#######################################

#@bot.tree.command(name="testing", guilds=guilds)
async def testing(inter):
    await inter.response.send_message("button", view=ExplainEmbedView())

#@bot.tree.command(name= "hello", description='Say Hello!',  guilds=guilds)
async def sayHello(inter, member: Member):
    await inter.response.defer()

    print(type(inter.followup))
    await inter.followup.send('Hello')

######################################
########   Player Commands    ########
######################################



#####################################
########   Admin Commands    ########
#####################################

@bot.tree.command(description="Get player-info on player, prefrence: Member, discordID, steam64ID", guilds=guilds)
@discord.app_commands.checks.has_role(cfg.ADMIN_ROLE)
async def admin_get_player_info(inter: Interaction, member: Member = None, discordid:str = None, steam64id: str = None) -> None:
    await inter.response.defer()
    if member is not None:
        with connect_database() as connection:
            embed = cl.get_player_info(connection, member=member)
            connection.commit()
    elif discordid is not None:
        with connect_database() as connection:
            embed = cl.get_player_info(connection, discordID=discordid)
            connection.commit()
    elif steam64id is not None:
        with connect_database() as connection:
            embed = cl.get_player_info(connection, steam64ID=steam64id)
            connection.commit()
    else:
        embed = Embed(title='Please use one of the options')
    await inter.followup.send(embed=embed)

@admin_get_player_info.error
async def admin_get_player_info_error(inter: Interaction, error: Exception):
    await inter.followup.send(embed=command_error_embed_gen(error))

@bot.tree.command(description="Get whitelist-info on player, prefrence: Member, discordID, steam64ID", guilds=guilds)
@discord.app_commands.checks.has_role(cfg.ADMIN_ROLE)
async def admin_get_whitelist_info(inter: Interaction, member: Member = None, discordid:str = None, steam64id: str = None) -> None:
    await inter.response.defer()
    if member is not None:
        with connect_database() as connection:
            embed = cl.get_whitelist_info(connection, member=member)
            connection.commit()
    elif discordid is not None:
        with connect_database() as connection:
            embed = cl.get_whitelist_info(connection, discordID=discordid)
            connection.commit()
    elif steam64id is not None:
        with connect_database() as connection:
            embed = cl.get_whitelist_info(connection, steam64ID=steam64id)
            connection.commit()
    else:
        embed = Embed(title='Please use one of the options')
    await inter.followup.send(embed=embed)

@admin_get_whitelist_info.error
async def admin_get_whitelist_info_error(inter: Interaction, error: Exception):
    await inter.followup.send(embed=command_error_embed_gen(error))

######################################
########   Delete Commands    ########
######################################

@bot.tree.command(description="Removes a player from the database, including their whitelist order and any whitelists on that order", guilds = guilds)
@discord.app_commands.checks.has_role(cfg.DELETE_ROLE)
async def admin_nuke_player(inter: Interaction, discordid: str, steam64id: str) -> None:
    await inter.response.defer()
    with connect_database() as connection:
        discord_player = get_player(connection, discordID=discordid)
        steam_player = get_player(connection, steam64ID=steam64id)
        if discord_player == steam_player:
            cl.remove_player(connection, discordID=discordid)
            connection.commit()
            embed = Embed(title = f"{discord_player.name} has been successfully deleted from the database.")
        else:
            embed = Embed(title = f"The discordID is from {discord_player.name} while the steamId is from {steam_player.name}. Double check and try again. If the issue persists you can annoy Leon I guess...")
    await inter.followup.send(embed=embed)

@admin_nuke_player.error
async def admin_nuke_player_info_error(inter: Interaction, error: Exception):
    await inter.followup.send(embed=command_error_embed_gen(error))

#########################################
########   Sys admin Commands    ########
#########################################

@bot.tree.command(description="Dont worry, don't touch unless you're the sys admin", guilds=guilds)
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
    await inter.followup.send(embed=command_error_embed_gen(error))

if __name__ == "__main__":
    bot.run(cfg.TOKEN)