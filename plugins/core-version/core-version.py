import modules.version as version
from modules.pluginbase import PluginBase


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
        await message.channel.send(f'Miharu [HM-A05] {version.get_version()} by {version.get_author()}')
        return True
