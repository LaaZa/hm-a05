import datetime as dt

import aiohttp

from modules.globals import Globals


class RadioAPI:

    def __init__(self):
        self.loaded_json = None
        self.data = {}
        self.queue = []
        self.dj = ''
        self.dj_color = None
        self.dj_image = None
        self.np = ''
        self.api_url = 'https://r-a-d.io/api/'

    async def update(self):
        try:
            await self.load_json()
            self.parse()
        except Exception:
            pass

    async def load_json(self):
            headers = {'User-Agent': ' Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0'}
            async with aiohttp.ClientSession(loop=Globals.disco.loop) as session:
                async with session.get(self.api_url, headers=headers) as response:
                    self.loaded_json = await response.json()

    def parse(self):
        self.data = self.loaded_json
        self.queue = self.data['main']['queue']
        self.dj = self.data['main']['dj']['djname']
        r, g, b = self.data['main']['dj']['djcolor'].split()
        self.dj_color = int('0x{0:02x}{1:02x}{2:02x}'.format(int(r), int(g), int(b)), 16)
        self.dj_image = self.api_url + 'dj-image/' + self.data['main']['dj']['djimage']
        self.np = self.data['main']['np']

    def queue_time(self, item):
        s = (dt.datetime.fromtimestamp(int(self.queue[item]['timestamp'])) - dt.datetime.fromtimestamp(int(self.data['main']['current']))).seconds
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        return str('%02d:%02d' % (minutes, seconds))

    def queue_track(self, item):
        return self.queue[item]['meta']

    def queue_is_request(self, item):
        return bool(self.queue[item]['type'])
