from discord import Embed, TextStyle, Interaction
from discord.ui import Modal, TextInput
from app.exceptions import MyException
from pymysql import OperationalError
from app import command_logic as cl
from app.database.database import connect_database


class RegisterModal(Modal):
    def __init__(self):
        super().__init__(title='Register',timeout=600)
    
    steam64ID = TextInput(
            label= 'Please provide your Steam64ID.', 
            placeholder='76561198029817168', 
            style=TextStyle.short, 
            max_length=19)

    
    async def on_submit(self, inter: Interaction):
        embed = Embed(title='Registration was successful')
        try:
            print(f"we are registering a player with id: {self.steam64ID}") 
            with connect_database() as connection:
                cl.register_player(connection, member=inter.author, steam64ID=self.steam64ID)
        except MyException as error:
            embed = Embed(title=error.message)
        except OperationalError:
            embed = Embed(
            title="The bot is currently having issues, please try again later.")
        await inter.response.send_message(embed=embed, ephemeral=True)

    async def on_error(self, error: Exception, inter: Interaction):
        await inter.response.send_message(error, ephemeral=True)

class AddFriendModal(Modal):
    def __init__(self):
        super().__init__(title='Add a friend to your whitelist', timeout=600)

    friend_steam64ID = TextInput(
            label= 'Please provide your friends Steam64ID.',
            placeholder='76561198029817168',
            style=TextStyle.short,
            max_length=19
            )

    async def on_submit(self, inter: Interaction):
        embed = Embed(title='Your friend was successfully added')
        try:
            print(f"we are registering a friend with id: {self.friend_steam64ID}") 
            #cl.add_player_to_whitelist(owner_member=inter.author, player_steam64ID=str(steam64ID))
        except MyException as error:
            embed = Embed(title=error.message)
        except OperationalError:
            embed = Embed(
            title="The bot is currently having issues, please try again later.")
        await inter.response.send_message(embed=embed, ephemeral=True)

    async def on_error(self, error: Exception, inter: Interaction):
        await inter.response.send_message(error, ephemeral=True) #TODO may not work?

class UpdateSteamIDModal(Modal):
    def __init__(self):
        super().__init__(title='Change your steam64ID', timeout=600)
    new_steam64ID = TextInput(
            label= 'Please provide your new Steam64ID.',
            placeholder='76561198029817168',
            style=TextStyle.short,
            max_length=19
            )
    

    async def on_submit(self, inter: Interaction):
        embed = Embed(title='Your Steam64ID was successfully updated.')
        try:
            print(f'{self.new_steam64ID}')
            #cl.change_steam64ID(inter.author, steam64ID)
        except MyException as error:
            embed = Embed(title=error.message)
        except OperationalError:
            embed = Embed(
            title="The bot is currently having issues, please try again later.")
        await inter.response.send_message(embed=embed, ephemeral=True)

    async def on_error(self, error: Exception, inter: Interaction):
        await inter.response.send_message(error, ephemeral=True)

class RemoveDataModal(Modal):
    def __init__(self):
        super().__init__(title='Delete yourself from our database.', timeout=600)

    delete = TextInput(
        label="Type 'DELETE' if you want to delete your data",
        placeholder='DELETE',
        style=TextStyle.short,
        max_length=6
    )

    async def on_submit(self, inter: Interaction):
        embed = Embed(title='Your information has been successfully deleted')
        message = str(self.delete)

        if message == "DELETE":
            try:
                print(f'{self.delete}')
                #cl.remove_player(inter.author)
            except MyException as error:
                embed = Embed(title=error.message)
            except OperationalError:
                embed = Embed(
                title="The bot is currently having issues, please try again later.")
        else: 
            embed = Embed(title='Nothing happened, and your data is still in the database.')
        
        await inter.response.send_message(embed=embed, ephemeral=True)

    async def on_error(self, error: Exception, inter: Interaction):
        await inter.response.send_message(error, ephemeral=True)


class RemoveFriendModal(Modal):
    def __init__(self):
        super().__init__(title='Remove a friend from your whitelist', timeout=600)

    friend_steamID = TextInput(
            label= 'Please provide your friends Steam64ID.',
            placeholder='76561198029817168',
            style=TextStyle.short,
            max_length=19
            )

    async def on_submit(self, inter: Interaction):
        embed = Embed(title='Your friend was successfully removed')

        try:
            print(f'{self.friend_steamID}')
            #cl.remove_player_from_whitelist(owner_member=inter.author, player_steam64ID=steam64ID)
        except MyException as error:
            embed = Embed(title=error.message)
        except OperationalError:
            embed = Embed(
            title="The bot is currently having issues, please try again later.")
        await inter.response.send_message(embed=embed, ephemeral=True)

    async def on_error(self, error: Exception, inter: Interaction):
        await inter.response.send_message(error, ephemeral=True)