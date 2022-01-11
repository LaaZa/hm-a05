import pickle
import inspect
from os import path, pardir
from varname.helpers import register

class Globals:
    config_data = None
    log = None
    disco = None
    default_command_prefix = None
    __channel_command_prefix = {}
    pluginloader = None
    events = None
    database_file = None
    permissions = None

    @classmethod
    def set_channel_command_prefix(cls, channel, prefix=default_command_prefix):
        cls.__channel_command_prefix.update({channel: prefix})

    @classmethod
    def channel_command_prefix(cls, channel):
        return cls.__channel_command_prefix.get(channel, cls.default_command_prefix)

    @register
    class SavedVar:

        _picklefile = path.abspath(path.join(path.join(path.dirname(__file__), pardir), 'save.pickle'))
        pickledata = {}
        loaded = False

        def __init__(self, var=None):

            frame = inspect.currentframe()
            frame = frame.f_back.f_back
            code = frame.f_code
            self._file = path.relpath(code.co_filename, path.join(path.dirname(__file__), pardir))
            self._name = self.__varname__
            self._data = var
            if not self.loaded:
                self._load()
            if not self.loaded and f'{self._file}#{self._name}' not in self.pickledata.keys():
                self.save()

        def _load(self):
            try:
                with open(self._picklefile, 'rb') as pic:
                    self.pickledata = pickle.load(pic)
                self.loaded = True
            except Exception:
                pass

        def save(self):
            with open(self._picklefile, 'wb') as pic:
                self.pickledata.update({f'{self._file}#{self._name}': self._data})
                pickle.dump(self.pickledata, pic)

        @property
        def x(self):
            return self.pickledata.get(f'{self._file}#{self._name}', None)

        @x.setter
        def x(self, val):
            self._data = val
            self.save()

        def __repr__(self):
            return self.x
