try:
    from ConfigParser import ConfigParser # Python 2
except ImportError:
    from configparser import ConfigParser # Python 3

def parse_config(config_path):
    config_parser = ConfigParser()
    config_parser.read(config_path)
    config_object = {}
    if config_parser.has_option("colors", "substring_colors"):
        value = config_parser.get("colors", "substring_colors")[-1].lower()
        config_object["substring_highlighting"] = (
            value and value != "no" and value != "false"
        )
    if config_parser.has_option("colors", "script_colors"):
        value = config_parser.get("colors", "script_colors")[-1].lower()
        config_object["script_syntax_highlighting"] = (
            value and value != "no" and value != "false"
        )
    if config_parser.has_option("load_file_paths", "paths"):
        config_object["load_paths"] = list(filter(None, (
            config_parser.get("load_file_paths", "paths").split("\n")
        )))
    return config_object
    