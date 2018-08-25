from lexscan import tokenize, ScanExp

reset_color = "\033[0m"
line_number_color = "\033[36m"

syntax_colors = {
    "comment": "\033[96m",
    "string": "\033[92m",
    "number": "\033[93m",
    "operator": "\033[37m",
    "control": "\033[95m",
}

lexscan_list = [
    ScanExp(r'"([^\\"]|\\\\|\\")*"', name="string"),
    ScanExp(r'[+-]?[0-9]+(\.[0-9]+)?', name="number"),
    ScanExp(r'(\+|\*|-|/|==|<=|<|>=|>|!=|->)', name="operator"),
    ScanExp(r'(?i)\b(elseif|ifx|if|else|endif|while|endwhile|return|begin|end|startscript|stopscript|float|short|long|set|to)\b', name="control"),
    ScanExp(r';.*', name="comment"),
    ScanExp(r'\s+', name="whitespace"),
    ScanExp(r'\b[_a-zA-Z][_a-zA-Z0-9]*', name="word"),
]

def syntax_highlight(text):
    lines = text.decode("latin-1").split("\n")
    output_lines = []
    for i in range(len(lines)):
        tokens = tokenize(lines[i], lexscan_list)
        output_line = ""
        for token in tokens:
            if token.expression and token.expression.name in syntax_colors:
                color = syntax_colors[token.expression.name]
                output_line += color + token.text + reset_color
            else:
                output_line += token.text
        output_lines.append(
            line_number_color + str(1 + i).rjust(3) + reset_color +
            " " + output_line
        )
    return "\n".join(output_lines)

def just_add_line_numbers(text):
    lines = text.split(b"\n")
    for i in range(len(lines)):
        lines[i] = (
            bytes(str(1 + i).encode("latin-1")).rjust(3) + b" " + lines[i]
        )
    return b"\n".join(lines)
