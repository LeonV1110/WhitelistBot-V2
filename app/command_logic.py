"""Handles the logic for the commands
    commands may be triggered in multiple ways, like buttons, slash commands or events."""
import uuid7
from discord import Member, Embed
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.database import Player, Whitelist_order, Role_assignment, Role, Whitelist
from app import util, config as cfg
from app.exceptions import PlayerNotFound, InsufficientTier, DuplicatePlayerPresent, MyException, DuplicatePlayerPresentSteam, DuplicatePlayerPresentDiscord


def update_player_from_member(session: Session, member: Member) -> None:
    discordID = str(member.id)
    tier = util.convert_role_to_tier(member.roles)
    discord_roles = util.convert_role_to_perm(member.roles)
    
    player = Player.get_by_id(session, discordID)

    player.name = member.name

    whitelist_order:Whitelist_order|None = player.whitelist_order
    if whitelist_order is not None:
        whitelist_order.tier = tier
        whitelist_order.check_and_update_whitelist_count()
        whitelist_order.check_and_update_active()

    db_role_assignments:list[Role_assignment] = player.role_assignments
    for db_role_assignment in list(db_role_assignments): #using list cast to create a copy
        if db_role_assignment.role.name not in discord_roles:
            player.role_assignments.remove(db_role_assignment)

    for role_name in discord_roles:
        db_role_names = [x.role.name for x in db_role_assignments]
        if role_name not in db_role_names:
            db_role = Role.get_by_name(session, role_name)
            player.role_assignments.append(Role_assignment(player = player, role = db_role))
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        util.check_integrityerror(e)
        raise

def deactivate_whitelist_order(session: Session, member: Member):
    discordID = str(member.id)
    player = Player.get_by_id(session, discordID)
    player.whitelist_order.active = False
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        util.check_integrityerror(e)
        raise

def register_player(session: Session, member:Member, steam64_id: str|None = None, eos_id: str|None = None):
    util.check_steam64_id(steam64_id)
    player = Player(
        player_id=str(uuid7.create()),
        name = member.name,
        discord_id = str(member.id),
        steam64_id = steam64_id,
        eos_id = eos_id,
        
    )
    session.add(player)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        util.check_integrityerror(e)
        raise

def remove_player(session: Session, member: Member|None = None, id: str|None = None):
    if member is not None:
        id = str(member.id)
    player = Player.get_by_id(session, id)
    session.delete(player)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        util.check_integrityerror(e)
        raise

def change_steam64_id(session: Session, member: Member, steam64_id: str):
    util.check_steam64_id(steam64_id)
    Player.get_by_id(session, str(member.id)).steam64_id = steam64_id
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        util.check_integrityerror(e)
        raise

def change_eos_id(session: Session, member: Member, eos_id: str):
    util.check_eos_id(eos_id)
    Player.get_by_id(session, str(member.id)).eos_id = eos_id
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        util.check_integrityerror(e)
        raise


def get_player_info(session: Session, member: Member = None, id: str|None = None) -> Embed:
    if member is not None:
        id = str(member.id)
    player = Player.get_by_id(session, id)

    embed = Embed(title=player.name)
    embed.add_field(name = 'Steam64 ID', value= str(player.steam64_id), inline=False)
    embed.add_field(name = 'Discord ID', value= str(player.discord_id), inline=False)
    embed.add_field(name = f'{cfg.BOTNAME} ID', value= str(player.player_id), inline=False)

    whitelist_status = 'Inactive'
    whitelist_owners = []
    for whitelist in player.whitelists:
        if whitelist.whitelist_order.active:
            whitelist_status = 'Active'
            whitelist_owners.append(whitelist.whitelist_order.player.name)
    embed.add_field(name = 'Whitelist Status', value = whitelist_status, inline=False)
    for whitelist_owner in whitelist_owners:
        embed.add_field(name = 'Whitelisted by', value = whitelist_owner, inline = False)
    if player.whitelist_order is not None:
        embed.add_field(name = 'Whitelist Subscription', value= player.whitelist_order.tier, inline=False)
    return embed

