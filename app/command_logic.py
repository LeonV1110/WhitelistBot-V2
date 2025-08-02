from discord import Member, Embed
from app.database.player import Player, NewPlayer
from app import util, config as cfg
from app.exceptions import PlayerNotFound, InsufficientTier, DuplicatePlayerPresent, MyException
from pymysql import Connection, OperationalError

def update_player_from_member(connection: Connection, member: Member):
    discordID = str(member.id)
    player:Player = util.get_player(connection, discordID=discordID)
    tier = util.convert_role_to_tier(member.roles)
    permission = util.convert_role_to_perm(member.roles)
    name = member.name
    player.update_player(connection, player.steam64ID, discordID, name, permission, tier)

def register_player(connection: Connection, member:Member, steam64ID: str):
    util.check_steam64ID(steam64ID)
    discordID = str(member.id)
    name = member.name
    tier = util.convert_role_to_tier(member.roles)
    permission = util.convert_role_to_perm(member.roles)
    NewPlayer(steam64ID, discordID, name, permission, tier).insert_player(connection)

def remove_player(connection: Connection, member: Member = None, discordID: str = None, steam64ID: str = None, BOTID: str = None):
    if member is not None:
        discordID = str(member.id)
    util.get_player(connection, discordID, steam64ID, BOTID).delete_player(connection)

def change_steam64ID(connection: Connection, member: Member, steam64ID: str):
    util.check_steam64ID(steam64ID)
    util.get_player(connection, discordID=str(member.id)).update_player(connection=connection, steam64ID=steam64ID)

def get_player_info(connection: Connection, member: Member = None, discordID: str = None, steam64ID: str = None, BOTID: str = None ) -> Embed:
    if member is not None:
        discordID = str(member.name)
    player:Player = util.get_player(connection, discordID, steam64ID, BOTID)

    embed = Embed(title=player.name)
    embed.add_field(name = 'Steam64 ID', value= str(player.steam64ID), inline=False)
    embed.add_field(name = 'Discord ID', value= str(player.discordID), inline=False)
    embed.add_field(name = f'{cfg.BOTNAME} ID', value= str(player.BOTID), inline=False)

    if player.check_whitelist(connection):
        whitelist_status = 'Active'
        whitelist_owner_BOTID = player.check_whos_whitelist_order()
        whitelist_owner = util.get_player(connection, BOTID= whitelist_owner_BOTID)
        embed.add_field(name = 'Whitelist Status', value = whitelist_status, inline=False)
        embed.add_field(name = 'Whitelisted by', value = whitelist_owner.name, inline = False)
    else:
        whitelist_status = "Inactive"
        embed.add_field(name = 'Whitelist Status', value = whitelist_status, inline=False)
    if player.whitelist_order is not None:
        embed.add_field(name = 'Whitelist Subscription', value= player.whitelist_order.tier, inline=False)
    return embed

def get_whitelist_info(connection: Connection, member: Member = None, discordID:str = None, steam64ID: str = None, BOTID: str = None) -> Embed:
    if member is not None:
        discordID = str(member.name)
    player:Player = util.get_player(connection, discordID, steam64ID, BOTID)
    if player.whitelist_order is None:
        return Embed(title="It seems like you don't have a whitelist subscription. Make sure you are subscribed on Patreon and reconnect your discord account to Patreon.")
    
    wo = player.whitelist_order
    whitelistees = ""
    for whitelist in wo.whitelists:
        player = util.get_player(connection, BOTID=whitelist.BOTID)
        whitelistees += player.name + ' ' + player.steam64ID + '\n'
    if player.check_whitelist(connection):
        whitelist_status = 'Active'
    else:
        whitelist_status = 'Inactive'

    embed = Embed(title = 'Whitelist Subscription: ' + player.name)
    embed.add_field(name = 'Tier: ', value= wo.tier, inline=False)
    embed.add_field(name = 'Status: ', value = whitelist_status, inline=False)

    embed.add_field(name = 'Whitelists: ', value= whitelistees, inline=False)

    return embed

