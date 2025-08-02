from app.exceptions import InvalidSteam64ID, InvalidDiscordID
from app.database.player import DatabasePlayer, SteamPlayer, BOTIDPlayer, Player, PlayerNotFound
from app import config as cfg
from pymysql import Connection

def check_steam64ID(steam64ID: str):
    #check if int
    str(steam64ID)
    try:
        int(steam64ID)
    except:
        raise InvalidSteam64ID("A steam64ID contains just numbers.")
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
    except:
        raise InvalidDiscordID('A discordID contains just numbers.')
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