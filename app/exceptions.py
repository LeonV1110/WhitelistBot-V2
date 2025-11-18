class MyException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class PlayerNotFound(MyException):
    def __init__(self, message:str = "Player is not registed or was not found."):
        self.message = message
        super().__init__(self.message)

class DuplicatePlayerPresent(MyException):
    def __init__(self, message:str="There is already a player with this steam64 or discord ID."):
        self.message = message
        super().__init__(self.message)

class DuplicatePlayerPresentSteam(DuplicatePlayerPresent):
    def __init__(self, message:str="There is already a player with this steam64 ID."):
        self.message = message
        super().__init__(self.message)

class DuplicatePlayerPresentDiscord(DuplicatePlayerPresent):
    def __init__(self, message:str="There is already a player with this discord ID."):
        self.message = message
        super().__init__(self.message)

class DuplicatePlayerPresentBOTID(DuplicatePlayerPresent):
    def __init__(self, message:str="There is already a player with this BOTID."):
        self.message = message
        super().__init__(self.message)

class InvalidSteam64ID(MyException):
    def __init__(self, message:str = "This is not a valid steam64ID."):
        self.message = message
        super().__init__(self.message)

class InvalidDiscordID(MyException):
    def __init__(self, message:str = "This is not a valid discordID."):
        self.message = message
        super().__init__(self.message)

class InsufficientTier(MyException):
    def __init__(self, message:str = "Your whitelist tier is insufficient for the current amount of whitelists."):
        self.message = message
        super().__init__(self.message)

class WhitelistOrderNotFound(MyException):
    def __init__(self, message:str = "You do not have an (active) whitelist subscription."):
        self.message = message
        super().__init__(self.message)

class WhitelistNotFound(MyException):
    def __init__(self, message:str = "This player does not have a whitelist on your subscription."):
        self.message = message
        super().__init__(self.message)

class SelfDestruct(MyException):
    def __init__(self, message:str = "This is your own steam64ID, you cannot remove yourself from your own subscription."):
        self.message = message
        super().__init__(self.message)

class FFS(MyException):
    def __init__(self, message:str = "????????"):
        self.message = message
        super().__init__(self.message)
