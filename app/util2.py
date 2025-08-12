"""A collection of utility functions"""
import random
from pymysql import Connection
from app.exceptions import MyException


def generate_ID(connection: Connection, type: str):
    size = 0
    if type == "BOTID":
        size = 15
    elif type == "ORDERID":
        size = 16
    else:
        raise MyException('You have sucessfully broken the bot :)') #TODO fix error msg
    start_val = int('1'*size)
    end_val = int('9'*size)

    BOTID = 1
    while BOTID == 1 or check_ID_pressence(connection, BOTID, type):
        BOTID = random.randint(start_val, end_val) #15 long ID
    return str(BOTID)

def check_ID_pressence(connection: Connection, ID: int, type: str) -> bool:
    if type == "BOTID":
        sql = "SELECT * FROM `player` WHERE `BOTID` = %s"
    elif type == "ORDERID":
        sql = "SELECT * FROM `whitelist_order` WHERE `BOTID` = %s"
    elif type == "STEAM":
        sql = "SELECT * FROM `player` WHERE `steam64ID` = %s"
    elif type == "DISCORD":
        sql = "SELECT * FROM `player` WHERE `discordID` = %s"
    else:
        raise MyException('You have sucessfully broken the bot :)') #TODO fix error msg
    vars = (str(ID))
    with connection.cursor() as cursor:
        return bool(cursor.execute(sql, vars))
