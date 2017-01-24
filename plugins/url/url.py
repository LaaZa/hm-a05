from modules.globals import Globals
from modules.pluginbase import PluginBase
import aiohttp.web
import re
from bs4 import BeautifulSoup as bs

import traceback


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.UNCORE
        self.name = 'Test url plugin'
        t = PluginBase.Trigger()
        t.add_event('on_message', r'\b((?:https?://\S+|www\d{0,2})\.\S+)', False, self.on_message)
        self.trigger = t.functions
        self.help = 'just a test'


        self.domain = re.compile(r'^\S*?(?=(/|:|$))')

        self.strip_prot_compiled = re.compile(r'^(\S*:)?//')
        self.delim_compiled = re.compile(r'%..|[_\-\.]')

    def title_in_url(self, title, url):
        title = title.lower()
        url = url.lower()

        loc = self.strip_prot_compiled.sub('', url)
        title_words = self.delim_compiled.split(title)
        title_words = [x for x in title_words if x]
        matches = int(0)
        matches_ratio = 0

        for title_word in title_words:
            if title_word in loc:
                matches += 1
        try:
            matches_ratio = float(matches / len(title_words))
        except ZeroDivisionError:
            matches_ratio = 0
        finally:
            return matches_ratio

    async def read_title(self, response, match):
        if 'html' in response.content_type:
            text = await response.text()
            soup = bs(text, 'html.parser')

            try:
                title = re.sub(r'\s\s+', ' ', soup.title.string.strip())[:256]
            except Exception:
                Globals.log.debug('Could not get URL title')
                return False
            title_in_url_ratio = self.title_in_url(title, match)
            Globals.log.debug('Link ratio: %s' % title_in_url_ratio)
            if title_in_url_ratio <= 0.5:
                return title

    async def on_message(self, message, trigger):
        match = trigger.group(0)
        try:
            url_location = re.sub(r'^(\S*:)?//', '', match)
            domain = self.domain.match(url_location).group()
            Globals.log.debug(f'URL: {match}')
            headers = {'User-Agent': ' Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/40.0'}
            title = ''
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(match, headers=headers, timeout=5) as response:
                        title = await self.read_title(response, match)
                except ValueError:
                    async with session.get('http://' + match, headers=headers, timeout=5) as response:
                        title = await self.read_title(response, match)
            if title:
                await Globals.disco.edit_message(message, new_content=f'{message.content} | {title}')
            return True
        except aiohttp.web.HTTPError as e:
            Globals.log.debug(f'ERROR: Failed to open {match}: {e.status} {e.reason}')

            return True
        except Exception:
            Globals.log.debug('ERROR: Getting url data failed: ')
            Globals.log.debug(traceback.format_exc())
            return True  # we don't want any plugins to execute that are dependent on this
