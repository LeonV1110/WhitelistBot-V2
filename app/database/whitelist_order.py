import random
from pymysql.connections import Connection
from app.database.whitelist import Whitelist
from app import config as cfg
from exceptions import InsufficientTier, DuplicatePlayerPresent, SelfDestruct, WhitelistNotFound

class WhitelistOrder():
    BOTID: str
    orderID: str
    tier: str #TODO, maybe make into a tierclass instead of a String
    whitelists: list[Whitelist]
    active: bool
    
    def __eq__(self, __o: object) -> bool:
        return self.__dict__ == __o.__dict__

    def __init__(self, BOTID: str, orderID: str, tier: str, whitelists: list[Whitelist] = [], active: bool = True):
        self.BOTID = BOTID
        self.orderID = orderID
        self.tier = tier
        self.whitelists = whitelists
        self.active = active
        return

    def insert_order(self, connection: Connection):
        sql = "INSERT INTO `whitelist_order` (`orderID`, `BOTID`, `tier`, `active`) VALUES (%s, %s, %s, %s)"
        vars = (self.orderID, self.BOTID, self.tier, int(self.active))
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)

        owner_whitelist = Whitelist(self.BOTID, self.orderID)
        owner_whitelist.insert_whitelist()
        return

    def update_order_tier(self, connection: Connection, tier:str):
        self.tier = tier

        if self.active:
            if len(self.whitelists) > cfg.WHITELIST_ALLOWANCE[tier]:
                self.active = False
        else:
            if len(self.whitelists) <= cfg.WHITELIST_ALLOWANCE[tier]:
                self.active = True

        sql = "UPDATE `whitelist_order` SET `active` = %s, `tier` = %s WHERE `ORDERID` = %s"
        vars = (int(self.active), tier , self.orderID)
        
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)

        if not self.active: raise InsufficientTier()
        return

    def update_order_activity(self, connection: Connection):
        if self.active:
            if len(self.whitelists) > cfg.WHITELIST_ALLOWANCE[self.tier]:
                self.active = False
        else:
            if len(self.whitelists) <= cfg.WHITELIST_ALLOWANCE[self.tier]:
                self.active = True
        
        sql = "UPDATE `whitelist_order` SET `active` = %s WHERE `ORDERID` = %s"
        vars = (int(self.active), self.orderID)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
        return

    def delete_order(self, connection: Connection):
        for whitelist in self.whitelists:
            whitelist.delete_whitelist(connection)
        sql = "DELETE FROM `whitelist_order` WHERE `orderID` = %s"
        vars = (self.orderID)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
        return
    
    def add_whitelist(self, connection: Connection, BOTID: str):
        for whitelist in self.whitelists:
            if whitelist.BOTID == BOTID:
                raise DuplicatePlayerPresent("This player is already present on your whitelist subscription.")
        
        if len(self.whitelists) + 1 <= cfg.WHITELIST_ALLOWANCE[self.tier]:
            Whitelist(BOTID, self.orderID).insert_whitelist(connection)
        else:
            raise InsufficientTier("Your whitelist subscription tier is insufficient to add any more whitelists")
        return
            
    def remove_whitelist(self, connection: Connection, BOTID: str):
        if BOTID == self.BOTID:
            raise SelfDestruct()
        for whitelist in self.whitelists:
            if whitelist.BOTID == BOTID:
                whitelist.delete_whitelist(connection)
                self.whitelists.remove(whitelist)
                self.update_order_activity(connection)
                return
        raise WhitelistNotFound()
    
class NewWhitelistOrder(WhitelistOrder):
    def __init__(self, BOTID: str, tier: str, connection: Connection):
        orderID = NewWhitelistOrder.__generate_orderID(connection)
        super().__init__(BOTID, orderID, tier, [])
    
    @staticmethod
    def __generate_orderID(connection: Connection) -> str:
        orderID: int = 1
        while orderID == 1 or NewWhitelistOrder.__check_orderID_pressence(orderID, connection):
            orderID = random.randint(1111111111111111, 9999999999999999) #16 long ID
        return str(orderID)
    
    @staticmethod
    def __check_orderID_pressence(orderID, connection: Connection) -> bool:
        sql = "SELECT * FROM `whitelist_order` WHERE `orderID` = %s"
        vars = (orderID)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
            res = cursor.fethone()
        return res(bool)
    
class DatabaseWhitelistOrder(WhitelistOrder):
    def __init__(self, BOTID, connection: Connection):
        sql = "SELECT * FROM `whitelist_order` WHERE `BOTID` = %s"
        vars = (BOTID)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
            res = cursor.fetchone()
        orderID = res['orderID']
        tier = res['tier']
        whitelists = DatabaseWhitelistOrder.get_all_whitelists(orderID=orderID, connection=connection)
        active = res['active']
        super().__init__(BOTID, orderID, tier, whitelists, active)

    @staticmethod
    def get_all_whitelists(orderID, connection: Connection) -> list:
        sql = "select * from `whitelist` where `orderID` = %s"
        vars = (orderID)
        with connection.cursor() as cursor:
            cursor.execute(sql, vars)
            res = cursor.fetchall()
        wl_list = []
        for wl_dict in res:
            whitelist = Whitelist(wl_dict['BOTID'], wl_dict['orderID'])
            wl_list.append(whitelist)
        return wl_list

class OrderIDWhitelistOrder(WhitelistOrder):
    def __init__(self, orderID, connection: Connection):
        sql = "SELECT * FROM `whitelist_order` WHERE `orderID` = %s"
        vars = (orderID)
        with connection.cursor() as cursor:
            cursor.executer(sql, vars)
            res = cursor.fetchone()
        BOTID = res['BOTID']
        tier = res['tier']
        whitelists = DatabaseWhitelistOrder.get_all_whitelists(orderID)
        active = res['active']

        super().__init__(BOTID, orderID, tier, whitelists, active)