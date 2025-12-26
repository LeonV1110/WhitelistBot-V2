"""A collection of utility functions"""
import pymysql

from pymysql import Connection, OperationalError
from discord import Embed, Intents
from discord.app_commands.errors import MissingRole, MissingAnyRole, CommandInvokeError
from discord.ext.commands import Bot
from discord.ui import View
from app import config as cfg
from app.exceptions import MyException, InvalidSteam64ID, InvalidDiscordID, PlayerNotFound
from app.database.player import DatabasePlayer, SteamPlayer, BOTIDPlayer, Player

RERAISING = False # dev config option to make the program reraise errors for a proper stacktrace instead of replying to the user
#TODO should be possible to have both


def check_steam64ID(steam64ID: str):
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


def get_player(connection: Connection, discordID: str = None, steam64ID: str = None, BOTID: str = None) -> Player:
    if discordID is not None:
        check_discordID(discordID)
        player = DatabasePlayer(discordID, connection)
    elif steam64ID is not None:
        check_steam64ID(steam64ID)
        player = SteamPlayer(steam64ID, connection)
    elif BOTID is not None:
        player = BOTIDPlayer(BOTID, connection)
    else:
        raise PlayerNotFound()
    return player

def convert_role_to_perm(roles):
    permission_roles = {}
    for key, value in cfg.PERMISSION_ROLES.items():
        permission_roles[int(value)] = cfg.PERMISSION_NAMES[key]

    roles.reverse()
    for role in roles:
        if role.id in permission_roles: return permission_roles[role.id]
    return None

def convert_role_to_tier(roles):
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
    elif isinstance(error, OperationalError):
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

def connect_database() -> pymysql.connections.Connection:
    connection = pymysql.connect(host=cfg.DATABASEHOST, port = int(cfg.DATABASEPORT), user = cfg.DATABASEUSER, password= cfg.DATABASEPSW, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, database=cfg.DATABASENAME)
    return connection

def create_bot(views : list[View] = []) -> Bot:
    intents = Intents.default()
    intents.members = True
    intents.message_content = True #TODO Likely not needed
    bot = Bot(command_prefix='!', intents=intents)
    for view in views:
        bot.add_view(view)
    return bot
