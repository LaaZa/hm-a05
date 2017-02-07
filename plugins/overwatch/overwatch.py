from modules.pluginbase import PluginBase
from modules.globals import Globals
import aiohttp
import json
import re

class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.UNCORE
        self.name = 'overwatch'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'owpatch', True, self.on_message)
        self.trigger = t.functions
        self.help = 'Returns the latest overwatch patch notes'

    async def on_message(self, message, trigger):
        try:
            async with aiohttp.ClientSession(loop=Globals.disco.loop) as session:
                async with session.get('https://api.lootbox.eu/patch_notes') as resp:
                    data = await resp.text()
            data = json.loads(data)
            def cleanhtml(raw_html):
                cleanr = re.compile('<.*?>')
                cleantext = re.sub(cleanr, '', raw_html)
                return cleantext
            await Globals.disco.send_message(message.channel, cleanhtml(data['patchNotes'][0]['detail']))
        except Exception as e:
            Globals.log.error(f'Could not get the patch notes: {str(e)}')
            await Globals.disco.send_message(message.channel, 'Something went wrong')
            return False