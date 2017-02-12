import os
import sys
import re
import json
import traceback
import types
from collections import OrderedDict, defaultdict, deque
import importlib as imp
import importlib.machinery
from modules.globals import Globals
from modules.pluginbase import PluginBase
import discord

class PluginLoader:

    plugins = OrderedDict()
    hooks = {}
    modules = {}
    channel_disabled = defaultdict(list)
    load_order = {'core': [], 'uncore': []}
    root = os.path.abspath(os.path.join(os.path.join(os.path.dirname(__file__), os.pardir), 'plugins/'))
    lofile = root + '/load.order'
    plugin_queue = deque()

    def __init__(self):
        Globals.pluginloader = self
        # Load plugins
        self.read_load_order()
        self.load_plugins()
        self.write_load_order()
        self.order()

    def get_plugin(self, attribute, value, types):
        for fname, plugin in ((x, y) for x, y in self.plugins.items() if y.type in types):
            attr = getattr(plugin, attribute)
            if attribute == 'trigger':
                for evn, values in attr:
                    if value in values[0]:
                        return plugin
            else:
                if value == attr:
                    return plugin

    async def generate_plugin_queue(self, event, is_command=False, **kwargs):
        self.purge_hooks()
        self.plugin_queue.clear()
        for plugin in self.plugins.values():
            fname = self.plugin_to_fname(plugin)
            triggers = plugin.trigger.get(event, [])
            if not isinstance(triggers, list):
                triggers = (triggers,)  # make trigger a tuple so we can loop through correctly
            for trigger, cmd, fn in triggers:
                if not is_command and not cmd and isinstance(trigger, type(re.compile(''))):  # use regex
                    match = re.search(trigger, kwargs['message'].content)
                    if match:
                        self.plugin_queue.append((plugin, event, match, fn))
                        if fname in self.hooks.keys():
                            for hooked in self.hooks.get(fname, ''):
                                self.plugin_queue.append((self.plugins.get(hooked), fname))
                                Globals.log.debug('Hook plugin added')
                elif is_command and isinstance(trigger, str) and trigger.lower() == PluginBase.Command(kwargs['message']).cmd.lower():
                    self.plugin_queue.append((plugin, event, trigger, fn))
                    if fname in self.hooks.keys():
                        for hooked in self.hooks.get(fname, ''):
                            self.plugin_queue.append((self.plugins.get(hooked), fname))
                            Globals.log.debug('Hook plugin added')
                elif not is_command and isinstance(trigger, types.FunctionType) and trigger(**kwargs):
                    self.plugin_queue.append((plugin, event, trigger, fn))
                    if fname in self.hooks.keys():
                        for hooked in self.hooks.get(fname, ''):
                            self.plugin_queue.append((self.plugins.get(hooked), fname))
                            Globals.log.debug('Hook plugin added')
        if len(self.plugin_queue) > 0:
            Globals.log.debug('Generated new plugin queue with %s plugins' % len(self.plugin_queue))
            return True

    async def execute_plugin_queue(self, channel,  **kwargs):
        if len(self.plugin_queue) <= 0:
            return -1
        plugin, event, trigger, fn = self.plugin_queue.popleft()
        kwargs['trigger'] = trigger
        self.purge_hooks()
        Globals.log.debug('Plugin Executing: ' + plugin.name)
        try:
            if self.plugin_to_fname(plugin) in self.channel_disabled[channel]:
                return False
            test = True
            if callable(trigger):
                test = trigger(**kwargs)
            if test:
                if await fn(**kwargs) and (self.plugin_to_fname(plugin) not in self.hooks.keys()):
                    Globals.log.debug('Plugin execution satisfied clearing queue')
                    self.plugin_queue.clear()
                    return True
                elif trigger in self.hooks.keys():
                    Globals.log.debug('Plugin Executing Trigger: ' + plugin.name)
                    return False
                else:
                    return False
            else:
                return False
        except Exception as err:
            Globals.log.error('Unhandled Exception from plugin: %s : %s' % (plugin.name, traceback.format_exc()))
            await Globals.disco.send_file(channel, fp=sys.path[0] + '/static/miharu_chibi_everything_small_crop_gradient.png', content=f'gets hit by unhandled **{type(err).__name__}** thrown from {plugin.name} plugin')
            return False

    def load_plugins(self, load='*'):
        status = 0
        root = self.root
        try:
            sys.path.insert(0, root)
            plugin_path = os.path.abspath(root)
            plugins_dirs = []
            with os.scandir(plugin_path) as it:
                for entry in it:
                    if entry.is_dir():
                        plugins_dirs.append((entry.path, entry.name))
            for path, fname in plugins_dirs:
                try:
                    loader = imp.machinery.SourceFileLoader(fname, path + '/' + fname + '.py')
                    mod = loader.load_module()
                    self.modules.update({fname: mod})
                    plugin = mod.Plugin()
                    try:  # test plugin for required params
                        getattr(plugin, 'name')
                        if getattr(plugin, 'type') not in PluginBase.PluginType:
                            raise AttributeError
                        getattr(plugin, 'trigger')
                        getattr(plugin, 'help')
                    except AttributeError:
                        Globals.log.error('Plugin failed test:' + fname)
                        continue
                    if fname == load and fname not in self.plugins.keys():
                        self.plugins[fname] = plugin
                        Globals.log.info('Plugin loaded: ' + fname)
                        status = 1
                        break
                    elif load == '*' and fname not in self.plugins.keys():
                        self.plugins[fname] = plugin
                        Globals.log.info('Plugin loaded: ' + fname)
                        status = 2
                    elif fname == load and fname in self.plugins.keys():
                        status = -1
                        break
                except Exception as err:
                    status = -2
                    Globals.log.error('Plugin \'' + fname + '\' load failed: ' + str(err))
                    continue
            sys.path.pop(0)
        except Exception as err:
            Globals.log.error('Plugin load failed: ' + str(err))
        finally:
            self.write_load_order()
            self.order()
        return status

    def unload_plugin(self, plugin):
        if plugin in self.plugins.keys():
            if self.plugins[plugin].type is not PluginBase.PluginType.CORE:
                self.plugins.pop(plugin)
                Globals.log.info('Plugin unloaded: ' + plugin)
                return 1
            else:
                return -1
        return 0

    def reload_plugin(self, plugin):
        if plugin in self.plugins.keys() and plugin in self.modules.keys():
            try:
                mod = imp.reload(self.modules.get(plugin))
                self.modules.update({plugin: mod})
                self.plugins.update({plugin: mod.Plugin()})
                return 1
            except Exception as err:
                Globals.log.error('Plugin \'' + plugin + '\' reload failed: ' + str(err) + traceback.format_exc())
                return -2
        else:
            return 0

    def read_load_order(self):
        try:
            with open(self.lofile, 'r') as f:
                data = f.read()
                try:
                    json_data = json.loads(data)
                    if isinstance(json_data, dict):
                        self.load_order = json_data
                        return True
                    else:
                        raise ValueError
                except ValueError:
                    Globals.log.info('Load order file not properly formatted -> skipped')
                    return False
        except FileNotFoundError:
            Globals.log.error('Load order file does not exist, creating one...')
            self.write_load_order()

    def write_load_order(self):
        for fname in self.plugins.keys():
            if self.plugins[fname].type is PluginBase.PluginType.CORE:  # core plugin
                if fname not in self.load_order['core']:
                    self.load_order['core'].append(fname)
            else:
                if fname not in self.load_order['uncore']:
                    self.load_order['uncore'].append(fname)
        with open(self.lofile, 'w') as f:
            f.write(json.dumps(self.load_order, indent=4))

    def order(self):
        for key in self.load_order['core']:
            if key in self.plugins.keys():
                self.plugins.move_to_end(key)
        for key in self.load_order['uncore']:
            if key in self.plugins.keys():
                self.plugins.move_to_end(key)

    def disable(self, fname, channel):
        for name, plugin in self.plugins.items():
            if fname == name:
                if fname not in self.channel_disabled[channel]:
                    if plugin.type is not PluginBase.PluginType.CORE:
                        self.channel_disabled[channel].append(fname)
                        Globals.log.info('Plugin %s disabled on %s' % (fname, channel))
                        return 1  # success
                    else:
                        return -1  # cannot disable core type
                else:
                    return 2  # already disabled

        return 0  # no such plugin

    def enable(self, fname, channel):
        for name, plugin in self.plugins.items():
            if fname == name:
                if fname in self.channel_disabled[channel]:
                    if plugin.type is not PluginBase.PluginType.CORE:
                        self.channel_disabled[channel].remove(fname)
                        Globals.log.info('Plugin %s enabled on %s' % (fname, channel))
                        return 1  # success
                else:
                    return 2  # already enabled

        return 0  # no such plugin

    def reloadorder(self):
        success = self.read_load_order()
        self.write_load_order()
        self.order()
        return success

    def add_hook(self, plugin_name, trigger_name):
        if plugin_name not in self.hooks.get(trigger_name, '') and self.hooks.get(trigger_name, False):
            self.hooks[trigger_name] += (plugin_name,)
        elif not self.hooks.get(trigger_name, False):
            self.hooks[trigger_name] = (plugin_name,)

    def purge_hooks(self):
        for hook, hooked in list(self.hooks.items()):
            if hook not in self.plugins.keys():
                Globals.log.debug('Hook(s) by %s purged' % hook)
                self.hooks.pop(hook)
            else:
                for h in [x for x in hooked if x not in self.plugins.keys()]:
                    Globals.log.debug('Hook by %s on %s purged' % (hook, h))
                self.hooks[hook] = [x for x in hooked if x in self.plugins.keys()]

    def plugin_to_fname(self, plugin):
        return list(self.plugins.keys())[list(self.plugins.values()).index(plugin)]
