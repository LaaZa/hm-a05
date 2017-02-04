from modules.pluginbase import PluginBase
from modules.globals import Globals
import aiohttp
import json


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.UNCORE
        self.name = 'Steam'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'steam', True, self.on_message)
        self.trigger = t.functions
        self.help = 'Checks the status of Steam, Steam community and Dota 2/CSGO GCs'

    async def on_message(self, message, trigger):
        try:
            async with aiohttp.ClientSession(loop=Globals.disco.loop) as session:
                async with session.get('http://steamgaug.es/api/v2', headers={'User-Agent': ' Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/40.0'}) as resp:
                    data = await resp.text()
            data = json.loads(data)
            status = 'Steam is up' if data['ISteamClient']['online'] else 'Steam is down'
            community = 'Community is up' if data['SteamCommunity']['online'] else 'Community is down'
            gc = 'Dota 2 game coordinator is up' if data['ISteamGameCoordinator']['570']['online'] else 'Dota 2 game coordinator is down.'
            csgc = 'CSGO game coordinator is up' if data['ISteamGameCoordinator']['730']['online'] else 'CSGO game coordinator is down.'
            await Globals.disco.send_message(message.channel, f'{status}\n{community}\n{gc}\n{csgc}')
        except Exception as e:
            Globals.log.error(f'Could not get Steam status: {str(e)}')
            await Globals.disco.send_message(message.channel, 'Something went wrong')
            return False

