from modules.globals import Globals
from modules.pluginbase import PluginBase

import nextcord


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        super().__init__()
        self.type = PluginBase.PluginType.CORE
        self.name = 'Bot Invite Link'
        self.add_trigger('on_message', 'invitelink', True, self.on_message)
        self.help = 'Post bot invite link for convenience'

    async def on_message(self, message, trigger):
        try:
            if Globals.permissions.is_admin(message.author):
                url = nextcord.utils.oauth_url(Globals.disco.user.id, permissions=nextcord.Permissions.all())
                msg = self.Command(message)
                if msg.word(0):
                    for mention in message.mentions:
                        await mention.send(url)
                        #await mention.send(f'https://discordapp.com/oauth2/authorize?&client_id={Globals.disco.user.id}&scope=bot&permissions=2146958591')
                else:
                    await message.author.send(url)
                    #await message.author.send(f'https://discordapp.com/oauth2/authorize?&client_id={Globals.disco.user.id}&scope=bot&permissions=2146958591')
                return True
            else:
                await message.channel.send('You have no permissions for this :<')
            return True
        except Exception as e:
            Globals.log.error(f'Could not send invite link: {str(e)}')
            return False
