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
                if Globals.permissions.is_admin(message.author):
                    await message.channel.send('Do I really have to go?')
                    msg = await Globals.disco.wait_for('message', timeout=5, check=lambda m: m.author is message.author and m.channel is message.channel and 'yes' in m.content.lower() or 'no' in m.content.lower())
                    if msg:
                        if msg.content.lower() == 'yes':
                            await message.channel.send('Sayonara!')
                            await Globals.disco.logout()
                            await Globals.disco.close()
                        else:
                            await message.channel.send('Oh, good.')
                    else:
                        await message.channel.send('Hmm? No? Oh, good.')
                    return True
                else:
                    await message.channel.send('You have no permissions for this :<')
                return True
            except Exception as e:
                Globals.log.error(f'Could not quit: {str(e)}')
                return False
