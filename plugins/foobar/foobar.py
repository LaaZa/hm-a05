from modules.globals import Globals
from modules.pluginbase import PluginBase


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.UNCORE
        self.name = 'foobar'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'foo', True, self.on_message)
        t.add_event('on_message', 'hur', True, self.on_message)
        self.trigger = t.functions
        self.help = 'just a test'

    async def on_message(self, message, trigger):
        if trigger == 'foo':
            await Globals.disco.send_message(message.channel, 'bar')
        else:
            await Globals.disco.send_message(message.channel, 'dur', tts=True)
        return True
