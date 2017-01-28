from modules.globals import Globals
from modules.pluginbase import PluginBase


class Events:

    def __init__(self):
        Globals.events = self

        @Globals.disco.event
        async def on_message(message):
            # Commands
            if message.author.id != Globals.disco.user.id and not message.author.bot:
                await Globals.pluginloader.generate_plugin_queue(message, 'on_message:cmd', (PluginBase.PluginType.CORE, PluginBase.PluginType.UNCORE))
                status = True
                while status:
                    if await Globals.pluginloader.execute_plugin_queue(channel=message.channel, message=message) == -1:
                        status = False
            # Reactions
            if message.author.id != Globals.disco.user.id and not message.author.bot:
                await Globals.pluginloader.generate_plugin_queue(message, 'on_message', (PluginBase.PluginType.CORE, PluginBase.PluginType.UNCORE))
                status = True
                while status:
                    if await Globals.pluginloader.execute_plugin_queue(channel=message.channel, message=message) == -1:
                        status = False

        @Globals.disco.event
        async def on_ready():
            Globals.log.info(f'Logged in: {Globals.disco.user.name} id: {Globals.disco.user.id}')

        @Globals.disco.event
        async def on_server_join(server):
            Globals.log.info(f'Joined Server: {server.name}')
