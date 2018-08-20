from record_classes import *
from sub_record_field_types import *

record_type_list = []

def get_record_type(name):
    for record_type in record_type_list:
        if name == record_type.name:
            return record_type
    # raise LookupError("Unknown record type \"%s\"." % name)

# Special size constants
SubRecordTypeField.variable_size = "v"
SubRecordTypeField.sub_record_size = "s"

record_type_list.append(RecordType("TES3", "main_header", [
    SubRecordType("HEDR", "header", fields=[
        SubRecordTypeField(4, "version", data_float),
        SubRecordTypeField(4, "unknown_1", data_integer_signed),
        SubRecordTypeField(32, "company_name", data_string_padded),
        SubRecordTypeField(256, "file_description", data_string_padded),
        SubRecordTypeField(4, "num_records", data_integer_signed),
    ]),
    SubRecordType("MAST", "required_master_files", fields=[
        SubRecordTypeField("v", "file_name", data_string_variable),
    ]),
    SubRecordType("DATA", "required_master_file_sizes", fields=[
        SubRecordTypeField(8, "file_size", data_integer_signed),
    ]),
]))

record_type_list.append(RecordType("SCPT", "script", [
    SubRecordType("SCHD", "header", fields=[
        SubRecordTypeField(32, "script_name", data_string_padded),
        SubRecordTypeField(4, "num_shorts", data_integer_signed),
        SubRecordTypeField(4, "num_longs", data_integer_signed),
        SubRecordTypeField(4, "num_floats", data_integer_signed),
        SubRecordTypeField(4, "script_data_size", data_integer_signed),
        SubRecordTypeField(4, "local_var_size", data_integer_signed),
    ]),
    SubRecordType("SCVR", "variable_name_list", fields=[
        SubRecordTypeField("s", "variable_names", data_string_list),
    ]),
    SubRecordType("SCDT", "compiled_data", fields=[
        SubRecordTypeField("s", "data", data_string_exact),
    ]),
    SubRecordType("SCTX", "script_text", fields=[
        SubRecordTypeField("s", "text", data_string_exact),
    ]),
]))

record_type_list.append(RecordType("GLOB", "global_variable", [
    SubRecordType("NAME", "name", fields=[
        SubRecordTypeField("v", "name", data_string_variable),
    ]),
    SubRecordType("FNAM", "type_name", fields=[
        SubRecordTypeField(1, "name", data_string_exact),
    ]),
    SubRecordType("FLTV", "value", fields=[
        # Type depends on type name: 's' (short) 'l' (long) or 'f' (float)
        SubRecordTypeField(4, "value", data_string_exact),
    ]),
]))

record_type_list.append(RecordType("GMST", "game_setting", [
    SubRecordType("NAME", "name", fields=[
        SubRecordTypeField("s", "name", data_string_exact),
    ]),
    SubRecordType("STRV", "string_value", fields=[
        SubRecordTypeField("s", "value", data_string_exact),
    ]),
    SubRecordType("INTV", "int_value", fields=[
        SubRecordTypeField(4, "value", data_integer_signed),
    ]),
    SubRecordType("FLTV", "float_value", fields=[
        SubRecordTypeField(4, "value", data_float),
    ]),
]))

