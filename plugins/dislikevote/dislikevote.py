from collections import defaultdict

import discord

from modules.globals import Globals
from modules.pluginbase import PluginBase


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.UNCORE
        self.name = 'Dislike Vote'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'dislikevote', True, self.on_message)
        t.add_event('on_reaction_add', self.reaction_check, False, self.on_reaction_add)
        self.trigger = t.functions
        self.help = 'Removes messages with enough certain reactions'

        self.subcommands = {
            'set': self.sub_set,
            'remove': self.sub_remove,
        }

        # Guild: Channel: Emoji: 'limit': int
        self.dislike_setting = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))

    async def on_message(self, message, trigger):
        try:
            msg = self.Command(message)
            if message.guild:
                if msg.word(0):
                    await self.subcommands.get(msg.word(0), self.dummy)(message)

            return True
        except Exception as e:
            Globals.log.error(f'Problem we have a Houston: {str(e)}')
            return False

    async def dummy(self, m):
        pass

    # TODO support more settings
    def reaction_check(self, reaction, user, **kwargs):
        channels = self.dislike_setting.get(reaction.message.guild, dict())
        emoji = channels.get(reaction.message.channel, dict())
        if str(reaction.emoji) in emoji.keys():
            if reaction.count >= emoji.get(str(reaction.emoji), dict()).get('limit', -1):
                return True
        return False

    async def on_reaction_add(self, reaction, user, **kwargs):
        msg = reaction.message
        try:
            await reaction.message.delete()
            return True
        except (discord.Forbidden, discord.HTTPException) as e:
            Globals.log.error(f'No permission to delete messages: {str(e)}')
        return False

    # TODO permissions and more settings
    async def sub_set(self, message):
        msg = Plugin.Command(message)
        try:
            emoji = msg.word(1)
            limit = msg.word(2)
            self.dislike_setting.update({
                message.guild: {
                    message.channel: {
                        emoji: {
                            'limit': int(limit)
                        }
                    }
                }
            })
        except Exception:
            return False
        return True

    # TODO permissions
    async def sub_remove(self, message):
        msg = Plugin.Command(message)
        try:
            self.dislike_setting.get(message.guild, dict()).pop(message.channel)
        except Exception:
            return False
        return True
