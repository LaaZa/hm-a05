import aiohttp
import nextcord

from modules.globals import Globals
from modules.pluginbase import PluginBase


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.UNCORE
        self.name = 'Osu stats'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'osu', True, self.on_message)
        self.trigger = t.functions
        self.help = 'Get osu stats'

        self.base_url = 'https://osu.ppy.sh/api/'

        self.api_key = Globals.config_data.get_opt('apikeys', 'osu_key')

    async def on_message(self, message, trigger):
        msg = self.Command(message)
        try:
            username = msg.words(0) or message.author.display_name
            json = None
            params = {'k': self.api_key, 'u': username, 'type': 'string'}
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url + 'get_user', params=params) as response:
                    json = await response.json()

            if not json:
                await message.channel.send(f'Can\'t find user {username}')
                return True

            username = json[0]['username']
            playcount = json[0]['playcount']
            pp_rank = json[0]['pp_rank']
            pp = json[0]['pp_raw']
            ranked_score = json[0]['ranked_score']
            total_score = json[0]['total_score']
            level = json[0]['level']
            accuracy = json[0]['accuracy']
            country = json[0]['country']
            pp_c_rank = json[0]['pp_country_rank']

            embed = nextcord.Embed(title=f'Osu! - {username}')
            embed.add_field(name='Performance', value=f'{int(float(pp))}pp (#{pp_rank}) {self.flag(country)} #{pp_c_rank}')
            embed.add_field(name='Ranked Score', value=f'{ranked_score}')
            embed.add_field(name='Total Score', value=f'{total_score}')
            embed.add_field(name='Hit Accuracy', value=f'{float(accuracy):.2f}%')
            embed.add_field(name='Play Count', value=f'{playcount}')
            embed.add_field(name='Level', value=f'{int(float(level))}')

            await message.channel.send(embed=embed)

            return True

        except TypeError:
            await message.channel.send(f'User {username} has no stats')
            return True
        except Exception as e:
            return True

    def flag(self, country):
        base = 127397
        return chr(ord(country[0]) + base) + chr(ord(country[1]) + base)