record_type_list.append(RecordType("CLAS", "class", [
    SubRecordType("NAME", "name", fields=[
        SubRecordTypeField("v", "name", data_string_variable),
    ]),
    SubRecordType("FNAM", "name_string", fields=[
        SubRecordTypeField("v", "name", data_string_variable),
    ]),
    SubRecordType("CLDT", "class_data", fields=[
        SubRecordTypeField(4, "attribute_id_1", data_integer_signed),
        SubRecordTypeField(4, "attribute_id_2", data_integer_signed),
        SubRecordTypeField(4, "specialization", data_integer_signed),
    ] + SubRecordTypeField.repeat(5, [
        SubRecordTypeField(4, "minor_id", data_integer_signed),
        SubRecordTypeField(4, "major_id", data_integer_signed),
    ]) + [
        SubRecordTypeField(4, "flags", data_flags([
            (0x01, "playable"),
        ])),
        SubRecordTypeField(4, "service_flags", data_flags([
            (0x00001, "weapons"), (0x00002, "armor"),
            (0x00004, "clothing"), (0x00008, "books"),
            (0x00010, "ingredients"), (0x00020, "picks"),
            (0x00040, "probes"), (0x00080, "lights"),
            (0x00100, "apparatus"), (0x00200, "repair_items"),
            (0x00400, "misc_items"), (0x00800, "spells"),
            (0x01000, "magic_items"), (0x02000, "potions"),
            (0x04000, "training"), (0x08000, "spellmaking"),
            (0x10000, "enchanting"), (0x20000, "repairs"),
        ])),
    ]),
    SubRecordType("DESC", "description", fields=[
        SubRecordTypeField("s", "text", data_string_exact),
    ]),
]))

record_type_list.append(RecordType("FACT", "faction", [
    SubRecordType("NAME", "name", fields=[
        SubRecordTypeField("v", "name", data_string_variable),
    ]),
    SubRecordType("FNAM", "name_string", fields=[
        SubRecordTypeField("v", "name", data_string_variable),
    ]),
    # 10 RNAM sub-records expected
    SubRecordType("RNAM", "rank_names", fields=[
        SubRecordTypeField(32, "name", data_string_padded),
    ]),
    SubRecordType("FADT", "faction_data", fields=[
        SubRecordTypeField(4, "attribute_id_1", data_integer_signed),
        SubRecordTypeField(4, "attribute_id_2", data_integer_signed),
    ] + SubRecordTypeField.repeat(10, [
        SubRecordTypeField(4, "rank_attribute_1", data_integer_signed),
        SubRecordTypeField(4, "rank_attribute_2", data_integer_signed),
        SubRecordTypeField(4, "rank_skill_1", data_integer_signed),
        SubRecordTypeField(4, "rank_skill_2", data_integer_signed),
        SubRecordTypeField(4, "rank_reputation", data_integer_signed),
    ]) + SubRecordTypeField.repeat(6, [
        SubRecordTypeField(4, "favored_skill_id", data_integer_signed),
    ]) + [
        SubRecordTypeField(4, "unknown_1", data_integer_signed),
        SubRecordTypeField(4, "flags", data_flags([
            (0x01, "hidden_from_player"),
        ])),
    ]),
    SubRecordType("ANAM", "faction_reaction_names", fields=[
        SubRecordTypeField("s", "faction_name", data_string_exact),
    ]),
    SubRecordType("INTV", "faction_reaction_values", fields=[
        SubRecordTypeField(4, "reaction_value", data_integer_signed),
    ]),
]))

record_type_list.append(RecordType("RACE", "race", [
    SubRecordType("NAME", "name", fields=[
        SubRecordTypeField("v", "name", data_string_variable),
    ]),
    SubRecordType("FNAM", "name_string", fields=[
        SubRecordTypeField("v", "name", data_string_variable),
    ]),
    SubRecordType("RADT", "race_data", fields=SubRecordTypeField.repeat(7, [
        SubRecordTypeField(4, "skill_bonus_id", data_integer_signed),
        SubRecordTypeField(4, "skill_bonus_value", data_integer_signed),
    ]) + [
        SubRecordTypeField(4, "base_strength_male", data_integer_signed),
        SubRecordTypeField(4, "base_strength_female", data_integer_signed),
        SubRecordTypeField(4, "base_intelligence_male", data_integer_signed),
        SubRecordTypeField(4, "base_intelligence_female", data_integer_signed),
        SubRecordTypeField(4, "base_willpower_male", data_integer_signed),
        SubRecordTypeField(4, "base_willpower_female", data_integer_signed),
        SubRecordTypeField(4, "base_agility_male", data_integer_signed),
        SubRecordTypeField(4, "base_agility_female", data_integer_signed),
        SubRecordTypeField(4, "base_speed_male", data_integer_signed),
        SubRecordTypeField(4, "base_speed_female", data_integer_signed),
        SubRecordTypeField(4, "base_endurance_male", data_integer_signed),
        SubRecordTypeField(4, "base_endurance_female", data_integer_signed),
        SubRecordTypeField(4, "base_personality_male", data_integer_signed),
        SubRecordTypeField(4, "base_personality_female", data_integer_signed),
        SubRecordTypeField(4, "base_luck_male", data_integer_signed),
        SubRecordTypeField(4, "base_luck_female", data_integer_signed),
        SubRecordTypeField(4, "base_height_male", data_float),
        SubRecordTypeField(4, "base_height_female", data_float),
        SubRecordTypeField(4, "base_weight_male", data_float),
        SubRecordTypeField(4, "base_weight_female", data_float),
        SubRecordTypeField(4, "flags", data_flags([
            (0x01, "playable"), (0x02, "beast")
        ])),
    ]),
    SubRecordType("NPCS", "ability_names", fields=[
        SubRecordTypeField(32, "name", data_string_padded),
    ]),
    SubRecordType("DESC", "description", fields=[
        SubRecordTypeField("s", "text", data_string_exact),
    ]),
]))

