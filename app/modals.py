"""Contians all modals"""
from discord import Embed, TextStyle, Interaction
from discord.ext.commands import Context
from discord.ui import Modal, TextInput
from app import command_logic as cl
from app.util import connect_database, command_error_embed_gen

class RegisterModal(Modal):
    def __init__(self):
        super().__init__(title='Register',timeout=600)

    steam64ID = TextInput(
            label= 'Please provide your Steam64ID.',
            placeholder='76561198029817168',
            style=TextStyle.short,
            max_length=19)

    async def on_submit(self, inter: Interaction):
        print(f"we are registering a player with id: {self.steam64ID}")
        with connect_database() as connection:
            cl.register_player(connection, member=inter.user, steam64ID=str(self.steam64ID))
            connection.commit()
        await inter.response.send_message(embed=Embed(title='Registration was successful'), ephemeral=True)

    async def on_error(self, inter: Interaction, error: Exception):
        await inter.response.send_message(embed=command_error_embed_gen(error), ephemeral=True)

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
        print(f"we are registering a friend with id: {self.friend_steam64ID}")
        with connect_database() as connection:
            cl.add_player_to_whitelist(connection, owner_member=inter.user, player_steam64ID=str(self.friend_steam64ID))
            connection.commit()
        await inter.response.send_message(embed=Embed(title='Your friend was successfully added'), ephemeral=True)

    async def on_error(self, inter: Interaction, error: Exception):
        await inter.response.send_message(embed=command_error_embed_gen(error), ephemeral=True)

class UpdateSteamIDModal(Modal):
    def __init__(self):
        super().__init__(title='Change your steam64ID', timeout=600)

    new_steam64ID = TextInput(
            label= 'Please provide your new Steam64ID.',
            placeholder='76561198029817168',
            style=TextStyle.short,
            max_length=19
            )

    async def on_submit(self,  inter: Interaction):
        print(f'We are updating the steam64ID to {self.new_steam64ID}')
        with connect_database() as connection:
            cl.change_steam64ID(connection, inter.user, steam64ID=self.new_steam64ID)
            connection.commit()
        await inter.response.send_message(embed = Embed(title='Your Steam64ID was successfully updated.'), ephemeral=True)

    async def on_error(self, inter: Interaction, error: Exception):
        await inter.response.send_message(embed=command_error_embed_gen(error), ephemeral=True)

class RemoveDataModal(Modal):
    def __init__(self):
        super().__init__(title='Delete yourself from our database.', timeout=600)

    delete = TextInput(
        label="Type 'DELETE' if you want to delete your data",
        placeholder='DELETE',
        style=TextStyle.short,
        max_length=6
    )

    async def on_submit(self,  inter: Interaction):
        embed = Embed(title='Your information has been successfully deleted')
        message = str(self.delete)

        if message == "DELETE":
            print(f'We are deleting the account of {inter.user}')
            with connect_database() as connection:
                cl.remove_player(connection=connection, member = inter.user)
                connection.commit()
        else: 
            embed = Embed(title='Nothing happened, and your data is still in the database.')

        await inter.response.send_message(embed=embed, ephemeral=True)

    async def on_error(self, inter: Interaction, error: Exception):
        await inter.response.send_message(embed=command_error_embed_gen(error), ephemeral=True)

class RemoveFriendModal(Modal):
    def __init__(self):
        super().__init__(title='Remove a friend from your whitelist', timeout=600)

    friend_steamID = TextInput(
            label= 'Please provide your friends Steam64ID.',
            placeholder='76561198029817168',
            style=TextStyle.short,
            max_length=19
            )

    async def on_submit(self,  inter: Interaction):
        embed = Embed(title='Your friend was successfully removed')
        print(f'{self.friend_steamID}')
        with connect_database() as connection:
            cl.remove_player_from_whitelist(connection, owner_member=inter.user, player_steam64ID=self.friend_steamID)
            connection.commit()
        await inter.response.send_message(embed=embed, ephemeral=True)

    async def on_error(self, inter: Interaction, error: Exception):
        await inter.response.send_message(embed=command_error_embed_gen(error), ephemeral=True)
