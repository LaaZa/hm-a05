import aiohttp
import urllib.parse
import xml.etree.ElementTree as et
import re
from modules.globals import Globals


class SimpleWolframAPI:

    def __init__(self, key):
        self.loaded_xml = ''
        self.root = None
        self._key = key
        self.api_url = f'http://api.wolframalpha.com/v2/query?appid={self._key}&reinterpret=true&input='
        self._query = ''
        self._excludeid = ('BasicUnitDimensions', 'Interpretation')

    async def request(self, query):
        quoted = await self.load_xml(query)
        await self.parse()
        return quoted

    async def load_xml(self, query):
        headers = {'User-Agent': ' Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0'}
        self._query = urllib.parse.quote_plus(query)
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url + self._query, headers=headers) as resp:
                self.loaded_xml = await resp.text(encoding='utf-8')
        return self._query

    async def parse(self):
        self.root = et.fromstring(self.loaded_xml)

    async def primary(self):
        primary = False
        l = []
        try:
            pods = self.root.findall('pod')
        except Exception:
            return False
        for pod in pods:
            if pod.get('title') == 'Input interpretation':
                joined = ', '.join(re.split(r'\n', pod.attrib['title'] + ': ' + pod.find('subpod').find('plaintext').text))
                l.append(joined)
            if pod.get('primary') == 'true':
                joined = ', '.join(re.split(r'\n', pod.attrib['title'] + ': ' + pod.find('subpod').find('plaintext').text))
                l.append(joined)
                primary = True
        if not primary:
            try:
                joined = ' , '.join(re.split(r'\n', pods[1].attrib['title'] + ': ' + pods[1].find('subpod').find('plaintext').text))
                l.append(joined)
            except Exception:
                l.append('http://www.wolframalpha.com/input/?i=' + self._query)
        return l

    async def all(self, limit):
        podlist = []
        try:
            pods = self.root.findall('pod')
        except Exception:
            return False
        for i, pod in enumerate(pods):
            try:
                if pod.attrib['id'] not in self._excludeid:
                    data = f"**{pod.attrib['title']}::**\n{pod.find('subpod').find('plaintext').text}"
                    data = data[:await self.find_nth(data, '\n', 5) + 1].rstrip()
                    poddata1 = re.sub(r'\t', '', data)
                    poddata2 = re.sub(r'\s\|', ':', poddata1)
                    poddata3 = re.sub(r'\n', ' \n ', poddata2)
                    poddata4 = re.sub(r'\|\s{2}:', r'//', poddata3)
                    if not poddata4.endswith('None'):
                        podlist.append(poddata4)
                    else:
                        limit += 1
                    if i >= limit:
                        break
            except Exception as e:
                Globals.log.error(e)
        return podlist

    async def find_nth(self, haystack, needle, n):
        start = haystack.find(needle)
        t = start
        while start >= 0 and n > 1:
            t = haystack.find(needle, t + len(needle))
            start = t
            n -= 1
        if start < 0:
            start = len(haystack) - 1
        return start
