import re
import os
import sys
from get_terminal_size import get_terminal_size
from textwrap import TextWrapper

from normalize_path import normalize_path
from info_string import pretty_info_string
from load_es_file import read_elder_scrolls_file
from file_load_progress import update_load_progress

normal = b"\033[0m"
emphasis = b"\033[42m"

reset_color = "\033[0m"
cell_color = "\033[96m"
region_color = "\033[92m"

wrapper = TextWrapper(
    initial_indent="    ",
    subsequent_indent="  ",
)
wrapper.normal = normal
wrapper.emphasis = emphasis

def get_wrap_width():
    cols = get_terminal_size().columns
    if cols <= 20: return max(1, cols - 2)
    return min(80, cols - 10)



# Flags:
# -i    ...turn on case sensitivity
def do_sub(es, config, text, flags):
    text = bytes(text.encode("latin-1", "ignore"))
    if len(text) < 3:
        print("Search string too short. Try a regex?\n")
        return
    wrapper.width = get_wrap_width()
    case_sensitive = flags.get("i")
    match_text = text if case_sensitive else text.lower()
    if case_sensitive:
        print("Starting case-sensitive substring search.\n")
    else:
        print("Starting case-insensitive substring search.\n")
    result_count = 0
    print("begin record search")
    for record in es.iter_info_records(include_overwritten=flags.get("O")):
        response_text = record.prop("response_text", "text")
        if not response_text: continue
        match_response_text = (
            response_text if case_sensitive else response_text.lower()
        )
        index = match_response_text.find(match_text)
        if index < 0: continue
        result_count += 1
        if config.get("substring_highlighting"):
            indexes = [index]
            while True:
                index = match_response_text.find(match_text, index + len(text))
                if index < 0: break
                indexes.insert(0, index)
            for index in indexes:
                high = index + len(text)
                response_text = (
                    response_text[:index] + emphasis +
                    response_text[index:high] + normal  +
                    response_text[high:]
                )
        print(pretty_info_string(
            config, wrapper, es, record, use_text=response_text,
            verbose=flags.get("V")
        ) + "\n")
    print("Finished showing %s results.\n" % result_count)

# Flags:
# -i
# -s
# -m
def do_re(es, config, text, flags):
    text = bytes(text.encode("latin-1", "ignore"))
    if len(text) == 0:
        print("Must provide a pattern.\n")
        return
    wrapper.width = get_wrap_width()
    re_flags = 0
    if flags.get("i"): re_flags += re.IGNORECASE
    if flags.get("s"): re_flags += re.DOTALL
    if flags.get("m"): re_flags += re.MULTILINE
    pattern = None
    try:
        pattern = re.compile(text, re_flags)
    except Exception as e:
        print("Regex pattern error: " + str(e))
        return
    print("Starting regular expression search.\n")
    result_count = 0
    for record in es.iter_info_records(include_overwritten=flags.get("O")):
        response_text = record.prop("response_text", "text")
        if not response_text: continue
        matches = list(re.finditer(pattern, response_text))
        if len(matches) == 0: continue
        result_count += 1
        if config.get("substring_highlighting"):
            for match in matches[::-1]:
                index = match.start(0)
                high = match.end(0)
                response_text = (
                    response_text[:index] + emphasis +
                    response_text[index:high] + normal  +
                    response_text[high:]
                )
        print(pretty_info_string(
            config, wrapper, es, record, use_text=response_text,
            verbose=flags.get("V")
        ) + "\n")
    print("Finished showing %s results.\n" % result_count)

# Flags:
# -r    ...include results for same race
# -c    ...include results for same class
# -f    ...include results for same faction
def do_npc(es, config, text, flags):
    text = bytes(text.encode("latin-1", "ignore"))
    if len(text) == 0:
        print("Must provide an NPC name.\n")
        return
    print("Starting NPC search.")
    if flags.get("r"): print("Including general race dialog.")
    if flags.get("c"): print("Including general class dialog.")
    if flags.get("f"): print("Including general faction dialog.")
    print("")
    wrapper.width = get_wrap_width()
    npc_record = es.get_record_by_name_input("NPC_", text.lower())
    if not npc_record:
        print("No matching NPC.\n")
        return
    npc_name = npc_record.prop("name", "name")
    result_count = 0
    for record in es.iter_info_records(include_overwritten=flags.get("O")):
        actor_name = record.prop("actor_name", "name")
        race_name = record.prop("race_name", "name")
        class_name = record.prop("class_name", "name")
        faction_name = record.prop("faction_name", "name")
        npc_race = npc_record.prop("race_name", "name")
        npc_class = npc_record.prop("class_name", "name")
        npc_faction = npc_record.prop("faction_name", "name")
        match = False
        if actor_name and actor_name != npc_name: continue
        if race_name and race_name != npc_race: continue
        if class_name and class_name != npc_class: continue
        if faction_name and faction_name != npc_faction: continue
        match = (actor_name == npc_name)
        if not match and flags.get("r"):
            match = (race_name == npc_race)
        if not match and flags.get("c"):
            match = (class_name == npc_class)
        if not match and flags.get("f"):
            match = (faction_name == npc_faction)
        if match:
            print(pretty_info_string(
                config, wrapper, es, record, verbose=flags.get("V")
            ) + "\n")
            result_count += 1
    print("Finished showing %s results.\n" % result_count)

