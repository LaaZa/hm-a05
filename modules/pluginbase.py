import asyncio
import re
from enum import Enum
from operator import itemgetter

import discord

from modules.globals import Globals


class PluginBase:

    class PluginType(Enum):
        CORE = 0
        UNCORE = 1

    class Trigger:

        def __init__(self):
            self.functions = {}

        def add_event(self, event, trigger, is_command, function):
            triggers = self.functions.get(event, [])
            triggers.append((trigger, is_command, function))
            self.functions.update({event: triggers})

    class Command:

        def __init__(self, message, clean=False):
            if clean:
                self.message_content = message.clean_content
            else:
                self.message_content = message.content
            self.cmd_prefix = Globals.channel_command_prefix(message.channel)
            self.parts = self.message_content.split()
            if len(self.parts) > 0 and self.parts[0].startswith(self.cmd_prefix):
                self.cmd = self.parts[0].lstrip(self.cmd_prefix)
            else:
                self.cmd = ''

            self.__message = message

        def word(self, position, excludecmd=True, default=''):
            words = self.message_content.split()
            try:
                if excludecmd and self.cmd:
                    if words[0][:1] == self.cmd_prefix:
                        del words[:words.index(self.cmd_prefix + self.cmd) + 1]
                    else:
                        del words[:words.index(self.cmd) + 1]
                return words[position]
            except (IndexError, ValueError):
                return default

        def wordlist(self, excludecmd=True, default=''):
            words = self.message_content.split()
            try:
                if excludecmd and self.message_content:
                    if words[0][:1] == self.cmd_prefix:
                        del words[:words.index(self.cmd_prefix + self.cmd) + 1]
                    else:
                        del words[:words.index(self.cmd_prefix) + 1]
                return words
            except (IndexError, ValueError):
                return [default]

        def words(self, start=0, excludecmd=True, default=''):
            try:
                if excludecmd and self.cmd:
                    text = self.message_content.partition(self.cmd)[2].strip()
                else:
                    text = self.message_content

                rawlist = re.split(r'(\s+)', text)
                wlist = list()

                for i in range(0, len(rawlist), 2):
                    wlist.append(i)
                out = ''.join(rawlist[wlist[start]:])
                return out.strip()
            except (IndexError, ValueError):
                return default

        def keyword_commands(self, keywords=(), strip=False):
            indx = []
            keyword_values = {}
            for keyword in keywords:
                i = self.message_content.find(keyword + ':')
                if i > -1:
                    indx.append((keyword, i))
            indx = sorted(indx, key=itemgetter(1))
            for i in range(len(indx)):
                if i == 0:
                    if strip:
                        keyword_values.update({indx[i - 1][0]: (self.message_content[indx[i - 1][1] + len(indx[i - 1][0]):].strip(':')).strip()})
                    else:
                        keyword_values.update({indx[i - 1][0]: self.message_content[indx[i - 1][1] + len(indx[i - 1][0]):].strip(':')})
                else:
                    if strip:
                        keyword_values.update({indx[i - 1][0]: (self.message_content[indx[i - 1][1] + len(indx[i - 1][0]):indx[i][1]].strip(':')).strip()})
                    else:
                        keyword_values.update({indx[i - 1][0]: self.message_content[indx[i - 1][1] + len(indx[i - 1][0]):indx[i][1]].strip(':')})
            Globals.log.debug(f'keyword_values: {keyword_values}')
            return keyword_values

        def is_private(self):
            return isinstance(self.__message, discord.DMChannel)

        def is_voice(self):
            return isinstance(self.__message, discord.VoiceChannel)

        def is_group_channel(self):
            return isinstance(self.__message, discord.GroupChannel)

    type = None
    name = None
    trigger = None
    help = None

    @classmethod
    def markdown(cls, content):
        start = '```markdown\n'
        end = '\n```'
        return start + str(content) + end

    class Jobs:

        interval_tasks = {}

        class IntervalTask:

            def __init__(self, coro, interval, *args, **kwargs):
                self.coro = coro
                self.interval = interval
                self.args = args
                self.kwargs = kwargs
                self.running = True

                self.task = Globals.disco.loop.create_task(self.run())

            async def run(self):
                while self.running:
                    await self.coro(*self.args, **self.kwargs)
                    await asyncio.sleep(self.interval, loop=Globals.disco.loop)

            def stop(self):
                self.running = False
                self.task.cancel()

            def __del__(self):
                self.stop()

        @classmethod
        def add_interval_task(cls, caller, task_id, interval, coroutine, *args, **kwargs):
            if caller.__module__ + task_id in cls.interval_tasks.keys():
                return False
            else:
                task = cls.IntervalTask(coroutine, interval, *args, **kwargs)
                cls.interval_tasks[caller.__module__ + task_id] = task
                return True

        @classmethod
        def remove_interval_task(cls, caller, task_id):
            if caller.__module__ + task_id in cls.interval_tasks.keys():
                cls.interval_tasks.get(caller.__module__ + task_id).stop()
                cls.interval_tasks.pop(caller.__module__ + task_id)
                return True
            else:
                return False

    class InteractiveMessage:

        messages = {}

        def __init__(self):
            self.message = None
            self.functions = {}
            self.toggles = []

            @Globals.disco.event
            async def on_reaction_add(reaction, user):
                if reaction.message.id in self.__class__.messages and not user.bot:
                    func = self.__class__.messages[reaction.message.id].functions.get(str(reaction))
                    await reaction.message.remove_reaction(str(reaction), user)
                    try:
                        await func[0](*func[1], **func[2])
                    except TypeError:
                        pass

                    for toggle in self.__class__.messages[reaction.message.id].toggles:
                        if toggle[toggle[0]][3] == str(reaction):
                            await reaction.message.clear_reactions()
                            await toggle[toggle[0]][0](*toggle[toggle[0]][1], **toggle[toggle[0]][2])
                            toggle[0] = 1 if toggle[0] == 2 else 2
                            await self.__add_reactions()

        async def send(self, channel, *args, **kwargs):
            self.message = await channel.send(*args, **kwargs)
            self.__class__.messages[self.message.id] = self
            await self.__add_reactions()

        async def edit(self, **kwargs):
            await self.message.edit(**kwargs)

        async def add_button(self, emoji, func, *args, **kwargs):
            self.functions[emoji] = (func, args, kwargs)
            if self.message:
                await self.__add_reactions()

        async def remove_button(self, emoji):
            try:
                self.functions.pop(emoji)
            except KeyError:
                pass
            self.__add_reactions()

        async def add_toggle(self, emoji_on, emoji_off, func_on, func_off, args_on: tuple, args_off: tuple, kwargs_on: dict, kwargs_off: dict):
            on = (func_on, args_on, kwargs_on, emoji_on)
            off = (func_off, args_off, kwargs_off, emoji_off)
            self.toggles.append([1, on, off])
            if self.message:
                await self.__add_reactions()

        async def __add_reactions(self):
            for emoji in self.functions.keys():
                if emoji not in (str(em) for em in self.message.reactions):
                    await self.message.add_reaction(emoji=emoji)

            for toggle in self.toggles:
                if toggle[toggle[0]][3] not in (str(em) for em in self.message.reactions):
                    await self.message.add_reaction(emoji=toggle[toggle[0]][3])
