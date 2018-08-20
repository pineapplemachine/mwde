help_text = """
Commands work like this:
    command <flags> <text>
Flags are a letter preceded by a hyphen.
Here are some examples of queries:
    npc Nalion
    topic alchemy
    sub -i example
    cell -p -V vivec

Here is a list of commands. Type "help <command>" for
more information about a particular command.
    sub
    re
    npc
    race
    faction
    cell
    topic
    quest
    load
    reload
    unload
    help
    about
    quit
""".strip()

about_text = """
You are currently using Morrowind Dialog Explorer.
MWDE is a mod tool by Sophie Kirschner for the game
TES3 Morrowind. MWDE provides tools for searching
and exploring Morrowind dialog topics and responses.

Morrowind Dialog Explorer is online at
    https://pineapplemachine.com/files/mwde
    https://github.com/pineapplemachine/mwde

Thanks for using MWDE!
""".strip()

sub_help_text = """
Show all dialog text that includes a substring.
    sub <text>
Options:
    sub -i  ... Case-sensitive (default insensitive)
    sub -O  ... Display dialog overwritten by a later file
    sub -V  ... Display more info about responses
Examples:
    sub Ald Daedroth
    sub -i vivec
""".strip()

re_help_text = """
Show all dialog text that contains text matching a
regular expression
    re <regex>
Options:
    re -i  ... Case-insensitive (default sensitive)
    re -s  ... Single line (affects . metacharacter)
    re -m  ... Multi-line (affects ^ and $ metacharacters)
    re -O  ... Display dialog overwritten by a later file
    re -V  ... Display more info about responses
Examples:
    re (color|colour)\b
""".strip()

npc_help_text = """
Show all dialog text that can be spoken by an NPC.
    npc <name>
Options:
    npc -r  ... Include dialog general to NPC's race
    npc -c  ... Include dialog general to NPC's class
    npc -f  ... Include dialog general to NPC's faction
    npc -O  ... Display dialog overwritten by a later file
    npc -V  ... Display more info about responses
Examples:
    npc Vianis Tiragrius
    npc -f dabienne mornardl
""".strip()

race_help_text = """
Show all dialog text spoken by NPCs of a certain race.
    race <name>
Examples:
    race argonian
    race altmer
    race dark elf
Options:
    race -O  ... Display dialog overwritten by a later file
    race -V  ... Display more info about responses
""".strip()

faction_help_text = """
Show all dialog text spoken by NPCs of a certain faction.
    faction <name>
Examples:
    faction Telvanni
    faction great house hlaalu
Options:
    faction -O  ... Display dialog overwritten by a later file
    faction -V  ... Display more info about responses
""".strip()
 
cell_help_text = """
Show all dialog text spoken by NPCs in a certain cell,
or cells whose name begins with a string.
    cell <name>
Examples:
    cell Mournhold, Plaza Brindisi Dorom
    cell -p Vivec
Options:
    cell -p  ... Match cell names starting with the input
    cell -O  ... Display dialog overwritten by a later file
    cell -V  ... Display more info about responses
""".strip()

topic_help_text = """
Show all dialog responses belonging to a certain topic.
    topic <name>
Examples:
    topic alchemy
Options:
    topic -O  ... Display dialog overwritten by a later file
    topic -V  ... Display more info about responses
""".strip()

quest_help_text = """
Show all dialog and journal text that pertains to a
quest.
    quest <name>
Examples:
    quest FG_SilenceMagistrate
Options:
    quest -O  ... Display dialog overwritten by a later file
    quest -V  ... Display more info about responses
""".strip()

load_help_text = """
Load a new ESM or ESP file into the program.
    load <path>
Examples:
    load C:/Morrowind/Data Files/Morrowind.esm
""".strip()

reload_help_text = """
Reload an ESM or ESP file previously loaded into
the program.
    reload <path>
Examples:
    reload Morrowind.esm
""".strip()

unload_help_text = """
Unload data from an ESM or ESP file previously
loaded into the program.
    unload <path>
Examples:
    unload Morrowind.esm
""".strip()

quit_help_text = """
Quit Morrowind Dialog Explorer.
You can also quit by pressing ctrl+c.
    quit
""".strip()
