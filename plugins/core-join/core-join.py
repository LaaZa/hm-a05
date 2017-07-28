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
                    if len(keywords) <= 0 and message.author.voice_channel:
                        await vc.move_to(discord.utils.get(message.server.channels, id=message.author.voice_channel.id, type=discord.ChannelType.voice))
                    else:
                        await vc.move_to(discord.utils.get(message.server.channels, name=keywords['vc:'], type=discord.ChannelType.voice))
                else:  # join channel if not joined on any
                    if len(keywords) <= 0 and message.author.voice_channel:
                        await Globals.disco.join_voice_channel(discord.utils.get(message.server.channels, id=message.author.voice_channel.id, type=discord.ChannelType.voice))
                    else:
                        await Globals.disco.join_voice_channel(discord.utils.get(message.server.channels, name=keywords['vc:'], type=discord.ChannelType.voice))
                if discord.Permissions(manage_messages=True) >= message.server.get_member(Globals.disco.user.id).permissions_in(message.channel):
                    Globals.log.error('Deleting message')
                    await Globals.disco.delete_message(message)
                return True
            except Exception as e:
                Globals.log.error(f'Could not join channel: {str(e)}')
                await message.channel.send('Can\'t join that channel')
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
                if discord.Permissions(manage_messages=True) <= message.server.get_member(Globals.disco.user.id).permissions_in(message.channel):
                    Globals.log.error('Deleting message')
                    await Globals.disco.delete_message(message)
                return True
            except Exception as e:
                Globals.log.error(f'Could not join channel: {str(e)}')
                await message.channel.send('Can\'t join that channel')
                return False
