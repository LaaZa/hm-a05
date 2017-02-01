from enum import Enum
from modules.globals import Globals
from operator import itemgetter
import re


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

        def __init__(self, message):
            self.message_content = message.content
            self.cmd_prefix = Globals.channel_command_prefix(message.channel)
            self.parts = message.content.split()
            if len(self.parts) > 0 and self.parts[0].startswith(self.cmd_prefix):
                self.cmd = self.parts[0].lstrip(self.cmd_prefix)
            else:
                self.cmd = ''

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

        def keyword_commands(self, keywords=()):
            indx = []
            keyword_values = {}
            for keyword in keywords:
                i = self.message_content.find(keyword)
                if i > -1:
                    indx.append((keyword, i))
            indx = sorted(indx, key=itemgetter(1))
            for i in range(len(indx)):
                if i == 0:
                    keyword_values.update({indx[i - 1][0]: self.message_content[indx[i - 1][1] + len(indx[i - 1][0]):].strip()})
                else:
                    keyword_values.update({indx[i - 1][0]: self.message_content[indx[i - 1][1] + len(indx[i - 1][0]):indx[i][1]].strip()})
            Globals.log.debug(f'keyword_values: {keyword_values}')
            return keyword_values

    type = None
    name = None
    trigger = None
    help = None

    def markdown(self, content):
        start = '```markdown\n'
        end = '\n```'
        return start + str(content) + end
