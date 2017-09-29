from modules.globals import Globals
from modules.pluginbase import PluginBase
from plugins.wolframalpha.simplewolframapi import SimpleWolframAPI


class Plugin(PluginBase):
    # plugin specific

    def __init__(self):
        self.type = PluginBase.PluginType.UNCORE
        self.name = 'WolframAlpha'
        t = PluginBase.Trigger()
        t.add_event('on_message', 'wa', True, self.on_message)
        self.trigger = t.functions
        self.help = 'Query WolframAlpha'

        self.key = Globals.config_data.get_opt('apikeys', 'wolframalpha_key')
        self.api = SimpleWolframAPI(self.key)

    async def on_message(self, message, trigger):
        msg = self.Command(message)
        #try:
        if len(msg.parts) > 1:
            async with message.channel.typing():
                req = await self.api.request(' '.join(msg.parts[1:]))
                if req:
                    answer = await self.api.all(3)
                    if answer:
                        await message.channel.send('\n'.join(answer))
                    else:
                        await message.channel.send('No one knows!')
        else:
            await message.channel.send('I found exactly what you were looking for: NOTHING!')
        return True
        #except Exception as e:
        #       Globals.log.error(f'Could not query wolframalpha: {str(e)}')
        #        return False'''
