from enum import Enum
from modules.globals import Globals
from operator import itemgetter


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
            self.cmd = self.parts[0].lstrip(self.cmd_prefix)

        def keyword_commands(self, keywords=()):
            indx = []
            keyword_values = {}
            for keyword in keywords:
                i = self.message_content.find(keyword)
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
