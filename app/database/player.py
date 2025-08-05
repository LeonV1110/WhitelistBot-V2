"""Player class and subclasses"""

from pymysql.connections import Connection
from app.database.permission import Permission
from app.database.whitelist_order import WhitelistOrder, NewWhitelistOrder, DatabaseWhitelistOrder, OrderIDWhitelistOrder
from app.exceptions import DuplicatePlayerPresentSteam, DuplicatePlayerPresentDiscord
from app.util2 import generate_ID


class Player():
    """Represents the Player table in the database"""
    BOTID: str
    steam64ID: str
    discordID: str
    name: str
    patreonID: str = None #Currently not used
    permission: Permission = None #TODO add class
    whitelist_order: WhitelistOrder = None  #TODO add class

    def __init__(self, BOTID: str, steam64ID: str, discordID: str, name: str, permission: Permission = None, whitelist_order: WhitelistOrder = None):
        self.BOTID = BOTID
        self.steam64ID = steam64ID
        self.discordID = discordID
        self.name = name
        if permission is not None:
            self.permission = permission
        if whitelist_order is not None:
            self.whitelist_order = whitelist_order

    def __eq__(self, __o: object) -> bool:
        return self.__dict__ == __o.__dict__

    def insert_player(self, connection: Connection):
        sql = "INSERT INTO `player` (`BOTID`, `steam64ID`, `discordID`, `name`, `patreonID`) VALUES (%s, %s, %s, %s, %s)"
        vars = (self.BOTID, self.steam64ID, self.discordID, self.name, self.patreonID)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
        if self.whitelist_order is not None:
            self.whitelist_order.insert_order(connection)
        if self.permission is not None:
            self.permission.insert_permission(connection)
        return

    def delete_player(self, connection: Connection):
        if self.whitelist_order is not None:
            self.whitelist_order.delete_order()
        if self.permission is not None:
            self.permission.delete_permission()
        #Delete any whitelists
        sql = "DELETE FROM `whitelist` WHERE `BOTID` = %s "
        vars = (self.BOTID)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)

        #Delete the actual player
        sql = "DELETE FROM `player` WHERE `BOTID` = %s"
        vars = (self.BOTID)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
        return

    def update_player(self, connection: Connection, steam64ID:str=None, discordID:str=None, name:str=None, permission_str:str = None, tier:str = None):
        if steam64ID is None:
            steam64ID = self.steam64ID
        if discordID is None:
            discordID = self.discordID
        if name is None:
            name = self.name
        if permission_str is None:
            if self.permission is None:
                return
            else:
                self.permission.delete_permission(connection)
        else:
            if self.permission is None:
                self.permission = Permission(self.BOTID, connection)
                self.permission.insert_permission(connection)
            else:
                self.permission.update_permission(permission_str, connection)

        if tier is not None:
            if self.whitelist_order is not None:
                self.whitelist_order.update_order_tier(connection, tier)
            else:
                self.add_whitelist_order(tier, connection)

    def add_whitelist_order(self, tier, connection: Connection):
        self.whitelist_order = NewWhitelistOrder(self.BOTID, tier, connection)
        self.whitelist_order.insert_order(connection)

    def update_whitelist_order(self, tier, connection: Connection):
        self.whitelist_order.update_order_tier(tier, connection)

    # Checks both for pressence of whitelist and if the order is active
    def check_whitelist(self, connection: Connection):
        sql = "SELECT * FROM `whitelist` WHERE `BOTID` = %s"
        vars = (self.BOTID)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
            whitelistTable = cursor.fetchone()
        if whitelistTable:
            orderID = whitelistTable['orderID']
            whitelistOrder = OrderIDWhitelistOrder(connection, orderID)
            return bool(whitelistOrder.active)
        else: return False

    def check_duplicate_player(self, connection: Connection):
        self.check_duplicate_player_discord(connection)
        self.check_duplicate_player_steam(connection)

    def check_duplicate_player_steam(self, connection: Connection):
        sql = "SELECT * FROM `player` WHERE `steam64ID` = %s"
        vars = (self.steam64ID)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
            res = cursor.fetchone()
        if bool(res): raise DuplicatePlayerPresentSteam()
        else: return

    def check_duplicate_player_discord(self, connection: Connection):
        sql = "SELECT * FROM `player` WHERE `discordID` = %s"
        vars = (self.discordID)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
            res = cursor.fetchone()
        if bool(res): 
            raise DuplicatePlayerPresentDiscord("You have already registered, if you want to update your Steam64 ID use the command /change_steam64id.")
        else: return

    def check_for_duplicate_player_in_DB(self, steam64ID, connection: Connection):
        sql = "SELECT * FROM `player` WHERE `steam64ID` = %s AND NOT `BOTID` = %s"
        vars = (steam64ID, self.BOTID)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
            res = cursor.fetchone()
        if bool(res):
            raise DuplicatePlayerPresentSteam()
        return

    #checks who's whitelist order you're on, and returns their BOTID
    def check_whos_whitelist_order(self, connection: Connection):
        if self.whitelist_order is not None:
            return self.BOTID
        else:
            sql = "SELECT * FROM `whitelist` WHERE `BOTID` = %s"
            vars = (self.BOTID)
            with connection.cursor() as cursor:
                cursor.execute(sql, vars)
                whitelistTable = cursor.fetchone()
            if whitelistTable:
                orderID = whitelistTable['OrderID']
                whitelistOrder = OrderIDWhitelistOrder(connection, orderID)
                return whitelistOrder.BOTID
            else:
                return "No whitelist" #TODO maybe raise an WhitelistNotFound error instead

    @staticmethod
    def get_permission(BOTID: str, connection: Connection):
        sql = "SELECT * FROM `permission` WHERE `BOTID` = %s"
        vars = (BOTID)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
            res = cursor.fetchone()
        if bool(res): return res['permission']
        else: return None


