from modules.globals import Globals
from modules.pluginbase import PluginBase


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.CORE
        self.name = 'quit'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'quit', True, self.on_message)
        self.trigger = t.functions
        self.help = 'Quit and end application'

    async def on_message(self, message, trigger):
            try:
                if Globals.permissions.has_permission(message.author, Globals.permissions.PermissionLevel.admin):
                    await Globals.disco.send_message(message.channel, 'Do I really have to go?')
                    msg = await Globals.disco.wait_for_message(timeout=5, author=message.author, channel=message.channel, check=lambda m: 'yes' in m.content.lower() or 'no' in m.content.lower())
                    if msg:
                        if msg.content.lower() == 'yes':
                            await Globals.disco.send_message(message.channel, 'Sayonara!')
                            await Globals.disco.logout()
                            await Globals.disco.close()
                        else:
                            await Globals.disco.send_message(message.channel, 'Oh, good.')
                    else:
                        await Globals.disco.send_message(message.channel, 'Hmm? No? Oh, good.')
                    return True
                else:
                    await Globals.disco.send_message(message.channel, 'You have no permissions for this :<')
                return True
            except Exception as e:
                Globals.log.error(f'Could not quit: {str(e)}')
                return False
