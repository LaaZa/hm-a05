from modules.globals import Globals


class Events:

    def __init__(self):
        Globals.events = self

        @Globals.disco.event
        async def on_message(message):
            # Commands
            if message.author.id != Globals.disco.user.id and not message.author.bot:
                await Globals.pluginloader.generate_plugin_queue('on_message', is_command=True, message=message)
                status = True
                while status:
                    result = await Globals.pluginloader.execute_plugin_queue(channel=message.channel, message=message)
                    if result is True:
                        return True
                    if result == -1:
                        status = False

            # Reactions
            if message.author.id != Globals.disco.user.id and not message.author.bot:
                await Globals.pluginloader.generate_plugin_queue('on_message', message=message)
                status = True
                while status:
                    result = await Globals.pluginloader.execute_plugin_queue(channel=message.channel, message=message)
                    if result is True:
                        return True
                    if result == -1:
                        status = False

        @Globals.disco.event
        async def on_ready():
            Globals.log.info(f'Logged in: {Globals.disco.user.name} id: {Globals.disco.user.id}')

        @Globals.disco.event
        async def on_server_join(server):
            Globals.log.info(f'Joined Server: {server.name}')

        @Globals.disco.event
        async def on_member_join(member):
            if not member.bot:
                await Globals.pluginloader.generate_plugin_queue('on_member_join', member=member)
                status = True
                while status:
                    if await Globals.pluginloader.execute_plugin_queue(channel=member.server.default_channel, member=member) == -1:
                        status = False

        @Globals.disco.event
        async def on_member_remove(member):
            if not member.bot:
                await Globals.pluginloader.generate_plugin_queue('on_member_remove', member=member)
                status = True
                while status:
                    if await Globals.pluginloader.execute_plugin_queue(channel=member.server.default_channel, member=member) == -1:
                        status = False

        @Globals.disco.event
        async def on_member_update(member_before, member_after):
            if not member_before.bot:
                await Globals.pluginloader.generate_plugin_queue('on_member_update', before=member_before, after=member_after)
                status = True
                while status:
                    if await Globals.pluginloader.execute_plugin_queue(channel=member_after.server.default_channel,
                                                                       before=member_before, after=member_after) == -1:
                        status = False

        @Globals.disco.event
        async def on_reaction_add(reaction, user):
            if not user.bot:
                await Globals.pluginloader.generate_plugin_queue('on_reaction_add', reaction=reaction, user=user)
                status = True
                while status:
                    if await Globals.pluginloader.execute_plugin_queue(channel=reaction.message.channel, reaction=reaction, user=user) == -1:
                        status = False

        @Globals.disco.event
        async def on_reaction_remove(reaction, user):
            if not user.bot:
                await Globals.pluginloader.generate_plugin_queue('on_reaction_remove', reaction=reaction, user=user)
                status = True
                while status:
                    if await Globals.pluginloader.execute_plugin_queue(channel=reaction.message.channel, reaction=reaction, user=user) == -1:
                        status = False

        @Globals.disco.event
        async def on_reaction_clear(message, reactions):
            await Globals.pluginloader.generate_plugin_queue('on_reaction_clear', message=message, reactions=reactions)
            status = True
            while status:
                if await Globals.pluginloader.execute_plugin_queue(channel=message.channel, message=message, reactions=reactions) == -1:
                    status = False
