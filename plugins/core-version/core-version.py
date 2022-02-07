import modules.version as version
from modules.pluginbase import PluginBase


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        super().__init__()
        self.type = PluginBase.PluginType.CORE
        self.name = 'Version info'
        self.add_trigger('on_message', 'version', True, self.on_message)
        self.add_trigger('on_message', 'about', True, self.on_message)
        self.help = 'Show version information'

    async def on_message(self, message, trigger):
        await message.channel.send(f'Miharu [HM-A05] {version.get_version()} by {version.get_author()}')
        return True