def add_player_to_whitelist(connection: Connection, owner_member: Member = None, owner_discordID: str = None, owner_steam64ID: str = None, owner_BOTID: str = None,
                            player_discordID: str = None, player_steam64ID: str = None, player_BOTID: str = None) -> Embed:
    if owner_member is not None:
        owner_discordID = str(owner_member.id)

    owner:Player = util.get_player(connection, owner_discordID, owner_steam64ID, owner_BOTID)
    player:Player = util.get_player(connection, player_discordID, player_steam64ID, player_BOTID)

    if owner.whitelist_order is None:
        return Embed(title="It seems like you don't have a whitelist subscription. Make sure you are subscribed on Patreon and reconnect your discord account to Patreon.")
    else:
        owner.whitelist_order.add_whitelist(connection, player.BOTID)
        return Embed(title= player.name + ' has been successfully added to your subscription.')

def remove_player_from_whitelist(connection: Connection, owner_member: Member = None, owner_discordID: str = None, owner_steam64ID: str = None, owner_BOTID: str = None,
                            player_discordID: str = None, player_steam64ID: str = None, player_BOTID: str = None) -> Embed:
    if owner_member is not None:
        owner_discordID = str(owner_member.id)

    owner:Player = util.get_player(connection, owner_discordID, owner_steam64ID, owner_BOTID)
    player:Player = util.get_player(connection, player_discordID, player_steam64ID, player_BOTID)

    if owner.whitelist_order is None:
        return Embed(title="It seems like you don't have a whitelist subscription. Make sure you are subscribed on Patreon and reconnect your discord account to Patreon.")
    else:
        owner.whitelist_order.remove_whitelist(connection, player.BOTID)
        return Embed(title = player.name + ' has been successfully removed from your subscription.')

def update_player_on_whitelist(connection: Connection, owner_member: Member = None, owner_discordID: str = None, owner_steam64ID: str = None, owner_BOTID: str = None,
old_player_discordID: str = None, old_player_steam64ID: str = None, old_player_BOTID: str = None,
new_player_discordID: str = None, new_player_steam64ID: str = None, new_player_BOTID: str = None) -> Embed:
    if owner_member is not None:
        owner_discordID = str(owner_member.id)
    
    owner:Player = util.get_player(connection, owner_discordID, owner_steam64ID, owner_BOTID)
    try:
        old_player = util.get_player(connection, old_player_discordID, old_player_steam64ID, old_player_BOTID)
    except PlayerNotFound:
        return Embed(title="The old player isn't in our database, and thus cannot be replaced.")
    try:
        new_player = util.get_player(connection, new_player_discordID, new_player_steam64ID, new_player_BOTID)
    except PlayerNotFound:
        return Embed(title= "The new player hasn't registered, and thus cannot be added to the whitelist")
    
    if owner == old_player or owner == new_player:
        return Embed(title="You have used your own steam64ID, but you can't add or remove yourself from your own whitelist subscription.")
    elif owner.whitelist_order is None:
        return Embed(title="It seems like you don't have a whitelist subscription. Make sure you are subscribed on Patreon and reconnect your discord account to Patreon.")

    try:
        owner.whitelist_order.remove_whitelist(connection, old_player.BOTID)
        owner.whitelist_order.add_whitelist(connection, new_player.BOTID)
    except (InsufficientTier, DuplicatePlayerPresent) as error:
        embed = Embed(title = error.message)
        try:
            owner.whitelist_order.add_whitelist(old_player.BOTID)
        except (OperationalError, MyException) as error:
            embed = Embed(title = "You have successfully broken the bot, I guess you can ping Leon.")
        return embed
    return Embed(title = old_player.name + ' has been successfully replaced with ' + new_player.name + '.')

    