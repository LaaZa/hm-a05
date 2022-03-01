from modules.globals import Globals
from modules.pluginbase import PluginBase


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        super().__init__()
        self.type = PluginBase.PluginType.CORE
        self.name = 'plugin manager'
        self.add_trigger('on_message', 'plugin', True, self.on_message)
        self.help = 'Manage plugins'

        self.subcommands = {
            'commands': self.commands,
            'enable': self.enable,
            'disable': self.disable,
            'slashenable': self.slash_enable,
            'slashdisable': self.slash_disable,
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
            await message.channel.send(f"Available subcommands: {', '.join(self.subcommands.keys())}")
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
        await message.channel.send(f"Available commands: {', '.join(commands)}")

    async def load(self, message, trigger):
        if not Globals.permissions.is_admin(message.author):
            await message.channel.send('You need admin rights for this command')
            return
        msg = self.Command(message)
        if msg.word(1):
            plugin = Globals.pluginloader.load_plugins(msg.words(1))
            if plugin == 1:
                await message.channel.send(f'Loaded plugin: {msg.words(1)}')
            elif plugin == 2 and msg.word(1) == '*':
                await message.channel.send('Loaded plugins: ' + ''.join('{} '.format(key) for key in Globals.pluginloader.plugins.keys()))
            elif plugin == -1:
                await message.channel.send('Plugin already loaded')
            elif plugin == -2:
                await message.channel.send('Could not load, plugin is throwing an error')
            else:
                await message.channel.send('No such plugin')
        else:
            await message.channel.send('You must state the name of the plugin')

    async def unload(self, message, trigger):
        if not Globals.permissions.is_admin(message.author):
            await message.channel.send('You need admin rights for this command')
            return
        msg = self.Command(message)
        if msg.word(1):
            plugin = Globals.pluginloader.unload_plugin(msg.words(1))
            if plugin == 1:
                await message.channel.send(f'Unloaded plugin: {msg.words(1)}')
            elif plugin == -1:
                await message.channel.send('Cannot unload a CORE type plugin')
            else:
                await message.channel.send('No such plugin')
        else:
            await message.channel.send('You must state the name of the plugin')

    async def reload(self, message, trigger):
        if not Globals.permissions.is_admin(message.author):
            await message.channel.send('You need admin rights for this command')
            return
        msg = self.Command(message)
        if msg.word(1):
            plugin = Globals.pluginloader.reload_plugin(msg.words(1))
            if plugin == 1:
                await message.channel.send(f'reloaded plugin: {msg.words(1)}')
                await Globals.disco.rollout_application_commands()
                await message.guild.rollout_application_commands()
            elif plugin == -2:
                await message.channel.send('Could not reload, plugin is throwing an error')
            else:
                await message.channel.send('No such plugin')
        else:
            await message.channel.send('You must state the name of the plugin')

    async def enable(self, message, trigger):
        msg = self.Command(message)
        if msg.word(1) in ('g', 'guild'):
            if not self.is_guild_admin(message.author, message.guild):
                await message.channel.send('You need guild management rights for this command')
                return
            if msg.word(2):
                plugin = 0
                for chan in message.guild.text_channels:
                    plugin = Globals.pluginloader.enable(msg.words(2), chan)

                if plugin == 1:
                    await message.channel.send(f'Enabled plugin: {msg.words(1)}')
                elif plugin == 2:
                    await message.channel.send('Plugin already enabled')
                else:
                    await message.channel.send('No such plugin loaded')
            else:
                await message.channel.send('You must state the name of the plugin')
        else:
            if not self.is_channel_admin(message.author, message.channel):
                await message.channel.send('You need channel management rights for this command')
                return
            if msg.word(1):
                plugin = Globals.pluginloader.enable(msg.words(1), message.channel)
                if plugin == 1:
                    await message.channel.send(f'Enabled plugin: {msg.words(1)}')
                elif plugin == 2:
                    await message.channel.send('Plugin already enabled')
                else:
                    await message.channel.send('No such plugin loaded')
            else:
                await message.channel.send('You must state the name of the plugin')

    async def disable(self, message, trigger):
        msg = self.Command(message)
        if msg.word(1) in ('g', 'guild'):
            if not self.is_guild_admin(message.author, message.guild):
                await message.channel.send('You need guild management rights for this command')
                return
            if msg.word(2):
                plugin = 0
                for chan in message.guild.text_channels:
                    plugin = Globals.pluginloader.disable(msg.words(2), chan)

                if plugin == 1:
                    await message.channel.send(f'Disabled plugin: {msg.words(2)}')
                elif plugin == -1:
                    await message.channel.send('Cannot disable a CORE type plugin')
                elif plugin == 2:
                    await message.channel.send('Plugin already disabled')
                else:
                    await message.channel.send('No such plugin loaded')
            else:
                await message.channel.send('You must state the name of the plugin')

        if not self.is_channel_admin(message.author, message.channel):
            await message.channel.send('You need channel management rights for this command')
            return
        if msg.word(1):
            plugin = Globals.pluginloader.disable(msg.words(1), message.channel)
            if plugin == 1:
                await message.channel.send(f'Disabled plugin: {msg.words(1)}')
            elif plugin == -1:
                await message.channel.send('Cannot disable a CORE type plugin')
            elif plugin == 2:
                await message.channel.send('Plugin already disabled')
            else:
                await message.channel.send('No such plugin loaded')
        else:
            await message.channel.send('You must state the name of the plugin')

    async def slash_enable(self, message, trigger):
        msg = self.Command(message)
        if not self.is_guild_admin(message.author, message.guild):
            await message.channel.send('You need guild management rights for this command')
            return
        if msg.word(1):
            plugin = Globals.pluginloader.add_slash_server(msg.words(1), message.guild)
            if plugin == 1:
                await message.channel.send(f'Enabled slash commands for plugin: {msg.words(1)}')
                await Globals.disco.rollout_application_commands()
                await message.guild.rollout_application_commands()
            elif plugin == 2:
                await message.channel.send('Slashes already enabled')
            else:
                await message.channel.send('No such plugin loaded')
        else:
            await message.channel.send('You must state the name of the plugin')

    async def slash_disable(self, message, trigger):
        msg = self.Command(message)
        if not self.is_channel_admin(message.author, message.guild):
            await message.channel.send('You need guild management rights for this command')
            return
        if msg.word(1):
            plugin = Globals.pluginloader.add_slash_server(msg.words(1), message.guild)
            if plugin == 1:
                await message.channel.send(f'Disabled slash commands for plugin: {msg.words(1)}')
                await Globals.disco.rollout_application_commands()
                await message.guild.rollout_application_commands()
            elif plugin == 2:
                await message.channel.send('Slashes already disabled')
            else:
                await message.channel.send('No such plugin loaded')
        else:
            await message.channel.send('You must state the name of the plugin')

    def is_channel_admin(self, user, channel):
        #  global bot admin is above channel admin
        if Globals.permissions.has_permission(user, Globals.permissions.PermissionLevel.admin):
            return True
        # channel management rights suffice as "channel admin"
        return Globals.permissions.has_discord_permissions(user, ('manage_channels',), channel=channel)

    def is_guild_admin(self, user, guild):
        #  global bot admin is above channel admin
        if Globals.permissions.has_permission(user, Globals.permissions.PermissionLevel.admin):
            return True
        # channel management rights suffice as "channel admin"
        return Globals.permissions.has_discord_permissions(user, ('administartor', 'manage_guild'), guild=guild)