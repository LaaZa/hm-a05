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
    def set_channel_command_prefix(cls, channel, prefix: str=default_command_prefix) -> None:
        cls.__channel_command_prefix.update({channel: prefix})

    @classmethod
    def channel_command_prefix(cls, channel) -> str:
        return cls.__channel_command_prefix.get(channel, cls.default_command_prefix)


@register
class SavedVar:

    _picklefile = path.abspath(path.join(path.join(path.dirname(__file__), pardir), 'save.pickle'))
    pickledata = {}
    loaded = False
    saved = False

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
            self.update()
            self.save()

    @classmethod
    def _load(cls):
        try:
            with open(cls._picklefile, 'rb') as pic:
                cls.pickledata = pickle.load(pic)
            cls.loaded = True
        except Exception as e:
            Globals.log.error(f'Could not load pickle: {str(e)}')

    def update(self):
        self.pickledata.update({f'{self._file}#{self._name}': self._data})
        self.saved = False

    @classmethod
    def save(cls):
        if not cls.saved:
            try:
                with open(cls._picklefile, 'wb') as pic:
                    pickle.dump(cls.pickledata, pic)
                cls.saved = True
            except Exception as e:
                Globals.log.error(f'Could not save pickle: {str(e)}')
        else:
            Globals.log.debug('already saved')

    @property
    def x(self):
        return self.pickledata.get(f'{self._file}#{self._name}', None)

    @x.setter
    def x(self, val):
        self._data = val
        self.update()

    def __repr__(self):
        return str(self.x)
