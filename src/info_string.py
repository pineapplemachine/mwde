import os
import re

from syntax_highlight import syntax_highlight, just_add_line_numbers
from function_type_names import dialog_function_type_names

reset_color = "\033[0m"
function_color = "\033[95m"
number_color = "\033[93m"
string_color = "\033[92m"
comparison_color = "\033[37m"

# Helpers
def pretty_number(config, value):
    if config.get("info_function_highlighting"):
        return number_color + str(value) + reset_color
    else:
        return str(value)
def pretty_string(config, value):
    if config.get("info_function_highlighting"):
        return string_color + "\"" + str(value) + "\"" + reset_color
    else:
        return "\"%s\"" % str(value)

# Get a pretty string from an INFO record
def pretty_info_string(
    config, wrapper, es, info_record,
    use_text=None, show_topic=True, verbose=False
):
    dialog_type = info_record.dialog_topic_record.prop("dialog_type", "type")
    context = []
    actor_name = info_record.prop("actor_name", "name")
    race_name = info_record.prop("race_name", "name")
    class_name = info_record.prop("class_name", "name")
    faction_name = info_record.prop("faction_name", "name")
    cell_name = info_record.prop("cell_name", "name")
    if actor_name:
        context.append(b"Actor: %s" % actor_name)
    if race_name:
        context.append(b"Race: %s" % race_name)
    if class_name:
        context.append(b"Class: %s" % class_name)
    if faction_name:
        context.append(b"Faction: %s" % faction_name)
    if cell_name:
        context.append(b"Cell: %s" % cell_name)
    context_str = b"  &  ".join(context) if len(context) else (
        b"<Journal>" if dialog_type == 4 else b"<Anyone>"
    )
    if show_topic: context_str += b"  (%s)" % (
        info_record.dialog_topic_record.prop("name", "name")
    )
    response_text = (
        use_text if use_text else info_record.prop("response_text", "text")
    )
    response_lines = list(map(
        (lambda l: bytes(l.encode("latin-1", "ignore"))),
        wrapper.wrap(response_text)
    ))
    # Handle substring highlighting -
    # don't highlight blanks at the end and beginning of lines
    for i in range(len(response_lines)):
        normal_i = response_lines[i].rfind(wrapper.normal)
        emphasis_i = response_lines[i].rfind(wrapper.emphasis)
        if emphasis_i > normal_i:
            response_lines[i] += wrapper.normal
            if i + 1 < len(response_lines):
                non_space_i = 0
                for j in range(4):
                    non_space_i = j
                    if response_lines[i + 1][j] != " ": break
                response_lines[i + 1] = (
                    response_lines[i + 1][:non_space_i] +
                    wrapper.emphasis +
                    response_lines[i + 1][non_space_i:]
                )
    wrapped_text = b"\n".join(response_lines)
    wrapped_text = wrapped_text.replace(b"\x92", b"'") # Fix funky edge case
    if not verbose:
        output_text = context_str + b"\n" + wrapped_text
        return output_text.decode("latin-1")
    # Build a list of "If <condition>" strings...
    conditions = []
    player_faction_name = info_record.prop("player_faction_name", "name")
    info_data = info_record.prop("info_data")
    player_faction_rank = info_data["player_faction_rank"] if info_data else None
    if player_faction_name and player_faction_rank == 0:
        conditions.append("- If player is not a member of faction %s" %
            player_faction_name.decode("latin-1", "ignore")
        )
    elif (player_faction_name and player_faction_rank > 0 and
        player_faction_rank is not None
    ):
        rank_name = es.get_faction_rank_name(
            player_faction_name, player_faction_rank
        )
        conditions.append("- If player rank in faction %s is %s%s" % (
            player_faction_name.decode("latin-1", "ignore"),
            pretty_number(config, player_faction_rank),
            " (%s)" % rank_name.decode("latin-1", "ignore") if rank_name else ""
        ))
    elif player_faction_name:
        conditions.append("- If player is a member of faction %s" %
            player_faction_name.decode("latin-1", "ignore")
        )
    if info_data:
        disposition = info_data["disposition"]
        if disposition is not None and dialog_type == 4:
            conditions.append("- If quest status is %s" %
                pretty_number(config, disposition)
            )
        elif disposition and disposition > 0:
            conditions.append("- If disposition is at least %s" %
                pretty_number(config, disposition)
            )
        gender = info_data["gender"]
        if gender == 0:
            conditions.append("- If NPC gender is male")
        elif gender == 1:
            conditions.append("- If NPC gender is female")
        faction_rank = info_data["faction_rank"]
        if faction_rank and faction_rank > 0:
            actor_name = info_record.prop("actor_name", "name")
            faction_name = info_record.prop("faction_name", "name")
            rank_name = None
            if actor_name and not faction_name:
                actor_record = es.get_record_by_name_id(b"NPC_", actor_name)
                if actor_record:
                    faction_name = actor_record.prop("faction_name", "name")
            if faction_name:
                rank_name = es.get_faction_rank_name(faction_name, faction_rank)
            conditions.append("- If NPC rank is at least %s%s" % (
                pretty_number(config, faction_rank),
                " (%s)" % rank_name.decode("latin-1") if rank_name else ""
            ))
    info_functions = info_record["functions"]
    if info_functions:
        func_numbers = [
            sub_record for sub_record in info_record.sub_records
            if sub_record.type_name in (b"INTV", b"FLTV")
        ]
        for i in range(len(info_functions)):
            function = info_functions[i]
            number = func_numbers[i][0].value if i < len(func_numbers) else 0
            func_string = dialog_function_string(
                config, es, info_record, function, number
            )
            if func_string:
                conditions.append(func_string)
    # Put it all together
    id_number = info_record.prop("info_id", "info_id")
    result_text = info_record.prop("result_text", "text")
    conditions_str = b"\n".join(map(
        lambda l: b"  " + bytes(l.encode("latin-1", "ignore")), conditions
    ))
    es_file_path = os.path.basename(info_record.es_file.path).encode(
        "latin-1", "ignore"
    )
    overwrite_str = b""
    if info_record.overwritten_by_record:
        overwrite_file = os.path.basename(
            info_record.overwritten_by_record.es_file.path
        ).encode("latin-1", "ignore")
        if len(info_record.overwritten_by_record["DELE"]):
            overwrite_str = b" (Removed by \"%s\")" % overwrite_file
        else:
            overwrite_str = b" (Overwritten by \"%s\")" % overwrite_file
    output_str = (
        b"Info ID " + id_number +
        (b" in \"%s\"" % es_file_path) +
        overwrite_str + b"\n" +
        context_str + b"\n" +
        ((conditions_str + b"\n") if conditions_str else b"") +
        b"Response Text:\n" + wrapped_text
    )
    if result_text and len(result_text.strip()):
        output_str += (b"\n" + b"Result Text:\n" + (
            syntax_highlight(result_text).encode("latin-1", "ignore")
            if config.get("script_syntax_highlighting") else
            just_add_line_numbers(result_text)
        ))
    return output_str.decode("latin-1")



