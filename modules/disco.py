import sys
import discord

from modules.globals import Globals


class Disco(discord.Client):

    def __init__(self, token):
        self.__token = token
        if not discord.opus.is_loaded():
            try:
                discord.opus.load_opus('opus')
            except OSError as e:
                Globals.log.info(f'Opus codec could not be loaded: {str(e)}')
            else:
                Globals.log.info('Opus codec loaded')
        else:
            Globals.log.info('Opus codec loaded')
        super().__init__()

    async def login(self):
        try:
            Globals.log.info(f'Logging in')
            await super().login(self.__token)
        except (discord.LoginFailure, discord.HTTPException, TypeError) as e:
            Globals.log.error(f'Login failed: {e}')

    async def logout(self):
        Globals.log.info(f'Logging out')
        await super().logout()

    def quit(self):
        Globals.log.info(f'Quitting')
        sys.exit()

    async def say(self, channel, content):
        await self.send_typing(channel)
        await self.send_message(channel, content)

    class DataMessage:

        def __init__(self, obj):
            self.message = obj
            self.data = dict()