def do_race(es, config, text, flags):
    text = bytes(text.encode("latin-1", "ignore"))
    if len(text) == 0:
        print("Must provide a race name.\n")
        return
    print("Starting race search.\n")
    wrapper.width = get_wrap_width()
    race_record = es.get_record_by_name_input("RACE", text.lower())
    if not race_record:
        print("No matching race.\n")
        return
    race_name = race_record.prop("name", "name")
    result_count = 0
    for record in es.iter_info_records(include_overwritten=flags.get("O")):
        info_race_name = record.prop("race_name", "name")
        if info_race_name == race_name:
            print(pretty_info_string(
                config, wrapper, es, record, verbose=flags.get("V")
            ) + "\n")
            result_count += 1
    print("Finished showing %s results.\n" % result_count)

def do_faction(es, config, text, flags):
    text = bytes(text.encode("latin-1", "ignore"))
    if len(text) == 0:
        print("Must provide a faction name.\n")
        return
    print("Starting faction search.\n")
    wrapper.width = get_wrap_width()
    faction_record = es.get_record_by_name_input("FACT", text.lower())
    if not faction_record:
        print("No matching faction.\n")
        return
    faction_name = faction_record.prop("name", "name")
    result_count = 0
    for record in es.iter_info_records(include_overwritten=flags.get("O")):
        info_faction_name = record.prop("faction_name", "name")
        if info_faction_name == faction_name:
            print(pretty_info_string(
                config, wrapper, es, record, verbose=flags.get("V")
            ) + "\n")
            result_count += 1
    print("Finished showing %s results.\n" % result_count)

# Flags:
# -p    ...prefix match instead of exact match
def do_cell(es, config, text, flags):
    text = bytes(text.encode("latin-1", "ignore"))
    if len(text) == 0:
        print("Must provide a cell name.\n")
        return
    print("Starting cell search.\n")
    wrapper.width = get_wrap_width()
    result_count = 0
    lower_text = text.lower()
    for record in es.iter_info_records(include_overwritten=flags.get("O")):
        cell_name = record.prop("cell_name", "name")
        if cell_name and ((
            flags.get("p") and cell_name.lower().startswith(lower_text)
        ) or (
            not flags.get("p") and cell_name.lower() == lower_text
        )):
            print(pretty_info_string(
                config, wrapper, es, record, verbose=flags.get("V")
            ) + "\n")
            result_count += 1
    print("Finished showing %s results.\n" % result_count)

def do_topic(es, config, text, flags):
    text = bytes(text.encode("latin-1", "ignore"))
    if len(text) == 0:
        print("Must provide a topic name.\n")
        return
    print("Starting topic search.\n")
    wrapper.width = get_wrap_width()
    result_count = 0
    lower_text = text.lower()
    for record in es.iter_info_records(include_overwritten=flags.get("O")):
        topic_name = record.dialog_topic_record.prop("name", "name")
        if topic_name and topic_name.lower().startswith(lower_text):
            print(pretty_info_string(
                config, wrapper, es, record, verbose=flags.get("V")
            ) + "\n")
            result_count += 1
    print("Finished showing %s results.\n" % result_count)

def do_quest(es, config, text, flags):
    text = bytes(text.encode("latin-1", "ignore"))
    if len(text) == 0:
        print("Must provide a quest name.\n")
        return
    print("Starting quest search.\n")
    wrapper.width = get_wrap_width()
    result_count = 0
    lower_text = text.lower()
    for record in es.iter_info_records(include_overwritten=flags.get("O")):
        match = False
        for sub_record in record["SCVR"]:
            if sub_record["variable"].lower() == lower_text:
                match = True
                break
        if not match:
            result_text = record.prop("result_text", "text")
            if result_text: match = lower_text in result_text.lower()
        if not match:
            topic_name = record.dialog_topic_record.prop("name", "name")
            if topic_name: match = (lower_text == topic_name.lower())
        if match:
            print(pretty_info_string(
                config, wrapper, es, record, verbose=flags.get("V")
            ) + "\n")
            result_count += 1
    print("Finished showing %s results.\n" % result_count)

