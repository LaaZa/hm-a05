import discord

class Globals:
    config_data = None
    log = None
    disco = None
    default_command_prefix = None
    __channel_command_prefix = {}
    pluginloader = None
    events = None

    @classmethod
    def set_channel_command_prefix(cls, channel, prefix=default_command_prefix):
        cls.__channel_command_prefix.update({channel: prefix})

    @classmethod
    def channel_command_prefix(cls, channel):
        return cls.__channel_command_prefix.get(channel, cls.default_command_prefix)
