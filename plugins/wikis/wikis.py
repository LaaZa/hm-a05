import asyncio
import re
from difflib import SequenceMatcher as SM

import aiohttp
import discord
import wikia
import wikipedia
from bs4 import BeautifulSoup

from modules.globals import Globals
from modules.pluginbase import PluginBase


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.UNCORE
        self.name = 'Wikipedia and Wikia'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'wiki', True, self.on_message_wikipedia)
        t.add_event('on_message', 'wikia', True, self.on_message_wikia)
        self.trigger = t.functions
        self.help = 'Query wikipedia and wikia'

    async def on_message_wikipedia(self, message, trigger):
        try:
            msg = self.Command(message)
            wiki = None
            if len(msg.parts) > 1:
                keyword = ' '.join(msg.parts[1:])
                wiki = wikipedia.page(keyword)
            else:
                wiki = wikipedia.random()[0]

        except wikipedia.exceptions.DisambiguationError as e:
            best_match = ''
            search = e.options
            options = list()
            for i, opt in enumerate(search):
                options.append(str(i + 1) + '. ' + opt)
            opts = '\n'.join(options)
            await message.channel.send(f'Try to be more specific. I found these though:\n{self.markdown(opts)}\nType any number above to get that article', delete_after=10)
            try:
                retry = await Globals.disco.wait_for(event='message', timeout=10, check=lambda m: m.channel is message.channel and m.author is message.author)
                best_match = search[int(retry.content) - 1]
                try:
                    await retry.delete()
                except (discord.Forbidden, discord.HTTPException):
                    pass
            except (ValueError, IndexError):
                return True
            except AttributeError:
                await message.channel.send('...well maybe it just doesn\'t exist, you suck at searching or I suck at finding... or maybe we just need more bananas.')
                return True
            except asyncio.TimeoutError:
                pass

            wiki = wikipedia.page(best_match)
        except wikipedia.exceptions.PageError:
            await message.channel.send('I didn\'t find anything on the Wikipedia about that. :<')
            return True

        text = f'{wikipedia.summary(wiki.title, 2)}'
        if len(text) > 400:
            text = f'{wikipedia.summary(wiki.title, 1)}'
        if len(text) > 400:
            text = f'{wikipedia.summary(wiki.title, 1)[:-3]}...'

        embed = discord.Embed(title=wiki.title, url=wiki.url.replace(' ', '_'), description='```' + text + '```', colour=discord.Colour.dark_blue())

        await message.channel.send(embed=embed)

        try:
            await message.delete()
        except (discord.Forbidden, discord.HTTPException):
            pass

        return True

        #except Exception as e:
         #   Globals.log.error(f'Could not search wikipedia: {str(e)}')
          #  return False

    async def on_message_wikia(self, message, trigger):
        try:
            msg = self.Command(message)
            wiki = None
            subwikia = msg.word(0)
            if len(msg.parts) > 2:
                keyword = ' '.join(msg.parts[2:])
                search = wikia.search(subwikia, keyword)
                best_ratio = 0
                best_match = ''
                for result in search:
                    if keyword.lower() in result.lower():
                        ratio = SM(None, keyword.lower(), result.lower()).ratio()
                        if ratio > best_ratio:
                            best_ratio = ratio
                            best_match = result

                try:
                    redirect_test = wikia.summary(subwikia, keyword)
                    if 'REDIRECT' in redirect_test:
                        best_match = redirect_test[9:]
                except wikia.WikiaError:
                    pass

                if not best_match:
                    #raise wikia.DisambiguationError(keyword, search)
                    options = list()
                    for i, opt in enumerate(search):
                        options.append(str(i + 1) + '. ' + opt)
                    opts = '\n'.join(options)
                    await message.channel.send(f'Try to be more specific. I found these though:\n{self.markdown(opts)}\nType any number above to get that article', delete_after=10)
                    try:
                        retry = await Globals.disco.wait_for(event='message', timeout=10, check=lambda m: m.channel is message.channel and m.author is message.author)
                        best_match = search[int(retry.content) - 1]
                        try:
                            await retry.delete()
                        except (discord.Forbidden, discord.HTTPException):
                            pass
                    except (ValueError, IndexError):
                        return True
                    except AttributeError:
                        await message.channel.send('...well maybe it just doesn\'t exist, you suck at searching or I suck at finding... or maybe we just need more bananas.')
                        return True
                    except asyncio.TimeoutError:
                        pass

                wiki = wikia.page(subwikia, best_match)
            else:
                await message.channel.send('I didn\'t find anything on the Wikia about that. :<')
                return True

            '''
            text = f'**{wiki.title}**| {wiki.url}\n{wikia.summary(subwikia, wiki.title)}'
            text = self.markdown('\n'.join(re.findall(r'^.+\.', wiki.content[:1500], flags=re.M)))

            text = f'**{wiki.title}**\n{text}'
            
            if len(text) > 400:
                text = f'**{wiki.title}**| {wiki.url}\n{wikia.summary(subwikia ,wiki.title)}'
            if len(text) > 400:
                text = f'**{wiki.title}**| {wiki.url}\n{wikia.summary(subwikia, wiki.title)[:-3]}...'
            '''

            image = ''
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(wiki.url) as response:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        try:
                            image = soup.select_one('[class*="infobox"] img').attrs['src']
                        except AttributeError:
                            image = soup.find('meta', attrs={'property': 'og:image'}).attrs['content']
            except AttributeError:
                pass

            text = wiki.content[:2000]
            if not text:
                text = wikia.summary(subwikia, wiki.title)
            paragraph = re.findall(r'^.+\.', text, flags=re.M)
            if not paragraph:
                paragraph = [text, ]
            embed_long = discord.Embed(title=wiki.title, url=wiki.url.replace(' ', '_'), description='```' + '``````'.join(paragraph) + '```', colour=discord.Colour.teal())
            embed_short = discord.Embed(title=wiki.title, url=wiki.url.replace(' ', '_'), description='```' + paragraph[0] + '```', colour=discord.Colour.teal())
            if image:
                embed_long.set_image(url=image)
            embed_long.set_footer(text=re.search(r'(?:/)((?:[a-z0-9|-]+\.)*[a-z0-9|-]+\.[a-z]+)(?:/)', wiki.url).group(1))
            embed_short.set_footer(text=re.search(r'(?:/)((?:[a-z0-9|-]+\.)*[a-z0-9|-]+\.[a-z]+)(?:/)', wiki.url).group(1))

            if Globals.permissions.client_has_discord_permissions(('manage_messages',), message.channel):
                imsg = PluginBase.InteractiveMessage()
                await imsg.add_toggle('➕', '➖', imsg.edit, imsg.edit, tuple(), tuple(), {'embed': embed_long}, {'embed': embed_short})
                await imsg.send(message.channel, embed=embed_short)
            else:
                await message.channel.send(message.channel, embed=embed_long)

        except wikia.PageError:
            await message.channel.send('I didn\'t find anything on the Wikia about that. :<')
        except ValueError:
            await message.channel.send('I didn\'t find anything on the Wikia about that. :<')
        except wikia.WikiaError:
            await message.channel.send('I didn\'t find anything :<')

        try:
            await message.delete()
        except (discord.Forbidden, discord.HTTPException):
            pass

        return True
