"""A collection of utility functions"""
from sqlalchemy import select, or_
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from discord import Embed, Intents
from discord.app_commands.errors import MissingRole, MissingAnyRole, CommandInvokeError
from discord.ext.commands import Bot
from discord.ui import View

from app import config as cfg
from app.exceptions import MyException, InvalidSteam64ID, InvalidDiscordID, PlayerNotFound, NoStoreID, InsufficientTier



RERAISING = False # dev config option to make the program reraise errors for a proper stacktrace instead of replying to the user
#TODO should be possible to have both


def check_steam64_id(steam64ID: str):
    #check if int
    str(steam64ID)
    try:
        int(steam64ID)
    except Exception as e:
        raise InvalidSteam64ID(f'A steam64ID contains just numbers. You provided "{steam64ID}"') from e
    #check if not default steam64ID
    if (steam64ID == str(76561197960287930)):
        raise InvalidSteam64ID("This is Gabe Newell's steam64ID, please make sure to enter the correct one.")
    #check if first numbers match
    if (not steam64ID[0:7] == "7656119"):
        raise InvalidSteam64ID("This is not a valid steam64ID.")
    #check the length
    if (len(steam64ID) < 17):
        raise InvalidSteam64ID("This is not a valid steam64ID, as it is shorter than 17 characters.")
    if (len(steam64ID) > 17):
        raise InvalidSteam64ID("This is not a valid steam64ID, as it is longer than 17 characters.")
    return 

def check_eos_id(eos_id: str):
    #TODO check eos id for validity
    return

def check_discordID(discordID: str):
    str(discordID)
    try:
        int(discordID)
    except Exception as e:
        raise InvalidDiscordID('A discordID contains just numbers.') from e
    if len(discordID) < 17: 
        raise InvalidDiscordID("A discordID is at least 17 characters long, this one is too short.")
    elif len(discordID) > 19:
        raise InvalidDiscordID("A discordID is at most 19 characters long, this one is too long.")
    return

def convert_discord_role_to_roles(roles):
    permission_roles = {}
    for key, value in cfg.ROLE_ROLES.items():
        permission_roles[int(value)] = cfg.ROLE_ROLES[key]
    
    roles.reverse()
    for role in roles:
        if role.id in permission_roles: #TODO
            pass

def convert_role_to_perm(roles): #TODO update to use new role based perms
    permission_roles = {}
    for key, value in cfg.ROLE_ROLES.items():
        permission_roles[int(value)] = cfg.ROLE_ROLES[key]

    roles.reverse()
    for role in roles:
        if role.id in permission_roles: return permission_roles[role.id]
    return None

def convert_role_to_tier(roles): #TODO update to use new number based tiers
    whitelist_roles = {}
    for key, value in cfg.WHITELIST_ROLES.items():
        whitelist_roles[int(value)] = cfg.WHITELIST_NAMES[key]
    roles.reverse()
    for role in roles:
        if role.id in whitelist_roles: return whitelist_roles[role.id]
    return None

def command_error_embed_gen(error: Exception) -> Embed:
    if isinstance(error, CommandInvokeError):
        error = error.__cause__
    if isinstance(error, MissingRole) or isinstance(error, MissingAnyRole):
        error_str = 'You do not have the required roles to use this command'
    elif isinstance(error, MyException):
        print("---------------------------------------")
        print(f"an {type(error)} error occured:")
        print(error)
        print("---------------------------------------")
        error_str = str(error)
        if RERAISING:
            raise Exception from error
    elif isinstance(error, SQLAlchemyError):
        print("---------------------------------------")
        print(f"an {type(error)} error occured:")
        print(error.orig)
        print("---------------------------------------")
        error_str = "The bot is currently having issues, please try again later."
    else:
        print("---------------------------------------")
        print(f"an {type(error)} error occured:")
        print(error)
        print("---------------------------------------")
        error_str = "Some unknown error occured, please ping your sys admin"
        if RERAISING:
            raise Exception from error
    return Embed(title=error_str)

def check_integrityerror(error: IntegrityError) -> None:
    orig = str(error.orig)
    if 'player_has_store_id' in orig:
        raise NoStoreID from error
    if 'whitelist_limit' in orig:
        raise InsufficientTier from error
    
def create_bot(views : list[View]|None = None) -> Bot:
    if views is None:
        views = []
    intents = Intents.default()
    intents.members = True
    intents.message_content = True #TODO Likely not needed
    bot = Bot(command_prefix='!', intents=intents)
    for view in views:
        bot.add_view(view)
    return bot

def get_db_string() -> str:
    return 'sqlite:///test.db' #TODO