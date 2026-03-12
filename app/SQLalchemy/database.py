from sqlalchemy import Column, String, Integer, ForeignKey, CheckConstraint, Boolean, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'

    player_id           = Column(String(36), primary_key=True)
    name                = Column(String, nullable=False)
    discord_id          = Column(String(19), nullable=False)
    steam64_id          = Column(String(17), nullable=True)
    eos_id              = Column(String(32), nullable=True)
    #TODO double check if eosID is actually max 32 characters

    whitelist_order     = relationship('Whitelist_order', back_populates='player')
    role_assignments    = relationship('Role_assignment', back_populates='player')
    whitelist           = relationship('Whitelist', back_populates='player')

    __table_args__ = (
        CheckConstraint('steam64_id IS NOT NULL OR eos_id IS NOT NULL',
                        name = 'player_has_store_id')
    )

class Role_assignment(Base):
    __tablename__ = 'role_assignments'

    player_id   = Column(String(36), ForeignKey('players.player_id'), primary_key=True)
    role_id     = Column(String(36), ForeignKey('roles.role_id'), primary_key=True)
    #TODO add server assignment

    player      = relationship('Player', back_populates='role_assignments')
    role        = relationship('Role', back_populates='role_assignments')

class Role(Base):
    __tablename__ = 'roles'

    role_id     = Column(String(36), primary_key=True)
    name        = Column(String, nullable= False)

    permission_assignment   = relationship('Permission_assignment', back_populates='role')
    role_assignments        = relationship('Role_assignment', back_populates='role')

class Permission_assignment(Base):
    __tablename__ = 'permission_assignments'

    permission_id   = Column(String(36), ForeignKey('permissions.permission_id'), primary_key=True)
    role_id         = Column(String(36), ForeignKey('roles.role_id'), primary_key=True)

    role            = relationship('Role', back_populates='permission_assignment')
    permission      = relationship('Permission', back_populates='permission_assignment')

class Permission(Base):
    __tablename__ = 'permissions'

    permission_id   = Column(String(36), primary_key=True)
    name            = Column(String, nullable=False)

    permission_assignment = relationship('Permission_assignment', back_populates='permission')

class Whitelist_order(Base):
    __tablename__ = 'whitelist_orders'

    order_id        = Column(String(36), primary_key=True)
    player_id       = Column(String(36), ForeignKey('players.player_id'), nullable=False)
    tier            = Column(Integer, nullable=False)
    active          = Column(Boolean, default=True, nullable=False)
    whitelist_count = Column(Integer, default=0)

    player          = relationship('Player', back_populates='whitelist_order')
    whitelists      = relationship('Whitelist', back_populates='whitelist_order')

    __table_args__ = (
        CheckConstraint('NOT active OR whitelist_count <= tier', name='whitelist_limit'),
        UniqueConstraint('player_id', name='one_active_order_per_player')
    )

class Whitelist(Base):
    __tablename__ = 'whitelists'

    order_id    = Column(String(36), ForeignKey('whitelist_orders.order_id'), primary_key=True)
    player_id   = Column(String(36), ForeignKey('players.player_id'), primary_key=True)

    whitelist_order = relationship('Whitelist_order', back_populates='whitelists')
    player          = relationship('Player', back_populates='whitelist')
