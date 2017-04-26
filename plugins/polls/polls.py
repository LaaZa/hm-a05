from collections import OrderedDict
from collections import defaultdict
from datetime import datetime, timedelta

import asyncio
import discord

from modules.pluginbase import PluginBase
from modules.globals import Globals
import dateparser
import emoji

class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.UNCORE
        self.name = 'Polls'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'poll', True, self.on_message)
        t.add_event('on_reaction_add', self.reaction_check, False, self.on_reaction_add)
        self.trigger = t.functions
        self.help = 'Make polls'

        self.subcommands = {
            'make': self.sub_make,
            'end': self.sub_end,
        }

        self.polls = defaultdict(lambda: defaultdict(list))
        self.number_emoji = {1: chr(49)+chr(8419), 2: chr(50)+chr(8419), 3: chr(51)+chr(8419), 4: chr(52)+chr(8419), 5: chr(53)+chr(8419), 6: chr(54)+chr(8419), 7: chr(55)+chr(8419), 8: chr(56)+chr(8419), 9: chr(57)+chr(8419)}

    async def on_message(self, message, trigger):
        try:
            msg = self.Command(message)
            if msg.word(0):
                await self.subcommands.get(msg.word(0), self.dummy)(message)

            return True
        except Exception as e:
            Globals.log.error(f'Problem we have a Houston: {str(e)}')
            return False

    async def dummy(self, m):
        pass

    def reaction_check(self, reaction, user, **kwargs):
        if reaction.emoji in self.number_emoji.values():
            msg = reaction.message
            if msg.author == msg.server.me:
                if self.polls.get(msg.server) and self.polls.get(msg.server).get(msg.channel):
                    for poll in self.polls[msg.server][msg.channel]:
                        if not poll.ended:
                            return True
        return False

    async def on_reaction_add(self, reaction, user, **kwargs):
        msg = reaction.message
        if self.polls.get(msg.server) and self.polls.get(msg.server).get(msg.channel):
            for poll in self.polls[msg.server][msg.channel]:
                if poll.card.id == msg.id and not poll.ended:
                    for k, v in self.number_emoji.items():
                        if v == reaction.emoji:
                            await poll.add_vote(user, k)
                            return

    async def sub_make(self, message):
        msg = self.Command(message)
        kwrds = msg.keyword_commands(('1', '2', '3', '4', '5', '6', '7', '8', '9', 'time', 'title'), strip=True)
        options_to_add = OrderedDict()
        for key, val in kwrds.items():
            if val and key.isdigit():
                options_to_add[key] = val

        if len(options_to_add) < 2:
            await Globals.disco.send_message(message.channel, 'A poll with less than 2 options doesn\'t make much sense.')
            return

        lowest_available_poll_id = 0

        poll_ids = set()

        if self.polls.get(message.server) and self.polls.get(message.server).get(message.channel):
            for poll in self.polls.get(message.server).get(message.channel):
                if not poll.ended:
                    poll_ids.add(poll.poll_id)

        for i in range(1, 1000):
            if i not in poll_ids:
                lowest_available_poll_id = i
                break

        poll = self.Poll(message, kwrds.get('title', ''), lowest_available_poll_id)
        for key, val in sorted(options_to_add.items()):
            await poll.add_option(int(key), val)

        if kwrds.get('time'):
            dt = dateparser.parse(kwrds.get('time'))
            if dt:
                if dt < datetime.now():
                    dt = datetime.now() + (datetime.now() - dt)

                poll.time = dt
                if dt - datetime.now() >= timedelta(days=1) and Globals.permissions.client_has_discord_permissions(('manage_messages',), message.channel):
                    await Globals.disco.send_message(message.channel, 'The poll time is quite long, would you like me to pin it?')
                    answer = await Globals.disco.wait_for_message(timeout=20, author=message.author, check=lambda m: m.content.lower() in ('y', 'yes', 'n', 'no', 'pin', 'don\'t pin', 'nah', 'yep', 'sure', 'ok', 'nope'))
                    if answer.content in ('y', 'yes', 'pin', 'yep', 'sure', 'ok'):
                        poll.pin = True
            else:
                await Globals.disco.send_message(message.channel, 'Sorry, I couldn\'t understand the time :/')

        await poll.create_card(message)
        self.polls[message.server][message.channel].append(poll)

    async def sub_end(self, message):
        msg = self.Command(message)
        ended_poll = False
        try:
            for poll in list(self.polls[message.server][message.channel]):
                if (poll.added_by == message.author or (Globals.permissions.is_admin(message.author) or Globals.permissions.has_discord_permissions(message.author, ('manage_messages',), message.channel))) and not poll.ended:
                    if msg.word(1):
                        if poll.poll_id == int(msg.word(1)):
                            await poll.end_poll()
                            self.polls[message.server][message.channel].remove(poll)
                            ended_poll = True
                            break
                    elif not msg.word(1):
                        await poll.end_poll()
                        self.polls[message.server][message.channel].remove(poll)
                        ended_poll = True
                        break
        except IndexError as e:
            await Globals.disco.send_message(message.channel, 'No polls to end')
            return
        except ValueError as e:
            await Globals.disco.send_message(message.channel, 'Invalid poll ID')
            return

        if not ended_poll:
            await Globals.disco.send_message(message.channel, 'No active polls to end')

    class Poll:

        def __init__(self, message, title, poll_id):
            self.options = OrderedDict()
            self.title = title
            self.message = message
            self.ended = False
            self.card = None
            self.total_votes = 0
            self.added_by = message.author
            self.votes = {}
            self.number_emoji = {1: chr(49) + chr(8419), 2: chr(50) + chr(8419), 3: chr(51) + chr(8419), 4: chr(52) + chr(8419), 5: chr(53) + chr(8419), 6: chr(54) + chr(8419), 7: chr(55) + chr(8419), 8: chr(56) + chr(8419), 9: chr(57) + chr(8419)}
            self.time = None
            self.pin = False
            self.time_task = None
            self.poll_id = poll_id

        async def add_option(self, num, option):
            self.options.update({str(num): {'option': option, 'votes': 0}})

        async def add_vote(self, member, num):
            if not self.options.get(str(num)):
                return
            try:
                if self.votes.get(member):
                    self.options.get(str(self.votes[member]))['votes'] -= 1
                    self.options.get(str(num))['votes'] += 1
                    await Globals.disco.remove_reaction(self.card, self.number_emoji[self.votes[member]], member)
                else:
                    self.options.get(str(num))['votes'] += 1
                    self.total_votes += 1
                self.votes[member] = num
                await self.update_card()
            except TypeError:
                pass

        async def create_card(self, message):
            embed = discord.Embed(title=f'POLL #{self.poll_id} - {self.title}')
            for num, option in self.options.items():
                embed.add_field(name=f'{num}. {option["option"]}', value='No votes', inline=False)
            embed.set_footer(text='Vote by adding reaction corresponding your choice. :one: :two: :three: ...')
            self.card = await Globals.disco.send_message(message.channel, embed=embed)
            if self.pin:
                await Globals.disco.pin_message(self.card)
            if self.time:
                self.time_task = Globals.disco.loop.call_at(Globals.disco.loop.time() + (self.time.timestamp() - datetime.now().timestamp()), self._time)

        async def update_card(self):
            if self.ended:
                return
            embed = discord.Embed(title=f'POLL #{self.poll_id} - {self.title}')
            for num, option in self.options.items():
                try:
                    percentage = option['votes'] / self.total_votes * 100
                except ZeroDivisionError:
                    percentage = 0
                val = '█' * round(percentage / 4)
                embed.add_field(name=f'{num}. {option["option"]}', value=f'{val} {percentage}%', inline=False)

            embed.set_footer(text='Vote by adding reaction corresponding your choice. :one: :two: :three: ...')
            self.card = await Globals.disco.edit_message(self.card, embed=embed)

        async def end_poll(self):
            self.ended = True
            if self.time_task:
                self.time_task.cancel()
            embed = discord.Embed(title=f'POLL #{self.poll_id} RESULTS - {self.title}')
            for num, option in self.options.items():
                try:
                    percentage = option['votes'] / self.total_votes * 100
                except ZeroDivisionError:
                    percentage = 0
                val = '█' * round(percentage / 4)

                embed.add_field(name=f'{num}. {option["option"]}', value=f'{val} {percentage}%', inline=False)
            embed.set_footer(text='VOTE HAS ENDED')
            self.card = await Globals.disco.edit_message(self.card, embed=embed)
            if self.pin:
                await Globals.disco.unpin_message(self.card)

        def _time(self):
            asyncio.ensure_future(self.end_poll(), loop=Globals.disco.loop)
