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
        self.help = 'Join voice channels. vc:VoiceChannelName s:Server'

    async def on_message(self, message, trigger):
            msg = PluginBase.Command(message)

            keywords = msg.keyword_commands(('vc:', 's:'))
            vc = None
            if message.server:
                try:
                    vc = Globals.disco.voice_client_in(message.server)
                    if vc:  # already on a channel
                        await vc.move_to(discord.utils.get(message.server.channels, name=keywords['vc:'], type=discord.ChannelType.voice))
                    else:  # join channel if not joined on any
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
                            vc = Globals.disco.voice_client_in(server)
                            if vc:  # already on a channel
                                await vc.move_to(discord.utils.get(server.channels, name=keywords['vc:'], type=discord.ChannelType.voice))
                            else:  # join channel if not joined on any
                                await Globals.disco.join_voice_channel(discord.utils.get(server.channels, name=keywords['vc:'], type=discord.ChannelType.voice))
                    return True
                except Exception as e:
                    Globals.log.error(f'Could not join channel: {str(e)}')
                    await Globals.disco.send_message(message.channel, 'Can\'t join that channel')
                    return False
