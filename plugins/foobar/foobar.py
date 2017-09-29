import sys

import discord

from modules.globals import Globals
from modules.pluginbase import PluginBase


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.UNCORE
        self.name = 'foobar'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'be', True, self.on_message)
        t.add_event('on_member_join', lambda member, **kwargs: True, False, self.on_member_join)
        self.trigger = t.functions
        self.help = 'just a test'

        self.expressions = {
            'shocked': 'expression_shock.png',
            'disoriented': 'expression_disoriented_anim.gif',
            'annoyed': 'expression_annoyed.png',
        }

    async def on_message(self, message, trigger):
        msg = self.Command(message)
        Globals.permissions.has_discord_permissions(message.author, ('manage_channels',), message.channel)
        if len(msg.parts) <= 1:
            return False
        expression = self.expressions.get(msg.parts[1], '')
        if expression:
            await Globals.disco.send(message.channel, discord.File(sys.path[0] + '/static/' + expression))
            return True
        else:
            return False

    async def on_member_join(self, member, trigger):
        await member.guild.default_channel.send(f'**Hello {member.name}-san!**')
        return True