def do_journal(es, config, text, flags):
    text = bytes(text.encode("latin-1", "ignore"))
    if len(text) == 0:
        print("Must provide a quest name.\n")
        return
    print("Starting journal search.\n")
    wrapper.width = get_wrap_width()
    result_count = 0
    lower_text = text.lower()
    for record in es.iter_info_records(include_overwritten=flags.get("O")):
        topic_name = record.dialog_topic_record.prop("name", "name")
        if lower_text == topic_name.lower():
            print(pretty_info_string(
                config, wrapper, es, record, verbose=flags.get("V")
            ) + "\n")
            result_count += 1
    print("Finished showing %s results.\n" % result_count)

# Flags:
# -p    ...prefix match instead of exact match
def do_npcat(es, config, text, flags):
    text = bytes(text.encode("latin-1", "ignore"))
    if len(text) == 0:
        print("Must provide a cell or region name.\n")
        return
    print("Starting NPC search by location.\n")
    wrapper.width = get_wrap_width()
    result_count = 0
    lower_text = text.lower()
    cell_str = (
        cell_color + "Cell:" + reset_color
        if config.get("npcat_list_highlighting") else "Cell:"
    )
    region_str = (
        region_color + "Region:" + reset_color
        if config.get("npcat_list_highlighting") else "Region:"
    )
    for record in es.iter_records():
        if record.type_name != b"CELL": continue
        cell_name = record.prop("name", "name")
        region_name = record.prop("region_name", "name")
        if not ((cell_name and ((
            flags.get("p") and cell_name.lower().startswith(lower_text)
        ) or (
            not flags.get("p") and cell_name.lower() == lower_text
        ))) or (region_name and ((
            flags.get("p") and region_name.lower().startswith(lower_text)
        ) or (
            not flags.get("p") and region_name.lower() == lower_text
        )))):
            continue
        sub_records_len = len(record.sub_records)
        for i in range(sub_records_len):
            sub_record = record.sub_records[i]
            if sub_record.type_name == b"FRMR" and i + 1 < sub_records_len:
                contained_record_name = record.sub_records[i + 1][0].value
                contained_record = es.get_record_by_name_id(
                    b"NPC_", contained_record_name
                )
                if not contained_record:
                    continue
                if not cell_name and not region_name:
                    continue
                elif cell_name and region_name:
                    print("Found: %s  %s %s / %s %s" % (
                        contained_record.prop("name", "name").decode("latin-1"),
                        cell_str, cell_name.decode("latin-1"),
                        region_str, region_name.decode("latin-1"),
                    ))
                elif cell_name:
                    print("Found: %s  %s %s" % (
                        contained_record.prop("name", "name").decode("latin-1"),
                        cell_str, cell_name.decode("latin-1"),
                    ))
                elif region_name:
                    print("Found: %s  %s %s" % (
                        contained_record.prop("name", "name").decode("latin-1"),
                        region_str, region_name.decode("latin-1"),
                    ))
                result_count += 1
    if result_count: print("")
    print("Finished showing %s results.\n" % result_count)

def do_load(es, config, text, flags):
    if len(text) == 0:
        print("Must provide a data file path.\n")
        return
    text = normalize_path(text)
    if not os.path.exists(text):
        print("File does not exist.\n")
        return
    input_base_name = os.path.basename(text)
    for es_file in es.es_files:
        if os.path.basename(es_file.path) == input_base_name:
            print("File \"%s\" is already loaded.\n" % input_base_name)
            return
    path = os.path.normpath(text)
    with open(path, "rb") as binary_file:
        es_file = read_elder_scrolls_file(path, binary_file,
            after_read_record=update_load_progress(path)
        )
    es.add_file(es_file)
    print("\nFinished loading data file. (%s records)\n" % len(es_file.records))

def do_reload(es, config, text, flags):
    if len(text) == 0:
        print("Must provide a data file name.\n")
        return
    text = normalize_path(text)
    input_base_name = os.path.basename(text)
    for i in range(len(es.es_files)):
        es_file = es.es_files[i]
        if os.path.basename(es_file.path) == input_base_name:
            with open(es_file.path, "rb") as binary_file:
                new_file = read_elder_scrolls_file(es_file.path, binary_file,
                    after_read_record=update_load_progress(es_file.path)
                )
            es.es_files[i] = new_file
            print("\nFinished reloading data file. (%s records)\n" %
                len(new_file.records)
            )
            return
    print("File \"%s\" is not loaded.\n" % input_base_name)

def do_unload(es, config, text, flags):
    if len(text) == 0:
        print("Must provide a data file name.\n")
        return
    text = normalize_path(text)
    input_base_name = os.path.basename(text)
    for i in range(len(es.es_files)):
        es_file = es.es_files[i]
        if os.path.basename(es_file.path) == input_base_name:
            del es.es_files[i]
            print("Unloaded data file.\n")
            return
    print("File \"%s\" is not loaded.\n" % input_base_name)
    
