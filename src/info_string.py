import os

from syntax_highlight import syntax_highlight, just_add_line_numbers
from function_type_names import dialog_function_type_names

# Get a pretty string from an INFO record
def pretty_info_string(
    config, wrapper, info_record,
    use_text=None, show_topic=True, verbose=False
):
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
    context_str = b"  &  ".join(context) if len(context) else b"<Anyone>"
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
    if player_faction_name:
        conditions.append("- If the player is a member of %s" %
            player_faction_name.encode("latin-1", "ignore")
        )
    info_data = info_record.prop("info_data")
    if info_data:
        dialog_type = info_record.dialog_topic_record.prop("dialog_type", "type")
        disposition = info_data["disposition"]
        if disposition is not None and dialog_type == 4:
            conditions.append("- If quest status is %s" % disposition)
        if disposition and disposition > 0:
            conditions.append("- If disposition is at least %s" % disposition)
        gender = info_data["gender"]
        if gender == 0:
            conditions.append("- If NPC is male")
        elif gender == 1:
            conditions.append("- If NPC is female")
        faction_rank = info_data["faction_rank"]
        if faction_rank and faction_rank > 0:
            conditions.append("- If NPC rank is at least %s" % faction_rank)
        player_rank = info_data["player_rank"]
        if player_rank and player_rank > 0:
            conditions.append("- If player rank is at least %s" % player_rank)
    info_functions = info_record["functions"]
    if info_functions:
        func_numbers = [
            sub_record for sub_record in info_record.sub_records
            if sub_record.type_name in (b"INTV", b"FLTV")
        ]
        for i in range(len(info_functions)):
            function = info_functions[i]
            number = func_numbers[i][0].value if i < len(func_numbers) else 0
            func_string = dialog_function_string(function, number)
            if func_string: conditions.append(func_string)
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
        

# Takes an SCVR sub-record and the value of the corresponding INTV or FLTV
def dialog_function_string(function, number_value):
    func_type = function["type"]
    comparison = function["comparison"]
    variable = function["variable"].encode("latin-1", "ignore")
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
        template = "- If function %s %s %s"
        func_name = dialog_function_type_names[function["function"]]
        return template % (func_name, comp_string, number_value)
    elif func_type == b"2": # Global
        template = "- If global %s %s %s"
        return template % (variable, comp_string, number_value)
    elif func_type == b"3": # Local
        template = "- If local %s %s %s"
        return template % (variable, comp_string, number_value)
    elif func_type == b"4": # Journal state
        template = "- If quest %s %s %s"
        return template % (variable, comp_string, number_value)
    elif func_type == b"5": # Item
        template = "- If player inventory contains %s %s %s"
        return template % (variable, comp_string, number_value)
    elif func_type == b"6": # Dead
        if comp_string in ("=", "<=") and number_value == 0:
            return "- If NPC %s is not dead" % variable
        elif comp_string in ("<") and number_value == 1:
            return "- If NPC %s is not dead" % variable
        elif comp_string in ("!=") and number_value == 1:
            return "- If NPC %s has not been killed exactly once" % variable
        template = "- If NPC death count for %s %s %s"
        return template % (variable, comp_string, number_value)
    elif func_type == b"7": # Not ID
        if ((comp_string in ("=", "<=") and number_value == 0) or
            (comp_string in ("!=", "<") and number_value == 1)
        ): return "- If NPC is not %s" % variable
        elif ((comp_string in ("=", ">=") and number_value == 1) or
            (comp_string in ("!=", ">") and number_value == 0)
        ): return "- If NPC is %s" % variable
        template = "- If not NPC ID %s %s %s"
        return template % (variable, comp_string, number_value)
    elif func_type == b"8": # Not Faction
        if ((comp_string in ("=", "<=") and number_value == 0) or
            (comp_string in ("!=", "<") and number_value == 1)
        ): return "- If NPC is not a member of faction %s" % variable
        elif ((comp_string in ("=", ">=") and number_value == 1) or
            (comp_string in ("!=", ">") and number_value == 0)
        ): return "- If NPC is a member of faction %s" % variable
        template = "- If not NPC faction %s %s %s"
        return template % (variable, comp_string, number_value)
    elif func_type == b"9": # Not Class
        if ((comp_string in ("=", "<=") and number_value == 0) or
            (comp_string in ("!=", "<") and number_value == 1)
        ): return "- If NPC is not a member of class %s" % variable
        elif ((comp_string in ("=", ">=") and number_value == 1) or
            (comp_string in ("!=", ">") and number_value == 0)
        ): return "- If NPC is a member of class %s" % variable
        template = "- If not NPC class %s %s %s"
        return template % (variable, comp_string, number_value)
    elif func_type == b"A": # Not Race
        if ((comp_string in ("=", "<=") and number_value == 0) or
            (comp_string in ("!=", "<") and number_value == 1)
        ): return "- If NPC is not a member of race %s" % variable
        elif ((comp_string in ("=", ">=") and number_value == 1) or
            (comp_string in ("!=", ">") and number_value == 0)
        ): return "- If NPC is a member of race %s" % variable
        template = "- If not NPC race %s %s %s"
        return template % (variable, comp_string, number_value)
    elif func_type == b"B": # Not Cell
        if ((comp_string in ("=", "<=") and number_value == 0) or
            (comp_string in ("!=", "<") and number_value == 1)
        ): return "- If NPC is not located in cell %s" % variable
        elif ((comp_string in ("=", ">=") and number_value == 1) or
            (comp_string in ("!=", ">") and number_value == 0)
        ): return "- If NPC is located in cell %s" % variable
        template = "- If not NPC cell %s %s %s"
        return template % (variable, comp_string, number_value)
    elif func_type == b"C": # Not Local
        template = "- If not local %s %s %s"
        return template % (variable, comp_string, number_value)
    else:
        raise ValueError("Unknown function type.")
