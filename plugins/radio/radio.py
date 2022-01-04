import time

import nextcord

from modules.globals import Globals
from modules.pluginbase import PluginBase
from plugins.radio.radioapi import RadioAPI


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.UNCORE
        self.name = 'R/a/dio'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'radio', True, self.on_message)
        self.trigger = t.functions
        self.help = 'Get info from R/a/dio'

        self.radio = RadioAPI()
        self.last_dj = ''
        self.last_np = ''
        self.auto_query_list = {'dj': {}, 'np': {}}
        self.last_update = None

    async def on_message(self, message, trigger):
        await self.radio.update()
        self.last_update = time.time()
        
        msg = self.Command(message)

        if msg.word(0) == 'np' or not msg.word(0):

            embed = nextcord.Embed(title='R/a/dio')
            embed.add_field(name='Now playing', value=self.radio.np)
            embed.set_thumbnail(url='https://r-a-d.io/assets/logo_image_small.png')
            await message.channel.send(embed=embed)
            self.last_np = self.radio.np
            if msg.word(1) == 'notify':
                if self.Jobs.add_interval_task(self, 'np' + str(message.channel.id), 10, self.autoquery, message, 'np'):
                    #self.auto_query_list['np'].update({message.channel: Globals.disco.loop.create_task(self.autoquery(message, 'np'))})
                    await message.channel.send('I\'ll tell you when the song changes')
                else:
                    #Globals.disco.loop.call_soon_threadsafe(self.auto_query_list['np'].get(message.channel).cancel)
                    #self.auto_query_list['np'].pop(message.channel)
                    self.Jobs.remove_interval_task(self, 'np' + str(message.channel.id))
                    await message.channel.send('Okay, I won\'t be notifying about song changes')
            return True
        elif msg.word(0) == 'dj':
            embed = nextcord.Embed(title='R/a/dio', colour=self.radio.dj_color)
            embed.add_field(name='Current DJ', value=self.radio.dj)
            embed.set_thumbnail(url=self.radio.dj_image)
            await message.channel.send(embed=embed)
            self.last_dj = self.radio.dj
            if msg.word(1) == 'notify':
                if self.Jobs.add_interval_task(self, 'dj' + str(message.channel.id), 10, self.autoquery, message, 'dj'):
                    #self.auto_query_list['np'].update({message.channel: Globals.disco.loop.create_task(self.autoquery(message, 'dj'))})
                    await message.channel.send('I\'ll tell you when the DJ changes')
                else:
                    #Globals.disco.loop.call_soon_threadsafe(self.auto_query_list['dj'].get(message.channel).cancel)
                    #self.auto_query_list['dj'].pop(message.channel)
                    self.Jobs.remove_interval_task(self, 'dj' + str(message.channel.id))
                    await message.channel.send('Okay, I won\'t be notifying about DJ changes')
            return True
        elif msg.word(0) == 'next':
            embed = nextcord.Embed(title='Next On R/a/dio')
            embed.add_field(name=self.radio.queue_track(0), value=f'in { self.radio.queue_time(0)}')
            embed.set_thumbnail(url='https://r-a-d.io/assets/logo_image_small.png')
            await message.channel.send(embed=embed)
            return True
        elif msg.word(0) == 'queue':
            embed = nextcord.Embed(title='R/a/dio Coming Up')
            for i, track in enumerate(self.radio.queue):
                if self.radio.queue_is_request(i):
                    embed.add_field(name=self.radio.queue_track(i), value=f'in {self.radio.queue_time(i)}', inline=False)
                    #text.append(f'**{self.radio.queue_track(i)} in {self.radio.queue_time(i)}**')
                else:
                    embed.add_field(name=self.radio.queue_track(i), value=f'in {self.radio.queue_time(i)}', inline=False)
                    #text.append(f'{self.radio.queue_track(i)} in {self.radio.queue_time(i)}')
            await message.channel.send(embed=embed)
            return True
        else:
            return False

    async def autoquery(self, message, querytype):
        if time.time() - self.last_update >= 10:
            await self.radio.update()
            self.last_update = time.time()

        if querytype == 'dj' and self.last_dj != self.radio.dj:
            embed = nextcord.Embed(title='R/a/dio', colour=self.radio.dj_color)
            embed.add_field(name='New DJ', value=self.radio.dj)
            embed.set_thumbnail(url=self.radio.dj_image)
            await message.channel.purge(limit=20, check=self.__purge_check_dj)
            await message.channel.send(embed=embed)
            self.last_dj = self.radio.dj
        elif querytype == 'np' and self.last_np != self.radio.np:
            embed = nextcord.Embed(title='R/a/dio')
            embed.add_field(name='Now playing', value=self.radio.np)
            embed.set_thumbnail(url='https://r-a-d.io/assets/logo_image_small.png')
            await message.channel.purge(limit=20, check=self.__purge_check_np)
            await message.channel.send(embed=embed)
            self.last_np = self.radio.np

    def __purge_check_np(self, m):
        try:
            return m.author == Globals.disco.user and m.embeds[0]['title'] == 'R/a/dio' and m.embeds[0]['fields'][0]['name'] == 'Now playing'
        except Exception:
            return False

    def __purge_check_dj(self, m):
        try:
            return m.author == Globals.disco.user and m.embeds[0]['title'] == 'R/a/dio' and m.embeds[0]['fields'][0]['name'] in ('New DJ', 'Current DJ')
        except Exception:
            return False
