from modules.globals import Globals
from modules.pluginbase import PluginBase
from modules import upsidedown as upd


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.UNCORE
        self.name = 'Flip text'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'upd', True, self.on_message)
        self.trigger = t.functions
        self.help = 'Flips a given string upside down'

    async def on_message(self, message, trigger):
        try:
            msg = self.Command(message)
            text = ' '.join(msg.parts[1:])
            await Globals.disco.send_message(message.channel, upd.flip(text))
            return True
        except Exception as e:
            Globals.log.error(f'Could not flip and send the message: {str(e)}')
            await Globals.disco.send_message(message.channel, 'Something went wrong')
            return False