# Helper for a common case for dialog_function_string
def common_dialog_function_string(
    config, func_name, variable_name, comparison, number_value,
    func_color=True
):
    if config.get("info_function_highlighting"):
        return "- If %s%s%s %s %s%s%s %s%s%s" % (
            (function_color if func_color else ""), func_name, reset_color,
            variable_name,
            comparison_color, comparison, reset_color,
            number_color, number_value, reset_color,
        )
    else:
        return "- If %s %s %s %s" % (
            func_name, variable_name, comparison, number_value
        )

# Takes an SCVR sub-record and the value of the corresponding INTV or FLTV
def dialog_function_string(config, es, info_record, function, number_value):
    func_type = function["type"]
    func_id = function["function"]
    comparison = function["comparison"]
    variable = function["variable"].decode("latin-1")
    comp_string = {
        b"0": "=",
        b"1": "!=",
        b"2": ">",
        b"3": ">=",
        b"4": "<",
        b"5": "<=",
    }.get(comparison, "???")
    if func_type == b"0": # Unused
        return None
    if func_type == b"1": # Function, e.g. "PC Axe > 1"
        func_name = dialog_function_type_names[func_id]
        if func_id == b"38": # Player Gender
            return common_dialog_function_string(config, "function",
                func_name, comp_string, number_value
            ) + " (%s)" % ("female" if number_value else "male")
        elif func_id == b"39": # Player Expelled From NPC Faction
            actor_name = info_record.prop("actor_name", "name")
            faction_name = info_record.prop("faction_name", "name")
            if actor_name and not faction_name:
                actor_record = es.get_record_by_name_id(b"NPC_", actor_name)
                if actor_record:
                    faction_name = actor_record.prop("faction_name", "name")
            if faction_name:
                return common_dialog_function_string(config, "function",
                    func_name, comp_string, number_value
                ) + (" (%s)" %
                    faction_name.decode("latin-1")
                )
        elif func_id == b"50": # Previous Dialog Choice
            choice_name = get_dialog_choice_name(es, info_record, number_value)
            if choice_name:
                return common_dialog_function_string(config, "function",
                    func_name, comp_string, number_value
                ) + "\n  - Choice: %s" % (
                    pretty_string(config, choice_name)
                )
        return common_dialog_function_string(config, "function",
            func_name, comp_string, number_value
        )
    elif func_type == b"2": # Global
        return common_dialog_function_string(config, "global",
            variable, comp_string, number_value
        )
    elif func_type == b"3": # Local
        return common_dialog_function_string(config, "local",
            variable, comp_string, number_value
        )
    elif func_type == b"4": # Journal state
        return common_dialog_function_string(config, "quest",
            variable, comp_string, number_value
        )
    elif func_type == b"5": # Item
        return common_dialog_function_string(config, "player inventory",
            variable, comp_string, number_value
        )
    elif func_type == b"6": # Dead
        if comp_string in ("=", "<=") and number_value == 0:
            return "- If NPC %s is not dead" % variable
        elif comp_string in ("<") and number_value == 1:
            return "- If NPC %s is not dead" % variable
        elif comp_string in ("!=") and number_value == 1:
            return "- If NPC %s has not been killed exactly once" % variable
        return common_dialog_function_string(config, "NPC death count for",
            variable, comp_string, number_value, func_color=False
        )
    elif func_type == b"7": # Not ID
        if ((comp_string in ("=", "<=") and number_value == 0) or
            (comp_string in ("!=", "<") and number_value == 1)
        ): return "- If NPC is not %s" % variable
        elif ((comp_string in ("=", ">=") and number_value == 1) or
            (comp_string in ("!=", ">") and number_value == 0)
        ): return "- If NPC is %s" % variable
        return common_dialog_function_string(config, "not NPC ID",
            variable, comp_string, number_value, func_color=False
        )
    elif func_type == b"8": # Not Faction
        if ((comp_string in ("=", "<=") and number_value == 0) or
            (comp_string in ("!=", "<") and number_value == 1)
        ): return "- If NPC is not a member of faction %s" % variable
        elif ((comp_string in ("=", ">=") and number_value == 1) or
            (comp_string in ("!=", ">") and number_value == 0)
        ): return "- If NPC is a member of faction %s" % variable
        return common_dialog_function_string(config, "not NPC faction",
            variable, comp_string, number_value, func_color=False
        )
    elif func_type == b"9": # Not Class
        if ((comp_string in ("=", "<=") and number_value == 0) or
            (comp_string in ("!=", "<") and number_value == 1)
        ): return "- If NPC is not a member of class %s" % variable
        elif ((comp_string in ("=", ">=") and number_value == 1) or
            (comp_string in ("!=", ">") and number_value == 0)
        ): return "- If NPC is a member of class %s" % variable
        return common_dialog_function_string(config, "not NPC class",
            variable, comp_string, number_value, func_color=False
        )
    elif func_type == b"A": # Not Race
        if ((comp_string in ("=", "<=") and number_value == 0) or
            (comp_string in ("!=", "<") and number_value == 1)
        ): return "- If NPC is not a member of race %s" % variable
        elif ((comp_string in ("=", ">=") and number_value == 1) or
            (comp_string in ("!=", ">") and number_value == 0)
        ): return "- If NPC is a member of race %s" % variable
        return common_dialog_function_string(config, "not NPC race",
            variable, comp_string, number_value, func_color=False
        )
    elif func_type == b"B": # Not Cell
        if ((comp_string in ("=", "<=") and number_value == 0) or
            (comp_string in ("!=", "<") and number_value == 1)
        ): return "- If NPC is not located in cell %s" % variable
        elif ((comp_string in ("=", ">=") and number_value == 1) or
            (comp_string in ("!=", ">") and number_value == 0)
        ): return "- If NPC is located in cell %s" % variable
        return common_dialog_function_string(config, "not NPC cell",
            variable, comp_string, number_value, func_color=False
        )
    elif func_type == b"C": # Not Local
        return common_dialog_function_string(config, "not local",
            variable, comp_string, number_value
        )
    else:
        raise ValueError("Unknown function type.")

dialog_choice_pattern = re.compile(r'"(.*?)"\s*(\d+)')
def get_dialog_choice_name(es, info_record, choice_number):
    on_record = info_record
    while on_record and on_record.type_name == b"INFO":
        next_info_id = on_record.prop("next_id", "info_id")
        if not next_info_id: return None
        next_info = es.get_info_record_by_id(int(next_info_id))
        if not next_info: return None
        on_record = next_info
        result_text = on_record.prop("result_text", "text")
        if not result_text: continue
        result_lines = result_text.decode("latin-1").split("\n")
        for line in result_lines:
            if line.strip().lower().startswith("choice"):
                for match in re.finditer(dialog_choice_pattern, line):
                    number = int(match.group(2))
                    if number == choice_number:
                        return match.group(1)
                return None
                
                
