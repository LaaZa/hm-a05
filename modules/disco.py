import sys

import nextcord

from modules.globals import Globals, SavedVar


class Disco(nextcord.Client):

    def __init__(self, token):
        self.__token = token

        '''
        if not nextcord.opus.is_loaded():
            try:
                nextcord.opus.load_opus('opus')
            except OSError as e:
                Globals.log.info(f'Opus codec could not be loaded: {str(e)}')
            else:
                Globals.log.info('Opus codec loaded')
        else:
            Globals.log.info('Opus codec loaded')
        '''

        super().__init__(intents=nextcord.Intents.all())

    def run(self, *args, **kwargs):
        super().run(self.__token)

    async def login(self, token):
        try:
            Globals.log.info(f'Logging in')
            await super().login(self.__token)
        except (nextcord.LoginFailure, nextcord.HTTPException, TypeError) as e:
            Globals.log.error(f'Login failed: {e}')

    async def logout(self):
        Globals.log.info(f'Logging out')
        SavedVar.save()
        await super().close()

    def quit(self):
        Globals.log.info(f'Quitting')
        SavedVar.save()
        sys.exit()

    async def say(self, channel, content):
        await channel.typing()
        await channel.send(content)

    class DataMessage:

        def __init__(self, obj):
            self.message = obj
            self.data = dict()
