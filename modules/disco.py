import sys
import discord
import copy

from modules.globals import Globals


class Disco(discord.Client):

    def __init__(self, token):
        self.__token = token
        super().__init__()

    async def login(self):
        try:
            Globals.log.info(f'Logging in')
            await super().login(self.__token)
        except (discord.LoginFailure, discord.HTTPException, TypeError) as e:
            Globals.log.error(f'Login failed: {e}')

    async def connect(self):
        try:
            await super().connect()
            super().opus.load_opus('libopus')
        except (discord.GatewayNotFound, discord.ConnectionClosed) as e:
            Globals.log.error(f'Connection failed: {e}')

    async def logout(self):
        Globals.log.info(f'Logging out')
        await super().logout()

    def quit(self):
        Globals.log.info(f'Quitting')
        sys.exit()

    class DataMessage:

        def __init__(self, obj):
            self.message = obj
            self.data = dict()
