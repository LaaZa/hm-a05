from modules.globals import Globals
from modules.pluginbase import PluginBase


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.CORE
        self.name = 'nickname change'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'nick', True, self.on_message)
        self.trigger = t.functions
        self.help = 'Change bot nickname'

    async def on_message(self, message, trigger):
        msg = PluginBase.Command(message)
        if message.server:
            try:
                if Globals.permissions.has_permission(message.author, Globals.permissions.PermissionLevel.admin):
                    await Globals.disco.change_nickname(message.server.get_member(Globals.disco.user.id), ' '.join(msg.parts[1:]).strip())
                else:
                    await message.channel.send('You have no permissions for this :<')
                return True
            except Exception as e:
                Globals.log.error(f'Could not change nick: {str(e)}')
                return False
