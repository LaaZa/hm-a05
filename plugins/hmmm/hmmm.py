import random
import re
from collections import defaultdict

import nextcord
import feedparser

from modules.globals import Globals
from modules.pluginbase import PluginBase


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.UNCORE
        self.name = 'Hmmm'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'hmmm', True, self.on_message)
        self.trigger = t.functions
        self.help = 'Hmmm'

        self.prev_links = defaultdict(list)

    async def on_message(self, message, trigger):
        try:
            limit = '100'
            msg = self.Command(message)
            d = feedparser.parse(f'http://www.reddit.com/r/hmmm/.rss?limit={limit}')
            body = random.choice(d.entries)['content'][0]['value']
            image_link = re.findall(r'<span><a href="(.*?)">\[link\]</a>', body)[0]

            embed = nextcord.Embed()
            embed.set_image(url=image_link)
            embed.set_footer(text='Hmmm')
            await message.channel.send(embed=embed)
        except Exception as e:
            Globals.log.error(f'Could not hmmm: {str(e)}')
            await message.channel.send('Hmmm')
            return False