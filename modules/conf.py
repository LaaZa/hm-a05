import configparser
import shutil
import sys
from os import path, pardir
from codecs import open as copen
from modules.globals import Globals
'''
stolen from HM-A06
'''


class Config(configparser.ConfigParser):
    dict = None
    conf_file = None
    defaultconf = None

    def __init__(self):
        super().__init__()
        Globals.config_data = self

        self.defaultconf = path.abspath(path.join(path.join(path.dirname(__file__), pardir), '.defaultconf'))
        self.conf_file = path.abspath(path.join(path.join(path.dirname(__file__), pardir), 'config.ini'))
        self.load()

    def load(self):
        try:
            with copen(self.conf_file, 'r', encoding='utf-8') as f:
                self.read_file(f)

            # Reads the ini file into a dictionary, http://stackoverflow.com/a/3220891/2612657
            d = dict(self._sections)
            for k in d:
                d[k] = dict(self._defaults, **d[k])
                d[k].pop('__name__', None)

            self.dict = d

        except FileNotFoundError:
            try:
                shutil.copy(self.defaultconf, self.conf_file)
                self.die("'No 'config.ini' found, copied defaults\nPlease verify values in it ('config.ini').")

            except FileNotFoundError:
                self.die("No 'config.ini' or '.defaultconf' found.")

    def reload(self):
        self.load()

    def get_opt(self, key, option):
        return self.dict[key][option]

    def die(self, msg='Quitting...'):
        try:
            Globals.log.error(msg)
            Globals.disco.quit()
        except AttributeError:
            print(msg)
            sys.exit()

