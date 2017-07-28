import urbandictionary as ud

from modules.globals import Globals
from modules.pluginbase import PluginBase


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.UNCORE
        self.name = 'urban'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'ud', True, self.on_message)
        self.trigger = t.functions
        self.help = 'Searches for a word in Urban dictionary and returns the top result'

    async def on_message(self, message, trigger):
        try:
            msg = self.Command(message)
            defs = ud.define(' '.join(msg.parts[1:]))
            await message.channel.send(defs[0].definition)
        except Exception as e:
            Globals.log.error(f'Viesti: {str(e)}')
            await message.channel.send('Something went wrong')
            return False
