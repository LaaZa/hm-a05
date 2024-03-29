import nextcord

from modules.globals import Globals
from modules.pluginbase import PluginBase


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        super().__init__()
        self.type = PluginBase.PluginType.CORE
        self.name = 'join'
        self.add_trigger('on_message', 'join', True, self.on_message)
        self.help = 'Join voice channels. vc:VoiceChannelName g:Guild'

    async def on_message(self, message, trigger):
        msg = PluginBase.Command(message)

        keywords = msg.keyword_commands(('vc', 'g'), strip=True)

        vc = None
        if message.guild:
            try:
                vc = message.guild.voice_client
                if vc:  # already on a channel
                    if len(keywords) <= 0 and message.author.voice.channel:
                        await vc.move_to(nextcord.utils.get(message.guild.channels, id=message.author.voice.channel.id))
                    else:
                        await vc.move_to(nextcord.utils.get(message.guild.channels, name=keywords['vc']))
                else:  # join channel if not joined on any
                    if len(keywords) <= 0 and message.author.voice.channel:
                        await nextcord.utils.get(message.guild.channels, id=message.author.voice.channel.id).connect()
                    else:
                        await nextcord.utils.get(message.guild.channels, name=keywords['vc']).connect()
                if Globals.permissions.client_has_discord_permissions(('manage_messages',), message.channel):
                    Globals.log.error('Deleting message')
                    await message.delete()
                return True
            except Exception as e:
                Globals.log.error(f'Could not join channel: {str(e)}')
                await message.channel.send('Can\'t join that channel')
                return False
        else:
            try:
                for guild in Globals.disco.guilds:
                    if guild.name == keywords['g']:
                        vc = guild.voice_client
                        if vc:  # already on a channel
                            await vc.move_to(nextcord.utils.get(guild.channels, name=keywords['vc']))
                        else:  # join channel if not joined on any
                            await nextcord.utils.get(guild.channels, name=keywords['vc']).connect()
                if Globals.permissions.client_has_discord_permissions(('manage_messages',), message.channel):
                    Globals.log.error('Deleting message')
                    await message.delete()
                return True
            except Exception as e:
                Globals.log.error(f'Could not join channel: {str(e)}')
                await message.channel.send('Can\'t join that channel')
                return False
