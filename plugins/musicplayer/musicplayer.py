import functools
import re
import struct
import urllib.parse
from collections import deque, defaultdict
from datetime import timedelta
from random import shuffle

import aiohttp
import discord
import youtube_dl

from modules.globals import Globals
from modules.pluginbase import PluginBase
from plugins.musicplayer.audioplayer import *


class Plugin(PluginBase):

    def __init__(self):
        self.type = PluginBase.PluginType.UNCORE
        self.name = 'Music player'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'mp', True, self.on_message)
        self.trigger = t.functions
        self.help = '''Play music!\n
        [add][a] to add url/search term to playlist\n
        [addnext][an] to add to be played next\n
        [play][pl][resume][r] to continue playing paused or stopped music\n
        [next][n] to stop currently playing song and start the next\n
        [stop] to stop(end) the current song and remain paused\n
        [pause][p] to pause pause the current track without ending it\n
        [playing][np][EMPTY] to get info card of the currently playing track\n
        [volume][vol] to adjust volume of the current track, values can be up,+,down,- to adjust accordingly +-10%'''

        self.client = Globals.disco
        self.audio_states = {}

        self.role_permissions = defaultdict(lambda: defaultdict(set))

        self.playlist_to_add = defaultdict(deque)

        self.last_info_card = {}

        self.command_aliases = (('add', 'a'), ('addnext', 'an'), ('play', 'pl'), ('next', 'n'), ('pause', 'stop', 'p'), ('resume', 'r'), ('volume', 'vol'), ('shuffle',))

        self.subcommands = {
            'add': self.sub_add,
            'a': self.sub_add,
            'addnext': self.sub_add,
            'an': self.sub_add,
            'play': self.sub_play,
            'pl': self.sub_play,
            'next': self.sub_next,
            'n': self.sub_next,
            'stop': self.sub_pause,
            'pause': self.sub_pause,
            'p': self.sub_pause,
            'resume': self.sub_play,
            'r': self.sub_play,
            'playing': self.sub_playing,
            'np': self.sub_playing,
            'volume': self.sub_volume,
            'vol': self.sub_volume,
            'shuffle': self.sub_shuffle,
        }

        self.volume = 0.2

    async def on_message(self, message, trigger):
        msg = self.Command(message)
        await self.set_voice_client(message.server)
        if Globals.disco.is_voice_connected(message.server):
            if message.author.voice_channel == Globals.disco.voice_client_in(message.server).channel:
                if msg.word(0, default='playing'):
                    subcmd = msg.word(0, default='playing')
                    if subcmd == 'permissions':
                        await self.sub_permissions(message)
                    else:
                        if self._has_permission(message, subcmd):
                            await self.subcommands.get(subcmd.lower(), lambda x: True)(message)
                        else:
                            await message.channel.send(f'{message.author.mention} you have no permission to use that command')
                    return True
            else:
                return False
        else:
            await message.channel.send('I\'m not on a voice channel')

    '''
    UTILITY FUNCTIONS
    '''

    def get_audio_state(self, server):
        state = self.audio_states.get(server.id)
        if state is None:
            state = AudioState(self.client, on_status_change=self.update_status, queue_next=self.add_next_from_queue)
            self.audio_states[server.id] = state
            Globals.log.debug('New audio state')
        return state

    async def set_voice_client(self, server):
        if Globals.disco.is_voice_connected(server):
            voice = Globals.disco.voice_client_in(server)
            state = self.get_audio_state(server)
            state.voice = voice

    def _unload(self):
        for state in self.audio_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.client.loop.create_task(state.voice.disconnect())
            except Exception:
                pass

    def _has_permission(self, message, command):
        if Globals.permissions.has_permission(message.author, Globals.permissions.PermissionLevel.admin) or Globals.permissions.has_discord_permissions(message.author, ('manage_channels',), message.channel):
            return True

        if command == 'playing':
            return True

        for pair in self.command_aliases:
            if command in pair:
                command = pair[0]

        for role in message.author.roles:
            if self.role_permissions.get(message.server.id) and self.role_permissions.get(message.server.id).get(role.id):
                for cmds in self.role_permissions.get(message.server.id).get(role.id):
                    if command in cmds:
                        return True

    async def get_stream_info(self, url):

        info = {'title': '', 'name': ''}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={'Icy-MetaData': '1'}) as response:
                    metaint = int(response.headers['icy-metaint'])
                    for _ in range(1):
                        await response.content.read(metaint)
                        metadata_length = struct.unpack('B', await response.content.read(1))[0] * 16
                        metadata = await response.content.read(metadata_length)
                        metadata = metadata.rstrip(b'\0')

                        m = re.search(br"StreamTitle='([^']*)';", metadata)
                        if m:
                            title = m.group(1)
                            if title:
                                info['title'] = title.decode('latin1')
                                info['name'] = response.headers['icy-name']
                                break
        except Exception:
            pass

        return info
    '''
    SUBCOMMANDS
    '''

    async def sub_permissions(self, message):
        p = Globals.permissions
        if not (p.has_permission(message.author, p.PermissionLevel.admin) or p.has_discord_permissions(message.author, ('manage_channels',), message.channel)):
            await message.channel.send('You have no rights to manage permissions')
            return
        msg = self.Command(message, clean=True)
        kwrds = msg.keyword_commands(('roles', 'commands'))
        if kwrds.get('roles') and kwrds.get('commands'):
            roles_str = kwrds.get('roles').lower().split('@')
            roles_str = ['@' + x.strip().lstrip('\u200b') if x.strip().startswith('\u200b') else x.strip() for x in roles_str]
            roles = []
            for role in message.server.roles:
                if role.name.lower() in roles_str:
                    roles.append(role)

            commands = kwrds.get('commands').split()
            commands = [x.strip() for x in commands]

            add_list = set()
            remove_list = set()
            for command in commands:
                if command.startswith('-'):
                    command = command.strip('-')
                    if command == '*':
                        remove_list = set([x[0] for x in self.command_aliases])
                    for alias in self.command_aliases:
                        if command in alias:
                            remove_list.add(alias[0])
                elif command == '*':
                    add_list = set([x[0] for x in self.command_aliases])
                else:
                    for alias in self.command_aliases:
                        if command in alias:
                            add_list.add(alias[0])

            final_list = add_list - remove_list

            for role in roles:
                if self.role_permissions.get(message.server.id) and self.role_permissions.get(message.server.id).get(role.id):
                    self.role_permissions[message.server.id][role.id].update(final_list)
                    self.role_permissions[message.server.id][role.id].difference_update(remove_list)
                else:
                    self.role_permissions[message.server.id][role.id] = final_list
            Globals.log.debug(self.role_permissions)
            await message.channel.send('Changed permissions')

        else:
            await message.channel.send('You need to specify roles: @role and commands: add pause -stop')

    async def sub_shuffle(self, message):
        if len(self.playlist_to_add.get(message.server, deque())) <= 1:
            await message.channel.send('The playlist doesn\'t have enough items to shuffle')
            return
        shuffle(self.playlist_to_add.get(message.server, deque()))
        await message.channel.send('シャッフル！ The playlist ain\'t what it used to be')

    async def sub_volume(self, message):
        state = self.get_audio_state(message.server)
        if state.current is None:
            await message.channel.send(f'I\'m not playing music')
            return
        cur_volume = state.player.volume * 100
        msg = self.Command(message)

        vol = msg.word(1).lower()
        value = cur_volume
        if vol:
            if vol in ('up', '+'):
                value = max(min(100, cur_volume + 10), 0)
            elif vol in ('down', '-'):
                value = max(min(100, cur_volume - 10), 0)
            elif vol in ('default', 'normal'):
                value = 20
            elif vol.isnumeric():
                if 0 < int(vol) <= 100:
                    value = int(vol)
            else:
                await message.channel.send(f'Current volume is {cur_volume}%')
                return
        else:
            await message.channel.send(f'Current volume is {cur_volume}%')
            return

        if state.is_playing():
            state.player.volume = value / 100
            await message.channel.send(f'Volume is now {state.player.volume * 100}%')

    async def sub_playing(self, message):
        state = self.get_audio_state(message.server)
        if state.current is None or not state.is_playing():
            await message.channel.send(f'Not playing anything right now')
        else:
            title = state.player.title
            try:
                duration = str(timedelta(seconds=state.player.duration))
            except TypeError:
                duration = ''
            url = state.player.url
            service = urllib.parse.urlsplit(url)[1]
            uploader = state.player.uploader
            upload_date = state.player.upload_date
            added_by = state.current.added_by
            method = 'Streaming' if state.player.is_live else 'Playing'

            info = {
                title: (f'Currently {method}', False),
                duration: ('Duration', False),
                uploader: ('Uploader', True),
                upload_date: ('Upload Date', True),
                added_by.mention: ('Added by', False)
            }
            embed = discord.Embed()
            for part, text in info.items():
                if part:
                    embed.add_field(name=text[0], value=part, inline=text[1])
            if state.player.thumbnail:
                embed.set_thumbnail(url=state.player.thumbnail)
            embed.set_footer(text=service)
            self.last_info_card[message.server] = await message.channel.send(embed=embed)

    async def sub_add(self, message):
        msg = self.Command(message)
        if msg.word(1) or message.attachments:
            url = ''
            if message.attachments:
                url = message.attachments[0]['url']
            else:
                url = msg.words(1)

            Globals.log.info(f'Adding url: {url}')
            media_info = await self.add_to_queue(message, url)
            if media_info:
                if media_info.get('duration'):
                    await message.channel.send(f'Added {"next " if media_info.get("next") else ""}**{media_info.get("title")}** [{str(timedelta(seconds=media_info.get("duration")))}] to playlist')
                elif media_info.get('_type') == 'playlist':
                    await message.channel.send(f'Added {"next " if media_info.get("next") else ""}{len(media_info.get("entries"))} items from **{media_info.get("title")}** to playlist')
                else:
                    await message.channel.send(f'Added {"next " if media_info.get("next") else ""}**{media_info.get("title")}** to playlist')
                if Globals.permissions.client_has_discord_permissions(('manage_messages',), message.channel):
                    await Globals.disco.delete_message(message)
        else:
            await message.channel.send('I need proper url :/')

    async def sub_play(self, message):
        state = self.get_audio_state(message.server)
        if state.current:
            await self.resume(message)
        else:
            if state.deck.empty() and not state.is_playing():
                await message.channel.send('The playlist is empty :<')

    async def sub_next(self, message):
        await self.next(message)

    async def sub_pause(self, message):
        await self.pause(message)

    async def add_to_queue(self, message, url):
        state = self.get_audio_state(message.server)
        await self.set_voice_client(message.server)

        Globals.disco.send_typing(message.server)
        info_out = None

        msg = self.Command(message)

        ytdl_options = {
            'quiet': False,
            'flat-playlist': True,
            'ignore-errors': False,
            'skip_download': True,
            'extract_flat': 'in_playlist',
            'logger': Globals.log,
            'default_search': 'auto',
        }

        ydl = youtube_dl.YoutubeDL(ytdl_options)

        info = None

        #  load media information/playlist
        try:
            func = functools.partial(ydl.extract_info, url, download=False)
            info = await Globals.disco.loop.run_in_executor(None, func)
        except youtube_dl.DownloadError as e:
            Globals.log.error(f'Could not add items from the playlist {str(e)}')
            await message.channel.send('Could not add items from the playlist :<')
            return None
        if info.get('_type') == 'playlist' and len(info.get('entries')) > 1:
            info_out = info
            await message.channel.send('Adding items from the playlist')

            #  generated playlists do not have title, we will use search query instead without part before :
            if not info.get('title'):
                info['title'] = url.split(':')[-1]

            if msg.word(0).lower() in ('addnext', 'an'):
                await self.put_to_deck(message, info.get('entries'))
                info_out['next'] = True
            else:
                for entry in info.get('entries'):
                    self.playlist_to_add[message.server].append(entry)
                    Globals.log.info(f'Added entry for url {entry.get("url") or entry.get("webpage_url")}')
        else:
            ytdl_options = {
                'quiet': False,
                'noplaylist': True,
                'ignore-errors': False,
                'skip_download': True,
                'logger': Globals.log,
                'default_search': 'auto',
            }
            #  load more detailed information for singular entries
            ydl = youtube_dl.YoutubeDL(ytdl_options)

            entry_info = None

            #  load media information
            try:
                func = functools.partial(ydl.extract_info, url, download=False)
                entry_info = await Globals.disco.loop.run_in_executor(None, func)
            except youtube_dl.DownloadError as e:
                Globals.log.error(f'Could not add items from the playlist {str(e)}')
                await message.channel.send('Could not add the item :<')
                return None
            #  search results can be playlists with only one entry
            if entry_info.get('entries') and len(entry_info.get('entries')) == 1:
                entry_info = entry_info['entries'][0]

            info_out = entry_info
            if msg.word(0).lower() in ('addnext', 'an'):
                await self.put_to_deck(message, [entry_info])
                info_out['next'] = True
            else:
                self.playlist_to_add[message.server].append(entry_info)
                Globals.log.info(f'Added entry for url {entry_info.get("url") or entry_info.get("webpage_url")}')

        #  immediately put on deck if it is empty
        if state.deck.empty():
            await self.add_next_from_queue(message)
        return info_out

    async def add_next_from_queue(self, message):
        if len(self.playlist_to_add[message.server]) > 0:
            await self.add_player(message, self.playlist_to_add[message.server].popleft())

    async def put_to_deck(self, message, entry_info_list):
        state = self.get_audio_state(message.server)

        #  get entry from the deck if exists and put it back on the playlist
        if not state.deck.empty():
            entry = await state.deck.get()
            self.playlist_to_add[message.server].appendleft(entry.info)
            Globals.log.info(f'Added back to playlist from deck entry for url {entry.info.get("url") or entry.info.get("webpage_url")}')
        #  add the entry or entries to the playlist next
        for entry_info in reversed(entry_info_list):
            self.playlist_to_add[message.server].appendleft(entry_info)
            Globals.log.info(f'Added entry for url to the front of playlist {entry_info.get("url") or entry_info.get("webpage_url")}')
        #  and put it on the deck immediately
        await self.add_next_from_queue(message)

    async def add_player(self, message, entry_info):
        if Globals.disco.is_voice_connected(message.server):
            state = self.get_audio_state(message.server)

            Globals.log.info(f'Adding player for url {entry_info.get("url") or entry_info.get("webpage_url")}')

            ytdl_options = {
                'quiet': True,
                'noplaylist': True,
                'retries': 20,
                'fixup': 'detect_or_warn',
                'continuedl': True,
                'logger': Globals.log,
            }
            try:
                player = await state.voice.create_ytdl_player(entry_info.get("webpage_url") or entry_info.get("url"), ytdl_options=ytdl_options, after=state.toggle_next, options='-bufsize 4096k')
            except Exception as e:
                Globals.log.error('Player adding failed:' + str(e))
                await self.add_next_from_queue(message)
            else:
                player.volume = self.volume
                if not entry_info.get('thumbnail'):
                    #  load some extra meta
                    func = functools.partial(player.yt.extract_info,  entry_info.get("webpage_url") or entry_info.get("url"), download=False)
                    info = await Globals.disco.loop.run_in_executor(None, func)

                    stream_info = await self.get_stream_info(entry_info.get('url'))
                    if stream_info.get('name'):
                        entry_info['title'] = stream_info.get('name') + ':\n' + stream_info.get('title') or entry_info.get('title')
                    else:
                        entry_info['title'] = stream_info.get('title') or entry_info.get('title')

                    Globals.log.debug(f'streaminfo {stream_info}')

                    if stream_info.get('name'):
                        entry_info['is_live'] = 1

                    player.thumbnail = info.get('thumbnail')
                else:
                    player.thumbnail = entry_info.get('thumbnail')

                audio_entry = AudioEntry(message, player, entry_info)
                await state.deck.put(audio_entry)
                Globals.log.info(f'Added player for {player.title}')
            try:
                return entry_info
            except IndexError:
                Globals.log.info(f'No players were added')
                return None
        else:
            await message.channel.send('I\'m not on a voice channel')
            return None

    async def pause(self, message):
        state = self.get_audio_state(message.server)
        if state.is_playing():
            state.player.pause()
            await self.update_status(message, AudioStatus.PAUSED)
            Globals.log.debug('Musicplayer: pause')

    async def resume(self, message):
        state = self.get_audio_state(message.server)
        state.player.resume()
        await self.update_status(message.channel, AudioStatus.PLAYING)
        Globals.log.debug('Musicplayer resume')

    async def next(self, message):
        player = self.get_audio_state(message.server)
        player.player.stop()
        Globals.log.error('Musicplayer Next')

    async def update_status(self, channel, status):
        return
        '''
        current_song = self.get_audio_state(channel.server).player
        if status is AudioStatus.PLAYING:
            game = discord.Game(name=f'[▶]{current_song.title}', type=int(current_song.is_live))
        elif status is AudioStatus.PAUSED:
            game = discord.Game(name=f'[⏸]{current_song.title}', type=int(current_song.is_live))
        else:
            game = None

        await Globals.disco.change_presence(game=game)'''

