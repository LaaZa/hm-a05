from modules.pluginbase import PluginBase
from modules.globals import Globals
import feedparser

class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.UNCORE
        self.name = 'Reddit'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'reddit', True, self.on_message)
        self.trigger = t.functions
        self.help = 'Returns the top post on reddit. Can optionally pass a subreddit to get the top post there instead'

    async def on_message(self, message, trigger):
        msg = self.Command(message)
        if len(msg.parts) > 1:
            path = '/r/' + ' '.join(msg.parts[1:]) + '/.rss'
            d = feedparser.parse('http://www.reddit.com' + path)
            await Globals.disco.send_message(message.channel, d.entries[0]['link'])
        else:
            d = feedparser.parse('http://www.reddit.com/.rss')
            await Globals.disco.send_message(message.channel, d.entries[0]['link'])
        return True