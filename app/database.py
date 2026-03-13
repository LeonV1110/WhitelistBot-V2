from sqlalchemy import Column, String, Integer, ForeignKey, CheckConstraint, Boolean, UniqueConstraint, create_engine, select, or_
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, Session
import app.events
from app.exceptions import PlayerNotFound, RoleNotFound
from __future__ import annotations

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'

    player_id           = Column(String(36), primary_key=True)
    name                = Column(String, nullable=False)
    discord_id          = Column(String(19), nullable=False, unique=True)
    steam64_id          = Column(String(17), nullable=True, unique=True)
    eos_id              = Column(String(32), nullable=True, unique=True)
    #TODO double check if eosID is actually max 32 characters

    whitelist_order     = relationship('Whitelist_order', back_populates='player', uselist=False, cascade="all, delete-orphan")
    role_assignments    = relationship('Role_assignment', back_populates='player', cascade="all, delete-orphan")
    whitelist           = relationship('Whitelist', back_populates='player', cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint('steam64_id IS NOT NULL OR eos_id IS NOT NULL',
                        name = 'player_has_store_id'),
    )

    @classmethod
    def get_by_id(cls, session: Session, id: str) -> Player:
        # Check if id is a UUID, if so it's likely the player_id, to try that
        if len(id) == 36:
            return session.get(cls, id)
        stmt = select(cls).where(or_(
            cls.discord_id == id,
            cls.steam64_id == id,
            cls.eos_id == id,
        ))
        player = session.scalar(stmt)
        if player is None:
            raise PlayerNotFound()
        else:
            return player


class Role_assignment(Base):
    __tablename__ = 'role_assignments'

    player_id   = Column(String(36), ForeignKey('players.player_id'), primary_key=True)
    role_id     = Column(String(36), ForeignKey('roles.role_id'), primary_key=True)
    #TODO add server assignment

    player      = relationship('Player', back_populates='role_assignments', uselist=False)
    role        = relationship('Role', back_populates='role_assignments', uselist=False)

class Role(Base):
    __tablename__ = 'roles'

    role_id     = Column(String(36), primary_key=True)
    name        = Column(String, nullable= False)

    @classmethod
    def get_by_name(cls, session:Session, name: str) -> Role:
        stmt = select(cls).where(cls.name == name)
        role = session.scalar(stmt)
        if role is None:
            raise RoleNotFound()
        else:
            return role

    permission_assignment   = relationship('Permission_assignment', back_populates='role', cascade="all, delete-orphan")
    role_assignments        = relationship('Role_assignment', back_populates='role', uselist=False, cascade="all, delete-orphan")

class Permission_assignment(Base):
    __tablename__ = 'permission_assignments'

    permission_id   = Column(String(36), ForeignKey('permissions.permission_id'), primary_key=True)
    role_id         = Column(String(36), ForeignKey('roles.role_id'), primary_key=True)

    role            = relationship('Role', back_populates='permission_assignment', uselist=False)
    permissions      = relationship('Permission', back_populates='permission_assignments')

class Permission(Base):
    __tablename__ = 'permissions'

    permission_id   = Column(String(36), primary_key=True)
    name            = Column(String, nullable=False)

    permission_assignments = relationship('Permission_assignment', back_populates='permissions', cascade="all, delete-orphan")

class Whitelist_order(Base):
    __tablename__ = 'whitelist_orders'

    order_id        = Column(String(36), primary_key=True)
    player_id       = Column(String(36), ForeignKey('players.player_id'), nullable=False)
    tier            = Column(Integer, nullable=False)
    active          = Column(Boolean, default=True, nullable=False)
    whitelist_count = Column(Integer, default=0)

    player          = relationship('Player', back_populates='whitelist_order', uselist = False)
    whitelists      = relationship('Whitelist', back_populates='whitelist_order', cascade="all, delete-orphan")

    def check_and_update_whitelist_count(self) -> None | tuple[int, int]:
        """Counts the number of whitelists on the current state in the session and updates it if wrong
        returns tuple of (old, new) if updated
        should always be used in conjunction with check_and_update_active"""
        new_count = len(self.whitelists)
        old_count = self.whitelist_count
        if old_count != new_count:
            self.whitelist_count = new_count
            return (old_count, new_count)

    def check_and_update_active(self) -> None | bool:
        """checks if the tier is sufficient
        assumes whitelist count is correct
        returns new value if updated"""
        if not self.active and self.tier >= self.whitelist_count:
            self.active = True
        elif self.active and self.tier < self.whitelist_count:
            self.active = False

    __table_args__ = (
        CheckConstraint('NOT active OR whitelist_count <= tier', name='whitelist_limit'),
        UniqueConstraint('player_id', name='one_active_order_per_player'),
    )

class Whitelist(Base):
    __tablename__ = 'whitelists'

    order_id    = Column(String(36), ForeignKey('whitelist_orders.order_id'), primary_key=True)
    player_id   = Column(String(36), ForeignKey('players.player_id'), primary_key=True)

    whitelist_order = relationship('Whitelist_order', back_populates='whitelists')
    player          = relationship('Player', back_populates='whitelist')

engine = create_engine('sqlite:///test.db', echo=True)
Session_ = sessionmaker(bind=engine)
session = Session_()
Base.metadata.create_all(engine)

#wl = Whitelist(order_id = 'testing', player_id = 'testing12')
#session.add(wl)
session.commit()