record_type_list.append(RecordType("NPC_", "npc", [
    SubRecordType("NAME", "name", fields=[
        SubRecordTypeField("v", "name", data_string_variable),
    ]),
    SubRecordType("FNAM", "name_string", fields=[
        SubRecordTypeField("v", "name", data_string_variable),
    ]),
    SubRecordType("RNAM", "race_name", fields=[
        SubRecordTypeField("v", "name", data_string_variable),
    ]),
    SubRecordType("CNAM", "class_name", fields=[
        SubRecordTypeField("v", "name", data_string_variable),
    ]),
    SubRecordType("ANAM", "faction_name", fields=[
        SubRecordTypeField("v", "name", data_string_variable),
    ]),
    SubRecordType("BNAM", "head_model_name", fields=[
        SubRecordTypeField("v", "name", data_string_variable),
    ]),
    SubRecordType("KNAM", "hair_model_name", fields=[
        SubRecordTypeField("v", "name", data_string_variable),
    ]),
    # ?
    # SubRecordType("MODL", "model_file_name", fields=[
    #     SubRecordTypeField("v", "name", data_string_exact),
    # ]),
    # SubRecordType("SCRI", "script_name", fields=[
    #     SubRecordTypeField("v", "name", data_string_exact),
    # ]),
    SubRecordType("NPDT", "npc_data", required_size=12, fields=[
        SubRecordTypeField(2, "level", data_integer_signed),
        SubRecordTypeField(1, "disposition", data_integer_signed),
        SubRecordTypeField(1, "faction_id", data_integer_signed),
        SubRecordTypeField(1, "faction_rank", data_integer_signed),
        SubRecordTypeField(1, "unknown_1", data_integer_signed),
        SubRecordTypeField(1, "unknown_2", data_integer_signed),
        SubRecordTypeField(1, "unknown_3", data_integer_signed),
        SubRecordTypeField(4, "gold", data_integer_signed),
    ]),
    SubRecordType("NPDT", "npc_data", required_size=52, fields=[
        SubRecordTypeField(2, "level", data_integer_signed),
        SubRecordTypeField(1, "strength", data_integer_signed),
        SubRecordTypeField(1, "intelligence", data_integer_signed),
        SubRecordTypeField(1, "willpower", data_integer_signed),
        SubRecordTypeField(1, "agility", data_integer_signed),
        SubRecordTypeField(1, "speed", data_integer_signed),
        SubRecordTypeField(1, "endurance", data_integer_signed),
        SubRecordTypeField(1, "personality", data_integer_signed),
        SubRecordTypeField(1, "luck", data_integer_signed),
    ] + SubRecordTypeField.repeat(27, [
        SubRecordTypeField(1, "skill", data_integer_signed),
    ]) + [
        SubRecordTypeField(1, "reputation", data_integer_signed),
        SubRecordTypeField(2, "health", data_integer_signed),
        SubRecordTypeField(2, "magicka", data_integer_signed),
        SubRecordTypeField(2, "fatigue", data_integer_signed),
        SubRecordTypeField(1, "disposition", data_integer_signed),
        SubRecordTypeField(1, "faction_id", data_integer_signed),
        SubRecordTypeField(1, "faction_rank", data_integer_signed),
        SubRecordTypeField(1, "unknown_1", data_integer_signed),
        SubRecordTypeField(4, "gold", data_integer_signed),
    ]),
    SubRecordType("FLAG", "flags", fields=[
        SubRecordTypeField(4, "flags", data_flags([
            (0x0001, "female"),
            (0x0002, "essential"),
            (0x0004, "respawn"),
            (0x0010, "auto_calc"),
            (0x0400, "blood_skeleton"), # ?
            (0x0800, "blood_metal"), # ?
        ])),
    ]),
    SubRecordType("NPCO", "inventory_items", fields=[
        SubRecordTypeField(4, "item_count", data_integer_signed),
        SubRecordTypeField(32, "item_name", data_string_padded),
    ]),
    SubRecordType("NPCS", "spells", fields=[
        SubRecordTypeField(32, "spell_name", data_string_padded),
    ]),
    SubRecordType("AIDT", "ai_data", fields=[
        SubRecordTypeField(1, "hello", data_integer_signed),
        SubRecordTypeField(1, "unknown_1", data_integer_signed),
        SubRecordTypeField(1, "fight", data_integer_signed),
        SubRecordTypeField(1, "flee", data_integer_signed),
        SubRecordTypeField(1, "alarm", data_integer_signed),
        SubRecordTypeField(1, "unknown_2", data_integer_signed),
        SubRecordTypeField(1, "unknown_3", data_integer_signed),
        SubRecordTypeField(1, "unknown_4", data_integer_signed),
        SubRecordTypeField(4, "service_flags", data_flags([
            (0x00001, "weapons"), (0x00002, "armor"),
            (0x00004, "clothing"), (0x00008, "books"),
            (0x00010, "ingredients"), (0x00020, "picks"),
            (0x00040, "probes"), (0x00080, "lights"),
            (0x00100, "apparatus"), (0x00200, "repair_items"),
            (0x00400, "misc_items"), (0x00800, "spells"),
            (0x01000, "magic_items"), (0x02000, "potions"),
            (0x04000, "training"), (0x08000, "spellmaking"),
            (0x10000, "enchanting"), (0x20000, "repairs"),
        ])),
    ]),
    # SubRecordType("AI_W", "ai_wander", fields=[
    #     SubRecordTypeField(2, "distance", data_integer_signed),
    #     SubRecordTypeField(2, "duration", data_integer_signed),
    #     SubRecordTypeField(1, "time_of_day", data_integer_signed),
    # ] + SubRecordTypeField.repeat(8, [
    #     SubRecordTypeField(1, "idle"),
    # ]) + [
    #     SubRecordTypeField(1, "unknown_1", data_integer_signed),
    # ]),
    # SubRecordType("AI_T", "ai_travel", fields=[
    #     SubRecordTypeField(4, "x", data_float),
    #     SubRecordTypeField(4, "y", data_float),
    #     SubRecordTypeField(4, "z", data_float),
    #     SubRecordTypeField(4, "unknown_1", data_integer_signed),
    # ]),
    # SubRecordType("AI_F", "ai_follow", fields=[
    #     SubRecordTypeField(4, "x", data_float),
    #     SubRecordTypeField(4, "y", data_float),
    #     SubRecordTypeField(4, "z", data_float),
    #     SubRecordTypeField(2, "duration", data_integer_signed),
    #     # You'd think this would be a padded string, but what's going
    #     # on with the characters often appearing after the NPC name?
    #     SubRecordTypeField(32, "npc_name", data_string_exact),
    #     SubRecordTypeField(2, "unknown_1", data_integer_signed),
    # ]),
    # SubRecordType("AI_E", "ai_escort", fields=[
    #     SubRecordTypeField(4, "x", data_float),
    #     SubRecordTypeField(4, "y", data_float),
    #     SubRecordTypeField(4, "z", data_float),
    #     SubRecordTypeField(2, "duration", data_integer_signed),
    #     # You'd think this would be a padded string, but what's going
    #     # on with the characters often appearing after the NPC name?
    #     SubRecordTypeField(32, "npc_name", data_string_exact),
    #     SubRecordTypeField(2, "unknown_1", data_integer_signed),
    # ]),
    # # Doesn't seem to appear in any official esm?
    # SubRecordType("AI_A", "ai_activate", fields=[
    #     SubRecordTypeField(32, "npc_name", data_string_exact),
    #     SubRecordTypeField(1, "unknown_1", data_integer_signed),
    # ]),
    # SubRecordType("CNDT", "cell_escort", fields=[
    #     SubRecordTypeField(4, "unknown_1", data_integer_signed),
    # ]),
]))

