class MyException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class PlayerNotFound(MyException):
    def __init__(self, message = "Player is not registed or was not found."):
        self.message = message
        super().__init__(self.message)

class DuplicatePlayerPresent(MyException):
    def __init__(self, message="There is already a player with this steam64 or discord ID."):
        self.message = message
        super().__init__(self.message)

class DuplicatePlayerPresentSteam(DuplicatePlayerPresent):
    def __init__(self, message="There is already a player with this steam64 ID."):
        self.message = message
        super().__init__(self.message)

class DuplicatePlayerPresentDiscord(DuplicatePlayerPresent):
    def __init__(self, message="There is already a player with this discord ID."):
        self.message = message
        super().__init__(self.message)

class DuplicatePlayerPresentBOTID(DuplicatePlayerPresent):
    def __init__(self, message="There is already a player with this BOTID."):
        self.message = message
        super().__init__(self.message)

class InvalidSteam64ID(MyException):
    def __init__(self, message = "This is not a valid steam64ID."):
        self.message = message
        super().__init__(self.message)

class InvalidDiscordID(MyException):
    def __init__(self, message = "This is not a valid discordID."):
        self.message = message
        super().__init__(self.message)

class InsufficientTier(MyException):
    def __init__(self, message = "Your whitelist tier is insufficient for the current amount of whitelists."):
        self.message = message
        super().__init__(self.message)

class WhitelistNotFound(MyException):
    def __init__(self, message = "This player does not have a whitelist on your subscription."):
        self.message = message
        super().__init__(self.message)

class SelfDestruct(MyException):
    def __init__(self, message = "This is your own steam64ID, you cannot remove yourself from your own subscription."):
        self.message = message
        super().__init__(self.message)

class FFS(MyException):
    def __init__(self, message = "????????"):
        self.message = message
        super().__init__(self.message)