def get_whitelist_info(session: Session, member: Member = None, id: str|None = None) -> Embed:
    if member is not None:
        id = str(member.id)
    player = Player.get_by_id(session, id)

    if player.whitelist_order is None:
        return Embed(title="It seems like you don't have a whitelist subscription. Make sure you are subscribed on Patreon and reconnect your discord account to Patreon.")
    
    wo = player.whitelist_order
    whitelistees = ""
    for whitelist in wo.whitelists:
        player = whitelist.player
        whitelistees += player.name + ' ' + player.steam64_id + '\n'
    whitelist_status = 'Inactive'
    for whitelist in player.whitelists:
        if whitelist.whitelist_order.active:
            whitelist_status = 'Active'

    embed = Embed(title = 'Whitelist Subscription: ' + player.name)
    embed.add_field(name = 'Tier: ', value= wo.tier, inline=False)
    embed.add_field(name = 'Status: ', value = whitelist_status, inline=False)

    embed.add_field(name = 'Whitelists: ', value= whitelistees, inline=False)

    return embed

def add_player_to_whitelist(session: Session, owner_member: Member = None, owner_id: str|None = None, player_id: str|None = None) -> Embed:
    if owner_member is not None:
        owner_id = str(owner_member.id)

    order = Player.get_by_id(session, owner_id).whitelist_order
    player = Player.get_by_id(session, player_id)

    if order is None:
        return Embed(title="It seems like you don't have a whitelist subscription. " \
        "Make sure you are subscribed on Patreon and reconnect your discord account to Patreon.")
    
    whitelist = Whitelist(
        order_id = order.order_id,
        player_id = player.player_id
    )
    session.add(whitelist)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        util.check_integrityerror(e)
        raise
    return Embed(title= player.name + ' has been successfully added to your subscription.')

def remove_player_from_whitelist(session: Session, owner_member: Member = None, owner_id: str|None = None, player_id: str|None = None) -> Embed:
    if owner_member is not None:
        owner_id = str(owner_member.id)

    order = Player.get_by_id(session, owner_id).whitelist_order
    player = Player.get_by_id(session, player_id)
    
    if order is None:
        return Embed(title="It seems like you don't have a whitelist subscription. " \
        "Make sure you are subscribed on Patreon and reconnect your discord account to Patreon.")
    
    stmt = select(Whitelist).where(
        Whitelist.order_id == order.order_id,
        Whitelist.player_id == player.player_id
    )
    wl = session.scalar(stmt)
    if wl is None:
        return Embed(title="The player you tried to remove was not whitelisted before.")
    
    session.delete(wl)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        util.check_integrityerror(e)
        raise
    return Embed(title=f'Player {player.name} was sucessfully removed from your whitelist')


def update_player_on_whitelist(session: Session, owner_member: Member = None, owner_id: str|None = None, old_player_id: str|None = None, new_player_id: str|None = None) -> Embed:
    if owner_member is not None:
        owner_id = str(owner_member.id)

    owner = Player.get_by_id(session, owner_id)
    old_player = Player.get_by_id(session, old_player_id)
    new_player = Player.get_by_id(session, new_player_id)
    #TODO add error handling for getting these players


    if owner is old_player or owner is new_player:
        return Embed(title="You have used your own id, but you can't add or remove yourself from your own whitelist subscription.")
    elif owner.whitelist_order is None:
        return Embed(title="It seems like you don't have a whitelist subscription. Make sure you are subscribed on Patreon and reconnect your discord account to Patreon.")


    whitelist = session.scalar(
        select(Whitelist).where(
            Whitelist.order_id == owner.whitelist_order.order_id,
            Whitelist.player_id == old_player.player_id
    ))

    if whitelist is None:
        return Embed(title="The player you tried to remove was not whitelisted before.")
    
    whitelist.player_id = new_player.player_id
    return Embed(title = old_player.name + ' has been successfully replaced with ' + new_player.name + '.')
  