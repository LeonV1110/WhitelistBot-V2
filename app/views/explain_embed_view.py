from discord.ui import View, button, Button
from discord import Interaction, ButtonStyle, Embed
from app.modals import RegisterModal, AddFriendModal, UpdateSteamIDModal, RemoveDataModal, RemoveFriendModal
from app.exceptions import MyException
from pymysql import OperationalError

class ExplainEmbedView(View):
    def __init__(self):
        super().__init__(timeout=None)

    #@button(label= "testing", custom_id="testing12")
    #async def something(self, inter: Interaction, button: Button):
    #    await inter.response.send_message("It worked!")

    @button(style = ButtonStyle.primary,label='Register', custom_id='embed:register')
    async def register(self, inter: Interaction, button: Button):
        await inter.response.send_modal(RegisterModal())

    @button(style = ButtonStyle.primary,label='Add a Friend', custom_id='embed:add_friend')
    async def add_friend(self, inter: Interaction, button: Button):
        await inter.response.send_modal(AddFriendModal())

    @button(style=ButtonStyle.primary, label='Change My Steam64ID', custom_id='embed:update_steamID')
    async def update_steamID(self, inter: Interaction, button: Button):
        await inter.response.send_modal(UpdateSteamIDModal())

    @button(style=ButtonStyle.secondary, label='Get My Info', custom_id='embed:get_player_info')
    async def get_player_info(self, inter: Interaction, button: Button):
        await inter.response.defer(ephemeral=True)

        try:
            embed = Embed(title='player info placeholder')
            #embed = cl.get_player_info(member = inter.author) #TODO
        except MyException as error:
            embed = Embed(title= error.message)
        except OperationalError:
            embed = Embed(title= "The bot is currently having issues, please try again later.")

        await inter.followup.send(embed= embed, ephemeral=True)


    @button(style=ButtonStyle.secondary, label='Get My Whitelist Info', custom_id='embed:get_whitelist_info')
    async def get_whitelist_info(self, inter: Interaction, button: Button):
        await inter.response.defer(ephemeral=True)

        try:
            embed = Embed(title='whitelist info placeholder')
            #embed = cl.get_whitelist_info(member = inter.author) #TODO
        except MyException as error:
            embed = Embed(title= error.message)
        except OperationalError:
            embed = Embed(title= "The bot is currently having issues, please try again later.")

        await inter.followup.send(embed= embed, ephemeral=True)


    @button(style=ButtonStyle.secondary, label='Update My Data', custom_id='embed:update_data')
    async def update_data(self, inter: Interaction, button: Button):
        await inter.response.defer(ephemeral=True)
        embed = Embed(title='Your data was successfully updated.')

        try:
            print('updating data')
            #cl.update_player_from_member(member=inter.author) #TODO
        except MyException as error:
            embed = Embed(title= error.message)
        except OperationalError:
            embed = Embed(title= "The bot is currently having issues, please try again later.")

        await inter.followup.send(embed= embed, ephemeral=True)

    @button(style = ButtonStyle.red, label='Delete My Data', custom_id='embed:remove_data')
    async def remove_data(self, inter:Interaction, button: Button):
        await inter.response.send_modal(RemoveDataModal())

    @button(style = ButtonStyle.red, label='Remove a Friend', custom_id='embed:remove_fried')
    async def remove_fried(self, inter:Interaction, button: Button):
        await inter.response.send_modal(RemoveFriendModal())
    