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
            await Globals.disco.send_typing(message.channel)
            req = await self.api.request(' '.join(msg.parts[1:]))
            if req:
                answer = await self.api.all(3)
                if answer:
                    await Globals.disco.send_message(message.channel, '\n'.join(answer))
                else:
                    await Globals.disco.send_message(message.channel, 'No one knows!')
        else:
            await Globals.disco.send_messgae(message.channel, 'I found exactly what you were looking for: NOTHING!')
        return True
        #except Exception as e:
        #       Globals.log.error(f'Could not query wolframalpha: {str(e)}')
        #        return False'''
