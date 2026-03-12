"""Whitelist class"""
from pymysql.connections import Connection


class Whitelist():
    """Represents the Whitelist table in the database"""
    BOTID: str
    orderID: str

    def __eq__(self, __o: object) -> bool:
        return self.__dict__ == __o.__dict__

    def __init__(self, BOTID: str, orderID: str):
        self.BOTID = BOTID
        self.orderID = orderID
        return

    def insert_whitelist(self, connection: Connection):
        sql = "INSERT INTO `whitelist` (`BOTID`, `orderID`) VALUES (%s, %s)"
        vars = (self.BOTID, self.orderID)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
        return

    def delete_whitelist(self, connection: Connection):
        sql = "DELETE FROM `whitelist` WHERE `BOTID` = %s"
        vars = (self.BOTID)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
        return

    def update_whitelist(self, orderID: str, connection: Connection):
        self.orderID = orderID
        sql = "UPDATE `whitelist` SET `orderID` = %s WHERE `BOTID` = %s"
        vars = (orderID, self.BOTID)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
        return
