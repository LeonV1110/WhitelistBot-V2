from sqlalchemy import event, inspect
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from app.database import Whitelist, Whitelist_order

# automatically enable foreign keys when sqlite is used
@event.listens_for(Engine, "connect")
def enable_sqlite_fk(dbapi_conn, conn_record):
    try:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
    except Exception as e:
        pass #TODO find correct exception to use


# Auto update whitelist count from within this app
@event.listens_for(Session, "before_flush")
def update_whitelist_counts(session, flush_context, instances):

    def change(order, delta):
        if order:
            order.whitelist_count += delta

    # New whitelist rows
    for obj in session.new:
        if isinstance(obj, Whitelist):
            change(obj.order, +1)

    # Deleted whitelist rows
    for obj in session.deleted:
        if isinstance(obj, Whitelist):
            change(obj.order, -1)

    # Updated rows (moved to another order)
    for obj in session.dirty:
        if not isinstance(obj, Whitelist):
            continue

        hist = inspect(obj).attrs.order_id.history
        if not hist.has_changes():
            continue

        # Old order loses one slot
        if hist.deleted:
            old_order = session.get(Whitelist_order, hist.deleted[0])
            change(old_order, -1)

        # New order gains one slot
        if hist.added:
            new_order = session.get(Whitelist_order, hist.added[0])
            change(new_order, +1)
