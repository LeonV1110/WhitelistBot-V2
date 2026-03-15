from app.database import engine, Base, get_session, Permission, Role, Permission_assignment
import app.config as cfg
import uuid7
from sqlalchemy import select, delete, tuple_


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
        perms = [Permission(permission_id = uuid7.create(), name = perm_name) for perm_name in permission_names]
        db_perms = session.scalar(select(Permission.name)).all()
        missing_perms = [perm for perm in perms if perm.name not in db_perms]
        session.add_all(missing_perms)
        session.commit()


def check_and_load_roles() -> None:
    with get_session() as session:
        roles = []
        db_roles = session.scalar(select(Role.name)).all()
        missing_roles = [role for role in roles if role.name not in db_roles]
        session.add_all(missing_roles)
        session.commit()


def check_and_load_perm_assignments() -> None:
    with get_session() as session:
        roles = session.scalars(select(Role)).all()
        role_by_name = {r.name: r for r in roles}
        
        cfg_role_names, _, _ = zip(*cfg.ROLES_CONFIG)

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

        for role_name, _, perms in zip(cfg.ROLES_CONFIG):
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
