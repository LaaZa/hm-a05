from modules.pluginbase import PluginBase
from modules.globals import Globals
import feedparser
import random
import re
import discord


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.UNCORE
        self.name = 'Hmmm'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'hmmm', True, self.on_message)
        self.trigger = t.functions
        self.help = 'Hmmm'

    async def on_message(self, message, trigger):
        try:
            limit = '200'
            msg = self.Command(message)
            d = feedparser.parse(f'http://www.reddit.com/r/hmmm/.rss?limit={limit}')
            body = random.choice(d.entries)['content'][0]['value']
            image_link = re.findall(r'<span><a href="(.*?)">\[link\]</a>', body)[0]
            embed = discord.Embed()
            embed.set_image(url=image_link)
            embed.set_footer(text='Hmmm')
            await Globals.disco.send_message(message.channel, embed=embed)
        except Exception as e:
            Globals.log.error(f'Could not hmmm: {str(e)}')
            await Globals.disco.send_message(message.channel, 'Hmmm')
            return False