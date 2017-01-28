from modules.globals import Globals
from modules.pluginbase import PluginBase


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.CORE
        self.name = 'plugin manager'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'plugin', True, self.on_message)
        self.trigger = t.functions
        self.help = 'Manage plugins'

        self.subcommands = {
            'commands': self.commands,
        }

    async def on_message(self, message, trigger):
            msg = self.Command(message)
            try:
                await self.subcommands.get(msg.parts[1])(message, trigger)
                return True
            except Exception as e:
                Globals.log.error(f'No subcommand: {str(e)}')
                return False

    async def commands(self, message, trigger):
        commands = []
        for fname, plugin in Globals.pluginloader.plugins.items():
            try:
                for evn in plugin.trigger.get('on_message'):
                    if evn[1]:
                        commands.append(evn[0])
            except IndexError:
                pass
        await Globals.disco.send_message(message.channel, f"Available commands: {', '.join(commands)}")
