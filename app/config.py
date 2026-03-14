"""Import configs into global variables"""
import configparser
from pathlib import Path

config = configparser.ConfigParser()

BASE_DIR = Path(__file__).resolve().parent.parent
config.read(BASE_DIR / "config.ini")

SETUP_DONE = bool(config['GENERAL']['SETUP'])

DATABASEUSER = config['DATABASE']['DATABASE_USERNAME']
DATABASEPSW = config['DATABASE']['DATABASE_PASSWORD']
DATABASEHOST = config['DATABASE']['DATABASE_HOST']
DATABASEPORT = config['DATABASE']['DATABASE_PORT']
DATABASENAME = config['DATABASE']['DATABASE_NAME']

TOKEN = config['DISCORD']['TOKEN']
GUILD_IDS = [int(config['DISCORD']['GUILDID'])]
BOTNAME = config['SETTINGS']['BOTNAME']
WHITELIST_LINK = config['SETTINGS']['WHITELIST_LINK']

ROLE_ROLES = config['ROLE_ROLES']
ROLE_NAMES = config['ROLE_NAMES']
PERMISSIONS_PER_ROLE = [[perm for perm in perms.split(',')] for perms in config['PERMISSIONS_PER_ROLE']]

WHITELIST_ROLES = config['WHITELIST_ROLES']
WHITELIST_NAMES = config['WHITELIST_NAMES']
WHITELIST_ALLOWANCE = config['WHITELIST_ALLOWANCE']

EXPLAIN_EMBED_ROLE = int(config['DISCORD_COMMAND_PERMISSIONS']['EXPLAIN_EMBED'])
DELETE_ROLE = int(config['DISCORD_COMMAND_PERMISSIONS']['DELETE'])
DELETE_ROLES = tuple([int(s.strip()) for s in config['DISCORD_COMMAND_PERMISSIONS']['DELETE'].split(',')])
ADMIN_ROLES = tuple([int(s.strip()) for s in config['DISCORD_COMMAND_PERMISSIONS']['ADMIN'].split(',')])


def check_config_validity() -> bool:
    for config in [TOKEN, GUILD_IDS, BOTNAME, WHITELIST_LINK, DATABASEUSER, DATABASEPSW, DATABASEHOST, DATABASEPORT, DATABASENAME]:
        if config == 'TODO':
            return False
        
    role_count = len(ROLE_ROLES)
    if len(ROLE_NAMES) != role_count or len(PERMISSIONS_PER_ROLE) != role_count:
        return False

    whitelist_type_count = len(WHITELIST_ROLES)
    if len(WHITELIST_NAMES) != whitelist_type_count or len(WHITELIST_ALLOWANCE) != whitelist_type_count:
        return False
    return True
