import discord

from modules.pluginbase import PluginBase


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.CORE
        self.name = 'DM with bot'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'dm', True, self.on_message)
        self.trigger = t.functions
        self.help = 'Bot starts a DM'

    async def on_message(self, message, trigger):
        if not isinstance(message.channel, discord.DMChannel):
            try:
                await message.author.send('Hello!')
                return True
            except Exception as e:
                return False
        else:
            await message.author.send('This is a DM already.')
            return True
