import logging

from modules.conf import Config
from modules.globals import Globals
from modules.pluginloader import PluginLoader
from modules.events import Events
from modules.disco import Disco

Globals()

#################
#   Settings    #
#################
conf = Config()

log_path = conf.get_opt('miharu', 'log_path')

Globals.default_command_prefix = conf.get_opt('miharu', 'default_command_prefix')

token = conf.get_opt('miharu', 'token')

#################
#    Logging    #
#################

log_formatter = logging.Formatter('%(asctime)s [%(levelname)-5.5s] [%(module)s/%(funcName)s] %(message)s')
root_logger = logging.getLogger('Miharu')

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
root_logger.addHandler(console_handler)

file_handler = logging.FileHandler(log_path, 'w', 'utf-8')
file_handler.setFormatter(log_formatter)
root_logger.addHandler(file_handler)

root_logger.setLevel(logging.DEBUG)

root_logger.info('Miharu start')

Globals.log = root_logger
#################

bot = Disco(token)
Globals.disco = bot
PluginLoader()

Events()

bot.run()

'''
bot = commands.Bot(command_prefix='?', description='test bot')

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
async def test(url):
    """Adds two numbers together."""
    bot.join_voice_channel('General')
    await bot.say(url)


bot.run(token)
'''