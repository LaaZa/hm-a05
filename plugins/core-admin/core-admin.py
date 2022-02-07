import nextcord

from modules.globals import Globals
from modules.pluginbase import PluginBase


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        super().__init__()
        self.type = PluginBase.PluginType.CORE
        self.name = 'Admin manager'
        self.add_trigger('on_message', 'admin', True, self.on_message)
        self.help = 'Manage admin rights'

    async def on_message(self, message, trigger):
        if isinstance(message.channel, nextcord.DMChannel):
            try:
                await message.channel.send('Please say the admin token')
                msg = await Globals.disco.wait_for('message', timeout=10, check=lambda x: x.channel == message.channel and x.author == message.author)
                if Globals.permissions.validate_token(msg.content.strip()):
                    Globals.permissions.add_permission(message.author, Globals.permissions.PermissionLevel.admin)
                    await message.channel.send('You are now admin!')
                else:
                    await message.channel.send('Invalid token :/')

                return True
            except Exception as e:
                Globals.log.error(f'Could not validate as an admin: {str(e)}')
                return False
        else:
            await message.channel.send('Works only in private!')
            return True
