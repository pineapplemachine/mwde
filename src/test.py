from ConfigParser import RawConfigParser
from collections import OrderedDict

# https://stackoverflow.com/a/15848928/3478907
class MultiOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super(MultiOrderedDict, self).__setitem__(key, value)
            # super().__setitem__(key, value) in Python 3

config_parser = RawConfigParser(dict_type=MultiOrderedDict)

# config_parser = ConfigParser()
config_parser.read("../config.ini")

color_section = config_parser.options("colors")
if color_section:
    print "[colors]"
    for option in color_section:
        print option, config_parser.get("colors", option)
else:
    print "no color section"

paths_section = config_parser.options("load_file_paths")

if paths_section:
    print "[load_file_paths]"
    for option in paths_section:
        print option, config_parser.get("load_file_paths", option)
else:
    print "no paths section"

