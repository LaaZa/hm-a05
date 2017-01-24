import discord
from modules.globals import Globals
from modules.pluginbase import PluginBase


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.CORE
        self.name = 'join'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'join', True, self.on_message)
        self.trigger = t.functions
        self.help = 'just a test'

    async def on_message(self, message, trigger):
            msg = PluginBase.Command(message)

            keywords = msg.keyword_commands(('vc:', 's:'))
            if message.server:
                try:
                    await Globals.disco.join_voice_channel(discord.utils.get(message.server.channels, name=keywords['vc:'], type=discord.ChannelType.voice))
                    return True
                except Exception as e:
                    Globals.log.error(f'Could not join channel: {str(e)}')
                    await Globals.disco.send_message(message.channel, 'Can\'t join that channel')
                    return False
            else:
                try:
                    for server in Globals.disco.servers:
                        if server.name == keywords['s:']:
                            await Globals.disco.join_voice_channel(discord.utils.get(server.channels, name=keywords['vc:'], type=discord.ChannelType.voice))
                    return True
                except Exception as e:
                    Globals.log.error(f'Could not join channel: {str(e)}')
                    await Globals.disco.send_message(message.channel, 'Can\'t join that channel')
                    return False
