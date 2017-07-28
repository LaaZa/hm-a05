import re

from modules.globals import Globals
from modules.pluginbase import PluginBase


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.UNCORE
        self.name = 'Answers'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'answer', True, self.on_message)
        t.add_event('on_message', re.compile('.+'), False, self.regex_answer)
        self.trigger = t.functions
        self.help = 'add answers to some regex'

        self.answers = {}

    async def on_message(self, message, trigger):
        msg = self.Command(message)
        try:
            if not Globals.permissions.has_permission(message.author, Globals.permissions.PermissionLevel.admin):
                await message.channel.send('You need admin permission :<')
                return True
            if msg.word(0) and msg.words(1):
                self.answers.update({re.compile(msg.word(0)): msg.words(1)})
                return True
        except Exception as e:
            raise e

    async def regex_answer(self, message, trigger):
        for regex, answer in self.answers.items():
            match = re.search(regex, message.content)
            if match:
                try:
                    await message.channel.send(answer.format(*match.groups()))
                    return True
                except IndexError:
                    await message.channel.send(answer)
                    return True
        return False
