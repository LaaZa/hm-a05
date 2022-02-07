import nextcord

from modules.pluginbase import PluginBase


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        super().__init__()
        self.type = PluginBase.PluginType.CORE
        self.name = 'DM with bot'
        self.add_trigger('on_message', 'dm', True, self.on_message)
        self.help = 'Bot starts a DM'

    async def on_message(self, message, trigger):
        if not isinstance(message.channel, nextcord.DMChannel):
            try:
                await message.author.send('Hello!')
                return True
            except Exception as e:
                return False
        else:
            await message.author.send('This is a DM already.')
            return True
