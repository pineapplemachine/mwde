# One thousand thanks to Dave Humphrey's documentation
# http://en.uesp.net/morrow/tech/mw_esm.txt

import sys
import os
import traceback
import argparse

from parse_config import parse_config
from normalize_path import normalize_path
from record_classes import ESData
from load_es_file import read_elder_scrolls_file
from explorer_commands import *
from command_help_text import *

# https://docs.python.org/2/library/readline.html
# https://stackoverflow.com/a/15416166/4099022
try:
    import readline
except ImportError:
    pass



config = {}

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument("--no-colors", action="store_true")
arg_parser.add_argument("--script-colors", action="store_true")
arg_parser.add_argument("--substring-colors", action="store_true")
arg_parser.add_argument("--function-colors", action="store_true")
arg_parser.add_argument("--load-paths", type=str, nargs="+")
arg_parser.add_argument("--config-path", type=str)
args = arg_parser.parse_args()

if args.script_colors:
    config["script_syntax_highlighting"] = True
if args.substring_colors:
    config["substring_highlighting"] = True
if args.function_colors:
    config["info_function_highlighting"] = True
if args.no_colors:
    config["substring_highlighting"] = False
    config["script_syntax_highlighting"] = False
    config["info_function_highlighting"] = False

config_path = "config.ini"
if args.config_path:
    config_path = args.config_path # os.path.join(os.getcwd(), args.config_path)
if os.path.exists(config_path):
    parsed_config_object = None
    try:
        parsed_config_object = parse_config(config_path)
    except Exception as e:
        print("Failed to parse config file: " + str(e))
    if parsed_config_object:
        for key in parsed_config_object:
            if key not in config:
                config[key] = parsed_config_object[key]
elif args.config_path:
    print("Couldn't find config file at \"%s\"." % config_path)

es = ESData([])

load_path_list = []
if isinstance(config.get("load_paths"), list):
    load_path_list.extend(config.get("load_paths"))
if args.load_paths:
    load_path_list.extend(args.load_paths)

if len(load_path_list):
    loaded_count = 0
    for load_path in config["load_paths"]:
        path = os.path.normpath(normalize_path(load_path))
        print("Loading \"%s\"..." % path)
        try:
            with open(path, "rb") as binary_file:
                es_file = read_elder_scrolls_file(path, binary_file)
            es.add_file(es_file)
            loaded_count += 1
        except:
            print("FILE LOAD ERROR. Please report bugs online at")
            print("  https://github.com/pineapplemachine/mwde/issues")
            print(traceback.format_exc())
    if len(config["load_paths"]):
        print("Finished loading %d data files." % loaded_count)

    # "E:/SteamLibrary/steamapps/common/Morrowind/Data Files/Morrowind.esm",
    # "E:/SteamLibrary/steamapps/common/Morrowind/Data Files/Tribunal.esm",
    # "E:/SteamLibrary/steamapps/common/Morrowind/Data Files/Bloodmoon.esm",
    # "E:/SteamLibrary/steamapps/common/Morrowind/Data Files/MoreQuests_WolverineMages.ESP",

def parse_command(input_text):
    command = ""
    options = {}
    text = ""
    first_space = False
    last_was_space = False
    in_text = False
    in_option = False
    for char in input_text.strip():
        if not in_text and (char == " " or char == "\t"):
            first_space = True
            last_was_space = True
        elif last_was_space and not in_text and char == "-":
            in_option = True
            last_was_space = False
        elif in_option:
            options[char] = True
            in_option = False
        elif not first_space:
            command += char
        else:
            text += char
            in_text = True
    return (command, options, text)

try:
    get_input = raw_input
except NameError:
    get_input = input



if config.get("substring_highlighting") or config.get("script_syntax_highlighting"):
    sys.stdout.write("\033[0m")

print("\nMorrowind Dialog Explorer v1.1 is ready.")

while True:
    try:
        command, flags, text = parse_command(get_input("query > "))
        if command == "help":
            print("\n" + {
                "sub": sub_help_text,
                "re": re_help_text,
                "npc": npc_help_text,
                "race": race_help_text,
                "faction": faction_help_text,
                "cell": cell_help_text,
                "topic": topic_help_text,
                "quest": quest_help_text,
                "npcat": npcat_help_text,
                "load": load_help_text,
                "reload": reload_help_text,
                "unload": unload_help_text,
                "about": about_text,
                "quit": quit_help_text,
                "exit": quit_help_text,
            }.get(text, help_text) + "\n")
        elif command == "about":
            print("\n" + about_text + "\n")
        elif command == "quit" or command == "exit":
            print("\nExiting Morrowind Dialog Explorer.\n")
            break
        elif command == "sub":
            do_sub(es, config, text, flags)
        elif command == "re":
            do_re(es, config, text, flags)
        elif command == "npc":
            do_npc(es, config, text, flags)
        elif command == "race":
            do_race(es, config, text, flags)
        elif command == "faction":
            do_faction(es, config, text, flags)
        elif command == "cell":
            do_cell(es, config, text, flags)
        elif command == "topic":
            do_topic(es, config, text, flags)
        elif command == "quest":
            do_quest(es, config, text, flags)
        elif command == "npcat":
            do_npcat(es, config, text, flags)
        elif command == "load":
            do_load(es, config, text, flags)
        elif command == "reload":
            do_reload(es, config, text, flags)
        elif command == "unload":
            do_unload(es, config, text, flags)
        elif len(command):
            print("Unknown command. Type \"help\" for help.")
    except EOFError:
        print("") # Happens sometimes with funny control keys
    except SystemError:
        pass # Happens sometimes with funny control keys
    except KeyboardInterrupt:
        print("\n\nExiting Morrowind Dialog Explorer.\n")
        break
    except Exception as e:
        print("\nCOMMAND ERROR. Please report bugs online at")
        print("  https://github.com/pineapplemachine/mwde/issues")
        print(traceback.format_exc())
