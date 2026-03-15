"""Import configs into global variables"""
import configparser
from pathlib import Path
from urllib.parse import quote_plus

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

ADDITIONAL_PERMISSIONS = [perm for perm in config['SETTINGS']['PERMISSIONS'].split(',')]
ROLES_CONFIG = []

for role_name, value in config["PERMISSION_ROLES"].items():
    role_id_str, perms_str = value.split(",", 1)
    role_id = int(role_id_str.strip())
    perms = [p.strip() for p in perms_str.split("|")]

    ROLES_CONFIG.append((role_name, role_id, perms))

WHITELIST_CONFIG = []

for tier_name, value in config['WHITELIST_ROLES'].items():
    role_id_str, tier_str = value.split(",", 1)
    role_id = int(role_id_str.strip())
    tier = int(tier_str.strip())
    WHITELIST_CONFIG.append((tier_name, role_id, tier))

EXPLAIN_EMBED_ROLE = int(config['DISCORD_COMMAND_PERMISSIONS']['EXPLAIN_EMBED'])
DELETE_ROLE = int(config['DISCORD_COMMAND_PERMISSIONS']['DELETE'])
DELETE_ROLES = tuple([int(s.strip()) for s in config['DISCORD_COMMAND_PERMISSIONS']['DELETE'].split(',')])
ADMIN_ROLES = tuple([int(s.strip()) for s in config['DISCORD_COMMAND_PERMISSIONS']['ADMIN'].split(',')])


def check_config_validity() -> bool:
    for config in [TOKEN, GUILD_IDS, BOTNAME, WHITELIST_LINK, DATABASEUSER, DATABASEPSW, DATABASEHOST, DATABASEPORT, DATABASENAME]:
        if config == 'TODO':
            return False
    return True


def get_db_string() -> str:
    db_conf = config["DATABASE"]

    # Build the driver string
    if db_conf.get("driver"):
        dialect_driver = f"{db_conf['dialect']}+{db_conf['driver']}"
    else:
        dialect_driver = db_conf["dialect"]

    # SQLite is special (no host/username/password for file DB)
    if db_conf["dialect"] == "sqlite":
        db_url = f"sqlite:///{db_conf['dbname']}"
    else:
        username = quote_plus(db_conf["username"])
        password = quote_plus(db_conf["password"])
        host = db_conf["host"]
        port = db_conf.get("port", "")  # optional
        port_part = f":{port}" if port else ""
        dbname = db_conf["dbname"]

        db_url = f"{dialect_driver}://{username}:{password}@{host}{port_part}/{dbname}"
    return db_url
