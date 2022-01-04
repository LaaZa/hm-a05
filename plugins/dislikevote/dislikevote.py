from collections import defaultdict

import nextcord

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
        self.help = 'Removes messages with enough certain reactions. | set :emoji: limit | remove'

        self.subcommands = {
            'set': self.sub_set,
            'remove': self.sub_remove,
        }

        # Channel: Emoji: 'limit': int
        self.dislike_setting = defaultdict(lambda: defaultdict(dict))

    async def on_message(self, message, trigger):
        if not (Globals.permissions.has_permission(message.author, Globals.permissions.PermissionLevel.admin) or Globals.permissions.has_discord_permissions(message.author, ('manage_messages',), message.channel)):
            await message.author.send(f'You don\'t have rights to use dislikevote command on {message.guild.name} #{message.channel.name}')
            return True

        if not Globals.permissions.client_has_discord_permissions(('manage_messages',), message.channel):
            await message.channel.send('I don\'t have rights to manage messages here.')
            return True

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

    def reaction_check(self, reaction, user, **kwargs):
        emoji = self.dislike_setting.get(reaction.message.channel, dict())
        if str(reaction.emoji) in emoji.keys() and not reaction.message.pinned:
            if reaction.count >= emoji.get(str(reaction.emoji), dict()).get('limit', -1):
                return True
        return False

    async def on_reaction_add(self, reaction, user, **kwargs):
        try:
            await reaction.message.delete()
            return True
        except (nextcord.Forbidden, nextcord.HTTPException) as e:
            Globals.log.error(f'No permission to delete messages: {str(e)}')
        return False

    async def sub_set(self, message):
        msg = Plugin.Command(message)
        try:
            emoji = msg.word(1)
            limit = msg.word(2)
            self.dislike_setting.update({
                message.channel: {
                    emoji: {
                        'limit': int(limit)
                    }
                }
            })
            await message.channel.send(f'Set dislike vote on this channel to {limit}x {emoji}')
        except Exception as e:
            Globals.log.error(f'Could not set dislike vote: {str(e)}')
            await message.channel.send('Could not set dislike vote.')
            return False
        return True

    async def sub_remove(self, message):
        try:
            self.dislike_setting.pop(message.channel)
            await message.channel.send(f'Removed dislike vote on this channel.')
        except Exception:
            await message.channel.send(f'No dislike vote set on this channel.')
        return True
