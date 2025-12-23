"""Import configs into global variables"""
import configparser
from pathlib import Path

config = configparser.ConfigParser()

BASE_DIR = Path(__file__).resolve().parent.parent
config.read(BASE_DIR / "config.ini")


DATABASEUSER = config['DATABASE']['DATABASE_USERNAME']
DATABASEPSW = config['DATABASE']['DATABASE_PASSWORD']
DATABASEHOST = config['DATABASE']['DATABASE_HOST']
DATABASEPORT = config['DATABASE']['DATABASE_PORT']
DATABASENAME = config['DATABASE']['DATABASE_NAME']

TOKEN = config['DISCORD']['TOKEN']
GUILD_IDS = [int(config['DISCORD']['GUILDID'])]
BOTNAME = config['SETTINGS']['BOTNAME']
WHITELIST_LINK = config['SETTINGS']['WHITELIST_LINK']

PERMISSION_ROLES = config['PERMISSION_ROLES']
PERMISSION_NAMES = config['PERMISSION_NAMES']

WHITELIST_ROLES = config['WHITELIST_ROLES']
WHITELIST_NAMES = config['WHITELIST_NAMES']
WHITELIST_ALLOWANCE = config['WHITELIST_ALLOWANCE']

EXPLAIN_EMBED_ROLE = int(config['DISCORD_COMMAND_PERMISSIONS']['EXPLAIN_EMBED'])
DELETE_ROLE = int(config['DISCORD_COMMAND_PERMISSIONS']['DELETE'])
DELETE_ROLES = tuple([int(s.strip()) for s in config['DISCORD_COMMAND_PERMISSIONS']['DELETE'].split(',')])
ADMIN_ROLES = tuple([int(s.strip()) for s in config['DISCORD_COMMAND_PERMISSIONS']['ADMIN'].split(',')])
