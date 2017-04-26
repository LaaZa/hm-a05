from modules.globals import Globals
from modules.pluginbase import PluginBase
import discord

class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.CORE
        self.name = 'plugin manager'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'plugin', True, self.on_message)
        self.trigger = t.functions
        self.help = 'Manage plugins'

        self.subcommands = {
            'commands': self.commands,
            'enable': self.enable,
            'disable': self.disable,
            'load': self.load,
            'unload': self.unload,
            'reload': self.reload,
        }

    async def on_message(self, message, trigger):
            msg = self.Command(message)
            try:
                await self.subcommands.get(msg.parts[1])(message, trigger)
                return True
            except Exception as e:
                Globals.log.error(f'No subcommand: {str(e)}')
                return False

    async def commands(self, message, trigger):
        commands = []
        for fname, plugin in Globals.pluginloader.plugins.items():
            try:
                for evn in plugin.trigger.get('on_message'):
                    if evn[1]:
                        commands.append(evn[0])
            except IndexError:
                pass
        await Globals.disco.send_message(message.channel, f"Available commands: {', '.join(commands)}")

    async def load(self, message, trigger):
        if not Globals.permissions.has_permission(message.author, Globals.permissions.PermissionLevel.admin):
            await Globals.disco.send_message(message.channel, 'You need admin rights for this command')
            return
        msg = self.Command(message)
        if msg.word(1):
            plugin = Globals.pluginloader.load_plugins(msg.words(1))
            if plugin == 1:
                await Globals.disco.send_message(message.channel, f'Loaded plugin: {msg.words(1)}')
            elif plugin == 2 and msg.word(1) == '*':
                await Globals.disco.send_message(message.channel, 'Loaded plugins: ' + ''.join('{} '.format(key) for key in Globals.pluginloader.plugins.keys()))
            elif plugin == -1:
                await Globals.disco.send_message(message.channel, 'Plugin already loaded')
            elif plugin == -2:
                await Globals.disco.send_message(message.channel, 'Could not load, plugin is throwing an error')
            else:
                await Globals.disco.send_message(message.channel, 'No such plugin')
        else:
            await Globals.disco.send_message(message.channel, 'You must state the name of the plugin')

    async def unload(self, message, trigger):
        if not Globals.permissions.has_permission(message.author, Globals.permissions.PermissionLevel.admin):
            await Globals.disco.send_message(message.channel, 'You need admin rights for this command')
            return
        msg = self.Command(message)
        if msg.word(1):
            plugin = Globals.pluginloader.unload_plugin(msg.words(1))
            if plugin == 1:
                await Globals.disco.send_message(message.channel, f'Unloaded plugin: {msg.words(1)}')
            elif plugin == -1:
                await Globals.disco.send_message(message.channel, 'Cannot unload a CORE type plugin')
            else:
                await Globals.disco.send_message(message.channel, 'No such plugin')
        else:
            await Globals.disco.send_message(message.channel, 'You must state the name of the plugin')

    async def reload(self, message, trigger):
        if not Globals.permissions.has_permission(message.author, Globals.permissions.PermissionLevel.admin):
            await Globals.disco.send_message(message.channel, 'You need admin rights for this command')
            return
        msg = self.Command(message)
        if msg.word(1):
            plugin = Globals.pluginloader.reload_plugin(msg.words(1))
            if plugin == 1:
                await Globals.disco.send_message(message.channel, f'reloaded plugin: {msg.words(1)}')
            elif plugin == -2:
                await Globals.disco.send_message(message.channel, 'Could not reload, plugin is throwing an error')
            else:
                await Globals.disco.send_message(message.channel, 'No such plugin')
        else:
            await Globals.disco.send_message(message.channel, 'You must state the name of the plugin')

    async def enable(self, message, trigger):
        if not self.is_channel_admin(message.author, message.channel):
            await Globals.disco.send_message(message.channel, 'You need channel management rights for this command')
            return
        msg = self.Command(message)
        if msg.word(1):
            plugin = Globals.pluginloader.enable(msg.words(1), message.channel)
            if plugin == 1:
                await Globals.disco.send_message(message.channel, f'Enabled plugin: {msg.words(1)}')
            elif plugin == 2:
                await Globals.disco.send_message(message.channel, 'Plugin already enabled')
            else:
                await Globals.disco.send_message(message.channel, 'No such plugin loaded')
        else:
            await Globals.disco.send_message(message.channel, 'You must state the name of the plugin')

    async def disable(self, message, trigger):
        if not self.is_channel_admin(message.author, message.channel):
            await Globals.disco.send_message(message.channel, 'You need channel management rights for this command')
            return
        msg = self.Command(message)
        if msg.word(1):
            plugin = Globals.pluginloader.disable(msg.words(1), message.channel)
            if plugin == 1:
                await Globals.disco.send_message(message.channel, f'Disabled plugin: {msg.words(1)}')
            elif plugin == -1:
                await Globals.disco.send_message(message.channel, 'Cannot disable a CORE type plugin')
            elif plugin == 2:
                await Globals.disco.send_message(message.channel, 'Plugin already disabled')
            else:
                await Globals.disco.send_message(message.channel, 'No such plugin loaded')
        else:
            await Globals.disco.send_message(message.channel, 'You must state the name of the plugin')

    def is_channel_admin(self, user, channel):
        #  global bot admin is above channel admin
        if Globals.permissions.has_permission(user, Globals.permissions.PermissionLevel.admin):
            return True
        #  channel management rights suffice as "channel admin"
        return Globals.permissions.has_discord_permissions(user, ('manage_channels',), channel=channel)
