from modules.globals import Globals
from modules.pluginbase import PluginBase


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.CORE
        self.name = 'Bot Invite Link'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'invitelink', True, self.on_message)
        self.trigger = t.functions
        self.help = 'Post bot invite link for convenience'

    async def on_message(self, message, trigger):
        try:
            if Globals.permissions.is_admin(message.author):
                msg = self.Command(message)
                if msg.word(0):
                    for mention in message.mentions:
                        await mention.send(f'https://discordapp.com/oauth2/authorize?&client_id={Globals.disco.user.id}&scope=bot&permissions=2146958591')
                else:
                    await message.author.send(f'https://discordapp.com/oauth2/authorize?&client_id={Globals.disco.user.id}&scope=bot&permissions=2146958591')
                return True
            else:
                await message.channel.send('You have no permissions for this :<')
            return True
        except Exception as e:
            Globals.log.error(f'Could not send invite link: {str(e)}')
            return False
