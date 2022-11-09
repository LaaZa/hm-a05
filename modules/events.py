from modules.globals import Globals


class Events:

    def __init__(self):
        Globals.events = self

        @Globals.disco.event
        async def on_message(message):
            # Commands
            if message.author == Globals.disco.user:
                return

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
            for plugin in Globals.pluginloader.plugins.values():
                for cmd in plugin.app_cmds:
                    try:
                        Globals.disco.add_application_command(cmd, overwrite=True, use_rollout=True)
                    except ValueError:
                        pass
            for guild in Globals.disco.guilds:
                await guild.sync_application_commands()
            await Globals.disco.sync_application_commands()

        @Globals.disco.event
        async def on_guild_join(guild):
            Globals.log.info(f'Joined guild: {guild.name}')

        @Globals.disco.event
        async def on_member_join(member):
            if not member.bot:
                await Globals.pluginloader.generate_plugin_queue('on_member_join', member=member)
                status = True
                while status:
                    if await Globals.pluginloader.execute_plugin_queue(channel=member.guild.text_channels[0], member=member) == -1:
                        status = False

        @Globals.disco.event
        async def on_member_remove(member):
            if not member.bot:
                await Globals.pluginloader.generate_plugin_queue('on_member_remove', member=member)
                status = True
                while status:
                    if await Globals.pluginloader.execute_plugin_queue(channel=member.guild.text_channels[0], member=member) == -1:
                        status = False

        @Globals.disco.event
        async def on_member_update(member_before, member_after):
            if not member_before.bot:
                await Globals.pluginloader.generate_plugin_queue('on_member_update', before=member_before, after=member_after)
                status = True
                while status:
                    if await Globals.pluginloader.execute_plugin_queue(channel=member_after.guild.text_channels[0],
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
