import json

import aiohttp

from modules.globals import Globals
from modules.pluginbase import PluginBase


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.UNCORE
        self.name = 'Yomomma'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'ym', True, self.on_message)
        self.trigger = t.functions
        self.help = 'A random yomama joke from http://api.yomomma.info/'

    async def on_message(self, message, trigger):
        try:
            async with aiohttp.ClientSession(loop=Globals.disco.loop) as session:
                async with session.get('http://api.yomomma.info/') as resp:
                    data = await resp.text()
            data = json.loads(data)
            await message.channel.send(data['joke'])
        except Exception as e:
            Globals.log.error(f'Could not retrieve the joke: {str(e)}')
            await message.channel.send('Something went wrong')
            return False