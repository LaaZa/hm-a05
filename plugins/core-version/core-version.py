from modules.globals import Globals
from modules.pluginbase import PluginBase
import modules.version as version


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.CORE
        self.name = 'Version info'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'version', True, self.on_message)
        t.add_event('on_message', 'about', True, self.on_message)
        self.trigger = t.functions
        self.help = 'Show version information'

    async def on_message(self, message, trigger):
        await Globals.disco.send_message(message.channel, f'Miharu [HM-A05] {version.get_version()} by {version.get_author()}')
        return True
