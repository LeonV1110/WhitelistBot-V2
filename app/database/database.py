import pymysql
import app.config as cfg

def connect_database() -> pymysql.connections.Connection:
    connection = pymysql.connect(host=cfg.DATABASEHOST, port = int(cfg.DATABASEPORT), user = cfg.DATABASEUSER, password= cfg.DATABASEPSW, charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor, database=cfg.DATABASENAME)
    return connection