record_type_list.append(RecordType("DIAL", "dialog_topic", [
    SubRecordType("NAME", "name", fields=[
        SubRecordTypeField("v", "name", data_string_variable),
    ]),
    SubRecordType("DATA", "dialog_type", fields=[
        SubRecordTypeField("s", "type", data_integer_unsigned),
    ]),
]))

record_type_list.append(RecordType("INFO", "dialog_response", [
    SubRecordType("INAM", "info_id", fields=[
        SubRecordTypeField("v", "info_id", data_string_variable),
    ]),
    SubRecordType("PNAM", "previous_id", fields=[
        SubRecordTypeField("v", "info_id", data_string_variable),
    ]),
    SubRecordType("NNAM", "next_id", fields=[
        SubRecordTypeField("v", "info_id", data_string_variable),
    ]),
    SubRecordType("DATA", "info_data", fields=[
        SubRecordTypeField(4, "unknown_1", data_integer_signed),
        SubRecordTypeField(4, "disposition", data_integer_signed),
        SubRecordTypeField(1, "faction_rank", data_integer_signed),
        SubRecordTypeField(1, "gender", data_integer_signed),
        SubRecordTypeField(1, "player_faction_rank", data_integer_signed),
        SubRecordTypeField(1, "unknown_2", data_integer_unsigned),
    ]),
    SubRecordType("ONAM", "actor_name", fields=[
        SubRecordTypeField("v", "name", data_string_variable),
    ]),
    SubRecordType("RNAM", "race_name", fields=[
        SubRecordTypeField("v", "name", data_string_variable),
    ]),
    SubRecordType("CNAM", "class_name", fields=[
        SubRecordTypeField("v", "name", data_string_variable),
    ]),
    SubRecordType("FNAM", "faction_name", fields=[
        SubRecordTypeField("v", "name", data_string_variable),
    ]),
    SubRecordType("ANAM", "cell_name", fields=[
        SubRecordTypeField("v", "name", data_string_variable),
    ]),
    SubRecordType("DNAM", "player_faction_name", fields=[
        SubRecordTypeField("v", "name", data_string_variable),
    ]),
    SubRecordType("SNAM", "sound_file_name", fields=[
        SubRecordTypeField("v", "file_name", data_string_variable),
    ]),
    SubRecordType("NAME", "response_text", fields=[
        SubRecordTypeField("s", "text", data_string_exact),
    ]),
    SubRecordType("SCVR", "functions", fields=[
        SubRecordTypeField(1, "index", data_string_exact),
        SubRecordTypeField(1, "type", data_string_exact),
        SubRecordTypeField(2, "function", data_string_exact),
        SubRecordTypeField(1, "comparison", data_string_exact),
        SubRecordTypeField("s", "variable", data_string_exact),
    ]),
    SubRecordType("INTV", "function_int", fields=[
        SubRecordTypeField(4, "value", data_integer_signed),
    ]),
    SubRecordType("FLTV", "function_float", fields=[
        SubRecordTypeField(4, "value", data_float),
    ]),
    SubRecordType("BNAM", "result_text", fields=[
        SubRecordTypeField("s", "text", data_string_exact),
    ]),
]))
