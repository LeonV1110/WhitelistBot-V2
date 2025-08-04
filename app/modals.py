from discord import Embed, TextStyle, Interaction
from discord.ext.commands import Context
from discord.ui import Modal, TextInput
from app import command_logic as cl
from app.database.database import connect_database
from app.util import command_error_handler

class RegisterModal(Modal):
    def __init__(self):
        super().__init__(title='Register',timeout=600)
    
    steam64ID = TextInput(
            label= 'Please provide your Steam64ID.', 
            placeholder='76561198029817168', 
            style=TextStyle.short, 
            max_length=19)

    async def on_submit(self, ctx: Context):
        print(f"we are registering a player with id: {self.steam64ID}") 
        with connect_database() as connection:
            cl.register_player(connection, member=ctx.author, steam64ID=str(self.steam64ID))
        await ctx.send(embed=Embed(title='Registration was successful'), ephemeral=True)

    async def on_error(self, inter: Interaction, error: Exception):
        await command_error_handler(inter, error)

class AddFriendModal(Modal):
    def __init__(self):
        super().__init__(title='Add a friend to your whitelist', timeout=600)

    friend_steam64ID = TextInput(
            label= 'Please provide your friends Steam64ID.',
            placeholder='76561198029817168',
            style=TextStyle.short,
            max_length=19
            )

    async def on_submit(self, ctx: Context):
        print(f"we are registering a friend with id: {self.friend_steam64ID}") 
        with connect_database() as connection:
            cl.add_player_to_whitelist(connection, owner_member=ctx.author, player_steam64ID=str(self.friend_steam64ID))
        await ctx.send(embed=Embed(title='Your friend was successfully added'), ephemeral=True)

    async def on_error(self, inter: Interaction, error: Exception):
        await command_error_handler(inter, error)

class UpdateSteamIDModal(Modal):
    def __init__(self):
        super().__init__(title='Change your steam64ID', timeout=600)
        
    new_steam64ID = TextInput(
            label= 'Please provide your new Steam64ID.',
            placeholder='76561198029817168',
            style=TextStyle.short,
            max_length=19
            )

    async def on_submit(self,  ctx: Context):
        print(f'We are updating the steam64ID to {self.new_steam64ID}')
        with connect_database() as connection:
            cl.change_steam64ID(connection, ctx.author, steam64ID=self.new_steam64ID)
        await ctx.send(embed = Embed(title='Your Steam64ID was successfully updated.'), ephemeral=True)

    async def on_error(self, inter: Interaction, error: Exception):
        await command_error_handler(inter, error)

class RemoveDataModal(Modal):
    def __init__(self):
        super().__init__(title='Delete yourself from our database.', timeout=600)

    delete = TextInput(
        label="Type 'DELETE' if you want to delete your data",
        placeholder='DELETE',
        style=TextStyle.short,
        max_length=6
    )

    async def on_submit(self,  ctx: Context):
        embed = Embed(title='Your information has been successfully deleted')
        message = str(self.delete)

        if message == "DELETE":
            print(f'We are deleting the account of {ctx.author}')
            with connect_database() as connection:
                cl.remove_player(connection=connection, member = ctx.author)
        else: 
            embed = Embed(title='Nothing happened, and your data is still in the database.')
        
        await ctx.send(embed=embed, ephemeral=True)


    async def on_error(self, inter: Interaction, error: Exception):
        await command_error_handler(inter, error)

class RemoveFriendModal(Modal):
    def __init__(self):
        super().__init__(title='Remove a friend from your whitelist', timeout=600)

    friend_steamID = TextInput(
            label= 'Please provide your friends Steam64ID.',
            placeholder='76561198029817168',
            style=TextStyle.short,
            max_length=19
            )

    async def on_submit(self,  ctx: Context):
        embed = Embed(title='Your friend was successfully removed')
        print(f'{self.friend_steamID}')
        with connect_database() as connection:
            cl.remove_player_from_whitelist(connection, owner_member=ctx.author, player_steam64ID=self.friend_steamID)
        await ctx.send(embed=embed, ephemeral=True)

    async def on_error(self, inter: Interaction, error: Exception):
        await command_error_handler(inter, error)