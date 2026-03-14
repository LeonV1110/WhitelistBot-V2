from app.database import engine, Base, get_session, Permission, Role, Permission_assignment
import app.config as cfg
import uuid7
from sqlalchemy import select, delete


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

def initial_setup() -> None:
    Base.metadata.create_all(engine)

    with get_session() as session:
        perms = [Permission(permission_id = uuid7.create(), name = perm_name) for perm_name in GAME_PERMISSIONS]
        session.add_all(perms)
        session.commit()
    check_and_load_roles()
    check_and_load_perm_assignments()

    
def check_setup() -> None:
    Base.metadata.create_all(engine) #will setup new tables, not edit existing ones

    with get_session() as session: # add missing permission entries
        perms = [Permission(permission_id = uuid7.create(), name = perm_name) for perm_name in GAME_PERMISSIONS]
        db_perms = session.scalar(select(Permission.name)).all()
        missing_perms = [perm for perm in perms if perm.name not in db_perms]
        session.add_all(missing_perms)
        session.commit()
    check_and_load_roles()
    check_and_load_perm_assignments()


def check_and_load_roles() -> None:
    with get_session() as session:
        roles = []
        db_roles = session.scalar(select(Role.name)).all()
        missing_roles = [role for role in roles if role.name not in db_roles]
        session.add_all(missing_roles)
        session.commit()

def check_and_load_perm_assignments() -> None:
    # Checks all perms assignments
    with get_session() as session:
        
        roles = zip(cfg.ROLE_NAMES, cfg.PERMISSIONS_PER_ROLE)
        for name, perms in roles:
            db_role = session.scalar(select(Role)).where(Role.name == name)
            if db_role is None:
                raise ValueError(f'role: {name} was not found in the db')
            
            db_perm_asses = db_role.permission_assignments
            db_perm_names = [db_perm_ass.permission.name for db_perm_ass in db_perm_asses]

            missing_in_db = set(perms) - set(db_perm_names)
            if len(missing_in_db) != 0:
                permissions = session.scalar(select(Permission).where(Permission.name.in_(missing_in_db))).all()

                session.add_all([Permission_assignment(permission_id = permission.permission_id, role_id = db_role.id) for permission in permissions])
            extra_in_db = set(db_perm_names) - set(perms)
            if len(extra_in_db) != 0:
                permissions = session.scalar(select(Permission).where(Permission.name.in_(extra_in_db))).all()
                session.execute(delete(Permission_assignment).where(Permission_assignment.permission.in_(permissions)))
