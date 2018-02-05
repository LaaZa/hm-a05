from modules.globals import Globals
from modules.pluginbase import PluginBase


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.CORE
        self.name = 'leave'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'leave', True, self.on_message)
        self.trigger = t.functions
        self.help = 'Leave from voice channels. g:Guild'

    async def on_message(self, message, trigger):
        msg = PluginBase.Command(message)

        keywords = msg.keyword_commands(('g',))

        vc = None
        if message.guild:
            try:
                vc = message.guild.voice_client
                if vc:  # already on a channel
                    await vc.disconnect()
                else:  # join channel if not joined on any
                    await message.channel.send('Not on voice channel')
                if Globals.permissions.client_has_discord_permissions(('manage_messages',), message.channel):
                    Globals.log.debug('Deleting message')
                    await message.delete()
                return True
            except Exception as e:
                Globals.log.error(f'Could not leave channel: {str(e)}')
                await message.channel.send('Can\'t leave voice channel')
                return False
        else:
            try:
                for guild in Globals.disco.guilds:
                    if guild.name == keywords['g']:
                        vc = guild.voice_client
                        if vc:  # already on a channel
                            await vc.disconnect()
                        else:  # join channel if not joined on any
                            await message.channel.send(f'Not on voice channel on {guild.name}')
                if Globals.permissions.client_has_discord_permissions(('manage_messages',), message.channel):
                    Globals.log.error('Deleting message')
                    await message.delete()
                return True
            except Exception as e:
                Globals.log.error(f'Could not leave channel: {str(e)}')
                await message.channel.send('Can\'t leave voice channel')
                return False