"""Permission class"""
from pymysql.connections import Connection

class Permission():
    """Represents the Permission table in the database"""
    BOTID: str
    permission: str

    def __eq__(self, __o: object) -> bool:
        return self.__dict__ == __o.__dict__

    def __init__(self, BOTID: str, permission: str):
        self.BOTID = BOTID
        self.permission = permission
        return

    def insert_permission(self, connection: Connection):
        sql = "INSERT INTO `permission` (`BOTID`, `permission`) VALUES (%s, %s)"
        vars = (self.BOTID, self.permission)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
        return

    def delete_permission(self, connection: Connection):
        sql = "DELETE FROM `permission` WHERE `BOTID` = %s"
        vars = (self.BOTID)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
        return

    def update_permission(self, permission: str, connection: Connection):
        self.permission = permission
        sql = "UPDATE `permission` SET `permission` = %s WHERE `BOTID` = %s"
        vars = (permission, self.BOTID)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
        return
