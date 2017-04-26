import asyncio
from enum import Enum


class AudioStatus(Enum):
    PLAYING = 1
    PAUSED = 2
    STOPPED = 3


class AudioEntry:

    def __init__(self, message, player, info):
        self.added_by = message.author
        self.channel = message.channel
        self.message = message
        self.player = player
        self.info = info


class AudioState:

    def __init__(self, client, on_status_change=None, queue_next=None):
        self.current = None
        self.voice = None
        self.client = client
        self.play_next_song = asyncio.Event()
        self.deck = asyncio.Queue()
        self.audio_player = self.client.loop.create_task(self.audio_player_task())

        self.on_status_change = on_status_change
        self.queue_next = queue_next

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    async def run_status_update(self, status):
        if self.on_status_change is not None and self.voice is not None:
            await self.on_status_change(self.voice.channel, status)

    @property
    def player(self):
        return self.current.player

    def toggle_next(self):
        self.client.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.deck.get()
            await self.run_status_update(AudioStatus.PLAYING)
            self.current.player.start()
            if self.deck.qsize() < 1:
                await self.queue_next(self.current.message)
            await self.play_next_song.wait()

            if self.deck.empty():
                await self.run_status_update(AudioStatus.STOPPED)
