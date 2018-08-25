try:
    from ConfigParser import ConfigParser # Python 2
except ImportError:
    from configparser import ConfigParser # Python 3

def get_boolean(text):
    text = text.strip().lower()
    for option in ("1", "y", "yes", "t", "true"):
        if text == option: return True
    return False

def parse_config(config_path):
    config_parser = ConfigParser()
    config_parser.read(config_path)
    config_object = {}
    if config_parser.has_option("colors", "substring_colors"):
        value = config_parser.get("colors", "substring_colors")
        config_object["substring_highlighting"] = get_boolean(value)
    if config_parser.has_option("colors", "script_colors"):
        value = config_parser.get("colors", "script_colors")
        config_object["script_syntax_highlighting"] = get_boolean(value)
    if config_parser.has_option("colors", "function_colors"):
        value = config_parser.get("colors", "function_colors")
        config_object["info_function_highlighting"] = get_boolean(value)
    if config_parser.has_option("colors", "npcat_colors"):
        value = config_parser.get("colors", "npcat_colors")
        config_object["npcat_list_highlighting"] = get_boolean(value)
    if config_parser.has_option("load_file_paths", "paths"):
        config_object["load_paths"] = list(filter(None, (
            config_parser.get("load_file_paths", "paths").split("\n")
        )))
    return config_object
    