###########################
####### SUBCLASSES ########
###########################

class NewPlayer(Player):
    def __init__(self, connection: Connection, steam64ID: str, discordID: str, name: str, permission_string: str = None, whitelist_tier: str = None, ):
        BOTID = generate_ID(connection, "BOTID")
        if permission_string is not None:
            permission = Permission(BOTID, permission_string)
        else:
            permission = None
        if whitelist_tier is not None:
            whitelist_order = NewWhitelistOrder(BOTID=BOTID, tier=whitelist_tier, connection=connection)
        else: 
            whitelist_order = None
        super().__init__(BOTID, steam64ID, discordID, name, permission, whitelist_order)

class DatabasePlayer(Player):
    def __init__(self, discordID: str, connection: Connection):

        sql = "SELECT * FROM `player` WHERE `discordID` = %s"
        vars = (discordID)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
            res = cursor.fetchone()
        
        steam64ID = res["steam64ID"]
        name = res["name"]
        BOTID = res["BOTID"]
        permission = DatabasePlayer.get_permission(BOTID=BOTID, connection=connection)
        whitelist_order = DatabaseWhitelistOrder(BOTID, connection)

        super().__init__(BOTID, steam64ID, discordID, name, permission, whitelist_order)

class SteamPlayer(Player):
    def __init__(self, steam64ID: str, connection: Connection):

        sql = "SELECT * FROM `player` WHERE `steam64ID` = %s"
        vars = (steam64ID)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
            res = cursor.fetchone()
        
        discordID = res["discordID"]
        name = res["name"]
        BOTID = res["BOTID"]
        permission = DatabasePlayer.get_permission(BOTID=BOTID, connection=connection)
        whitelist_order = DatabaseWhitelistOrder(BOTID, connection)

        super().__init__(BOTID, steam64ID, discordID, name, permission, whitelist_order)

class BOTIDPlayer(Player):
    def __init__(self, BOTID: str, connection: Connection):

        sql = "SELECT * FROM `player` WHERE `BOTID` = %s"
        vars = (BOTID)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
            res = cursor.fetchone()
        steam64ID = res["steam64ID"]
        discordID = res["discordID"]
        name = res["name"]
        permission = DatabasePlayer.get_permission(BOTID=BOTID, connection=connection)
        whitelist_order = DatabaseWhitelistOrder(BOTID, connection)

        super().__init__(BOTID, steam64ID, discordID, name, permission, whitelist_order)
