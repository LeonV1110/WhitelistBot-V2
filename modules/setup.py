"""Functions for handling the initial setup, both first time setup and startup"""

import sys
import subprocess
import uuid7
from sqlalchemy import select, delete, tuple_
from discord.ext.commands import Bot
from discord import Intents
from discord.ui import View

from modules.database import Base, get_session, Permission, Role, Permission_assignment, engine
import modules.config as cfg

GAME_PERMISSIONS = [
    "startvote",
    "changemap",
    "pause",
    "cheat",
    "private",
    "balance",
    "chat",
    "kick",
    "ban",
    "config",
    "cameraman",
    "immune",
    "manageserver",
    "featuretest",
    "reserve",
    "demos",
    "clientdemos",
    "debug",
    "teamchange",
    "forceteamchange",
    "canseeadminchat"
    ]

def check_setup() -> None:

    Base.metadata.create_all(engine) #will setup new tables, not edit existing ones

    check_and_load_permissions()
    check_and_load_roles()
    check_and_load_perm_assignments()


def check_and_load_permissions() -> None:
    with get_session() as session: # add missing permission entries
        permission_names = GAME_PERMISSIONS + cfg.ADDITIONAL_PERMISSIONS
        perms = [Permission(permission_id = str(uuid7.create()), name = perm_name) for perm_name in permission_names]
        db_perms_scaler = session.scalar(select(Permission.name))
        if db_perms_scaler is None:
            missing_perms = perms
        else:
            db_perms = db_perms_scaler.all()
            missing_perms = [perm for perm in perms if perm.name not in db_perms]
        session.add_all(missing_perms)
        session.commit()


def check_and_load_roles() -> None:
    with get_session() as session:
        role_names, _, _ = zip(*cfg.ROLES_CONFIG)
        db_roles_scalar = session.scalar(select(Role.name))
        if db_roles_scalar is None:
            missing_role_names = role_names
        else:
            db_roles = db_roles_scalar.all()
            missing_role_names = [role for role in role_names if role.name not in db_roles]
        missing_roles = [Role(role_id = str(uuid7.create()), name = role_name) for role_name in missing_role_names]
        session.add_all(missing_roles)
        session.commit()


def check_and_load_perm_assignments() -> None:
    with get_session() as session:
        roles = session.scalars(select(Role)).all()
        role_by_name = {r.name: r for r in roles}

        cfg_role_names, _, cfg_role_perms = zip(*cfg.ROLES_CONFIG)

        for role_name in cfg_role_names:
            if role_name not in role_by_name:
                raise ValueError(f'role: {role_name} was not found in the db')
                #TODO check if needed, maybe just let it fail instead

        permissions = session.scalars(select(Permission)).all()
        perm_by_name = {p.name: p for p in permissions}

        assignments = session.scalars(select(Permission_assignment)).all()

        db_state: dict[int, set[str]] = {}
        for a in assignments:
            db_state.setdefault(a.role_id, set()).add(a.permission.name)

        inserts = []
        deletes = []

        for role_name, perms in zip(cfg_role_names, cfg_role_perms):
            role = role_by_name[role_name]
            role_id = role.role_id

            desired = set(perms)
            current = db_state.get(role_id, set()) #default to empty set
            missing = desired - current
            extra = current - desired

            for perm_name in missing:
                permission = perm_by_name[perm_name]

                inserts.append(Permission_assignment(
                    role_id=role_id, 
                    permission_id = permission.permission_id
                    )
                )

            for perm_name in extra:
                permission = perm_by_name[perm_name]

                deletes.append((role_id, permission.permission_id))

        if inserts:
            session.add_all(inserts)

        if deletes:
            session.execute(
                delete(Permission_assignment).where(
                    tuple_(
                        Permission_assignment.role_id, Permission_assignment.permission_id
                    ).in_(deletes)
                )
            )

DRIVER_PACKAGES = {
    "postgresql+psycopg": "psycopg[binary]",
    "postgresql+psycopg2": "psycopg2-binary",
    "mysql+pymysql": "pymysql",
    "mysql+mariadbconnector": "mariadb",
}

def install_package(package_name: str):
    """Install a package via pip at runtime."""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

def ensure_db_driver(dialect_driver: str):
    pkg = DRIVER_PACKAGES.get(dialect_driver)
    if pkg is None:
        return  # SQLite or unknown, assume builtin
    try:
        # Try to import dynamically
        module_name = pkg.split("[")[0]  # remove extras if any
        __import__(module_name)
    except ImportError:
        print(f"Driver {module_name} not found, installing...")
        install_package(pkg)

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